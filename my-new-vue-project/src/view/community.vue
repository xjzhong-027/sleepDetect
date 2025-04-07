<template>
  <div class="community-container">
    <!-- 顶部导航栏 -->
    <div class="header">
      <div class="back-button" @click="goBack">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </div>
      <h1>社区分享</h1>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-section">
      <div class="search-box">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"/>
          <path d="M21 21l-4.35-4.35"/>
        </svg>
        <input type="text" placeholder="搜索用户或话题">
      </div>
      <div class="filter-tags">
        <span class="tag active">全部</span>
        <span class="tag">优质睡眠</span>
        <span class="tag">睡眠问题</span>
        <span class="tag">经验分享</span>
      </div>
    </div>

    <!-- 分享列表 -->
    <div class="share-list">
      <div v-for="share in shareList" :key="share.id" class="share-card">
        <div class="user-info">
          <div class="avatar-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
          </div>
          <div class="user-details">
            <h3>{{ share.user.name }}</h3>
            <p>{{ share.user.time }}</p>
          </div>
        </div>
        <div class="sleep-data">
          <div class="data-item">
            <span class="label">睡眠评分</span>
            <span class="value">{{ share.sleepData.score }}</span>
          </div>
          <div class="data-item">
            <span class="label">睡眠时长</span>
            <span class="value">{{ share.sleepData.duration }}</span>
          </div>
          <div class="data-item">
            <span class="label">睡眠质量</span>
            <span class="value">{{ share.sleepData.quality }}%</span>
          </div>
        </div>
        <div class="share-content">
          <p>{{ share.content }}</p>
        </div>
        <div class="share-tags">
          <span v-for="tag in share.tags" :key="tag" class="tag">{{ tag }}</span>
        </div>
        <div class="actions">
          <button class="action-btn" @click="likeShare(share)">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" :class="{ 'liked-heart': share.isLiked }" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
            </svg>
            <span :class="{ 'liked': share.isLiked }">{{ share.likes }}</span>
          </button>
          <button class="action-btn" @click="toggleComments(share)">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
            <span>{{ share.comments }}</span>
          </button>
        </div>

        <!-- 评论区域 -->
        <div class="comments-section" v-if="share.showComments">
          <!-- 评论列表 -->
          <div class="comment-list" v-if="share.commentList?.length">
            <div v-for="comment in share.commentList" :key="comment.id" class="comment-item">
              <div class="user-info">
                <div class="avatar-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                  </svg>
                </div>
                <div class="user-details">
                  <h3>{{ comment.user.name }}</h3>
                  <p>{{ comment.user.time }}</p>
                </div>
              </div>
              <div class="comment-content">
                <p>{{ comment.content }}</p>
              </div>
            </div>
          </div>
          <div v-else class="no-comments">
            暂无评论
          </div>

          <!-- 评论输入框 -->
          <div class="comment-input">
            <textarea v-model="share.newComment" 
                      placeholder="写下你的评论..." 
                      rows="2"></textarea>
            <button class="send-btn" @click="addComment(share)" :disabled="!share.newComment?.trim()">
              发送
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 发布评论按钮 -->
    <div class="publish-btn" @click="showPublishModal = true">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 5v14M5 12h14"/>
      </svg>
    </div>

    <!-- 发布评论模态框 -->
    <div class="modal" v-if="showPublishModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>发布分享</h2>
          <button class="close-btn" @click="showPublishModal = false">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>
        
        <div class="modal-body">
          <!-- 选择历史报告数据 -->
          <div class="report-selector">
            <h3>选择历史报告数据</h3>
            <div class="report-list">
              <div v-for="report in historyReports" :key="report.date" 
                   class="report-item" 
                   :class="{ 'selected': selectedReport?.date === report.date }"
                   @click="selectReport(report)">
                <div class="report-date">{{ report.date }}</div>
                <div class="report-data">
                  <span>评分: {{ report.score }}</span>
                  <span>时长: {{ report.duration }}</span>
                  <span>质量: {{ report.quality }}%</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 评论内容输入 -->
          <div class="comment-input">
            <h3>分享内容</h3>
            <textarea v-model="commentContent" 
                      placeholder="分享你的睡眠体验..." 
                      rows="4"></textarea>
          </div>

          <!-- 标签选择 -->
          <div class="tag-selector">
            <h3>选择标签</h3>
            <div class="tag-list">
              <span v-for="tag in availableTags" 
                    :key="tag" 
                    class="tag" 
                    :class="{ 'active': selectedTags.includes(tag) }"
                    @click="toggleTag(tag)">
                {{ tag }}
              </span>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="cancel-btn" @click="showPublishModal = false">取消</button>
          <button class="publish-btn" @click="publishComment" :disabled="!canPublish">发布</button>
        </div>
      </div>
    </div>

    <!-- 底部导航 -->
    <BottomNav />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import BottomNav from '../components/BottomNav.vue';
