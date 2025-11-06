<template>
  <div class="commission-letter-panel">
    <a-empty
      description="功能开发中..."
      :image="Empty.PRESENTED_IMAGE_SIMPLE"
    >
      <template #description>
        <span style="color: #8c8c8c;">
          委托密函功能即将推出
        </span>
      </template>
    </a-empty>
  </div>
</template>

<script setup>
import { Empty } from 'ant-design-vue'

// 这个组件目前是占位符
// 根据原始需求，委托密函功能暂时留空
</script>

<style scoped>
.commission-letter-panel {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}
</style>