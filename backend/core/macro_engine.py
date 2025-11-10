"""
统一宏引擎 - 合并 macros.py 和 enhanced_macros.py
简化、直接的宏管理和执行系统
"""
import json
import time
import uuid
import logging
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

class MacroExecutionStatus(Enum):
    """宏执行状态"""
    PENDING = "待执行"
    RUNNING = "执行中"
    SUCCESS = "执行成功"
    FAILED = "执行失败"

@dataclass
class MacroExecutionResult:
    """宏执行结果"""
    macro_id: str
    macro_name: str
    status: MacroExecutionStatus
    steps_executed: int = 0
    total_steps: int = 0
    execution_time: float = 0.0
    error_message: str = ""
    repeat_count: int = 1
    current_repeat: int = 0

class MacroStep(BaseModel):
    """宏步骤模型"""
    type: str = Field(..., description="步骤类型: key, delay, click")
    key: Optional[str] = Field(None, description="按键")
    delay: Optional[float] = Field(None, description="延迟时间(秒)")
    x: Optional[int] = Field(None, description="点击X坐标")
    y: Optional[int] = Field(None, description="点击Y坐标")
    button: Optional[str] = Field("left", description="鼠标按钮")
    press_type: Optional[str] = Field("press", description="按键类型: press, down, up")
    duration: Optional[float] = Field(0.1, description="按键持续时间(秒)")
    text: Optional[str] = Field(None, description="输入文本")

    @validator('type')
    def validate_type(cls, v):
        allowed_types = ['key', 'delay', 'click', 'text']
        if v not in allowed_types:
            raise ValueError(f'步骤类型必须是 {allowed_types} 之一')
        return v

    @validator('press_type')
    def validate_press_type(cls, v):
        if v not in ['press', 'down', 'up']:
            raise ValueError('按键类型必须是 press, down 或 up')
        return v

