<template>
  <div class="bottom-nav">
    <router-link to="/" class="nav-item" :class="{ active: currentPath === '/' }">
      <i class="fas fa-home"></i>
      <span>首页</span>
    </router-link>
    <router-link to="/detect" class="nav-item" :class="{ active: currentPath === '/detect' }">
      <i class="fas fa-video"></i>
      <span>监测</span>
    </router-link>
    <router-link to="/device" class="nav-item add-button" :class="{ active: currentPath === '/device' }">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 5V19M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span>设备</span>
    </router-link>
    <router-link to="/report" class="nav-item" :class="{ active: currentPath === '/report' }">
      <i class="fas fa-history"></i>
      <span>历史报告</span>
    </router-link>
    <router-link to="/profile" class="nav-item" :class="{ active: currentPath === '/profile' }">
      <i class="fas fa-user"></i>
      <span>我的</span>
    </router-link>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const currentPath = computed(() => route.path);
</script>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 84px;
  z-index: 100;
  background: #FFFFFF;
  box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.05);
  display: flex;
  justify-content: space-around;
  align-items: center;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  color: #666;
  font-size: 12px;
  gap: 4px;
  padding: 8px;
  transition: all 0.3s ease;
}

.nav-item.active {
  color: #4CAF50;
}

.nav-item i {
  font-size: 24px;
  margin-bottom: 4px;
}

.nav-item span {
  margin-top: 2px;
}

.add-button {
  width: 56px;
  height: 56px;
  background: #389BFF;
  border-radius: 50%;
  margin-top: -28px;
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  box-shadow: 0 4px 8px rgba(56, 155, 255, 0.3);
}

.add-button.active {
  background: #389BFF;
  color: white;
}

.add-button span {
  margin-top: 4px;
  color: white;
}

@media screen and (max-width: 393px) {
  .nav-item {
    font-size: 11px;
    padding: 6px;
  }
}
</style> 