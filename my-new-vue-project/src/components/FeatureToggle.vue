<template>
  <div class="feature-item">
    <span>{{ featureLabel }}</span>
    <label class="switch">
      <input
        type="checkbox"
        :checked="enabled"
        @change="$emit('toggle', feature, $event.target.checked)"
      >
      <span class="slider round"></span>
    </label>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { Feature } from '@/types';

const props = defineProps<{
  feature: Feature;
  enabled: boolean;
}>();

const featureLabel = computed(() => {
  const labels: Record<Feature, string> = {
    posture: '姿势检测',
    emotion: '情绪检测',
    wake: '夜起检测'
  };
  return labels[props.feature];
});

defineEmits<{
  (e: 'toggle', feature: Feature, enabled: boolean): void;
}>();
</script>

<style scoped>
.feature-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.feature-item:last-child {
  border-bottom: none;
}

.feature-item span {
  font-size: 14px;
  color: #333;
}

/* 开关样式 */
.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
}

input:checked + .slider {
  background-color: #4CAF50;
}

input:checked + .slider:before {
  transform: translateX(26px);
}

.slider.round {
  border-radius: 24px;
}

.slider.round:before {
  border-radius: 50%;
}
</style> 