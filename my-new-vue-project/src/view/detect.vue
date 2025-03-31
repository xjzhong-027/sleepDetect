<template>
  <div class="page-wrapper">
    <div class="detect-container">
      <!-- 顶栏 -->
      <TopNav title="睡眠监测" />

      <!-- 内容区域容器 -->
      <div class="content-wrapper">
        <!-- 时钟区域 -->
        <div class="clock-container">
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
        </div>

        <!-- 功能控制区域 -->
        <div class="feature-controls">
          <div class="feature-item">
            <span>姿势检测</span>
            <label class="switch">
              <input type="checkbox" v-model="features.posture" @change="toggleFeature('posture', $event.target.checked)">
              <span class="slider round"></span>
            </label>
          </div>
          <div class="feature-item">
            <span>情绪检测</span>
            <label class="switch">
              <input type="checkbox" v-model="features.emotion" @change="toggleFeature('emotion', $event.target.checked)">
              <span class="slider round"></span>
            </label>
          </div>
          <div class="feature-item">
            <span>夜起检测</span>
            <label class="switch">
              <input type="checkbox" v-model="features.wake" @change="toggleFeature('wake', $event.target.checked)">
              <span class="slider round"></span>
            </label>
          </div>
        </div>

        <!-- 数据展示区域 -->
        <div class="data-container">
          <div class="data-row">
            <div class="data-item" @click="$router.push('/detect')">
              <div class="data-label">睡眠时长</div>
              <div class="data-value">{{ formatDuration(sleepDuration) }}</div>
            </div>
            <div class="data-item" @click="$router.push('/emotiondetect')">
              <div class="data-label">情绪</div>
              <div class="data-value">{{ currentEmotion }}</div>
            </div>
          </div>
          <div class="data-row">
            <div class="data-item" @click="$router.push('/nightwake')">
              <div class="data-label">夜起次数</div>
              <div class="data-value">{{ nightWakeCount }}次</div>
            </div>
            <div class="data-item" @click="$router.push('/posturedetect')">
              <div class="data-label">姿势</div>
              <div class="data-value">{{ currentPosture }}</div>
            </div>
          </div>
        </div>

        <!-- 控制按钮 -->
        <div class="control-container">
          <button 
            @click="startStopMonitoring" 
            class="control-button"
            :class="{ 'monitoring': isMonitoring }"
          >
            {{ isMonitoring ? '结束监测' : '开始监测' }}
          </button>
        </div>
      </div>

      <!-- 底部导航 -->
      <BottomNav />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios';
import BottomNav from '../components/BottomNav.vue';
import TopNav from '../components/TopNav.vue';
import { useRouter } from 'vue-router';

const apiBaseUrl = 'http://127.0.0.1:5000';
const currentEmotion = ref('未检测');
const currentPosture = ref('未检测');
const soundLevel = ref(45);
const sleepDuration = ref(0); // 以秒为单位
const isMonitoring = ref(false);
const connectionStatus = ref('未连接');
const startTime = ref(null);
const maxSoundLevel = ref(0);
const videoStream = ref(null);
const nightWakeCount = ref(0);
let monitoringInterval = null;

// 时钟相关
const hourDegrees = ref(0);
const minuteDegrees = ref(0);
const secondDegrees = ref(0);

const updateClock = () => {
  const now = new Date();
  const hours = now.getHours() % 12;
  const minutes = now.getMinutes();
  const seconds = now.getSeconds();

  hourDegrees.value = (hours * 30) + (minutes * 0.5); // 每小时30度，每分钟0.5度
  minuteDegrees.value = minutes * 6; // 每分钟6度
  secondDegrees.value = seconds * 6; // 每秒6度
};

// 格式化时间显示
const formatDuration = (seconds) => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = seconds % 60;
  
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
};

// 更新睡眠时长
const updateSleepDuration = () => {
  if (isMonitoring.value && startTime.value) {
    sleepDuration.value = Math.floor((Date.now() - startTime.value) / 1000);
  }
};

