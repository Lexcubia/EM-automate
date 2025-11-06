<template>
  <div class="main-container" :class="{ 'dark': isDarkMode }">
    <!-- 顶部标题栏 -->
    <div class="header">
      <div class="header-content">
        <div class="title">
          <h1>{{ appName }}</h1>
          <span class="version">v{{ appStore.appVersion }}</span>
        </div>
        <div class="header-actions">
          <!-- 暗黑模式切换按钮 -->
          <a-button
            type="text"
            @click="toggleDarkMode"
            class="theme-toggle"
            :title="isDarkMode ? '切换到亮色模式' : '切换到暗黑模式'"
          >
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
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <div class="content-wrapper">
        <!-- 左侧：可收缩的侧边菜单 -->
        <div class="sidebar" :class="{ 'collapsed': isCollapsed }">
          <!-- 收缩/展开按钮 -->
          <div class="sidebar-toggle">
            <a-button
              type="text"
              @click="toggleSidebar"
              class="toggle-btn"
              :title="isCollapsed ? '展开菜单' : '收缩菜单'"
            >
              <template #icon>
                <MenuUnfoldOutlined v-if="isCollapsed" />
                <MenuFoldOutlined v-else />
              </template>
            </a-button>
          </div>

          <!-- 菜单内容 -->
          <a-menu
            v-model:selectedKeys="selectedKeys"
            mode="inline"
            @click="handleMenuClick"
            class="sidebar-menu"
            :inline-collapsed="isCollapsed"
          >
            <a-menu-item key="training">
              <template #icon>
                <RocketOutlined />
              </template>
              <span>历练</span>
            </a-menu-item>
            <a-menu-item key="keyboard">
              <template #icon>
                <ControlOutlined />
              </template>
              <span>键盘映射</span>
            </a-menu-item>
            <a-menu-item key="macro">
              <template #icon>
                <FileTextOutlined />
              </template>
              <span>自定义宏</span>
            </a-menu-item>
            <a-menu-item key="fishing">
              <template #icon>
                <ExperimentOutlined />
              </template>
              <span>钓鱼</span>
            </a-menu-item>
            <a-menu-item key="about">
              <template #icon>
                <InfoCircleOutlined />
              </template>
              <span>关于</span>
            </a-menu-item>
          </a-menu>
        </div>

        <!-- 右侧：主内容区域 -->
        <div class="main-panel">
          <!-- 根据选中的菜单显示不同内容 -->
          <component :is="currentComponent" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
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
} from '@ant-design/icons-vue'
import { useAppStore } from '@/stores/app'
import { useTaskStore } from '@/stores/task'

// 组件导入
import TrainingPanel from '@/components/TrainingPanel.vue'
import KeyboardPanel from '@/components/KeyboardPanel.vue'
import MacroPanel from '@/components/MacroPanel.vue'
import FishingPanel from '@/components/FishingPanel.vue'
import AboutPanel from '@/components/AboutPanel.vue'

// Store
const appStore = useAppStore()
const taskStore = useTaskStore()

// 响应式数据
const selectedKeys = ref(['training'])
const logs = ref([])
const logContainer = ref(null)
const isCollapsed = ref(false)
const isDarkMode = ref(localStorage.getItem('darkMode') === 'true')
const appName = ref('EM-Automate')

// 组件映射
const componentMap = {
  training: TrainingPanel,
  keyboard: KeyboardPanel,
  macro: MacroPanel,
  fishing: FishingPanel,
  about: AboutPanel
}

// 计算属性：当前选中的组件
const currentComponent = computed(() => {
  const currentKey = selectedKeys.value[0] || 'training'
  return componentMap[currentKey]
})

// 菜单点击处理
const handleMenuClick = ({ key }) => {
  selectedKeys.value = [key]
  addLog('info', `切换到: ${getMenuName(key)}`)
}

// 侧边栏收缩/展开
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
  localStorage.setItem('sidebarCollapsed', isCollapsed.value)
}

// 暗黑模式切换
const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value
  localStorage.setItem('darkMode', isDarkMode.value)
  applyTheme()
}

