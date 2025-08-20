// 强化学习可视化工具 - JavaScript核心功能
let socket;
let isDragMode = false;
let draggedElement = null;
let dragOffset = { x: 0, y: 0 };
let originalPositions = {};
let isMonitoring = false;
let barChart, lineChart;
let startTime = null;
let timerInterval = null;

// 显示通知
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// 初始化Socket连接
function initSocket() {
    try {
        socket = io();
        
        socket.on('connect', function() {
            document.getElementById('statusIndicator').className = 'status-indicator status-active';
            document.getElementById('statusText').textContent = '已连接';
            console.log('Socket连接成功');
            showNotification('Socket连接成功', 'success');
        });

        socket.on('disconnect', function() {
            document.getElementById('statusIndicator').className = 'status-indicator status-inactive';
            document.getElementById('statusText').textContent = '连接断开';
            console.log('Socket连接断开');
            showNotification('Socket连接断开', 'error');
        });

        socket.on('data_update', function(data) {
            updateCharts(data.training_data);
            updatePhysicsModel(data.physics_data);
        });

        socket.on('monitoring_started', function(data) {
            console.log('监控已启动:', data);
            showNotification('监控已启动！', 'success');
        });

        socket.on('connect_error', function(error) {
            console.error('Socket连接错误:', error);
            document.getElementById('statusIndicator').className = 'status-indicator status-inactive';
            document.getElementById('statusText').textContent = '连接失败';
            showNotification('Socket连接失败', 'error');
        });

    } catch (error) {
        console.error('初始化Socket失败:', error);
        showNotification('初始化Socket失败', 'error');
    }
}

// 启动监控
function startMonitoring() {
    console.log('启动监控按钮被点击');
    
    if (isMonitoring) {
        showNotification('监控已在运行中', 'error');
        return;
    }

    try {
        fetch('/api/start_monitoring', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                frequency: 10
            })
        })
        .then(response => {
            console.log('API响应状态:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('API响应数据:', data);
            if (data.success) {
                isMonitoring = true;
                document.getElementById('startBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
                document.getElementById('systemStatus').textContent = '监控中';
                showNotification('监控启动成功！', 'success');
                startTimer();
            } else {
                showNotification('监控启动失败: ' + (data.message || '未知错误'), 'error');
            }
        })
        .catch(error => {
            console.error('启动监控失败:', error);
            showNotification('启动监控失败: ' + error.message, 'error');
        });
    } catch (error) {
        console.error('启动监控异常:', error);
        showNotification('启动监控异常: ' + error.message, 'error');
    }
}

// 停止监控
function stopMonitoring() {
    console.log('停止监控按钮被点击');
    
    if (!isMonitoring) {
        showNotification('监控未在运行', 'error');
        return;
    }

    try {
        fetch('/api/stop_monitoring', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                isMonitoring = false;
                document.getElementById('startBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
                document.getElementById('systemStatus').textContent = '待机';
                showNotification('监控已停止', 'success');
                stopTimer();
            } else {
                showNotification('停止监控失败: ' + (data.message || '未知错误'), 'error');
            }
        })
        .catch(error => {
            console.error('停止监控失败:', error);
            showNotification('停止监控失败: ' + error.message, 'error');
        });
    } catch (error) {
        console.error('停止监控异常:', error);
        showNotification('停止监控异常: ' + error.message, 'error');
    }
}

