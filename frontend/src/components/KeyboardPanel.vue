<template>
  <div class="keyboard-panel">
    <a-card title="键位配置" :bordered="false">
      <!-- 操作按钮区域 -->
      <div class="action-buttons" style="margin-bottom: 16px">
        <a-space>
          <a-button @click="exportConfig">导出配置</a-button>
          <a-upload
            :show-upload-list="false"
            :before-upload="importConfig"
            accept=".json"
          >
            <a-button>导入配置</a-button>
          </a-upload>
          <a-button @click="resetConfig" danger>重置为默认</a-button>
        </a-space>
      </div>

      <!-- 键位配置表格 -->
      <a-table
        :columns="columns"
        :data-source="keybindingsList"
        :pagination="false"
        bordered
        size="middle"
        :scroll="{ y: 400 }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'action'">
            <span>{{ actionNames[record.action] || record.action }}</span>
          </template>
          <template v-if="column.key === 'key'">
            <a-tag color="blue">
              {{ keyNames[record.key] || record.key }}
            </a-tag>
          </template>
          <template v-if="column.key === 'actions'">
            <a-space>
              <a-button size="small" @click="editKeyBinding(record)">
                编辑
              </a-button>
              <a-button size="small" @click="testKeyBinding(record.action)">
                测试
              </a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 编辑键位对话框 -->
    <a-modal
      v-model:open="editModalVisible"
      title="编辑键位"
      @ok="saveKeyBinding"
      @cancel="cancelEdit"
      width="500px"
    >
      <div style="margin-bottom: 16px">
        <label style="font-weight: bold; color: #666">动作：</label>
        <span style="margin-left: 8px">
          {{ currentEdit?.action ? (actionNames[currentEdit.action] || currentEdit.action) : '' }}
        </span>
      </div>
      <div>
        <label style="font-weight: bold; color: #666">按键：</label>
        <a-select
          v-model:value="selectedKey"
          placeholder="选择新的按键"
          style="width: 100%; margin-top: 8px"
          show-search
          :filter-option="filterOption"
          size="large"
        >
          <a-select-option
            v-for="(name, key) in availableKeys"
            :key="key"
            :value="key"
          >
            <span style="font-weight: 500">{{ name }}</span>
            <span style="color: #999; margin-left: 8px">({{ key }})</span>
          </a-select-option>
        </a-select>
      </div>
      <div v-if="currentEdit" style="margin-top: 16px; padding: 12px; background: #f5f5f5; border-radius: 4px">
        <div v-if="currentEdit" style="font-size: 12px; color: #666">
          当前按键：<span style="font-weight: bold; color: #1890ff">
            {{ keyNames[currentEdit.key] || currentEdit.key }}
          </span>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { keybindingsApi } from '@/utils/api'

// 数据定义
const keybindings = ref<Record<string, string>>({})
const actionNames = ref<Record<string, string>>({})
const keyNames = ref<Record<string, string>>({})

// 编辑相关
const editModalVisible = ref(false)
const currentEdit = ref<{ action: string; key: string } | null>(null)
const selectedKey = ref('')

// 表格列定义
const columns = [
  {
    title: '动作',
    dataIndex: 'action',
    key: 'action',
    width: '35%',
    fixed: 'left' as const
  },
  {
    title: '当前按键',
    dataIndex: 'key',
    key: 'key',
    width: '35%'
  },
  {
    title: '操作',
    key: 'actions',
    width: '30%',
    fixed: 'right' as const
  }
]

// 计算属性
const keybindingsList = computed(() => {
  return Object.entries(keybindings.value).map(([action, key]) => ({
    action,
    key
  }))
})

const availableKeys = computed(() => {
  const allKeys = {
    ...keyNames.value,
    // 添加常用键盘按键
    'A': 'A键',
    'B': 'B键',
    'C': 'C键',
    'D': 'D键',
    'E': 'E键',
    'F': 'F键',
    'G': 'G键',
    'H': 'H键',
    'I': 'I键',
    'J': 'J键',
    'K': 'K键',
    'L': 'L键',
    'M': 'M键',
    'N': 'N键',
    'O': 'O键',
    'P': 'P键',
    'Q': 'Q键',
    'R': 'R键',
    'S': 'S键',
    'T': 'T键',
    'U': 'U键',
    'V': 'V键',
    'W': 'W键',
    'X': 'X键',
    'Y': 'Y键',
    'Z': 'Z键',
    '0': '0键',
    '1': '1键',
    '2': '2键',
    '3': '3键',
    '4': '4键',
    '5': '5键',
    '6': '6键',
    '7': '7键',
    '8': '8键',
    '9': '9键',
    'F1': 'F1键',
    'F2': 'F2键',
    'F3': 'F3键',
    'F4': 'F4键',
    'F5': 'F5键',
    'F6': 'F6键',
    'F7': 'F7键',
    'F8': 'F8键',
    'F9': 'F9键',
    'F10': 'F10键',
    'F11': 'F11键',
    'F12': 'F12键',
    'num0': '小键盘0',
    'num1': '小键盘1',
    'num2': '小键盘2',
    'num3': '小键盘3',
    'num4': '小键盘4',
    'num5': '小键盘5',
    'num6': '小键盘6',
    'num7': '小键盘7',
    'num8': '小键盘8',
    'num9': '小键盘9',
    'multiply': '小键盘*',
    'add': '小键盘+',
    'subtract': '小键盘-',
    'decimal': '小键盘.',
    'divide': '小键盘/'
  }
  return allKeys
})

