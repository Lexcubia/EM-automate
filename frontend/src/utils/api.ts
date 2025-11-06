import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { useAppStore } from '@/stores/app'
import type { ApiResponse } from '@/types'

// 扩展 Axios 配置类型
interface ExtendedAxiosRequestConfig extends AxiosRequestConfig {
  metadata?: {
    startTime: Date
  }
}

// 扩展 Window 接口
declare global {
  interface Window {
    debugAPI?: {
      log: (...args: any[]) => void
      error: (...args: any[]) => void
    }
  }
}

// 创建axios实例
const api: AxiosInstance = axios.create({
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config: ExtendedAxiosRequestConfig): ExtendedAxiosRequestConfig => {
    const appStore = useAppStore()

    // 设置基础URL
    if (appStore.backendConfig) {
      config.baseURL = `http://${appStore.backendConfig.host}:${appStore.backendConfig.port}`
    }

    // 添加请求时间戳
    config.metadata = { startTime: new Date() }

    // 开发模式下打印请求信息
    if (import.meta.env.DEV && window.debugAPI) {
      window.debugAPI.log('API Request:', config.method?.toUpperCase(), config.url, config.data)
    }

    return config
  },
  (error: AxiosError): Promise<AxiosError> => {
    console.error('请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse): AxiosResponse => {
    // 计算请求耗时
    const endTime = new Date()
    const duration = endTime - (response.config as ExtendedAxiosRequestConfig).metadata!.startTime

    // 开发模式下打印响应信息
    if (import.meta.env.DEV && window.debugAPI) {
      window.debugAPI.log('API Response:', response.config.method?.toUpperCase(), response.config.url, `(${duration}ms)`, response.data)
    }

    return response
  },
  (error: AxiosError): Promise<AxiosError> => {
    // 开发模式下打印错误信息
    if (import.meta.env.DEV && window.debugAPI) {
      window.debugAPI.error('API Error:', error.config?.method?.toUpperCase(), error.config?.url, error.response?.data || error.message)
    }

    // 处理不同类型的错误
    if (error.code === 'ECONNABORTED') {
      error.message = '请求超时，请检查网络连接'
    } else if (error.code === 'ERR_NETWORK') {
      error.message = '网络连接失败，请检查后端服务是否运行'
    } else if (error.response) {
      // 服务器返回了错误状态码
      const status = error.response.status
      const data = error.response.data as any

      switch (status) {
        case 400:
          error.message = data?.detail || '请求参数错误'
          break
        case 401:
          error.message = '未授权访问'
          break
        case 403:
          error.message = '禁止访问'
          break
        case 404:
          error.message = '请求的资源不存在'
          break
        case 500:
          error.message = data?.detail || '服务器内部错误'
          break
        default:
          error.message = data?.detail || `请求失败 (${status})`
      }
    } else if (error.request) {
      error.message = '服务器无响应'
    }

    return Promise.reject(error)
  }
)

// 导出工具函数
export const apiUtils = {
  // 检查连接状态
  async checkConnection(): Promise<boolean> {
    try {
      await api.get('/')
      return true
    } catch (error) {
      return false
    }
  },

  // 重试请求
  async retry<T>(
    requestFn: () => Promise<T>,
    maxRetries: number = 3,
    delay: number = 1000
  ): Promise<T> {
    let lastError: any

    for (let i = 0; i < maxRetries; i++) {
      try {
        return await requestFn()
      } catch (error) {
        lastError = error
        if (i < maxRetries - 1) {
          await new Promise(resolve => setTimeout(resolve, delay))
        }
      }
    }

    throw lastError
  },

  // 通用 GET 请求
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await api.get<ApiResponse<T>>(url, config)
    return response.data
  },

  // 通用 POST 请求
  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await api.post<ApiResponse<T>>(url, data, config)
    return response.data
  },

  // 通用 PUT 请求
  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await api.put<ApiResponse<T>>(url, data, config)
    return response.data
  },

  // 通用 DELETE 请求
  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await api.delete<ApiResponse<T>>(url, config)
    return response.data
  }
}

export { api }
export type { ExtendedAxiosRequestConfig }