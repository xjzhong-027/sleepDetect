<template>
  <div class="page-wrapper">
    <div class="profile-container">
      <!-- 顶栏 -->
      <div class="header">
        <h1>个人中心</h1>
      </div>

      <!-- 用户信息区域 -->
      <div class="user-section">
        <div class="avatar-container">
          <img :src="userAvatar" alt="用户头像" class="avatar">
          <div class="edit-avatar">
            <input type="file" ref="avatarInput" @change="handleAvatarChange" accept="image/*" style="display: none">
            <button class="edit-btn" @click="$refs.avatarInput.click()">更换头像</button>
          </div>
        </div>
        <div class="user-info">
          <div class="username">{{ isLoggedIn ? userInfo.username : '未登录' }}</div>
          <div class="user-id" v-if="isLoggedIn">ID: {{ userInfo.userId }}</div>
        </div>
      </div>

      <!-- 登录/注册表单 -->
      <div class="auth-section" v-if="!isLoggedIn">
        <div class="auth-tabs">
          <div 
            :class="['tab', { active: authMode === 'login' }]" 
            @click="authMode = 'login'"
          >登录</div>
          <div 
            :class="['tab', { active: authMode === 'register' }]" 
            @click="authMode = 'register'"
          >注册</div>
        </div>
        
        <div class="auth-form">
          <div class="form-group">
            <input 
              type="text" 
              v-model="formData.username" 
              placeholder="用户名"
              :class="{ error: formErrors.username }"
            >
            <div class="error-message" v-if="formErrors.username">{{ formErrors.username }}</div>
          </div>
          <div class="form-group">
            <input 
              type="password" 
              v-model="formData.password" 
              placeholder="密码"
              :class="{ error: formErrors.password }"
            >
            <div class="error-message" v-if="formErrors.password">{{ formErrors.password }}</div>
          </div>
          <div class="form-group" v-if="authMode === 'register'">
            <input 
              type="password" 
              v-model="formData.confirmPassword" 
              placeholder="确认密码"
              :class="{ error: formErrors.confirmPassword }"
            >
            <div class="error-message" v-if="formErrors.confirmPassword">{{ formErrors.confirmPassword }}</div>
          </div>
          <button 
            class="submit-btn" 
            @click="handleAuth"
            :disabled="isLoading"
          >
            {{ isLoading ? '处理中...' : (authMode === 'login' ? '登录' : '注册') }}
          </button>
        </div>
      </div>

      <!-- 用户数据统计 -->
      <div class="stats-section" v-if="isLoggedIn">
        <h2>数据统计</h2>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-value">{{ userStats.totalSleepDays }}</div>
            <div class="stat-label">监测天数</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ userStats.averageScore }}</div>
            <div class="stat-label">平均评分</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ userStats.bestScore }}</div>
            <div class="stat-label">最高评分</div>
          </div>
        </div>
      </div>

      <!-- 功能列表 -->
      <div class="features-section" v-if="isLoggedIn">
        <h2>功能设置</h2>
        <div class="feature-list">
          <div class="feature-item" @click="navigateTo('/report')">
            <span>睡眠报告</span>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M9 5L16 12L9 19" stroke="#666" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="feature-item" @click="navigateTo('/settings')">
            <span>系统设置</span>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M9 5L16 12L9 19" stroke="#666" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="feature-item" @click="handleLogout">
            <span>退出登录</span>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M9 5L16 12L9 19" stroke="#666" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
      </div>

      <!-- 底部导航 -->
      <BottomNav />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import BottomNav from '../components/BottomNav.vue';
import axios from 'axios';

const router = useRouter();
const isLoggedIn = ref(false);
const authMode = ref('login');
const isLoading = ref(false);
const userAvatar = ref('/default-avatar.png');
const avatarInput = ref(null);

// 添加API基础URL
const apiBaseUrl = 'http://127.0.0.1:5000';

// 用户信息
const userInfo = ref({
  username: '',
  userId: '',
  avatar: ''
});

// 表单数据
const formData = ref({
  username: '',
  password: '',
  confirmPassword: ''
});

// 表单错误
const formErrors = ref({
  username: '',
  password: '',
  confirmPassword: ''
});

// 用户统计数据
const userStats = ref({
  totalSleepDays: 0,
  averageScore: 0,
  bestScore: 0
});

