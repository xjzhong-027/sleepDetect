<template>
  <div class="page-wrapper">
    <div class="emotiondetect-container">
      <!-- 顶栏 -->
      <div class="header">
        <div class="back-button" @click="$router.go(-1)">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M15 18L9 12L15 6" stroke="#333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <h1>情绪检测</h1>
        <div class="share-button">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M18 8C19.6569 8 21 6.65685 21 5C21 3.34315 19.6569 2 18 2C16.3431 2 15 3.34315 15 5C15 5.12548 15.0077 5.24917 15.0227 5.37061L8.08261 9.34064C7.54305 8.51444 6.74765 8 5.85714 8C4.10238 8 2.68571 9.41667 2.68571 11.1714C2.68571 12.9262 4.10238 14.3429 5.85714 14.3429C6.74765 14.3429 7.54305 13.8284 8.08261 13.0022L15.0227 16.9722C15.0077 17.0937 15 17.2174 15 17.3429C15 19.0976 16.3431 20.5143 18 20.5143C19.6569 20.5143 21 19.0976 21 17.3429C21 15.5881 19.6569 14.1714 18 14.1714C17.1095 14.1714 16.3141 14.686 15.7745 15.5122L8.83447 11.5421C8.84947 11.4207 8.85714 11.297 8.85714 11.1714C8.85714 11.0458 8.84947 10.9221 8.83447 10.8007L15.7745 6.83064C16.3141 7.65685 17.1095 8.17143 18 8.17143Z" stroke="#333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
      </div>

      <!-- 情绪状态圆环 -->
      <div class="emotion-circle">
        <div class="circle-content">
          <div class="emotion-text">当前情绪</div>
          <div class="emotion-value">开心</div>
        </div>
      </div>

      <!-- 心情指数对比区域 -->
      <div class="mood-comparison">
        <div class="mood-card">
          <div class="mood-title">今日心情</div>
          <div class="mood-score">85</div>
          <div class="mood-circle">
            <div class="score-text">85</div>
            <div class="score-unit">分</div>
          </div>
        </div>
        <div class="mood-card">
          <div class="mood-title">昨日心情</div>
          <div class="mood-score">78</div>
          <div class="mood-circle">
            <div class="score-text">78</div>
            <div class="score-unit">分</div>
          </div>
        </div>
      </div>

      <!-- 对比分析 -->
      <div class="analysis-section">
        <div class="analysis-title">对比分析</div>
        <div class="analysis-content">
          <div class="trend-up">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M8 12L8 4M8 4L4 8M8 4L12 8" stroke="#4CAF50" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>较昨日提升 7 分</span>
          </div>
          <div class="trend-detail">情绪波动趋于稳定，建议继续保持</div>
        </div>
      </div>

      <!-- 情绪记录 -->
      <div class="emotion-history">
        <h2>情绪记录</h2>
        <div class="history-list">
          <div v-for="(record, index) in emotionHistory" :key="index" class="history-item">
            <div class="time">{{ record.time }}</div>
            <div class="emotion">{{ record.emotion }}</div>
          </div>
        </div>
      </div>

      <!-- 情绪自测按钮 -->
      <div class="test-button-container">
        <button class="test-button" @click="$router.push('/emotiontest')">
          情绪自测
        </button>
      </div>

      <!-- 底部导航 -->
      <BottomNav />
    </div>
  </div>
</template>

<script setup>
import BottomNav from '../components/BottomNav.vue';
</script>

<style scoped>
.page-wrapper {
  width: 393px;
  margin: 0 auto;
  min-height: 100vh;
  background: #FFFFFF;
}

.emotiondetect-container {
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
  justify-content: space-between;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.back-button, .share-button {
  padding: 20px;
  cursor: pointer;
}

.header h1 {
  font-size: 20px;
  font-weight: 600;
  color: #333333;
  margin: 0;
}

.emotion-circle {
  width: 150px;
  height: 150px;
  margin: 109px auto 20px;
  border-radius: 50%;
  background: linear-gradient(135deg, #389BFF 0%, #20BBC0 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  text-align: center;
}

.circle-content {
  padding: 20px;
}

.emotion-text {
  font-size: 16px;
  margin-bottom: 8px;
}

.emotion-value {
  font-size: 24px;
  font-weight: bold;
}

.mood-comparison {
  width: 100%;
  display: flex;
  justify-content: space-between;
  padding: 0 20px;
  margin-bottom: 20px;
}

.mood-card {
  width: 185px;
  height: 319px;
  background: #FFFFFF;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.mood-title {
  font-size: 16px;
  color: #333;
  margin-bottom: 10px;
}

.mood-score {
  font-size: 48px;
  font-weight: bold;
  color: #333;
  margin-bottom: 20px;
}

.mood-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: #f8f9fa;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.score-text {
  font-size: 32px;
  font-weight: bold;
  color: #333;
}

.score-unit {
  font-size: 14px;
  color: #666;
}

.analysis-section {
  padding: 20px;
  background: #f8f9fa;
  margin: 0 20px 20px;
  border-radius: 12px;
}

.analysis-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
}

.trend-up {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #4CAF50;
  margin-bottom: 8px;
}

.trend-detail {
  font-size: 14px;
  color: #666;
}

.emotion-history {
  padding: 20px;
}

.history-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
}

.history-item {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 12px;
  margin-bottom: 12px;
}

.time {
  font-size: 14px;
  color: #666;
  width: 60px;
}

.emotion-info {
  flex: 1;
}

.emotion-type {
  font-size: 16px;
  color: #333;
  margin-bottom: 4px;
}

.emotion-duration {
  font-size: 12px;
  color: #666;
}

.emotion-score {
  font-size: 16px;
  font-weight: 600;
  color: #333;
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
  
  .mood-card {
    width: 150px;
    height: 280px;
  }
  
  .mood-circle {
    width: 100px;
    height: 100px;
  }
  
  .score-text {
    font-size: 28px;
  }
}

.test-button-container {
  width: 100%;
  max-width: 393px;
  display: flex;
  justify-content: center;
  margin: 20px auto;
  padding: 0 15px;
  box-sizing: border-box;
}

.test-button {
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

.test-button:hover {
  background-color: #45a049;
}
</style> 