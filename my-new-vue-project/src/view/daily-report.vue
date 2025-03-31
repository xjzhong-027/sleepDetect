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
        <h1>今日睡眠报告</h1>
      </div>

      <!-- 睡眠评分 -->
      <div class="score-section">
        <div class="score-circle">
          <div class="score-value">{{ sleepScore }}</div>
          <div class="score-label">睡眠评分</div>
        </div>
        <div class="score-details">
          <div class="detail-item">
            <span class="label">睡眠时长</span>
            <span class="value">{{ sleepDuration }}</span>
          </div>
          <div class="detail-item">
            <span class="label">入睡时间</span>
            <span class="value">{{ sleepTime }}</span>
          </div>
          <div class="detail-item">
            <span class="label">起床时间</span>
            <span class="value">{{ wakeTime }}</span>
          </div>
        </div>
      </div>

      <!-- 监测数据卡片 -->
      <div class="monitoring-cards">
        <!-- 情绪状态卡片 -->
        <div class="card">
          <div class="card-header">
            <h3>情绪状态</h3>
            <div class="status-indicator" :class="emotionStatus">{{ emotionStatus }}</div>
          </div>
          <div class="card-content">
            <div class="emotion-chart">
              <img v-if="emotionChart" :src="'data:image/png;base64,' + emotionChart" alt="情绪分布图" />
            </div>
            <div class="emotion-stats">
              <div class="stat-item">
                <span class="label">平均情绪</span>
                <span class="value">{{ averageEmotion }}</span>
              </div>
              <div class="stat-item">
                <span class="label">情绪波动</span>
                <span class="value">{{ emotionFluctuation }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 夜起情况卡片 -->
        <div class="card">
          <div class="card-header">
            <h3>夜起情况</h3>
            <div class="status-indicator" :class="wakeStatus">{{ wakeStatus }}</div>
          </div>
          <div class="card-content">
            <div class="wake-stats">
              <div class="stat-item">
                <span class="label">夜起次数</span>
                <span class="value">{{ nightWakeCount }}次</span>
              </div>
              <div class="stat-item">
                <span class="label">平均间隔</span>
                <span class="value">{{ averageWakeInterval }}</span>
              </div>
            </div>
            <div class="wake-timeline">
              <div v-for="(time, index) in wakeupTimes" :key="index" class="timeline-item">
                <span class="time">{{ time }}</span>
                <span class="duration">持续 {{ wakeDurations[index] }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 睡眠姿势卡片 -->
        <div class="card">
          <div class="card-header">
            <h3>睡眠姿势</h3>
            <div class="status-indicator" :class="postureStatus">{{ postureStatus }}</div>
          </div>
          <div class="card-content">
            <div class="posture-chart">
              <img v-if="postureChart" :src="'data:image/png;base64,' + postureChart" alt="姿势分布图" />
            </div>
            <div class="posture-stats">
              <div class="stat-item">
                <span class="label">不良姿势</span>
                <span class="value">{{ badPostureCount }}次</span>
              </div>
              <div class="stat-item">
                <span class="label">持续时间</span>
                <span class="value">{{ badPostureDuration }}</span>
              </div>
            </div>
            <div class="posture-tips">
              <div v-for="(tip, index) in postureTips" :key="index" class="tip-item">
                {{ tip }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 睡眠建议 -->
      <div class="suggestions-section">
        <h2>睡眠建议</h2>
        <div class="suggestion-cards">
          <div v-for="(suggestion, index) in sleepSuggestions" :key="index" class="suggestion-card">
            <div class="suggestion-icon">{{ suggestion.icon }}</div>
            <div class="suggestion-content">
              <h4>{{ suggestion.title }}</h4>
              <p>{{ suggestion.content }}</p>
            </div>
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
import { useRoute } from 'vue-router';

const route = useRoute();

// 睡眠评分相关
const sleepScore = ref(0);
const sleepDuration = ref('0小时0分');
const sleepTime = ref('--:--');
const wakeTime = ref('--:--');

// 情绪状态相关
const emotionStatus = ref('未检测');
const averageEmotion = ref('未检测');
const emotionFluctuation = ref('未检测');
const emotionChart = ref('');

// 夜起情况相关
const wakeStatus = ref('未检测');
const nightWakeCount = ref(0);
const averageWakeInterval = ref('未检测');
const wakeupTimes = ref([]);
const wakeDurations = ref([]);

// 睡眠姿势相关
const postureStatus = ref('未检测');
const badPostureCount = ref(0);
const badPostureDuration = ref('0分钟');
const postureTips = ref([]);
const postureChart = ref('');

// 睡眠建议
const sleepSuggestions = ref([]);

// 处理从detect.vue传递的数据
const processReportData = (data) => {
  try {
    // 1. 处理睡眠数据
    if (data.sleep_data) {
      const { duration, start_time, end_time } = data.sleep_data;
      sleepDuration.value = formatDuration(duration);
      sleepTime.value = formatTime(start_time);
      wakeTime.value = formatTime(end_time);
    }

    // 2. 处理情绪数据
    if (data.emotion_data) {
      const { current, history } = data.emotion_data;
      emotionStatus.value = {
        current: current || '未检测',
        history: history || []
      };
      if (current) {
        averageEmotion.value = current;
      }
      if (history && history.length > 0) {
        const emotionCounts = {};
        history.forEach(record => {
          emotionCounts[record.emotion] = (emotionCounts[record.emotion] || 0) + 1;
        });
        emotionFluctuation.value = Object.keys(emotionCounts).length > 1 ? '较大' : '较小';
      }
    }

    // 3. 处理夜起数据
    if (data.wake_data) {
      const { count, history } = data.wake_data;
      nightWakeCount.value = count || 0;
      wakeStatus.value = count <= 3 ? '正常' : '较多';
      wakeupTimes.value = history.map(record => formatTime(record.time));
      wakeDurations.value = history.map(record => formatDuration(record.duration));
    }

    // 4. 处理姿势数据
    if (data.posture_data) {
      const { current, history, statistics } = data.posture_data;
      postureStatus.value = {
        current: current || '未检测',
        history: history || [],
        statistics: statistics || {}
      };
      if (current) {
        badPostureCount.value = statistics.bad_posture_count || 0;
        badPostureDuration.value = formatDuration(statistics.bad_posture_duration || 0);
      }
      if (history && history.length > 0) {
        // 生成姿势建议
        postureTips.value = generatePostureTips(history);
      }
    }

    // 5. 处理历史数据
    if (data.history_data) {
      const { posture, emotion, wake } = data.history_data;
      // 这里可以根据需要处理历史数据
    }

    // 6. 生成建议
    generateSuggestions(data);

    // 7. 计算睡眠评分
    sleepScore.value = calculateSleepScore(data);

  } catch (error) {
    console.error('处理报告数据失败:', error);
    showError('处理报告数据时发生错误');
  }
};

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return '未知';
  const date = new Date(timestamp);
  return date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: false 
  });
};

