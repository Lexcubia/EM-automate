<template>
  <div class="commission-panel">
    <a-row :gutter="16">
      <!-- 任务选择 -->
      <a-col :span="14">
        <div class="section">
          <h4>选择任务</h4>
          <a-radio-group
            v-model:value="selectedMission"
            direction="vertical"
            @change="onMissionChange"
          >
            <a-radio
              v-for="mission in missions"
              :key="mission.key"
              :value="mission.key"
              class="mission-radio"
            >
              {{ mission.displayName }}
              <a-tag size="small" class="mission-type-tag">
                {{ missionTypeDisplay(mission.type) }}
              </a-tag>
            </a-radio>
          </a-radio-group>
        </div>
      </a-col>

      <!-- 等级选择 -->
      <a-col :span="10">
        <div class="section">
          <h4>选择等级</h4>
          <a-radio-group
            v-model:value="selectedLevel"
            direction="vertical"
            :disabled="!selectedMission"
          >
            <a-radio
              v-for="level in availableLevels"
              :key="level.key"
              :value="level.key"
              class="level-radio"
            >
              {{ level.displayName }}
            </a-radio>
          </a-radio-group>
        </div>
      </a-col>
    </a-row>

    <!-- 执行次数 -->
    <div class="section execution-count">
      <h4>执行次数</h4>
      <a-input-number
        v-model:value="runCount"
        :min="1"
        :max="99"
        :disabled="!selectedMission"
        size="large"
        style="width: 120px"
      />
      <span class="count-help">1-99次</span>
    </div>

    <!-- 添加按钮 -->
    <div class="add-task-section">
      <a-button
        type="primary"
        size="large"
        :disabled="!canAddTask"
        @click="addTask"
        block
      >
        <template #icon>
          <PlusOutlined />
        </template>
        添加到队列
      </a-button>
    </div>

    <!-- 快速添加 -->
    <div class="quick-add-section">
      <a-divider>快速添加</a-divider>
      <a-space wrap>
        <a-button
          size="small"
          @click="quickAddAllLevels"
          :disabled="missions.length === 0"
        >
          全等级各1次
        </a-button>
        <a-button
          size="small"
          @click="quickAddSelectedMission"
          :disabled="!selectedMission"
        >
          当前任务全等级
        </a-button>
      </a-space>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { useMenuStore } from '@/stores/menu'

const emit = defineEmits(['task-selected'])

// Store
const menuStore = useMenuStore()

// 响应式数据
const selectedMission = ref('')
const selectedLevel = ref('')
const runCount = ref(1)
const missions = ref([])

// 计算属性
const currentMission = computed(() => {
  return missions.value.find(m => m.key === selectedMission.value)
})

const availableLevels = computed(() => {
  return currentMission.value?.levels || []
})

const canAddTask = computed(() => {
  return selectedMission.value && runCount.value > 0 && runCount.value <= 99
})

// 方法
const loadMissions = async () => {
  try {
    const subCategories = await menuStore.ensureSubCategoriesLoaded('commission')
    const dailyCommission = subCategories.find(sub => sub.key === 'daily_commission')
    missions.value = dailyCommission?.missions || []
    console.log('加载委托任务:', missions.value)
  } catch (error) {
    console.error('加载委托任务失败:', error)
  }
}

const onMissionChange = () => {
  // 重置等级选择
  selectedLevel.value = ''
}

const missionTypeDisplay = (type) => {
  return menuStore.getMissionTypeDisplay(type)
}

const addTask = () => {
  if (!canAddTask.value) return

  const mission = currentMission.value
  const level = availableLevels.value.find(l => l.key === selectedLevel.value)

  if (!mission || !level) return

  const task = {
    mission_key: mission.key,
    display_name: `${mission.displayName}(${level.displayName})`,
    mission_type: mission.type,
    selected_level: level.key,
    level_display_name: level.displayName,
    run_count: runCount.value,
    category: 'commission',
    sub_category: 'daily_commission'
  }

  emit('task-selected', task)

  // 重置选择
  selectedMission.value = ''
  selectedLevel.value = ''
  runCount.value = 1
}

const quickAddAllLevels = () => {
  const dailyCommission = missions.value
  dailyCommission.forEach(mission => {
    mission.levels.forEach(level => {
      const task = {
        mission_key: mission.key,
        display_name: `${mission.displayName}(${level.displayName})`,
        mission_type: mission.type,
        selected_level: level.key,
        level_display_name: level.displayName,
        run_count: 1,
        category: 'commission',
        sub_category: 'daily_commission'
      }
      emit('task-selected', task)
    })
  })
}

const quickAddSelectedMission = () => {
  if (!currentMission.value) return

  currentMission.value.levels.forEach(level => {
    const task = {
      mission_key: currentMission.value.key,
      display_name: `${currentMission.value.displayName}(${level.displayName})`,
      mission_type: currentMission.value.type,
      selected_level: level.key,
      level_display_name: level.displayName,
      run_count: 1,
      category: 'commission',
      sub_category: 'daily_commission'
    }
    emit('task-selected', task)
  })
}

// 生命周期
onMounted(async () => {
  await loadMissions()

  // 预加载任务类型显示名称
  const missionTypes = [...new Set(missions.value.map(m => m.type))]
  await Promise.all(
    missionTypes.map(type => menuStore.getMissionTypeDisplay(type))
  )
})
</script>

<style scoped>
.commission-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.section {
  margin-bottom: 16px;
}

.section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #262626;
}

.mission-radio,
.level-radio {
  display: block;
  margin-bottom: 8px;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  transition: all 0.3s;
}

.mission-radio:hover,
.level-radio:hover {
  border-color: #40a9ff;
  background-color: #f6ffed;
}

.mission-radio :deep(.ant-radio-wrapper),
.level-radio :deep(.ant-radio-wrapper) {
  align-items: flex-start;
  width: 100%;
}

.mission-type-tag {
  margin-left: 8px;
  font-size: 10px;
}

.execution-count {
  display: flex;
  align-items: center;
  gap: 12px;
}

.count-help {
  font-size: 12px;
  color: #8c8c8c;
}

.add-task-section {
  margin: 20px 0;
}

.quick-add-section {
  margin-top: auto;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .execution-count {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>