<template>
  <div class="home-container">
    <div class="header">
      <div class="header-content">
        <h1>睡眠助手</h1>
      </div>
    </div>

    <!-- 金刚区 -->
    <div class="diamond-section">
      <div class="diamond-scroll">
        <div class="diamond-grid">
          <div class="diamond-item" @click="navigateTo('posturedetect')">
            <div class="diamond-icon">airline_seat_recline_normal</div>
            <div class="diamond-text">姿势检测</div>
          </div>
          <div class="diamond-item" @click="navigateTo('emotiondetect')">
            <div class="diamond-icon">mood</div>
            <div class="diamond-text">情绪检测</div>
          </div>
          <div class="diamond-item" @click="navigateTo('detect')">
            <div class="diamond-icon">bedtime</div>
            <div class="diamond-text">夜起检测</div>
          </div>
          <div class="diamond-item" @click="navigateTo('detect')">
            <div class="diamond-icon">timer</div>
            <div class="diamond-text">睡眠时长</div>
          </div>
          <div class="diamond-item" @click="navigateTo('daily-report')">
            <div class="diamond-icon">assessment</div>
            <div class="diamond-text">今日报告</div>
          </div>
          <div class="diamond-item" @click="navigateTo('report')">
            <div class="diamond-icon">history</div>
            <div class="diamond-text">历史报告</div>
          </div>
          <div class="diamond-item" @click="navigateTo('emotiontest')">
            <div class="diamond-icon">psychology</div>
            <div class="diamond-text">情绪问卷</div>
          </div>
          <div class="diamond-item" @click="navigateTo('sounddetect')">
            <div class="diamond-icon">hearing</div>
            <div class="diamond-text">声音检测</div>
          </div>
        </div>
      </div>
    </div>

    <div class="bottom-nav">
      <BottomNav />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import BottomNav from '../components/BottomNav.vue';

const router = useRouter();

const navigateTo = (route) => {
  router.push(`/${route}`);
};
</script>

<style scoped>
.home-container {
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

.header-content {
  width: 393px;
  margin: 0 auto;
  padding: 0 20px;
}

.header-content h1 {
  margin: 0;
  color: #333;
  font-size: 20px;
  font-weight: 500;
}

/* 金刚区样式 */
.diamond-section {
  margin-top: 89px;
  padding: 20px 0;
  background: #FFFFFF;
}

.diamond-scroll {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

.diamond-scroll::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

.diamond-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
  padding: 0 20px;
  min-width: 393px;
}

.diamond-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px 0;
  background: #F8F9FA;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.diamond-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.diamond-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #4CAF50;
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 20px;
  margin-bottom: 8px;
}

.diamond-text {
  color: #333;
  font-size: 14px;
  font-weight: 500;
}

.bottom-nav {
  position: fixed;
  bottom: 0;
  width: 100%;
  height: 84px;
  background: #FFFFFF;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.05);
}
</style> 