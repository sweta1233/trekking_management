<template>
  <div class="ai-assistant-container">
    <!-- Header -->
    <div class="ai-header">
      <div class="ai-header-left">
        <span class="ai-icon">🤖</span>
        <div>
          <h2>TrekMate AI Assistant</h2>
          <p class="ai-subtitle">
            Powered by RAG, LangGraph & Vector Search
          </p>
        </div>
      </div>
      <button
        v-if="conversationHistory.length > 0"
        @click="clearConversation"
        class="btn-clear"
        title="Start new conversation"
      >
        <span>🔄</span> New Chat
      </button>
    </div>

    <!-- Feature Pills -->
    <div class="features-bar" v-if="conversationHistory.length === 0">
      <div class="feature-pill">📚 RAG Document Search</div>
      <div class="feature-pill">🎯 Smart Recommendations</div>
      <div class="feature-pill">🗓️ Trip Planning</div>
      <div class="feature-pill">🎒 Packing Lists</div>
      <div class="feature-pill">💪 Fitness Assessment</div>
    </div>

    <!-- Suggested Questions (shown when no conversation) -->
    <div v-if="conversationHistory.length === 0" class="suggestions-container">
      <h3>Ask me anything about trekking:</h3>
      <div class="suggestions-grid">
        <button
          v-for="(suggestion, idx) in suggestedQuestions"
          :key="idx"
          @click="sendSuggestion(suggestion)"
          class="suggestion-card"
        >
          <span class="suggestion-icon">{{ suggestion.icon }}</span>
          <span class="suggestion-text">{{ suggestion.text }}</span>
        </button>
      </div>
    </div>

    <!-- Chat Messages -->
    <div class="chat-messages" ref="messagesContainer">
      <div
        v-for="(msg, idx) in conversationHistory"
        :key="idx"
        :class="['message', msg.role]"
      >
        <div class="message-avatar">
          {{ msg.role === 'user' ? '👤' : '🤖' }}
        </div>
        <div class="message-content">
          <div class="message-header">
            <strong>{{ msg.role === 'user' ? 'You' : 'TrekMate AI' }}</strong>
            <span v-if="msg.intent" class="intent-badge">{{ msg.intent }}</span>
          </div>

          <!-- Message text with markdown rendering -->
          <div class="message-text" v-html="renderMarkdown(msg.content)"></div>

          <!-- Sources (for RAG responses) -->
          <div v-if="msg.sources && msg.sources.length > 0" class="sources-container">
            <div class="sources-header">
              <span>📄 Sources ({{ msg.sources.length }})</span>
              <button @click="msg.showSources = !msg.showSources" class="toggle-sources">
                {{ msg.showSources ? '▼' : '▶' }}
              </button>
            </div>
            <div v-if="msg.showSources" class="sources-list">
              <div v-for="(source, sidx) in msg.sources" :key="sidx" class="source-item">
                <div class="source-citation">
                  📖 <strong>{{ source.title }}</strong>
                  <span class="source-meta">
                    (Page {{ source.page_number }}, § {{ source.section }})
                  </span>
                </div>
                <div class="source-excerpt">{{ source.excerpt }}</div>
                <div class="source-score">
                  Relevance: {{ (source.similarity_score * 100).toFixed(0) }}%
                </div>
              </div>
            </div>
          </div>

          <!-- Metadata footer -->
          <div v-if="msg.metadata" class="message-metadata">
            <span v-if="msg.metadata.latency_ms">
              ⚡ {{ msg.metadata.latency_ms }}ms
            </span>
            <span v-if="msg.metadata.model_used">
              🧠 {{ msg.metadata.model_used }}
            </span>
            <span v-if="msg.metadata.grounding_score">
              ✓ {{ (msg.metadata.grounding_score * 100).toFixed(0) }}% grounded
            </span>
            <span v-if="msg.metadata.tool_calls && msg.metadata.tool_calls.length > 0">
              🔧 {{ msg.metadata.tool_calls.length }} tools
            </span>
          </div>
        </div>
      </div>

      <!-- Loading indicator -->
      <div v-if="isLoading" class="message assistant loading">
        <div class="message-avatar">🤖</div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span><span></span><span></span>
          </div>
          <div class="loading-text">
            {{ loadingMessage }}
          </div>
        </div>
      </div>

      <!-- Error message -->
      <div v-if="errorMessage" class="error-banner">
        <span>⚠️</span>
        <span>{{ errorMessage }}</span>
        <button @click="errorMessage = null" class="close-error">✕</button>
      </div>
    </div>

    <!-- Input Area -->
    <div class="chat-input-container">
      <!-- Trek context selector -->
      <div v-if="availableTreks.length > 0" class="context-selector">
        <label>
          <input
            type="checkbox"
            v-model="includeTrekContext"
            @change="onContextToggle"
          />
          Ask about specific trek:
        </label>
        <select
          v-if="includeTrekContext"
          v-model="selectedTrekId"
          class="trek-select"
        >
          <option :value="null">General trekking questions</option>
          <option
            v-for="trek in availableTreks"
            :key="trek.id"
            :value="trek.id"
          >
            {{ trek.trek_name }} ({{ trek.max_altitude_m }}m)
          </option>
        </select>
      </div>

      <!-- Input box -->
      <div class="input-wrapper">
        <textarea
          v-model="userInput"
          @keydown.enter.exact.prevent="sendMessage"
          @keydown.enter.shift.exact="userInput += '\n'"
          placeholder="Ask about treks, gear, fitness, itineraries, or safety..."
          rows="2"
          class="chat-input"
          :disabled="isLoading"
        ></textarea>
        <button
          @click="sendMessage"
          :disabled="!userInput.trim() || isLoading"
          class="btn-send"
          title="Send message (Enter)"
        >
          <span v-if="!isLoading">🚀</span>
          <span v-else>⏳</span>
        </button>
      </div>

      <div class="input-hints">
        <small>💡 Press Enter to send, Shift+Enter for new line</small>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'AIAssistant',

  data() {
    return {
      userInput: '',
      conversationHistory: [],
      sessionId: null,
      isLoading: false,
      loadingMessage: 'Thinking...',
      errorMessage: null,
      includeTrekContext: false,
      selectedTrekId: null,
      availableTreks: [],

      suggestedQuestions: [
        { icon: '🏔️', text: 'Which trek is best for beginners?' },
        { icon: '🎒', text: 'What should I pack for Kedarkantha?' },
        { icon: '💪', text: 'Am I fit enough for a 4000m trek?' },
        { icon: '📅', text: 'Create a 5-day itinerary for me' },
        { icon: '⚠️', text: 'How to prevent altitude sickness?' },
        { icon: '🌦️', text: 'Best season for Himalayan treks?' },
      ],
    }
  },

  mounted() {
    this.initializeSession()
    this.loadAvailableTreks()

    // Check if opened with specific trek context
    if (this.$route.query.trekId) {
      this.selectedTrekId = parseInt(this.$route.query.trekId)
      this.includeTrekContext = true
    }
  },

  methods: {
    initializeSession() {
      // Generate unique session ID for conversation tracking
      this.sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    },

    async loadAvailableTreks() {
      try {
        const response = await api.get('/treks', {
          params: {
            status: 'Open',
            per_page: 20
          }
        })
        this.availableTreks = response.data.treks || []
      } catch (error) {
        console.error('Failed to load treks:', error)
      }
    },

    async sendMessage() {
      if (!this.userInput.trim() || this.isLoading) return

      const message = this.userInput.trim()
      this.userInput = ''

      // Add user message to history
      this.conversationHistory.push({
        role: 'user',
        content: message,
        timestamp: new Date(),
      })

      this.scrollToBottom()

      // Send to AI backend
      await this.callAIBackend(message)
    },

    async callAIBackend(message) {
      this.isLoading = true
      this.errorMessage = null

      // Determine loading message based on content
      if (message.toLowerCase().includes('recommend')) {
        this.loadingMessage = 'Analyzing your preferences and matching treks...'
      } else if (message.toLowerCase().includes('pack')) {
        this.loadingMessage = 'Generating personalized packing list...'
      } else if (message.toLowerCase().includes('itinerary') || message.toLowerCase().includes('plan')) {
        this.loadingMessage = 'Planning your trek itinerary...'
      } else if (message.toLowerCase().includes('fit')) {
        this.loadingMessage = 'Assessing your fitness readiness...'
      } else {
        this.loadingMessage = 'Searching documents and analyzing...'
      }

      try {
        const response = await api.post('/ai/chat', {
          message: message,
          session_id: this.sessionId,
          trek_id: this.includeTrekContext ? this.selectedTrekId : null,
        })

        const data = response.data

        // Add assistant response to history
        const assistantMessage = {
          role: 'assistant',
          content: data.response || 'I apologize, I could not generate a response.',
          intent: data.intent,
          sources: data.sources || [],
          showSources: false,
          timestamp: new Date(),
          metadata: {
            latency_ms: data.latency_ms,
            model_used: data.model_used,
            grounding_score: data.grounding_score,
            tool_calls: data.tool_calls,
          }
        }

        this.conversationHistory.push(assistantMessage)

        this.scrollToBottom()

      } catch (error) {
        console.error('AI chat error:', error)

        this.errorMessage = error.response?.data?.error || 'AI service temporarily unavailable. Please try again.'

        // Add fallback message
        this.conversationHistory.push({
          role: 'assistant',
          content: '⚠️ I encountered an error processing your request. Please try rephrasing your question or try again in a moment.',
          timestamp: new Date(),
        })
      } finally {
        this.isLoading = false
        this.scrollToBottom()
      }
    },

    sendSuggestion(suggestion) {
      this.userInput = suggestion.text
      this.sendMessage()
    },

    clearConversation() {
      if (confirm('Start a new conversation? Current chat will be cleared.')) {
        this.conversationHistory = []
        this.initializeSession()
        this.selectedTrekId = null
        this.includeTrekContext = false
      }
    },

    onContextToggle() {
      if (!this.includeTrekContext) {
        this.selectedTrekId = null
      }
    },

    renderMarkdown(text) {
      // Basic markdown rendering
      if (!text) return ''

      let html = text
        // Headers
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        // Bold
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Italic
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        // Code blocks
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        // Bullet lists
        .replace(/^\- (.*$)/gim, '<li>$1</li>')
        .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
        // Line breaks
        .replace(/\n/g, '<br>')

      return html
    },

    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      })
    }
  }
}
</script>

