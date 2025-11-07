<template>
  <div id="app">
    <a-config-provider :locale="zhCN">
      <router-view />
    </a-config-provider>
  </div>
</template>

<script setup lang="ts">
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import { onMounted } from 'vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

onMounted(async () => {
  // 初始化应用
  await appStore.initialize()

  // 设置应用标题
  document.title = 'EM-Automate'
})
</script>

<style>
#app {
  height: 100vh;
  overflow: hidden;
}

body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 禁用文本选择（在某些UI元素上） */
.no-select {
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

/* 卡片阴影效果 */
.card-shadow {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 渐变背景 */
.gradient-bg {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
</style>