// 更新姿势检测状态
const updatePosture = async () => {
  if (!isMonitoring.value) return;
  
  try {
    const response = await axios.get(apiBaseUrl + '/get_posture');
    currentPosture.value = response.data.posture;
  } catch (error) {
    console.error('获取姿势数据失败:', error);
    currentPosture.value = '检测失败';
  }
};

let clockInterval = null;
let durationInterval = null;

// 添加功能状态
const features = ref({
  posture: true,
  emotion: false,
  wake: false
});

// 获取功能状态
const getFeatures = async () => {
  try {
    const response = await axios.get(apiBaseUrl + '/get_features');
    features.value = response.data;
  } catch (error) {
    console.error('获取功能状态失败:', error);
  }
};

// 切换功能
const toggleFeature = async (feature, enabled) => {
  try {
    await axios.post(apiBaseUrl + '/toggle_feature', {
      feature: feature,
      enabled: enabled
    });
    console.log(`${feature} 功能已${enabled ? '启用' : '禁用'}`);
  } catch (error) {
    console.error('切换功能失败:', error);
    // 恢复原状态
    features.value[feature] = !enabled;
  }
};

// 初始化所有状态
const initializeStates = () => {
  currentEmotion.value = '未检测';
  currentPosture.value = '未检测';
  nightWakeCount.value = 0;
  sleepDuration.value = 0;
  startTime.value = null;
  maxSoundLevel.value = 0;
  connectionStatus.value = '未连接';
  isMonitoring.value = false;
};

const router = useRouter();

const startStopMonitoring = async () => {
  try {
    if (isMonitoring.value) {
      // 停止监测
      isMonitoring.value = false;
      clearAllIntervals();
      
      // 停止摄像头
      try {
        await axios.get('http://localhost:5001/stop_monitoring');
      } catch (error) {
        console.error('停止摄像头失败:', error);
        // 继续执行，因为摄像头可能已经停止
      }

      // 获取最终监测数据
      try {
        const [monitoringResponse, historyResponse] = await Promise.all([
          axios.get('http://localhost:5001/get_monitoring_data'),
          axios.get('http://localhost:5001/get_history_data')
        ]);

        const monitoringData = monitoringResponse.data;
        const historyData = historyResponse.data;

        // 准备报告数据
        const reportData = {
          sleep_data: {
            duration: monitoringData.sleep_duration || 0,
            start_time: monitoringData.start_time,
            end_time: monitoringData.end_time
          },
          emotion_data: {
            current: monitoringData.emotion?.current || '未检测',
            history: monitoringData.emotion?.history || []
          },
          wake_data: {
            count: monitoringData.wake?.count || 0,
            history: monitoringData.wake?.history || []
          },
          posture_data: {
            current: monitoringData.posture?.current || '未检测',
            history: monitoringData.posture?.history || [],
            statistics: monitoringData.posture?.statistics || {}
          },
          history_data: historyData
        };

        // 直接导航到报告页面
        router.push({
          path: '/daily-report',
          query: { data: JSON.stringify(reportData) }
        });
      } catch (error) {
        console.error('获取监测数据失败:', error);
        showError('获取监测数据失败，请重试');
      }
    } else {
      // 开始监测
      isMonitoring.value = true;
      startTime.value = new Date();
      
      // 启动摄像头
      try {
        await axios.get('http://localhost:5001/start_monitoring');
      } catch (error) {
        console.error('启动摄像头失败:', error);
        showError('启动摄像头失败，请重试');
        isMonitoring.value = false;
        return;
      }

      // 开始定时获取数据
      monitoringInterval = setInterval(async () => {
        try {
          const response = await axios.get('http://localhost:5001/get_monitoring_data');
          const data = response.data;
          
          // 更新UI显示
          currentPosture.value = data.posture?.current || '未检测';
          currentEmotion.value = data.emotion?.current || '未检测';
          nightWakeCount.value = data.wake?.count || 0;
          
          // 更新监测时长
          const now = new Date();
          const duration = Math.floor((now - startTime.value) / 1000);
          sleepDuration.value = duration;
        } catch (error) {
          console.error('获取监测数据失败:', error);
        }
      }, 1000);
    }
  } catch (error) {
    console.error('监测操作失败:', error);
    showError('操作失败，请重试');
    isMonitoring.value = false;
  }
};

