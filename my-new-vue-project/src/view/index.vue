<template>
  <div class="page">
    <!-- 顶栏 -->
    <div class="header">
      <h1 class="title">你的专属睡眠平台</h1>
    </div>

    <!-- Banner -->
    <div class="banner">
      <div class="banner-content">
        <h2>智能睡眠监测</h2>
        <p>AI驱动的睡眠质量分析，让每一晚都睡得更好</p>
      </div>
    </div>

    <!-- 使用人数 -->
    <div class="user-count">
      <span>全国正有 2,356 人正在使用</span>
    </div>

    <!-- 睡眠科普文章 -->
    <div class="articles">
      <div class="article-card">
        <h3>如何提高睡眠质量？</h3>
        <p>科学研究表明，良好的睡眠习惯对身心健康至关重要...</p>
      </div>
      <div class="article-card">
        <h3>睡眠与情绪的关系</h3>
        <p>充足的睡眠能够有效改善情绪，提升生活质量...</p>
      </div>
      <div class="article-card">
        <h3>打造理想睡眠环境</h3>
        <p>合适的温度、光线和噪音控制，让睡眠更加舒适...</p>
      </div>
    </div>

    <!-- 底部导航 -->
    <BottomNav />
  </div>
</template>

<script setup>
import BottomNav from '../components/BottomNav.vue';
</script>

<style scoped>
.page {
  width: 393px;
  height: 852px;
  background: #FFFFFF;
  position: relative;
  overflow-y: auto;
  padding-bottom: 84px; /* 为底部导航留出空间 */
}

.header {
  width: 393px;
  height: 89px;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  position: fixed;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.title {
  font-size: 20px;
  font-weight: 600;
  color: #333333;
  margin: 0;
}

.banner {
  width: 393px;
  height: 196px;
  background: linear-gradient(135deg, #389BFF 0%, #20BBC0 100%);
  margin-top: 89px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  text-align: center;
  padding: 20px;
}

.banner-content h2 {
  font-size: 24px;
  margin-bottom: 10px;
}

.banner-content p {
  font-size: 16px;
  opacity: 0.9;
}

.user-count {
  width: 393px;
  height: 58px;
  background: #F8F9FA;
  display: flex;
  align-items: center;
  padding: 0 20px;
  font-size: 14px;
  color: #666666;
}

.articles {
  width: 393px;
  height: 406px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.article-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.article-card h3 {
  font-size: 16px;
  color: #333333;
  margin: 0 0 8px 0;
}

.article-card p {
  font-size: 14px;
  color: #666666;
  margin: 0;
  line-height: 1.5;
}
</style>