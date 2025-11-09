import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Antd from 'ant-design-vue'
import App from './App.vue'
import router from './router'
import { useMenuStore } from './stores/menu'
import 'ant-design-vue/dist/reset.css'

// 开发环境调试工具
if (import.meta.env.DEV) {
  // 创建全局调试对象
  window.debugAPI = {
    log: (...args: any[]) => {
      console.log('[API Debug]', ...args)
    },
    error: (...args: any[]) => {
      console.error('[API Debug]', ...args)
    }
  }
}

// 创建应用实例
const app = createApp(App)

// 使用插件
app.use(createPinia())
app.use(router)
app.use(Antd)

// 全局错误处理
app.config.errorHandler = (err: unknown, _instance: any, info: string): void => {
  console.error('Vue 全局错误:', err, info)

  // 在开发环境显示详细错误信息
  if (import.meta.env.DEV) {
    console.groupCollapsed('错误详情')
    console.error('错误对象:', err)
    console.error('错误信息:', info)
    console.groupEnd()
  }
}

// 全局警告处理
app.config.warnHandler = (msg: string, _instance: any, trace: string): void => {
  if (import.meta.env.DEV) {
    console.warn('Vue 警告:', msg, trace)
  }
}

// 初始化菜单配置（异步加载）
const initializeApp = async () => {
  try {
    // 预加载菜单配置
    const menuStore = useMenuStore()
    await menuStore.loadMenuConfig()
    console.log('菜单配置初始化完成')
  } catch (error) {
    console.warn('菜单配置初始化失败，将使用默认配置:', error)
  }

  // 挂载应用
  app.mount('#app')

  // 导出应用实例供调试使用
  if (import.meta.env.DEV) {
    ;(window as any).__VUE_APP__ = app
  }
}

// 启动应用
initializeApp()