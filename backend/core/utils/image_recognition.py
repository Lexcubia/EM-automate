"""
图像识别工具模块
统一处理所有图像识别相关功能
"""
import cv2
import numpy as np
import pyautogui
import logging
from typing import Optional, Tuple, List
from pathlib import Path

logger = logging.getLogger(__name__)

class ImageRecognition:
    """图像识别器 - 简单直接的图像匹配"""

    def __init__(self, confidence_threshold: float = 0.8):
        """
        初始化图像识别器

        Args:
            confidence_threshold: 匹配置信度阈值
        """
        self.confidence_threshold = confidence_threshold
        self.assets_path = Path(__file__).parent.parent.parent / "assets" / "images"

    def find_image(self, image_name: str, confidence: Optional[float] = None) -> Optional[Tuple[int, int]]:
        """
        在屏幕上查找指定图像

        Args:
            image_name: 图像文件名
            confidence: 匹配置信度（可选，使用默认阈值）

        Returns:
            找到的图像中心坐标，未找到返回None
        """
        try:
            confidence = confidence or self.confidence_threshold
            image_path = self.assets_path / image_name

            if not image_path.exists():
                logger.warning(f"图像文件不存在: {image_path}")
                return None

            location = pyautogui.locateOnScreen(str(image_path), confidence=confidence)
            if location:
                center = pyautogui.center(location)
                logger.debug(f"找到图像 {image_name} 在位置 {center}")
                return (center.x, center.y)
            else:
                logger.debug(f"未找到图像: {image_name}")
                return None

        except Exception as e:
            logger.error(f"图像识别失败 {image_name}: {e}")
            return None

    def wait_for_image(self, image_name: str, timeout: float = 10.0,
                      confidence: Optional[float] = None) -> bool:
        """
        等待图像出现在屏幕上

        Args:
            image_name: 图像文件名
            timeout: 超时时间（秒）
            confidence: 匹配置信度

        Returns:
            是否找到图像
        """
        import time
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self.find_image(image_name, confidence):
                return True
            time.sleep(0.5)

        logger.warning(f"等待图像超时: {image_name}")
        return False

    def click_image(self, image_name: str, confidence: Optional[float] = None,
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
        position = self.find_image(image_name, confidence)
        if position:
            pyautogui.click(position[0], position[1], button=button)
            logger.debug(f"点击图像: {image_name} 在位置 {position}")
            return True
        return False

    def validate_images(self, image_names: List[str]) -> dict:
        """
        验证图像文件是否存在

        Args:
            image_names: 图像文件名列表

        Returns:
            验证结果字典
        """
        results = {}
        for image_name in image_names:
            image_path = self.assets_path / image_name
            results[image_name] = {
                "exists": image_path.exists(),
                "path": str(image_path)
            }

        return results