// 应用主题
const applyTheme = () => {
  if (isDarkMode.value) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

const getMenuName = (key) => {
  const menuNames = {
    training: '历练',
    keyboard: '键盘映射',
    macro: '自定义宏',
    fishing: '钓鱼',
    about: '关于'
  }
  return menuNames[key] || key
}

// 日志相关方法
const addLog = (type, message) => {
  const logEntry = {
    type,
    message,
    time: new Date().toLocaleTimeString()
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

const clearLogs = () => {
  logs.value = []
}

// 生命周期
onMounted(async () => {
  // 恢复侧边栏状态
  const savedCollapsedState = localStorage.getItem('sidebarCollapsed')
  if (savedCollapsedState !== null) {
    isCollapsed.value = savedCollapsedState === 'true'
  }

  // 应用初始主题
  applyTheme()

  await initializeApp()
})

const initializeApp = async () => {
  try {
    addLog('info', '正在初始化应用...')

    if (!appStore.isBackendReady) {
      await appStore.initialize()
    }

    addLog('success', '应用初始化完成')
  } catch (error) {
    addLog('error', `应用初始化失败: ${error.message}`)
    appStore.showError('初始化失败', error.message)
  }
}

// 暴露给历练组件的方法
const handleTaskSelected = (task) => {
  taskStore.addTask(task)
  addLog('info', `添加任务: ${task.display_name} x${task.run_count}`)
}

const startTasks = async () => {
  try {
    addLog('info', '开始执行任务队列...')
    const result = await taskStore.startExecution()
    addLog('success', `任务执行已启动，共${result.total_tasks}次任务`)
  } catch (error) {
    addLog('error', `启动任务失败: ${error.message}`)
    appStore.showError('启动失败', error.message)
  }
}

const stopTasks = async () => {
  try {
    addLog('warning', '正在停止任务执行...')
    const result = await taskStore.stopExecution()
    addLog('warning', '任务执行已停止')
  } catch (error) {
    addLog('error', `停止任务失败: ${error.message}`)
    appStore.showError('停止失败', error.message)
  }
}

const clearQueue = () => {
  taskStore.clearQueue()
  addLog('info', '已清空任务队列')
}

// 暴露给子组件
defineExpose({
  handleTaskSelected,
  startTasks,
  stopTasks,
  clearQueue,
  addLog
})
</script>

<style scoped>
/* 亮色主题 */
.main-container {
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
}

.content-wrapper {
  display: flex;
  gap: 16px;
  height: 100%;
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
}

.sidebar.collapsed {
  width: 80px;
}

.sidebar-toggle {
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: center;
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
}

.sidebar-menu :deep(.ant-menu-item) {
  height: 50px;
  line-height: 50px;
  margin: 4px 8px;
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
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  transition: all 0.3s ease;
}

/* 暗黑主题 */
.main-container.dark {
  background: #141414;
}

.main-container.dark .header {
  background: #1f1f1f;
  border-bottom-color: #303030;
}

.main-container.dark .title h1 {
  color: #1890ff;
}

.main-container.dark .version {
  color: #a6a6a6;
  background: #262626;
}

.main-container.dark .theme-toggle {
  color: #a6a6a6;
}

.main-container.dark .theme-toggle:hover {
  color: #1890ff;
  background-color: #262626;
}

.main-container.dark .sidebar {
  background: #1f1f1f;
  border-right-color: #303030;
}

.main-container.dark .sidebar-toggle {
  border-bottom-color: #303030;
}

.main-container.dark .toggle-btn {
  color: #a6a6a6;
}

.main-container.dark .toggle-btn:hover {
  color: #1890ff;
  background-color: #262626;
}

.main-container.dark .sidebar-menu :deep(.ant-menu-item) {
  color: #a6a6a6;
}

.main-container.dark .sidebar-menu :deep(.ant-menu-item:hover) {
  background-color: #262626;
  color: #1890ff;
}

.main-container.dark .sidebar-menu :deep(.ant-menu-item-selected) {
  background-color: #111b26;
  color: #1890ff;
}

.main-container.dark .main-panel {
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