<template>
  <div class="commission-panel">
    <a-row :gutter="16">
      <!-- 任务选择 -->
      <a-col :span="16">
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
              <span class="mission-content">
                <span class="mission-name">{{ mission.displayName }}</span>
                <span class="mission-tags">
                  <a-tag v-if="mission.infinity" size="small" color="purple" class="mission-type-tag">无尽</a-tag>
                  <a-tag size="small" color="blue" class="mission-type-tag">
                    {{ missionTypeDisplay(mission.type) }}
                  </a-tag>
                </span>
              </span>
            </a-radio>
          </a-radio-group>
        </div>
      </a-col>

      <!-- 等级选择 -->
      <a-col :span="8">
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

    <!-- 宏序列选择 -->
    <div class="macro-section">
      <div class="section">
        <h4>选择宏序列</h4>
        <a-select
          v-model:value="selectedMacro"
          placeholder="选择要执行的宏序列（必需）"
          style="width: 100%"
          :loading="macrosLoading"
          :disabled="macros.length === 0"
        >
          <a-select-option
            v-for="macro in macros"
            :key="macro.id"
            :value="macro.id"
            :disabled="!macro.enabled"
          >
            <div class="macro-option">
              <span class="macro-name">{{ macro.name }}</span>
              <span class="macro-info">{{ macro.steps.length }}步</span>
            </div>
          </a-select-option>
        </a-select>
        <div v-if="selectedMacro" class="macro-preview">
          <div class="macro-description">
            {{ selectedMacroObj?.description || '暂无描述' }}
          </div>
          <div class="macro-steps-preview">
            {{ getMacroStepsPreview(selectedMacroObj?.steps || []) }}
          </div>
        </div>
      </div>
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
        添加任务+宏到队列
      </a-button>
      <div class="task-summary">
        将添加：{{ currentMission?.displayName }}({{ availableLevels.find(l => l.key === selectedLevel)?.displayName }}) + {{ selectedMacroObj?.name || '请选择宏' }}
      </div>
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
import { macroApi } from '@/utils/api'
import type { Mission, MacroCommand, MacroStep } from '@/types'

const emit = defineEmits(['task-selected'])

// Store
const menuStore = useMenuStore()

// 响应式数据
const selectedMission = ref('')
const selectedLevel = ref('')
const runCount = ref(1)
const missions = ref<Mission[]>([])

// 宏相关数据
const selectedMacro = ref('')
const macros = ref<MacroCommand[]>([])
const macrosLoading = ref(false)

// 计算属性
const currentMission = computed(() => {
  return missions.value.find(m => m.key === selectedMission.value)
})

const availableLevels = computed(() => {
  return currentMission.value?.levels || []
})

const canAddTask = computed(() => {
  return selectedMission.value && selectedLevel.value && selectedMacro.value && runCount.value > 0 && runCount.value <= 99
})

const selectedMacroObj = computed(() => {
  return macros.value.find(m => m.id === selectedMacro.value)
})

// canAddMacroTask 不再需要，因为宏现在是可选的附加项

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

const missionTypeDisplay = (type: string) => {
  return menuStore.getMissionTypeDisplay(type)
}

const addTask = () => {
  if (!canAddTask.value) return

  const mission = currentMission.value
  const level = availableLevels.value.find(l => l.key === selectedLevel.value)
  const macro = selectedMacroObj.value

  if (!mission || !level || !macro) return

  // 创建带宏的任务
  const task = {
    id: `commission_${mission.key}_${level.key}_${macro.id}_${Date.now()}`,
    name: `${mission.displayName}(${level.displayName}) + ${macro.name}`,
    type: 'commission',
    category: 'commission',
    sub_category: 'daily_commission',
    mission_key: mission.key,
    selected_level: level.key,
    level_display_name: level.displayName,
    run_count: runCount.value,
    priority: 1,
    status: 'pending' as const,
    progress: 0,
    added_at: new Date().toISOString(),
    params: {
      mission_display_name: mission.displayName,
      mission_type: mission.type,
      infinity: mission.infinity,
      macro_id: macro.id,
      macro_name: macro.name,
      macro_steps_count: macro.steps.length,
      macro_description: macro.description
    }
  }

  emit('task-selected', task)

  // 重置选择
  selectedMission.value = ''
  selectedLevel.value = ''
  selectedMacro.value = ''
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
  const mission = currentMission.value
  if (!mission) return

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
}

// 宏相关方法
const loadMacros = async () => {
  try {
    macrosLoading.value = true
    const response = await macroApi.getMacros()
    macros.value = response.macros || []
  } catch (error) {
    console.error('加载宏列表失败:', error)
  } finally {
    macrosLoading.value = false
  }
}

const getMacroStepsPreview = (steps: MacroStep[]) => {
  if (steps.length === 0) return '无步骤'

  const preview = steps.slice(0, 4).map(step => {
    if (step.type === 'key') {
      return `按键${step.key}`
    } else {
      return `延迟${step.delay}秒`
    }
  }).join(' → ')

  return steps.length > 4 ? `${preview}...` : preview
}

// addMacroTask 方法不再需要，因为宏现在是任务的附加项

// 生命周期
onMounted(async () => {
  await Promise.all([
    loadMissions(),
    loadMacros()
  ])

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
  display: flex;
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
:deep(.mission-radio span.ant-radio+*){
  width: 100%;
  padding-inline-end: 0
}


.mission-content {
  display: flex;
  justify-content: space-between;
}

/* .mission-tags {
 
} */
.mission-type-tag {
  margin-inline: 0;
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

/* 宏相关样式 */
.macro-section {
  margin-bottom: 16px;
}

.macro-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.macro-name {
  font-weight: 500;
}

.macro-info {
  font-size: 12px;
  color: #999;
}

.macro-preview {
  margin-top: 8px;
  padding: 8px 12px;
  background: #f5f5f5;
  border-radius: 4px;
  font-size: 12px;
}

.macro-description {
  color: #666;
  margin-bottom: 4px;
}

.macro-steps-preview {
  color: #999;
}

.task-summary {
  margin-top: 8px;
  padding: 8px 12px;
  background: #e6f7ff;
  border: 1px solid #91d5ff;
  border-radius: 4px;
  font-size: 12px;
  color: #1890ff;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .execution-count {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .task-summary {
    font-size: 11px;
  }
}
</style>