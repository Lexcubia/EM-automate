"""
菜单管理模块
负责加载和管理游戏任务菜单配置
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class LevelInfo:
    """等级信息"""
    key: str
    displayName: str


@dataclass
class MissionInfo:
    """任务信息"""
    key: str
    displayName: str
    type: str
    levels: List[LevelInfo]


@dataclass
class CategoryInfo:
    """分类信息"""
    key: str
    displayName: str
    missions: Dict[str, MissionInfo]


@dataclass
class SubCategoryInfo:
    """子分类信息"""
    key: str
    displayName: str
    children: Dict[str, MissionInfo]


class MenuManager:
    """菜单管理器"""

    def __init__(self, config_file: Optional[str] = None):
        """
        初始化菜单管理器

        Args:
            config_file: 菜单配置文件路径，默认为config目录下的menu_config.json
        """
        if config_file is None:
            config_file = Path(__file__).parent.parent / "config" / "menu_config.json"

        self.config_file = config_file
        self.mission_types = {}
        self.menu_structure = {}
        self.load_config()

    def load_config(self):
        """加载菜单配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self.mission_types = config.get('missionTypes', {})
            self.menu_structure = config.get('menu', {})

        except FileNotFoundError:
            # 配置文件不存在时，使用默认配置
            print(f"警告: 菜单配置文件未找到: {self.config_file}")
            print("使用默认菜单配置")
            self._load_default_config()
        except json.JSONDecodeError as e:
            print(f"警告: 菜单配置文件格式错误: {e}")
            print("使用默认菜单配置")
            self._load_default_config()
        except Exception as e:
            print(f"警告: 加载菜单配置失败: {e}")
            print("使用默认菜单配置")
            self._load_default_config()

    def _load_default_config(self):
        """加载默认菜单配置"""
        # 基于coordinates.json中的tabs配置生成默认菜单
        self.mission_types = {
            "commission": "委托",
            "night_sailing": "夜航手册",
            "commission_letter": "委托密函"
        }

        self.menu_structure = {
            "game_missions": {
                "displayName": "游戏任务",
                "children": {
                    "daily_missions": {
                        "displayName": "日常任务",
                        "missions": [
                            {
                                "key": "commission",
                                "displayName": "委托",
                                "type": "commission",
                                "levels": []
                            },
                            {
                                "key": "night_sailing",
                                "displayName": "夜航手册",
                                "type": "night_sailing",
                                "levels": [
                                    {"key": "LV20", "displayName": "LV20"},
                                    {"key": "LV30", "displayName": "LV30"},
                                    {"key": "LV40", "displayName": "LV40"},
                                    {"key": "LV50", "displayName": "LV50"},
                                    {"key": "LV55", "displayName": "LV55"},
                                    {"key": "LV60", "displayName": "LV60"},
                                    {"key": "LV65", "displayName": "LV65"},
                                    {"key": "LV70", "displayName": "LV70"},
                                    {"key": "LV80", "displayName": "LV80"}
                                ]
                            },
                            {
                                "key": "commission_letter",
                                "displayName": "委托密函",
                                "type": "commission_letter",
                                "levels": []
                            }
                        ]
                    }
                }
            }
        }

    def get_main_categories(self) -> List[str]:
        """获取主分类显示名称列表"""
        return [data.get('displayName', key) for key, data in self.menu_structure.items()]

    def get_main_category_keys(self) -> List[str]:
        """获取主分类key列表"""
        return list(self.menu_structure.keys())

    def get_sub_categories(self, main_category_key: str) -> Dict[str, SubCategoryInfo]:
        """
        获取指定主分类下的子分类

        Args:
            main_category_key: 主分类key

        Returns:
            子分类字典
        """
        if main_category_key not in self.menu_structure:
            return {}

        main_data = self.menu_structure[main_category_key]
        sub_categories = {}

        for sub_key, sub_data in main_data.get('children', {}).items():
            category_info = SubCategoryInfo(
                key=sub_key,
                displayName=sub_data.get('displayName', sub_key),
                children={}
            )

            missions_data = sub_data.get('missions', [])
            for mission_data in missions_data:
                mission_key = mission_data.get('key', '')
                levels_data = mission_data.get('levels', [])

                # 转换等级数据
                levels = []
                for level_data in levels_data:
                    level_info = LevelInfo(
                        key=level_data.get('key', ''),
                        displayName=level_data.get('displayName', '')
                    )
                    levels.append(level_info)

                mission_info = MissionInfo(
                    key=mission_key,
                    displayName=mission_data.get('displayName', ''),
                    type=mission_data.get('type', ''),
                    levels=levels
                )
                category_info.children[mission_key] = mission_info

            sub_categories[sub_key] = category_info

        return sub_categories

    def get_all_missions(self) -> List[MissionInfo]:
        """获取所有任务列表"""
        all_missions = []

        for main_category_key in self.get_main_category_keys():
            sub_categories = self.get_sub_categories(main_category_key)
            for sub_category in sub_categories.values():
                for mission in sub_category.children.values():
                    all_missions.append(mission)

        return all_missions

    def get_mission_by_path(self, main_category_key: str, sub_category_key: str, mission_key: str) -> Optional[MissionInfo]:
        """
        根据路径获取任务信息

        Args:
            main_category_key: 主分类key
            sub_category_key: 子分类key
            mission_key: 任务key

        Returns:
            任务信息，如果未找到返回None
        """
        sub_categories = self.get_sub_categories(main_category_key)
        if sub_category_key not in sub_categories:
            return None

        return sub_categories[sub_category_key].children.get(mission_key)

    def get_subcategory_missions(self, main_category_key: str, sub_category_key: str) -> List[Dict[str, Any]]:
        """
        获取指定子分类下的所有任务（简化版，直接返回原始数据）

        Args:
            main_category_key: 主分类key
            sub_category_key: 子分类key

        Returns:
            任务列表
        """
        if main_category_key not in self.menu_structure:
            return []

        main_data = self.menu_structure[main_category_key]
        children = main_data.get('children', {})

        if sub_category_key not in children:
            return []

        sub_data = children[sub_category_key]
        return sub_data.get('missions', [])

    def get_mission_type_display_name(self, mission_type: str) -> str:
        """
        获取任务类型的显示名称

        Args:
            mission_type: 任务类型英文标识

        Returns:
            任务类型中文显示名称
        """
        return self.mission_types.get(mission_type, mission_type)

    def validate_mission_selection(self, selections: Dict[str, Any]) -> bool:
        """
        验证任务选择的有效性

        Args:
            selections: 用户选择的任务配置

        Returns:
            是否有效
        """
        # TODO: 实现选择验证逻辑
        return True

    def export_selections(self, selections: Dict[str, Any]) -> str:
        """
        导出用户选择为JSON字符串

        Args:
            selections: 用户选择的任务配置

        Returns:
            JSON格式的选择配置
        """
        return json.dumps(selections, ensure_ascii=False, indent=2)

    def __str__(self) -> str:
        return f"MenuManager(main_categories={self.get_main_categories()})"


# 创建默认实例，但允许失败
def create_menu_manager() -> MenuManager:
    """创建菜单管理器实例"""
    try:
        return MenuManager()
    except Exception as e:
        print(f"创建菜单管理器失败: {e}")
        # 创建一个最小可用实例
        manager = MenuManager.__new__(MenuManager)
        manager.mission_types = {
            "commission": "委托",
            "night_sailing": "夜航手册",
            "commission_letter": "委托密函"
        }
        manager.menu_structure = {}
        manager.config_file = ""
        return manager