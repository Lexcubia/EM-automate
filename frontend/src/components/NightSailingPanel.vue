<template>
  <div class="night-sailing-panel">
    <div class="section">
      <h4>选择等级</h4>
      <a-radio-group
        v-model:value="selectedLevel"
        direction="vertical"
        @change="onLevelChange"
      >
        <a-radio
          v-for="level in levels"
          :key="level.key"
          :value="level.key"
          class="level-radio"
        >
          {{ level.displayName }}
        </a-radio>
      </a-radio-group>
    </div>

    <div class="section">
      <h4>选择怪物类型</h4>
      <a-checkbox-group
        v-model:value="selectedMonsters"
        direction="vertical"
        :disabled="!selectedLevel"
      >
        <a-checkbox
          v-for="monster in availableMonsters"
          :key="monster.key"
          :value="monster.key"
          class="monster-checkbox"
        >
          {{ monster.displayName }}
        </a-checkbox>
      </a-checkbox-group>
    </div>

    <div class="section execution-count">
      <h4>执行次数</h4>
      <a-input-number
        v-model:value="runCount"
        :min="1"
        :max="99"
        :disabled="!selectedLevel"
        size="large"
        style="width: 120px"
      />
      <span class="count-help">1-99次</span>
    </div>

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
const selectedLevel = ref('')
const selectedMonsters = ref([])
const runCount = ref(1)
const levels = ref([])
const monstersByLevel = ref({})

// 计算属性
const currentLevelData = computed(() => {
  return levels.value.find(l => l.key === selectedLevel.value)
})

const availableMonsters = computed(() => {
  return monstersByLevel.value[selectedLevel.value] || []
})

const canAddTask = computed(() => {
  return selectedLevel.value && selectedMonsters.value.length > 0 && runCount.value > 0
})

// 方法
const loadLevels = async () => {
  try {
    const subCategories = await menuStore.ensureSubCategoriesLoaded('commission')
    const nightSailing = subCategories.find(sub => sub.key === 'night_sailing_manual')
    levels.value = nightSailing?.missions || []

    // 构建怪物数据
    levels.value.forEach(level => {
      if (level.levels && level.levels.length > 0) {
        monstersByLevel.value[level.key] = level.levels
      }
    })

    console.log('加载夜航手册等级:', levels.value)
  } catch (error) {
    console.error('加载夜航手册失败:', error)
  }
}

const onLevelChange = () => {
  // 重置怪物选择
  selectedMonsters.value = []
}

const addTask = () => {
  if (!canAddTask.value) return

  const level = currentLevelData.value
  const monsters = availableMonsters.value.filter(m => selectedMonsters.value.includes(m.key))

  monsters.forEach(monster => {
    const task = {
      mission_key: level.key,
      display_name: `${level.displayName} - ${monster.displayName}`,
      mission_type: level.type,
      selected_level: monster.key,
      level_display_name: monster.displayName,
      run_count: runCount.value,
      category: 'commission',
      sub_category: 'night_sailing_manual'
    }
    emit('task-selected', task)
  })

  // 重置选择
  selectedLevel.value = ''
  selectedMonsters.value = []
  runCount.value = 1
}

// 生命周期
onMounted(async () => {
  await loadLevels()
})
</script>

<style scoped>
.night-sailing-panel {
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

.level-radio,
.monster-checkbox {
  display: block;
  margin-bottom: 8px;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  transition: all 0.3s;
}

.level-radio:hover,
.monster-checkbox:hover {
  border-color: #40a9ff;
  background-color: #f6ffed;
}

.level-radio :deep(.ant-radio-wrapper),
.monster-checkbox :deep(.ant-checkbox-wrapper) {
  align-items: flex-start;
  width: 100%;
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

@media (max-width: 768px) {
  .execution-count {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>