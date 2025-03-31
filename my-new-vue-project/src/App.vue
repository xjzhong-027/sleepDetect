<script setup>

</script>

<template>
  <div class="app-container">
    <div class="page-container">
      <router-view></router-view>
    </div>
  </div>
</template>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: #f5f5f5;
}

.app-container {
  width: 100%;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  background: #f5f5f5;
}

.page-container {
  width: 100%;
  max-width: 393px;
  min-height: 100vh;
  background: #FFFFFF;
  position: relative;
  overflow-y: auto;
  padding-bottom: 84px;
  margin: 0 auto;
}

/* 全局响应式样式 */
@media screen and (max-width: 393px) {
  .page-container {
    max-width: 100%;
  }
  
  .container {
    max-width: 100%;
  }
  
  .data-item {
    padding: 10px;
  }
  
  .data-value {
    font-size: 20px;
  }
  
  .analysis-header {
    font-size: 14px;
  }
  
  .item-label,
  .item-value {
    font-size: 12px;
  }
  
  .posture-types h3 {
    font-size: 16px;
  }
  
  .posture-type h4 {
    font-size: 14px;
  }
  
  .posture-type p {
    font-size: 12px;
  }
}
</style>
