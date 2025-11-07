<template>
  <div class="main-view">
    <!-- 主内容区域 -->
    <div class="main-content">
      <div class="content-wrapper">
        <!-- 右侧：主内容区域 -->
        <div class="main-panel">
          <!-- 路由视图，根据当前路由显示对应组件 -->
          <router-view />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// MainView 现在是一个简单的容器，布局逻辑已移至 MainLayout
// 这个文件可以保留用于将来可能的全局功能
</script>

<style scoped>
.main-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.content-wrapper {
  display: flex;
  gap: 16px;
  height: 100%;
  flex: 1;
}

.main-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
}
</style>
