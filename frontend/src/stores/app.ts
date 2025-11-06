import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/utils/api'
import type { BackendConfig, SystemInfo, ApiResponse } from '@/types'

// 扩展 Window 接口
declare global {
  interface Window {
    electronAPI?: {
      getBackendConfig(): Promise<BackendConfig>
      getAppVersion(): Promise<string>
      showErrorBox(title: string, content: string): void
    }
  }
}

export const useAppStore = defineStore('app', () => {
  // 状态
  const loading = ref<boolean>(false)
  const backendConfig = ref<BackendConfig | null>(null)
  const appVersion = ref<string>('1.0.0')
  const systemInfo = ref<SystemInfo | null>(null)
  const error = ref<string | null>(null)

  // 计算属性
  const isBackendReady = computed<boolean>(() => backendConfig.value !== null)
  const isElectron = computed<boolean>(() => {
    return typeof window !== 'undefined' && window.electronAPI
  })

  // 方法
  const initialize = async (): Promise<void> => {
    try {
      loading.value = true
      error.value = null

      // 如果是Electron环境，获取后端配置
      if (isElectron.value && window.electronAPI) {
        try {
          backendConfig.value = await window.electronAPI.getBackendConfig()
          appVersion.value = await window.electronAPI.getAppVersion()
        } catch (electronError) {
          console.warn('Electron API 调用失败，使用默认配置:', electronError)
          setDefaultBackendConfig()
        }
      } else {
        // 浏览器环境的默认配置
        setDefaultBackendConfig()
      }

      // 测试后端连接
      await testBackendConnection()

      // 获取系统信息
      await fetchSystemInfo()

      console.log('应用初始化完成')
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '未知错误'
      console.error('应用初始化失败:', err)
      error.value = errorMessage
      throw new Error(`应用初始化失败: ${errorMessage}`)
    } finally {
      loading.value = false
    }
  }

  const setDefaultBackendConfig = (): void => {
    backendConfig.value = {
      host: '127.0.0.1',
      port: 8000,
      timeout: 10000,
      retries: 3
    }
  }

  const testBackendConnection = async (): Promise<void> => {
    try {
      const response = await api.get<ApiResponse>('/')
      if (!response.data?.success) {
        throw new Error('后端服务响应异常')
      }
      console.log('后端连接成功')
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '网络连接失败'
      console.error('后端连接失败:', err)
      throw new Error(`无法连接到后端服务器: ${errorMessage}`)
    }
  }

  const fetchSystemInfo = async (): Promise<void> => {
    try {
      const response = await api.get<ApiResponse<SystemInfo>>('/api/system/info')
      if (response.data?.success && response.data.data) {
        systemInfo.value = response.data.data
      } else {
        throw new Error('系统信息格式错误')
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '获取系统信息失败'
      console.warn('获取系统信息失败:', err)
      // 不抛出错误，允许应用继续运行
    }
  }

  const updateBackendConfig = (config: Partial<BackendConfig>): void => {
    if (backendConfig.value) {
      backendConfig.value = { ...backendConfig.value, ...config }
    }
  }

  const clearError = (): void => {
    error.value = null
  }

  const showError = (title: string, content: string): void => {
    if (isElectron.value && window.electronAPI) {
      window.electronAPI.showErrorBox(title, content)
    } else {
      // 在浏览器环境使用 Ant Design 的 message 组件
      console.error(`${title}: ${content}`)
      // 这里可以集成 UI 框架的消息组件
      if (typeof window !== 'undefined' && (window as any).message) {
        ;(window as any).message.error(`${title}: ${content}`)
      }
    }
  }

  const showSuccess = (title: string, content: string): void => {
    if (isElectron.value && window.electronAPI) {
      // Electron 暂没有成功消息框，可以使用通知
      console.log(`${title}: ${content}`)
    } else {
      console.log(`${title}: ${content}`)
      // 这里可以集成 UI 框架的消息组件
      if (typeof window !== 'undefined' && (window as any).message) {
        ;(window as any).message.success(`${title}: ${content}`)
      }
    }
  }

  const refreshSystemInfo = async (): Promise<void> => {
    await fetchSystemInfo()
  }

  // 重置应用状态
  const reset = (): void => {
    loading.value = false
    backendConfig.value = null
    appVersion.value = '1.0.0'
    systemInfo.value = null
    error.value = null
  }

  return {
    // 状态
    loading,
    backendConfig,
    appVersion,
    systemInfo,
    error,

    // 计算属性
    isBackendReady,
    isElectron,

    // 方法
    initialize,
    testBackendConnection,
    fetchSystemInfo,
    updateBackendConfig,
    clearError,
    showError,
    showSuccess,
    refreshSystemInfo,
    reset
  }
})