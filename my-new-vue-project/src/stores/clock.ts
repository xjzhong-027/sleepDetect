import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { ClockState } from '@/types';

export const useClockStore = defineStore('clock', () => {
  const state = ref<ClockState>({
    currentTime: new Date()
  });

  let clockInterval: number | null = null;

  const updateClock = () => {
    state.value.currentTime = new Date();
  };

  const startClock = () => {
    if (clockInterval) return;
    updateClock();
    clockInterval = window.setInterval(updateClock, 1000);
  };

  const stopClock = () => {
    if (clockInterval) {
      clearInterval(clockInterval);
      clockInterval = null;
    }
  };

  return {
    state,
    currentTime: state.value.currentTime,
    startClock,
    stopClock
  };
}); 