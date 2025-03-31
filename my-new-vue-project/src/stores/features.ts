import { defineStore } from 'pinia';
import { ref } from 'vue';
import axios from 'axios';
import type { Feature, FeatureState } from '@/types';
import { API_BASE_URL } from '@/config';

export const useFeatureStore = defineStore('features', () => {
  const state = ref<FeatureState>({
    features: {
      posture: true,
      emotion: true,
      wake: false
    }
  });

  const fetchFeatures = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/get_features`);
      state.value.features = response.data;
    } catch (error) {
      console.error('获取功能状态失败:', error);
      throw error;
    }
  };

  const toggleFeature = async (feature: Feature, enabled: boolean) => {
    try {
      await axios.post(`${API_BASE_URL}/toggle_feature`, {
        feature,
        enabled
      });
      state.value.features[feature] = enabled;
    } catch (error) {
      console.error('切换功能失败:', error);
      throw error;
    }
  };

  return {
    state,
    features: state.value.features,
    fetchFeatures,
    toggleFeature
  };
}); 