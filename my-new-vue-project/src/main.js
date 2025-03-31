import { createApp } from 'vue';
import './style.css';
import './assets/styles/icons.css';  // 添加图标样式
import App from './App.vue';
import router from './router'; // 引入路由实例
import '@fortawesome/fontawesome-free/css/all.css';

const app = createApp(App);
app.use(router); // 使用路由
app.mount('#app');