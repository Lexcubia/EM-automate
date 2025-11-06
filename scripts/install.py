#!/usr/bin/env python3
"""
EM-Automate 依赖安装脚本
跨平台 Python 实现，自动安装前后端所有依赖
"""

import os
import sys
import subprocess
import platform
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


def run_command(cmd, cwd=None, check=True, capture_output=False):
    """执行系统命令"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            check=check,
            capture_output=capture_output,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        Colors.error(f"命令执行失败: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        Colors.error(f"错误信息: {e}")
        return None


def check_command_exists(command):
    """检查命令是否存在"""
    try:
        subprocess.run([command, '--version'],
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_package_manager():
    """安装 pnpm 包管理器"""
    Colors.step("3. 检查/安装 pnpm 包管理器...")

    if not check_command_exists('pnpm'):
        Colors.info("pnpm 未找到，正在安装...")
        if not run_command("npm install -g pnpm"):
            Colors.error("pnpm 安装失败")
            return False
        Colors.success("pnpm 安装成功")
    else:
        result = run_command("pnpm --version", capture_output=True)
        Colors.success(f"pnpm 已安装 (版本: {result.stdout.strip()})")

    return True


def install_python_deps(backend_path):
    """安装 Python 依赖"""
    Colors.step("4. 安装后端 Python 依赖...")

    venv_path = backend_path / "venv"

    # 创建虚拟环境
    if not venv_path.exists():
        Colors.info("创建 Python 虚拟环境...")
        if not run_command(f"python -m venv venv", cwd=backend_path):
            Colors.error("虚拟环境创建失败")
            return False
        Colors.success("虚拟环境创建成功")
    else:
        Colors.warning("虚拟环境已存在，跳过创建")

    # 激活虚拟环境并安装依赖
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip.exe"
        requirements_file = "requirements.txt"
    else:
        pip_cmd = "venv/bin/pip"
        requirements_file = "requirements.txt"

    Colors.info("安装 Python 依赖包...")
    if not run_command(f"{pip_cmd} install -r {requirements_file}", cwd=backend_path):
        Colors.error("Python 依赖安装失败")
        return False

    Colors.success("Python 依赖安装完成")
    return True


def install_node_deps(frontend_path):
    """安装 Node.js 依赖"""
    Colors.step("5. 安装前端 Node.js 依赖...")

    Colors.info("安装前端依赖包...")
    if not run_command("pnpm install", cwd=frontend_path):
        Colors.error("前端依赖安装失败")
        return False

    Colors.success("前端依赖安装完成")
    return True


def main():
    """主函数"""
    print("=" * 40)
    print("EM-Automate 依赖安装脚本")
    print("=" * 40)

    # 获取脚本路径
    script_dir = Path(__file__).parent
    backend_path = script_dir.parent / "backend"
    frontend_path = script_dir.parent / "frontend"

    # 检查项目结构
    if not backend_path.exists():
        Colors.error(f"后端目录不存在: {backend_path}")
        return 1

    if not frontend_path.exists():
        Colors.error(f"前端目录不存在: {frontend_path}")
        return 1

    Colors.step("1. 检查 Python 环境...")
    if not check_command_exists('python') and not check_command_exists('python3'):
        Colors.error("未找到 Python，请先安装 Python 3.8+")
        return 1

    result = run_command("python --version", capture_output=True) or run_command("python3 --version", capture_output=True)
    Colors.success(f"Python: {result.stdout.strip()}")

    Colors.step("2. 检查 Node.js 环境...")
    if not check_command_exists('node'):
        Colors.error("未找到 Node.js，请先安装 Node.js")
        return 1

    result = run_command("node --version", capture_output=True)
    Colors.success(f"Node.js: {result.stdout.strip()}")

    # 安装依赖
    if not install_package_manager():
        return 1

    if not install_python_deps(backend_path):
        return 1

    if not install_node_deps(frontend_path):
        return 1

    print()
    print("=" * 40)
    Colors.success("所有依赖安装成功！")
    print("=" * 40)
    print()
    print("使用说明：")
    print("  启动项目: python start_project.py")
    print("  打包项目: python build_project.py")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())