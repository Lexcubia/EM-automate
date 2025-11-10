"""
二重螺旋游戏自动化脚本 - 优化后的核心模块

模块架构：
- config.py: 配置管理
- window_manager.py: 窗口管理
- input_controller.py: 统一输入控制
- utils/: 工具模块包
  - image_recognition.py: 图像识别
  - coordinate_parser.py: 坐标解析
- macro_engine.py: 统一宏引擎
- game_navigator.py: 游戏导航器
- task_executor.py: 任务执行器
"""

# 核心配置和管理
from .config import config
from .window_manager import WindowManager

# 输入和控制
from .input_controller import InputController, input_controller

# 工具模块
from .utils import ImageRecognition, CoordinateParser

# 核心功能模块
from .macro_engine import (
    MacroEngine, macro_engine,
    MacroCommand, MacroStep, MacroExecutionResult
)
from .game_navigator import GameNavigator, game_navigator
from .task_executor import (
    TaskExecutor, task_executor,
    Task, TaskCategory, TaskFactory
)

__all__ = [
    # 配置和窗口
    'config',
    'WindowManager',

    # 输入控制
    'InputController',
    'input_controller',

    # 工具模块
    'ImageRecognition',
    'CoordinateParser',

    # 宏引擎
    'MacroEngine',
    'macro_engine',
    'MacroCommand',
    'MacroStep',
    'MacroExecutionResult',

    # 导航器
    'GameNavigator',
    'game_navigator',

    # 任务执行器
    'TaskExecutor',
    'task_executor',
    'Task',
    'TaskCategory',
    'TaskFactory'
]