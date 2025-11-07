<template>
  <div class="training-panel">
    <div class="content-wrapper">
      <!-- 左侧：任务选择区域 -->
      <div class="left-panel">
        <a-card title="任务选择" class="task-selection-card">
          <a-tabs v-model:activeKey="activeTab" type="card" size="small">
            <!-- 委托标签页 -->
            <a-tab-pane key="commission" tab="委托">
              <CommissionPanel @task-selected="handleTaskSelected" />
            </a-tab-pane>

            <!-- 夜航手册标签页 -->
            <a-tab-pane key="night_sailing_manual" tab="夜航手册">
              <NightSailingPanel @task-selected="handleTaskSelected" />
            </a-tab-pane>

            <!-- 委托密函标签页 -->
            <a-tab-pane key="commission_letter" tab="委托密函">
              <CommissionLetterPanel @task-selected="handleTaskSelected" />
            </a-tab-pane>
          </a-tabs>
        </a-card>
      </div>

      <!-- 右侧：任务队列和日志区域 -->
      <div class="right-panel">
        <!-- 任务队列 -->
        <a-card title="任务队列" class="task-queue-card">
          <template #extra>
            <a-space>
              <a-button
                size="small"
                @click="clearQueue"
                :disabled="taskStore.canStop"
              >
                清空队列
              </a-button>
            </a-space>
          </template>

          <TaskQueue
            :tasks="taskStore.taskQueue"
            :is-running="taskStore.isRunning"
            @remove-task="taskStore.removeTask"
            @move-up="taskStore.moveTaskUp"
            @move-down="taskStore.moveTaskDown"
            @update-task="taskStore.updateTask"
          />

          <!-- 控制按钮 -->
          <div class="control-buttons">
            <a-space>
              <a-button
                type="primary"
                size="large"
                :loading="taskStore.isRunning"
                :disabled="!taskStore.canStart"
                @click="startTasks"
              >
                <template #icon>
                  <PlayCircleOutlined />
                </template>
                开始执行
              </a-button>
              <a-button
                danger
                size="large"
                :disabled="!taskStore.canStop"
                @click="stopTasks"
              >
                <template #icon>
                  <StopOutlined />
                </template>
                停止执行
              </a-button>
            </a-space>
          </div>

          <!-- 进度显示 -->
          <div v-if="taskStore.isRunning || taskStore.currentProgress.total > 0" class="progress-section">
            <a-progress
              :percent="taskStore.progressPercentage"
              :status="taskStore.isRunning ? 'active' : 'success'"
              :stroke-color="taskStore.isRunning ? '#1890ff' : '#52c41a'"
            />
            <div class="progress-text">
              <span>{{ taskStore.currentProgress.current }} / {{ taskStore.currentProgress.total }}</span>
              <span v-if="taskStore.currentProgress.status" class="status-text">
                - {{ taskStore.currentProgress.status }}
              </span>
            </div>
          </div>
        </a-card>

        <!-- 日志显示区域 -->
        <a-card title="执行日志" class="log-card">
          <template #extra>
            <a-button size="small" @click="clearLogs">清空日志</a-button>
          </template>
          <div class="log-container" ref="logContainer">
            <div
              v-for="(log, index) in logs"
              :key="index"
              :class="['log-entry', `log-${log.type}`]"
            >
              <span class="log-time">{{ log.time }}</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
            <div v-if="logs.length === 0" class="log-empty">暂无日志</div>
          </div>
        </a-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import {
  PlayCircleOutlined,
  StopOutlined
} from '@ant-design/icons-vue'
import { useTaskStore } from '@/stores/task'
import CommissionPanel from './CommissionPanel.vue'
import NightSailingPanel from './NightSailingPanel.vue'
import CommissionLetterPanel from './CommissionLetterPanel.vue'
import TaskQueue from './TaskQueue.vue'

// Store
const taskStore = useTaskStore()

// 响应式数据
const activeTab = ref('commission')
const logs = ref([])
const logContainer = ref(null)

// 方法
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
  }
}

const stopTasks = async () => {
  try {
    addLog('warning', '正在停止任务执行...')
    const result = await taskStore.stopExecution()
    addLog('warning', '任务执行已停止')
  } catch (error) {
    addLog('error', `停止任务失败: ${error.message}`)
  }
}

const clearQueue = () => {
  taskStore.clearQueue()
  addLog('info', '已清空任务队列')
}

const clearLogs = () => {
  logs.value = []
}

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

// 生命周期
onMounted(() => {
  startLogMonitoring()
})

onUnmounted(() => {
  taskStore.cleanup()
})

const startLogMonitoring = () => {
  // 监听任务状态变化，添加相应日志
  const unwatchIsRunning = taskStore.$subscribe((mutation, state) => {
    if (mutation.events?.key === 'isRunning') {
      if (state.isRunning) {
        addLog('info', '任务执行中...')
      } else {
        addLog('info', '任务执行已结束')
      }
    }
  })

  // 监听进度变化
  const unwatchProgress = taskStore.$subscribe((mutation, state) => {
    if (mutation.events?.key === 'currentProgress' && state.currentProgress.status) {
      addLog('info', state.currentProgress.status)
    }
  })

  // 清理函数
  onUnmounted(() => {
    unwatchIsRunning()
    unwatchProgress()
  })
}
</script>

<style scoped>
.training-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.content-wrapper {
  display: flex;
  gap: 16px;
  height: 100%;
}

.left-panel {
  width: 400px;
  display: flex;
  flex-direction: column;
}

.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0;
}

.task-selection-card,
.task-queue-card,
.log-card {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.task-selection-card :deep(.ant-card-body),
.task-queue-card :deep(.ant-card-body),
.log-card :deep(.ant-card-body) {
  flex: 1;
  padding: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.control-buttons {
  margin: 16px 0;
  text-align: center;
}

.progress-section {
  margin: 16px 0;
  padding: 12px;
  background: #fafafa;
  border-radius: 6px;
}

.progress-text {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  font-size: 12px;
  color: #666;
}

.status-text {
  color: #1890ff;
  font-weight: 500;
}

.log-container {
  height: 200px;
  overflow-y: auto;
  background: #000;
  border-radius: 4px;
  padding: 8px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  line-height: 1.4;
}

.log-entry {
  margin-bottom: 2px;
  word-wrap: break-word;
}

.log-time {
  color: #888;
  margin-right: 8px;
}

.log-message {
  color: #ccc;
}

.log-info .log-message {
  color: #ccc;
}

.log-success .log-message {
  color: #52c41a;
}

.log-warning .log-message {
  color: #faad14;
}

.log-error .log-message {
  color: #ff4d4f;
}

.log-empty {
  color: #666;
  text-align: center;
  font-style: italic;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .left-panel {
    width: 350px;
  }
}

@media (max-width: 1000px) {
  .content-wrapper {
    flex-direction: column;
  }

  .left-panel {
    width: 100%;
    height: 300px;
  }
}
</style>