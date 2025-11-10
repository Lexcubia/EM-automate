"""
游戏窗口管理器
负责窗口检测、定位和坐标转换
"""
import logging
import time
from typing import Optional, Tuple, Dict, Any
import pyautogui
import pygetwindow as gw
from .config import config

# Windows API 导入（用于获取客户端区域大小）
try:
    import win32gui
    import win32api
    import win32con
    WINDOWS_API_AVAILABLE = True
except ImportError:
    WINDOWS_API_AVAILABLE = False
    logger.warning("Windows API 不可用，将使用 pygetwindow 的窗口大小（包含边框）")

logger = logging.getLogger(__name__)


class WindowManager:
    """游戏窗口管理器"""

    def __init__(self):
        """初始化窗口管理器"""
        self.window_title = config.game_window_title
        self.process_name = config.game_process_name
        self.window_resolution = config.get_game_window_resolution()
        self.window_position = config.get_game_window_position()

        self._window = None
        self._window_bounds = None

        # 初始化时查找窗口
        self._find_game_window()

    def _find_game_window(self) -> bool:
        """
        查找游戏窗口

        Returns:
            是否找到窗口
        """
        try:
            # 尝试精确匹配窗口标题
            windows = gw.getWindowsWithTitle(self.window_title)

            if windows:
                self._window = windows[0]
                logger.info(f"找到游戏窗口: {self.window_title}")
            else:
                # 如果精确匹配失败，尝试模糊匹配
                all_windows = gw.getAllWindows()
                for window in all_windows:
                    if self.window_title in window.title:
                        self._window = window
                        logger.info(f"模糊匹配找到游戏窗口: {window.title}")
                        break

                if not self._window:
                    logger.warning(f"未找到游戏窗口: {self.window_title}")
                    return False

            # 获取窗口边界
            self._update_window_bounds()
            return True

        except Exception as e:
            logger.error(f"查找游戏窗口失败: {e}")
            return False

    def _update_window_bounds(self):
        """更新窗口边界信息"""
        if self._window:
            # 获取窗口句柄
            hwnd = self._get_window_hwnd()

            if hwnd and WINDOWS_API_AVAILABLE:
                # 使用 Windows API 获取客户端区域大小
                try:
                    # 获取窗口矩形（包含边框）
                    window_rect = win32gui.GetWindowRect(hwnd)
                    left, top, right, bottom = window_rect

                    # 获取客户端矩形（不包含边框和标题栏）
                    client_rect = win32gui.GetClientRect(hwnd)
                    client_left, client_top, client_right, client_bottom = client_rect
                    client_width = client_right - client_left
                    client_height = client_bottom - client_top

                    # 计算窗口边框和标题栏的偏移
                    border_left = left  # 窗口左边界到屏幕左边界的距离
                    border_top = top    # 窗口上边界到屏幕上边界的距离

                    # 计算客户端区域的屏幕坐标
                    client_screen_left = left + (right - left - client_width) // 2
                    client_screen_top = top + (bottom - top - client_height - (bottom - top - client_width) // 2)

                    # 更精确的方法：使用 ClientToScreen
                    point = win32gui.ClientToScreen(hwnd, (0, 0))
                    client_screen_left, client_screen_top = point

                    self._window_bounds = {
                        'left': client_screen_left,      # 客户端区域左边界
                        'top': client_screen_top,        # 客户端区域上边界
                        'width': client_width,           # 客户端区域宽度
                        'height': client_height,         # 客户端区域高度
                        'window_left': left,             # 整个窗口左边界
                        'window_top': top,               # 整个窗口上边界
                        'window_width': right - left,    # 整个窗口宽度
                        'window_height': bottom - top    # 整个窗口高度
                    }

                    logger.info(f"窗口边界更新 - 客户端区域: {client_width}x{client_height}, "
                               f"整个窗口: {(right-left)}x{(bottom-top)}")
                    logger.debug(f"窗口边界详情: {self._window_bounds}")
                    return

                except Exception as e:
                    logger.warning(f"使用 Windows API 获取客户端区域失败: {e}")

            # 回退到 pygetwindow 方法（包含边框）
            self._window_bounds = {
                'left': self._window.left,
                'top': self._window.top,
                'width': self._window.width,
                'height': self._window.height
            }
            logger.debug(f"窗口边界（pygetwindow）: {self._window_bounds}")

    def _get_window_hwnd(self):
        """获取窗口句柄"""
        try:
            if WINDOWS_API_AVAILABLE and self._window:
                # 通过窗口标题查找窗口句柄
                def enum_windows_callback(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd):
                        window_title = win32gui.GetWindowText(hwnd)
                        if window_title == self._window.title:
                            windows.append(hwnd)
                    return True

                windows = []
                win32gui.EnumWindows(enum_windows_callback, windows)
                return windows[0] if windows else None
            return None
        except Exception as e:
            logger.warning(f"获取窗口句柄失败: {e}")
            return None

    def is_window_found(self) -> bool:
        """检查是否找到游戏窗口"""
        return self._window is not None

    def activate_window(self) -> bool:
        """
        激活游戏窗口

        Returns:
            是否成功激活
        """
        try:
            if not self._window:
                if not self._find_game_window():
                    return False

            # 激活窗口
            self._window.activate()
            time.sleep(0.5)  # 等待窗口激活

            # 验证窗口是否处于前台
            if self._window.isActive:
                logger.info("游戏窗口已激活")
                return True
            else:
                logger.warning("游戏窗口激活失败")
                return False

        except Exception as e:
            logger.error(f"激活游戏窗口失败: {e}")
            return False

    def get_window_bounds(self) -> Optional[Dict[str, int]]:
        """
        获取窗口边界信息

        Returns:
            窗口边界字典 {'left', 'top', 'width', 'height'}
        """
        if self._window:
            self._update_window_bounds()  # 更新最新位置
            return self._window_bounds
        return None

    def window_to_screen_coords(self, window_x: int, window_y: int) -> Tuple[int, int]:
        """
        将窗口相对坐标转换为屏幕绝对坐标

        Args:
            window_x: 窗口内X坐标
            window_y: 窗口内Y坐标

        Returns:
            屏幕绝对坐标 (screen_x, screen_y)
        """
        try:
            if not self._window:
                if not self._find_game_window():
                    raise Exception("游戏窗口未找到")

            bounds = self.get_window_bounds()
            if not bounds:
                raise Exception("无法获取窗口边界")

            screen_x = bounds['left'] + window_x
            screen_y = bounds['top'] + window_y

            logger.debug(f"窗口坐标 ({window_x}, {window_y}) -> 屏幕坐标 ({screen_x}, {screen_y})")
            return screen_x, screen_y

        except Exception as e:
            logger.error(f"坐标转换失败: {e}")
            # 返回原始坐标作为后备
            return window_x, window_y

    def screen_to_window_coords(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """
        将屏幕绝对坐标转换为窗口相对坐标

        Args:
            screen_x: 屏幕X坐标
            screen_y: 屏幕Y坐标

        Returns:
            窗口相对坐标 (window_x, window_y)
        """
        try:
            if not self._window:
                if not self._find_game_window():
                    raise Exception("游戏窗口未找到")

            bounds = self.get_window_bounds()
            if not bounds:
                raise Exception("无法获取窗口边界")

            window_x = screen_x - bounds['left']
            window_y = screen_y - bounds['top']

            logger.debug(f"屏幕坐标 ({screen_x}, {screen_y}) -> 窗口坐标 ({window_x}, {window_y})")
            return window_x, window_y

        except Exception as e:
            logger.error(f"坐标转换失败: {e}")
            return screen_x, screen_y

    def click_at_window_coords(self, window_x: int, window_y: int,
                              button: str = 'left', clicks: int = 1,
                              interval: float = 0.0) -> bool:
        """
        在窗口相对坐标位置点击

        Args:
            window_x: 窗口内X坐标
            window_y: 窗口内Y坐标
            button: 鼠标按钮 ('left', 'right', 'middle')
            clicks: 点击次数
            interval: 点击间隔

        Returns:
            是否成功点击
        """
        try:
            # 转换为屏幕坐标
            screen_x, screen_y = self.window_to_screen_coords(window_x, window_y)

            # 执行点击
            pyautogui.click(screen_x, screen_y, button=button,
                           clicks=clicks, interval=interval)

            logger.debug(f"窗口点击: ({window_x}, {window_y}) -> 屏幕: ({screen_x}, {screen_y})")
            return True

        except Exception as e:
            logger.error(f"窗口点击失败: {e}")
            return False

    def get_window_center(self) -> Optional[Tuple[int, int]]:
        """
        获取窗口中心坐标（窗口相对坐标）

        Returns:
            窗口中心坐标 (center_x, center_y)
        """
        try:
            bounds = self.get_window_bounds()
            if not bounds:
                return None

            center_x = bounds['width'] // 2
            center_y = bounds['height'] // 2

            return center_x, center_y

        except Exception as e:
            logger.error(f"获取窗口中心失败: {e}")
            return None

    def is_point_in_window(self, window_x: int, window_y: int) -> bool:
        """
        检查点是否在窗口内

        Args:
            window_x: 窗口内X坐标
            window_y: 窗口内Y坐标

        Returns:
            是否在窗口内
        """
        try:
            bounds = self.get_window_bounds()
            if not bounds:
                return False

            return (0 <= window_x <= bounds['width'] and
                    0 <= window_y <= bounds['height'])

        except Exception as e:
            logger.error(f"检查窗口内点失败: {e}")
            return False

    def get_mouse_position_window_coords(self) -> Optional[Tuple[int, int]]:
        """
        获取当前鼠标位置（窗口相对坐标）

        Returns:
            鼠标窗口坐标 (window_x, window_y)
        """
        try:
            screen_x, screen_y = pyautogui.position()
            return self.screen_to_window_coords(screen_x, screen_y)

        except Exception as e:
            logger.error(f"获取鼠标位置失败: {e}")
            return None

    def move_mouse_to_window_coords(self, window_x: int, window_y: int,
                                   duration: float = 0.0) -> bool:
        """
        移动鼠标到窗口相对坐标位置

        Args:
            window_x: 窗口内X坐标
            window_y: 窗口内Y坐标
            duration: 移动持续时间

        Returns:
            是否成功移动
        """
        try:
            screen_x, screen_y = self.window_to_screen_coords(window_x, window_y)
            pyautogui.moveTo(screen_x, screen_y, duration=duration)

            logger.debug(f"鼠标移动到窗口坐标: ({window_x}, {window_y})")
            return True

        except Exception as e:
            logger.error(f"移动鼠标失败: {e}")
            return False

    def validate_window_size(self) -> bool:
        """
        验证窗口大小是否符合配置

        Returns:
            窗口大小是否正确
        """
        try:
            bounds = self.get_window_bounds()
            if not bounds:
                return False

            expected_width, expected_height = self.window_resolution

            # 允许一定的误差范围
            tolerance = 10
            width_match = abs(bounds['width'] - expected_width) <= tolerance
            height_match = abs(bounds['height'] - expected_height) <= tolerance

            if width_match and height_match:
                logger.info(f"窗口大小验证通过: {bounds['width']}x{bounds['height']}")
                return True
            else:
                logger.warning(f"窗口大小不匹配: 期望 {expected_width}x{expected_height}, "
                            f"实际 {bounds['width']}x{bounds['height']}")
                return False

        except Exception as e:
            logger.error(f"验证窗口大小失败: {e}")
            return False

    def refresh_window(self) -> bool:
        """
        刷新窗口信息

        Returns:
            是否成功刷新
        """
        try:
            return self._find_game_window()
        except Exception as e:
            logger.error(f"刷新窗口信息失败: {e}")
            return False

    def get_client_area_info(self) -> Optional[Dict[str, Any]]:
        """
        获取客户端区域详细信息

        Returns:
            客户端区域信息字典，包含客户端区域和整个窗口的尺寸信息
        """
        if not self._window:
            return None

        bounds = self.get_window_bounds()
        if not bounds:
            return None

        return {
            'client_area': {
                'left': bounds['left'],
                'top': bounds['top'],
                'width': bounds['width'],
                'height': bounds['height']
            },
            'whole_window': {
                'left': bounds.get('window_left', bounds['left']),
                'top': bounds.get('window_top', bounds['top']),
                'width': bounds.get('window_width', bounds['width']),
                'height': bounds.get('window_height', bounds['height'])
            },
            'border_offsets': {
                'left_offset': bounds.get('window_left', bounds['left']) - bounds['left'],
                'top_offset': bounds.get('window_top', bounds['top']) - bounds['top'],
                'width_diff': bounds.get('window_width', bounds['width']) - bounds['width'],
                'height_diff': bounds.get('window_height', bounds['height']) - bounds['height']
            },
            'has_windows_api': WINDOWS_API_AVAILABLE
        }

    def get_window_info(self) -> Dict[str, Any]:
        """
        获取窗口详细信息

        Returns:
            窗口信息字典
        """
        try:
            info = {
                'title': self.window_title,
                'process_name': self.process_name,
                'found': self.is_window_found(),
                'bounds': self.get_window_bounds(),
                'expected_resolution': self.window_resolution,
                'is_valid_size': False,
                'client_area_info': self.get_client_area_info()
            }

            if self._window:
                info.update({
                    'actual_title': self._window.title,
                    'is_active': self._window.isActive,
                    'is_minimized': self._window.isMinimized,
                    'is_maximized': self._window.isMaximized
                })

                # 验证窗口大小
                info['is_valid_size'] = self.validate_window_size()

            return info

        except Exception as e:
            logger.error(f"获取窗口信息失败: {e}")
            return {'error': str(e)}