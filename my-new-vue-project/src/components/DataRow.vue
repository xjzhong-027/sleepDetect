<template>
  <div class="data-row">
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
// 这是一个简单的容器组件，不需要额外的逻辑
</script>

<style scoped>
.data-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.data-row:last-child {
  margin-bottom: 0;
}
</style> 