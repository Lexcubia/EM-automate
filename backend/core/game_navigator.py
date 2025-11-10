"""
游戏导航器 - 简化配置驱动的导航系统
合并了 navigation.py 的核心功能，去除不必要的复杂性
"""
import time
import logging
import json
from typing import Dict, Tuple, Any, Optional
from pathlib import Path
from .window_manager import WindowManager
from .input_controller import input_controller
from .utils.coordinate_parser import CoordinateParser
from .utils.image_recognition import ImageRecognition

logger = logging.getLogger(__name__)

class GameNavigator:
    """游戏导航器 - 简单直接的配置驱动导航"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化导航器

        Args:
            config_path: 配置文件路径，默认为 backend/config/coordinates.json
        """
        self.window_manager = WindowManager()
        self.coord_parser = CoordinateParser()
        self.image_recognition = ImageRecognition()

        # 加载配置
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "coordinates.json"

        self.config = self._load_config(config_path)

        if self.config:
            logger.info("游戏导航器初始化成功")
        else:
            logger.warning("导航器配置加载失败，将使用基础导航模式")

    def _load_config(self, config_path: str) -> Optional[Dict[str, Any]]:
        """加载配置文件"""
        try:
            if not Path(config_path).exists():
                logger.warning(f"导航配置文件不存在: {config_path}")
                return None

            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 验证基本配置
            if 'tabs' not in config:
                logger.warning("配置文件缺少 tabs 配置")
                return None

            logger.info(f"导航配置加载成功: {config_path}")
            return config

        except Exception as e:
            logger.error(f"导航配置加载失败: {e}")
            return None

    def navigate_to_dungeon(self, mission_info: Dict[str, Any]) -> bool:
        """
        导航到指定副本

        Args:
            mission_info: 任务信息，包含 mission_type 和 selected_level

        Returns:
            是否成功导航
        """
        try:
            mission_type = mission_info.get("mission_type", "")
            selected_level = mission_info.get("selected_level", "")

            logger.info(f"导航到副本: {mission_type} -> {selected_level}")

            # 如果没有配置，使用简单导航
            if not self.config:
                return self._simple_navigate(mission_type, selected_level)

            # 激活窗口
            if not self.window_manager.activate_window():
                logger.error("激活游戏窗口失败")
                return False

            # 导航到标签页
            if not self.navigate_to_tab(mission_type):
                logger.error(f"导航到标签页失败: {mission_type}")
                return False

            # 选择等级（如果需要）
            if mission_type == "night_sailing" and selected_level:
                if not self.select_night_sailing_level(selected_level):
                    logger.error(f"选择夜航等级失败: {selected_level}")
                    return False

            # 进入副本
            if not self.perform_action("enter_dungeon"):
                logger.error("进入副本失败")
                return False

            logger.info(f"导航完成: {mission_type} -> {selected_level}")
            return True

        except Exception as e:
            logger.error(f"导航失败: {e}")
            return False

    def navigate_to_tab(self, tab_name: str) -> bool:
        """
        导航到指定标签页

        Args:
            tab_name: 标签名称

        Returns:
            是否成功导航
        """
        try:
            if not self.config or 'tabs' not in self.config:
                return self._simple_tab_navigation(tab_name)

            tabs_config = self.config['tabs']
            if tab_name not in tabs_config:
                logger.error(f"不支持的标签: {tab_name}")
                return False

            tab_config = tabs_config[tab_name]

            # 获取点击位置
            position = tab_config.get('position', [])
            if not position:
                logger.error(f"标签 {tab_name} 缺少位置配置")
                return False

            center_x, center_y = self.coord_parser.get_center(position)

            # 点击标签
            if not input_controller.click_at(center_x, center_y):
                logger.error(f"点击标签失败: {tab_name}")
                return False

            # 等待页面切换
            time.sleep(2.0)

            # 验证是否成功切换（如果有验证图像）
            active_image = tab_config.get('images', {}).get('active')
            if active_image:
                if self.image_recognition.find_image(active_image, confidence=0.8):
                    logger.info(f"成功切换到 {tab_config.get('name', tab_name)} 标签")
                    return True
                else:
                    logger.warning(f"标签切换验证失败: {tab_name}")
                    return False

            # 没有验证图像，默认成功
            logger.info(f"切换到标签: {tab_name}")
            return True

        except Exception as e:
            logger.error(f"导航到标签失败 {tab_name}: {e}")
            return False

    def select_night_sailing_level(self, level: str) -> bool:
        """
        选择夜航手册等级

        Args:
            level: 等级字符串（如 "LV20"）

        Returns:
            是否成功选择
        """
        try:
            if not self.config:
                return self._simple_level_selection(level)

            levels_config = self.config.get('night_sailing_levels', {}).get('levels', {})
            if level not in levels_config:
                logger.error(f"不支持的夜航等级: {level}")
                return False

            level_position = levels_config[level]
            level_x, level_y = self.coord_parser.get_center(level_position)

            # 点击等级
            if not input_controller.click_at(level_x, level_y):
                logger.error(f"点击等级失败: {level}")
                return False

            time.sleep(1.0)
            logger.info(f"选择夜航等级: {level}")
            return True

        except Exception as e:
            logger.error(f"选择夜航等级失败 {level}: {e}")
            return False

    def perform_action(self, action_name: str) -> bool:
        """
        执行预定义动作

        Args:
            action_name: 动作名称

        Returns:
            是否成功执行
        """
        try:
            if not self.config:
                return self._simple_action(action_name)

            actions = self.config.get('actions', {})
            if action_name not in actions:
                logger.warning(f"不支持的动作: {action_name}，使用简单执行")
                return self._simple_action(action_name)

            action_config = actions[action_name]
            position = action_config.get('position', [])

            if not position:
                logger.error(f"动作 {action_name} 缺少位置配置")
                return False

            x, y = self.coord_parser.get_center(position)
            success = input_controller.click_at(x, y)

            if success:
                logger.debug(f"执行动作: {action_config.get('description', action_name)}")

            return success

        except Exception as e:
            logger.error(f"执行动作失败 {action_name}: {e}")
            return False

    def _simple_navigate(self, mission_type: str, selected_level: str) -> bool:
        """简单导航逻辑（备用方案）"""
        logger.info(f"简单导航模式: {mission_type} -> {selected_level}")

        # 激活窗口
        if not self.window_manager.activate_window():
            return False

        # 模拟导航时间
        time.sleep(2.0)

        # 根据任务类型执行不同的按键序列
        if mission_type == "commission":
            input_controller.press_key('tab')  # 切换到委托标签
            time.sleep(1.0)
        elif mission_type == "night_sailing":
            input_controller.press_key('tab', 0.2)  # 切换到夜航标签
            input_controller.press_key('tab', 0.2)
            time.sleep(1.0)
        elif mission_type == "commission_letter":
            input_controller.press_key('tab', 0.2)  # 切换到委托密函标签
            input_controller.press_key('tab', 0.2)
            input_controller.press_key('tab', 0.2)
            time.sleep(1.0)

        # 选择等级（如果需要）
        if mission_type == "night_sailing" and selected_level:
            input_controller.press_key('down')  # 选择等级
            time.sleep(0.5)

        # 进入副本
        input_controller.press_key('enter')
        time.sleep(1.0)

        return True

    def _simple_tab_navigation(self, tab_name: str) -> bool:
        """简单标签导航"""
        logger.info(f"简单标签导航: {tab_name}")

        # 根据标签名称使用不同的按键次数
        tab_mappings = {
            'commission': 1,
            'night_sailing': 2,
            'commission_letter': 3
        }

        presses = tab_mappings.get(tab_name, 1)
        for _ in range(presses):
            input_controller.press_key('tab')
            time.sleep(0.3)

        return True

    def _simple_level_selection(self, level: str) -> bool:
        """简单等级选择"""
        logger.info(f"简单等级选择: {level}")

        # 提取等级数字
        if level.startswith('LV'):
            level_num = level[2:]
            try:
                level_int = int(level_num)
                # 根据等级数字按键次数选择
                for _ in range(level_int - 1):  # LV1 不需要按键
                    input_controller.press_key('down')
                    time.sleep(0.2)
            except ValueError:
                logger.warning(f"无法解析等级: {level}")

        return True

    def _simple_action(self, action_name: str) -> bool:
        """简单动作执行"""
        logger.info(f"简单动作执行: {action_name}")

        action_mappings = {
            'enter_dungeon': 'enter',
            'start_mission': 'enter',
            'confirm': 'space',
            'cancel': 'esc'
        }

        key = action_mappings.get(action_name, 'enter')
        input_controller.press_key(key)
        time.sleep(0.5)

        return True

    def is_at_navigation_page(self) -> bool:
        """检查是否在导航页面"""
        if not self.config:
            # 简单检查：假设在导航页面
            return True

        location_image = self.config.get('navigation', {}).get('location_image')
        if not location_image:
            logger.warning("配置中未找到 location_image")
            return True  # 默认认为在导航页面

        return self.image_recognition.find_image(location_image, confidence=0.7)

    def get_window_info(self) -> Dict[str, Any]:
        """获取窗口信息"""
        return self.window_manager.get_window_info()

    def refresh_window(self) -> bool:
        """刷新窗口"""
        return self.window_manager.refresh_window()

    def get_available_tabs(self) -> Dict[str, str]:
        """获取可用的标签页"""
        if not self.config or 'tabs' not in self.config:
            return {}

        return {key: tab.get('name', key) for key, tab in self.config['tabs'].items()}

    def get_available_levels(self) -> list:
        """获取可用的夜航等级"""
        if not self.config:
            return []

        levels_config = self.config.get('night_sailing_levels', {}).get('levels', {})
        return list(levels_config.keys())

# 全局导航器实例
game_navigator = GameNavigator()