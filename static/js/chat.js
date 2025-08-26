document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const chatMessages = document.getElementById('chatMessages');
    
    // Ladda statistik
    loadStats();
    
    // Skicka meddelande när man klickar på send
    sendButton.addEventListener('click', sendMessage);
    
    // Skicka meddelande när man trycker Enter
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    async function sendMessage() {
        const message = messageInput.value.trim();
        
        if (!message) return;
        
        // Visa användarens meddelande
        addMessage(message, 'user');
        
        // Rensa input
        messageInput.value = '';
        
        // Visa "typing" indikator
        const typingIndicator = addTypingIndicator();
        
        try {
            // Skicka till servern
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            // Ta bort typing indicator
            typingIndicator.remove();
            
            // Visa bottens svar
            addMessage(data.response, 'bot');
            
        } catch (error) {
            console.error('Error:', error);
            typingIndicator.remove();
            addMessage('Oops! Something went wrong. Try again later.', 'bot');
        }
    }
    
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        
        const authorSpan = document.createElement('span');
        authorSpan.classList.add('message-author');
        authorSpan.textContent = sender === 'user' ? 'You' : 'Bot';
        
        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        contentDiv.textContent = text;
        
        messageDiv.appendChild(authorSpan);
        messageDiv.appendChild(contentDiv);
        
        chatMessages.appendChild(messageDiv);
        
        // Scrolla ner till senaste meddelandet
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.classList.add('message', 'bot-message', 'typing-indicator');
        typingDiv.innerHTML = `
            <span class="message-author">Bot</span>
            <div class="message-content">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
            </div>
        `;
        
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return typingDiv;
    }
    
    async function loadStats() {
        try {
            const response = await fetch('/stats');
            const data = await response.json();
            
            const statsDiv = document.getElementById('stats');
            statsDiv.innerHTML = `
                <p><strong>Status:</strong> ${data.status}</p>
                <p><strong>Träningsdata:</strong> ${data.total_responses.toLocaleString()} svar</p>
                <p><strong>Nyckelord:</strong> ${data.unique_keywords.toLocaleString()}</p>
            `;
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }
});

// CSS för typing indicator
const style = document.createElement('style');
style.textContent = `
    .typing-indicator .message-content {
        display: flex;
        gap: 4px;
        padding: 16px;
    }
    
    .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #666;
        animation: typing 1.4s infinite;
    }
    
    .dot:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .dot:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes typing {
        0%, 60%, 100% {
            transform: translateY(0);
            opacity: 0.5;
        }
        30% {
            transform: translateY(-10px);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);