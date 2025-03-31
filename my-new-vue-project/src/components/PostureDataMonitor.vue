<template>
  <div class="posture-monitor">
    <div class="monitor-header">
      <h3>姿势监测数据</h3>
      <div class="monitor-status" :class="{ active: isMonitoring }">
        {{ isMonitoring ? '监测中' : '未监测' }}
      </div>
    </div>

    <!-- 今日统计表格 -->
    <div class="statistics-section">
      <h4>今日统计</h4>
      <div class="statistics-table-container">
        <table class="statistics-table">
          <thead>
            <tr>
              <th>姿势类型</th>
              <th>持续时间</th>
              <th>次数</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="stat in dailyStats" :key="stat.posture_type">
              <td>{{ stat.posture_type }}</td>
              <td>{{ formatDuration(stat.total_duration) }}</td>
              <td>{{ stat.count }}次</td>
            </tr>
            <tr v-if="dailyStats.length === 0">
              <td colspan="3" class="no-data">暂无数据</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 姿势分布图表 -->
    <div class="chart-section">
      <h4>姿势分布</h4>
      <div ref="chartContainer" class="chart-container"></div>
    </div>

    <!-- 历史记录 -->
    <div class="history-section">
      <h4>最近记录</h4>
      <div class="history-list">
        <div v-for="(record, index) in historyRecords" :key="index" class="history-item">
          <div class="history-time">{{ record.timestamp }}</div>
          <div class="history-posture">{{ record.posture }}</div>
          <div class="history-duration">{{ formatDuration(record.duration) }}</div>
        </div>
        <div v-if="historyRecords.length === 0" class="no-data">
          暂无历史记录
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

export default {
  name: 'PostureDataMonitor',
  props: {
    currentPosture: {
      type: String,
      default: '未检测'
    },
    isMonitoring: {
      type: Boolean,
      default: false
    },
    historyData: {
      type: Array,
      default: () => []
    }
  },
  setup(props) {
    const apiBaseUrl = 'http://127.0.0.1:5001'
    const chartContainer = ref(null)
    const chart = ref(null)
    const dailyStats = ref([])
    const historyRecords = ref([])
    let statsInterval = null

    const formatDuration = (seconds) => {
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      const remainingSeconds = seconds % 60
      
      if (hours > 0) {
        return `${hours}小时${minutes}分`
      } else if (minutes > 0) {
        return `${minutes}分${remainingSeconds}秒`
      } else {
        return `${remainingSeconds}秒`
      }
    }

    const updateChart = (data) => {
      if (!chart.value || !Array.isArray(data)) return

      const chartData = data.map(item => ({
        name: item.posture_type,
        value: item.total_duration
      }))

      chart.value.setOption({
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c}秒 ({d}%)'
        },
        legend: {
          orient: 'horizontal',
          bottom: 0,
          data: chartData.map(item => item.name)
        },
        series: [{
          name: '姿势分布',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '14',
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: false
          },
          data: chartData
        }]
      })
    }

    const processHistoryData = (data) => {
      if (!Array.isArray(data)) return [];
      
      // 按姿势类型统计
      const stats = {}
      let lastPosture = null
      
      data.forEach(record => {
        if (!stats[record.posture]) {
          stats[record.posture] = {
            total_duration: 0,
            count: 0
          }
        }
        // 累加持续时间
        stats[record.posture].total_duration += record.duration
        
        // 只在姿势发生变化时增加计数
        if (lastPosture !== record.posture) {
          stats[record.posture].count += 1
          lastPosture = record.posture
        }
      })

      // 转换为数组格式并按持续时间排序
      return Object.entries(stats)
        .map(([posture_type, data]) => ({
          posture_type,
          total_duration: data.total_duration,
          count: data.count
        }))
        .sort((a, b) => b.total_duration - a.total_duration)
    }

    // 监听 historyData 变化
    watch(() => props.historyData, (newData) => {
      if (newData && newData.length > 0) {
        // 更新历史记录，只保留最近的50条记录
        historyRecords.value = newData.slice(-50)
        // 更新统计数据
        dailyStats.value = processHistoryData(newData)
        // 更新图表
        updateChart(dailyStats.value)
      }
    }, { immediate: true })

    // 监听 isMonitoring 变化
    watch(() => props.isMonitoring, (newValue) => {
      if (!newValue) {
        // 停止监测时清空数据
        historyRecords.value = []
        dailyStats.value = []
        if (chart.value) {
          chart.value.clear()
        }
      }
    })

    onMounted(() => {
      if (chartContainer.value) {
        chart.value = echarts.init(chartContainer.value)
        // 如果有初始数据，则显示
        if (props.historyData && props.historyData.length > 0) {
          historyRecords.value = props.historyData.slice(-50)
          dailyStats.value = processHistoryData(props.historyData)
          updateChart(dailyStats.value)
        }
      }
    })

    onUnmounted(() => {
      if (statsInterval) {
        clearInterval(statsInterval)
      }
      if (chart.value) {
        chart.value.dispose()
      }
    })

    return {
      dailyStats,
      historyRecords,
      formatDuration,
      chartContainer
    }
  }
}
</script>

<style scoped>
.posture-monitor {
  padding: 20px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.monitor-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.monitor-status {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 14px;
  background: #f5f5f5;
  color: #666;
}

.monitor-status.active {
  background: #e6f7e6;
  color: #4CAF50;
}

.statistics-section,
.chart-section,
.history-section {
  margin-bottom: 20px;
}

h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #333;
}

.statistics-table-container {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #eee;
  border-radius: 8px;
}

.statistics-table {
  width: 100%;
  border-collapse: collapse;
}

.statistics-table th,
.statistics-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.statistics-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
  position: sticky;
  top: 0;
  z-index: 1;
}

.statistics-table td {
  color: #666;
}

.statistics-table tr:last-child td {
  border-bottom: none;
}

.chart-container {
  height: 250px;
  margin: 10px 0;
}

.history-list {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #eee;
  border-radius: 8px;
}

.history-item {
  display: flex;
  padding: 12px;
  border-bottom: 1px solid #eee;
}

.history-item:last-child {
  border-bottom: none;
}

.history-time {
  width: 100px;
  color: #666;
}

.history-posture {
  flex: 1;
  color: #333;
}

.history-duration {
  width: 80px;
  text-align: right;
  color: #666;
}

.no-data {
  padding: 20px;
  text-align: center;
  color: #999;
}

/* 自定义滚动条样式 */
.statistics-table-container::-webkit-scrollbar,
.history-list::-webkit-scrollbar {
  width: 6px;
}

.statistics-table-container::-webkit-scrollbar-track,
.history-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.statistics-table-container::-webkit-scrollbar-thumb,
.history-list::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}

.statistics-table-container::-webkit-scrollbar-thumb:hover,
.history-list::-webkit-scrollbar-thumb:hover {
  background: #999;
}
</style> 