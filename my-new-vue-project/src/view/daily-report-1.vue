<template>
  <div class="page-wrapper">
    <div class="report-container">
      <!-- 顶栏 -->
      <div class="header">
        <div class="back-button" @click="$router.go(-1)">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M15 18L9 12L15 6" stroke="#333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <h1>睡眠报告</h1>
        <div class="date">2024-04-01</div>
      </div>

      <!-- 睡眠评分 -->
      <div class="score-section">
        <div class="score-card">
          <div class="score-value">85</div>
          <div class="score-label">睡眠评分</div>
          <div class="score-status">良好</div>
        </div>
      </div>

      <!-- 睡眠时长 -->
      <div class="duration-section">
        <h2>睡眠时长</h2>
        <div class="duration-card">
          <div class="duration-value">7小时30分</div>
          <div class="duration-time">22:30 - 06:00</div>
        </div>
      </div>

      <!-- 睡眠质量分析 -->
      <div class="analysis-section">
        <h2>睡眠质量分析</h2>
        <div class="analysis-grid">
          <div class="analysis-card">
            <div class="analysis-icon">😴</div>
            <div class="analysis-value">90%</div>
            <div class="analysis-label">睡眠姿势</div>
          </div>
          <div class="analysis-card">
            <div class="analysis-icon">😊</div>
            <div class="analysis-value">88%</div>
            <div class="analysis-label">情绪状态</div>
          </div>
        </div>
      </div>

      <!-- 睡眠建议 -->
      <div class="suggestions-section">
        <h2>睡眠建议</h2>
        <div class="suggestions-list">
          <div class="suggestion-item">
            <div class="suggestion-icon">💡</div>
            <div class="suggestion-text">继续保持良好的睡眠习惯，建议每天保持7-8小时的睡眠时间。</div>
          </div>
          <div class="suggestion-item">
            <div class="suggestion-icon">💡</div>
            <div class="suggestion-text">建议在睡前1小时避免使用电子设备，有助于提高睡眠质量。</div>
          </div>
        </div>
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

.report-container {
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
  flex: 1;
}

.date {
  font-size: 14px;
  color: #666;
  margin-right: 20px;
}

.score-section {
  margin-top: 89px;
  padding: 20px;
}

.score-card {
  background: #4CAF50;
  border-radius: 12px;
  padding: 30px;
  text-align: center;
  color: white;
}

.score-value {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 10px;
}

.score-label {
  font-size: 16px;
  margin-bottom: 5px;
}

.score-status {
  font-size: 14px;
  opacity: 0.9;
}

.duration-section {
  padding: 20px;
}

.duration-section h2 {
  font-size: 18px;
  color: #333;
  margin-bottom: 15px;
}

.duration-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.duration-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.duration-time {
  font-size: 14px;
  color: #666;
}

.analysis-section {
  padding: 20px;
}

.analysis-section h2 {
  font-size: 18px;
  color: #333;
  margin-bottom: 15px;
}

.analysis-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.analysis-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.analysis-icon {
  font-size: 24px;
  margin-bottom: 10px;
}

.analysis-value {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.analysis-label {
  font-size: 14px;
  color: #666;
}

.suggestions-section {
  padding: 20px;
}

.suggestions-section h2 {
  font-size: 18px;
  color: #333;
  margin-bottom: 15px;
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: #FFFFFF;
  border-radius: 12px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.suggestion-icon {
  font-size: 20px;
  margin-top: 2px;
}

.suggestion-text {
  font-size: 14px;
  color: #333;
  line-height: 1.5;
}
</style> 