// 计时器相关
function startTimer() {
    startTime = Date.now();
    timerInterval = setInterval(updateTimer, 1000);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

function updateTimer() {
    if (startTime) {
        const elapsed = Date.now() - startTime;
        const hours = Math.floor(elapsed / 3600000);
        const minutes = Math.floor((elapsed % 3600000) / 60000);
        const seconds = Math.floor((elapsed % 60000) / 1000);
        
        document.getElementById('runTime').textContent = 
            `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
}

// 拖拽功能
function toggleDragMode() {
    isDragMode = !isDragMode;
    const btn = document.getElementById('dragBtn');
    
    if (isDragMode) {
        btn.textContent = '🔒 锁定模式';
        btn.style.background = 'linear-gradient(135deg, #ef4444, #dc2626, #b91c1c)';
        showNotification('拖拽模式已启用', 'success');
    } else {
        btn.textContent = '🖱️ 拖拽模式';
        btn.style.background = 'linear-gradient(135deg, #3b82f6, #1d4ed8, #1e40af)';
        showNotification('拖拽模式已禁用', 'success');
    }
}

// 重置布局
function resetLayout() {
    const modules = document.querySelectorAll('.draggable-module');
    modules.forEach(module => {
        const moduleId = module.dataset.module;
        if (originalPositions[moduleId]) {
            module.style.left = originalPositions[moduleId].left;
            module.style.top = originalPositions[moduleId].top;
        }
    });
    showNotification('布局已重置', 'success');
}

// 保存原始位置
function saveOriginalPositions() {
    const modules = document.querySelectorAll('.draggable-module');
    modules.forEach(module => {
        const moduleId = module.dataset.module;
        const rect = module.getBoundingClientRect();
        const container = document.getElementById('fabLayout').getBoundingClientRect();
        
        originalPositions[moduleId] = {
            left: module.style.left || (rect.left - container.left) + 'px',
            top: module.style.top || (rect.top - container.top) + 'px'
        };
    });
}

// 初始化拖拽事件
function initDragEvents() {
    const modules = document.querySelectorAll('.draggable-module');
    
    modules.forEach(module => {
        module.addEventListener('mousedown', handleMouseDown);
    });
    
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
}

function handleMouseDown(e) {
    if (!isDragMode) return;
    
    draggedElement = e.target.closest('.draggable-module');
    if (!draggedElement) return;
    
    e.preventDefault();
    
    const rect = draggedElement.getBoundingClientRect();
    const container = document.getElementById('fabLayout').getBoundingClientRect();
    
    dragOffset.x = e.clientX - rect.left;
    dragOffset.y = e.clientY - rect.top;
    
    draggedElement.classList.add('dragging');
}

function handleMouseMove(e) {
    if (!draggedElement || !isDragMode) return;
    
    e.preventDefault();
    
    const container = document.getElementById('fabLayout').getBoundingClientRect();
    
    let newX = e.clientX - container.left - dragOffset.x;
    let newY = e.clientY - container.top - dragOffset.y;
    
    // 边界检查
    newX = Math.max(0, Math.min(newX, container.width - draggedElement.offsetWidth));
    newY = Math.max(0, Math.min(newY, container.height - draggedElement.offsetHeight));
    
    draggedElement.style.left = newX + 'px';
    draggedElement.style.top = newY + 'px';
}

function handleMouseUp(e) {
    if (draggedElement) {
        draggedElement.classList.remove('dragging');
        draggedElement = null;
    }
}

// 初始化图表
function initCharts() {
    // 柱状图 - 显示数值标签
    const barCtx = document.getElementById('barChart').getContext('2d');
    barChart = new Chart(barCtx, {
        type: 'bar',
        data: {
            labels: ['奖励', '损失', '效率'],
            datasets: [{
                label: '训练指标',
                data: [0, 0, 0],
                backgroundColor: [
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(245, 158, 11, 0.8)'
                ],
                borderColor: [
                    'rgba(59, 130, 246, 1)',
                    'rgba(239, 68, 68, 1)',
                    'rgba(245, 158, 11, 1)'
                ],
                borderWidth: 2,
                yAxisID: 'y'
            }, {
                label: '成功率 (%)',
                data: [0],
                backgroundColor: 'rgba(16, 185, 129, 0.8)',
                borderColor: 'rgba(16, 185, 129, 1)',
                borderWidth: 2,
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#f1f5f9',
                        usePointStyle: true,
                        padding: 20
                    }
                },
                datalabels: {
                    display: true,
                    color: '#f1f5f9',
                    font: {
                        weight: 'bold'
                    },
                    formatter: function(value, context) {
                        return Math.round(value * 100) / 100;
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '训练指标',
                        color: '#cbd5e1'
                    },
                    ticks: {
                        color: '#cbd5e1'
                    },
                    grid: {
                        color: 'rgba(203, 213, 225, 0.2)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: '成功率 (%)',
                        color: '#10b981'
                    },
                    ticks: {
                        color: '#10b981'
                    },
                    grid: {
                        drawOnChartArea: false,
                    }
                },
                x: {
                    ticks: {
                        color: '#cbd5e1'
                    },
                    grid: {
                        color: 'rgba(203, 213, 225, 0.2)'
                    }
                }
            }
        }
    });

    // 折线图 - 双Y轴设计
    const lineCtx = document.getElementById('lineChart').getContext('2d');
    lineChart = new Chart(lineCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '奖励值',
                data: [],
                borderColor: 'rgba(59, 130, 246, 1)',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.4,
                yAxisID: 'y',
                pointRadius: 3,
                pointHoverRadius: 6
            }, {
                label: '损失值',
                data: [],
                borderColor: 'rgba(239, 68, 68, 1)',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                tension: 0.4,
                yAxisID: 'y',
                pointRadius: 3,
                pointHoverRadius: 6
            }, {
                label: '成功率 (%)',
                data: [],
                borderColor: 'rgba(16, 185, 129, 1)',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4,
                yAxisID: 'y1',
                pointRadius: 3,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#f1f5f9',
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += Math.round(context.parsed.y * 100) / 100;
                                if (context.dataset.label.includes('成功率')) {
                                    label += '%';
                                }
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: '奖励/损失值',
                        color: '#cbd5e1'
                    },
                    ticks: {
                        color: '#cbd5e1'
                    },
                    grid: {
                        color: 'rgba(203, 213, 225, 0.2)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    min: 0,
                    max: 100,
                    title: {
                        display: true,
                        text: '成功率 (%)',
                        color: '#10b981'
                    },
                    ticks: {
                        color: '#10b981',
                        callback: function(value) {
                            return value + '%';
                        }
                    },
                    grid: {
                        drawOnChartArea: false,
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '训练轮次',
                        color: '#cbd5e1'
                    },
                    ticks: {
                        color: '#cbd5e1'
                    },
                    grid: {
                        color: 'rgba(203, 213, 225, 0.2)'
                    }
                }
            }
        }
    });
}

// 更新图表数据
function updateCharts(trainingData) {
    if (!trainingData) return;

    // 更新柱状图 - 双Y轴设计
    if (barChart && trainingData.rewards && trainingData.rewards.length > 0) {
        const latest = trainingData.rewards.length - 1;
        
        // 左侧Y轴数据：奖励、损失、效率
        barChart.data.datasets[0].data = [
            Math.round((trainingData.rewards[latest] || 0) * 100) / 100,
            Math.round((trainingData.losses[latest] || 0) * 100) / 100,
            Math.round((trainingData.efficiency[latest] || 0) * 100) / 100
        ];
        
        // 右侧Y轴数据：成功率（百分比）
        barChart.data.datasets[1].data = [
            Math.round((trainingData.success_rates[latest] || 0) * 100) / 100
        ];
        
        // 更新成功率标签位置
        barChart.data.labels = ['奖励', '损失', '效率', '成功率'];
        
        barChart.update('none');
    }

    // 更新折线图 - 三条线，双Y轴
    if (lineChart && trainingData.episodes) {
        const maxPoints = 50; // 显示最近50个数据点
        const episodes = trainingData.episodes.slice(-maxPoints);
        
        lineChart.data.labels = episodes;
        
        // 左侧Y轴：奖励值和损失值
        lineChart.data.datasets[0].data = trainingData.rewards ? 
            trainingData.rewards.slice(-maxPoints).map(val => Math.round(val * 100) / 100) : [];
        lineChart.data.datasets[1].data = trainingData.losses ? 
            trainingData.losses.slice(-maxPoints).map(val => Math.round(val * 100) / 100) : [];
        
        // 右侧Y轴：成功率（百分比）
        lineChart.data.datasets[2].data = trainingData.success_rates ? 
            trainingData.success_rates.slice(-maxPoints).map(val => Math.round(val * 100) / 100) : [];
        
        lineChart.update('none');
    }
}

// 更新物理模型
function updatePhysicsModel(physicsData) {
    if (!physicsData) return;

    // 更新腔室状态
    if (physicsData.pm_chambers) {
        Object.keys(physicsData.pm_chambers).forEach(chamberId => {
            const chamber = physicsData.pm_chambers[chamberId];
            const element = document.getElementById(chamberId.toLowerCase());
            if (element) {
                element.className = element.className.replace(/chamber-\w+/, `chamber-${chamber.status}`);
            }
        });
    }

    // 更新统计信息
    if (physicsData.active_wafers !== undefined) {
        document.getElementById('activeWafers').textContent = physicsData.active_wafers;
    }
    if (physicsData.processing_chambers !== undefined) {
        document.getElementById('processingChambers').textContent = physicsData.processing_chambers;
    }
    if (physicsData.throughput !== undefined) {
        document.getElementById('throughput').textContent = physicsData.throughput + ' WPH';
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('页面加载完成，开始初始化...');
    
    // 注册Chart.js数据标签插件
    if (typeof ChartDataLabels !== 'undefined') {
        Chart.register(ChartDataLabels);
        console.log('数据标签插件已注册');
    }
    
    // 初始化各个组件
    initSocket();
    initCharts();
    initDragEvents();
    saveOriginalPositions();
    
    // 设置初始状态
    document.getElementById('stopBtn').disabled = true;
    
    console.log('初始化完成');
    showNotification('系统初始化完成 - 支持双Y轴显示和数值标签', 'success');
});