<style scoped>
.ai-assistant-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

/* Header */
.ai-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom: 3px solid #5568d3;
}

.ai-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-icon {
  font-size: 32px;
}

.ai-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.ai-subtitle {
  margin: 4px 0 0;
  font-size: 12px;
  opacity: 0.9;
}

.btn-clear {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.btn-clear:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Features Bar */
.features-bar {
  display: flex;
  gap: 8px;
  padding: 12px 24px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  overflow-x: auto;
  flex-wrap: nowrap;
}

.feature-pill {
  background: white;
  border: 1px solid #dee2e6;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  white-space: nowrap;
  color: #495057;
}

/* Suggestions */
.suggestions-container {
  padding: 32px 24px;
  background: #f8f9fa;
}

.suggestions-container h3 {
  margin: 0 0 20px;
  font-size: 18px;
  color: #495057;
}

.suggestions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 12px;
}

.suggestion-card {
  background: white;
  border: 2px solid #e9ecef;
  padding: 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 12px;
  text-align: left;
}

.suggestion-card:hover {
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
  transform: translateY(-2px);
}

.suggestion-icon {
  font-size: 24px;
}

.suggestion-text {
  font-size: 14px;
  color: #495057;
}

/* Chat Messages */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: #f8f9fa;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message-avatar {
  font-size: 32px;
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  background: white;
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.message.user .message-content {
  background: #667eea;
  color: white;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.intent-badge {
  background: #e9ecef;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  color: #6c757d;
  text-transform: uppercase;
}

.message.user .intent-badge {
  background: rgba(255, 255, 255, 0.3);
  color: white;
}

.message-text {
  line-height: 1.6;
  word-wrap: break-word;
}

.message-text h1, .message-text h2, .message-text h3 {
  margin: 12px 0 8px;
  font-weight: 600;
}

.message-text ul {
  margin: 8px 0;
  padding-left: 20px;
}

.message-text code {
  background: #f8f9fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.message.user .message-text code {
  background: rgba(255, 255, 255, 0.2);
}

/* Sources */
.sources-container {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e9ecef;
}

.sources-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  font-weight: 600;
  color: #6c757d;
  margin-bottom: 8px;
}

