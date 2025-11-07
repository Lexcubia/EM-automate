# SCSS 样式指南

## 概述
本项目已配置支持 SCSS 预处理器，所有样式文件应使用 SCSS 语法编写。

## 文件结构

```
src/styles/
├── variables.scss     # SCSS 变量定义
├── global.scss        # 全局样式
├── mixins.scss        # SCSS 混入
└── components/        # 组件样式
    ├── _buttons.scss
    ├── _cards.scss
    └── ...
```

## 已配置功能

### 1. SCSS 变量
- 颜色系统（主题色、中性色）
- 字体系统
- 间距系统
- 圆角、阴影
- 动画过渡
- 响应式断点

### 2. 全局工具类
- 布局类：`.flex`, `.flex-center`, `.flex-between`
- 间距类：`.m-xs`, `.p-sm`, `.mx-lg` 等
- 文字对齐：`.text-center`, `.text-left`
- 颜色类：`.text-primary`, `.bg-success`
- 圆角阴影：`.rounded`, `.shadow`

### 3. 响应式支持
- 预定义断点变量
- 响应式工具类

## 使用指南

### 在 Vue 组件中使用
```vue
<style lang="scss" scoped>
.my-component {
  // 使用 SCSS 变量
  color: $primary-color;
  padding: $spacing-md;
  border-radius: $border-radius-base;

  // 嵌套语法
  .child-element {
    font-size: $font-size-sm;

    &:hover {
      color: $primary-color;
      transition: $transition-base;
    }
  }

  // 使用全局工具类
  @extend .flex-center;
}
</style>
```

### 添加新的 SCSS 文件
在 `src/styles/` 目录下创建新的 `.scss` 文件，然后在需要的地方导入：

```scss
@import '@/styles/variables';
@import '@/styles/mixins';
```

## 最佳实践

1. **优先使用变量**：使用预定义的变量而不是硬编码值
2. **保持嵌套简洁**：避免超过3层嵌套
3. **使用混入**：将重复的样式规则提取为混入
4. **模块化样式**：按功能拆分样式文件
5. **响应式设计**：使用预定义的断点变量

## 修改现有组件

要将现有的 `<style>` 标签转换为 SCSS：

1. 将 `<style>` 改为 `<style lang="scss">`
2. 如果有 `scoped` 属性，保留：`<style lang="scss" scoped>`
3. 使用 SCSS 语法重写样式：
   - 使用变量替换硬编码值
   - 使用嵌套语法
   - 使用混入和函数

## 示例转换

### 转换前（CSS）：
```css
.my-component {
  height: 100vh;
  background: #1890ff;
  padding: 16px;
  border-radius: 6px;
}

.my-child {
  color: #ffffff;
}

.my-child:hover {
  opacity: 0.8;
}
```

### 转换后（SCSS）：
```scss
.my-component {
  height: 100vh;
  background: $primary-color;
  padding: $spacing-md;
  border-radius: $border-radius-base;

  .my-child {
    color: $white;
    transition: $transition-base;

    &:hover {
      opacity: 0.8;
    }
  }
}
```