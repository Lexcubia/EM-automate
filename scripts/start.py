#!/usr/bin/env python3
"""
EM-Automate 项目启动脚本
跨平台 Python 实现，同时启动前后端开发服务器
"""

import os
import sys
import subprocess
import signal
import time
import platform
import threading
from pathlib import Path


class Colors:
    """终端颜色输出"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

    @staticmethod
    def success(msg):
        print(f"{Colors.GREEN}[完成]{Colors.END} {msg}")

    @staticmethod
    def error(msg):
        print(f"{Colors.RED}[错误]{Colors.END} {msg}")

    @staticmethod
    def warning(msg):
        print(f"{Colors.YELLOW}[警告]{Colors.END} {msg}")

    @staticmethod
    def info(msg):
        print(f"{Colors.BLUE}[信息]{Colors.END} {msg}")

    @staticmethod
    def step(msg):
        print(f"{Colors.BOLD}{msg}{Colors.END}")


class OutputReader:
    """输出读取器，用于实时显示子进程输出"""

    def __init__(self, process, name, color_prefix):
        self.process = process
        self.name = name
        self.color_prefix = color_prefix
        self.running = True

    def read_output(self, stream):
        """读取并输出流"""
        while self.running:
            try:
                line = stream.readline()
                if line:
                    print(f"{self.color_prefix}[{self.name}]{Colors.END} {line.strip()}")
                else:
                    break
            except:
                break

    def start_reading(self, stdout, stderr):
        """开始读取输出"""
        threading.Thread(target=self.read_output, args=(stdout,), daemon=True).start()
        threading.Thread(target=self.read_output, args=(stderr,), daemon=True).start()


class ProjectStarter:
    """项目启动器"""

    def __init__(self):
        self.processes = []
        self.script_dir = Path(__file__).parent
        self.backend_path = self.script_dir.parent / "backend"
        self.frontend_path = self.script_dir.parent / "frontend"

    def check_command_exists(self, command):
        """检查命令是否存在"""
        try:
            subprocess.run([command, '--version'],
                          capture_output=True, check=True, timeout=5)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def check_environment(self):
        """检查环境是否就绪"""
        Colors.step("1. 检查环境...")

        # 检查 pnpm 是否安装（Windows 下使用 pnpm.cmd）
        pnpm_cmd = 'pnpm.cmd' if platform.system() == "Windows" else 'pnpm'
        if not self.check_command_exists(pnpm_cmd):
            Colors.error("pnpm 未安装或不在 PATH 中")
            Colors.info("请先运行 python install_deps.py 安装依赖，或手动安装 pnpm")
            return False

        # 检查后端虚拟环境
        venv_path = self.backend_path / "venv"
        if not venv_path.exists():
            Colors.error("后端虚拟环境不存在，请先运行 python install_deps.py")
            return False

        # 检查前端依赖
        node_modules = self.frontend_path / "node_modules"
        if not node_modules.exists():
            Colors.error("前端依赖不存在，请先运行 python install_deps.py")
            return False

        Colors.success("环境检查通过")
        return True

    def start_backend(self):
        """启动后端服务"""
        Colors.step("2. 启动后端服务...")

        # 确定虚拟环境的 Python 路径
        if platform.system() == "Windows":
            python_path = self.backend_path / "venv" / "Scripts" / "python.exe"
        else:
            python_path = self.backend_path / "venv" / "bin" / "python"

        # 检查 Python 可执行文件是否存在
        if not python_path.exists():
            Colors.error(f"Python 虚拟环境未找到: {python_path}")
            Colors.info("请先运行 python install.py 安装依赖")
            return False

        # 启动 FastAPI 服务器
        backend_cmd = [str(python_path), "-m", "uvicorn", "api_server:app", "--reload", "--host", "127.0.0.1", "--port", "8000"]

        Colors.info("启动 FastAPI 服务器 (端口 8000)...")

        try:
            process = subprocess.Popen(
                backend_cmd,
                cwd=self.backend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # 创建输出读取器
            reader = OutputReader(process, "后端", Colors.BLUE)
            reader.start_reading(process.stdout, process.stderr)

            self.processes.append(('backend', process, reader))
            Colors.success("后端服务启动成功")
            return True

        except Exception as e:
            Colors.error(f"后端服务启动失败: {e}")
            Colors.error(f"请检查以下路径是否存在: {python_path}")
            return False

    def start_frontend(self):
        """启动前端服务"""
        Colors.step("3. 启动前端服务...")

        # 根据平台选择正确的命令
        if platform.system() == "Windows":
            frontend_cmd = ["pnpm.cmd", "run", "dev"]
        else:
            frontend_cmd = ["pnpm", "run", "dev"]

        Colors.info("启动 Vue3 开发服务器 (端口 5173)...")

        try:
            process = subprocess.Popen(
                frontend_cmd,
                cwd=self.frontend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # 创建输出读取器
            reader = OutputReader(process, "前端", Colors.GREEN)
            reader.start_reading(process.stdout, process.stderr)

            self.processes.append(('frontend', process, reader))
            Colors.success("前端服务启动成功")
            return True

        except Exception as e:
            Colors.error(f"前端服务启动失败: {e}")
            return False

    def wait_for_services(self):
        """等待服务启动"""
        Colors.step("4. 等待服务就绪...")

        Colors.info("等待后端服务启动...")
        time.sleep(3)

        Colors.info("等待前端服务启动...")
        time.sleep(5)

        Colors.success("所有服务已就绪")

    def show_service_info(self):
        """显示服务信息"""
        print()
        print("=" * 40)
        Colors.success("服务启动成功！")
        print("=" * 40)
        print()
        print("服务地址：")
        print("  前端: http://localhost:5173")
        print("  后端: http://localhost:8000")
        print("  后端文档: http://localhost:8000/docs")
        print()
        print("实时日志输出将显示在下方，按 Ctrl+C 停止所有服务")
        print("-" * 50)

    def cleanup(self):
        """清理资源"""
        Colors.info("正在停止所有服务...")
        for name, process, reader in self.processes:
            try:
                # 停止输出读取器
                if hasattr(reader, 'running'):
                    reader.running = False

                if process.poll() is None:  # 进程仍在运行
                    process.terminate()
                    # 等待进程结束，最多等待5秒
                    process.wait(timeout=5)
                    Colors.success(f"{name} 服务已停止")
            except subprocess.TimeoutExpired:
                Colors.warning(f"强制终止 {name} 服务")
                process.kill()
            except Exception as e:
                Colors.error(f"停止 {name} 服务时出错: {e}")

    def signal_handler(self, signum, frame):
        """信号处理器"""
        print()
        Colors.info("接收到中断信号，正在关闭服务...")
        self.cleanup()
        sys.exit(0)

    def run(self):
        """运行启动器"""
        print("=" * 40)
        print("EM-Automate 项目启动脚本")
        print("=" * 40)

        # 检查环境
        if not self.check_environment():
            return 1

        # 启动服务
        if not self.start_backend():
            return 1

        if not self.start_frontend():
            self.cleanup()
            return 1

        # 等待服务就绪
        self.wait_for_services()

        # 显示服务信息
        self.show_service_info()

        # 注册信号处理器
        try:
            signal.signal(signal.SIGINT, self.signal_handler)
            if platform.system() != "Windows":
                signal.signal(signal.SIGTERM, self.signal_handler)
        except (AttributeError, OSError):
            # Windows 下可能不支持某些信号
            pass

        # 保持脚本运行
        try:
            for name, process, reader in self.processes:
                process.wait()
        except KeyboardInterrupt:
            print()
            Colors.info("接收到中断信号，正在关闭服务...")
        finally:
            self.cleanup()

        return 0


def main():
    """主函数"""
    starter = ProjectStarter()
    return starter.run()


if __name__ == "__main__":
    sys.exit(main())