#!/usr/bin/env python3
"""
EM-Automate 项目打包脚本
跨平台 Python 实现，构建并打包 Electron 应用
"""

import os
import sys
import subprocess
import shutil
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


class ProjectBuilder:
    """项目打包器"""

    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.backend_path = self.script_dir.parent / "backend"
        self.frontend_path = self.script_dir.parent / "frontend"
        self.dist_path = self.script_dir.parent / "dist"

    def run_command(self, cmd, cwd=None, check=True):
        """执行系统命令"""
        try:
            subprocess.run(cmd, shell=True, cwd=cwd, check=check)
            return True
        except subprocess.CalledProcessError as e:
            Colors.error(f"命令执行失败: {cmd}")
            Colors.error(f"错误信息: {e}")
            return False

    def check_environment(self):
        """检查环境是否就绪"""
        Colors.step("1. 检查环境...")

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

    def check_backend_api(self):
        """检查后端 API 服务器文件"""
        Colors.step("2. 检查后端 API 服务器文件...")

        api_server_py = self.backend_path / "api_server.py"
        api_server_pkg = self.backend_path / "api_server"

        if not api_server_py.exists() and not api_server_pkg.exists():
            Colors.error("未找到后端 API 服务器文件")
            Colors.info("请确保 backend 目录中包含 api_server.py 或 api_server 包")
            return False

        Colors.success("后端 API 服务器文件检查通过")
        return True

    def build_frontend(self):
        """构建前端项目"""
        Colors.step("3. 构建前端项目...")

        Colors.info("正在构建前端...")
        if not self.run_command("pnpm run build", cwd=self.frontend_path):
            Colors.error("前端构建失败")
            return False

        Colors.success("前端构建完成")
        return True

    def package_electron_app(self):
        """打包 Electron 应用"""
        Colors.step("4. 打包 Electron 应用...")

        Colors.info("正在打包桌面应用...")
        if not self.run_command("pnpm run electron:build", cwd=self.frontend_path):
            Colors.error("Electron 打包失败")
            return False

        Colors.success("Electron 应用打包完成")
        return True

    def cleanup_temp_files(self):
        """清理临时文件"""
        Colors.step("5. 清理临时文件...")

        # 清理前端构建缓存
        frontend_dist = self.frontend_path / "dist"
        if frontend_dist.exists():
            Colors.info("清理前端构建缓存...")
            try:
                shutil.rmtree(frontend_dist)
                Colors.success("前端构建缓存清理完成")
            except Exception as e:
                Colors.warning(f"清理前端构建缓存失败: {e}")

    def show_build_results(self):
        """显示打包结果"""
        print()
        print("=" * 40)
        Colors.success("应用打包成功！")
        print("=" * 40)
        print()
        print(f"输出目录: {self.dist_path}")
        print()

        # 根据平台显示不同的输出信息
        system = platform.system()
        if system == "Windows":
            print("安装包位置：")
            print(f"  Windows: {self.dist_path}\\*.exe")
            print(f"  便携版: {self.dist_path}\\win-unpacked\\")
        elif system == "Darwin":  # macOS
            print("安装包位置：")
            print(f"  macOS: {self.dist_path}/*.dmg")
        else:  # Linux
            print("安装包位置：")
            print(f"  Linux: {self.dist_path}/*.AppImage")

        print()
        Colors.info("可以将安装包分发给其他用户使用")

    def run(self):
        """运行打包器"""
        print("=" * 40)
        print("EM-Automate 项目打包脚本")
        print("=" * 40)

        # 检查环境
        if not self.check_environment():
            return 1

        # 检查后端 API
        if not self.check_backend_api():
            return 1

        # 构建前端
        if not self.build_frontend():
            return 1

        # 打包 Electron 应用
        if not self.package_electron_app():
            return 1

        # 清理临时文件
        self.cleanup_temp_files()

        # 显示结果
        self.show_build_results()

        return 0


def main():
    """主函数"""
    builder = ProjectBuilder()
    return builder.run()


if __name__ == "__main__":
    sys.exit(main())