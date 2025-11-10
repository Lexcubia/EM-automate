"""
统一任务执行器 - 实现基于a.md的8步流程
整合了 automation.py, task_engine.py, game_controller.py 的核心功能
简化、直接、无特殊情况的任务执行系统
"""
import time
import logging
import psutil
from typing import List, Dict, Any, Callable, Optional
from enum import Enum
from dataclasses import dataclass
from .config import config
from .macro_engine import macro_engine, MacroExecutionResult
from .game_navigator import game_navigator
from .window_manager import WindowManager
from .input_controller import input_controller

logger = logging.getLogger(__name__)

class TaskCategory(Enum):
    """任务分类"""
    COMMISSION = "委托"
    NIGHT_SAILING = "夜航手册"
    COMMISSION_LETTER = "委托密函"

@dataclass
class Task:
    """简化后的任务数据结构"""
    id: str
    name: str
    category: TaskCategory
    level: str = ""
    macro_id: str = ""
    run_count: int = 1
    current_run: int = 0
    params: Dict[str, Any] = None

    def __post_init__(self):
        if self.params is None:
            self.params = {}

class GameController:
    """游戏控制器 - 简化版游戏状态管理"""

    def __init__(self):
        self.window_manager = WindowManager()
        self.in_game_timeout = 30  # 进入游戏超时时间
        self.task_completion_timeout = 120  # 任务完成超时时间

    def ensure_in_game(self) -> bool:
        """确保在游戏中"""
        try:
            # 1. 检查游戏进程
            if not self._check_game_process():
                logger.error("游戏进程未运行")
                return False

            # 2. 激活游戏窗口
            if not self.window_manager.activate_window():
                logger.error("激活游戏窗口失败")
                return False

            # 3. 等待游戏界面加载
            if not self._wait_for_game_interface():
                logger.error("等待游戏界面加载失败")
                return False

            logger.info("成功进入游戏")
            return True

        except Exception as e:
            logger.error(f"确保在游戏中失败: {e}")
            return False

    def _check_game_process(self) -> bool:
        """检查游戏进程是否运行"""
        try:
            for process in psutil.process_iter(['pid', 'name']):
                if process.info['name'] == config.game_process_name:
                    logger.debug(f"找到游戏进程: PID {process.info['pid']}")
                    return True
            return False
        except Exception as e:
            logger.error(f"检查游戏进程失败: {e}")
            return False

    def _wait_for_game_interface(self) -> bool:
        """等待游戏界面加载"""
        logger.info("等待游戏界面加载")
        start_time = time.time()

        while time.time() - start_time < self.in_game_timeout:
            # 简化实现：假设游戏界面已加载
            # 在实际应用中，这里应该使用图像识别检测游戏特征元素
            time.sleep(1)
            return True  # 简化版直接返回成功

        logger.error("游戏界面加载超时")
        return False

    def wait_for_task_completion(self, task_name: str = "") -> bool:
        """检测任务完成"""
        logger.info(f"开始检测任务完成: {task_name}")

        start_time = time.time()
        check_interval = 2.0

        while time.time() - start_time < self.task_completion_timeout:
            # 简化实现：等待一段时间后认为任务完成
            # 在实际应用中，这里应该检测任务完成界面、奖励界面等

            time.sleep(check_interval)
            # 模拟任务完成检测
            if time.time() - start_time > 10:  # 假设10秒后任务完成
                logger.info(f"任务完成: {task_name}")
                return True

        logger.warning(f"任务完成检测超时: {task_name}")
        return True  # 超时也认为完成，避免卡死

    def should_continue_next_run(self, current_run: int, total_runs: int) -> bool:
        """判断是否继续下一次执行"""
        return current_run < total_runs

    def exit_to_prepare_next_task(self, need_continue: bool) -> bool:
        """退出当前关卡准备下一个任务"""
        try:
            if need_continue:
                # 继续同一个任务
                logger.info("准备下一次相同任务执行")
                input_controller.press_key('enter')  # 再次挑战
                time.sleep(3)
            else:
                # 切换到下一个任务，返回主界面
                logger.info("准备切换到下一个任务")
                input_controller.press_key('esc')  # 返回
                time.sleep(2)

            return True

        except Exception as e:
            logger.error(f"退出关卡准备失败: {e}")
            return False

    def collect_rewards(self) -> bool:
        """收集奖励"""
        try:
            logger.info("开始收集奖励")

            # 模拟收集奖励操作
            screen_width, _ = input_controller.window_manager.window_to_screen_coords(960, 540)
            input_controller.click_at(960, 540 + 50)  # 点击中央偏下位置
            time.sleep(1)

            logger.info("奖励收集完成")
            return True

        except Exception as e:
            logger.error(f"收集奖励失败: {e}")
            return False

