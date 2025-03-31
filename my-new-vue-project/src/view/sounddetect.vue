.sounddetect-container {
  width: 100%;
  min-height: 100vh;
  background: #FFFFFF;
  position: relative;
  overflow-y: auto;
  padding-bottom: 84px; /* 为底部导航留出空间 */
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
  flex: 1;
  text-align: center;
}

.camera-container {
  width: 100%;
  max-width: 393px;
  height: 300px;
  margin-top: 89px;
  background: #f8f9fa;
  overflow: hidden;
  position: relative;
}

.camera-feed {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.data-container {
  width: 100%;
  max-width: 393px;
  display: flex;
  padding: 15px;
  gap: 15px;
  background: #ffffff;
  margin: 0 auto;
}

.data-item {
  flex: 1;
  background: #f8f9fa;
  border-radius: 12px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.data-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.data-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.control-container {
  width: 100%;
  max-width: 393px;
  display: flex;
  justify-content: center;
  margin: 20px auto;
  padding: 0 15px;
  box-sizing: border-box;
  position: sticky;
  bottom: 84px;
  background: #ffffff;
}

.control-button {
  width: 200px;
  height: 50px;
  border: none;
  border-radius: 25px;
  background-color: #4CAF50;
  color: white;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.control-button.monitoring {
  background-color: #f44336;
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
  .camera-container,
  .data-container,
  .control-container {
    max-width: 100%;
  }
  
  .data-item {
    padding: 10px;
  }
  
  .data-value {
    font-size: 20px;
  }
} 