// 格式化时长
const formatDuration = (seconds) => {
  if (!seconds) return '0小时0分钟';
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  return `${hours}小时${minutes}分钟`;
};

// 生成姿势建议
const generatePostureTips = (history) => {
  const tips = [];
  const postureCounts = {};
  
  // 统计各种姿势的持续时间
  history.forEach(record => {
    postureCounts[record.posture] = (postureCounts[record.posture] || 0) + record.duration;
  });

  // 根据统计结果生成建议
  if (postureCounts['左侧睡'] > 3600) {
    tips.push('建议适当调整左侧睡姿，避免长期压迫左肩和左臂');
  }
  if (postureCounts['右侧睡'] > 3600) {
    tips.push('建议适当调整右侧睡姿，避免长期压迫右肩和右臂');
  }
  if (postureCounts['左偏头仰睡'] > 1800 || postureCounts['右偏头仰睡'] > 1800) {
    tips.push('建议保持头部正位，避免长期偏头睡姿');
  }

  return tips;
};

// 生成建议
const generateSuggestions = (data) => {
  const suggestions = [];

  // 1. 睡眠时长建议
  if (data.sleep_data?.duration) {
    const duration = data.sleep_data.duration;
    if (duration < 6 * 3600) {
      suggestions.push('睡眠时间不足，建议保持7-8小时的睡眠时间');
    } else if (duration > 9 * 3600) {
      suggestions.push('睡眠时间过长，建议控制在8小时以内');
    }
  }

  // 2. 夜起建议
  if (data.wake_data?.count > 2) {
    suggestions.push('夜起次数较多，建议睡前避免饮用咖啡因饮品');
  }

  // 3. 姿势建议
  if (data.posture_data?.statistics) {
    const { statistics } = data.posture_data;
    const maxPosture = Object.entries(statistics)
      .reduce((max, [key, value]) => value > max.value ? { key, value } : max, { key: '', value: 0 });
    
    if (maxPosture.key === '左侧睡' && maxPosture.value > 0.6) {
      suggestions.push('左侧睡时间过长，建议适当调整睡姿');
    }
  }

  // 4. 情绪建议
  if (data.emotion_data?.current === '焦虑' || data.emotion_data?.current === '紧张') {
    suggestions.push('睡眠情绪较为紧张，建议进行放松练习');
  }

  sleepSuggestions.value = suggestions;
};

