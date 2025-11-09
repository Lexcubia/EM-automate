"""
自动化示例：展示如何在游戏自动化中使用键位配置
"""
import time
from .keybindings import keybindings_manager
import logging

logger = logging.getLogger(__name__)

class GameAutomationExample:
    """游戏自动化示例类"""

    def __init__(self):
        self.keybindings = keybindings_manager

    def basic_combat_sequence(self):
        """基础战斗序列示例"""
        logger.info("开始执行基础战斗序列")

        try:
            # 1. 跳跃
            self.keybindings.execute_action("jump", "press", 0.1)
            time.sleep(0.5)

            # 2. 闪避
            self.keybindings.execute_action("dodge", "press", 0.1)
            time.sleep(0.3)

            # 3. 近战攻击
            self.keybindings.execute_action("melee_attack", "press", 0.1)
            time.sleep(0.5)

            # 4. 战技
            self.keybindings.execute_action("skill", "press", 0.1)
            time.sleep(1.0)

            # 5. 远程攻击
            self.keybindings.execute_action("ranged_attack", "press", 0.1)
            time.sleep(0.5)

            # 6. 终结技
            self.keybindings.execute_action("ultimate", "press", 0.1)
            time.sleep(2.0)

            # 7. 魔灵支援
            self.keybindings.execute_action("spirit_support", "press", 0.1)

            logger.info("基础战斗序列执行完成")
            return True

        except Exception as e:
            logger.error(f"战斗序列执行失败: {e}")
            return False

    def movement_pattern(self, duration: float = 5.0):
        """移动模式示例"""
        logger.info(f"开始执行移动模式，持续时间: {duration}秒")

        start_time = time.time()

        try:
            while time.time() - start_time < duration:
                # 前进
                self.keybindings.execute_action("move_forward", "down")
                time.sleep(0.1)

                # 随机左右移动
                if int(time.time()) % 2 == 0:
                    self.keybindings.execute_action("move_left", "down")
                else:
                    self.keybindings.execute_action("move_right", "down")

                time.sleep(0.5)

                # 停止移动
                self.keybindings.execute_action("move_forward", "up")
                self.keybindings.execute_action("move_left", "up")
                self.keybindings.execute_action("move_right", "up")

                time.sleep(0.2)

            logger.info("移动模式执行完成")
            return True

        except Exception as e:
            logger.error(f"移动模式执行失败: {e}")
            return False

    def inventory_management(self):
        """背包管理示例"""
        logger.info("开始执行背包管理")

        try:
            # 打开背包
            self.keybindings.execute_action("backpack", "press", 0.1)
            time.sleep(1.0)

            # 装填子弹
            self.keybindings.execute_action("reload", "press", 0.1)
            time.sleep(0.5)

            # 关闭背包
            self.keybindings.execute_action("backpack", "press", 0.1)

            logger.info("背包管理执行完成")
            return True

        except Exception as e:
            logger.error(f"背包管理执行失败: {e}")
            return False

    def open_map_and_teleport(self):
        """地图传送示例"""
        logger.info("开始执行地图传送")

        try:
            # 打开地图
            self.keybindings.execute_action("map", "press", 0.1)
            time.sleep(1.0)

            # 这里应该有图像识别来选择传送点
            # 暂时用交互键代替
            self.keybindings.execute_action("interact", "press", 0.1)
            time.sleep(2.0)

            # 关闭地图
            self.keybindings.execute_action("map", "press", 0.1)

            logger.info("地图传送执行完成")
            return True

        except Exception as e:
            logger.error(f"地图传送执行失败: {e}")
            return False

    def custom_action_sequence(self, actions: list):
        """自定义动作序列"""
        logger.info(f"开始执行自定义动作序列，共{len(actions)}个动作")

        try:
            for i, action_config in enumerate(actions):
                action = action_config.get("action")
                press_type = action_config.get("press_type", "press")
                duration = action_config.get("duration", 0.1)
                delay = action_config.get("delay", 0.0)

                if not action:
                    logger.warning(f"第{i+1}个动作配置无效，跳过")
                    continue

                success = self.keybindings.execute_action(action, press_type, duration)
                if not success:
                    logger.warning(f"第{i+1}个动作{action}执行失败")

                # 延迟
                if delay > 0:
                    time.sleep(delay)

            logger.info("自定义动作序列执行完成")
            return True

        except Exception as e:
            logger.error(f"自定义动作序列执行失败: {e}")
            return False

    def emergency_recovery(self):
        """紧急恢复序列"""
        logger.info("开始执行紧急恢复序列")

        try:
            # 跳跃取消当前动作
            self.keybindings.execute_action("jump", "press", 0.1)
            time.sleep(0.2)

            # 闪避险境
            self.keybindings.execute_action("dodge", "press", 0.1)
            time.sleep(0.5)

            # 使用复苏技能
            self.keybindings.execute_action("revive", "press", 0.1)
            time.sleep(1.0)

            logger.info("紧急恢复序列执行完成")
            return True

        except Exception as e:
            logger.error(f"紧急恢复序列执行失败: {e}")
            return False

# 使用示例
if __name__ == "__main__":
    # 创建自动化实例
    automation = GameAutomationExample()

    # 执行基础战斗序列
    automation.basic_combat_sequence()

    # 执行移动模式
    automation.movement_pattern(3.0)

    # 执行自定义动作序列
    custom_actions = [
        {"action": "jump", "press_type": "press", "duration": 0.1, "delay": 0.5},
        {"action": "skill", "press_type": "press", "duration": 0.1, "delay": 1.0},
        {"action": "ultimate", "press_type": "press", "duration": 0.1, "delay": 0.0}
    ]
    automation.custom_action_sequence(custom_actions)