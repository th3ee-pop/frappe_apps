/**
 * AI Chat Widget - Floating chat interface for frappe_apps
 * Appears on all pages of the LMS system
 */

class ChatWidget {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.init();
    }

    init() {
        // Wait for page to load
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.render());
        } else {
            this.render();
        }
    }

    render() {
        // Create widget container
        const widget = document.createElement('div');
        widget.id = 'ai-chat-widget';
        widget.innerHTML = this.getHTML();
        document.body.appendChild(widget);

        // Attach event listeners
        this.attachEvents();

        // Load chat history
        this.loadHistory();
    }

    getHTML() {
        return `
            <!-- Floating Button -->
            <div id="chat-toggle-btn" class="chat-toggle-btn">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
                <span id="unread-badge" class="unread-badge" style="display: none;">0</span>
            </div>

            <!-- Chat Panel -->
            <div id="chat-panel" class="chat-panel" style="display: none;">
                <!-- Header -->
                <div class="chat-header">
                    <div class="chat-header-title">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="3"></circle>
                            <path d="M12 1v6m0 6v6m9-9h-6m-6 0H3"></path>
                        </svg>
                        <span>AI Learning Assistant</span>
                    </div>
                    <div class="chat-header-actions">
                        <button id="clear-chat-btn" class="icon-btn" title="Clear chat">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="3 6 5 6 21 6"></polyline>
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                            </svg>
                        </button>
                        <button id="close-chat-btn" class="icon-btn" title="Close">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="18" y1="6" x2="6" y2="18"></line>
                                <line x1="6" y1="6" x2="18" y2="18"></line>
                            </svg>
                        </button>
                    </div>
                </div>

                <!-- Messages Area -->
                <div id="chat-messages" class="chat-messages">
                    <div class="welcome-message">
                        <p>👋 Hello! I'm your AI learning assistant.</p>
                        <p>I can help you with your courses, answer questions, and guide your learning journey.</p>
                    </div>
                </div>

                <!-- Input Area -->
                <div class="chat-input-container">
                    <textarea
                        id="chat-input"
                        class="chat-input"
                        placeholder="Ask me anything about your courses..."
                        rows="1"
                    ></textarea>
                    <button id="send-btn" class="send-btn">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="22" y1="2" x2="11" y2="13"></line>
                            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                        </svg>
                    </button>
                </div>
            </div>
        `;
    }

    attachEvents() {
        // Toggle button
        document.getElementById('chat-toggle-btn').addEventListener('click', () => {
            this.toggleChat();
        });

        // Close button
        document.getElementById('close-chat-btn').addEventListener('click', () => {
            this.toggleChat();
        });

        // Clear chat button
        document.getElementById('clear-chat-btn').addEventListener('click', () => {
            this.clearChat();
        });

        // Send button
        document.getElementById('send-btn').addEventListener('click', () => {
            this.sendMessage();
        });

        // Input - Enter to send
        const input = document.getElementById('chat-input');
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize textarea
        input.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
    }

    toggleChat() {
        this.isOpen = !this.isOpen;
        const panel = document.getElementById('chat-panel');
        const btn = document.getElementById('chat-toggle-btn');

        if (this.isOpen) {
            panel.style.display = 'flex';
            btn.style.display = 'none';
            document.getElementById('chat-input').focus();
            this.clearUnreadBadge();
        } else {
            panel.style.display = 'none';
            btn.style.display = 'flex';
        }
    }

    async sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();

        if (!message) return;

        // Clear input
        input.value = '';
        input.style.height = 'auto';

        // Add user message to UI
        this.addMessage('user', message);

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Call API
            const response = await frappe.call({
                method: 'frappe_apps.api.hello_authenticated',
                args: {},
            });

            // Remove typing indicator
            this.hideTypingIndicator();

            // Add AI response
            const aiMessage = `I received your message: "${message}". I'm currently a demo - full AI integration coming soon!`;
            this.addMessage('assistant', aiMessage);

        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
            console.error('Chat error:', error);
        }
    }

    addMessage(type, content) {
        const messagesDiv = document.getElementById('chat-messages');
        const messageEl = document.createElement('div');
        messageEl.className = `chat-message ${type}-message`;

        const avatar = type === 'user' ? '👤' : '🤖';
        messageEl.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">${this.escapeHtml(content)}</div>
        `;

        messagesDiv.appendChild(messageEl);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;

        // Store in messages array
        this.messages.push({ type, content, timestamp: new Date() });
    }

    showTypingIndicator() {
        const messagesDiv = document.getElementById('chat-messages');
        const indicator = document.createElement('div');
        indicator.id = 'typing-indicator';
        indicator.className = 'chat-message assistant-message typing';
        indicator.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <div class="typing-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        messagesDiv.appendChild(indicator);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    clearChat() {
        if (confirm('Clear all chat messages?')) {
            const messagesDiv = document.getElementById('chat-messages');
            messagesDiv.innerHTML = `
                <div class="welcome-message">
                    <p>👋 Chat cleared. How can I help you?</p>
                </div>
            `;
            this.messages = [];
        }
    }

    loadHistory() {
        // Placeholder - will load from backend later
        console.log('Chat widget loaded');
    }

    clearUnreadBadge() {
        document.getElementById('unread-badge').style.display = 'none';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize chat widget when page loads
if (typeof frappe !== 'undefined') {
    frappe.ready(() => {
        window.chatWidget = new ChatWidget();
    });
} else {
    // Fallback if frappe is not available
    window.addEventListener('DOMContentLoaded', () => {
        window.chatWidget = new ChatWidget();
    });
}
