<template>
    <div class="page">
      <!-- 这里放置登录页面的具体内容，比如表单等 -->
       <div class="login-container">
            <h2 class="login_text">登录</h2>
            <div class="input-form"><input class="username" type="text" id="username" placeholder="请输入用户名"></div>
            
            <div class="input-form"><input class="password" type="password" id="password" placeholder="请输入密码"></div>
            <div class="input-form"><input class='test' v></div>
            <div class="button-container">
                <button class="login-button">立即登录</button>
                <button class="signup-button">注册</button>
            </div>
            
      </div>
    </div>
    
  </template>
  
 
  
  <style scoped>
  .page {
    width: 1440px;
    height: 1024px; /* 使背景框高度占满整个视口高度 */
    background: linear-gradient(180deg, #389BFF 0%, #F0F0F1 97%);
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .login-container{
    position: absolute;
    left:358px;
    top:238px;
    width:734px;
    height:573px;
    border-radius: 17px;
    display: flex;
    flex-direction: column;
    border: 1px solid #000000;
  }
  .login-text{
    position: absolute;
    left: 326px;
    top: 59px;
    width: 72px;
    height: 52px;
    font-family: Source Han Sans;
    font-size: 36px;
    font-weight: normal;
    line-height: normal;
    letter-spacing: 0em;
    font-variation-settings: "opsz" auto;
    color: #3D3D3D;
  }
  .password{
    width: 482px;
    height: 72px;
    background: linear-gradient(to right, #87CEEB, #90EE90);;
    border-radius: 13px;
  }
  .username{
    width: 482px;
    height: 72px;
    background: linear-gradient(to bottom, #FFC0CB, #D8BFD8);;
    border: 1px solid ;
    border-radius: 13px;
  }
  .input-form{
    margin-top: 40px;
  }
  .input-form input::placeholder {
  color: #000000; /* 设置占位符文本颜色 */
  font-style: italic; /* 设置占位符文本为斜体 */
  font-size: 14px; /* 设置占位符文本大小 */
}
.button-container{
    display: flex;
    flex-direction: row;
    margin-top:87px;
}
.login-button {
  width: 300px;
  padding: 10px;
  background-color: #389BFF;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 16px;
  margin-left: 134px;
  margin-right:49px;
}

.login-button:hover {
  background-color: #1e73be;
}
.signup-button{

    opacity: 1;
    background: #A5CEF7;
}
  </style>