// 处理头像更改
const handleAvatarChange = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('avatar', file);

  try {
    const response = await axios.post(apiBaseUrl + '/api/upload-avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    userAvatar.value = response.data.avatarUrl;
  } catch (error) {
    console.error('上传头像失败:', error);
  }
};

// 处理认证（登录/注册）
const handleAuth = async () => {
  if (!validateForm()) return;

  isLoading.value = true;
  try {
    const endpoint = authMode.value === 'login' ? '/api/login' : '/api/register';
    const response = await axios.post(apiBaseUrl + endpoint, {
      username: formData.value.username,
      password: formData.value.password
    });

    if (response.data.success) {
      isLoggedIn.value = true;
      userInfo.value = response.data.user;
      userAvatar.value = response.data.user.avatar || '/default-avatar.png';
      await fetchUserStats();
    }
  } catch (error) {
    console.error('认证失败:', error);
  } finally {
    isLoading.value = false;
  }
};

// 表单验证
const validateForm = () => {
  formErrors.value = {
    username: '',
    password: '',
    confirmPassword: ''
  };

  let isValid = true;

  if (!formData.value.username) {
    formErrors.value.username = '请输入用户名';
    isValid = false;
  }

  if (!formData.value.password) {
    formErrors.value.password = '请输入密码';
    isValid = false;
  }

  if (authMode.value === 'register' && formData.value.password !== formData.value.confirmPassword) {
    formErrors.value.confirmPassword = '两次输入的密码不一致';
    isValid = false;
  }

  return isValid;
};

// 获取用户统计数据
const fetchUserStats = async () => {
  try {
    const response = await axios.get(apiBaseUrl + '/api/user-stats');
    userStats.value = response.data;
  } catch (error) {
    console.error('获取统计数据失败:', error);
  }
};

// 处理退出登录
const handleLogout = async () => {
  try {
    await axios.post(apiBaseUrl + '/api/logout');
    isLoggedIn.value = false;
    userInfo.value = {
      username: '',
      userId: '',
      avatar: ''
    };
    userStats.value = {
      totalSleepDays: 0,
      averageScore: 0,
      bestScore: 0
    };
  } catch (error) {
    console.error('退出登录失败:', error);
  }
};

// 页面导航
const navigateTo = (path) => {
  router.push(path);
};

onMounted(async () => {
  try {
    const response = await axios.get(apiBaseUrl + '/api/check-auth');
    if (response.data.isLoggedIn) {
      isLoggedIn.value = true;
      userInfo.value = response.data.user;
      userAvatar.value = response.data.user.avatar || '/default-avatar.png';
      await fetchUserStats();
    }
  } catch (error) {
    console.error('检查认证状态失败:', error);
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

.profile-container {
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
  justify-content: center;
  position: fixed;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.header h1 {
  font-size: 20px;
  font-weight: 600;
  color: #333333;
  margin: 0;
}

.user-section {
  margin-top: 89px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #f8f9fa;
}

.avatar-container {
  position: relative;
  margin-bottom: 15px;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #4CAF50;
}

.edit-avatar {
  position: absolute;
  bottom: 0;
  right: 0;
}

.edit-btn {
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 15px;
  padding: 4px 8px;
  font-size: 12px;
  cursor: pointer;
}

.user-info {
  text-align: center;
}

.username {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin-bottom: 5px;
}

.user-id {
  font-size: 14px;
  color: #666;
}

.auth-section {
  padding: 20px;
}

.auth-tabs {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 2px solid #eee;
}

.tab {
  flex: 1;
  text-align: center;
  padding: 10px;
  cursor: pointer;
  color: #666;
  position: relative;
}

.tab.active {
  color: #4CAF50;
}

.tab.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 2px;
  background: #4CAF50;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  position: relative;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
}

.form-group input.error {
  border-color: #f44336;
}

.error-message {
  color: #f44336;
  font-size: 12px;
  margin-top: 4px;
}

.submit-btn {
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px;
  font-size: 16px;
  cursor: pointer;
}

.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.stats-section {
  padding: 20px;
}

.stats-section h2 {
  font-size: 18px;
  color: #333;
  margin-bottom: 15px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}

.stat-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 15px;
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #4CAF50;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.features-section {
  padding: 20px;
}

.features-section h2 {
  font-size: 18px;
  color: #333;
  margin-bottom: 15px;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.feature-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 12px;
  cursor: pointer;
}

.feature-item span {
  color: #333;
  font-size: 16px;
}

.feature-item:hover {
  background: #f0f0f0;
}
</style> 