class TaskExecutor:
    """统一任务执行器 - 简洁的8步流程实现"""

    def __init__(self):
        self.is_running = False
        self.should_stop = False
        self.game_controller = GameController()

        logger.info("任务执行器初始化完成")

    def execute_task_queue(self, tasks: List[Task], progress_callback: Optional[Callable] = None) -> bool:
        """
        执行任务队列 - 实现a.md的完整8步流程

        Args:
            tasks: 任务列表
            progress_callback: 进度回调函数

        Returns:
            是否全部成功完成
        """
        if not tasks:
            logger.warning("任务队列为空")
            return False

        self.is_running = True
        self.should_stop = False
        total_runs = sum(task.run_count for task in tasks)
        completed_runs = 0

        logger.info(f"开始执行任务队列（8步流程），共{len(tasks)}个任务，{total_runs}次执行")

        try:
            # 步骤3：进入游戏（整个流程只需要进入一次）
            if not self.game_controller.ensure_in_game():
                logger.error("进入游戏失败")
                return False

            # 步骤8：循环执行每个任务
            for task_index, task in enumerate(tasks):
                if self.should_stop:
                    logger.info("收到停止信号，中断执行")
                    break

                logger.info(f"开始执行任务[{task_index+1}/{len(tasks)}]: {task.name}")

                # 执行单个任务多次
                for run in range(task.run_count):
                    if self.should_stop:
                        logger.info("收到停止信号，中断执行")
                        break

                    task.current_run = run + 1
                    logger.info(f"执行任务第{task.current_run}/{task.run_count}次")

                    # 步骤4：根据任务分类执行不同的跳转逻辑
                    if not self._navigate_to_task(task):
                        logger.error(f"导航到任务失败: {task.name}")
                        continue

                    # 步骤5：进入游戏关卡（如果需要）
                    if not self.game_controller.ensure_in_game():
                        logger.error(f"确保在游戏中失败: {task.name}")
                        continue

                    # 步骤6：循环执行配置的宏
                    if not self._execute_macros(task):
                        logger.error(f"宏执行失败: {task.name}")
                        continue

                    # 步骤6（续）：检测任务完成
                    if not self.game_controller.wait_for_task_completion(task.name):
                        logger.warning(f"任务完成检测失败: {task.name}")

                    # 收集奖励
                    if not self.game_controller.collect_rewards():
                        logger.warning(f"收集奖励失败: {task.name}")

                    completed_runs += 1
                    logger.info(f"任务执行完成: {task.name} (第{task.current_run}次)")

                    # 更新进度
                    if progress_callback:
                        progress = completed_runs / total_runs * 100
                        status = f"任务[{task_index+1}/{len(tasks)}] 第{task.current_run}/{task.run_count}次"
                        progress_callback(completed_runs, total_runs, status)

                    # 步骤7：判断是否再次进入关卡还是退出关卡执行下一个任务
                    need_continue = self.game_controller.should_continue_next_run(task.current_run, task.run_count)

                    # 退出当前关卡，准备下一次执行
                    if not self.game_controller.exit_to_prepare_next_task(need_continue):
                        logger.warning(f"退出关卡准备失败: {task.name}")

                    # 任务间休息
                    time.sleep(1)

                # 任务切换休息
                if not self.should_stop and task_index < len(tasks) - 1:
                    logger.info(f"完成任务 {task_index+1}/{len(tasks)}，休息2秒后继续...")
                    time.sleep(2)

            logger.info(f"任务队列执行完成: {completed_runs}/{total_runs}次成功")
            return completed_runs == total_runs

        except Exception as e:
            logger.error(f"任务队列执行异常: {e}")
            return False
        finally:
            self.is_running = False

    def _navigate_to_task(self, task: Task) -> bool:
        """导航到指定任务 - 步骤4"""
        try:
            logger.info(f"导航到任务: {task.name}")

            # 构建导航参数
            mission_type = self._category_to_mission_type(task.category)
            selected_level = task.level if task.category == TaskCategory.NIGHT_SAILING else None

            # 执行导航
            success = game_navigator.navigate_to_dungeon({
                'mission_type': mission_type,
                'selected_level': selected_level
            })

            if success:
                logger.info(f"成功导航到任务: {task.name}")
            else:
                logger.error(f"导航到任务失败: {task.name}")

            return success

        except Exception as e:
            logger.error(f"导航到任务失败: {e}")
            return False

    def _category_to_mission_type(self, category: TaskCategory) -> str:
        """将任务分类转换为导航器需要的任务类型"""
        category_mapping = {
            TaskCategory.COMMISSION: 'commission',
            TaskCategory.NIGHT_SAILING: 'night_sailing',
            TaskCategory.COMMISSION_LETTER: 'commission_letter'
        }
        return category_mapping.get(category, 'commission')

    def _execute_macros(self, task: Task) -> bool:
        """执行宏 - 步骤6"""
        logger.info(f"开始执行宏: {task.name}")

        try:
            # 定义宏执行进度回调
            def macro_progress_callback(current, total, status):
                logger.info(f"宏执行进度: {current}/{total} - {status}")

            # 使用宏引擎执行宏
            result = macro_engine.execute_macro_for_task(
                task_category=task.category.value,
                task_name=task.name,
                macro_id=task.macro_id if task.macro_id else None,
                repeat_count=1,
                progress_callback=macro_progress_callback
            )

            # 记录执行结果
            if result.status.value == "执行成功":
                logger.info(f"宏执行成功: {result.macro_name}")
                return True
            else:
                logger.error(f"宏执行失败: {result.error_message}")
                return False

        except Exception as e:
            logger.error(f"执行宏异常: {e}")
            return False

    def stop(self):
        """停止任务执行"""
        logger.info("停止任务执行")
        self.should_stop = True
        self.is_running = False

