# EM-Automate 项目脚本

本目录包含项目的便捷管理脚本，支持 **Python** 和 **Shell/Batch** 两种实现。

## 推荐使用：Python 脚本

Python 脚本具有更好的跨平台兼容性、错误处理和用户体验。

### 1. 依赖安装脚本
**脚本**: `install.py`

**功能**：
- 自动检查 Python 3.8+ 和 Node.js 环境
- 安装 pnpm 包管理器（如不存在）
- 创建 Python 虚拟环境并安装后端依赖
- 安装前端 Vue3 + Electron 依赖
- 彩色终端输出和详细进度提示

**使用方法**：
```bash
python install.py
# 或
python3 install.py
```

### 2. 项目启动脚本
**脚本**: `start.py`

**功能**：
- 同时启动后端 FastAPI 服务器 (端口 8000) 和前端 Vue3 开发服务器 (端口 5173)
- Windows 下自动打开新窗口显示日志
- Linux/macOS 支持优雅的服务停止 (Ctrl+C)
- 自动环境检查和服务状态监控

**使用方法**：
```bash
python start.py
# 或
python3 start.py
```

**访问地址**：
- 前端界面: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

### 3. 项目打包脚本
**脚本**: `build.py`

**功能**：
- 构建前端生产版本
- 使用 Electron Builder 打包桌面应用
- 生成各平台的安装包
- 自动清理临时文件

**使用方法**：
```bash
python build.py
# 或
python3 build.py
```

**输出位置**：
- Windows: `dist/*.exe` (安装包) 和 `dist/win-unpacked/` (便携版)
- Linux: `dist/*.AppImage`
- macOS: `dist/*.dmg`

## 备用方案：Shell/Batch 脚本

如果 Python 环境不可用，可使用传统脚本：

| 功能 | Windows | Linux/macOS |
|------|---------|-------------|
| 依赖安装 | `install-deps.bat` | `install-deps.sh` |
| 项目启动 | `run-start.bat` | `run-start.sh` |
| 项目打包 | `run-build.bat` | `run-build.sh` |

## 使用顺序

1. **首次使用**：`python install.py` 安装所有依赖
2. **开发调试**：`python start.py` 启动开发服务器
3. **发布打包**：`python build.py` 生成安装包

## 环境要求

- **Python**: 3.8+ (推荐使用 Python 脚本)
- **Node.js**: 16.0+
- **操作系统**: Windows 10+, macOS 10.14+, Linux

## Python 脚本特性

- ✅ **跨平台兼容**：同一脚本适用于所有操作系统
- ✅ **彩色输出**：清晰的状态提示和错误信息
- ✅ **环境检查**：自动检测所需环境和依赖
- ✅ **错误处理**：完善的异常捕获和用户友好提示
- ✅ **进程管理**：优雅的服务启动和停止
- ✅ **自动清理**：打包后自动清理临时文件

## 故障排除

### Python 版本问题
```bash
# 检查 Python 版本
python --version
python3 --version

# 如果提示 "python 不是内部或外部命令"，请使用 python3
```

### 权限问题 (Linux/macOS)
```bash
# 给脚本添加执行权限（如果需要）
chmod +x *.py
```

### 端口占用
- 如果 8000 或 5173 端口被占用，脚本会提示错误
- 使用以下命令查找占用进程：
  ```bash
  # Windows
  netstat -ano | findstr :8000
  netstat -ano | findstr :5173

  # Linux/macOS
  lsof -i :8000
  lsof -i :5173
  ```

### 依赖安装失败
- 确保网络连接正常
- 检查 Python 和 Node.js 是否正确安装
- Windows 用户可能需要管理员权限