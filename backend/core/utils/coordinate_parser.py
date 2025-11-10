"""
坐标解析工具模块
处理各种坐标格式的解析和转换
"""
from typing import Tuple, List, Union
import logging

logger = logging.getLogger(__name__)

class CoordinateParser:
    """坐标解析器 - 处理字符串坐标到数值的转换"""

    @staticmethod
    def parse_coord(coord_str: str) -> Tuple[int, int]:
        """
        解析 'x,y' 格式的坐标字符串

        Args:
            coord_str: 坐标字符串，如 "100,200"

        Returns:
            坐标元组 (x, y)
        """
        try:
            x, y = coord_str.split(',')
            return int(x), int(y)
        except (ValueError, AttributeError) as e:
            raise ValueError(f"无效的坐标格式: {coord_str}") from e

    @staticmethod
    def get_center(position: Union[List[str], Tuple[str, str]]) -> Tuple[int, int]:
        """
        获取坐标区域的中心点

        Args:
            position: 坐标位置，可以是:
                     - ["x,y"] 单点坐标
                     - ["x1,y1", "x2,y2"] 区域坐标

        Returns:
            中心点坐标 (center_x, center_y)
        """
        if not position:
            raise ValueError("坐标位置不能为空")

        if len(position) == 1:
            # 单点坐标
            return CoordinateParser.parse_coord(position[0])
        elif len(position) == 2:
            # 区域坐标 ["x1,y1", "x2,y2"]
            x1, y1 = CoordinateParser.parse_coord(position[0])
            x2, y2 = CoordinateParser.parse_coord(position[1])
            return ((x1 + x2) // 2, (y1 + y2) // 2)
        else:
            raise ValueError(f"无效的坐标格式: {position}")

    @staticmethod
    def validate_coords(position: Union[List[str], Tuple[str, str]]) -> bool:
        """
        验证坐标格式是否有效

        Args:
            position: 坐标位置

        Returns:
            是否有效
        """
        try:
            CoordinateParser.get_center(position)
            return True
        except ValueError:
            return False

    @staticmethod
    def parse_rect_coords(position: List[str]) -> Tuple[int, int, int, int]:
        """
        解析矩形坐标区域

        Args:
            position: 区域坐标 ["x1,y1", "x2,y2"]

        Returns:
            矩形坐标 (left, top, right, bottom)
        """
        if len(position) != 2:
            raise ValueError("矩形坐标需要两个点")

        x1, y1 = CoordinateParser.parse_coord(position[0])
        x2, y2 = CoordinateParser.parse_coord(position[1])

        # 确保坐标顺序正确
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)

        return left, top, right, bottom

    @staticmethod
    def get_area_size(position: List[str]) -> Tuple[int, int]:
        """
        获取坐标区域的尺寸

        Args:
            position: 区域坐标 ["x1,y1", "x2,y2"]

        Returns:
            区域尺寸 (width, height)
        """
        left, top, right, bottom = CoordinateParser.parse_rect_coords(position)
        return right - left, bottom - top