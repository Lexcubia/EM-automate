"""
键盘映射配置管理模块
提供键位配置的加载、保存、验证和执行功能
"""
import json
import os
from typing import Dict, Optional, List, Tuple
from pathlib import Path
import logging
from pydantic import BaseModel, Field, validator
from pyautogui import keyDown, keyUp, press, mouseDown, mouseUp, click

logger = logging.getLogger(__name__)


class KeyBindingProfile(BaseModel):
    """键位配置文件模型"""
    name: str = Field(..., description="配置文件名称")
    description: str = Field("", description="配置文件描述")
    bindings: Dict[str, str] = Field(..., description="键位映射")


class KeyBindingsManager:
    """键盘映射管理器 - 单配置模式"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化键位管理器

        Args:
            config_path: 配置文件路径，默认为 backend/config/keybindings.json
        """
        if config_path is None:
            current_dir = Path(__file__).parent.parent
            config_path = current_dir / "config" / "keybindings.json"

        self.config_path = Path(config_path)
        self.config_data = {}
        self._load_config()

    def _load_config(self) -> None:
        """加载配置文件"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
            else:
                logger.warning(f"配置文件不存在: {self.config_path}")
                self._create_default_config()

            logger.info("已加载键位配置")

        except Exception as e:
            logger.error(f"加载键位配置失败: {e}")
            self._create_default_config()

    def _create_default_config(self) -> None:
        """创建默认配置"""
        self.config_data = {
            "bindings": {
                "melee_attack": "left_mouse",
                "ranged_attack": "right_mouse",
                "skill": "E",
                "ultimate": "Q",
                "spirit_support": "Z",
                "jump": "space",
                "slide_crouch": "lctrl",
                "dodge": "lshift",
                "revive": "X",
                "reload": "R",
                "backpack": "B",
                "interact": "F",
                "training": "L",
                "map": "M",
                "tactical_backpack": "tab",
                "abandon_challenge": "P",
                "move_forward": "W",
                "move_backward": "S",
                "move_left": "A",
                "move_right": "D"
            },
            "action_names": {
                "melee_attack": "近战攻击",
                "ranged_attack": "远程攻击",
                "skill": "战技",
                "ultimate": "终结技",
                "spirit_support": "魔灵支援",
                "jump": "跳跃",
                "slide_crouch": "滑行/下蹲",
                "dodge": "闪避",
                "revive": "复苏",
                "reload": "装填子弹",
                "backpack": "背包",
                "interact": "交互",
                "training": "历练",
                "map": "地图",
                "tactical_backpack": "战术背包",
                "abandon_challenge": "放弃挑战",
                "move_forward": "前进",
                "move_backward": "后退",
                "move_left": "左移",
                "move_right": "右移"
            },
            "key_names": {
                "left_mouse": "鼠标左键",
                "right_mouse": "鼠标右键",
                "middle_mouse": "鼠标中键",
                "space": "空格",
                "lctrl": "左Ctrl",
                "rctrl": "右Ctrl",
                "lshift": "左Shift",
                "rshift": "右Shift",
                "lalt": "左Alt",
                "ralt": "右Alt",
                "tab": "Tab",
                "enter": "回车",
                "escape": "Esc",
                "backspace": "退格",
                "delete": "Delete",
                "up": "上箭头",
                "down": "下箭头",
                "left": "左箭头",
                "right": "右箭头"
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

            logger.info("键位配置已保存")

        except Exception as e:
            logger.error(f"保存键位配置失败: {e}")

    def get_current_bindings(self) -> Dict[str, str]:
        """获取当前键位映射"""
        return self.config_data.get("bindings", {})

    def get_binding(self, action: str) -> Optional[str]:
        """获取指定动作的键位"""
        bindings = self.get_current_bindings()
        return bindings.get(action)

    def set_binding(self, action: str, key: str) -> bool:
        """设置指定动作的键位"""
        try:
            # 检查键位冲突
            if self._check_key_conflict(action, key):
                logger.warning(f"键位冲突: {key} 已被其他动作使用")
                return False

            # 更新配置
            if "bindings" not in self.config_data:
                self.config_data["bindings"] = {}

            self.config_data["bindings"][action] = key
            self._save_config()

            logger.info(f"已设置键位: {action} -> {key}")
            return True

        except Exception as e:
            logger.error(f"设置键位失败: {e}")
            return False

    def _check_key_conflict(self, current_action: str, new_key: str) -> bool:
        """检查键位冲突"""
        bindings = self.get_current_bindings()
        for action, key in bindings.items():
            if action != current_action and key == new_key:
                return True
        return False

    def execute_action(self, action: str, press_type: str = "press", duration: float = 0.1) -> bool:
        """执行指定动作的键位操作"""
        try:
            key = self.get_binding(action)
            if not key:
                logger.warning(f"未找到动作 {action} 的键位配置")
                return False

            return self._execute_key(key, press_type, duration)

        except Exception as e:
            logger.error(f"执行动作失败 {action}: {e}")
            return False

    def _execute_key(self, key: str, press_type: str, duration: float) -> bool:
        """执行具体的键位操作"""
        try:
            # 处理鼠标按键
            if key.endswith("_mouse"):
                button = key.split("_")[0]
                if press_type == "press":
                    click(button=button)
                elif press_type == "down":
                    mouseDown(button=button)
                elif press_type == "up":
                    mouseUp(button=button)
            else:
                # 处理键盘按键
                if press_type == "press":
                    press(key)
                elif press_type == "down":
                    keyDown(key)
                elif press_type == "up":
                    keyUp(key)

            return True

        except Exception as e:
            logger.error(f"执行键位操作失败 {key}: {e}")
            return False

    def get_action_names(self) -> Dict[str, str]:
        """获取动作名称映射"""
        return self.config_data.get("action_names", {})

    def get_key_names(self) -> Dict[str, str]:
        """获取键位名称映射"""
        return self.config_data.get("key_names", {})

    def export_config(self, file_path: str) -> bool:
        """导出当前配置"""
        try:
            config_data = {
                "bindings": self.get_current_bindings(),
                "action_names": self.get_action_names(),
                "key_names": self.get_key_names(),
                "version": "1.0",
                "exported_at": str(Path(__file__).stat().st_mtime)
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)

            logger.info(f"已导出配置到: {file_path}")
            return True

        except Exception as e:
            logger.error(f"导出配置失败: {e}")
            return False

    def import_config(self, file_path: str) -> bool:
        """导入配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            if "bindings" not in config_data:
                logger.error("配置文件格式错误：缺少 bindings 字段")
                return False

            # 更新配置
            self.config_data["bindings"] = config_data["bindings"]

            # 可选更新名称映射
            if "action_names" in config_data:
                self.config_data["action_names"] = config_data["action_names"]

            if "key_names" in config_data:
                self.config_data["key_names"] = config_data["key_names"]

            self._save_config()
            logger.info("已导入配置")
            return True

        except Exception as e:
            logger.error(f"导入配置失败: {e}")
            return False

    def reset_to_default(self) -> bool:
        """重置为默认配置"""
        try:
            self._create_default_config()
            logger.info("已重置为默认配置")
            return True
        except Exception as e:
            logger.error(f"重置配置失败: {e}")
            return False


# 全局键位管理器实例
keybindings_manager = KeyBindingsManager()