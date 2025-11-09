# EM-Automate

EM-Automate 是一个基于 Electron + Vue3 + Python 的游戏自动化工具，专为《二重螺旋》游戏设计，提供自动化的委托、夜航手册和其他游戏任务的执行功能。

## 🎯 项目概述

本项目是一个桌面应用程序，通过图形界面自动化操作来执行游戏中的重复性任务，包括：
- 日常委托自动化
- 夜航手册任务执行
- 委托密函处理
- 多种任务类型支持（侦察、避险、驱逐、探险等）

## 🏗️ 技术架构

### 前端技术栈
- **Electron 27** - 桌面应用程序框架
- **Vue 3** - 现代化前端框架
- **TypeScript** - 类型安全的 JavaScript
- **Ant Design Vue** - UI 组件库
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **Vite** - 构建工具

### 后端技术栈
- **Python 3** - 后端开发语言
- **FastAPI** - 现代化 Web 框架
- **Uvicorn** - ASGI 服务器
- **PyAutoGUI** - 图形界面自动化
- **OpenCV** - 计算机视觉
- **Pydantic** - 数据验证

## 📁 项目结构

```
EM/
├── frontend/                 # 前端代码
│   ├── src/
│   │   ├── components/      # Vue 组件
│   │   ├── stores/         # Pinia 状态管理
│   │   ├── types/          # TypeScript 类型定义
│   │   ├── utils/          # 工具函数
│   │   └── main.ts         # 应用入口
│   ├── public/             # 静态资源
│   ├── assets/             # 资源文件
│   ├── package.json        # 前端依赖配置
│   └── vite.config.ts      # Vite 配置
├── backend/                 # 后端代码
│   ├── core/               # 核心自动化逻辑
│   ├── api_server.py       # FastAPI 服务器
│   ├── requirements.txt    # Python 依赖
│   └── pyproject.toml      # Python 项目配置
├── menu_config.json        # 菜单配置文件
└── README.md              # 项目文档
```

## 🚀 快速开始

### 环境要求

- **Node.js** >= 16.0.0
- **Python** >= 3.8
- **pnpm** >= 8.0.0 (推荐)

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/your-repo/EM.git
   cd EM
   ```

2. **安装前端依赖**
   ```bash
   cd frontend
   pnpm install
   ```

3. **设置后端环境**
   ```bash
   cd backend
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate

   pip install -r requirements.txt
   ```

### 开发模式

1. **启动前端开发服务器**
   ```bash
   cd frontend
   pnpm run dev
   ```

2. **启动后端 API 服务器**
   ```bash
   cd backend
   python api_server.py
   ```

3. **启动 Electron 应用**
   ```bash
   cd frontend
   pnpm run electron:dev
   ```

### 生产构建

1. **构建前端**
   ```bash
   cd frontend
   pnpm run build
   ```

2. **打包 Electron 应用**
   ```bash
   cd frontend
   pnpm run electron:build
   ```

## 📖 功能特性

### 🎮 支持的任务类型

- **侦察任务** - 无限执行模式
- **避险任务** - 角色经验获取
- **驱逐任务** - 武器经验获取
- **探险任务** - 角色突破材料
- **调停任务** - 武器突破材料
- **驱离任务** - 魔之楔收集
- **护送任务** - 深红凝珠获取
- **追缉任务** - 角色技能材料
- **扼守任务** - 共鸣技能材料
- **迁移任务** - 铸造材料获取

### 🏆 夜航手册支持

- LV20-LV80 全等级覆盖
- 多种敌人类型识别
- 自动战斗执行

### 📋 委托密函

- 角色密函处理
- 武器密函处理
- 魔之楔密函处理

## ⚙️ 配置说明

### 菜单配置

项目使用 `menu_config.json` 文件来管理所有任务配置，包括：
- 任务类型定义
- 等级设置
- 显示名称映射

### 应用设置

前端通过 Pinia store 管理应用状态，后端通过 FastAPI 提供配置接口。

## 🔧 开发指南

### 添加新任务

1. 在 `menu_config.json` 中添加任务配置
2. 在后端 `core/automation.py` 中实现自动化逻辑
3. 在前端组件中添加对应的 UI 控件

### 自定义自动化流程

1. 修改 `backend/core/automation.py`
2. 添加新的图像识别模板
3. 实现对应的操作逻辑

## 🐛 故障排除

### 常见问题

1. **Python 环境问题**
   - 确保使用正确的 Python 版本
   - 激活虚拟环境

2. **依赖安装失败**
   - 清除缓存重新安装
   - 检查网络连接

3. **自动化识别失败**
   - 检查游戏分辨率设置
   - 确保游戏窗口在前台

### 日志查看

- 前端日志：浏览器开发者工具控制台
- 后端日志：`backend/erm_backend.log`

## 📝 更新日志

### v1.0.0
- 初始版本发布
- 基础委托功能
- 夜航手册支持
- 委托密函处理

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## ⚠️ 免责声明

本工具仅供学习和研究目的使用。使用本工具自动化游戏操作可能违反游戏服务条款，请自行承担使用风险。开发者不对因使用本工具而导致的任何账号问题负责。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件至：[your-email@example.com]

---

**Happy Gaming! 🎮**