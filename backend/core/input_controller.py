"""
输入控制器 - 统一所有输入操作
合并了来自 automation.py, macros.py, enhanced_macros.py 的输入功能
"""
import time
import pyautogui
import logging
from typing import Optional, Tuple, Dict, Any, List
from .window_manager import WindowManager
from .utils.image_recognition import ImageRecognition

logger = logging.getLogger(__name__)

class InputController:
    """统一输入控制器 - 简单直接的输入操作"""

    def __init__(self):
        """初始化输入控制器"""
        # 设置pyautogui安全设置
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1

        # 初始化依赖组件
        self.window_manager = WindowManager()
        self.image_recognition = ImageRecognition()

        logger.info("输入控制器初始化完成")

    def click_at(self, x: int, y: int, button: str = "left",
                 clicks: int = 1, interval: float = 0.0) -> bool:
        """
        在指定坐标点击

        Args:
            x, y: 坐标
            button: 鼠标按钮 (left/right/middle)
            clicks: 点击次数
            interval: 点击间隔

        Returns:
            是否成功点击
        """
        try:
            # 确保窗口激活
            self.window_manager.activate_window()

            # 转换为屏幕坐标
            screen_x, screen_y = self.window_manager.window_to_screen_coords(x, y)

            # 执行点击
            pyautogui.click(screen_x, screen_y, button=button,
                           clicks=clicks, interval=interval)

            logger.debug(f"点击坐标: ({x}, {y}) -> 屏幕: ({screen_x}, {screen_y})")
            return True

        except Exception as e:
            logger.error(f"点击失败: {e}")
            return False

    def click_image(self, image_name: str, confidence: float = 0.8,
                   button: str = "left") -> bool:
        """
        点击指定图像

        Args:
            image_name: 图像文件名
            confidence: 匹配置信度
            button: 鼠标按钮

        Returns:
            是否成功点击
        """
        try:
            position = self.image_recognition.find_image(image_name, confidence)
            if position:
                return self.click_at(position[0], position[1], button)
            return False

        except Exception as e:
            logger.error(f"点击图像失败: {e}")
            return False

    def press_key(self, key: str, duration: Optional[float] = None) -> bool:
        """
        按下按键

        Args:
            key: 按键名称
            duration: 按键持续时间（秒）

        Returns:
            是否成功按下
        """
        try:
            if duration and duration > 0.1:
                # 长按
                pyautogui.keyDown(key)
                pyautogui.sleep(duration)
                pyautogui.keyUp(key)
            else:
                # 短按
                pyautogui.press(key)

            logger.debug(f"按键: {key}" + (f" (持续{duration}秒)" if duration else ""))
            return True

        except Exception as e:
            logger.error(f"按键失败: {e}")
            return False

    def key_down(self, key: str) -> bool:
        """按下按键（不释放）"""
        try:
            pyautogui.keyDown(key)
            logger.debug(f"按下按键: {key}")
            return True
        except Exception as e:
            logger.error(f"按下按键失败: {e}")
            return False

    def key_up(self, key: str) -> bool:
        """释放按键"""
        try:
            pyautogui.keyUp(key)
            logger.debug(f"释放按键: {key}")
            return True
        except Exception as e:
            logger.error(f"释放按键失败: {e}")
            return False

    def type_text(self, text: str, interval: float = 0.1) -> bool:
        """
        输入文本

        Args:
            text: 要输入的文本
            interval: 每个字符之间的间隔

        Returns:
            是否成功输入
        """
        try:
            pyautogui.typewrite(text, interval=interval)
            logger.debug(f"输入文本: {text}")
            return True

        except Exception as e:
            logger.error(f"输入文本失败: {e}")
            return False

    def move_mouse(self, x: int, y: int, duration: float = 0.0) -> bool:
        """
        移动鼠标到指定坐标

        Args:
            x, y: 坐标
            duration: 移动持续时间

        Returns:
            是否成功移动
        """
        try:
            # 转换为屏幕坐标
            screen_x, screen_y = self.window_manager.window_to_screen_coords(x, y)
            pyautogui.moveTo(screen_x, screen_y, duration=duration)

            logger.debug(f"移动鼠标: ({x}, {y}) -> 屏幕: ({screen_x}, {screen_y})")
            return True

        except Exception as e:
            logger.error(f"移动鼠标失败: {e}")
            return False

    def delay(self, seconds: float) -> bool:
        """
        延迟等待

        Args:
            seconds: 延迟时间（秒）

        Returns:
            是否成功延迟
        """
        try:
            if seconds <= 0:
                logger.warning(f"延迟时间无效: {seconds}")
                return False

            pyautogui.sleep(seconds)
            logger.debug(f"延迟: {seconds}秒")
            return True

        except Exception as e:
            logger.error(f"延迟失败: {e}")
            return False

    def execute_action_sequence(self, actions: List[Dict[str, Any]]) -> bool:
        """
        执行动作序列

        Args:
            actions: 动作列表，每个动作包含类型和参数

        Returns:
            是否全部成功执行
        """
        try:
            for i, action in enumerate(actions):
                action_type = action.get('type')

                if action_type == 'key':
                    key = action.get('key')
                    duration = action.get('duration')
                    press_type = action.get('press_type', 'press')

                    if not key:
                        logger.error(f"动作 {i+1}: 按键动作缺少键位")
                        return False

                    if press_type == 'down':
                        if not self.key_down(key):
                            return False
                    elif press_type == 'up':
                        if not self.key_up(key):
                            return False
                    else:  # press
                        if not self.press_key(key, duration):
                            return False

                elif action_type == 'click':
                    x = action.get('x')
                    y = action.get('y')
                    button = action.get('button', 'left')
                    clicks = action.get('clicks', 1)

                    if x is None or y is None:
                        logger.error(f"动作 {i+1}: 点击动作缺少坐标")
                        return False

                    if not self.click_at(x, y, button, clicks):
                        return False

                elif action_type == 'delay':
                    delay = action.get('delay', 0)
                    if not self.delay(delay):
                        return False

                elif action_type == 'text':
                    text = action.get('text', '')
                    interval = action.get('interval', 0.1)
                    if not self.type_text(text, interval):
                        return False

                else:
                    logger.error(f"动作 {i+1}: 未知动作类型 {action_type}")
                    return False

            logger.debug(f"成功执行 {len(actions)} 个动作")
            return True

        except Exception as e:
            logger.error(f"执行动作序列失败: {e}")
            return False

    def wait_for_image(self, image_name: str, timeout: float = 10.0,
                      confidence: float = 0.8) -> bool:
        """
        等待图像出现

        Args:
            image_name: 图像文件名
            timeout: 超时时间
            confidence: 匹配置信度

        Returns:
            是否找到图像
        """
        return self.image_recognition.wait_for_image(image_name, timeout, confidence)

    def get_mouse_position(self) -> Optional[Tuple[int, int]]:
        """
        获取当前鼠标位置（窗口坐标）

        Returns:
            鼠标位置 (x, y)
        """
        try:
            screen_x, screen_y = pyautogui.position()
            return self.window_manager.screen_to_window_coords(screen_x, screen_y)
        except Exception as e:
            logger.error(f"获取鼠标位置失败: {e}")
            return None

# 全局输入控制器实例
input_controller = InputController()