/**
 * AI Chatbot Widget - Bottom Right Corner
 * Handles text and voice interactions with meal ordering
 */

class MealPrepChatbot {
    constructor() {
        this.isOpen = false;
        this.isListening = false;
        this.conversationHistory = [];
        this.apiKey = localStorage.getItem('voice_api_key') || '';
        this.init();
    }

    init() {
        this.createChatbotUI();
        this.attachEventListeners();
        this.loadMeals();
    }

    createChatbotUI() {
        // Create chatbot widget HTML
        const chatbotHTML = `
            <div id="chatbot-widget" class="chatbot-widget">
                <!-- Floating Chat Button -->
                <button id="chatbot-toggle-btn" class="chatbot-btn" title="Open AI Assistant">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
                    </svg>
                </button>

                <!-- Chat Window (Initially Hidden) -->
                <div id="chatbot-window" class="chatbot-window hidden">
                    <div class="chatbot-header">
                        <h3> MealPrep AI Assistant</h3>
                        <button id="chatbot-close-btn" class="close-btn" title="Close">×</button>
                    </div>

                    <div id="chatbot-messages" class="chatbot-messages">
                        <div class="chatbot-message bot">
                            <p>Hi! I'm your AI meal ordering assistant. Tell me what you'd like to order!</p>
                        </div>
                    </div>

                    <div class="chatbot-input-area">
                        <div class="input-controls">
                            <input 
                                type="text" 
                                id="chatbot-input" 
                                class="chatbot-input" 
                                placeholder="Ask for a meal..."
                                autocomplete="off"
                            >
                            <button id="send-btn" class="send-btn" title="Send Message">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M16.6915026,12.4744748 L3.50612381,13.2599618 C3.19218622,13.2599618 3.03521743,13.4170592 3.03521743,13.5741566 L1.15159189,20.0151496 C0.8376543,20.8006365 0.99,21.89 1.77946707,22.52 C2.41,22.99 3.50612381,23.1 4.13399899,22.8429026 L21.714504,14.0454487 C22.6563168,13.5741566 23.1272231,12.6315722 22.9702544,11.6889879 L4.13399899,1.16126562 C3.34915502,0.9041682 2.40734225,1.01463286 1.77946707,1.4859248 C0.994623095,2.11268405 0.837654326,3.0552684 1.15159189,3.84075527 L3.03521743,10.2817482 C3.03521743,10.4388456 3.34915502,10.5489103 3.50612381,10.5489103 L16.6915026,11.3343972 C16.6915026,11.3343972 17.1624089,11.3343972 17.1624089,10.8631052 L17.1624089,12.0031869 C17.1624089,12.4744748 16.6915026,12.4744748 16.6915026,12.4744748 Z"/>
                                </svg>
                            </button>
                            <button id="voice-btn" class="voice-btn" title="Start Voice Input">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                                    <path d="M17 16.91c-1.48 1.46-3.51 2.36-5.7 2.36-2.19 0-4.22-.9-5.7-2.36M19 21h2v2h-2z"/>
                                </svg>
                            </button>
                        </div>
                        <div id="listening-indicator" class="listening-indicator hidden">
                            <span class="pulse"></span> Listening...
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', chatbotHTML);
    }

    attachEventListeners() {
        // Toggle chat window
        document.getElementById('chatbot-toggle-btn').addEventListener('click', () => this.toggleChat());
        document.getElementById('chatbot-close-btn').addEventListener('click', () => this.toggleChat());

        // Send message
        document.getElementById('send-btn').addEventListener('click', () => this.sendMessage());
        document.getElementById('chatbot-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });

        // Voice input
        document.getElementById('voice-btn').addEventListener('click', () => this.toggleVoiceInput());
    }

    toggleChat() {
        this.isOpen = !this.isOpen;
        const window = document.getElementById('chatbot-window');
        if (this.isOpen) {
            window.classList.remove('hidden');
            document.getElementById('chatbot-input').focus();
        } else {
            window.classList.add('hidden');
        }
    }

    async sendMessage() {
        const input = document.getElementById('chatbot-input');
        const message = input.value.trim();

        if (!message) return;

        // Add user message to UI
        this.addMessageToChat(message, 'user');
        input.value = '';

        try {
            // Send to backend
            const response = await fetch('/api/chatbot/message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();

            if (data.error) {
                this.addMessageToChat('Sorry, I encountered an error. Please try again.', 'bot');
                return;
            }

            // Add bot response
            this.addMessageToChat(data.response, 'bot');

            // If meal was ordered, add to cart
            if (data.meal_ordered && data.meal) {
                await this.addMealToCart(data.meal.id, data.quantity);
                this.addMessageToChat(`✓ Added to cart! Your total items: check cart for details.`, 'bot');
            }

            // Text-to-speech if available
            if (data.speak) {
                this.speak(data.response);
            }
        } catch (error) {
            console.error('Chat error:', error);
            this.addMessageToChat('Sorry, I\'m having trouble connecting. Please try again.', 'bot');
        }
    }

    addMessageToChat(message, sender) {
        const messagesDiv = document.getElementById('chatbot-messages');
        const messageEl = document.createElement('div');
        messageEl.className = `chatbot-message ${sender}`;
        messageEl.innerHTML = `<p>${this.escapeHtml(message)}</p>`;
        messagesDiv.appendChild(messageEl);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    async addMealToCart(mealId, quantity) {
        try {
            await fetch('/api/chatbot/add-to-cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    meal_id: mealId,
                    quantity: quantity || 1
                })
            });
        } catch (error) {
            console.error('Cart error:', error);
        }
    }

    toggleVoiceInput() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            this.addMessageToChat('Voice input is not supported in your browser. Please use text instead.', 'bot');
            return;
        }

        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }

    startListening() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();

        recognition.language = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        this.isListening = true;
        document.getElementById('listening-indicator').classList.remove('hidden');
        document.getElementById('voice-btn').classList.add('listening');

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            document.getElementById('chatbot-input').value = transcript;
            this.stopListening();
            this.sendMessage();
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.addMessageToChat('Sorry, I couldn\'t hear you clearly. Please try again.', 'bot');
            this.stopListening();
        };

        recognition.onend = () => {
            this.stopListening();
        };

        recognition.start();
    }

    stopListening() {
        this.isListening = false;
        document.getElementById('listening-indicator').classList.add('hidden');
        document.getElementById('voice-btn').classList.remove('listening');
    }

    speak(text) {
        if (!('speechSynthesis' in window)) {
            console.log('Text-to-speech not supported');
            return;
        }

        // Cancel any existing speech
        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9;
        utterance.pitch = 1;
        utterance.volume = 0.8;

        window.speechSynthesis.speak(utterance);
    }

    async loadMeals() {
        try {
            const response = await fetch('/api/chatbot/meals');
            const meals = await response.json();
            this.meals = meals;
        } catch (error) {
            console.error('Failed to load meals:', error);
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize chatbot when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.mealPrepChatbot = new MealPrepChatbot();
});
