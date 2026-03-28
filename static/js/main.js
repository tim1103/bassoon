/**
 * 浙江省新高考选课排课系统 - 主 JavaScript 文件
 */

// 全局工具函数
const Utils = {
    // 格式化日期
    formatDate: (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // 显示提示消息
    showMessage: (message, type = 'info') => {
        const colors = {
            success: '#27ae60',
            error: '#e74c3c',
            warning: '#f39c12',
            info: '#3498db'
        };

        // 创建消息元素
        const messageEl = document.createElement('div');
        messageEl.textContent = message;
        messageEl.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 2rem;
            background: ${colors[type]};
            color: white;
            border-radius: 4px;
            z-index: 9999;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(messageEl);

        // 3 秒后移除
        setTimeout(() => {
            messageEl.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => messageEl.remove(), 300);
        }, 3000);
    },

    // 确认对话框
    confirm: (message) => {
        return new Promise((resolve) => {
            if (window.confirm(message)) {
                resolve(true);
            } else {
                resolve(false);
            }
        });
    },

    // API 请求封装
    request: async (url, options = {}) => {
        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || '请求失败');
            }

            return data;
        } catch (error) {
            console.error('Request error:', error);
            throw error;
        }
    },

    // 文件上传
    uploadFile: async (url, file, dataType) => {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${url}/${dataType}`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Upload error:', error);
            throw error;
        }
    }
};

// 添加动画样式
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', () => {
    // 模态框点击外部关闭
    window.onclick = (event) => {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    };

    // 表单验证增强
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = '提交中...';
                
                // 2 秒后恢复（防止重复提交）
                setTimeout(() => {
                    submitBtn.disabled = false;
                    const originalText = submitBtn.textContent.replace('中...', '');
                    submitBtn.textContent = originalText;
                }, 2000);
            }
        });
    });

    // 表格行点击效果
    const tables = document.querySelectorAll('.data-table');
    tables.forEach(table => {
        table.addEventListener('click', (e) => {
            if (e.target.tagName === 'TD') {
                // 高亮选中的行
                const row = e.target.parentElement;
                row.parentElement.querySelectorAll('tr').forEach(r => {
                    r.style.backgroundColor = '';
                });
                row.style.backgroundColor = '#e8f4f8';
            }
        });
    });

    console.log('选课排课系统已加载');
});

// 导出为全局可用
window.Utils = Utils;
