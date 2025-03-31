<!-- Live2D 虚拟形象组件 -->
<template>
  <div class="live2d-container" ref="live2dContainer">
    <canvas ref="live2dCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { Application } from '@cubism/framework';
import { Live2DModel } from 'pixi-live2d-display';
import * as PIXI from 'pixi.js';

const props = defineProps({
  poseData: {
    type: Object,
    default: () => ({})
  }
});

const live2dContainer = ref(null);
const live2dCanvas = ref(null);
let app = null;
let model = null;

// 姿势映射参数
const POSE_PARAMS = {
  ParamAngleX: { min: -30, max: 30 }, // 头部左右转动
  ParamAngleY: { min: -30, max: 30 }, // 头部上下转动
  ParamAngleZ: { min: -30, max: 30 }, // 头部倾斜
  ParamBodyAngleX: { min: -10, max: 10 }, // 身体左右移动
  ParamBodyAngleY: { min: -10, max: 10 }, // 身体前后移动
  ParamBodyAngleZ: { min: -10, max: 10 }, // 身体倾斜
};

// 初始化Live2D
const initLive2D = async () => {
  try {
    // 初始化PIXI应用
    app = new PIXI.Application({
      view: live2dCanvas.value,
      transparent: true,
      autoStart: true,
      width: live2dContainer.value.clientWidth,
      height: live2dContainer.value.clientHeight
    });

    // 加载模型
    // 注意：这里需要替换为你的Live2D模型路径
    const modelPath = '/models/your-model/model.json';
    model = await Live2DModel.from(modelPath);

    // 调整模型大小和位置
    model.scale.set(0.5);
    model.anchor.set(0.5, 0.5);
    model.position.set(
      app.renderer.width / 2,
      app.renderer.height / 2
    );

    // 添加到舞台
    app.stage.addChild(model);

  } catch (error) {
    console.error('Live2D初始化失败:', error);
  }
};

// 更新模型姿势
const updatePose = (poseData) => {
  if (!model) return;

  try {
    // 从MediaPipe姿势数据映射到Live2D参数
    const { landmarks } = poseData;
    if (!landmarks) return;

    // 计算头部角度
    const nose = landmarks[0];
    const leftEye = landmarks[2];
    const rightEye = landmarks[5];
    const leftShoulder = landmarks[11];
    const rightShoulder = landmarks[12];

    // 计算头部旋转角度
    const faceCenter = {
      x: (leftEye.x + rightEye.x) / 2,
      y: (leftEye.y + rightEye.y) / 2
    };
    
    // 计算头部左右转动
    const angleX = Math.atan2(nose.x - faceCenter.x, nose.z || 0.1) * 180 / Math.PI;
    model.internalModel.coreModel.setParameterValueById(
      'ParamAngleX',
      angleX * 2 // 放大效果
    );

    // 计算头部上下转动
    const angleY = Math.atan2(nose.y - faceCenter.y, nose.z || 0.1) * 180 / Math.PI;
    model.internalModel.coreModel.setParameterValueById(
      'ParamAngleY',
      -angleY * 2 // 放大效果，注意Y轴方向相反
    );

    // 计算身体倾斜
    const bodyAngleZ = Math.atan2(
      rightShoulder.y - leftShoulder.y,
      rightShoulder.x - leftShoulder.x
    ) * 180 / Math.PI;
    model.internalModel.coreModel.setParameterValueById(
      'ParamBodyAngleZ',
      bodyAngleZ
    );

  } catch (error) {
    console.error('更新姿势失败:', error);
  }
};

// 监听姿势数据变化
watch(() => props.poseData, (newPoseData) => {
  updatePose(newPoseData);
}, { deep: true });

// 组件挂载时初始化
onMounted(async () => {
  await initLive2D();
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize);
});

// 组件卸载时清理
onUnmounted(() => {
  if (app) {
    app.destroy(true);
  }
  window.removeEventListener('resize', handleResize);
});

// 处理窗口大小变化
const handleResize = () => {
  if (app && live2dContainer.value) {
    app.renderer.resize(
      live2dContainer.value.clientWidth,
      live2dContainer.value.clientHeight
    );
    if (model) {
      model.position.set(
        app.renderer.width / 2,
        app.renderer.height / 2
      );
    }
  }
};
</script>

<style scoped>
.live2d-container {
  width: 100%;
  height: 100%;
  position: relative;
}

canvas {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
}
</style> 