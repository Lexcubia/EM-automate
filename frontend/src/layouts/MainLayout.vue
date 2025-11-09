<template>
  <div class="main-layout" :class="{ dark: isDarkMode }">
    <!-- 顶部标题栏 -->
    <header class="header">
      <div class="header-content">
        <div class="title">
          <h1>EM-Automate</h1>
          <span class="version">v{{ appStore.appVersion }}</span>
        </div>
        <div class="header-actions">
          <!-- 暗黑模式切换按钮 -->
          <a-button type="text" @click="toggleDarkMode" class="theme-toggle" :title="isDarkMode ? '切换到亮色模式' : '切换到暗黑模式'">
            <template #icon>
              <BulbOutlined v-if="!isDarkMode" />
              <BulbFilled v-else />
            </template>
          </a-button>
          <div class="status-info">
            <a-tag v-if="appStore.isBackendReady" :color="isDarkMode ? 'green' : 'green'">
              <template #icon>
                <CheckCircleOutlined />
              </template>
              后端已连接
            </a-tag>
            <a-tag v-else color="red">
              <template #icon>
                <CloseCircleOutlined />
              </template>
              后端未连接
            </a-tag>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区域 -->
    <main class="main-content">
      <div class="content-wrapper">
        <!-- 左侧：可收缩的侧边菜单 -->
        <aside class="sidebar" :class="{ collapsed: isCollapsed }">
          <!-- 收缩/展开按钮 -->
          <div class="sidebar-toggle">
            <a-button type="text" @click="toggleSidebar" class="toggle-btn" :title="isCollapsed ? '展开菜单' : '收缩菜单'">
              <template #icon>
                <MenuUnfoldOutlined v-if="isCollapsed" />
                <MenuFoldOutlined v-else />
              </template>
            </a-button>
          </div>

          <!-- 菜单内容 -->
          <a-menu v-model:selectedKeys="selectedKeys" mode="inline" @click="handleMenuClick" class="sidebar-menu" :inline-collapsed="isCollapsed">
            <a-menu-item v-for="item in menuItems" :key="item.key">
              <template #icon>
                <component :is="getIconComponent(item.icon || '')" />
              </template>
              <span>{{ item.name }}</span>
            </a-menu-item>
          </a-menu>
        </aside>

        <!-- 右侧：主内容区域 -->
        <section class="main-panel">
          <!-- 路由视图，根据当前路由显示对应组件 -->
          <router-view />
        </section>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  RocketOutlined,
  ControlOutlined,
  FileTextOutlined,
  ExperimentOutlined,
  InfoCircleOutlined,
  BulbOutlined,
  BulbFilled
} from "@ant-design/icons-vue"
import { useAppStore } from "@/stores/app"
import { useTaskStore } from "@/stores/task"
import { generateMenuFromRoutes, getMenuKeyFromPath } from "@/utils/menu-generator"

// Store
const appStore = useAppStore()
const taskStore = useTaskStore()

// Router
const route = useRoute()
const router = useRouter()

// Props - 移除未使用的 props

// 响应式数据
const selectedKeys = ref<string[]>([])
const logs = ref<Array<{
  type: string
  message: string
  time: string
}>>([])
const logContainer = ref<HTMLElement | null>(null)
const isCollapsed = ref(false)
const isDarkMode = ref(localStorage.getItem("darkMode") === "true")

// 从路由生成菜单项
const menuItems = computed(() => {
  return generateMenuFromRoutes([...router.options.routes])
})

// 图标组件映射
const iconComponentMap: Record<string, any> = {
  RocketOutlined,
  ControlOutlined,
  FileTextOutlined,
  ExperimentOutlined,
  InfoCircleOutlined,
}

// 获取图标组件
const getIconComponent = (iconName: string) => {
  return iconComponentMap[iconName] || RocketOutlined
}

// 根据当前路由更新选中的菜单键
const updateSelectedKeys = () => {
  const menuKey = getMenuKeyFromPath(route.path, menuItems.value)
  selectedKeys.value = menuKey ? [menuKey] : ['training']
}

// 菜单点击处理 - 使用路由导航
const handleMenuClick = ({ key }: { key: string }) => {
  const menuItem = menuItems.value.find(item => item.key === key)
  if (menuItem) {
    router.push(menuItem.path)
  }
}

// 侧边栏收缩/展开
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
  localStorage.setItem("sidebarCollapsed", String(isCollapsed.value))
}

// 暗黑模式切换
const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value
  localStorage.setItem("darkMode", String(isDarkMode.value))
  applyTheme()
}

// 应用主题
const applyTheme = () => {
  if (isDarkMode.value) {
    document.documentElement.classList.add("dark")
  } else {
    document.documentElement.classList.remove("dark")
  }
}

// 日志相关方法
const addLog = (type: string, message: string) => {
  const logEntry = {
    type,
    message,
    time: new Date().toLocaleTimeString(),
  }

  logs.value.push(logEntry)

  // 保持日志数量在合理范围内
  if (logs.value.length > 100) {
    logs.value.splice(0, logs.value.length - 100)
  }

  // 自动滚动到底部
  nextTick(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight
    }
  })
}


// 暴露给历练组件的方法
const handleTaskSelected = (task: any) => {
  taskStore.addTask(task)
  addLog("info", `添加任务: ${task.display_name} x${task.run_count}`)
}

const startTasks = async () => {
  try {
    addLog("info", "开始执行任务队列...")
    await taskStore.startExecution()
    addLog("success", `任务执行已启动`)
  } catch (error) {
    addLog("error", `启动任务失败: ${(error as Error).message}`)
    appStore.showError("启动失败", (error as Error).message)
  }
}

