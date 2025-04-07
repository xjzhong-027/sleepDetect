<template>
  <div class="article-detail">
    <!-- 顶栏 -->
    <div class="header">
      <button class="back-btn" @click="goBack">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </button>
      <h1 class="title">{{ article.title }}</h1>
    </div>

    <!-- 文章内容 -->
    <div class="content">
      <div class="article-meta">
        <span class="date">{{ article.date }}</span>
        <span class="author">{{ article.author }}</span>
      </div>
      
      <div class="article-body">
        <p v-for="(paragraph, index) in article.content" :key="index">{{ paragraph }}</p>
      </div>

      <div class="article-tips" v-if="article.tips">
        <h3>小贴士</h3>
        <ul>
          <li v-for="(tip, index) in article.tips" :key="index">{{ tip }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const articleId = route.params.id;

// 文章数据
const article = ref({
  title: '',
  date: '',
  author: '',
  content: [],
  tips: []
});

// 根据文章ID获取对应的文章内容
const getArticleContent = (id) => {
  const articles = {
    'improve-sleep': {
      title: '如何提高睡眠质量？',
      date: '2024-03-15',
      author: '睡眠专家',
      content: [
        '科学研究表明，良好的睡眠习惯对身心健康至关重要。现代人普遍存在睡眠问题，如何提高睡眠质量成为许多人关注的焦点。',
        '首先，建立规律的作息时间非常重要。每天尽量在同一时间上床睡觉和起床，这有助于调节生物钟。建议成年人保持7-9小时的睡眠时间。',
        '其次，创造良好的睡眠环境。保持卧室温度在18-22摄氏度之间，使用遮光窗帘，确保房间安静。选择舒适的床垫和枕头也很重要。',
        '睡前避免使用电子设备，因为蓝光会抑制褪黑素的分泌，影响入睡。建议睡前1小时停止使用手机、电脑等设备。',
        '适当的运动有助于改善睡眠质量，但要注意避免在睡前3小时内进行剧烈运动。可以选择瑜伽、散步等温和的运动方式。'
      ],
      tips: [
        '睡前可以喝一杯温牛奶，有助于放松身心',
        '使用香薰精油，如薰衣草，有助于促进睡眠',
        '睡前进行10-15分钟的冥想或深呼吸练习',
        '保持卧室通风，确保空气新鲜'
      ]
    },
    'sleep-emotion': {
      title: '睡眠与情绪的关系',
      date: '2024-03-14',
      author: '心理专家',
      content: [
        '睡眠与情绪之间存在着密切的关联。研究表明，睡眠不足会导致情绪波动、易怒、焦虑和抑郁等情绪问题。',
        '睡眠不足会影响大脑中负责情绪调节的区域，使人们更容易产生负面情绪。同时，情绪问题也会反过来影响睡眠质量，形成恶性循环。',
        '深度睡眠阶段对情绪调节尤为重要。在这个阶段，大脑会处理白天的情绪体验，帮助人们更好地应对压力。',
        '保持良好的睡眠习惯，可以帮助我们更好地管理情绪。建议每天保持规律的作息时间，创造舒适的睡眠环境。',
        '如果长期存在睡眠和情绪问题，建议及时寻求专业帮助。心理咨询和睡眠治疗可以有效地改善这些问题。'
      ],
      tips: [
        '睡前可以写日记，记录当天的情绪体验',
        '进行正念冥想，帮助放松身心',
        '保持规律的作息时间，有助于情绪稳定',
        '避免在睡前思考令人焦虑的问题'
      ]
    },
    'sleep-environment': {
      title: '打造理想睡眠环境',
      date: '2024-03-13',
      author: '环境专家',
      content: [
        '一个理想的睡眠环境对提高睡眠质量至关重要。合适的温度、光线和噪音控制，可以让睡眠更加舒适。',
        '温度是影响睡眠的重要因素。研究表明，人体在稍凉的环境中更容易入睡。建议将卧室温度控制在18-22摄氏度之间。',
        '光线对睡眠质量也有重要影响。黑暗的环境有助于促进褪黑素的分泌，帮助入睡。建议使用遮光窗帘，避免外界光线干扰。',
        '噪音控制同样重要。持续的噪音会干扰睡眠，建议使用耳塞或白噪音机来屏蔽外界噪音。',
        '卧室的空气质量也不容忽视。保持通风，使用空气净化器，确保空气新鲜。避免在卧室内吸烟或使用刺激性气味的物品。'
      ],
      tips: [
        '使用遮光窗帘，确保卧室足够黑暗',
        '选择舒适的床垫和枕头',
        '保持卧室通风，确保空气新鲜',
        '使用白噪音机或耳塞，减少噪音干扰'
      ]
    }
  };

  return articles[id] || articles['improve-sleep'];
};

// 返回上一页
const goBack = () => {
  router.back();
};

onMounted(() => {
  article.value = getArticleContent(articleId);
});
</script>

<style scoped>
.article-detail {
  width: 393px;
  min-height: 100vh;
  background: #FFFFFF;
  position: relative;
}

.header {
  width: 393px;
  height: 89px;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  padding: 0 20px;
  position: fixed;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.back-btn {
  background: none;
  border: none;
  padding: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-btn svg {
  width: 24px;
  height: 24px;
  color: #333;
}

.title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 0 10px;
  flex: 1;
  text-align: center;
}

.content {
  padding: 120px 20px 40px;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  color: #666;
  font-size: 14px;
}

.article-body {
  line-height: 1.8;
  color: #333;
  margin-bottom: 30px;
}

.article-body p {
  margin-bottom: 16px;
}

.article-tips {
  background: #F8F9FA;
  padding: 20px;
  border-radius: 12px;
  margin-top: 30px;
}

.article-tips h3 {
  color: #4CAF50;
  font-size: 16px;
  margin-bottom: 15px;
}

.article-tips ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.article-tips li {
  color: #666;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 10px;
  padding-left: 20px;
  position: relative;
}

.article-tips li::before {
  content: '•';
  color: #4CAF50;
  position: absolute;
  left: 0;
}
</style> 