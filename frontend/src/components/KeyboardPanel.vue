<template>
  <div class="keyboard-panel">
    <a-card title="键盘映射" class="placeholder-card">
      <div class="placeholder-content">
        <div class="placeholder-icon">
          <div class="icon-placeholder">⌨️</div>
        </div>
        <h3>键盘映射</h3>
        <p>键盘映射功能正在开发中...</p>
        <a-empty description="敬请期待" />
      </div>
    </a-card>
  </div>
</template>

<script setup>
// 暂时移除图标，避免导入问题
</script>

<style scoped>
.keyboard-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.placeholder-card {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.placeholder-card :deep(.ant-card-body) {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.placeholder-content {
  text-align: center;
  max-width: 400px;
}

.placeholder-icon {
  margin-bottom: 16px;
}

.placeholder-content h3 {
  margin: 16px 0 8px 0;
  color: #262626;
  font-size: 18px;
}

.placeholder-content p {
  color: #8c8c8c;
  margin-bottom: 24px;
}
</style>