import { ref, computed } from 'vue';

const router = useRouter();
const showPublishModal = ref(false);
const showCommentModal = ref(false);
const commentContent = ref('');
const selectedTags = ref([]);
const selectedReport = ref(null);
const selectedShare = ref(null);
const newComment = ref('');

// 模拟历史报告数据
const historyReports = ref([
  { date: '2024-04-01', score: 92, duration: '8小时15分', quality: 95 },
  { date: '2024-04-02', score: 85, duration: '7小时30分', quality: 90 },
  { date: '2024-04-03', score: 78, duration: '6小时45分', quality: 85 },
  { date: '2024-04-04', score: 88, duration: '7小时15分', quality: 92 }
]);

const availableTags = ['优质睡眠', '睡眠问题', '经验分享', '睡姿调整', '情绪管理'];

const canPublish = computed(() => {
  return commentContent.value.trim() && selectedReport.value;
});

const goBack = () => {
  router.back();
};

const selectReport = (report) => {
  selectedReport.value = report;
};

const toggleTag = (tag) => {
  const index = selectedTags.value.indexOf(tag);
  if (index === -1) {
    selectedTags.value.push(tag);
  } else {
    selectedTags.value.splice(index, 1);
  }
};

// 修改分享列表数据，添加点赞状态
const shareList = ref([
  {
    id: 1,
    user: {
      name: '睡眠达人',
      avatar: '',
      time: '2小时前'
    },
    sleepData: {
      score: 92,
      duration: '8小时15分',
      quality: 95
    },
    content: '昨晚的睡眠质量非常好！使用了睡姿检测功能，发现侧卧姿势最适合我。情绪检测显示睡前状态很放松，这可能是睡眠质量好的原因之一。',
    likes: 128,
    comments: 32,
    tags: ['优质睡眠', '经验分享'],
    showComments: false,
    commentList: [],
    newComment: '',
    isLiked: false // 添加点赞状态
  },
  {
    id: 2,
    user: {
      name: '夜猫子',
      avatar: '',
      time: '5小时前'
    },
    sleepData: {
      score: 75,
      duration: '6小时45分',
      quality: 85
    },
    content: '昨晚睡得不太好，声音检测显示有几次被噪音惊醒。情绪检测显示睡前有些焦虑，这可能影响了睡眠质量。需要调整一下作息时间了。',
    likes: 64,
    comments: 18,
    tags: ['睡眠问题'],
    isLiked: false
  },
  {
    id: 3,
    user: {
      name: '早睡早起',
      avatar: '',
      time: '昨天'
    },
    sleepData: {
      score: 85,
      duration: '7小时30分',
      quality: 90
    },
    content: '使用了夜间唤醒检测功能，发现自己在凌晨3点左右有一次短暂的清醒。睡姿检测显示大部分时间保持仰卧姿势，这可能有助于提高睡眠质量。',
    likes: 96,
    comments: 24,
    tags: ['经验分享', '睡姿调整'],
    isLiked: false
  }
]);

// 修改点赞功能
const likeShare = (share) => {
  if (share.isLiked) {
    // 取消点赞
    share.likes -= 1;
    share.isLiked = false;
  } else {
    // 点赞
    share.likes += 1;
    share.isLiked = true;
  }
};

// 显示/隐藏评论
const toggleComments = (share) => {
  share.showComments = !share.showComments;
  if (!share.commentList) {
    share.commentList = [];
  }
  if (!share.newComment) {
    share.newComment = '';
  }
};

// 修改发布评论函数，添加点赞状态
const publishComment = () => {
  if (!canPublish.value) return;

  // 创建新的分享
  const newShare = {
    id: shareList.value.length + 1,
    user: {
      name: '我',
      avatar: '',
      time: '刚刚'
    },
    sleepData: {
      score: selectedReport.value.score,
      duration: selectedReport.value.duration,
      quality: selectedReport.value.quality
    },
    content: commentContent.value,
    likes: 0,
    comments: 0,
    tags: selectedTags.value,
    isLiked: false // 添加点赞状态
  };

  // 将新分享添加到列表开头
  shareList.value.unshift(newShare);

  // 清空表单
  commentContent.value = '';
  selectedTags.value = [];
  selectedReport.value = null;
  showPublishModal.value = false;
};

// 添加评论
const addComment = (share) => {
  if (!share.newComment?.trim()) return;

  // 创建新评论
  const comment = {
    id: Date.now(),
    user: {
      name: '我',
      avatar: '',
      time: '刚刚'
    },
    content: share.newComment
  };

  // 添加评论
  share.commentList.unshift(comment);
  share.comments += 1;

  // 清空评论输入
  share.newComment = '';
};
</script>

