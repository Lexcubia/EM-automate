"""
简化任务管理器 - 基于a.md的8步流程
直接、简单、无复杂转换的任务状态管理
"""
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/utils/api'

// 简化的任务项 - 对应后端Task结构
interface SimpleTask {
  id: string
  name: string
  category: string  // 对应TaskCategory
  level: string
  macro_id: string
  run_count: number
  params: Record<string, any>
}

// 任务进度状态
interface SimpleProgress {
  current: number
  total: number
  status: string
  isRunning: boolean
}

export const useSimpleTaskStore = defineStore('simpleTask', () => {
  // 状态
  const taskQueue = ref<SimpleTask[]>([])
  const isRunning = ref<boolean>(false)
  const currentProgress = ref<SimpleProgress>({
    current: 0,
    total: 0,
    status: '空闲',
    isRunning: false
  })
  const error = ref<string | null>(null)
  const progressPollingInterval = ref<NodeJS.Timeout | null>(null)

  // 计算属性
  const totalRuns = computed<number>(() => {
    return taskQueue.value.reduce((sum, task) => sum + task.run_count, 0)
  })

  const progressPercentage = computed<number>(() => {
    if (currentProgress.value.total === 0) return 0
    return Math.round((currentProgress.value.current / currentProgress.value.total) * 100)
  })

  const canStart = computed<boolean>(() => {
    return taskQueue.value.length > 0 && !isRunning.value
  })

  const canStop = computed<boolean>(() => {
    return isRunning.value
  })

  const canClear = computed<boolean>(() => {
    return taskQueue.value.length > 0 && !isRunning.value
  })

  // 任务分类到中文的映射
  const categoryMap = {
    'commission': '委托',
    'night_sailing_manual': '夜航手册',
    'commission_letter': '委托密函'
  }

  // 方法
  const addTask = (task: Omit<SimpleTask, 'id'>): void => {
    const taskWithId: SimpleTask = {
      ...task,
      id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      params: task.params || {}
    }
    taskQueue.value.push(taskWithId)
    console.log('添加简化任务:', taskWithId)
  }

  const removeTask = (taskId: string): void => {
    const index = taskQueue.value.findIndex(task => task.id === taskId)
    if (index !== -1) {
      const removedTask = taskQueue.value.splice(index, 1)[0]
      console.log('移除任务:', removedTask)
    }
  }

  const updateTask = (taskId: string, updates: Partial<SimpleTask>): void => {
    const task = taskQueue.value.find(task => task.id === taskId)
    if (task) {
      Object.assign(task, updates)
      console.log('更新任务:', task)
    }
  }

  const clearQueue = (): void => {
    if (!isRunning.value) {
      const clearedCount = taskQueue.value.length
      taskQueue.value = []
      console.log(`清空队列，移除了${clearedCount}个任务`)
    }
  }

  const startExecution = async (): Promise<void> => {
    try {
      if (taskQueue.value.length === 0) {
        throw new Error('任务队列为空')
      }

      error.value = null
      isRunning.value = true

      // 重置进度
      currentProgress.value = {
        current: 0,
        total: totalRuns.value,
        status: '准备执行...',
        isRunning: true
      }

      console.log('开始执行简化任务队列:', taskQueue.value)

      // 直接发送任务数据到后端，不做任何转换
      const response = await api.post('/api/tasks/execute', {
        tasks: taskQueue.value
      })

      if (!response.data?.success) {
        throw new Error(response.data?.message || '启动任务失败')
      }

      // 开始轮询进度
      startProgressPolling()

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '启动任务失败'
      console.error('启动任务执行失败:', err)
      error.value = errorMessage
      isRunning.value = false
      currentProgress.value.isRunning = false
      throw new Error(errorMessage)
    }
  }

  const stopExecution = async (): Promise<void> => {
    try {
      if (!isRunning.value) return

      console.log('停止任务执行')

      await api.post('/api/tasks/stop')

      // 重置状态
      isRunning.value = false
      currentProgress.value = {
        current: 0,
        total: 0,
        status: '已停止',
        isRunning: false
      }
      error.value = null

      // 停止进度轮询
      stopProgressPolling()

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '停止任务失败'
      console.error('停止任务执行失败:', err)
      error.value = errorMessage

      // 即使停止失败也要重置前端状态
      isRunning.value = false
      currentProgress.value = {
        current: 0,
        total: 0,
        status: '已停止',
        isRunning: false
      }
    }
  }

  const startProgressPolling = (): void => {
    stopProgressPolling() // 确保没有重复的轮询

    progressPollingInterval.value = setInterval(async () => {
      try {
        const response = await api.get('/api/tasks/progress')

        if (response.data?.success && response.data.data) {
          const progress = response.data.data
          currentProgress.value = {
            ...currentProgress.value,
            ...progress
          }

          // 如果任务完成，停止轮询
          if (progress.status === '执行完成' ||
              progress.status === '执行失败' ||
              !progress.isRunning) {
            isRunning.value = false
            currentProgress.value.isRunning = false
            stopProgressPolling()
            console.log('任务执行完成:', progress.status)
          }
        }
      } catch (err) {
        console.error('获取进度失败:', err)
      }
    }, 1000) // 每秒轮询一次
  }

  const stopProgressPolling = (): void => {
    if (progressPollingInterval.value) {
      clearInterval(progressPollingInterval.value)
      progressPollingInterval.value = null
    }
  }

  const clearError = (): void => {
    error.value = null
  }

  // 重置状态
  const reset = (): void => {
    stopProgressPolling()
    taskQueue.value = []
    isRunning.value = false
    currentProgress.value = {
      current: 0,
      total: 0,
      status: '空闲',
      isRunning: false
    }
    error.value = null
  }

  // 从现有任务格式转换为简化格式
  const convertFromLegacyTask = (legacyTask: any): SimpleTask => {
    // 确定任务分类
    let category = 'commission' // 默认
    if (legacyTask.sub_category) {
      if (legacyTask.sub_category.includes('commission')) {
        category = 'commission'
      } else if (legacyTask.sub_category.includes('night_sailing')) {
        category = 'night_sailing_manual'
      } else if (legacyTask.sub_category.includes('commission_letter')) {
        category = 'commission_letter'
      }
    }

    return {
      id: legacyTask.id || '',
      name: legacyTask.name || legacyTask.mission_key || '',
      category: category,
      level: legacyTask.selected_level || '',
      macro_id: legacyTask.params?.macro_id || '',
      run_count: legacyTask.run_count || 1,
      params: legacyTask.params || {}
    }
  }

  return {
    // 状态
    taskQueue,
    isRunning,
    currentProgress,
    error,

    // 计算属性
    totalRuns,
    progressPercentage,
    canStart,
    canStop,
    canClear,

    // 工具
    categoryMap,

    // 方法
    addTask,
    removeTask,
    updateTask,
    clearQueue,
    startExecution,
    stopExecution,
    clearError,
    reset,
    convertFromLegacyTask
  }
})