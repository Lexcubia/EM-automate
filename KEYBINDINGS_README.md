# 键位配置系统使用指南

本文档介绍EM-Automate项目中键位配置系统的使用方法。

## 🎯 系统概述

键位配置系统允许用户：
- 自定义游戏操作的键位映射
- 导入导出配置
- 重置为默认配置
- 在自动化脚本中使用配置的键位
- 系统采用单配置模式，确保配置的一致性

## 📁 文件结构

```
backend/
├── config/
│   └── keybindings.json          # 键位配置文件
├── core/
│   ├── keybindings.py            # 键位管理核心模块（单配置模式）
│   └── automation_example.py     # 自动化使用示例
└── api_server.py                 # API接口（已集成键位相关接口）

frontend/
├── src/
│   ├── components/
│   │   └── KeyboardPanel.vue     # 键位配置界面组件
│   ├── types/
│   │   └── index.d.ts           # 类型定义（已添加键位相关类型）
│   └── utils/
│       └── api.ts               # API工具（已添加键位相关API）
```

## ⚙️ 配置文件格式

### JSON配置结构

```json
{
  "bindings": {
    "melee_attack": "left_mouse",
    "ranged_attack": "right_mouse",
    "skill": "E",
    "ultimate": "Q",
    "spirit_support": "Z",
    "jump": "space",
    // ... 更多键位映射
  },
  "action_names": {
    "melee_attack": "近战攻击",
    "ranged_attack": "远程攻击",
    "skill": "战技",
    "ultimate": "终结技",
    // ... 动作名称映射
  },
  "key_names": {
    "left_mouse": "鼠标左键",
    "right_mouse": "鼠标右键",
    "space": "空格",
    "E": "E键",
    // ... 按键名称映射
  }
}
```

## 🔧 后端使用方法

### 1. 基本使用

```python
from core.keybindings import keybindings_manager

# 获取当前键位配置
bindings = keybindings_manager.get_current_bindings()

# 执行指定动作
keybindings_manager.execute_action("skill", "press", 0.1)

# 设置新的键位
keybindings_manager.set_binding("skill", "R")
```

### 2. 配置管理

```python
# 导出当前配置
keybindings_manager.export_config("keybindings_backup.json")

# 导入配置
keybindings_manager.import_config("keybindings_backup.json")

# 重置为默认配置
keybindings_manager.reset_to_default()
```

### 3. 在自动化脚本中使用

```python
from core.automation_example import GameAutomationExample

# 创建自动化实例
automation = GameAutomationExample()

# 执行基础战斗序列
automation.basic_combat_sequence()

# 执行自定义动作序列
custom_actions = [
    {"action": "jump", "press_type": "press", "duration": 0.1, "delay": 0.5},
    {"action": "skill", "press_type": "press", "duration": 0.1, "delay": 1.0}
]
automation.custom_action_sequence(custom_actions)
```

## 🖥️ 前端界面使用

### 1. 在Vue组件中使用

```vue
<template>
  <div>
    <KeyboardPanel />
  </div>
</template>

<script setup>
import KeyboardPanel from '@/components/KeyboardPanel.vue'
</script>
```

### 2. 通过API调用

```typescript
import { keybindingsApi } from '@/utils/api'

// 获取键位配置
const config = await keybindingsApi.getKeybindings()

// 更新键位
await keybindingsApi.updateKeybinding('skill', 'R')

// 执行键位测试
await keybindingsApi.executeKeybinding('skill', 'press', 0.1)

// 导出配置
await keybindingsApi.exportConfig('backup.json')

// 重置配置
await keybindingsApi.resetConfig()
```

## 🎮 支持的动作类型

| 动作ID | 中文名称 | 默认按键 | 说明 |
|--------|----------|----------|------|
| melee_attack | 近战攻击 | 鼠标左键 | 近战武器攻击 |
| ranged_attack | 远程攻击 | 鼠标右键 | 远程武器攻击 |
| skill | 战技 | E | 角色技能 |
| ultimate | 终结技 | Q | 大招技能 |
| spirit_support | 魔灵支援 | Z | 召唤支援 |
| jump | 跳跃 | 空格 | 角色跳跃 |
| slide_crouch | 滑行/下蹲 | 左Ctrl | 滑行或下蹲 |
| dodge | 闪避 | 左Shift | 快速闪避 |
| revive | 复苏 | X | 复活技能 |
| reload | 装填子弹 | R | 重新装弹 |
| backpack | 背包 | B | 打开背包 |
| interact | 交互 | F | 与物体交互 |
| training | 历练 | L | 打开历练界面 |
| map | 地图 | M | 打开地图 |
| tactical_backpack | 战术背包 | Tab | 战术装备 |
| abandon_challenge | 放弃挑战 | P | 放弃当前挑战 |
| move_forward | 前进 | W | 向前移动 |
| move_backward | 后退 | S | 向后移动 |
| move_left | 左移 | A | 向左移动 |
| move_right | 右移 | D | 向右移动 |

## 🔌 API接口

### 获取当前键位配置
```
GET /api/keybindings/current
```

### 更新键位配置
```
POST /api/keybindings/update
{
  "action": "skill",
  "key": "R"
}
```

### 执行键位操作
```
POST /api/keybindings/execute
{
  "action": "skill",
  "press_type": "press",
  "duration": 0.1
}
```

### 获取配置文件列表
```
GET /api/keybindings/profiles
```

### 创建配置文件
```
POST /api/keybindings/profiles/create
{
  "profile_id": "custom_config",
  "name": "自定义配置",
  "description": "我的个人配置"
}
```

## 📝 最佳实践

1. **键位冲突检测**：系统会自动检测键位冲突，避免多个动作使用同一个按键。

2. **配置备份**：定期导出配置文件作为备份，避免意外丢失。

3. **环境适配**：为不同的游戏环境（如PVP、PVE）创建专门的配置文件。

4. **测试验证**：修改键位后使用测试功能验证配置是否正确。

5. **自动化集成**：在自动化脚本中使用键位管理器，保持配置的一致性。

## 🚨 注意事项

1. 修改键位配置会影响所有使用该配置的自动化脚本。

2. 删除配置文件时，系统会自动切换到默认配置。

3. 导入配置文件时，请确保文件格式正确且来源可信。

4. 某些特殊按键（如功能键）可能需要管理员权限才能正常工作。

5. 游戏更新可能导致原有键位配置失效，需要及时更新。

## 🔍 故障排除

### 常见问题

**Q: 键位测试失败**
A: 检查游戏窗口是否在前台，确保按键配置正确。

**Q: 配置文件导入失败**
A: 检查JSON文件格式是否正确，确保文件包含必要的字段。

**Q: 自动化脚本中的键位不生效**
A: 确认当前使用的配置文件正确，检查键位是否已被修改。

**Q: 按键冲突警告**
A: 检查是否有多个动作使用了同一个按键，修改其中一个即可。

---

如需更多帮助，请查看项目文档或提交Issue。