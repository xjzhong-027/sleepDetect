<template>
  <div class="page-wrapper">
    <div class="device-container">
      <!-- 顶栏 -->
      <div class="header">
        <h1>设备管理</h1>
      </div>

      <!-- 当前设备 -->
      <div class="current-device">
        <h2>当前设备</h2>
        <div v-if="currentDevice" class="device-card connected">
          <div class="device-icon">
            <i class="fas fa-video"></i>
          </div>
          <div class="device-info">
            <h3>{{ currentDevice.name }}</h3>
            <p class="status">已连接</p>
            <p class="device-id">设备ID: {{ currentDevice.id }}</p>
          </div>
          <button class="disconnect-btn" @click="disconnectDevice">
            断开连接
          </button>
        </div>
        <div v-else class="connect-prompt">
          <p>暂无连接设备</p>
          <button class="connect-btn" @click="startConnect">
            <i class="fas fa-plus"></i>
            连接新设备
          </button>
        </div>
      </div>

      <!-- 历史设备 -->
      <div class="history-devices">
        <h2>历史设备</h2>
        <div class="device-list">
          <div v-for="device in historyDevices" :key="device.id" class="device-card">
            <div class="device-icon">
              <i class="fas fa-video"></i>
            </div>
            <div class="device-info">
              <h3>{{ device.name }}</h3>
              <p class="last-connected">上次连接: {{ device.lastConnected }}</p>
              <p class="device-id">设备ID: {{ device.id }}</p>
            </div>
            <button class="connect-btn small" @click="connectDevice(device)">
              连接
            </button>
          </div>
        </div>
      </div>

      <!-- 底部导航 -->
      <BottomNav />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import BottomNav from '../components/BottomNav.vue';

const currentDevice = ref(null);
const historyDevices = ref([
  {
    id: 'CAM001',
    name: '卧室摄像头',
    lastConnected: '2024-03-20 23:15'
  },
  {
    id: 'CAM002',
    name: '书房摄像头',
    lastConnected: '2024-03-19 20:30'
  },
  {
    id: 'CAM003',
    name: '客厅摄像头',
    lastConnected: '2024-03-18 19:45'
  }
]);

const startConnect = async () => {
  try {
    // 请求摄像头权限
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    // 如果成功获取权限，创建新设备
    const newDevice = {
      id: 'CAM' + (Math.floor(Math.random() * 1000)).toString().padStart(3, '0'),
      name: '本地摄像头',
      lastConnected: new Date().toLocaleString()
    };
    // 连接新设备
    currentDevice.value = newDevice;
    // 将新设备添加到历史设备列表
    if (!historyDevices.value.find(device => device.id === newDevice.id)) {
      historyDevices.value.unshift(newDevice);
    }
    // 停止摄像头流
    stream.getTracks().forEach(track => track.stop());
  } catch (error) {
    console.error('无法访问摄像头:', error);
    alert('请允许访问摄像头以连接设备');
  }
};

const connectDevice = (device) => {
  currentDevice.value = device;
};

const disconnectDevice = () => {
  currentDevice.value = null;
};
</script>

<style scoped>
.page-wrapper {
  width: 393px;
  margin: 0 auto;
  min-height: 100vh;
  background: #FFFFFF;
}

.device-container {
  width: 100%;
  min-height: 100vh;
  background: #FFFFFF;
  position: relative;
  overflow-y: auto;
  padding-bottom: 84px;
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

.header h1 {
  font-size: 20px;
  font-weight: 600;
  color: #333333;
  margin: 0;
  width: 100%;
  text-align: center;
}

.current-device {
  width: 100%;
  max-width: 393px;
  margin: 109px auto 0;
  padding: 0 20px;
}

.current-device h2, .history-devices h2 {
  font-size: 16px;
  color: #333;
  margin-bottom: 16px;
}

.device-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.device-card.connected {
  border: 2px solid #4CAF50;
}

.device-icon {
  width: 48px;
  height: 48px;
  background: #f0f0f0;
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.device-icon i {
  font-size: 24px;
  color: #666;
}

.device-info {
  flex: 1;
}

.device-info h3 {
  font-size: 16px;
  color: #333;
  margin: 0 0 4px 0;
}

.status {
  color: #4CAF50;
  font-size: 14px;
  margin: 0 0 4px 0;
}

.device-id, .last-connected {
  font-size: 12px;
  color: #666;
  margin: 0;
}

.connect-prompt {
  text-align: center;
  padding: 32px;
  background: #f8f9fa;
  border-radius: 12px;
}

.connect-prompt p {
  color: #666;
  margin-bottom: 16px;
}

.connect-btn {
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 25px;
  padding: 12px 24px;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.connect-btn.small {
  padding: 8px 16px;
  font-size: 14px;
}

.disconnect-btn {
  background: #f44336;
  color: white;
  border: none;
  border-radius: 20px;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
}

.history-devices {
  width: 100%;
  max-width: 393px;
  margin: 20px auto;
  padding: 0 20px;
}

.device-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
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

@media screen and (max-width: 393px) {
  .page-wrapper {
    width: 100%;
  }
}
</style> 