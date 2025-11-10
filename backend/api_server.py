"""
FastAPI 后端服务
为 Electron + Vue3 前端提供 API 接口
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import threading
import logging
import time
from pathlib import Path
import sys

# 导入核心模块
from core.menu_manager import create_menu_manager
from core.task_executor import task_executor, TaskFactory, Task
from core.macro_engine import macro_engine
from core.game_navigator import game_navigator
from core.input_controller import input_controller
from core.keybindings import keybindings_manager
from core.menu_config import menu_config_manager

# 创建菜单管理器实例
menu_manager = create_menu_manager()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('erm_backend.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="二重螺旋自动化API", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局自动化实例
task_executor_instance = task_executor  # 使用统一的任务执行器
is_running = False
current_task = None
task_thread = None
current_progress = {"current": 0, "total": 0, "status": "", "is_running": False}

# 数据模型 - 统一前后端格式
class MissionTask(BaseModel):
    id: str
    name: str
    type: str
    category: Optional[str] = None
    sub_category: Optional[str] = None
    mission_key: Optional[str] = None
    selected_level: Optional[str] = None
    level_display_name: Optional[str] = None
    run_count: int = 1
    priority: int = 1
    status: str = "pending"
    progress: int = 0
    added_at: str
    params: Dict[str, Any] = {}

class TaskQueue(BaseModel):
    tasks: List[MissionTask]

class TaskProgress(BaseModel):
    current: int
    total: int
    status: str
    is_running: bool

# 键位相关数据模型
class KeyBindingUpdate(BaseModel):
    action: str
    key: str

class KeyBindingExecute(BaseModel):
    action: str
    press_type: str = "press"
    duration: float = 0.1

# 菜单配置相关数据模型
class MenuConfigUpdate(BaseModel):
    config_data: Dict[str, Any]

# 宏配置相关数据模型
class MacroCreate(BaseModel):
    name: str
    description: str = ""
    steps: List[Dict[str, Any]]

class MacroUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[List[Dict[str, Any]]] = None
    enabled: Optional[bool] = None

class MacroExecute(BaseModel):
    macro_id: str
    repeat_count: int = 1

# API路由
@app.get("/")
async def root():
    """API根路径"""
    return {"message": "二重螺旋自动化API服务运行中", "version": "1.0.0"}

@app.get("/api/menu/main-categories")
async def get_main_categories():
    """获取主分类列表"""
    try:
        categories = menu_manager.get_main_categories()
        category_keys = menu_manager.get_main_category_keys()
        return [
            {"key": key, "displayName": name}
            for key, name in zip(category_keys, categories)
        ]
    except Exception as e:
        logger.error(f"获取主分类失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/menu/sub-categories/{main_category}")
async def get_sub_categories(main_category: str):
    """获取子分类列表"""
    try:
        sub_categories = menu_manager.get_sub_categories(main_category)
        result = []
        for sub_key, sub_info in sub_categories.items():
            result.append({
                "key": sub_key,
                "displayName": sub_info.displayName,
                "missions": [
                    {
                        "key": mission.key,
                        "displayName": mission.displayName,
                        "type": mission.type,
                        "levels": [
                            {"key": level.key, "displayName": level.displayName}
                            for level in mission.levels
                        ]
                    }
                    for mission in sub_info.children.values()
                ]
            })
        return result
    except Exception as e:
        logger.error(f"获取子分类失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/menu/mission-type/{mission_type}")
async def get_mission_type_display(mission_type: str):
    """获取任务类型显示名称"""
    try:
        display_name = menu_manager.get_mission_type_display_name(mission_type)
        return {"mission_type": mission_type, "display_name": display_name}
    except Exception as e:
        logger.error(f"获取任务类型显示名称失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/menu/missions/{main_category}/{sub_category}")
async def get_subcategory_missions(main_category: str, sub_category: str):
    """获取指定子分类下的任务列表"""
    try:
        missions = menu_manager.get_subcategory_missions(main_category, sub_category)
        return {"missions": missions}
    except Exception as e:
        logger.error(f"获取任务列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/task/status")
async def get_task_status():
    """获取当前任务状态"""
    global is_running, current_task
    progress = task_executor_instance.get_progress()
    return TaskProgress(
        current=progress.get("current", 0),
        total=progress.get("total", 0),
        status=progress.get("status", ""),
        is_running=is_running
    )

@app.post("/api/task/start")
async def start_tasks(queue: TaskQueue, background_tasks: BackgroundTasks):
    """开始执行任务队列"""
    return await start_tasks_execute(queue)

@app.post("/api/tasks/execute")
async def start_tasks_execute(request: Dict[str, Any]):
    """开始执行任务队列 - 使用新的任务引擎"""
    global is_running, task_thread, current_progress

    if is_running:
        raise HTTPException(status_code=400, detail="任务正在执行中")

    tasks_data = request.get("tasks", [])
    if not tasks_data:
        raise HTTPException(status_code=400, detail="任务队列为空")

    try:
        # 使用TaskFactory转换前端数据为Task对象
        tasks = [TaskFactory.create_from_frontend_data(task_data) for task_data in tasks_data]
        total_runs = sum(task.run_count for task in tasks)

        logger.info(f"开始执行任务队列，共{len(tasks)}个任务，{total_runs}次执行")

        # 重置进度
        current_progress = {
            "current": 0,
            "total": total_runs,
            "status": "准备执行...",
            "is_running": True
        }

        # 定义进度回调函数
        def progress_callback(completed, total, status):
            current_progress.update({
                "current": completed,
                "total": total,
                "status": status,
                "is_running": True
            })

        # 在后台线程中执行任务
        def run_tasks():
            global is_running
            try:
                is_running = True
                success = task_executor.execute_task_queue(tasks, progress_callback)

                # 更新最终状态
                current_progress.update({
                    "status": "执行完成" if success else "执行失败",
                    "is_running": False
                })
                logger.info(f"任务队列执行完成: {'成功' if success else '失败'}")

            except Exception as e:
                logger.error(f"任务队列执行异常: {e}")
                current_progress.update({
                    "status": f"执行异常: {str(e)}",
                    "is_running": False
                })
            finally:
                is_running = False

        # 启动后台任务
        task_thread = threading.Thread(target=run_tasks, daemon=True)
        task_thread.start()

        return {
            "success": True,
            "message": "任务执行已启动",
            "data": {
                "total_tasks": len(tasks),
                "total_runs": total_runs
            }
        }

    except Exception as e:
        logger.error(f"启动任务执行失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

  
@app.post("/api/task/stop")
async def stop_tasks():
    """停止当前任务"""
    return await stop_tasks_execute()

@app.post("/api/tasks/stop")
async def stop_tasks_execute():
    """停止当前任务 - 使用新的任务引擎"""
    global is_running, current_progress

    if not is_running:
        raise HTTPException(status_code=400, detail="没有正在执行的任务")

    try:
        logger.info("API请求停止执行")

        # 停止新任务引擎
        task_executor.stop()

        # 重置状态
        is_running = False
        current_progress = {
            "current": 0,
            "total": 0,
            "status": "已停止",
            "is_running": False
        }

        return {"success": True, "message": "任务已停止"}
    except Exception as e:
        logger.error(f"停止任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/progress")
async def get_tasks_progress():
    """获取任务进度 - 使用新的任务引擎"""
    global current_progress

    return {
        "success": True,
        "data": current_progress
    }

@app.get("/api/tasks/history")
async def get_tasks_history():
    """获取任务历史 - 统一接口"""
    return {
        "success": True,
        "data": []
    }

@app.get("/api/system/info")
async def get_system_info():
    """获取系统信息"""
    try:
        import psutil
        import platform

        return {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent
        }
    except ImportError:
        return {"message": "系统信息模块未安装"}
    except Exception as e:
        logger.error(f"获取系统信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 键位配置相关API
@app.get("/api/keybindings")
async def get_keybindings():
    """获取键位配置"""
    try:
        bindings = keybindings_manager.get_current_bindings()
        action_names = keybindings_manager.get_action_names()
        key_names = keybindings_manager.get_key_names()

        return {
            "bindings": bindings,
            "action_names": action_names,
            "key_names": key_names
        }
    except Exception as e:
        logger.error(f"获取键位配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/keybindings/update")
async def update_keybinding(request: KeyBindingUpdate):
    """更新键位配置"""
    try:
        success = keybindings_manager.set_binding(request.action, request.key)
        if success:
            return {"message": "键位更新成功"}
        else:
            raise HTTPException(status_code=400, detail="键位更新失败，可能存在键位冲突")
    except Exception as e:
        logger.error(f"更新键位失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/keybindings/execute")
async def execute_keybinding(request: KeyBindingExecute):
    """执行键位操作"""
    try:
        success = keybindings_manager.execute_action(
            request.action,
            request.press_type,
            request.duration
        )
        if success:
            return {"message": "键位执行成功"}
        else:
            raise HTTPException(status_code=400, detail="键位执行失败，请检查配置")
    except Exception as e:
        logger.error(f"执行键位失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/keybindings/export")
async def export_keybindings(file_path: str):
    """导出键位配置"""
    try:
        success = keybindings_manager.export_config(file_path)
        if success:
            return {"message": "配置导出成功"}
        else:
            raise HTTPException(status_code=400, detail="配置导出失败")
    except Exception as e:
        logger.error(f"导出配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/keybindings/import")
async def import_keybindings(file_path: str):
    """导入键位配置"""
    try:
        success = keybindings_manager.import_config(file_path)
        if success:
            return {"message": "配置导入成功"}
        else:
            raise HTTPException(status_code=400, detail="配置导入失败")
    except Exception as e:
        logger.error(f"导入配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/keybindings/reset")
async def reset_keybindings():
    """重置键位配置"""
    try:
        success = keybindings_manager.reset_to_default()
        if success:
            return {"message": "配置重置成功"}
        else:
            raise HTTPException(status_code=400, detail="配置重置失败")
    except Exception as e:
        logger.error(f"重置配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 宏配置相关API
@app.get("/api/macros")
async def get_macros():
    """获取所有宏配置"""
    try:
        macros = macro_engine.get_all_macros()
        return {
            "macros": [macro.model_dump() for macro in macros]
        }
    except Exception as e:
        logger.error(f"获取宏配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/macros")
async def create_macro(request: MacroCreate):
    """创建新宏"""
    try:
        macro = macro_engine.create_macro(
            name=request.name,
            description=request.description,
            steps_data=request.steps
        )
        if macro:
            return {"message": "宏创建成功", "macro_id": macro.id}
        else:
            raise HTTPException(status_code=400, detail="宏创建失败")
    except Exception as e:
        logger.error(f"创建宏失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/macros/{macro_id}")
async def update_macro(macro_id: str, request: MacroUpdate):
    """更新宏配置"""
    try:
        success = macro_engine.update_macro(
            macro_id=macro_id,
            name=request.name,
            description=request.description,
            steps_data=request.steps,
            enabled=request.enabled
        )
        if success:
            return {"message": "宏更新成功"}
        else:
            raise HTTPException(status_code=404, detail="宏不存在或更新失败")
    except Exception as e:
        logger.error(f"更新宏失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/macros/{macro_id}")
async def delete_macro(macro_id: str):
    """删除宏"""
    try:
        success = macro_engine.delete_macro(macro_id)
        if success:
            return {"message": "宏删除成功"}
        else:
            raise HTTPException(status_code=404, detail="宏不存在")
    except Exception as e:
        logger.error(f"删除宏失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/macros/execute")
async def execute_macro(request: MacroExecute):
    """执行宏"""
    try:
        success = macro_engine.execute_macro(
            macro_id=request.macro_id,
            repeat_count=request.repeat_count
        )
        if success:
            return {"message": "宏执行成功"}
        else:
            raise HTTPException(status_code=400, detail="宏执行失败，请检查宏配置")
    except Exception as e:
        logger.error(f"执行宏失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/macros/export")
async def export_macros():
    """导出宏配置"""
    try:
        # 生成临时文件路径
        import tempfile
        temp_dir = tempfile.gettempdir()
        file_path = f"{temp_dir}/macros_export_{int(time.time())}.json"

        success = macro_engine.export_config(file_path)
        if success:
            # 读取文件内容并返回
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        else:
            raise HTTPException(status_code=400, detail="宏配置导出失败")
    except Exception as e:
        logger.error(f"导出宏配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/macros/import")
async def import_macros(config_data: Dict[str, Any]):
    """导入宏配置"""
    try:
        success = macro_engine.import_config(config_data)
        if success:
            return {"message": "宏配置导入成功"}
        else:
            raise HTTPException(status_code=400, detail="宏配置导入失败")
    except Exception as e:
        logger.error(f"导入宏配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 菜单配置相关API
@app.get("/api/menu/config")
async def get_menu_config():
    """获取完整菜单配置"""
    try:
        config = menu_config_manager.get_menu_config()
        return config
    except Exception as e:
        logger.error(f"获取菜单配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/menu/mission-types")
async def get_mission_types():
    """获取任务类型映射"""
    try:
        mission_types = menu_config_manager.get_mission_types()
        return mission_types
    except Exception as e:
        logger.error(f"获取任务类型失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/menu/mission-types/{mission_type}")
async def get_mission_type_display(mission_type: str):
    """获取任务类型的显示名称"""
    try:
        display_name = menu_config_manager.get_mission_type_display_name(mission_type)
        return {"mission_type": mission_type, "display_name": display_name}
    except Exception as e:
        logger.error(f"获取任务类型显示名称失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/menu/main-categories")
async def get_main_categories():
    """获取主分类列表"""
    try:
        categories = menu_config_manager.get_main_categories()
        category_keys = menu_config_manager.get_main_category_keys()
        return [
            {"key": key, "displayName": name}
            for key, name in zip(category_keys, categories)
        ]
    except Exception as e:
        logger.error(f"获取主分类失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/menu/sub-categories/{main_category}")
async def get_sub_categories(main_category: str):
    """获取子分类列表"""
    try:
        sub_categories = menu_config_manager.get_sub_categories(main_category)
        result = []
        for sub_key, sub_info in sub_categories.items():
            result.append({
                "key": sub_key,
                "displayName": sub_info.get("displayName", sub_key),
                "missions": sub_info.get("missions", [])
            })
        return result
    except Exception as e:
        logger.error(f"获取子分类失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/menu/missions/{main_category}/{sub_category}")
async def get_missions(main_category: str, sub_category: str):
    """获取任务列表"""
    try:
        missions = menu_config_manager.get_missions(main_category, sub_category)
        return {
            "main_category": main_category,
            "sub_category": sub_category,
            "missions": missions
        }
    except Exception as e:
        logger.error(f"获取任务列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/menu/config")
async def update_menu_config(request: MenuConfigUpdate):
    """更新菜单配置"""
    try:
        success = menu_config_manager.update_menu_config(request.config_data)
        if success:
            return {"message": "菜单配置更新成功"}
        else:
            raise HTTPException(status_code=400, detail="菜单配置更新失败")
    except Exception as e:
        logger.error(f"更新菜单配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/menu/validate")
async def validate_menu_config():
    """验证菜单配置"""
    try:
        validation = menu_config_manager.validate_config()
        return validation
    except Exception as e:
        logger.error(f"验证菜单配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="debug")