"""
Core utilities package
提供图像识别、坐标解析等通用工具
"""

from .image_recognition import ImageRecognition
from .coordinate_parser import CoordinateParser

__all__ = ['ImageRecognition', 'CoordinateParser']