<template>
  <button 
    class="control-button"
    :class="{ 'monitoring': isMonitoring }"
    @click="$emit('click')"
  >
    {{ isMonitoring ? '结束监测' : '开始监测' }}
  </button>
</template>

<script setup lang="ts">
defineProps<{
  isMonitoring: boolean;
}>();

defineEmits<{
  (e: 'click'): void;
}>();
</script>

<style scoped>
.control-button {
  width: 200px;
  height: 50px;
  border: none;
  border-radius: 25px;
  background-color: #4CAF50;
  color: white;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.control-button.monitoring {
  background-color: #f44336;
}
</style> 