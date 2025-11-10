"""
配置管理模块
负责读取和管理游戏配置
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Tuple, Optional


class GameConfig:
    """游戏配置管理类"""

    def __init__(self, env_file: Optional[str] = None):
        """
        初始化配置

        Args:
            env_file: .env文件路径，默认为项目根目录下的.env
        """
        if env_file is None:
            env_file = Path(__file__).parent.parent.parent / ".env"

        load_dotenv(env_file)

        # 游戏窗口配置
        self.game_window_title = os.getenv("GAME_WINDOW_TITLE", "二重螺旋")
        self.game_process_name = os.getenv("GAME_PROCESS_NAME", "EM-Win64-Shipping.exe")

        # 游戏窗口分辨率配置
        self.game_window_width = int(os.getenv("GAME_WINDOW_WIDTH", "1920"))
        self.game_window_height = int(os.getenv("GAME_WINDOW_HEIGHT", "1080"))

        # 游戏窗口位置配置（可选）
        self.game_window_x = os.getenv("GAME_WINDOW_X")
        self.game_window_y = os.getenv("GAME_WINDOW_Y")
        if self.game_window_x:
            self.game_window_x = int(self.game_window_x)
        if self.game_window_y:
            self.game_window_y = int(self.game_window_y)

        # 屏幕分辨率配置（用于兼容性）
        self.screen_width = int(os.getenv("SCREEN_WIDTH", "1920"))
        self.screen_height = int(os.getenv("SCREEN_HEIGHT", "1080"))

        # 验证配置
        self._validate_config()

    def _validate_config(self):
        """验证配置的合理性"""
        if self.screen_width <= 0 or self.screen_height <= 0:
            raise ValueError("屏幕分辨率必须大于0")

        if self.game_window_width <= 0 or self.game_window_height <= 0:
            raise ValueError("游戏窗口分辨率必须大于0")

        if not self.game_window_title:
            raise ValueError("游戏窗口标题不能为空")

        if not self.game_process_name:
            raise ValueError("游戏进程名不能为空")

    def get_resolution(self) -> Tuple[int, int]:
        """获取屏幕分辨率"""
        return (self.screen_width, self.screen_height)

    def get_game_window_resolution(self) -> Tuple[int, int]:
        """获取游戏窗口分辨率"""
        return (self.game_window_width, self.game_window_height)

    def get_game_window_position(self) -> Optional[Tuple[int, int]]:
        """获取游戏窗口位置"""
        if self.game_window_x is not None and self.game_window_y is not None:
            return (self.game_window_x, self.game_window_y)
        return None

    def get_window_info(self) -> Tuple[str, str]:
        """获取窗口信息"""
        return (self.game_window_title, self.game_process_name)

    def __str__(self) -> str:
        return f"GameConfig(window='{self.game_window_title}', process='{self.game_process_name}', resolution={self.get_resolution()})"


# 全局配置实例
config = GameConfig()