// 辅助函数：清除所有定时器
const clearAllIntervals = () => {
  if (monitoringInterval) {
    clearInterval(monitoringInterval);
    monitoringInterval = null;
  }
  if (durationInterval) {
    clearInterval(durationInterval);
    durationInterval = null;
  }
  if (clockInterval) {
    clearInterval(clockInterval);
    clockInterval = null;
  }
};

// 辅助函数：启动监测定时器
const startMonitoringTimers = () => {
  // 更新睡眠时长
  durationInterval = setInterval(updateSleepDuration, 1000);
  
  // 更新监测数据
  monitoringInterval = setInterval(async () => {
    try {
      const response = await axios.get(apiBaseUrl + '/get_monitoring_data');
      if (response.data) {
        const { posture, emotion, wake } = response.data;
        
        // 使用可选链操作符安全地更新数据
        if (posture?.current) currentPosture.value = posture.current;
        if (emotion?.current) currentEmotion.value = emotion.current;
        if (wake?.count !== undefined) nightWakeCount.value = wake.count;
      }
    } catch (error) {
      console.error('获取监测数据失败:', error);
      handleMonitoringError(error);
    }
  }, 1000);
};

// 辅助函数：处理监测错误
const handleMonitoringError = (error) => {
  if (error.response?.status === 503) {
    currentPosture.value = '摄像头未就绪';
    currentEmotion.value = '摄像头未就绪';
  } else {
    currentPosture.value = '检测失败';
    currentEmotion.value = '检测失败';
  }
};

onMounted(() => {
  initializeStates();
  updateClock();
  clockInterval = setInterval(updateClock, 1000);
  getFeatures();
});

onUnmounted(() => {
  // 清除所有定时器
  if (clockInterval) {
    clearInterval(clockInterval);
    clockInterval = null;
  }
  if (durationInterval) {
    clearInterval(durationInterval);
    durationInterval = null;
  }
  if (monitoringInterval) {
    clearInterval(monitoringInterval);
    monitoringInterval = null;
  }
  
  // 如果正在监测，停止监测
  if (isMonitoring.value) {
    axios.get(apiBaseUrl + '/stop_monitoring').catch(error => {
      console.error('停止监测失败:', error);
    });
  }
});
</script>

<style scoped>
.page-wrapper {
  width: 393px;
  margin: 0 auto;
  min-height: 100vh;
  background: #FFFFFF;
}

.detect-container {
  width: 100%;
  min-height: 100vh;
  background: #FFFFFF;
  position: relative;
  overflow-y: auto;
  padding-bottom: 84px;
}

.content-wrapper {
  width: 393px;
  margin: 0 auto;
  padding-top: 89px;
  padding-bottom: 154px;
}

.clock-container {
  width: 375px;
  height: 375px;
  margin: 20px auto;
  display: flex;
  justify-content: center;
  align-items: center;
}

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

.data-container {
  width: 100%;
  max-width: 393px;
  background-color: #ffffff;
  padding: 15px;
  border-radius: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  margin: 0 auto;
}

.data-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.data-row:last-child {
  margin-bottom: 0;
}

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

.control-container {
  width: 100%;
  max-width: 393px;
  display: flex;
  justify-content: center;
  margin: 20px auto;
  padding: 0 15px 20px 15px;
  box-sizing: border-box;
  position: fixed;
  bottom: 84px;
  left: 50%;
  transform: translateX(-50%);
  background: #ffffff;
  z-index: 90;
}

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

/* 确保底栏组件固定在底部 */
:deep(.bottom-nav) {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 84px;
  z-index: 100;
}

.video-container {
  display: none;
}

@media screen and (max-width: 393px) {
  .page-wrapper {
    width: 100%;
  }
  
  .clock-container {
    width: 100%;
    height: 300px;
  }
  
  .clock {
    height: 300px;
  }
  
  .data-item {
    height: 70px;
  }
}

.feature-controls {
  width: 100%;
  max-width: 393px;
  background-color: #ffffff;
  padding: 15px;
  border-radius: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  margin: 0 auto 15px;
}

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