<style scoped>
.community-container {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 84px;
}

.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  z-index: 100;
}

.back-button {
  display: flex;
  align-items: center;
  margin-right: 15px;
  cursor: pointer;
}

.header h1 {
  font-size: 18px;
  margin: 0;
  color: #333;
}

.search-section {
  margin-top: 80px;
  padding: 15px;
  background: white;
}

.search-box {
  display: flex;
  align-items: center;
  background: #f5f5f5;
  border-radius: 20px;
  padding: 8px 15px;
  margin-bottom: 15px;
}

.search-box input {
  border: none;
  background: none;
  margin-left: 10px;
  width: 100%;
  outline: none;
}

.filter-tags {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 5px;
}

.tag {
  padding: 5px 15px;
  background: #f5f5f5;
  border-radius: 15px;
  font-size: 14px;
  white-space: nowrap;
}

.tag.active {
  background: #4CAF50;
  color: white;
}

.share-list {
  padding: 15px;
}

.share-card {
  background: white;
  border-radius: 12px;
  padding: 15px;
  margin-bottom: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.user-info {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.avatar-icon {
  width: 40px;
  height: 40px;
  border-radius: 20px;
  background: #E8F5E9;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
}

.avatar-icon svg {
  color: #4CAF50;
  font-size: 24px;
}

.user-details h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.user-details p {
  margin: 5px 0 0;
  font-size: 12px;
  color: #999;
}

.sleep-data {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 8px;
}

.data-item {
  text-align: center;
}

.data-item .label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.data-item .value {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.share-content {
  margin-bottom: 15px;
}

.share-content p {
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
  color: #333;
}

.actions {
  display: flex;
  gap: 20px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  background: none;
  border: none;
  color: #666;
  font-size: 14px;
  cursor: pointer;
}

.action-btn svg {
  color: #666;
  transition: all 0.3s;
}

.action-btn .liked {
  color: #ff4d4f;
}

.liked-heart {
  fill: #ff4d4f !important;
  color: #ff4d4f !important;
}

.back-button svg {
  color: #333;
}

.search-box svg {
  color: #666;
}

/* 发布按钮样式 */
.publish-btn {
  position: fixed;
  right: 20px;
  bottom: 100px;
  width: 56px;
  height: 56px;
  border-radius: 28px;
  background: #4CAF50;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  z-index: 10;
}

/* 模态框样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  padding: 15px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
}

.modal-body {
  padding: 15px;
}

/* 报告选择器样式 */
.report-selector {
  margin-bottom: 20px;
}

.report-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 10px;
}

.report-item {
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 8px;
  cursor: pointer;
}

.report-item.selected {
  border-color: #4CAF50;
  background: #E8F5E9;
}

.report-date {
  font-weight: 500;
  margin-bottom: 5px;
}

.report-data {
  display: flex;
  gap: 15px;
  font-size: 14px;
  color: #666;
}

/* 评论输入框样式 */
.comment-input {
  margin-bottom: 20px;
}

.comment-input textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 8px;
  resize: none;
  margin-top: 10px;
}

/* 标签选择器样式 */
.tag-selector {
  margin-bottom: 20px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

/* 模态框底部按钮 */
.modal-footer {
  padding: 15px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.modal-footer button {
  padding: 8px 20px;
  border-radius: 20px;
  border: none;
  cursor: pointer;
}

.cancel-btn {
  background: #f5f5f5;
  color: #666;
}

.publish-btn {
  background: #4CAF50;
  color: white;
}

.publish-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.share-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 15px;
}

.share-tags .tag {
  padding: 4px 12px;
  background: #E8F5E9;
  color: #4CAF50;
  border-radius: 12px;
  font-size: 12px;
}

/* 评论区域样式 */
.comments-section {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.comment-list {
  margin-bottom: 15px;
}

.comment-item {
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-content {
  margin-top: 5px;
  margin-left: 50px;
}

.comment-content p {
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
  color: #333;
}

.no-comments {
  text-align: center;
  color: #999;
  padding: 10px;
  font-size: 14px;
}

/* 评论输入框样式 */
.comment-input {
  display: flex;
  gap: 10px;
  align-items: flex-end;
  margin-top: 10px;
}

.comment-input textarea {
  flex: 1;
  padding: 8px;
  border: 1px solid #eee;
  border-radius: 8px;
  resize: none;
  font-size: 14px;
}

.send-btn {
  padding: 6px 15px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 15px;
  cursor: pointer;
  font-size: 14px;
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style> 