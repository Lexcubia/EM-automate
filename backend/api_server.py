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
from pathlib import Path
import sys

# 导入核心模块
from core.menu_manager import menu_manager
from core.automation import GameAutomation
from core.keybindings import keybindings_manager
from core.menu_config import menu_config_manager

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
automation_instance = GameAutomation()
is_running = False
current_task = None
task_thread = None

# 数据模型
class MissionTask(BaseModel):
    mission_key: str
    selected_level: Optional[str] = None
    run_count: int = 1
    mission_type: str
    display_name: str

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
    progress = automation_instance.get_progress()
    return TaskProgress(
        current=progress.get("current", 0),
        total=progress.get("total", 0),
        status=progress.get("status", ""),
        is_running=is_running
    )

@app.post("/api/task/start")
async def start_tasks(queue: TaskQueue, background_tasks: BackgroundTasks):
    """开始执行任务队列"""
    global is_running, task_thread, current_task

    if is_running:
        raise HTTPException(status_code=400, detail="任务正在执行中")

    if not queue.tasks:
        raise HTTPException(status_code=400, detail="任务队列为空")

    try:
        # 转换任务格式
        missions = []
        for task in queue.tasks:
            mission_data = {
                "mission_key": task.mission_key,
                "selected_level": task.selected_level,
                "run_count": task.run_count
            }
            missions.append(mission_data)

        # 记录任务信息
        task_names = []
        total_tasks = 0
        for m in missions:
            mission_display = f"{m['mission_key']}"
            if m['selected_level']:
                mission_display += f"({m['selected_level']})"
            mission_display += f" x{m['run_count']}"
            task_names.append(mission_display)
            total_tasks += m['run_count']

        logger.info(f"API请求开始执行: {', '.join(task_names)} (总计{total_tasks}次)")

        # 在后台线程中执行任务
        def run_tasks():
            global is_running, current_task
            try:
                is_running = True
                automation_instance.run_automation(missions)
            except Exception as e:
                logger.error(f"任务执行出错: {e}")
            finally:
                is_running = False
                current_task = None

        task_thread = threading.Thread(target=run_tasks)
        task_thread.daemon = True
        task_thread.start()

        return {"message": "任务已开始执行", "total_tasks": total_tasks}

    except Exception as e:
        logger.error(f"启动任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/task/stop")
async def stop_tasks():
    """停止当前任务"""
    global is_running, current_task

    if not is_running:
        raise HTTPException(status_code=400, detail="没有正在执行的任务")

    try:
        logger.info("API请求停止执行")
        automation_instance.stop()
        is_running = False
        current_task = None
        return {"message": "任务已停止"}
    except Exception as e:
        logger.error(f"停止任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")