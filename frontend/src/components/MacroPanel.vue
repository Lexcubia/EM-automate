<template>
  <div class="macro-panel">
    <a-card title="自定义宏" :bordered="false">
      <!-- 操作按钮区域 -->
      <div class="action-buttons" style="margin-bottom: 16px">
        <a-space>
          <a-button type="primary" @click="showCreateModal">
            <template #icon>
              <PlusOutlined />
            </template>
            新建宏
          </a-button>
          <a-button @click="exportMacros">导出宏</a-button>
          <a-upload
            :show-upload-list="false"
            :before-upload="importMacros"
            accept=".json"
          >
            <a-button>导入宏</a-button>
          </a-upload>
        </a-space>
      </div>

      <!-- 宏列表 -->
      <div class="macro-list">
        <a-list
          :data-source="macros"
          :loading="loading"
          item-layout="horizontal"
        >
          <template #renderItem="{ item }">
            <a-list-item>
              <a-list-item-meta>
                <template #title>
                  <div class="macro-title">
                    <span class="macro-name">{{ item.name }}</span>
                    <a-switch
                      v-model:checked="item.enabled"
                      size="small"
                      @change="updateMacroStatus(item)"
                    />
                  </div>
                </template>
                <template #description>
                  <div class="macro-description">
                    {{ item.description || '暂无描述' }}
                  </div>
                  <div class="macro-steps-info">
                    <a-tag color="blue">{{ item.steps.length }} 个步骤</a-tag>
                    <span class="steps-preview">
                      {{ getStepsPreview(item.steps) }}
                    </span>
                  </div>
                </template>
              </a-list-item-meta>
              <template #actions>
                <a-button size="small" @click="editMacro(item)">编辑</a-button>
                <a-button size="small" @click="testMacro(item)">测试</a-button>
                <a-button size="small" @click="addToQueue(item)">添加到队列</a-button>
                <a-popconfirm
                  title="确定要删除这个宏吗？"
                  ok-text="确定"
                  cancel-text="取消"
                  @confirm="deleteMacro(item.id)"
                >
                  <a-button size="small" danger>删除</a-button>
                </a-popconfirm>
              </template>
            </a-list-item>
          </template>
        </a-list>
      </div>

      <!-- 空状态 -->
      <a-empty v-if="!loading && macros.length === 0" description="暂无宏，点击上方按钮创建">
        <a-button type="primary" @click="showCreateModal">创建第一个宏</a-button>
      </a-empty>
    </a-card>

    <!-- 创建/编辑宏对话框 -->
    <a-modal
      v-model:open="editModalVisible"
      :title="currentEditMacro ? '编辑宏' : '创建宏'"
      width="800px"
      @ok="saveMacro"
      @cancel="cancelEdit"
    >
      <div class="macro-form">
        <!-- 基本信息 -->
        <div class="form-section">
          <h4>基本信息</h4>
          <a-form layout="vertical">
            <a-form-item label="宏名称" required>
              <a-input
                v-model:value="macroForm.name"
                placeholder="输入宏名称"
                :maxlength="50"
              />
            </a-form-item>
            <a-form-item label="描述">
              <a-textarea
                v-model:value="macroForm.description"
                placeholder="输入宏描述（可选）"
                :rows="2"
                :maxlength="200"
              />
            </a-form-item>
          </a-form>
        </div>

        <!-- 步骤编辑 -->
        <div class="form-section">
          <div class="section-header">
            <div>
              <h4>宏步骤</h4>
              <div class="available-keys-info">
                <span v-if="Object.keys(availableKeys).length > 0" class="keys-count">
                  可用按键：{{ Object.keys(availableKeys).length }} 个
                </span>
                <span v-else class="no-keys-warning">
                  ⚠️ 无可用按键配置，请先在键盘映射中配置按键
                </span>
              </div>
            </div>
            <a-button
              size="small"
              type="dashed"
              @click="addStep"
              :disabled="Object.keys(availableKeys).length === 0"
            >
              <template #icon>
                <PlusOutlined />
              </template>
              添加步骤
            </a-button>
          </div>

          <div class="steps-list">
            <div
              v-for="(step, index) in macroForm.steps"
              :key="step.id || index"
              class="step-item"
            >
              <div class="step-header">
                <span class="step-number">步骤 {{ index + 1 }}</span>
                <a-button
                  size="small"
                  type="text"
                  danger
                  @click="removeStep(index)"
                >
                  <DeleteOutlined />
                </a-button>
              </div>

              <div class="step-content">
                <a-row :gutter="16">
                  <a-col :span="8">
                    <a-form-item label="类型">
                      <a-select
                        v-model:value="step.type"
                        @change="onStepTypeChange(index)"
                      >
                        <a-select-option value="key">按键</a-select-option>
                        <a-select-option value="delay">延迟</a-select-option>
                      </a-select>
                    </a-form-item>
                  </a-col>

                  <a-col :span="step.type === 'key' ? 8 : 16">
                    <a-form-item :label="step.type === 'key' ? '按键' : '延迟时间(秒)'">
                      <a-select
                        v-if="step.type === 'key'"
                        v-model:value="step.key"
                        :placeholder="Object.keys(availableKeys).length === 0 ? '请先配置键盘映射' : '选择按键'"
                        show-search
                        :filter-option="filterKeyOption"
                        :disabled="Object.keys(availableKeys).length === 0"
                      >
                        <a-select-option
                          v-for="(name, key) in availableKeys"
                          :key="key"
                          :value="key"
                        >
                          {{ name }} ({{ key }})
                        </a-select-option>
                      </a-select>
                      <a-input-number
                        v-else
                        v-model:value="step.delay"
                        :min="0.1"
                        :max="60"
                        :step="0.1"
                        placeholder="延迟时间"
                        style="width: 100%"
                      />
                    </a-form-item>
                  </a-col>

                  <a-col v-if="step.type === 'key'" :span="8">
                    <a-form-item label="按键方式">
                      <a-select v-model:value="step.press_type">
                        <a-select-option value="press">按下并释放</a-select-option>
                        <a-select-option value="down">按下</a-select-option>
                        <a-select-option value="up">释放</a-select-option>
                      </a-select>
                    </a-form-item>
                  </a-col>
                </a-row>

                <a-row v-if="step.type === 'key' && step.press_type === 'press'" :gutter="16">
                  <a-col :span="12">
                    <a-form-item label="持续时间(秒)">
                      <a-input-number
                        v-model:value="step.duration"
                        :min="0.1"
                        :max="10"
                        :step="0.1"
                        placeholder="按键持续时间"
                        style="width: 100%"
                      />
                    </a-form-item>
                  </a-col>
                </a-row>
              </div>
            </div>
          </div>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import { macroApi, keybindingsApi } from '@/utils/api'
