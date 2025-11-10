<template>
  <div class="night-sailing-panel">
    <a-row :gutter="16">
      <a-col :span="8">
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
              <div class="level-info">
                <span class="level-name">{{ level.displayName }}</span>
              </div>
            </a-radio>
          </a-radio-group>
        </div>
      </a-col>
      <a-col :span="16">
        <div class="section">
          <h4>选择怪物类型</h4>
          <a-radio-group
            v-model:value="selectedMonster"
            direction="vertical"
            :disabled="!selectedLevel"
          >
            <a-radio
              v-for="monster in availableMonsters"
              :key="monster.key"
              :value="monster.key"
              class="monster-radio"
            >
              <div class="monster-info">
                <span class="monster-name">{{ monster.displayName }}</span>
                <span class="monster-tags">
                  <a-tag
                    v-if="currentLevelData?.type"
                    size="small"
                    color="blue"
                    class="monster-type-tag"
                  >
                    {{ missionTypeDisplay(currentLevelData.type) }}
                  </a-tag>
                </span>
              </div>
            </a-radio>
          </a-radio-group>
        </div>
      </a-col>
    </a-row>

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
        将添加：{{ currentLevelData?.displayName }} - {{ availableMonsters.find(m => m.key === selectedMonster)?.displayName }} + {{ selectedMacroObj?.name || '请选择宏' }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { PlusOutlined } from "@ant-design/icons-vue";
import { useMenuStore } from "@/stores/menu";
import { macroApi } from "@/utils/api";
import type { Mission, MissionLevel, MacroCommand, MacroStep } from "@/types";

const emit = defineEmits(["task-selected"]);

// Store
const menuStore = useMenuStore();

// 响应式数据
const selectedLevel = ref("");
const selectedMonster = ref("");
const runCount = ref(1);
const levels = ref<Mission[]>([]);
const monstersByLevel = ref<Record<string, MissionLevel[]>>({});

// 宏相关数据
const selectedMacro = ref("");
const macros = ref<MacroCommand[]>([]);
const macrosLoading = ref(false);


// 计算属性
const currentLevelData = computed(() => {
  return levels.value.find((l) => l.key === selectedLevel.value);
});

const availableMonsters = computed(() => {
  return monstersByLevel.value[selectedLevel.value] || [];
});

const canAddTask = computed(() => {
  return (
    selectedLevel.value &&
    selectedMonster.value &&
    selectedMacro.value &&
    runCount.value > 0
  );
});

const selectedMacroObj = computed(() => {
  return macros.value.find(m => m.id === selectedMacro.value)
});

// 方法
const missionTypeDisplay = (type: string): string => {
  return menuStore.getMissionTypeDisplay(type)
}


const loadLevels = async () => {
  try {
    const subCategories = await menuStore.ensureSubCategoriesLoaded(
      "commission"
    );
    const nightSailing = subCategories.find(
      (sub) => sub.key === "night_sailing_manual"
    );
    levels.value = nightSailing?.missions || [];

    // 构建怪物数据
    levels.value.forEach((level) => {
      if (level.levels && level.levels.length > 0) {
        monstersByLevel.value[level.key] = level.levels;
      }
    });

    console.log("加载夜航手册等级:", levels.value);
  } catch (error) {
    console.error("加载夜航手册失败:", error);
  }
};

const onLevelChange = () => {
  // 重置怪物选择
  selectedMonster.value = "";
};

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

const addTask = () => {
  if (!canAddTask.value) return;

  const level = currentLevelData.value;
  if (!level) return;

  const monster = availableMonsters.value.find((m) =>
    m.key === selectedMonster.value
  );
  const macro = selectedMacroObj.value;

  if (!monster || !macro) return;

  // 创建带宏的任务
  const task: any = {
    id: `night_sailing_${level.key}_${monster.key}_${macro.id}_${Date.now()}`,
    name: `${level.displayName} - ${monster.displayName} + ${macro.name}`,
    type: 'commission',
    category: 'commission',
    sub_category: 'night_sailing_manual',
    mission_key: level.key,
    selected_level: monster.key,
    level_display_name: monster.displayName,
    run_count: runCount.value,
    priority: 1,
    status: 'pending' as const,
    progress: 0,
    added_at: new Date().toISOString(),
    params: {
      mission_display_name: level.displayName,
      mission_type: level.type,
      monster_display_name: monster.displayName,
      monster_key: monster.key,
      macro_id: macro.id,
      macro_name: macro.name,
      macro_steps_count: macro.steps.length,
      macro_description: macro.description
    }
  }

  emit("task-selected", task);

  // 重置选择
  selectedLevel.value = "";
  selectedMonster.value = "";
  selectedMacro.value = "";
  runCount.value = 1;
};

// 生命周期
onMounted(async () => {
  await Promise.all([
    loadLevels(),
    loadMacros()
  ])
});
</script>

<style lang="scss" scoped>
.night-sailing-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.section {
  margin-bottom: 16px;

  h4 {
    margin: 0 0 12px 0;
    font-size: 14px;
    font-weight: 600;
    color: #262626;
  }
}

.level-radio,
.monster-radio {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  transition: all 0.3s;
  gap: 8px;

  &:hover {
    border-color: #40a9ff;
    background-color: #f6ffed;
  }

  :deep(span.ant-radio+*){
  width: 100%;
  padding-inline-end: 0
}

  .level-info,
  .monster-info {
    display: flex;
    justify-content: space-between;
  }

  .level-name,
  .monster-name {
    font-weight: 500;
    color: #262626;
    line-height: 20px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    flex: 1;
    min-width: 0;
    height: 20px;
  }

  .monster-tags {
    display: flex;
    align-items: center;
  }

  .level-type-tag,
  .monster-type-tag {
    margin-inline: 0;
    margin-left: 8px;
    font-size: 10px;
  }
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
