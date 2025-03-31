# Sleep Posture Detection System

基于 Vue.js 和 Python Flask 的睡眠姿势检测系统，实现了实时姿势监测、数据统计和可视化功能。

## 功能特点

- 实时视频流姿势检测
- 姿势数据统计和可视化
- 历史记录查询
- 数据库存储
- 响应式界面设计

## 技术栈

### 前端
- Vue.js 3
- ECharts
- Axios
- Vue Router

### 后端
- Python Flask
- OpenCV
- MediaPipe
- MySQL
- Flask-CORS

## 项目结构

```
sleep_posture_detection/
├── backend/                 # 后端代码
│   ├── camera_manager.py    # 相机管理模块
│   ├── posture_analyzer.py  # 姿势分析模块
│   ├── db_utils.py         # 数据库工具
│   └── posture_detect.py   # 主应用服务器
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/    # Vue组件
│   │   ├── views/        # 页面视图
│   │   ├── router/       # 路由配置
│   │   └── App.vue       # 主应用组件
│   ├── package.json      # 依赖配置
│   └── vite.config.js    # Vite配置
└── README.md             # 项目说明文档
```

## 安装说明

### 后端环境配置

1. 安装Python依赖：
```bash
pip install -r requirements.txt
```

2. 配置MySQL数据库：
```sql
CREATE DATABASE sleep_posture;
USE sleep_posture;
```

3. 启动后端服务：
```bash
cd backend
python posture_detect.py
```

### 前端环境配置

1. 安装Node.js依赖：
```bash
cd frontend
npm install
```

2. 启动开发服务器：
```bash
npm run dev
```

## 使用说明

1. 启动后端服务和前端开发服务器
2. 访问 `http://localhost:5173` 打开应用
3. 点击"开始监测"按钮开始姿势检测
4. 在界面上查看实时姿势数据和统计信息

## 注意事项

- 确保摄像头可用且权限正确
- MySQL服务需要正确配置并运行
- 后端服务默认运行在 `http://127.0.0.1:5000`
- 确保安装所有必要的Python包和Node.js依赖

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License 