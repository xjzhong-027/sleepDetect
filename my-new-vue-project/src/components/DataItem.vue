<template>
  <div class="data-item" @click="$emit('click')">
    <div class="data-label">{{ label }}</div>
    <div class="data-value">{{ value }}</div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string;
  value: string | number;
}>();

defineEmits<{
  (e: 'click'): void;
}>();
</script>

<style scoped>
.data-item {
  width: calc(50% - 7.5px);
  height: 80px;
  background-color: #f8f9fa;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.data-item:hover {
  background-color: #e9ecef;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.data-label {
  font-size: 13px;
  color: #666;
  margin-bottom: 6px;
}

.data-value {
  font-size: 20px;
  color: #333;
  font-weight: bold;
}

@media screen and (max-width: 393px) {
  .data-item {
    height: 70px;
  }
}
</style> 