import type { MacroCommand, MacroStep } from '@/types'

const emit = defineEmits(['task-selected'])

// 数据定义
const macros = ref<MacroCommand[]>([])
const loading = ref(false)
const keyNames = ref<Record<string, string>>({})


// 编辑相关
const editModalVisible = ref(false)
const currentEditMacro = ref<MacroCommand | null>(null)
const macroForm = ref<{
  name: string
  description: string
  steps: (MacroStep & { id?: string })[]
}>({
  name: '',
  description: '',
  steps: []
})

// 可用按键列表（完全来源于键位配置）
const availableKeys = computed(() => {
  return keyNames.value
})

// 方法
const loadMacros = async () => {
  try {
    loading.value = true
    const response = await macroApi.getMacros()
    macros.value = response.macros || []
  } catch (error) {
    message.error('加载宏列表失败')
    console.error('加载宏列表失败:', error)
  } finally {
    loading.value = false
  }
}

const loadKeyNames = async () => {
  try {
    const response = await keybindingsApi.getKeybindings()
    keyNames.value = response.key_names || {}
  } catch (error) {
    console.error('加载键位名称失败:', error)
  }
}

const getStepsPreview = (steps: MacroStep[]) => {
  if (steps.length === 0) return '无步骤'

  const preview = steps.slice(0, 3).map(step => {
    if (step.type === 'key') {
      const keyName = availableKeys.value[step.key!] || step.key
      return keyName
    } else {
      return `延迟${step.delay}秒`
    }
  }).join(' → ')

  return steps.length > 3 ? `${preview}...` : preview
}

