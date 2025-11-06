import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/utils/api'
import type { QueueItem, TaskHistory, ApiResponse } from '@/types'

// 任务进度状态
interface TaskProgress {
  current: number
  total: number
  status: string
  isRunning: boolean
}

// 任务队列项（扩展类型）
interface ExtendedQueueItem extends QueueItem {
  run_count?: number
  params?: Record<string, any>
}

export const useTaskStore = defineStore('task', () => {
  // 状态
  const taskQueue = ref<ExtendedQueueItem[]>([])
  const isRunning = ref<boolean>(false)
  const currentProgress = ref<TaskProgress>({
    current: 0,
    total: 0,
    status: '',
    isRunning: false
  })
  const taskHistory = ref<TaskHistory[]>([])
  const progressPollingInterval = ref<NodeJS.Timeout | null>(null)
  const error = ref<string | null>(null)

  // 计算属性
  const totalTasks = computed<number>(() => {
    return taskQueue.value.reduce((sum, task) => sum + (task.run_count || 1), 0)
  })

  const completedTasks = computed<number>(() => {
    return currentProgress.value.current
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

  // 方法
  const addTask = (task: Omit<ExtendedQueueItem, 'id' | 'addedAt'>): void => {
    const taskWithId: ExtendedQueueItem = {
      ...task,
      id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      addedAt: new Date().toISOString(),
      status: 'pending',
      progress: 0
    }
    taskQueue.value.push(taskWithId)
    console.log('添加任务:', taskWithId)
  }

  const removeTask = (taskId: string): void => {
    const index = taskQueue.value.findIndex(task => task.id === taskId)
    if (index !== -1) {
      const removedTask = taskQueue.value.splice(index, 1)[0]
      console.log('移除任务:', removedTask)
    }
  }

  const updateTask = (taskId: string, updates: Partial<ExtendedQueueItem>): void => {
    const task = taskQueue.value.find(task => task.id === taskId)
    if (task) {
      Object.assign(task, updates)
      console.log('更新任务:', task)
    }
  }

  const moveTaskUp = (taskId: string): void => {
    const index = taskQueue.value.findIndex(task => task.id === taskId)
    if (index > 0) {
      [taskQueue.value[index - 1], taskQueue.value[index]] =
      [taskQueue.value[index], taskQueue.value[index - 1]]
    }
  }

  const moveTaskDown = (taskId: string): void => {
    const index = taskQueue.value.findIndex(task => task.id === taskId)
    if (index < taskQueue.value.length - 1) {
      [taskQueue.value[index], taskQueue.value[index + 1]] =
      [taskQueue.value[index + 1], taskQueue.value[index]]
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
      currentProgress.value = {
        current: 0,
        total: totalTasks.value,
        status: '准备执行...',
        isRunning: true
      }

      console.log('开始执行任务队列:', taskQueue.value)

      // 转换任务格式并发送到后端
      const apiTasks = taskQueue.value.map(task => ({
        name: task.name,
        type: task.type,
        params: task.params || {},
        priority: task.priority,
        run_count: task.run_count || 1
      }))

      const response = await api.post('/api/tasks/execute', { tasks: apiTasks })

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

      isRunning.value = false
      currentProgress.value.isRunning = false
      currentProgress.value.status = '已停止'

      // 停止进度轮询
      stopProgressPolling()

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '停止任务失败'
      console.error('停止任务执行失败:', err)
      error.value = errorMessage
    }
  }

  const pauseExecution = async (): Promise<void> => {
    try {
      if (!isRunning.value) return

      console.log('暂停任务执行')

      await api.post('/api/tasks/pause')

      currentProgress.value.status = '已暂停'
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '暂停任务失败'
      console.error('暂停任务执行失败:', err)
      error.value = errorMessage
    }
  }

  const resumeExecution = async (): Promise<void> => {
    try {
      if (!isRunning.value) return

      console.log('恢复任务执行')

      await api.post('/api/tasks/resume')

      currentProgress.value.status = '执行中'
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '恢复任务失败'
      console.error('恢复任务执行失败:', err)
      error.value = errorMessage
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
          if (progress.status === 'completed' || progress.status === 'failed') {
            isRunning.value = false
            currentProgress.value.isRunning = false
            stopProgressPolling()

            // 获取任务历史
            await fetchTaskHistory()
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

  const fetchTaskHistory = async (): Promise<void> => {
    try {
      const response = await api.get<ApiResponse<TaskHistory[]>>('/api/tasks/history')

      if (response.data?.success && response.data.data) {
        taskHistory.value = response.data.data
      }
    } catch (err) {
      console.error('获取任务历史失败:', err)
    }
  }

  const clearHistory = async (): Promise<void> => {
    try {
      await api.delete('/api/tasks/history')
      taskHistory.value = []
      console.log('任务历史已清空')
    } catch (err) {
      console.error('清空任务历史失败:', err)
    }
  }

  const retryTask = async (taskId: string): Promise<void> => {
    try {
      await api.post(`/api/tasks/${taskId}/retry`)
      console.log('任务重试:', taskId)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '重试任务失败'
      console.error('重试任务失败:', err)
      error.value = errorMessage
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
      status: '',
      isRunning: false
    }
    error.value = null
  }

  return {
    // 状态
    taskQueue,
    isRunning,
    currentProgress,
    taskHistory,
    error,

    // 计算属性
    totalTasks,
    completedTasks,
    progressPercentage,
    canStart,
    canStop,
    canClear,

    // 方法
    addTask,
    removeTask,
    updateTask,
    moveTaskUp,
    moveTaskDown,
    clearQueue,
    startExecution,
    stopExecution,
    pauseExecution,
    resumeExecution,
    fetchTaskHistory,
    clearHistory,
    retryTask,
    clearError,
    reset
  }
})