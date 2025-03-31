<template>
  <div class="clock">
    <div class="clock-face">
      <!-- 时钟刻度 -->
      <div v-for="n in 12" :key="n" class="clock-mark" :style="{ transform: `rotate(${n * 30}deg)` }">
        <div class="mark-line"></div>
        <div class="mark-number">{{ n }}</div>
      </div>
      <!-- 时钟指针 -->
      <div class="hand hour-hand" :style="{ transform: `rotate(${hourDegrees}deg)` }"></div>
      <div class="hand minute-hand" :style="{ transform: `rotate(${minuteDegrees}deg)` }"></div>
      <div class="hand second-hand" :style="{ transform: `rotate(${secondDegrees}deg)` }"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  currentTime: Date;
}>();

const hourDegrees = computed(() => {
  const hours = props.currentTime.getHours() % 12;
  const minutes = props.currentTime.getMinutes();
  return (hours * 30) + (minutes * 0.5); // 每小时30度，每分钟0.5度
});

const minuteDegrees = computed(() => {
  return props.currentTime.getMinutes() * 6; // 每分钟6度
});

const secondDegrees = computed(() => {
  return props.currentTime.getSeconds() * 6; // 每秒6度
});
</script>

<style scoped>
.clock {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background-color: #ffffff;
  position: relative;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.clock-face {
  width: 100%;
  height: 100%;
  position: relative;
}

.clock-mark {
  position: absolute;
  width: 100%;
  height: 100%;
}

.mark-line {
  position: absolute;
  top: 0;
  left: 50%;
  width: 2px;
  height: 15px;
  background-color: #333;
  transform-origin: bottom;
}

.mark-number {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 16px;
  color: #333;
  font-weight: bold;
}

.hand {
  position: absolute;
  bottom: 50%;
  left: 50%;
  transform-origin: bottom;
  background-color: #333;
}

.hour-hand {
  width: 4px;
  height: 60px;
  margin-left: -2px;
}

.minute-hand {
  width: 3px;
  height: 80px;
  margin-left: -1.5px;
}

.second-hand {
  width: 2px;
  height: 90px;
  margin-left: -1px;
  background-color: #ff4444;
}
</style> 