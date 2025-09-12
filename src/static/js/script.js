document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chatMessages');
    const messageInput = document.getElementById('messageInput');
    const sendMessageBtn = document.getElementById('sendMessage');
    const fileUpload = document.getElementById('fileUpload');
    const fileInput = document.getElementById('fileInput');
    const fileList = document.getElementById('fileList');
    const actionButtons = document.querySelectorAll('.action-btn');

    let sessionId = generateSessionId();
    let uploadedFiles = [];

    // 生成会话ID
    function generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9);
    }

    // 调整文本区域高度
    messageInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // 发送消息函数
    async function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;

        // 添加用户消息到聊天界面
        addMessage(message, 'user');
        messageInput.value = '';
        messageInput.style.height = 'auto';

        // 如果有上传文件，显示文件信息
        if (uploadedFiles.length > 0) {
            const fileMessage = document.createElement('div');
            fileMessage.className = 'message user-message';

            let fileListHtml = '<div class="file-message"><i class="fas fa-paperclip"></i> 已上传文件:';
            uploadedFiles.forEach(file => {
                fileListHtml += `<div class="file-item">${file.name}</div>`;
            });
            fileListHtml += '</div>';

            fileMessage.innerHTML = fileListHtml;
            chatMessages.appendChild(fileMessage);
        }

        messageInput.value = '';
        messageInput.style.height = 'auto';

        // 显示AI正在输入
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'message ai-message';
        typingIndicator.innerHTML = `
            <div class="message-content typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        chatMessages.appendChild(typingIndicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            // 准备FormData，包含文件和文本消息
            const formData = new FormData();
            if (message) {
                formData.append('message', message);
            }
            formData.append('session_id', sessionId);
            formData.append('mode', getCurrentMode()); // 新增：传入mode

            // 添加上传的文件
            uploadedFiles.forEach(file => {
                formData.append('files', file);
            });

            // 发送请求到后端
            const response = await fetch('/api/chat', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                // 尝试获取更详细的错误信息
                clonedResponse = response.clone(); // 克隆响应流，防止错误响应中多次读取
                let errorDetail = `HTTP error! status: ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorDetail += `, detail: ${JSON.stringify(errorData)}`;
                } catch (e) {
                    // 如果无法解析 JSON 错误响应，使用原始文本
                    const errorText = await clonedResponse.text();
                    errorDetail += `, text: ${errorText}`;
                }
                throw new Error(errorDetail);
            }

            const data = await response.json();

            // 移除输入指示器
            chatMessages.removeChild(typingIndicator);

            // 添加AI响应到聊天界面，使用Markdown渲染
            addMarkdownMessage(data.response, 'ai');

            // 清空已上传文件列表
            uploadedFiles = [];
            updateFileList();
        } catch (error) {
            console.error('Error:', error);
            chatMessages.removeChild(typingIndicator);
            addMessage('抱歉，发生了错误。请稍后再试。', 'ai');
        }
    }

    // 添加普通文本消息到聊天界面
    function addMessage(content, sender) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}-message`;

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = content;

        messageElement.appendChild(messageContent);
        chatMessages.appendChild(messageElement);

        // 滚动到底部
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // 添加Markdown格式的消息到聊天界面
    function addMarkdownMessage(content, sender) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}-message`;

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content markdown-body';

        // 使用Marked.js解析Markdown
        messageContent.innerHTML = marked.parse(content);

        // 为代码块添加高亮
        messageContent.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });

        messageElement.appendChild(messageContent);
        chatMessages.appendChild(messageElement);

        // 滚动到底部
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }


    // 更新文件列表显示
    function updateFileList() {
        fileList.innerHTML = '';

        uploadedFiles.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <span>${file.name}</span>
                <button class="remove-file" data-index="${index}">
                    <i class="fas fa-times"></i>
                </button>
            `;
            fileList.appendChild(fileItem);
        });

        // 添加移除文件的事件监听
        document.querySelectorAll('.remove-file').forEach(button => {
            button.addEventListener('click', function() {
                const index = parseInt(this.getAttribute('data-index'));
                uploadedFiles.splice(index, 1);
                updateFileList();
            });
        });
    }

    // 发送消息按钮点击事件
    sendMessageBtn.addEventListener('click', sendMessage);

    // 按Enter发送消息
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // 文件上传点击事件
    fileUpload.addEventListener('click', function() {
        fileInput.click();
    });

    // 文件选择变化事件
    fileInput.addEventListener('change', function() {
        for (let i = 0; i < this.files.length; i++) {
            uploadedFiles.push(this.files[i]);
        }
        updateFileList();
    });

    // 拖放文件上传
    fileUpload.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.style.borderColor = 'var(--secondary-color)';
        this.style.backgroundColor = '#f0f8ff';
    });

    fileUpload.addEventListener('dragleave', function() {
        this.style.borderColor = '#ccc';
        this.style.backgroundColor = 'transparent';
    });

    fileUpload.addEventListener('drop', function(e) {
        e.preventDefault();
        this.style.borderColor = '#ccc';
        this.style.backgroundColor = 'transparent';

        for (let i = 0; i < e.dataTransfer.files.length; i++) {
            uploadedFiles.push(e.dataTransfer.files[i]);
        }
        updateFileList();
    });

    // 快速操作按钮点击事件
    actionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const command = this.getAttribute('data-command');
            messageInput.value = command;
        });
    });

    // 新增：模式切换
    const intentAnalysisToggle = document.getElementById('intentAnalysisToggle');
    const planToggle = document.getElementById('planToggle');

    // 同步状态：确保只有一个为 on
    function syncToggles(exceptButton) {
        [intentAnalysisToggle, planToggle].forEach(btn => {
            if (btn !== exceptButton && btn.getAttribute('data-state') === 'on') {
                btn.setAttribute('data-state', 'off');
            }
        });
    }

    // 切换状态函数
    function setupToggle(button) {
        button.addEventListener('click', function () {
            const currentState = this.getAttribute('data-state');
            // 如果已经是 on，点击无效
            if (currentState === 'on') return;
            // 当前按钮设为 on
            this.setAttribute('data-state', 'on');
            // 关闭另一个
            syncToggles(this);
            // 日志输出
            if (this.id === 'intentAnalysisToggle') {
                console.log("模式切换：意图识别已启用");
            } else if (this.id === 'planToggle') {
                console.log("模式切换：规划模式已启用");
            }
        });
    }

    // 初始化 toggle 按钮
    setupToggle(intentAnalysisToggle);
    setupToggle(planToggle);
    // 页面加载时设置默认状态
    window.addEventListener('DOMContentLoaded', () => {
        intentAnalysisToggle.setAttribute('data-state', 'on');
        planToggle.setAttribute('data-state', 'off');
    });
    // 获取状态
    function getCurrentMode() {
        if (intentAnalysisToggle.getAttribute('data-state') === 'on') {
            return 'analyze';
        } else if (planToggle.getAttribute('data-state') === 'on') {
            return 'plan';
        }
        return 'analyze'; // fallback
    }
});

