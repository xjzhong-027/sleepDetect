<template>
    <div class="page-wrapper">
      <div class="emotiontest-container">
        <!-- 顶栏 -->
        <div class="header">
          <div class="back-button" @click="$router.go(-1)">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M15 18L9 12L15 6" stroke="#333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h1>情绪自测</h1>
        </div>
  
        <!-- 内容区域 -->
        <div class="content-wrapper">
          <!-- 测试说明 -->
          <div v-if="!started && !completed" class="test-intro">
            <div class="intro-card">
              <h2>情绪自测问卷</h2>
              <p>本问卷包含10个问题，用于评估您当前的情绪状态。请根据您的真实感受作答。</p>
              <button class="start-button" @click="startTest">开始测试</button>
            </div>
          </div>
  
          <!-- 测试题目 -->
          <div v-if="started && !completed" class="test-questions">
            <div class="progress-bar">
              <div class="progress" :style="{ width: `${(currentQuestionIndex + 1) * 10}%` }"></div>
            </div>
            <div class="question-card">
              <div class="question-number">问题 {{ currentQuestionIndex + 1 }}/10</div>
              <div class="question-text">{{ currentQuestion.text }}</div>
              <div class="options">
                <button 
                  v-for="(option, index) in currentQuestion.options" 
                  :key="index"
                  class="option-button"
                  @click="selectOption(index)"
                >
                  {{ option }}
                </button>
              </div>
            </div>
          </div>
  
          <!-- 测试结果 -->
          <div v-if="completed" class="test-result">
            <div class="result-card">
              <h2>测试完成</h2>
              <div class="score-circle">
                <div class="score">{{ totalScore }}</div>
                <div class="score-label">情绪指数</div>
              </div>
              <div class="result-analysis">
                <h3>情绪分析</h3>
                <p>{{ getEmotionAnalysis() }}</p>
              </div>
              <div class="suggestions">
                <h3>建议</h3>
                <p>{{ getSuggestions() }}</p>
              </div>
              <button class="restart-button" @click="restartTest">重新测试</button>
            </div>
          </div>
        </div>
  
        <!-- 底部导航 -->
        <BottomNav />
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue';
  import BottomNav from '../components/BottomNav.vue';
  
  const questions = [
    {
      text: "您最近一周的睡眠质量如何？",
      options: ["很差", "较差", "一般", "较好", "很好"],
      weights: [1, 2, 3, 4, 5]
    },
    {
      text: "您是否经常感到焦虑或紧张？",
      options: ["总是", "经常", "有时", "很少", "从不"],
      weights: [1, 2, 3, 4, 5]
    },
    {
      text: "您对日常活动的兴趣如何？",
      options: ["完全没有", "很少", "一般", "较多", "非常多"],
      weights: [1, 2, 3, 4, 5]
    },
    {
      text: "您是否容易感到疲劳？",
      options: ["总是", "经常", "有时", "很少", "从不"],
      weights: [1, 2, 3, 4, 5]
    },
    {
      text: "您的人际关系如何？",
      options: ["很差", "较差", "一般", "较好", "很好"],
      weights: [1, 2, 3, 4, 5]
    },
    {
      text: "您是否经常感到心情低落？",
      options: ["总是", "经常", "有时", "很少", "从不"],
      weights: [1, 2, 3, 4, 5]
    },
    {
      text: "您的工作或学习效率如何？",
      options: ["很差", "较差", "一般", "较好", "很好"],
      weights: [1, 2, 3, 4, 5]
    },
    {
      text: "您是否经常感到烦躁或易怒？",
      options: ["总是", "经常", "有时", "很少", "从不"],
      weights: [1, 2, 3, 4, 5]
    },
    {
      text: "您对未来是否充满希望？",
      options: ["完全没有", "很少", "一般", "较多", "非常多"],
      weights: [1, 2, 3, 4, 5]
    },
    {
      text: "您是否经常感到孤独？",
      options: ["总是", "经常", "有时", "很少", "从不"],
      weights: [1, 2, 3, 4, 5]
    }
  ];
  
  const started = ref(false);
  const completed = ref(false);
  const currentQuestionIndex = ref(0);
  const answers = ref([]);
  const totalScore = ref(0);
  const scoreDetails = ref(null);
  
  const currentQuestion = computed(() => questions[currentQuestionIndex.value]);
  
  const startTest = () => {
    started.value = true;
    answers.value = [];
    currentQuestionIndex.value = 0;
  };
  
  const selectOption = (optionIndex) => {
    answers.value.push(optionIndex);
    if (currentQuestionIndex.value < questions.length - 1) {
      currentQuestionIndex.value++;
    } else {
      calculateScore();
      completed.value = true;
    }
  };
  
  const calculateScore = () => {
    // 计算原始分数（1-5分每题，共10题，最高50分）
    const rawScore = answers.value.reduce((sum, answerIndex, questionIndex) => {
      return sum + questions[questionIndex].weights[answerIndex];
    }, 0);
    
    // 获取昨日分数（模拟数据，实际应从后端获取）
    const yesterdayScore = 75; // 示例昨日分数
    
    // 获取昨夜情绪数据（模拟数据，实际应从后端获取）
    const emotionData = {
      happy: 0.6,    // 60%的时间是开心的
      neutral: 0.3,  // 30%的时间是平静的
      sad: 0.1       // 10%的时间是难过的
    };
    
    // 计算基础分数（将50分转换为100分制）
    const baseScore = Math.round((rawScore / 50) * 100);
    
    // 计算历史影响（昨日分数占30%权重）
    const historicalInfluence = yesterdayScore * 0.3;
    
    // 计算情绪影响（开心情绪占比越高，加分越多，最高加10分）
    const emotionBonus = emotionData.happy * 10;
    
    // 计算最终分数（基础分数占70% + 历史影响30% + 情绪加分）
    let finalScore = (baseScore * 0.7) + historicalInfluence + emotionBonus;
    
    // 确保分数在合理范围内（60-90分）
    finalScore = Math.max(60, Math.min(90, finalScore));
    
    // 四舍五入到整数
    totalScore.value = Math.round(finalScore);
    
    // 保存分数详情用于显示
    scoreDetails.value = {
      baseScore,
      historicalInfluence,
      emotionBonus,
      finalScore: totalScore.value,
      emotionData
    };
  };
  
  const getEmotionAnalysis = () => {
    if (totalScore.value <= 70) {
      return "您的情绪状态需要关注，但请记住这是暂时的。建议多与亲友交流，保持积极的心态。";
    } else if (totalScore.value <= 80) {
      return "您的情绪状态良好，继续保持当前的生活节奏。记住，保持稳定的情绪状态比追求高分更重要。";
    } else {
      return "您的情绪状态非常好，继续保持这种积极的状态。但也要注意，情绪波动是正常的，不必给自己太大压力。";
    }
  };
  
  const getSuggestions = () => {
    if (totalScore.value <= 70) {
      return "1. 保持规律的作息时间，充足的睡眠很重要\n2. 适当进行户外活动，呼吸新鲜空气\n3. 与亲友保持联系，分享您的感受\n4. 培养积极的兴趣爱好，转移注意力\n5. 如果感到不适，及时寻求专业帮助";
    } else if (totalScore.value <= 80) {
      return "1. 继续保持良好的生活习惯\n2. 记录每天的小确幸，培养感恩之心\n3. 保持适度运动，释放压力\n4. 维持社交活动，保持人际联系\n5. 学会接纳自己的情绪，不必过分追求完美";
    } else {
      return "1. 继续保持乐观积极的心态\n2. 分享您的积极经验，帮助他人\n3. 保持适度运动，维持良好状态\n4. 持续关注心理健康，预防为主\n5. 记住，情绪波动是正常的，不必给自己太大压力";
    }
  };
  
  const restartTest = () => {
    started.value = false;
    completed.value = false;
    currentQuestionIndex.value = 0;
    answers.value = [];
    totalScore.value = 0;
  };
  </script>
  
  <style scoped>
  .page-wrapper {
    width: 393px;
    margin: 0 auto;
    min-height: 100vh;
    background: #FFFFFF;
  }
  
  .emotiontest-container {
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
    left: 0;
    right: 0;
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
  
  .content-wrapper {
    width: 393px;
    margin: 0 auto;
    padding-top: 89px;
  }
  
  .intro-card, .question-card, .result-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 20px;
    margin: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  }
  
  .test-intro h2 {
    font-size: 24px;
    color: #333;
    margin-bottom: 16px;
    text-align: center;
  }
  
  .test-intro p {
    font-size: 16px;
    color: #666;
    line-height: 1.6;
    margin-bottom: 24px;
    text-align: center;
  }
  
  .start-button {
    width: 200px;
    height: 50px;
    border: none;
    border-radius: 25px;
    background-color: #4CAF50;
    color: white;
    font-size: 16px;
    cursor: pointer;
    display: block;
    margin: 0 auto;
    transition: background-color 0.3s;
  }
  
  .start-button:hover {
    background-color: #45a049;
  }
  
  .progress-bar {
    width: 100%;
    height: 4px;
    background: #f0f0f0;
    margin: 20px 0;
    border-radius: 2px;
  }
  
  .progress {
    height: 100%;
    background: #4CAF50;
    border-radius: 2px;
    transition: width 0.3s ease;
  }
  
  .question-number {
    font-size: 14px;
    color: #666;
    margin-bottom: 12px;
  }
  
  .question-text {
    font-size: 18px;
    color: #333;
    margin-bottom: 24px;
    line-height: 1.5;
  }
  
  .options {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  
  .option-button {
    background: #f8f9fa;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 12px;
    font-size: 16px;
    color: #333;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .option-button:hover {
    background: #e9ecef;
    transform: translateY(-2px);
  }
  
  .score-circle {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    background: linear-gradient(135deg, #389BFF 0%, #20BBC0 100%);
    color: white;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    margin: 20px auto;
  }
  
  .score {
    font-size: 48px;
    font-weight: bold;
  }
  
  .score-label {
    font-size: 16px;
    opacity: 0.9;
  }
  
  .result-analysis, .suggestions {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 20px;
    margin: 20px 0;
    text-align: left;
  }
  
  .result-analysis h3, .suggestions h3 {
    font-size: 18px;
    color: #333;
    margin-bottom: 12px;
  }
  
  .result-analysis p, .suggestions p {
    font-size: 16px;
    color: #666;
    line-height: 1.6;
    white-space: pre-line;
  }
  
  .restart-button {
    width: 200px;
    height: 50px;
    border: none;
    border-radius: 25px;
    background-color: #4CAF50;
    color: white;
    font-size: 16px;
    cursor: pointer;
    display: block;
    margin: 20px auto 0;
    transition: background-color 0.3s;
  }
  
  .restart-button:hover {
    background-color: #45a049;
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
    
    .content-wrapper {
      width: 100%;
    }
    
    .intro-card, .question-card, .result-card {
      margin: 10px;
    }
    
    .question-text {
      font-size: 16px;
    }
    
    .option-button {
      font-size: 14px;
    }
    
    .score-circle {
      width: 120px;
      height: 120px;
    }
    
    .score {
      font-size: 36px;
    }
  }
  </style> 