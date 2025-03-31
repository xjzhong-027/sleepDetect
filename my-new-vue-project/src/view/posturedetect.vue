<template>
  <div class="posturedetect-container">
    <!-- 顶栏 -->
    <div class="header">
      <div class="back-button" @click="$router.go(-1)">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path d="M15 18L9 12L15 6" stroke="#333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <h1>姿势检测</h1>
    </div>

    <!-- 摄像头画面 -->
    <div class="camera-container">
      <img v-if="isMonitoring" :src="videoUrl" class="camera-feed" :key="videoKey" />
      <div v-else class="camera-placeholder">
        <span>等待开启摄像头...</span>
      </div>
      <div class="posture-text">{{ postureData.posture || '未检测' }}</div>
    </div>

    <!-- 姿势数据和3D重建区域 -->
    <div class="data-container">
      <!-- 3D重建区域 -->
      <div class="reconstruction-section">
        <div class="reconstruction-area">
          <ThreeDReconstruction :landmarks="currentLandmarks" />
        </div>
        <div class="position-description">
          <template v-if="positionDescription.includes('未检测')">
            等待检测人体姿势...
          </template>
          <template v-else>
            <strong>{{ postureData.posture || '未检测' }}</strong>: {{ postureData.description || '等待检测人体姿势...' }}
          </template>
        </div>
      </div>
      
      <!-- 实时姿势分析 -->
      <div class="realtime-analysis">
        <div class="analysis-header">实时监测数据</div>
        <div class="analysis-content">
          <div class="analysis-item">
            <div class="item-label">当前姿势</div>
            <div class="item-value">{{ postureData.posture || '未检测' }}</div>
          </div>
          <div class="analysis-item">
            <div class="item-label">姿势说明</div>
            <div class="item-value">{{ postureData.description || '等待检测人体姿势...' }}</div>
          </div>
          <div class="analysis-item">
            <div class="item-label">健康影响</div>
            <div class="item-value">{{ postureData.health_impact || '' }}</div>
          </div>
          <div class="analysis-item">
            <div class="item-label">建议</div>
            <div class="item-value">{{ postureData.suggestion || '' }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 数据监控组件 -->
    <PostureDataMonitor
      :current-posture="postureData.posture"
      :is-monitoring="isMonitoring"
      :history-data="historyData"
    />

    <!-- 姿势分类说明 -->
    <div class="info-section">
      <div class="posture-types">
        <h3>姿势分类说明</h3>
        <div class="posture-type" v-for="(desc, type) in postureDescriptions" :key="type">
          <h4>{{ type }}</h4>
          <p>{{ desc }}</p>
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
        {{ isMonitoring ? '结束检测' : '开始检测' }}
      </button>
    </div>

    <!-- 底部导航 -->
    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import BottomNav from '../components/BottomNav.vue';
import ThreeDReconstruction from '../components/ThreeDReconstruction.vue';
import PostureDataMonitor from '../components/PostureDataMonitor.vue'

const router = useRouter();
const apiBaseUrl = 'http://127.0.0.1:5001';
const isMonitoring = ref(false);
const videoKey = ref(0);
const postureData = ref({
  posture: '未检测',
  description: '等待检测人体姿势...',
  health_impact: '',
  suggestion: ''
});
const positionDescription = ref('未检测到人体');
const currentLandmarks = ref(null);
const videoUrl = ref('');
let monitoringInterval = null;

// 使用真实历史数据
const historyData = ref([]);

const postureDescriptions = {
  '左侧睡': '身体向左侧倾斜，肩部和髋部呈一定角度。此姿势有助于缓解胃酸反流，但需注意左肩和左臂的压力。',
  '右侧睡': '身体向右侧倾斜，肩部和髋部保持对齐。适合孕妇睡眠，但需注意右肩和右臂的血液循环。',
  '正常仰睡': '身体平躺，脊椎自然伸展，头部与床面平行。有助于维持脊椎自然曲线，但可能加重打鼾情况。',
  '左偏头仰睡': '仰卧位基础上头部向左偏转。注意颈部肌肉的拉伸程度，避免长期保持以防颈部疲劳。',
  '右偏头仰睡': '仰卧位基础上头部向右偏转。需注意颈椎的扭转角度，建议使用合适高度的枕头辅助。'
};

// 修改静态历史数据，添加更多信息
const staticHistoryData = [
  { 
    posture: '正常仰睡', 
    duration: 120, 
    timestamp: '22:30:00',
    description: '身体平躺，脊椎自然伸展，头部与床面平行。有助于维持脊椎自然曲线，但可能加重打鼾情况。'
  },
  { 
    posture: '左侧睡', 
    duration: 45, 
    timestamp: '23:15:00',
    description: '身体向左侧倾斜，肩部和髋部呈一定角度。此姿势有助于缓解胃酸反流，但需注意左肩和左臂的压力。'
  },
  { 
    posture: '右侧睡', 
    duration: 75, 
    timestamp: '00:30:00',
    description: '身体向右侧倾斜，肩部和髋部保持对齐。适合孕妇睡眠，但需注意右肩和右臂的血液循环。'
  },
  { 
    posture: '左偏头仰睡', 
    duration: 60, 
    timestamp: '01:45:00',
    description: '仰卧位基础上头部向左偏转。注意颈部肌肉的拉伸程度，避免长期保持以防颈部疲劳。'
  },
  { 
    posture: '右偏头仰睡', 
    duration: 45, 
    timestamp: '02:30:00',
    description: '仰卧位基础上头部向右偏转。需注意颈椎的扭转角度，建议使用合适高度的枕头辅助。'
  },
  { 
    posture: '正常仰睡', 
    duration: 90, 
    timestamp: '03:15:00',
    description: '身体平躺，脊椎自然伸展，头部与床面平行。有助于维持脊椎自然曲线，但可能加重打鼾情况。'
  },
  { 
    posture: '左侧睡', 
    duration: 60, 
    timestamp: '04:00:00',
    description: '身体向左侧倾斜，肩部和髋部呈一定角度。此姿势有助于缓解胃酸反流，但需注意左肩和左臂的压力。'
  },
  { 
    posture: '右侧睡', 
    duration: 45, 
    timestamp: '04:45:00',
    description: '身体向右侧倾斜，肩部和髋部保持对齐。适合孕妇睡眠，但需注意右肩和右臂的血液循环。'
  },
  { 
    posture: '正常仰睡', 
    duration: 120, 
    timestamp: '05:30:00',
    description: '身体平躺，脊椎自然伸展，头部与床面平行。有助于维持脊椎自然曲线，但可能加重打鼾情况。'
  }
];

const getPostureDescription = (posture) => {
  return postureDescriptions[posture] || '等待检测中...';
};

const handleApiError = (error, message) => {
  console.error(message, error);
  if (error.response) {
    console.error('Error response:', error.response.data);
    console.error('Error status:', error.response.status);
  }
};

const checkCameraStatus = async () => {
  try {
    const response = await axios.get(apiBaseUrl + '/check_camera');
    if (response.data.status === 'success') {
      return true;
    } else {
      console.error('摄像头状态检查失败:', response.data.message);
      alert(response.data.message || '摄像头未就绪，请检查摄像头权限或设备连接');
      return false;
    }
  } catch (error) {
    console.error('检查摄像头状态失败:', error);
    if (error.response && error.response.status === 404) {
      alert('摄像头检查接口未找到，请确保后端服务正常运行');
    } else {
      alert('检查摄像头状态失败，请检查后端服务状态');
    }
    return false;
  }
};

const startStopMonitoring = async () => {
  try {
    if (isMonitoring.value) {
      // 显示确认对话框
      const shouldGenerateReport = confirm('是否生成今日睡眠报告？\n点击"确定"生成报告，点击"取消"直接结束检测。');
      
      // 停止监测
      if (monitoringInterval) {
        clearInterval(monitoringInterval);
        monitoringInterval = null;
      }
      
      await axios.get(apiBaseUrl + '/stop_monitoring');
      isMonitoring.value = false;
      videoKey.value++;
      videoUrl.value = '';
      postureData.value = {
        posture: '未检测',
        description: '等待检测人体姿势...',
        health_impact: '',
        suggestion: ''
      };
      positionDescription.value = '未检测到人体';
      currentLandmarks.value = null;
      historyData.value = []; // 清空历史数据
      
      // 如果用户选择生成报告，跳转到报告页面
      if (shouldGenerateReport) {
        router.push('/report');
      }
      return;
    }

    // 开始监测
    console.log('正在检查健康状态...');
    const healthResponse = await axios.get(apiBaseUrl + '/health');
    if (healthResponse.data.status !== 'healthy') {
      throw new Error('后端服务未就绪');
    }
    console.log('健康检查通过');

    // 先开始监测
    console.log('正在启动监测...');
    try {
      const response = await axios.get(apiBaseUrl + '/start_monitoring');
      console.log('监测启动响应:', response.data);
      if (response.data.error) {
        throw new Error(response.data.error);
      }
    } catch (error) {
      console.error('启动监测失败:', error);
      if (error.response && error.response.data && error.response.data.error) {
        throw new Error(error.response.data.error);
      }
      throw error;
    }
    
    console.log('监测已启动，正在配置功能...');
    // 启用姿势检测功能
    await axios.post(apiBaseUrl + '/toggle_feature', { feature: 'posture', enabled: true });
    
    isMonitoring.value = true;
    videoKey.value++;
    postureData.value = {
      posture: '开始检测...',
      description: '未检测到人体',
      health_impact: '',
      suggestion: ''
    };
    positionDescription.value = '未检测到人体';
    
    // 添加时间戳来强制浏览器重新请求视频流
    videoUrl.value = `${apiBaseUrl}/video_feed?t=${Date.now()}`;
    console.log('视频流URL:', videoUrl.value);
    
    // 使用 requestAnimationFrame 来优化更新频率
    let lastUpdateTime = 0;
    const updateInterval = 1000; // 1秒更新一次数据
    
    const updateData = async () => {
      if (!isMonitoring.value) return;
      
      const currentTime = Date.now();
      if (currentTime - lastUpdateTime >= updateInterval) {
        try {
          console.log('正在获取监测数据...');
          const response = await axios.get(apiBaseUrl + '/get_monitoring_data');
          console.log('监测数据响应:', response.data);
          
          if (response.data) {
            const { posture, history, landmarks } = response.data;
            
            // 更新姿势数据
            if (posture) {
              console.log('姿势数据:', posture);
              postureData.value = posture;
              console.log('更新后的姿势数据:', postureData.value);
            }
            
            // 更新3D重建数据
            if (landmarks) {
              console.log('关键点数据:', landmarks);
              currentLandmarks.value = landmarks;
            }
            
            // 更新位置描述
            positionDescription.value = posture?.position_description || '未检测到人体';
            console.log('更新后的位置描述:', positionDescription.value);
            
            // 更新历史数据
            if (history && history.length > 0) {
              console.log('历史数据:', history);
              historyData.value = history;
            }
          }
        } catch (error) {
          console.error('获取监测数据失败:', error);
          if (error.response) {
            console.error('错误响应:', error.response.data);
            console.error('错误状态码:', error.response.status);
          }
          handleApiError(error, '获取监测数据失败:');
          handleMonitoringError(error);
        }
        lastUpdateTime = currentTime;
      }
      
      if (isMonitoring.value) {
        requestAnimationFrame(updateData);
      }
    };
    
    requestAnimationFrame(updateData);
  } catch (error) {
    handleApiError(error, '操作失败:');
    // 使用更具体的错误信息
    const errorMessage = error.response?.data?.error || error.message || '操作失败，请检查摄像头权限和后端服务状态';
    alert(errorMessage);
    isMonitoring.value = false;
    postureData.value = {
      posture: '未检测',
      description: '未检测到人体',
      health_impact: '',
      suggestion: ''
    };
    positionDescription.value = '未检测到人体';
    currentLandmarks.value = null;
    videoUrl.value = '';
  }
};

const handleMonitoringError = (error) => {
  if (error.response && error.response.status === 503) {
    postureData.value = {
      posture: error.response.data.error === "Camera not available" ? '摄像头未就绪' : '检测未启动',
      description: '未检测到人体',
      health_impact: '',
      suggestion: ''
    };
  } else {
    postureData.value = {
      posture: '检测失败',
      description: '未检测到人体',
      health_impact: '',
      suggestion: ''
    };
  }
  currentLandmarks.value = null;
};

onMounted(async () => {
  try {
    const response = await axios.get(apiBaseUrl + '/health');
    if (response.data.status === 'healthy') {
      // 如果摄像头未就绪，提示用户但允许继续
      if (response.data.camera_status !== '正常') {
        console.log('摄像头未就绪，等待用户手动启动');
      }
    } else {
      alert('系统未就绪，请检查后端服务状态');
    }
  } catch (error) {
    console.error('检查系统状态失败:', error);
    alert('检查系统状态失败，请确保后端服务正在运行');
  }
});

onUnmounted(async () => {
  if (monitoringInterval) {
    clearInterval(monitoringInterval);
    monitoringInterval = null;
  }
  
  if (isMonitoring.value) {
    try {
      await axios.get(apiBaseUrl + '/stop_monitoring');
    } catch (error) {
      // 忽略错误，因为组件要卸载了
    }
  }
});
</script>

<style scoped>
.posturedetect-container {
  width: 100%;
  min-height: 100vh;
  background: #FFFFFF;
  position: relative;
  overflow-y: auto;
  padding-bottom: 84px; /* 为底部导航留出空间 */
}

.header {
  width: 100%;
  height: 89px;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.back-button {
  padding: 20px;
  cursor: pointer;
}

.header h1 {
  font-size: 20px;
  font-weight: 600;
  color: #333333;
  margin: 0;
}

.camera-container {
  width: 100%;
  max-width: 393px;
  height: 300px;
  margin-top: 89px;
  background: #f8f9fa;
  overflow: hidden;
  position: relative;
}

.camera-feed {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.data-container {
  width: 100%;
  max-width: 393px;
  display: flex;
  padding: 15px;
  gap: 15px;
  background: #ffffff;
  margin: 0 auto;
}

.reconstruction-section {
  width: 180px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.reconstruction-area {
  width: 100%;
  height: 180px;
  background: #f0f2f5;
  border-radius: 8px;
  overflow: hidden;
}

.position-description {
  font-size: 12px;
  color: #666;
  line-height: 1.4;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 8px;
  text-align: justify;
}

.realtime-analysis {
  flex: 1;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
}

.analysis-header {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 15px;
}

.analysis-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.analysis-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
  padding: 10px;
  background: #ffffff;
  border-radius: 8px;
  margin-bottom: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.item-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.item-value {
  font-size: 16px;
  color: #333;
  line-height: 1.4;
  font-weight: 600;
}

.info-section {
  padding: 15px;
  margin-top: 15px;
}

.posture-types {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
}

.posture-types h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  color: #333;
}

.posture-type {
  margin-bottom: 15px;
}

.posture-type h4 {
  margin: 0 0 5px 0;
  font-size: 16px;
  color: #333;
}

.posture-type p {
  margin: 0;
  font-size: 14px;
  color: #666;
  line-height: 1.6;
}

.control-container {
  width: 100%;
  max-width: 393px;
  display: flex;
  justify-content: center;
  margin: 20px auto;
  padding: 0 15px;
  box-sizing: border-box;
  position: sticky;
  bottom: 84px;
  background: #ffffff;
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
  transition: all 0.3s ease;
}

.control-button.monitoring {
  background-color: #f44336;
  transform: scale(1.05);
}

.control-button:hover {
  transform: scale(1.05);
}

.control-button.monitoring:hover {
  background-color: #d32f2f;
}

:deep(.posture-monitor) {
  margin: 15px;
  border-radius: 12px;
  background: #f8f9fa;
  padding: 20px;
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

.posture-text {
  position: absolute;
  bottom: 20px;
  left: 20px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
}

@media screen and (max-width: 393px) {
  .camera-container,
  .data-container,
  .control-container {
    max-width: 100%;
  }
  
  .reconstruction-section {
    width: 150px;
  }
  
  .reconstruction-area {
    height: 150px;
  }
  
  .position-description {
    font-size: 11px;
  }
  
  .analysis-header {
    font-size: 14px;
  }
  
  .item-label,
  .item-value {
    font-size: 12px;
  }
  
  .posture-types h3 {
    font-size: 16px;
  }
  
  .posture-type h4 {
    font-size: 14px;
  }
  
  .posture-type p {
    font-size: 12px;
  }
}
</style> 