// 方法
const loadKeybindings = async () => {
  try {
    const response = await keybindingsApi.getKeybindings()
    keybindings.value = response.bindings
    actionNames.value = response.action_names
    keyNames.value = response.key_names
  } catch (error) {
    message.error('加载键位配置失败')
  }
}

const editKeyBinding = (record: { action: string; key: string }) => {
  currentEdit.value = { ...record }
  selectedKey.value = record.key
  editModalVisible.value = true
}

const saveKeyBinding = async () => {
  if (!currentEdit.value || !selectedKey.value) {
    message.error('请选择按键')
    return
  }

  if (selectedKey.value === currentEdit.value.key) {
    message.info('按键没有变化')
    editModalVisible.value = false
    return
  }

  try {
    await keybindingsApi.updateKeybinding(currentEdit.value.action, selectedKey.value)
    message.success('键位更新成功')
    editModalVisible.value = false
    await loadKeybindings()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '键位更新失败')
  }
}

const cancelEdit = () => {
  editModalVisible.value = false
  currentEdit.value = null
  selectedKey.value = ''
}

const testKeyBinding = async (action: string) => {
  try {
    await keybindingsApi.executeKeybinding(action, 'press', 0.1)
    message.success('键位测试成功')
  } catch (error: any) {
    message.error(error.response?.data?.detail || '键位测试失败')
  }
}

const exportConfig = async () => {
  try {
    // 创建文件下载
    const configData = {
      bindings: keybindings.value,
      action_names: actionNames.value,
      key_names: keyNames.value,
      export_time: new Date().toISOString(),
      version: '1.0'
    }

    const blob = new Blob([JSON.stringify(configData, null, 2)], {
      type: 'application/json'
    })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `keybindings_${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    message.success('配置文件导出成功')
  } catch (error) {
    message.error('配置文件导出失败')
  }
}

const importConfig = async (file: File) => {
  try {
    const text = await file.text()
    const data = JSON.parse(text)

    if (!data.bindings) {
      message.error('配置文件格式错误：缺少 bindings 字段')
      return false
    }

    Modal.confirm({
      title: '确认导入配置',
      content: '导入配置将覆盖当前的键位设置，是否继续？',
      okText: '确认',
      cancelText: '取消',
      onOk: async () => {
        try {
          // 这里应该调用后端API，目前先模拟成功
          await keybindingsApi.importConfig(file.name)
          message.success('配置文件导入成功')
          await loadKeybindings()
        } catch (error: any) {
          message.error('配置文件导入失败，请检查文件格式')
        }
      }
    })

  } catch (error) {
    message.error('配置文件解析失败，请检查文件格式')
  }

  return false // 阻止默认上传行为
}

const resetConfig = () => {
  Modal.confirm({
    title: '确认重置配置',
    content: '重置将恢复所有键位为默认设置，此操作不可撤销，是否继续？',
    okText: '确认重置',
    cancelText: '取消',
    okType: 'danger',
    onOk: async () => {
      try {
        await keybindingsApi.resetConfig()
        message.success('配置重置成功')
        await loadKeybindings()
      } catch (error: any) {
        message.error('配置重置失败')
      }
    }
  })
}

const filterOption = (input: string, option: any) => {
  const key = option.value.toLowerCase()
  const name = option.children?.[0]?.toLowerCase?.() || ''
  return key.includes(input.toLowerCase()) || name.includes(input.toLowerCase())
}

// 生命周期
onMounted(async () => {
  await loadKeybindings()
})
</script>

<style scoped>
.keyboard-panel {
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

:deep(.ant-table-thead > tr > th) {
  background: #fafafa;
  font-weight: 600;
}

:deep(.ant-table-tbody > tr:hover > td) {
  background: #f5f5f5;
}

:deep(.ant-select-selection-item) {
  font-weight: 500;
}
</style>