.toggle-sources {
  background: none;
  border: none;
  cursor: pointer;
  color: #667eea;
  font-size: 12px;
  padding: 4px 8px;
}

.sources-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 12px;
}

.source-item {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 6px;
  border-left: 3px solid #667eea;
}

.source-citation {
  font-size: 13px;
  font-weight: 600;
  color: #495057;
  margin-bottom: 6px;
}

.source-meta {
  font-weight: normal;
  color: #6c757d;
  font-size: 12px;
}

.source-excerpt {
  font-size: 12px;
  color: #6c757d;
  line-height: 1.5;
  margin-bottom: 6px;
}

.source-score {
  font-size: 11px;
  color: #28a745;
  font-weight: 600;
}

/* Message Metadata */
.message-metadata {
  display: flex;
  gap: 12px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e9ecef;
  font-size: 11px;
  color: #6c757d;
}

.message.user .message-metadata {
  border-top-color: rgba(255, 255, 255, 0.3);
  color: rgba(255, 255, 255, 0.8);
}

/* Loading */
.loading .message-content {
  background: #f8f9fa;
  border: 2px dashed #dee2e6;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  margin-bottom: 8px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #667eea;
  border-radius: 50%;
  animation: bounce 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-10px); }
}

.loading-text {
  font-size: 13px;
  color: #6c757d;
  font-style: italic;
}

/* Error */
.error-banner {
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
  padding: 12px 16px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 16px 0;
}

.close-error {
  margin-left: auto;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: #721c24;
}

/* Input Area */
.chat-input-container {
  background: white;
  border-top: 2px solid #e9ecef;
  padding: 16px 24px;
}

.context-selector {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  font-size: 14px;
}

.trek-select {
  flex: 1;
  padding: 6px 12px;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 14px;
}

.input-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.chat-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #ced4da;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  resize: none;
  transition: border-color 0.2s;
}

.chat-input:focus {
  outline: none;
  border-color: #667eea;
}

.btn-send {
  background: #667eea;
  border: none;
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 20px;
  transition: all 0.2s;
  flex-shrink: 0;
}

.btn-send:hover:not(:disabled) {
  background: #5568d3;
  transform: scale(1.05);
}

.btn-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.input-hints {
  margin-top: 8px;
  text-align: center;
  color: #6c757d;
}

/* Responsive */
@media (max-width: 768px) {
  .ai-assistant-container {
    height: calc(100vh - 80px);
    border-radius: 0;
  }

  .suggestions-grid {
    grid-template-columns: 1fr;
  }

  .features-bar {
    overflow-x: auto;
  }

  .message-metadata {
    flex-wrap: wrap;
  }
}
</style>
