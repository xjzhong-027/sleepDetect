// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import IndexComponent from '../view/index.vue'
import SounddetectComponent from '../components/sounddetect.vue';
import LoginComponent from '../view/login.vue'
import LoginTestComponent from '../view/logintest.vue'
import DetectComponent from '../view/detect.vue';

const routes = [
  {
    path: '/',
    name: 'Index',
    component: IndexComponent
  },
  {
    path: '/posturedetect',
    name: 'Posturedetect',
    component: () => import('../view/posturedetect.vue')
  },
  {
    path: '/index',
    name: 'IndexOld',
    component: IndexComponent
  },
  {
    path: '/sounddetect',
    name: 'Sounddetect',
    component: SounddetectComponent
  },
  {
    path:'/login',
    name: 'Login',
    component: LoginComponent
  },
  {
    path:'/logintest',
    name:'Logintest',
    component:LoginTestComponent
  },
  {
    path:'/detect',
    name:'Detect',
    component:DetectComponent
  },
  {
    path: '/daily-report',
    name: 'DailyReport',
    component: () => import('../view/daily-report.vue')
  },
  {
    path: '/report',
    name: 'Report',
    component: () => import('../view/report.vue')
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../view/profile.vue')
  },
  {
    path: '/device',
    name: 'Device',
    component: () => import('../view/device.vue')
  },
  {
    path: '/emotiondetect',
    name: 'Emotiondetect',
    component: () => import('../view/emotiondetect.vue')
  },
  {
    path: '/emotiontest',
    name: 'Emotiontest',
    component: () => import('../view/emotiontest.vue')
  },
  {
    path: '/nightwake',
    name: 'Nightwake',
    component: () => import('../view/nightwake.vue')
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;