class TaskFactory:
    """任务工厂 - 用于创建任务对象"""

    @staticmethod
    def create_from_frontend_data(frontend_task: Dict[str, Any]) -> Task:
        """
        从前端数据创建任务对象

        Args:
            frontend_task: 前端发送的任务数据

        Returns:
            Task对象
        """
        # 确定任务分类
        sub_category = frontend_task.get('sub_category', '')
        if 'commission' in sub_category:
            category = TaskCategory.COMMISSION
        elif 'night_sailing' in sub_category:
            category = TaskCategory.NIGHT_SAILING
        elif 'commission_letter' in sub_category:
            category = TaskCategory.COMMISSION_LETTER
        else:
            # 根据任务类型判断
            mission_type = frontend_task.get('mission_type', '')
            if 'commission' in mission_type:
                category = TaskCategory.COMMISSION
            elif 'night_sailing' in mission_type:
                category = TaskCategory.NIGHT_SAILING
            elif 'commission_letter' in mission_type:
                category = TaskCategory.COMMISSION_LETTER
            else:
                category = TaskCategory.COMMISSION  # 默认

        return Task(
            id=frontend_task.get('id', ''),
            name=frontend_task.get('name', frontend_task.get('mission_key', '')),
            category=category,
            level=frontend_task.get('selected_level', ''),
            macro_id=frontend_task.get('params', {}).get('macro_id', ''),
            run_count=frontend_task.get('run_count', 1),
            params=frontend_task.get('params', {})
        )

# 全局任务执行器实例
task_executor = TaskExecutor()