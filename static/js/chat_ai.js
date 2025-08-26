document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const chatMessages = document.getElementById('chatMessages');
    const resetBtn = document.getElementById('resetBtn');
    const sendText = document.getElementById('sendText');
    const loadingSpinner = document.getElementById('loadingSpinner');
    
    // Ladda statistik
    loadStats();
    
    // Event listeners
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
        
        // Visa användarens meddelande
        addMessage(message, 'user');
        
        // Rensa input och disable knapp
        messageInput.value = '';
        sendButton.disabled = true;
        sendText.classList.add('hidden');
        loadingSpinner.classList.remove('hidden');
        
        // Visa typing indicator
        const typingIndicator = addTypingIndicator();
        
        try {
            // Skicka till AI-servern
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
            
            // Visa AI-genererat svar
            addMessage(data.response, 'bot', data.ai_generated, data.generation_time);
            
        } catch (error) {
            console.error('Error:', error);
            typingIndicator.remove();
            addMessage('Oops! Connection error. Please try again.', 'bot', false);
        } finally {
            // Återställ knapp
            sendButton.disabled = false;
            sendText.classList.remove('hidden');
            loadingSpinner.classList.add('hidden');
            messageInput.focus();
        }
    }
    
    function addMessage(text, sender, isAiGenerated = false, generationTime = null) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        
        const authorSpan = document.createElement('span');
        authorSpan.classList.add('message-author');
        authorSpan.textContent = sender === 'user' ? 'You' : 'AI Bot';
        
        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        contentDiv.textContent = text;
        
        messageDiv.appendChild(authorSpan);
        messageDiv.appendChild(contentDiv);
        
        // Lägg till AI-indikator för bot-meddelanden
        if (sender === 'bot' && isAiGenerated) {
            const aiIndicator = document.createElement('span');
            aiIndicator.classList.add('ai-indicator');
            aiIndicator.textContent = generationTime ? 
                `✨ AI Generated in ${generationTime}` : 
                '✨ AI Generated';
            messageDiv.appendChild(aiIndicator);
        }
        
        chatMessages.appendChild(messageDiv);
        
        // Scrolla ner till senaste meddelandet
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.classList.add('message', 'bot-message', 'typing-indicator');
        typingDiv.innerHTML = `
            <span class="message-author">AI Bot</span>
            <div class="message-content">
                <div style="display: flex; gap: 5px;">
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
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
                // Rensa chatten men behåll välkomstmeddelandet
                const messages = chatMessages.querySelectorAll('.message');
                messages.forEach((msg, index) => {
                    if (index > 0) {
                        msg.remove();
                    }
                });
                
                addMessage('Conversation reset! Let\'s start fresh 💕', 'bot', true);
            }
        } catch (error) {
            console.error('Error resetting conversation:', error);
        }
    }
    
    async function loadStats() {
        try {
            const response = await fetch('/stats');
            const data = await response.json();
            
            const statsDiv = document.querySelector('.stats-section');
            statsDiv.innerHTML = `
                <h4>📊 AI Statistics:</h4>
                <p><strong>Model:</strong> ${data.model}</p>
                <p><strong>Training Data:</strong> ${data.total_training_samples.toLocaleString()} samples</p>
                <p><strong>Type:</strong> ${data.type}</p>
                <p><strong>Status:</strong> <span style="color: #4ade80;">● ${data.status}</span></p>
                <p><strong>Conversation:</strong> ${data.conversation_length} messages</p>
            `;
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }
    
    // Auto-update stats every 10 seconds
    setInterval(loadStats, 10000);
    
    // Focus on input
    messageInput.focus();
});