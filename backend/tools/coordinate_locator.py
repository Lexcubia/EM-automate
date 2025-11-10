#!/usr/bin/env python3
"""
游戏窗口坐标定位工具
用于实时显示和捕获游戏窗口内的鼠标坐标位置
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.core.window_manager import WindowManager
from backend.core.config import config

# 设置日志
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CoordinateLocator:
    """坐标定位器主类"""

    def __init__(self):
        """初始化坐标定位器"""
        self.window_manager = WindowManager()
        self.running = False
        self.update_thread = None
        self.captured_coords = []

        # 创建主界面
        self.setup_ui()

        # 启动坐标更新
        self.start_coordinate_update()

    def setup_ui(self):
        """设置用户界面"""
        self.root = tk.Tk()
        self.root.title("游戏窗口坐标定位器")
        self.root.geometry("600x500")
        self.root.resizable(True, True)

        # 设置窗口总是在最前面
        self.root.attributes('-topmost', True)

        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)

        # 窗口状态显示
        self.setup_window_status(main_frame)

        # 坐标显示区域
        self.setup_coordinate_display(main_frame)

        # 控制按钮
        self.setup_control_buttons(main_frame)

        # 坐标历史记录
        self.setup_coordinate_history(main_frame)

    def setup_window_status(self, parent):
        """设置窗口状态显示区域"""
        status_frame = ttk.LabelFrame(parent, text="窗口状态", padding="5")
        status_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # 窗口标题显示
        ttk.Label(status_frame, text="游戏窗口:").grid(row=0, column=0, sticky=tk.W)
        self.window_title_label = ttk.Label(status_frame, text="未找到", foreground="red")
        self.window_title_label.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))

        # 窗口大小显示
        ttk.Label(status_frame, text="窗口大小:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        self.window_size_label = ttk.Label(status_frame, text="0x0")
        self.window_size_label.grid(row=0, column=3, sticky=tk.W, padx=(5, 0))

        # 窗口位置显示
        ttk.Label(status_frame, text="窗口位置:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.window_position_label = ttk.Label(status_frame, text="(0, 0)")
        self.window_position_label.grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=(5, 0))

        # 状态指示器
        self.status_indicator = ttk.Label(status_frame, text="●", foreground="red")
        self.status_indicator.grid(row=1, column=2, sticky=tk.W, padx=(20, 0), pady=(5, 0))
        self.status_text = ttk.Label(status_frame, text="未连接")
        self.status_text.grid(row=1, column=3, sticky=tk.W, padx=(5, 0), pady=(5, 0))

        # 刷新按钮
        ttk.Button(status_frame, text="刷新窗口", command=self.refresh_window).grid(row=0, column=4, padx=(5, 0))

        # 选择窗口按钮
        ttk.Button(status_frame, text="选择窗口", command=self.select_window).grid(row=0, column=5, padx=(5, 0))

    def setup_coordinate_display(self, parent):
        """设置坐标显示区域"""
        coord_frame = ttk.LabelFrame(parent, text="实时坐标", padding="10")
        coord_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # 屏幕绝对坐标
        screen_frame = ttk.Frame(coord_frame)
        screen_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(screen_frame, text="屏幕坐标:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W)
        self.screen_coord_label = ttk.Label(screen_frame, text="(0, 0)", font=("Courier", 12))
        self.screen_coord_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        # 窗口相对坐标
        window_frame = ttk.Frame(coord_frame)
        window_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(window_frame, text="窗口坐标:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W)
        self.window_coord_label = ttk.Label(window_frame, text="(0, 0)", font=("Courier", 12), foreground="blue")
        self.window_coord_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        # 坐标状态指示
        self.coord_status_label = ttk.Label(coord_frame, text="鼠标不在窗口内", foreground="gray")
        self.coord_status_label.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))

    def setup_control_buttons(self, parent):
        """设置控制按钮区域"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10))

        # 捕获坐标按钮
        self.capture_button = ttk.Button(
            button_frame,
            text="捕获当前坐标 (Space)",
            command=self.capture_coordinate
        )
        self.capture_button.grid(row=0, column=0, padx=(0, 10))

        # 清空历史按钮
        ttk.Button(button_frame, text="清空历史", command=self.clear_history).grid(row=0, column=1, padx=(0, 10))

        # 保存按钮
        ttk.Button(button_frame, text="保存坐标", command=self.save_coordinates).grid(row=0, column=2, padx=(0, 10))

        # 加载按钮
        ttk.Button(button_frame, text="加载坐标", command=self.load_coordinates).grid(row=0, column=3, padx=(0, 10))

        # 快捷键绑定
        self.root.bind('<space>', lambda e: self.capture_coordinate())
        self.root.bind('<Escape>', lambda e: self.quit())

    def setup_coordinate_history(self, parent):
        """设置坐标历史记录区域"""
        history_frame = ttk.LabelFrame(parent, text="坐标历史记录", padding="5")
        history_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)

        # 创建滚动文本框
        self.history_text = scrolledtext.ScrolledText(
            history_frame,
            height=10,
            width=70,
            font=("Courier", 9)
        )
        self.history_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 添加初始说明
        self.add_history_entry("=== 坐标定位器启动 ===")
        self.add_history_entry("按空格键捕获当前坐标")
        self.add_history_entry("按ESC键退出程序")
        self.add_history_entry("")

    def add_history_entry(self, text: str):
        """添加历史记录条目"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {text}\n"
        self.history_text.insert(tk.END, entry)
        self.history_text.see(tk.END)

    def update_window_status(self):
        """更新窗口状态显示"""
        if self.window_manager.is_window_found():
            bounds = self.window_manager.get_window_bounds()
            if bounds:
                self.window_title_label.config(
                    text=self.window_manager._window.title,
                    foreground="green"
                )
                self.window_size_label.config(text=f"{bounds['width']}x{bounds['height']}")
                self.window_position_label.config(text=f"({bounds['left']}, {bounds['top']})")
                self.status_indicator.config(foreground="green")
                self.status_text.config(text="已连接")
            else:
                self.window_title_label.config(text="窗口信息获取失败", foreground="orange")
                self.status_indicator.config(foreground="orange")
                self.status_text.config(text="错误")
        else:
            # 尝试列出所有可见窗口进行调试
            try:
                import pygetwindow as gw
                all_windows = gw.getAllWindows()
                matching_windows = [w for w in all_windows if self.window_manager.window_title.lower() in w.title.lower()]

                if matching_windows:
                    # 找到相似的窗口，使用第一个
                    self.window_manager._window = matching_windows[0]
                    self.window_manager._update_window_bounds()
                    self.add_history_entry(f"找到相似窗口: {matching_windows[0].title}")
                    return self.update_window_status()  # 递归调用更新状态
                else:
                    # 显示所有窗口标题供调试
                    window_titles = [w.title for w in all_windows[:10] if w.title.strip()]
                    self.window_title_label.config(text=f"未找到匹配窗口 (可见: {len(window_titles)}个)", foreground="red")
                    if window_titles:
                        self.add_history_entry(f"可见窗口: {', '.join(window_titles[:3])}...")
                self.window_size_label.config(text="0x0")
                self.window_position_label.config(text="(0, 0)")
                self.status_indicator.config(foreground="red")
                self.status_text.config(text="未连接")
            except Exception as e:
                self.window_title_label.config(text=f"窗口检测错误: {str(e)}", foreground="red")
                self.window_size_label.config(text="0x0")
                self.window_position_label.config(text="(0, 0)")
                self.status_indicator.config(foreground="red")
                self.status_text.config(text="检测错误")

    def update_coordinate_display(self):
        """更新坐标显示"""
        try:
            import pyautogui

            # 获取屏幕坐标
            screen_x, screen_y = pyautogui.position()
            self.screen_coord_label.config(text=f"({screen_x}, {screen_y})")

            # 检查鼠标是否在游戏窗口内
            if self.window_manager.is_window_found():
                window_x, window_y = self.window_manager.screen_to_window_coords(screen_x, screen_y)

                if self.window_manager.is_point_in_window(window_x, window_y):
                    # 鼠标在窗口内
                    self.window_coord_label.config(
                        text=f"({window_x}, {window_y})",
                        foreground="blue"
                    )
                    self.coord_status_label.config(
                        text="鼠标在窗口内",
                        foreground="green"
                    )
                    self.current_valid_coords = (window_x, window_y)
                else:
                    # 鼠标不在窗口内
                    self.window_coord_label.config(
                        text=f"({window_x}, {window_y})",
                        foreground="gray"
                    )
                    self.coord_status_label.config(
                        text="鼠标不在窗口内",
                        foreground="gray"
                    )
                    self.current_valid_coords = None
            else:
                self.window_coord_label.config(text="(--, --)", foreground="red")
                self.coord_status_label.config(text="游戏窗口未找到", foreground="red")
                self.current_valid_coords = None

        except Exception as e:
            logger.error(f"更新坐标显示失败: {e}")
            self.screen_coord_label.config(text="错误", foreground="red")
            self.window_coord_label.config(text="错误", foreground="red")

    def capture_coordinate(self):
        """捕获当前坐标"""
        if hasattr(self, 'current_valid_coords') and self.current_valid_coords:
            window_x, window_y = self.current_valid_coords

            # 添加到历史记录
            coord_info = {
                'window_x': window_x,
                'window_y': window_y,
                'timestamp': datetime.now().isoformat(),
                'window_bounds': self.window_manager.get_window_bounds()
            }
            self.captured_coords.append(coord_info)

            # 显示捕获信息
            self.add_history_entry(f"捕获坐标: 窗口({window_x}, {window_y})")

            # 视觉反馈
            original_color = self.capture_button.cget("background")
            self.capture_button.config(background="lightgreen")
            self.root.after(100, lambda: self.capture_button.config(background=original_color))
        else:
            self.add_history_entry("捕获失败: 鼠标不在游戏窗口内")
            messagebox.showwarning("捕获失败", "请将鼠标移动到游戏窗口内再捕获坐标")

    def clear_history(self):
        """清空历史记录"""
        self.captured_coords.clear()
        self.history_text.delete(1.0, tk.END)
        self.add_history_entry("=== 历史记录已清空 ===")
        self.add_history_entry("")

    def save_coordinates(self):
        """保存捕获的坐标到文件"""
        if not self.captured_coords:
            messagebox.showwarning("无数据", "没有捕获的坐标可保存")
            return

        try:
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"coordinates_{timestamp}.json"
            filepath = Path(__file__).parent.parent.parent / "config" / filename

            # 确保目录存在
            filepath.parent.mkdir(exist_ok=True)

            # 保存数据
            save_data = {
                'created_time': datetime.now().isoformat(),
                'game_window': self.window_manager.window_title,
                'window_bounds': self.window_manager.get_window_bounds(),
                'coordinates': self.captured_coords
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)

            self.add_history_entry(f"坐标已保存到: {filename}")
            messagebox.showinfo("保存成功", f"坐标已保存到:\n{filepath}")

        except Exception as e:
            logger.error(f"保存坐标失败: {e}")
            messagebox.showerror("保存失败", f"保存坐标时出错:\n{str(e)}")

    def load_coordinates(self):
        """从文件加载坐标"""
        try:
            from tkinter import filedialog

            # 选择文件
            filepath = filedialog.askopenfilename(
                title="选择坐标文件",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
                initialdir=Path(__file__).parent.parent.parent / "config"
            )

            if not filepath:
                return

            # 加载数据
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 验证数据格式
            if 'coordinates' in data:
                self.captured_coords = data['coordinates']

                # 清空并显示加载的坐标
                self.clear_history()
                self.add_history_entry(f"=== 从文件加载坐标: {Path(filepath).name} ===")

                for coord in self.captured_coords:
                    window_x = coord['window_x']
                    window_y = coord['window_y']
                    timestamp = coord.get('timestamp', '')
                    self.add_history_entry(f"坐标: 窗口({window_x}, {window_y})")

                messagebox.showinfo("加载成功", f"已加载 {len(self.captured_coords)} 个坐标")
            else:
                messagebox.showerror("文件格式错误", "选择的文件不是有效的坐标文件")

        except Exception as e:
            logger.error(f"加载坐标失败: {e}")
            messagebox.showerror("加载失败", f"加载坐标时出错:\n{str(e)}")

    def select_window(self):
        """手动选择游戏窗口"""
        try:
            import pygetwindow as gw

            # 获取所有可见窗口
            all_windows = gw.getAllWindows()
            visible_windows = [w for w in all_windows if w.title.strip() and w.visible]

            if not visible_windows:
                messagebox.showwarning("无窗口", "没有找到可见窗口")
                return

            # 创建窗口选择对话框
            dialog = tk.Toplevel(self.root)
            dialog.title("选择游戏窗口")
            dialog.geometry("500x400")
            dialog.transient(self.root)
            dialog.grab_set()

            # 窗口列表
            list_frame = ttk.Frame(dialog, padding="10")
            list_frame.pack(fill=tk.BOTH, expand=True)

            ttk.Label(list_frame, text="请选择游戏窗口:").pack(anchor=tk.W, pady=(0, 5))

            # 创建列表框和滚动条
            list_container = ttk.Frame(list_frame)
            list_container.pack(fill=tk.BOTH, expand=True)

            scrollbar = ttk.Scrollbar(list_container)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            listbox = tk.Listbox(list_container, yscrollcommand=scrollbar.set, height=15)
            listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=listbox.yview)

            # 填充窗口列表
            for window in visible_windows:
                title = window.title
                if len(title) > 50:
                    title = title[:47] + "..."
                listbox.insert(tk.END, f"{title} ({window.width}x{window.height})")

            # 按钮框架
            button_frame = ttk.Frame(dialog)
            button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

            def on_select():
                selection = listbox.curselection()
                if selection:
                    selected_window = visible_windows[selection[0]]
                    self.window_manager._window = selected_window
                    self.window_manager._update_window_bounds()
                    self.add_history_entry(f"手动选择窗口: {selected_window.title}")
                    dialog.destroy()

            def on_cancel():
                dialog.destroy()

            ttk.Button(button_frame, text="确定", command=on_select).pack(side=tk.RIGHT, padx=(5, 0))
            ttk.Button(button_frame, text="取消", command=on_cancel).pack(side=tk.RIGHT)

            # 默认选择第一项
            if visible_windows:
                listbox.selection_set(0)
                listbox.focus_set()

            # 绑定双击事件
            listbox.bind('<Double-Button-1>', lambda e: on_select())

        except Exception as e:
            messagebox.showerror("错误", f"选择窗口时出错:\n{str(e)}")
            logger.error(f"选择窗口失败: {e}")

    def refresh_window(self):
        """刷新游戏窗口"""
        if self.window_manager.refresh_window():
            self.add_history_entry("游戏窗口已刷新")
        else:
            self.add_history_entry("刷新游戏窗口失败")

    def coordinate_update_loop(self):
        """坐标更新循环"""
        while self.running:
            try:
                # 更新窗口状态
                self.update_window_status()

                # 更新坐标显示
                self.update_coordinate_display()

                # 短暂延迟
                time.sleep(0.05)  # 20 FPS

            except Exception as e:
                logger.error(f"坐标更新循环错误: {e}")
                time.sleep(0.5)

    def start_coordinate_update(self):
        """启动坐标更新线程"""
        self.running = True
        self.update_thread = threading.Thread(target=self.coordinate_update_loop, daemon=True)
        self.update_thread.start()

    def quit(self):
        """退出程序"""
        self.running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1.0)
        self.root.quit()
        self.root.destroy()

    def run(self):
        """运行主程序"""
        try:
            # 设置窗口关闭事件
            self.root.protocol("WM_DELETE_WINDOW", self.quit)

            # 启动主循环
            self.root.mainloop()

        except KeyboardInterrupt:
            logger.info("用户中断程序")
        except Exception as e:
            logger.error(f"程序运行错误: {e}")
            messagebox.showerror("程序错误", f"程序运行时出错:\n{str(e)}")
        finally:
            self.quit()


def main():
    """主函数"""
    print("=== 游戏窗口坐标定位器 ===")
    print("使用说明:")
    print("1. 确保游戏窗口已打开")
    print("2. 将鼠标移动到游戏窗口内")
    print("3. 按空格键捕获当前坐标")
    print("4. 按ESC键退出程序")
    print("")

    try:
        locator = CoordinateLocator()
        locator.run()
    except Exception as e:
        logger.error(f"启动坐标定位器失败: {e}")
        print(f"启动失败: {e}")


if __name__ == "__main__":
    main()