const showCreateModal = () => {
  currentEditMacro.value = null
  macroForm.value = {
    name: '',
    description: '',
    steps: []
  }
  editModalVisible.value = true
}

const editMacro = (macro: MacroCommand) => {
  currentEditMacro.value = macro
  macroForm.value = {
    name: macro.name,
    description: macro.description || '',
    steps: macro.steps.map(step => ({ ...step }))
  }
  editModalVisible.value = true
}

const addStep = () => {
  // 获取第一个可用的按键作为默认值
  const availableKeyList = Object.keys(availableKeys.value)
  const firstKey = availableKeyList.length > 0 ? availableKeyList[0] : ''

  const newStep: MacroStep & { id?: string } = {
    id: Date.now().toString(),
    type: 'key',
    key: firstKey,
    press_type: 'press',
    duration: 0.1
  }
  macroForm.value.steps.push(newStep)
}

const removeStep = (index: number) => {
  macroForm.value.steps.splice(index, 1)
}

const onStepTypeChange = (index: number) => {
  const step = macroForm.value.steps[index]
  if (step.type === 'delay') {
    delete step.key
    delete step.press_type
    delete step.duration
    step.delay = 1.0
  } else {
    delete step.delay
    // 获取第一个可用的按键作为默认值
    const availableKeyList = Object.keys(availableKeys.value)
    step.key = availableKeyList.length > 0 ? availableKeyList[0] : ''
    step.press_type = 'press'
    step.duration = 0.1
  }
}

const saveMacro = async () => {
  if (!macroForm.value.name.trim()) {
    message.error('请输入宏名称')
    return
  }

  if (macroForm.value.steps.length === 0) {
    message.error('请至少添加一个步骤')
    return
  }

  // 验证步骤
  for (const step of macroForm.value.steps) {
    if (step.type === 'key' && !step.key) {
      message.error('请为按键步骤选择按键')
      return
    }
    if (step.type === 'delay' && (!step.delay || step.delay <= 0)) {
      message.error('请设置有效的延迟时间')
      return
    }
  }

  try {
    const macroData = {
      name: macroForm.value.name.trim(),
      description: macroForm.value.description.trim(),
      steps: macroForm.value.steps.map(({ id, ...step }) => step)
    }

    if (currentEditMacro.value) {
      await macroApi.updateMacro(currentEditMacro.value.id, macroData)
      message.success('宏更新成功')
    } else {
      await macroApi.createMacro(macroData)
      message.success('宏创建成功')
    }

    editModalVisible.value = false
    await loadMacros()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '保存宏失败')
  }
}

const cancelEdit = () => {
  editModalVisible.value = false
  currentEditMacro.value = null
}

const updateMacroStatus = async (macro: MacroCommand) => {
  try {
    await macroApi.updateMacro(macro.id, { enabled: macro.enabled })
    message.success('宏状态更新成功')
  } catch (error) {
    // 恢复原状态
    macro.enabled = !macro.enabled
    message.error('宏状态更新失败')
  }
}

const deleteMacro = async (macroId: string) => {
  try {
    await macroApi.deleteMacro(macroId)
    message.success('宏删除成功')
    await loadMacros()
  } catch (error) {
    message.error('宏删除失败')
  }
}

