<template>
    <div class="dream-recorder">
        <h2>梦话录音</h2>
        <button @click="toggleMonitoring" :disabled="isPausing === monitoring">
            {{ monitoring ? (isPausing ? '恢复监测' : '暂停监测') : '开始监测' }}
        </button>
        <span>当前声贝量：{{ currentVolume.toFixed(2) }} dB</span>
        <span>最大声贝量：{{ maxVolume.toFixed(2) }} dB</span>
        <span>{{ recordingStatus }}</span>
        <!-- 展示所有录制的音频 -->
        <div v-for="(url, index) in audioUrls" :key="index">
            <audio :src="url" controls></audio>
            <a :href="url" :download="'dream_talk_' + index + '.webm'">下载梦话音频 {{ index + 1 }}</a>
        </div>
        <canvas ref="chartRef" width="400" height="200"></canvas>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { Chart, LineController, LineElement, CategoryScale, LinearScale, PointElement } from 'chart.js';

// 注册所需的控制器和元素
Chart.register(LineController, LineElement, CategoryScale, LinearScale, PointElement);

const monitoring = ref(true); // 初始化为开始监测
const recording = ref(false);
const audioUrls = ref([]); // 存储所有录音的 URL
const recordingStatus = ref('未监测到声音');
const currentVolume = ref(0); // 用于存储当前声贝量
const maxVolume = ref(-Infinity); // 用于存储最大声贝量
const isPausing = ref(false); // 新增状态变量，用于控制是否暂停监测
const chartRef = ref(null);
const volumeData = ref([]); // 存储音量数据和时间戳
let mediaRecorder = null;
let audioChunks = [];
let audioContext = null;
let analyser = null;
let source = null;
let silenceTimer = null;
let chartInstance = null;
let volumeCheckInterval = null; // 用于存储 setInterval 的返回值
const RECORD_THRESHOLD = 30; // 开始录音的声贝阈值
const STOP_THRESHOLD = 25; // 停止录音的声贝阈值
const SILENCE_DURATION = 2000; // 无声持续时间（毫秒），可根据实际情况调整

// 开始监测周围声音
const startMonitoring = async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        source = audioContext.createMediaStreamSource(stream);
        source.connect(analyser);

        analyser.fftSize = 2048;
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        const checkVolume = () => {
            if (isPausing.value) {
                return;
            }

            analyser.getByteFrequencyData(dataArray);
            let sum = 0;
            for (let i = 0; i < bufferLength / 2; i++) {
                sum += dataArray[i];
            }
            const average = sum / (bufferLength / 2);
            const volume = 20 * Math.log10(average / 255); // 转换为 dB
            currentVolume.value = volume; // 更新当前声贝量

            // 更新最大声贝量
            if (volume > maxVolume.value) {
                maxVolume.value = volume;
            }

            // 记录音量数据和时间戳
            volumeData.value.push({
                time: new Date().toLocaleTimeString(),
                volume
            });

            if (volume > RECORD_THRESHOLD &&!recording.value) {
                startRecording(stream);
                recordingStatus.value = '自动录音已开启';
            } else if (volume <= STOP_THRESHOLD && recording.value) {
                if (!silenceTimer) {
                    silenceTimer = setTimeout(() => {
                        stopRecording();
                        recordingStatus.value = '自动录音已停止';
                        silenceTimer = null;
                    }, SILENCE_DURATION);
                }
            } else if (volume > STOP_THRESHOLD && recording.value) {
                if (silenceTimer) {
                    clearTimeout(silenceTimer);
                    silenceTimer = null;
                }
            }

            // 更新图表数据
            if (chartInstance) {
                chartInstance.data.labels = volumeData.value.map(item => item.time);
                chartInstance.data.datasets[0].data = volumeData.value.map(item => item.volume);
                chartInstance.update();
            }
        };

        // 每秒执行一次音量检测
        volumeCheckInterval = setInterval(checkVolume, 1000);
    } catch (error) {
        console.error("访问麦克风失败:", error);
        recordingStatus.value = "访问麦克风失败，请检查权限设置。";
    }
};

// 开始录音
const startRecording = (stream) => {
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
            audioChunks.push(event.data);
        }
    };

    mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
        const url = URL.createObjectURL(audioBlob);
        audioUrls.value.push(url);
    };

    mediaRecorder.start();
    recording.value = true;
};

// 停止录音
const stopRecording = () => {
    if (mediaRecorder) {
        mediaRecorder.stop();
        recording.value = false;
    }
};

// 切换监测状态
const toggleMonitoring = () => {
    isPausing.value =!isPausing.value;
    if (!isPausing.value &&!monitoring.value) {
        startMonitoring();
        monitoring.value = true;
    }
};

onMounted(() => {
    try {
        startMonitoring();
        // 初始化图表
        if (chartRef.value) {
            chartInstance = new Chart(chartRef.value, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: '噪声分贝量',
                        data: [],
                        borderColor: 'blue',
                        backgroundColor: 'rgba(0, 0, 255, 0.1)',
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: '时间'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: '分贝量'
                            }
                        }
                    }
                }
            });
        } else {
            console.error("未找到 canvas 元素");
        }
    } catch (error) {
        console.error("mounted 钩子执行出错:", error);
    }
});

onUnmounted(() => {
    if (chartInstance) {
        chartInstance.destroy();
    }
    if (volumeCheckInterval) {
        clearInterval(volumeCheckInterval);
    }
});
</script>

<style scoped>
.dream-recorder {
    text-align: center;
    padding: 20px;
}

audio {
    margin: 10px;
}

a {
    display: block;
    margin-bottom: 20px;
}
</style>