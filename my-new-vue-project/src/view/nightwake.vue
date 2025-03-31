<template>
  <div class="page-wrapper">
    <div class="nightwake-container">
      <!-- 顶栏 -->
      <div class="header">
        <div class="back-button" @click="$router.go(-1)">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M15 18L9 12L15 6" stroke="#333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <h1>夜起记录</h1>
      </div>

      <!-- 今日统计 -->
      <div class="today-stats">
        <div class="stat-card">
          <div class="stat-title">今日夜起次数</div>
          <div class="stat-value">{{ nightWakeCount }}次</div>
        </div>
        <div class="stat-card">
          <div class="stat-title">平均间隔</div>
          <div class="stat-value">{{ averageInterval }}</div>
        </div>
      </div>

      <!-- 时间点列表 -->
      <div class="timeline">
        <h2>夜起时间点</h2>
        <div class="timeline-list">
          <div v-for="(time, index) in wakeupTimes" :key="index" class="timeline-item">
            <div class="time">{{ time }}</div>
            <div class="duration">持续 {{ wakeDurations[index] }}</div>
          </div>
        </div>
      </div>

      <!-- 历史数据表格 -->
      <div class="history-table">
        <h2>历史记录</h2>
        <table>
          <thead>
            <tr>
              <th>日期</th>
              <th>次数</th>
              <th>总时长</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(record, index) in historyRecords" :key="index">
              <td>{{ record.date }}</td>
              <td>{{ record.count }}</td>
              <td>{{ record.duration }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 底部导航 -->
      <BottomNav />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import BottomNav from '../components/BottomNav.vue';

const nightWakeCount = ref(0);
const averageInterval = ref('2小时30分');
const wakeupTimes = ref(['23:30', '02:15', '04:45']);
const wakeDurations = ref(['5分钟', '3分钟', '4分钟']);
const historyRecords = ref([
  { date: '2024-03-20', count: 3, duration: '12分钟' },
  { date: '2024-03-19', count: 2, duration: '8分钟' },
  { date: '2024-03-18', count: 1, duration: '5分钟' }
]);

onMounted(() => {
  // 从后端获取数据
});
</script>

<style scoped>
.page-wrapper {
  width: 393px;
  margin: 0 auto;
  min-height: 100vh;
  background: #FFFFFF;
}

.nightwake-container {
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
}

.today-stats {
  margin-top: 89px;
  padding: 20px;
  display: flex;
  gap: 15px;
}

.stat-card {
  flex: 1;
  background: #f8f9fa;
  border-radius: 12px;
  padding: 15px;
  text-align: center;
}

.stat-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  color: #333;
  font-weight: bold;
}

.timeline {
  padding: 20px;
}

.timeline h2 {
  font-size: 18px;
  color: #333;
  margin-bottom: 15px;
}

.timeline-item {
  display: flex;
  justify-content: space-between;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 10px;
}

.time {
  font-size: 16px;
  color: #333;
}

.duration {
  font-size: 14px;
  color: #666;
}

.history-table {
  padding: 20px;
}

.history-table h2 {
  font-size: 18px;
  color: #333;
  margin-bottom: 15px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  font-weight: 600;
  color: #333;
}

td {
  color: #666;
}
</style> 