const testMacro = async (macro: MacroCommand) => {
  try {
    await macroApi.executeMacro(macro.id, 1)
    message.success('宏测试执行成功')
  } catch (error: any) {
    message.error(error.response?.data?.detail || '宏测试执行失败')
  }
}

const addToQueue = (macro: MacroCommand) => {
  const task = {
    id: `macro_${macro.id}_${Date.now()}`,
    name: macro.name,
    type: 'macro',
    category: 'macro',
    macro_id: macro.id,
    run_count: 1,
    priority: 1,
    status: 'pending' as const,
    progress: 0,
    added_at: new Date().toISOString(),
    params: {
      macro_name: macro.name,
      steps_count: macro.steps.length
    }
  }

  emit('task-selected', task)
  message.success('宏已添加到任务队列')
}

const exportMacros = async () => {
  try {
    const response = await macroApi.exportMacros()

    const blob = new Blob([JSON.stringify(response, null, 2)], {
      type: 'application/json'
    })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `macros_${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    message.success('宏配置导出成功')
  } catch (error) {
    message.error('宏配置导出失败')
  }
}

const importMacros = async (file: File) => {
  try {
    const text = await file.text()
    const data = JSON.parse(text)

    if (!data.macros || !Array.isArray(data.macros)) {
      message.error('配置文件格式错误：缺少 macros 字段')
      return false
    }

    Modal.confirm({
      title: '确认导入宏配置',
      content: `将导入 ${data.macros.length} 个宏，是否继续？`,
      okText: '确认',
      cancelText: '取消',
      onOk: async () => {
        try {
          await macroApi.importMacros(data)
          message.success('宏配置导入成功')
          await loadMacros()
        } catch (error: any) {
          message.error(error.response?.data?.detail || '宏配置导入失败')
        }
      }
    })
  } catch (error) {
    message.error('配置文件解析失败，请检查文件格式')
  }

  return false // 阻止默认上传行为
}

const filterKeyOption = (input: string, option: any) => {
  const key = option.value.toLowerCase()
  const name = option.children?.toLowerCase?.() || ''
  return key.includes(input.toLowerCase()) || name.includes(input.toLowerCase())
}

// 生命周期
onMounted(async () => {
  await Promise.all([
    loadMacros(),
    loadKeyNames()
  ])
})
</script>

<style scoped>
.macro-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.action-buttons {
  background: #f5f5f5;
  padding: 16px;
  border-radius: 6px;
  margin-bottom: 16px;
}

.macro-list {
  flex: 1;
  min-height: 0;
}

.macro-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.macro-name {
  font-weight: 600;
  color: #262626;
}

.macro-description {
  color: #8c8c8c;
  margin-bottom: 8px;
}

.macro-steps-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.steps-preview {
  font-size: 12px;
  color: #666;
  flex: 1;
}

.macro-form {
  max-height: 60vh;
  overflow-y: auto;
}

.form-section {
  margin-bottom: 24px;
}

.form-section h4 {
  margin: 0 0 16px 0;
  font-size: 14px;
  font-weight: 600;
  color: #262626;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.available-keys-info {
  margin-top: 4px;
}

.keys-count {
  font-size: 12px;
  color: #52c41a;
  font-weight: 500;
}

.no-keys-warning {
  font-size: 12px;
  color: #faad14;
  font-weight: 500;
}

.steps-list {
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  padding: 16px;
  background: #fafafa;
}

.step-item {
  background: white;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 12px;
}

.step-item:last-child {
  margin-bottom: 0;
}

.step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.step-number {
  font-weight: 600;
  color: #1890ff;
}

.step-content {
  padding-top: 8px;
}

:deep(.ant-form-item) {
  margin-bottom: 12px;
}

:deep(.ant-form-item-label) {
  padding-bottom: 4px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .macro-title {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .steps-preview {
    display: none;
  }
}
</style>