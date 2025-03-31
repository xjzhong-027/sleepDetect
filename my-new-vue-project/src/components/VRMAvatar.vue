<!-- VRM虚拟形象组件 -->
<template>
  <div class="vrm-container" ref="vrmContainer">
    <canvas ref="vrmCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { VRMLoaderPlugin, VRMUtils } from '@pixiv/three-vrm';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

const props = defineProps({
  poseData: {
    type: Object,
    default: () => ({})
  }
});

const vrmContainer = ref(null);
const vrmCanvas = ref(null);
let scene, camera, renderer, vrm, mixer, controls;
let currentAction = null;

// 初始化Three.js场景
const initScene = () => {
  // 创建场景
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf0f2f5);

  // 创建相机
  camera = new THREE.PerspectiveCamera(
    30,
    vrmContainer.value.clientWidth / vrmContainer.value.clientHeight,
    0.1,
    1000
  );
  camera.position.set(0, 1, 3);

  // 创建渲染器
  renderer = new THREE.WebGLRenderer({
    canvas: vrmCanvas.value,
    antialias: true
  });
  renderer.setSize(vrmContainer.value.clientWidth, vrmContainer.value.clientHeight);
  renderer.setPixelRatio(window.devicePixelRatio);

  // 添加轨道控制
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.screenSpacePanning = true;

  // 添加光源
  const light = new THREE.DirectionalLight(0xffffff);
  light.position.set(1, 1, 1).normalize();
  scene.add(light);
  scene.add(new THREE.AmbientLight(0xffffff, 0.5));

  // 加载VRM模型
  loadVRM();

  // 开始动画循环
  animate();
};

// 加载VRM模型
const loadVRM = async () => {
  const loader = new GLTFLoader();
  loader.register((parser) => new VRMLoaderPlugin(parser));

  try {
    // 更新为你的模型路径
    const gltf = await loader.loadAsync('/model1.vrm');
    vrm = gltf.userData.vrm;
    
    // 初始化VRM
    VRMUtils.rotateVRM0(vrm);
    scene.add(vrm.scene);

    // 调整模型位置和缩放
    vrm.scene.position.set(0, -1, 0); // 降低模型位置以适应视图
    vrm.scene.scale.set(1.5, 1.5, 1.5); // 调整模型大小
    
    // 设置相机位置以更好地查看模型
    camera.position.set(0, 1, 3);
    controls.target.set(0, 1, 0);
    controls.update();
    
    // 创建动画混合器
    mixer = new THREE.AnimationMixer(vrm.scene);
    
  } catch (error) {
    console.error('VRM加载失败:', error);
  }
};

// 更新姿势
const updatePose = (poseData) => {
  if (!vrm || !vrm.humanoid) return;

  try {
    const { landmarks } = poseData;
    if (!landmarks) return;

    // 获取关键点
    const nose = new THREE.Vector3(...landmarks[0]);
    const leftShoulder = new THREE.Vector3(...landmarks[11]);
    const rightShoulder = new THREE.Vector3(...landmarks[12]);
    const leftHip = new THREE.Vector3(...landmarks[23]);
    const rightHip = new THREE.Vector3(...landmarks[24]);
    const leftElbow = new THREE.Vector3(...landmarks[13]);
    const rightElbow = new THREE.Vector3(...landmarks[14]);
    const leftWrist = new THREE.Vector3(...landmarks[15]);
    const rightWrist = new THREE.Vector3(...landmarks[16]);

    // 计算身体方向
    const spineVector = new THREE.Vector3()
      .subVectors(
        new THREE.Vector3().addVectors(leftShoulder, rightShoulder).multiplyScalar(0.5),
        new THREE.Vector3().addVectors(leftHip, rightHip).multiplyScalar(0.5)
      ).normalize();

    // 更新骨骼旋转
    // 头部旋转
    const headRotation = new THREE.Euler(
      Math.atan2(nose.y - leftShoulder.y, Math.abs(nose.z - leftShoulder.z)) * 2,
      Math.atan2(nose.x - leftShoulder.x, Math.abs(nose.z - leftShoulder.z)) * 2,
      0
    );
    vrm.humanoid.getNormalizedBoneNode('head').rotation.copy(headRotation);

    // 脊柱旋转
    const spineRotation = new THREE.Euler(
      Math.atan2(spineVector.y, Math.abs(spineVector.z)) * 1.5,
      Math.atan2(spineVector.x, Math.abs(spineVector.z)) * 1.5,
      0
    );
    vrm.humanoid.getNormalizedBoneNode('spine').rotation.copy(spineRotation);

    // 左臂旋转
    const leftArmRotation = calculateLimbRotation(leftShoulder, leftElbow, leftWrist);
    vrm.humanoid.getNormalizedBoneNode('leftUpperArm').rotation.copy(leftArmRotation);

    // 右臂旋转
    const rightArmRotation = calculateLimbRotation(rightShoulder, rightElbow, rightWrist);
    vrm.humanoid.getNormalizedBoneNode('rightUpperArm').rotation.copy(rightArmRotation);

  } catch (error) {
    console.error('更新姿势失败:', error);
  }
};

// 计算肢体旋转
const calculateLimbRotation = (joint1, joint2, joint3) => {
  const v1 = new THREE.Vector3().subVectors(joint2, joint1);
  const v2 = new THREE.Vector3().subVectors(joint3, joint2);
  
  const angle = v1.angleTo(v2);
  const axis = new THREE.Vector3().crossVectors(v1, v2).normalize();
  
  const quaternion = new THREE.Quaternion().setFromAxisAngle(axis, angle);
  return new THREE.Euler().setFromQuaternion(quaternion);
};

// 动画循环
const animate = () => {
  requestAnimationFrame(animate);
  
  if (mixer) {
    mixer.update(0.016); // 假设60fps
  }
  
  if (controls) {
    controls.update();
  }
  
  if (vrm) {
    vrm.update(0.016);
  }
  
  renderer.render(scene, camera);
};

// 处理窗口大小变化
const handleResize = () => {
  if (!camera || !renderer || !vrmContainer.value) return;
  
  camera.aspect = vrmContainer.value.clientWidth / vrmContainer.value.clientHeight;
  camera.updateProjectionMatrix();
  
  renderer.setSize(
    vrmContainer.value.clientWidth,
    vrmContainer.value.clientHeight
  );
};

// 监听姿势数据变化
watch(() => props.poseData, (newPoseData) => {
  updatePose(newPoseData);
}, { deep: true });

// 组件挂载时初始化
onMounted(() => {
  initScene();
  window.addEventListener('resize', handleResize);
});

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  if (renderer) {
    renderer.dispose();
  }
  if (scene) {
    scene.traverse((object) => {
      if (object.geometry) {
        object.geometry.dispose();
      }
      if (object.material) {
        if (Array.isArray(object.material)) {
          object.material.forEach((material) => material.dispose());
        } else {
          object.material.dispose();
        }
      }
    });
  }
});
</script>

<style scoped>
.vrm-container {
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