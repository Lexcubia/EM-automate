<template>
  <div class="task-queue">
    <div v-if="tasks.length === 0" class="empty-queue">
      <a-empty
        description="任务队列为空"
        :image="Empty.PRESENTED_IMAGE_SIMPLE"
      />
    </div>

    <div v-else class="queue-list">
      <div
        v-for="(task, index) in tasks"
        :key="task.id"
        :class="['task-item', { 'task-running': isRunning && index === 0 }]"
      >
        <div class="task-content">
          <div class="task-info">
            <div class="task-name">{{ task.display_name }}</div>
            <div class="task-meta">
              <a-tag size="small" color="blue">
                {{ missionTypeDisplay(task.mission_type) }}
              </a-tag>
              <span class="task-count">x{{ task.run_count }}</span>
            </div>
          </div>

          <div class="task-controls">
            <a-input-number
              :value="task.run_count"
              :min="1"
              :max="99"
              size="small"
              :disabled="isRunning"
              @change="(value) => updateTaskCount(task.id, value)"
              style="width: 60px"
            />
          </div>
        </div>

        <div class="task-actions">
          <a-button-group size="small">
            <a-tooltip title="上移">
              <a-button
                :disabled="index === 0 || isRunning"
                @click="moveUp(task.id)"
              >
                <UpOutlined />
              </a-button>
            </a-tooltip>

            <a-tooltip title="下移">
              <a-button
                :disabled="index === tasks.length - 1 || isRunning"
                @click="moveDown(task.id)"
              >
                <DownOutlined />
              </a-button>
            </a-tooltip>

            <a-tooltip title="删除">
              <a-button
                danger
                :disabled="isRunning"
                @click="removeTask(task.id)"
              >
                <DeleteOutlined />
              </a-button>
            </a-tooltip>
          </a-button-group>
        </div>

        <!-- 执行进度指示器 -->
        <div v-if="isRunning && index === 0" class="execution-indicator">
          <a-progress
            :percent="getTaskProgress(task)"
            size="small"
            :show-info="false"
            status="active"
          />
          <span class="progress-text">执行中...</span>
        </div>
      </div>
    </div>

    <!-- 队列统计 -->
    <div v-if="tasks.length > 0" class="queue-stats">
      <a-statistic-countdown
        title="任务总数"
        :value="totalTasks"
        format=""
      />
      <a-divider type="vertical" />
      <a-statistic
        title="预计时间"
        :value="estimatedTime"
        suffix="分钟"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  UpOutlined,
  DownOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue'
import { Empty } from 'ant-design-vue'
import { useMenuStore } from '@/stores/menu'

const props = defineProps({
  tasks: {
    type: Array,
    default: () => []
  },
  isRunning: {
    type: Boolean,
    default: false
  },
  currentProgress: {
    type: Object,
    default: () => ({
      current: 0,
      total: 0,
      status: '',
      isRunning: false
    })
  }
})

const emit = defineEmits([
  'remove-task',
  'move-up',
  'move-down',
  'update-task'
])

// Store
const menuStore = useMenuStore()

// 计算属性
const totalTasks = computed(() => {
  return props.tasks.reduce((sum, task) => sum + task.run_count, 0)
})

const estimatedTime = computed(() => {
  // 假设每个任务平均耗时2分钟
  return Math.ceil(totalTasks.value * 2)
})

// 方法
const missionTypeDisplay = (type) => {
  return menuStore.getMissionTypeDisplay(type)
}

const removeTask = (taskId) => {
  emit('remove-task', taskId)
}

const moveUp = (taskId) => {
  emit('move-up', taskId)
}

const moveDown = (taskId) => {
  emit('move-down', taskId)
}

const updateTaskCount = (taskId, count) => {
  if (count && count >= 1 && count <= 99) {
    emit('update-task', taskId, { run_count: count })
  }
}

const getTaskProgress = (task) => {
  if (!props.isRunning) return 0

  // 简单的进度计算，实际应该基于更精确的逻辑
  const overallProgress = props.currentProgress.current / props.currentProgress.total
  const taskWeight = task.run_count / totalTasks.value

  return Math.min(100, Math.round(overallProgress * 100 / taskWeight))
}
</script>

<style scoped>
.task-queue {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.empty-queue {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.queue-list {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 16px;
}

.task-item {
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  margin-bottom: 12px;
  padding: 12px;
  transition: all 0.3s;
  background: white;
}

.task-item:hover {
  border-color: #40a9ff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.task-running {
  border-color: #52c41a;
  background: linear-gradient(45deg, #f6ffed 0%, #ffffff 100%);
  box-shadow: 0 2px 8px rgba(82, 196, 26, 0.2);
}

.task-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.task-info {
  flex: 1;
  min-width: 0;
}

.task-name {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
  margin-bottom: 4px;
  word-break: break-all;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.task-count {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.task-controls {
  display: flex;
  align-items: center;
}

.task-actions {
  display: flex;
  justify-content: flex-end;
}

.execution-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}

.progress-text {
  font-size: 12px;
  color: #52c41a;
  font-weight: 500;
  white-space: nowrap;
}

.queue-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
  background: #fafafa;
  border-radius: 6px;
  border-top: 1px solid #f0f0f0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .task-content {
    flex-direction: column;
    gap: 8px;
  }

  .task-controls {
    width: 100%;
  }

  .task-actions {
    margin-top: 8px;
  }
}

/* 滚动条样式 */
.queue-list::-webkit-scrollbar {
  width: 4px;
}

.queue-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 2px;
}

.queue-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

.queue-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>