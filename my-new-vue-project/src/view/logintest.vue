<template>
    <div>
      <!-- 注册表单 -->
      <form @submit.prevent="register">
        <h2>注册</h2>
        <input v-model="registerUsername" placeholder="用户名" />
        <input v-model="registerPassword" type="password" placeholder="密码" />
        <input v-model="registerEmail" placeholder="邮箱" />
        <button type="submit">注册</button>
      </form>
  
      <!-- 登录表单 -->
      <form @submit.prevent="login">
        <h2>登录</h2>
        <input v-model="loginUsername" placeholder="用户名" />
        <input v-model="loginPassword" type="password" placeholder="密码" />
        <button type="submit">登录</button>
      </form>
    </div>
</template>
  
<script setup>
  import { ref } from 'vue';
  import axios from 'axios';
  
  // 注册表单数据
  const registerUsername = ref('');
  const registerPassword = ref('');
  const registerEmail = ref('');
  
  // 登录表单数据
  const loginUsername = ref('');
  const loginPassword = ref('');
  
  // 注册方法
  const register = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:5000/register', {
        username: registerUsername.value,
        password: registerPassword.value,
        email: registerEmail.value
      });
      console.log(response.data.message);
      // 可根据后端返回结果进行相应处理，如提示用户注册成功
    } catch (error) {
      console.error(error.response.data.message);
      // 处理注册失败情况，如显示错误提示
    }
  };
  
  // 登录方法
  const login = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:5000/login', {
        username: loginUsername.value,
        password: loginPassword.value
      });
      console.log(response.data.message);
      // 处理登录成功情况，如跳转到用户主页
    } catch (error) {
      console.error(error.response.data.message);
      // 处理登录失败情况，如显示错误提示
    }
  };
</script>