/**
 * 数据可视化组件
 * 使用 Chart.js 展示统计数据
 */

// 全局图表实例
let charts = {};

/**
 * 初始化统计概览图表
 */
function initOverviewCharts(stats) {
    // 基础数据统计饼图
    const basicDataCtx = document.getElementById('basicDataChart');
    if (basicDataCtx) {
        const dataLabels = {
            'campuses': '校区',
            'teachers': '教师',
            'students': '学生',
            'classes': '班级',
            'classrooms': '教室',
            'courses': '课程'
        };
        
        const colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#E91E63', '#00BCD4'];
        
        const data = Object.keys(stats).map((key, index) => ({
            label: dataLabels[key] || key,
            value: stats[key],
            color: colors[index % colors.length]
        })).filter(d => d.value > 0);
        
        if (data.length > 0) {
            createPieChart('basicDataChart', data);
        }
    }
    
    // 选课统计
    const selectionStatsCtx = document.getElementById('selectionStatsChart');
    if (selectionStatsCtx) {
        loadSelectionStats();
    }
}

/**
 * 创建饼图
 */
function createPieChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    // 销毁已有图表
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }
    
    charts[canvasId] = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.map(d => d.label),
            datasets: [{
                data: data.map(d => d.value),
                backgroundColor: data.map(d => d.color),
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1) + '%';
                            return `${label}: ${value} (${percentage})`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * 创建柱状图
 */
function createBarChart(canvasId, labels, values, title, color = '#4CAF50') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    // 销毁已有图表
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }
    
    charts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: values,
                backgroundColor: color,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

/**
 * 加载选课统计
 */
function loadSelectionStats() {
    fetch('/api/stats/selection')
        .then(response => response.json())
        .then(result => {
            if (result.success && result.data) {
                renderSelectionStats(result.data);
            }
        })
        .catch(error => console.error('加载选课统计失败:', error));
}

/**
 * 渲染选课统计图表
 */
function renderSelectionStats(stats) {
    // 按科目统计 - 柱状图
    if (stats.by_subject && Object.keys(stats.by_subject).length > 0) {
        const subjects = Object.keys(stats.by_subject);
        const counts = Object.values(stats.by_subject);
        createBarChart('subjectStatsChart', subjects, counts, '选课人数', '#2196F3');
    }
    
    // 更新总数显示
    const totalEl = document.getElementById('totalSelections');
    if (totalEl) {
        totalEl.textContent = stats.total || 0;
    }
}

/**
 * 显示加载状态
 */
function showLoading(elementId) {
    const el = document.getElementById(elementId);
    if (el) {
        el.innerHTML = '<div class="loading-spinner"><div class="spinner"></div><p>加载中...</p></div>';
    }
}

/**
 * 隐藏加载状态
 */
function hideLoading(elementId) {
    const el = document.getElementById(elementId);
    if (el) {
        const spinner = el.querySelector('.loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    }
}

/**
 * 显示错误信息
 */
function showError(message, elementId) {
    const el = document.getElementById(elementId);
    if (el) {
        el.innerHTML = `<div class="error-message">${message}</div>`;
    }
}

/**
 * 显示成功提示
 */
function showSuccess(message) {
    const toast = document.createElement('div');
    toast.className = 'toast toast-success';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * 显示错误提示
 */
function showToastError(message) {
    const toast = document.createElement('div');
    toast.className = 'toast toast-error';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * 格式化日期时间
 */
function formatDateTime(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * 导出表格为 Excel
 */
function exportTableToExcel(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    // 这里可以添加实际的导出逻辑
    // 或者调用后端 API 进行导出
    window.location.href = `/api/export/${filename}`;
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 加载概览统计
    const statsEl = document.getElementById('overviewStats');
    if (statsEl) {
        fetch('/api/stats/overview')
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    initOverviewCharts(result.data);
                }
            })
            .catch(error => {
                console.error('加载统计失败:', error);
            });
    }
});