class MacroCommand(BaseModel):
    """宏命令模型"""
    id: str = Field(..., description="宏ID")
    name: str = Field(..., description="宏名称")
    description: Optional[str] = Field("", description="宏描述")
    category: Optional[str] = Field("", description="宏分类")
    steps: List[MacroStep] = Field(..., description="宏步骤列表")
    enabled: bool = Field(True, description="是否启用")
    created_at: Optional[str] = Field(None, description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")

class MacroEngine:
    """统一宏引擎 - 简化直接的宏系统"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化宏引擎

        Args:
            config_path: 配置文件路径，默认为 backend/config/macros.json
        """
        if config_path is None:
            current_dir = Path(__file__).parent.parent
            config_path = current_dir / "config" / "macros.json"

        self.config_path = Path(config_path)
        self.macros: Dict[str, MacroCommand] = {}
        self.execution_history: List[MacroExecutionResult] = []

        # 任务分类到宏的映射
        self.category_macros = {
            "委托": ["委托_通用", "委托_默认"],
            "夜航手册": ["夜航手册_通用", "夜航手册_默认"],
            "委托密函": ["委托密函_通用", "委托密函_默认"]
        }

        # 默认回退操作序列
        self.fallback_actions = [
            {'type': 'key', 'key': 'space', 'press_type': 'press', 'duration': 0.5},
            {'type': 'delay', 'delay': 0.3},
            {'type': 'key', 'key': 'enter', 'press_type': 'press', 'duration': 0.3},
            {'type': 'delay', 'delay': 1.0},
            {'type': 'key', 'key': 'z', 'press_type': 'press', 'duration': 2.0},
            {'type': 'delay', 'delay': 0.5},
            {'type': 'key', 'key': 'x', 'press_type': 'press', 'duration': 1.0},
            {'type': 'delay', 'delay': 0.5},
            {'type': 'key', 'key': 'c', 'press_type': 'press', 'duration': 1.5},
        ]

        # 加载配置
        self._load_config()
        logger.info("宏引擎初始化完成")

    def _load_config(self) -> None:
        """加载配置文件"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self._parse_macros(config_data.get("macros", []))
            else:
                logger.warning(f"配置文件不存在: {self.config_path}")
                self._create_default_config()

            logger.info(f"已加载 {len(self.macros)} 个宏配置")

        except Exception as e:
            logger.error(f"加载宏配置失败: {e}")
            self._create_default_config()

    def _parse_macros(self, macros_data: List[Dict[str, Any]]) -> None:
        """解析宏配置"""
        self.macros.clear()

        for macro_data in macros_data:
            try:
                # 转换步骤格式
                steps_data = macro_data.get("steps", [])
                steps = []
                for step_data in steps_data:
                    # 标准化步骤格式
                    if 'type' not in step_data:
                        continue

                    step = MacroStep(**step_data)
                    steps.append(step)

                # 创建宏对象
                macro_data["steps"] = steps
                macro = MacroCommand(**macro_data)
                self.macros[macro.id] = macro

            except Exception as e:
                logger.error(f"解析宏配置失败: {macro_data.get('name', 'Unknown')}, 错误: {e}")

    def _create_default_config(self) -> None:
        """创建默认配置"""
        default_macros = [
            {
                "id": str(uuid.uuid4()),
                "name": "默认通用宏",
                "description": "系统默认的通用宏",
                "category": "通用",
                "enabled": True,
                "steps": self.fallback_actions
            }
        ]

        config_data = {
            "macros": [macro.dict() for macro in default_macros],
            "version": "2.0.0",
            "last_updated": None
        }

        self._save_config(config_data)

    def _save_config(self, config_data: Optional[Dict[str, Any]] = None) -> None:
        """保存配置文件"""
        try:
            # 确保目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            if config_data is None:
                config_data = {
                    "macros": [macro.dict() for macro in self.macros.values()],
                    "version": "2.0.0",
                    "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
                }

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)

            logger.info("宏配置已保存")

        except Exception as e:
            logger.error(f"保存宏配置失败: {e}")

    def execute_macro_for_task(self,
                             task_category: str,
                             task_name: str,
                             macro_id: Optional[str] = None,
                             repeat_count: int = 1,
                             progress_callback: Optional[Callable] = None) -> MacroExecutionResult:
        """
        为任务执行宏 - 智能匹配和回退机制

        Args:
            task_category: 任务分类
            task_name: 任务名称
            macro_id: 指定的宏ID（可选）
            repeat_count: 重复次数
            progress_callback: 进度回调函数

        Returns:
            宏执行结果
        """
        start_time = time.time()
        result = MacroExecutionResult(
            macro_id=macro_id or "",
            macro_name="",
            status=MacroExecutionStatus.PENDING,
            repeat_count=repeat_count,
            current_repeat=0
        )

        try:
            # 策略1：使用指定的宏ID
            if macro_id:
                logger.info(f"尝试使用指定宏: {macro_id}")
                if self._execute_macro_by_id(macro_id, repeat_count, progress_callback):
                    result.status = MacroExecutionStatus.SUCCESS
                    result.macro_name = self._get_macro_name(macro_id)
                else:
                    result.status = MacroExecutionStatus.FAILED
                    result.error_message = f"指定宏执行失败: {macro_id}"

                result.execution_time = time.time() - start_time
                self.execution_history.append(result)
                return result

            # 策略2：尝试精确匹配任务宏
            exact_macro_names = [
                f"{task_category}_{task_name}",
                f"{task_category}_{task_name}_通用",
            ]

            for macro_name in exact_macro_names:
                logger.info(f"尝试精确匹配宏: {macro_name}")
                found_macro_id = self._find_macro_by_name(macro_name)
                if found_macro_id and self._execute_macro_by_id(found_macro_id, repeat_count, progress_callback):
                    result.macro_id = found_macro_id
                    result.macro_name = macro_name
                    result.status = MacroExecutionStatus.SUCCESS
                    break

            if result.status == MacroExecutionStatus.SUCCESS:
                result.execution_time = time.time() - start_time
                self.execution_history.append(result)
                return result

            # 策略3：尝试分类默认宏
            default_macro_names = self.category_macros.get(task_category, [])
            for macro_name in default_macro_names:
                logger.info(f"尝试分类默认宏: {macro_name}")
                found_macro_id = self._find_macro_by_name(macro_name)
                if found_macro_id and self._execute_macro_by_id(found_macro_id, repeat_count, progress_callback):
                    result.macro_id = found_macro_id
                    result.macro_name = macro_name
                    result.status = MacroExecutionStatus.SUCCESS
                    break

            if result.status == MacroExecutionStatus.SUCCESS:
                result.execution_time = time.time() - start_time
                self.execution_history.append(result)
                return result

            # 策略4：执行通用回退操作
            logger.info("使用通用回退操作")
            if self._execute_fallback_actions(repeat_count, progress_callback):
                result.macro_name = "通用回退操作"
                result.status = MacroExecutionStatus.SUCCESS
            else:
                result.macro_name = "通用回退操作"
                result.status = MacroExecutionStatus.FAILED
                result.error_message = "所有宏执行策略都失败"

            result.execution_time = time.time() - start_time
            self.execution_history.append(result)
            return result

        except Exception as e:
            result.status = MacroExecutionStatus.FAILED
            result.error_message = str(e)
            result.execution_time = time.time() - start_time
            logger.error(f"宏执行异常: {e}")

            self.execution_history.append(result)
            return result

    def _execute_macro_by_id(self, macro_id: str, repeat_count: int,
                            progress_callback: Optional[Callable] = None) -> bool:
        """通过ID执行宏"""
        try:
            macro = self.get_macro(macro_id)
            if not macro:
                logger.error(f"宏不存在: {macro_id}")
                return False

            if not macro.enabled:
                logger.warning(f"宏已禁用: {macro.name}")
                return False

            logger.info(f"开始执行宏: {macro.name}, 重复次数: {repeat_count}")

            # 导入输入控制器（避免循环导入）
            from .input_controller import input_controller

            for repeat in range(repeat_count):
                if progress_callback:
                    progress_callback(repeat + 1, repeat_count, f"执行宏 {macro.name} 第{repeat + 1}次")

                for i, step in enumerate(macro.steps):
                    if not self._execute_step(step, input_controller):
                        logger.error(f"执行宏步骤失败: {macro.name}, 步骤 {i + 1}")
                        return False

            logger.info(f"宏执行完成: {macro.name}")
            return True

        except Exception as e:
            logger.error(f"执行宏失败: {e}")
            return False

    def _execute_step(self, step: MacroStep, input_controller) -> bool:
        """执行宏步骤"""
        try:
            if step.type == 'key':
                return self._execute_key_step(step, input_controller)
            elif step.type == 'delay':
                return input_controller.delay(step.delay or 0.1)
            elif step.type == 'click':
                return input_controller.click_at(step.x, step.y, step.button)
            elif step.type == 'text':
                return input_controller.type_text(step.text or "")
            else:
                logger.error(f"未知的步骤类型: {step.type}")
                return False

        except Exception as e:
            logger.error(f"执行步骤失败: {e}")
            return False

    def _execute_key_step(self, step: MacroStep, input_controller) -> bool:
        """执行按键步骤"""
        try:
            if not step.key:
                logger.error("按键步骤缺少键位配置")
                return False

            if step.press_type == "down":
                return input_controller.key_down(step.key)
            elif step.press_type == "up":
                return input_controller.key_up(step.key)
            else:  # press
                return input_controller.press_key(step.key, step.duration)

        except Exception as e:
            logger.error(f"执行按键步骤失败: {e}")
            return False

    def _execute_fallback_actions(self, repeat_count: int,
                                 progress_callback: Optional[Callable] = None) -> bool:
        """执行回退操作"""
        try:
            logger.info(f"执行回退操作，重复次数: {repeat_count}")

            from .input_controller import input_controller

            for repeat in range(repeat_count):
                if progress_callback:
                    progress_callback(repeat + 1, repeat_count, f"执行回退操作 第{repeat + 1}次")

                if not input_controller.execute_action_sequence(self.fallback_actions):
                    logger.error("执行回退操作序列失败")
                    return False

            logger.info("回退操作执行完成")
            return True

        except Exception as e:
            logger.error(f"执行回退操作失败: {e}")
            return False

    def get_macro(self, macro_id: str) -> Optional[MacroCommand]:
        """获取指定宏"""
        return self.macros.get(macro_id)

    def get_all_macros(self) -> List[MacroCommand]:
        """获取所有宏"""
        return list(self.macros.values())

    def _find_macro_by_name(self, name: str) -> Optional[str]:
        """根据名称查找宏ID"""
        for macro in self.macros.values():
            if macro.name == name:
                return macro.id
        return None

    def _get_macro_name(self, macro_id: str) -> str:
        """获取宏名称"""
        macro = self.get_macro(macro_id)
        return macro.name if macro else "未知宏"

    def create_macro(self, name: str, description: str = "",
                    category: str = "", steps_data: List[Dict[str, Any]] = None) -> Optional[MacroCommand]:
        """创建新宏"""
        try:
            macro_id = str(uuid.uuid4())

            # 解析步骤
            steps = []
            if steps_data:
                for i, step_data in enumerate(steps_data):
                    steps.append(MacroStep(**step_data))

            # 创建宏
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            macro = MacroCommand(
                id=macro_id,
                name=name,
                description=description,
                category=category,
                steps=steps,
                enabled=True,
                created_at=current_time,
                updated_at=current_time
            )

            # 保存宏
            self.macros[macro_id] = macro
            self._save_config()

            logger.info(f"已创建宏: {name}")
            return macro

        except Exception as e:
            logger.error(f"创建宏失败: {e}")
            return None

    def delete_macro(self, macro_id: str) -> bool:
        """删除宏"""
        try:
            if macro_id not in self.macros:
                logger.error(f"宏不存在: {macro_id}")
                return False

            macro_name = self.macros[macro_id].name
            del self.macros[macro_id]
            self._save_config()

            logger.info(f"已删除宏: {macro_name}")
            return True

        except Exception as e:
            logger.error(f"删除宏失败: {e}")
            return False

    def get_execution_history(self) -> List[MacroExecutionResult]:
        """获取执行历史"""
        return self.execution_history.copy()

    def clear_execution_history(self):
        """清空执行历史"""
        self.execution_history.clear()
        logger.info("执行历史已清空")

# 全局宏引擎实例
macro_engine = MacroEngine()