const stopTasks = async () => {
  try {
    addLog("warning", "正在停止任务执行...")
    await taskStore.stopExecution()
    addLog("warning", "任务执行已停止")
  } catch (error) {
    addLog("error", `停止任务失败: ${(error as Error).message}`)
    appStore.showError("停止失败", (error as Error).message)
  }
}

const clearQueue = () => {
  taskStore.clearQueue()
  addLog("info", "已清空任务队列")
}

// 应用初始化
const initializeApp = async () => {
  try {
    addLog("info", "正在初始化应用...")

    if (!appStore.isBackendReady) {
      await appStore.initialize()
    }

    addLog("success", "应用初始化完成")
  } catch (error) {
    addLog("error", `应用初始化失败: ${(error as Error).message}`)
    appStore.showError("初始化失败", (error as Error).message)
  }
}

// 监听路由变化，自动更新菜单选中状态
watch(
  () => route.path,
  () => {
    updateSelectedKeys()
  },
  { immediate: true }
)

// 生命周期
onMounted(async () => {
  // 恢复侧边栏状态
  const savedCollapsedState = localStorage.getItem("sidebarCollapsed")
  if (savedCollapsedState !== null) {
    isCollapsed.value = savedCollapsedState === "true"
  }

  // 应用初始主题
  applyTheme()

  // 初始化菜单选中状态
  updateSelectedKeys()

  // 初始化应用
  await initializeApp()
})

// 暴露给子组件
defineExpose({
  handleTaskSelected,
  startTasks,
  stopTasks,
  clearQueue,
  addLog,
})
</script>

<style scoped>
/* 亮色主题 */
.main-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
  transition: all 0.3s ease;
}

.header {
  background: white;
  border-bottom: 1px solid #e8e8e8;
  padding: 0 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
}

.title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1890ff;
  transition: color 0.3s ease;
}

.version {
  font-size: 12px;
  color: #666;
  background: #f0f0f0;
  padding: 2px 8px;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.theme-toggle {
  color: #666;
  transition: all 0.3s ease;
}

.theme-toggle:hover {
  color: #1890ff;
  background-color: #f5f5f5;
}

.main-content {
  flex: 1;
  padding: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.content-wrapper {
  display: flex;
  gap: 16px;
  height: 100%;
  flex: 1;
}

/* 侧边栏样式 */
.sidebar {
  width: 200px;
  flex-shrink: 0;
  background: white;
  border-right: 1px solid #e8e8e8;
  border-radius: 8px;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.sidebar.collapsed {
  width: 80px;
}

.sidebar-toggle {
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: center;
  flex-shrink: 0;
}

.toggle-btn {
  width: 100%;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  transition: all 0.3s ease;
}

.toggle-btn:hover {
  color: #1890ff;
  background-color: #f5f5f5;
}

.sidebar-menu {
  height: calc(100% - 72px);
  border-right: none;
  background: transparent;
  flex: 1;
}

.sidebar-menu :deep(.ant-menu-item) {
  height: 50px;
  line-height: 50px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.sidebar-menu :deep(.ant-menu-item:hover) {
  background-color: #f5f5f5;
  color: #1890ff;
}

.sidebar-menu :deep(.ant-menu-item-selected) {
  background-color: #e6f7ff;
  color: #1890ff;
}

.sidebar-menu :deep(.ant-menu-item-selected::after) {
  display: none;
}

.sidebar-menu :deep(.anticon) {
  font-size: 16px;
  margin-right: 12px;
  transition: all 0.3s ease;
}

.main-panel {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  transition: all 0.3s ease;
}

/* 暗黑主题 */
.main-layout.dark {
  background: #141414;
}

.main-layout.dark .header {
  background: #1f1f1f;
  border-bottom-color: #303030;
}

.main-layout.dark .title h1 {
  color: #1890ff;
}

.main-layout.dark .version {
  color: #a6a6a6;
  background: #262626;
}

.main-layout.dark .theme-toggle {
  color: #a6a6a6;
}

.main-layout.dark .theme-toggle:hover {
  color: #1890ff;
  background-color: #262626;
}

.main-layout.dark .sidebar {
  background: #1f1f1f;
  border-right-color: #303030;
}

.main-layout.dark .sidebar-toggle {
  border-bottom-color: #303030;
}

.main-layout.dark .toggle-btn {
  color: #a6a6a6;
}

.main-layout.dark .toggle-btn:hover {
  color: #1890ff;
  background-color: #262626;
}

.main-layout.dark .sidebar-menu :deep(.ant-menu-item) {
  color: #a6a6a6;
}

.main-layout.dark .sidebar-menu :deep(.ant-menu-item:hover) {
  background-color: #262626;
  color: #1890ff;
}

.main-layout.dark .sidebar-menu :deep(.ant-menu-item-selected) {
  background-color: #111b26;
  color: #1890ff;
}

.main-layout.dark .main-panel {
  background: #1f1f1f;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .sidebar {
    width: 180px;
  }

  .sidebar.collapsed {
    width: 80px;
  }
}

@media (max-width: 768px) {
  .content-wrapper {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    height: auto;
  }

  .sidebar.collapsed {
    width: 100%;
    height: auto;
  }

  .sidebar-menu {
    height: auto;
  }

  .sidebar-menu :deep(.ant-menu-item) {
    height: 50px;
  }
}

/* 动画效果 */
.sidebar-menu :deep(.ant-menu-item) {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
