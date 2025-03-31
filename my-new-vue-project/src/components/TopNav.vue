<template>
  <div class="header">
    <div v-if="showBack" class="back-button" @click="$router.go(-1)">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path d="M15 18L9 12L15 6" stroke="#333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    <h1>{{ title }}</h1>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  showBack: {
    type: Boolean,
    default: false
  }
});
</script>

<style scoped>
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
  flex: 1;
  text-align: center;
}
</style> 