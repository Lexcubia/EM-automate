"""
菜单配置管理模块
提供菜单配置的加载和管理功能
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class MenuConfigManager:
    """菜单配置管理器"""

    def __init__(self, config_path: str = None):
        """
        初始化菜单配置管理器

        Args:
            config_path: 配置文件路径，默认为 backend/config/menu_config.json
        """
        if config_path is None:
            current_dir = Path(__file__).parent.parent
            config_path = current_dir / "config" / "menu_config.json"

        self.config_path = Path(config_path)
        self.config_data = {}
        self._load_config()

    def _load_config(self) -> None:
        """加载配置文件"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
                logger.info("已加载菜单配置")
            else:
                logger.warning(f"菜单配置文件不存在: {self.config_path}")
                self._create_default_config()

        except Exception as e:
            logger.error(f"加载菜单配置失败: {e}")
            self._create_default_config()

    def _create_default_config(self) -> None:
        """创建默认配置"""
        self.config_data = {
            "missionTypes": {
                "scout_endless": "侦察",
                "avoidance": "避险",
                "expulsion": "驱逐",
                "explore_endless": "探险",
                "mediate": "调停",
                "drive_off": "驱离",
                "escort": "护送",
                "pursuit": "追缉",
                "defend_endless": "扼守",
                "migrate": "迁移",
                "character": "角色",
                "weapon": "武器",
                "magic_wedge": "魔之楔"
            },
            "menu": {
                "commission": {
                    "displayName": "委托",
                    "children": {
                        "daily_commission": {
                            "displayName": "委托",
                            "missions": []
                        },
                        "night_sailing_manual": {
                            "displayName": "夜航手册",
                            "missions": []
                        },
                        "commission_letter": {
                            "displayName": "委托密函",
                            "missions": []
                        }
                    }
                }
            }
        }
        self._save_config()

    def _save_config(self) -> None:
        """保存配置文件"""
        try:
            # 确保目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, ensure_ascii=False, indent=2)

            logger.info("菜单配置已保存")

        except Exception as e:
            logger.error(f"保存菜单配置失败: {e}")

    def get_menu_config(self) -> Dict[str, Any]:
        """获取完整菜单配置"""
        return self.config_data

    def get_mission_types(self) -> Dict[str, str]:
        """获取任务类型映射"""
        return self.config_data.get("missionTypes", {})

    def get_mission_type_display_name(self, mission_type: str) -> str:
        """获取任务类型的显示名称"""
        mission_types = self.get_mission_types()
        return mission_types.get(mission_type, mission_type)

    def get_main_categories(self) -> List[str]:
        """获取主分类列表"""
        menu = self.config_data.get("menu", {})
        return list(menu.keys())

    def get_main_category_keys(self) -> List[str]:
        """获取主分类键列表"""
        return self.get_main_categories()

    def get_sub_categories(self, main_category: str) -> Dict[str, Any]:
        """获取指定主分类的子分类"""
        menu = self.config_data.get("menu", {})
        main_section = menu.get(main_category, {})
        return main_section.get("children", {})

    def get_missions(self, main_category: str, sub_category: str) -> List[Dict[str, Any]]:
        """获取指定分类的任务列表"""
        sub_categories = self.get_sub_categories(main_category)
        sub_section = sub_categories.get(sub_category, {})
        return sub_section.get("missions", [])

    def update_menu_config(self, config_data: Dict[str, Any]) -> bool:
        """更新菜单配置"""
        try:
            self.config_data = config_data
            self._save_config()
            logger.info("菜单配置更新成功")
            return True
        except Exception as e:
            logger.error(f"更新菜单配置失败: {e}")
            return False

    def update_mission_types(self, mission_types: Dict[str, str]) -> bool:
        """更新任务类型映射"""
        try:
            self.config_data["missionTypes"] = mission_types
            self._save_config()
            logger.info("任务类型映射更新成功")
            return True
        except Exception as e:
            logger.error(f"更新任务类型映射失败: {e}")
            return False

    def update_menu_structure(self, menu_structure: Dict[str, Any]) -> bool:
        """更新菜单结构"""
        try:
            self.config_data["menu"] = menu_structure
            self._save_config()
            logger.info("菜单结构更新成功")
            return True
        except Exception as e:
            logger.error(f"更新菜单结构失败: {e}")
            return False

    def add_mission(self, main_category: str, sub_category: str, mission_data: Dict[str, Any]) -> bool:
        """添加新任务"""
        try:
            if "menu" not in self.config_data:
                self.config_data["menu"] = {}

            if main_category not in self.config_data["menu"]:
                self.config_data["menu"][main_category] = {
                    "displayName": main_category,
                    "children": {}
                }

            if "children" not in self.config_data["menu"][main_category]:
                self.config_data["menu"][main_category]["children"] = {}

            if sub_category not in self.config_data["menu"][main_category]["children"]:
                self.config_data["menu"][main_category]["children"][sub_category] = {
                    "displayName": sub_category,
                    "missions": []
                }

            self.config_data["menu"][main_category]["children"][sub_category]["missions"].append(mission_data)
            self._save_config()
            logger.info(f"任务添加成功: {main_category} -> {sub_category}")
            return True

        except Exception as e:
            logger.error(f"添加任务失败: {e}")
            return False

    def remove_mission(self, main_category: str, sub_category: str, mission_index: int) -> bool:
        """删除任务"""
        try:
            if (main_category in self.config_data.get("menu", {}) and
                sub_category in self.config_data["menu"][main_category].get("children", {})):

                missions = self.config_data["menu"][main_category]["children"][sub_category]["missions"]
                if 0 <= mission_index < len(missions):
                    missions.pop(mission_index)
                    self._save_config()
                    logger.info(f"任务删除成功: {main_category} -> {sub_category} -> 索引{mission_index}")
                    return True

            logger.warning(f"任务不存在: {main_category} -> {sub_category} -> 索引{mission_index}")
            return False

        except Exception as e:
            logger.error(f"删除任务失败: {e}")
            return False

    def validate_config(self) -> Dict[str, Any]:
        """验证配置文件完整性"""
        issues = []

        # 检查必需字段
        required_fields = ["missionTypes", "menu"]
        for field in required_fields:
            if field not in self.config_data:
                issues.append(f"缺少必需字段: {field}")

        # 检查菜单结构
        if "menu" in self.config_data:
            menu = self.config_data["menu"]
            for main_cat, main_data in menu.items():
                if "displayName" not in main_data:
                    issues.append(f"主分类 {main_cat} 缺少 displayName")
                if "children" not in main_data:
                    issues.append(f"主分类 {main_cat} 缺少 children")
                else:
                    for sub_cat, sub_data in main_data["children"].items():
                        if "displayName" not in sub_data:
                            issues.append(f"子分类 {main_cat}->{sub_cat} 缺少 displayName")
                        if "missions" not in sub_data:
                            issues.append(f"子分类 {main_cat}->{sub_cat} 缺少 missions")

        return {
            "valid": len(issues) == 0,
            "issues": issues
        }

    def export_config(self, file_path: str) -> bool:
        """导出配置到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, ensure_ascii=False, indent=2)
            logger.info(f"菜单配置已导出到: {file_path}")
            return True
        except Exception as e:
            logger.error(f"导出菜单配置失败: {e}")
            return False

    def import_config(self, file_path: str) -> bool:
        """从文件导入配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            # 验证导入的配置
            temp_manager = MenuConfigManager()
            temp_manager.config_data = config_data
            validation = temp_manager.validate_config()

            if not validation["valid"]:
                logger.error(f"导入的配置文件无效: {validation['issues']}")
                return False

            self.config_data = config_data
            self._save_config()
            logger.info(f"菜单配置已从文件导入: {file_path}")
            return True

        except Exception as e:
            logger.error(f"导入菜单配置失败: {e}")
            return False


# 全局菜单配置管理器实例
menu_config_manager = MenuConfigManager()