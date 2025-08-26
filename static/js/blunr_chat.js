document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const chatMessages = document.getElementById('chatMessages');
    const resetBtn = document.getElementById('resetBtn');
    const sendText = document.getElementById('sendText');
    const loadingSpinner = document.getElementById('loadingSpinner');
    
    // Quick message chips
    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', function() {
            messageInput.value = this.textContent.replace(/['"]/g, '');
            messageInput.focus();
        });
    });
    
    // Send message
    sendButton.addEventListener('click', sendMessage);
    resetBtn.addEventListener('click', resetConversation);
    
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !sendButton.disabled) {
            sendMessage();
        }
    });
    
    async function sendMessage() {
        const message = messageInput.value.trim();
        
        if (!message) return;
        
        // Remove welcome message if exists
        const welcomeMsg = document.querySelector('.welcome-message');
        if (welcomeMsg) {
            welcomeMsg.style.opacity = '0';
            setTimeout(() => welcomeMsg.remove(), 300);
        }
        
        // Add user message
        addMessage(message, 'user');
        
        // Clear input and disable button
        messageInput.value = '';
        sendButton.disabled = true;
        sendText.classList.add('hidden');
        loadingSpinner.classList.remove('hidden');
        
        // Add typing indicator
        const typingIndicator = addTypingIndicator();
        
        try {
            // Send to server
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            typingIndicator.remove();
            
            // Add bot response
            addMessage(data.response, 'bot', data.ai_generated, data.generation_time);
            
        } catch (error) {
            console.error('Error:', error);
            typingIndicator.remove();
            addMessage('Connection error. Please try again.', 'bot', false);
        } finally {
            sendButton.disabled = false;
            sendText.classList.remove('hidden');
            loadingSpinner.classList.add('hidden');
            messageInput.focus();
        }
    }
    
    function addMessage(text, sender, isAiGenerated = false, generationTime = null) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        
        // Avatar
        const avatarImg = document.createElement('img');
        avatarImg.classList.add('message-avatar');
        avatarImg.src = sender === 'user' ? 
            '/static/images/user-avatar.png' : 
            '/static/images/ai-avatar.png';
        avatarImg.alt = sender === 'user' ? 'You' : 'AI';
        
        // Message bubble
        const bubbleDiv = document.createElement('div');
        bubbleDiv.classList.add('message-bubble');
        
        // Author
        const authorSpan = document.createElement('span');
        authorSpan.classList.add('message-author');
        authorSpan.textContent = sender === 'user' ? 'You' : 'Creator AI';
        
        // Content
        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        contentDiv.textContent = text;
        
        bubbleDiv.appendChild(authorSpan);
        bubbleDiv.appendChild(contentDiv);
        
        // AI badge
        if (sender === 'bot' && isAiGenerated) {
            const aiBadge = document.createElement('span');
            aiBadge.classList.add('ai-badge');
            aiBadge.textContent = generationTime ? 
                `✨ AI Generated in ${generationTime}` : 
                '✨ AI Generated';
            bubbleDiv.appendChild(aiBadge);
        }
        
        messageDiv.appendChild(avatarImg);
        messageDiv.appendChild(bubbleDiv);
        
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.classList.add('message', 'bot-message', 'typing-indicator');
        typingDiv.innerHTML = `
            <img src="/static/images/ai-avatar.png" alt="AI" class="message-avatar">
            <div class="message-bubble">
                <span class="message-author">Creator AI</span>
                <div class="message-content">
                    <div style="display: flex; gap: 4px;">
                        <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #5865F2; animation: typing 1.4s infinite;"></span>
                        <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #5865F2; animation: typing 1.4s infinite; animation-delay: 0.2s;"></span>
                        <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #5865F2; animation: typing 1.4s infinite; animation-delay: 0.4s;"></span>
                    </div>
                </div>
            </div>
        `;
        
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return typingDiv;
    }
    
    async function resetConversation() {
        try {
            const response = await fetch('/reset', {
                method: 'POST'
            });
            
            if (response.ok) {
                // Clear all messages except first
                const messages = chatMessages.querySelectorAll('.message');
                messages.forEach((msg, index) => {
                    if (index > 0) {
                        msg.style.opacity = '0';
                        setTimeout(() => msg.remove(), 300);
                    }
                });
                
                setTimeout(() => {
                    addMessage('Conversation reset! Let\'s start fresh 💕', 'bot', true);
                }, 400);
            }
        } catch (error) {
            console.error('Error resetting:', error);
        }
    }
    
    // Load stats
    async function loadStats() {
        try {
            const response = await fetch('/stats');
            const data = await response.json();
            
            document.getElementById('trainingData').textContent = 
                `${data.total_training_samples.toLocaleString()} samples`;
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }
    
    loadStats();
    setInterval(loadStats, 30000);
    
    // Focus input
    messageInput.focus();
});

// Add typing animation CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes typing {
        0%, 60%, 100% {
            transform: translateY(0);
            opacity: 0.7;
        }
        30% {
            transform: translateY(-10px);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);