// 计算睡眠评分
const calculateSleepScore = (data) => {
  let score = 100;
  
  // 1. 睡眠时长评分
  if (data.sleep_data?.duration) {
    const duration = data.sleep_data.duration;
    if (duration < 6 * 3600) {
      score -= 20;
    } else if (duration > 9 * 3600) {
      score -= 10;
    }
  }

  // 2. 夜起评分
  if (data.wake_data?.count) {
    const count = data.wake_data.count;
    if (count > 2) {
      score -= count * 5;
    }
  }

  // 3. 姿势评分
  if (data.posture_data?.statistics) {
    const { statistics } = data.posture_data;
    const maxPosture = Object.entries(statistics)
      .reduce((max, [key, value]) => value > max.value ? { key, value } : max, { key: '', value: 0 });
    
    if (maxPosture.key === '左侧睡' && maxPosture.value > 0.6) {
      score -= 10;
    }
  }

  // 4. 情绪评分
  if (data.emotion_data?.current === '焦虑' || data.emotion_data?.current === '紧张') {
    score -= 15;
  }

  // 确保分数在0-100之间
  return Math.max(0, Math.min(100, score));
};

// 错误提示
const showError = (message) => {
  // 这里可以添加错误提示UI组件
  console.error(message);
};

// 获取报告数据
const fetchDailyReport = async () => {
  try {
    // 1. 尝试从路由参数获取数据
    const routeData = route.query.data;
    if (routeData) {
      const data = JSON.parse(routeData);
      processReportData(data);
      return;
    }

    // 2. 如果没有路由数据，尝试从本地存储获取
    const storedReportId = localStorage.getItem('currentReportId');
    if (storedReportId) {
      const response = await axios.get(`http://localhost:5002/get_report/${storedReportId}`);
      if (response.data.report) {
        processReportData(response.data.report);
      }
    } else {
      showError('未找到报告数据');
    }
  } catch (error) {
    console.error('获取报告数据失败:', error);
    showError('获取报告数据失败');
  }
};

onMounted(() => {
  fetchDailyReport();
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

.score-section {
  margin-top: 89px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 20px;
  background: #f8f9fa;
}

.score-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: #4CAF50;
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.score-value {
  font-size: 36px;
  font-weight: bold;
}

.score-label {
  font-size: 14px;
  margin-top: 4px;
}

.score-details {
  flex: 1;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.detail-item .label {
  color: #666;
  font-size: 14px;
}

.detail-item .value {
  color: #333;
  font-weight: 500;
}

.monitoring-cards {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.card {
  background: #FFFFFF;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.card-header {
  padding: 15px;
  background: #f8f9fa;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.status-indicator {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-indicator.良好 {
  background: #e8f5e9;
  color: #4CAF50;
}

.status-indicator.正常 {
  background: #e3f2fd;
  color: #2196f3;
}

.status-indicator.较差 {
  background: #ffebee;
  color: #f44336;
}

.card-content {
  padding: 15px;
}

.emotion-chart,
.posture-chart {
  width: 100%;
  height: 200px;
  margin-bottom: 15px;
  border-radius: 8px;
  overflow: hidden;
}

.emotion-chart img,
.posture-chart img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.stat-item .label {
  color: #666;
  font-size: 14px;
}

.stat-item .value {
  color: #333;
  font-weight: 500;
}

.wake-timeline {
  margin-top: 10px;
}

.timeline-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.timeline-item:last-child {
  border-bottom: none;
}

.timeline-item .time {
  color: #333;
}

.timeline-item .duration {
  color: #666;
  font-size: 14px;
}

.posture-tips {
  margin-top: 10px;
}

.tip-item {
  padding: 8px 0;
  color: #666;
  font-size: 14px;
}

.suggestions-section {
  padding: 20px;
}

.suggestions-section h2 {
  font-size: 18px;
  color: #333;
  margin-bottom: 15px;
}

.suggestion-cards {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.suggestion-card {
  display: flex;
  gap: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 12px;
}

.suggestion-icon {
  font-size: 24px;
}

.suggestion-content h4 {
  margin: 0 0 8px 0;
  color: #333;
}

.suggestion-content p {
  margin: 0;
  color: #666;
  font-size: 14px;
}
</style> 