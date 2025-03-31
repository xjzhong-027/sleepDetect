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
        <h1>历史睡眠报告</h1>
      </div>

      <!-- 历史数据统计 -->
      <div class="stats-section">
        <div class="stat-card">
          <div class="stat-value">{{ averageScore }}</div>
          <div class="stat-label">平均睡眠评分</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ totalDays }}</div>
          <div class="stat-label">监测天数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ bestScore }}</div>
          <div class="stat-label">最佳评分</div>
        </div>
      </div>

      <!-- 历史趋势图 -->
      <div class="trend-section">
        <h2>睡眠趋势</h2>
        <div class="trend-chart">
          <img v-if="trendChart" :src="'data:image/png;base64,' + trendChart" alt="睡眠趋势图" />
        </div>
      </div>

      <!-- 历史记录列表 -->
      <div class="history-section">
        <h2>历史记录</h2>
        <div class="history-list">
          <div v-for="(record, index) in historyRecords" :key="index" class="history-item" @click="viewDetail(record)">
            <div class="history-date">
              <div class="date">{{ record.date }}</div>
              <div class="time">{{ record.time }}</div>
            </div>
            <div class="history-score">
              <div class="score">{{ record.score }}</div>
              <div class="duration">{{ record.duration }}</div>
            </div>
            <div class="history-status" :class="record.status">{{ record.status }}</div>
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
import BottomNav from '../components/BottomNav.vue';
import axios from 'axios';

// 统计数据
const averageScore = ref(0);
const totalDays = ref(0);
const bestScore = ref(0);
const trendChart = ref('');

// 历史记录
const historyRecords = ref([]);

// 获取历史报告数据
const fetchHistoryReports = async () => {
  try {
    // 获取所有报告
    const response = await axios.get('http://localhost:5002/list_reports');
    const reports = response.data.reports;

    // 更新统计数据
    if (reports.length > 0) {
      const scores = reports.map(report => report.sleep_score);
      averageScore.value = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
      bestScore.value = Math.max(...scores);
      totalDays.value = reports.length;
    }

    // 更新历史记录
    historyRecords.value = reports.map(report => ({
      id: report.id,
      date: report.timestamp.split(' ')[0],
      time: report.timestamp.split(' ')[1].slice(0, 5),
      score: report.sleep_score,
      duration: `${Math.floor(report.sleep_period.duration / 3600)}小时${Math.floor((report.sleep_period.duration % 3600) / 60)}分`,
      status: report.sleep_score >= 80 ? '良好' : report.sleep_score >= 60 ? '一般' : '较差'
    }));

    // 获取趋势图
    trendChart.value = response.data.trend_chart;

  } catch (error) {
    console.error('获取历史报告失败:', error);
  }
};

// 查看详情
const viewDetail = async (record) => {
  try {
    const response = await axios.get(`http://localhost:5002/get_report/${record.id}`);
    // 这里可以添加查看详情的逻辑，比如打开一个模态框显示详细信息
    console.log('报告详情:', response.data.report);
  } catch (error) {
    console.error('获取报告详情失败:', error);
  }
};

onMounted(() => {
  fetchHistoryReports();
});
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
}

.stats-section {
  margin-top: 89px;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  gap: 15px;
  background: #f8f9fa;
}

.stat-card {
  flex: 1;
  background: #FFFFFF;
  border-radius: 12px;
  padding: 15px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
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

.trend-section {
  padding: 20px;
}

.trend-section h2 {
  font-size: 18px;
  color: #333;
  margin-bottom: 15px;
}

.trend-chart {
  width: 100%;
  height: 200px;
  background: #FFFFFF;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.trend-chart img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.history-section {
  padding: 20px;
}

.history-section h2 {
  font-size: 18px;
  color: #333;
  margin-bottom: 15px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.history-item {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  cursor: pointer;
}

.history-date {
  display: flex;
  flex-direction: column;
}

.history-date .date {
  font-size: 16px;
  color: #333;
  font-weight: 500;
}

.history-date .time {
  font-size: 14px;
  color: #666;
}

.history-score {
  text-align: center;
}

.history-score .score {
  font-size: 20px;
  font-weight: bold;
  color: #4CAF50;
}

.history-score .duration {
  font-size: 12px;
  color: #666;
}

.history-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.history-status.良好 {
  background: #e8f5e9;
  color: #4CAF50;
}

.history-status.一般 {
  background: #e3f2fd;
  color: #2196f3;
}

.history-status.较差 {
  background: #ffebee;
  color: #f44336;
}
</style> 