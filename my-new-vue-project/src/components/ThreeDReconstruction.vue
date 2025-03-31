<template>
  <div class="reconstruction-container" ref="container"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

const props = defineProps({
  landmarks: {
    type: Object,
    default: () => null
  }
});

const container = ref(null);
let scene, camera, renderer, controls;
let humanModel, bedModel, jointSpheres = [];

// 初始化Three.js场景
const initThreeJS = () => {
  // 创建场景
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf0f0f0);

  // 创建相机
  camera = new THREE.PerspectiveCamera(
    45,
    container.value.clientWidth / container.value.clientHeight,
    0.1,
    1000
  );
  camera.position.set(0, 3, 0); // 设置相机位置在正上方
  camera.lookAt(0, 0, 0); // 相机朝向床的中心

  // 创建渲染器
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(container.value.clientWidth, container.value.clientHeight);
  renderer.shadowMap.enabled = true;
  container.value.appendChild(renderer.domElement);

  // 添加轨道控制器（禁用旋转，只允许平移和缩放）
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.minDistance = 2;
  controls.maxDistance = 4;
  controls.enableRotate = false; // 禁用旋转
  controls.target.set(0, 0, 0);

  // 添加环境光和方向光
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
  scene.add(ambientLight);

  const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
  directionalLight.position.set(0, 4, 0);
  directionalLight.castShadow = true;
  scene.add(directionalLight);

  // 创建床模型
  createBed();

  // 开始动画循环
  animate();
};

// 创建床模型
const createBed = () => {
  // 创建床的几何体
  const bedGeometry = new THREE.BoxGeometry(1.2, 0.1, 2);
  const bedMaterial = new THREE.MeshPhongMaterial({ color: 0x8b4513 });
  bedModel = new THREE.Mesh(bedGeometry, bedMaterial);
  bedModel.position.y = 0;
  bedModel.receiveShadow = true;
  scene.add(bedModel);

  // 添加床垫
  const mattressGeometry = new THREE.BoxGeometry(1.1, 0.05, 1.9);
  const mattressMaterial = new THREE.MeshPhongMaterial({ color: 0xd3d3d3 });
  const mattress = new THREE.Mesh(mattressGeometry, mattressMaterial);
  mattress.position.y = 0.075;
  mattress.receiveShadow = true;
  scene.add(mattress);

  // 添加床脚
  const legGeometry = new THREE.CylinderGeometry(0.02, 0.02, 0.3);
  const legMaterial = new THREE.MeshPhongMaterial({ color: 0x8b4513 });
  const positions = [
    [-0.55, -0.15, -0.95],
    [0.55, -0.15, -0.95],
    [-0.55, -0.15, 0.95],
    [0.55, -0.15, 0.95]
  ];

  positions.forEach(pos => {
    const leg = new THREE.Mesh(legGeometry, legMaterial);
    leg.position.set(...pos);
    leg.castShadow = true;
    scene.add(leg);
  });
};

// 创建关节球体
const createJointSphere = (position) => {
  const geometry = new THREE.SphereGeometry(0.02);
  const material = new THREE.MeshPhongMaterial({ color: 0x00ff00 });
  const sphere = new THREE.Mesh(geometry, material);
  sphere.position.copy(position);
  sphere.castShadow = true;
  return sphere;
};

// 更新人体模型
const updateHumanModel = (landmarks) => {
  // 清除之前的人体模型和关节球体
  if (humanModel) {
    scene.remove(humanModel);
  }
  jointSpheres.forEach(sphere => scene.remove(sphere));
  jointSpheres = [];

  if (!landmarks) return;

  // 创建人体骨架的几何体
  const geometry = new THREE.BufferGeometry();
  const material = new THREE.LineBasicMaterial({ color: 0x00ff00, linewidth: 2 });
  
  // 定义关键点连接
  const connections = [
    // 躯干
    [11, 12], // 肩膀
    [23, 24], // 臀部
    [11, 23], // 左侧躯干
    [12, 24], // 右侧躯干
    // 手臂
    [11, 13], [13, 15], // 左臂
    [12, 14], [14, 16], // 右臂
    // 腿
    [23, 25], [25, 27], // 左腿
    [24, 26], [26, 28], // 右腿
    // 头部
    [0, 11], [0, 12], // 头部到肩膀
  ];

  const positions = [];
  const processedPoints = new Set();

  // 添加关键点连接
  connections.forEach(([start, end]) => {
    if (landmarks[start] && landmarks[end]) {
      // 调整坐标系统
      const startPos = new THREE.Vector3(
        landmarks[start][0] - 0.5,
        -landmarks[start][1] + 1,
        -landmarks[start][2]
      );
      const endPos = new THREE.Vector3(
        landmarks[end][0] - 0.5,
        -landmarks[end][1] + 1,
        -landmarks[end][2]
      );

      positions.push(
        startPos.x, startPos.y, startPos.z,
        endPos.x, endPos.y, endPos.z
      );

      // 为每个未处理的关键点创建关节球体
      if (!processedPoints.has(start)) {
        const sphere = createJointSphere(startPos);
        scene.add(sphere);
        jointSpheres.push(sphere);
        processedPoints.add(start);
      }
      if (!processedPoints.has(end)) {
        const sphere = createJointSphere(endPos);
        scene.add(sphere);
        jointSpheres.push(sphere);
        processedPoints.add(end);
      }
    }
  });

  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  humanModel = new THREE.LineSegments(geometry, material);
  humanModel.castShadow = true;
  scene.add(humanModel);
};

// 动画循环
const animate = () => {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
};

// 处理窗口大小变化
const handleResize = () => {
  if (!container.value) return;
  
  camera.aspect = container.value.clientWidth / container.value.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.value.clientWidth, container.value.clientHeight);
};

// 监听landmarks变化
watch(() => props.landmarks, (newLandmarks) => {
  if (newLandmarks) {
    updateHumanModel(newLandmarks);
  }
}, { deep: true });

onMounted(() => {
  initThreeJS();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  if (renderer) {
    renderer.dispose();
  }
  if (container.value) {
    container.value.innerHTML = '';
  }
});
</script>

<style scoped>
.reconstruction-container {
  width: 100%;
  height: 100%;
  background: #f0f0f0;
}
</style> 