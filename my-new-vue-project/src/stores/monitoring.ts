import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';
import type { MonitoringState } from '@/types';
import { API_BASE_URL } from '@/config';

export const useMonitoringStore = defineStore('monitoring', () => {
  const state = ref<MonitoringState>({
    isMonitoring: false,
    currentEmotion: '未检测',
    currentPosture: '未检测',
    nightWakeCount: 0,
    sleepDuration: 0
  });

  let pollingInterval: number | null = null;

  const requestCameraPermission = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      stream.getTracks().forEach(track => track.stop());
      return true;
    } catch (error) {
      console.error('获取摄像头权限失败:', error);
      return false;
    }
  };

  const startMonitoring = async () => {
    try {
      // 先请求摄像头权限
      const hasPermission = await requestCameraPermission();
      if (!hasPermission) {
        throw new Error('无法获取摄像头权限');
      }

      // 启动后端监测
      const response = await axios.get(`${API_BASE_URL}/start_monitoring`);
      if (response.data.message === '监测已开始') {
        state.value.isMonitoring = true;
        startDataPolling();
      }
    } catch (error) {
      console.error('启动监测失败:', error);
      throw error;
    }
  };

  const stopMonitoring = async () => {
    try {
      await axios.get(`${API_BASE_URL}/stop_monitoring`);
      state.value.isMonitoring = false;
      stopDataPolling();
    } catch (error) {
      console.error('停止监测失败:', error);
      throw error;
    }
  };

  const startDataPolling = () => {
    if (pollingInterval) return;
    
    pollingInterval = window.setInterval(async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/get_monitoring_data`);
        const { posture, emotion, wake } = response.data;
        
        state.value.currentPosture = posture.current;
        state.value.currentEmotion = emotion.current;
        state.value.nightWakeCount = wake.count;
      } catch (error) {
        console.error('获取监测数据失败:', error);
      }
    }, 1000);
  };

  const stopDataPolling = () => {
    if (pollingInterval) {
      clearInterval(pollingInterval);
      pollingInterval = null;
    }
  };

  return {
    state,
    startMonitoring,
    stopMonitoring,
    startDataPolling,
    stopDataPolling
  };
}); 