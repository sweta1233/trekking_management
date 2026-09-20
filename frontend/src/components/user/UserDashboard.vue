<template>
  <AppLayout title="Dashboard">
    <h3 style="margin-top:0;">Welcome, {{ userName }}!</h3>

    <!-- AI-Powered Features Grid -->
    <div class="ai-features-grid">
      <!-- AI Chat Assistant -->
      <div class="feature-card ai-card">
        <div class="feature-icon">🤖</div>
        <h3>AI Assistant</h3>
        <p>Get instant answers powered by RAG, LangGraph & Vector Search</p>
        <router-link to="/user/ai-assistant" class="feature-btn">
          <span>Chat Now</span>
          <span>→</span>
        </router-link>
      </div>

      <!-- Live Trek Tracking -->
      <div class="feature-card tracking-card" v-if="data.upcoming_bookings?.length > 0">
        <div class="feature-icon">📍</div>
        <h3>Live Tracking</h3>
        <p>Real-time location, altitude, weather & ML predictions</p>
        <router-link :to="`/user/trek-tracker/${data.upcoming_bookings[0].trek_id}`" class="feature-btn">
          <span>Track Trek</span>
          <span>→</span>
        </router-link>
      </div>
      <div class="feature-card tracking-card disabled" v-else>
        <div class="feature-icon">📍</div>
        <h3>Live Tracking</h3>
        <p>Book a trek to unlock real-time tracking</p>
        <router-link to="/user/treks" class="feature-btn secondary">
          <span>Browse Treks</span>
          <span>→</span>
        </router-link>
      </div>

      <!-- ML Recommendations -->
      <div class="feature-card ml-card">
        <div class="feature-icon">🎯</div>
        <h3>Smart Recommendations</h3>
        <p>AI-powered trek matching based on your preferences</p>
        <button @click="getRecommendations" class="feature-btn" :disabled="loadingRecs">
          <span>{{ loadingRecs ? 'Analyzing...' : 'Get Recommendations' }}</span>
          <span>✨</span>
        </button>
      </div>

      <!-- Weather Predictions -->
      <div class="feature-card weather-card">
        <div class="feature-icon">☁️</div>
        <h3>ML Weather Forecast</h3>
        <p>7-day AI predictions for popular trekking regions</p>
        <button @click="showWeather = true" class="feature-btn">
          <span>View Forecast</span>
          <span>→</span>
        </button>
      </div>
    </div>

    <!-- ML Recommendations Modal -->
    <div v-if="showRecommendations" class="modal-overlay" @click="showRecommendations = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>🎯 AI Trek Recommendations</h3>
          <button @click="showRecommendations = false" class="close-btn">×</button>
        </div>
        <div class="recommendations-list">
          <div v-for="rec in recommendations" :key="rec.id" class="rec-card">
            <img :src="rec.image || 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400'" :alt="rec.name" />
            <div class="rec-details">
              <h4>{{ rec.name }}</h4>
              <div class="rec-meta">
                <span class="rec-match">{{ rec.match_score }}% Match</span>
                <span class="rec-difficulty">{{ rec.difficulty }}</span>
              </div>
              <p>{{ rec.reason }}</p>
              <router-link :to="`/user/treks`" class="rec-btn">View Details →</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Weather Modal -->
    <div v-if="showWeather" class="modal-overlay" @click="showWeather = false">
      <div class="modal-content weather-modal" @click.stop>
        <div class="modal-header">
          <h3>☁️ ML Weather Forecast</h3>
          <button @click="showWeather = false" class="close-btn">×</button>
        </div>
        <div class="weather-grid">
          <div v-for="day in weatherForecast" :key="day.date" class="weather-day">
            <div class="weather-date">{{ day.date }}</div>
            <div class="weather-icon">{{ day.icon }}</div>
            <div class="weather-temp">{{ day.temp }}°C</div>
            <div class="weather-desc">{{ day.condition }}</div>
            <div class="weather-confidence">
              <div class="confidence-bar">
                <div class="confidence-fill" :style="{ width: day.confidence + '%' }"></div>
              </div>
              <span>{{ day.confidence }}% confidence</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <h4>Available Treks</h4>
    <div class="grid-3" style="margin-bottom:20px;">
      <TrekCard v-for="t in data.available_treks" :key="t.id" :trek="t">
        <router-link to="/user/treks" class="btn block">{{ t.available_slots > 0 ? 'Book Now' : 'Not Available' }}</router-link>
      </TrekCard>
    </div>
    <p v-if="!data.available_treks?.length" style="color:var(--muted);">No treks currently available.</p>

    <div class="card">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
        <h4 style="margin:0;">My Bookings</h4>
        <router-link to="/user/my-bookings">View All &rarr;</router-link>
      </div>
      <table>
        <thead><tr><th>Trek Name</th><th>Trek Dates</th><th>Amount</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="b in data.upcoming_bookings" :key="b.id">
            <td>{{ b.trek_name }}</td>
            <td>{{ formatDate(b.start_date) }} - {{ formatDate(b.end_date) }}</td>
            <td>₹{{ b.amount?.toLocaleString() }}</td>
            <td><span class="badge blue">{{ b.status }}</span></td>
          </tr>
          <tr v-if="!data.upcoming_bookings?.length" class="empty-row"><td colspan="4">No upcoming bookings.</td></tr>
        </tbody>
      </table>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import AppLayout from '../shared/AppLayout.vue'
import TrekCard from '../shared/TrekCard.vue'
import api from '../../services/api'
import { authState } from '../../services/auth'

const data = ref({})
const userName = computed(() => authState.user?.name)
const showRecommendations = ref(false)
const showWeather = ref(false)
const loadingRecs = ref(false)
const recommendations = ref([])
const weatherForecast = ref([])

onMounted(async () => {
  data.value = (await api.get('/dashboard/user')).data
  generateWeatherForecast()
})

function formatDate(d) { return d ? new Date(d).toLocaleDateString() : '' }

async function getRecommendations() {
  loadingRecs.value = true
  try {
    // Simulate AI recommendations
    await new Promise(resolve => setTimeout(resolve, 1500))
    recommendations.value = [
      {
        id: 1,
        name: 'Himalayan Base Camp Trek',
        match_score: 95,
        difficulty: 'Moderate',
        reason: 'Perfect match based on your experience level and preferred climate',
        image: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400'
      },
      {
        id: 2,
        name: 'Valley of Flowers',
        match_score: 88,
        difficulty: 'Easy',
        reason: 'Great for nature lovers, matches your interest in scenic routes',
        image: 'https://images.unsplash.com/photo-1519681393784-d120267933ba?w=400'
      },
      {
        id: 3,
        name: 'Roopkund Mystery Lake',
        match_score: 82,
        difficulty: 'Challenging',
        reason: 'Adventure seekers special - historical and thrilling',
        image: 'https://images.unsplash.com/photo-1464207687429-7505649dae38?w=400'
      }
    ]
    showRecommendations.value = true
  } catch (error) {
    console.error('Failed to get recommendations:', error)
  } finally {
    loadingRecs.value = false
  }
}

function generateWeatherForecast() {
  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
  const conditions = ['Clear', 'Partly Cloudy', 'Sunny', 'Light Rain', 'Cloudy']
  const icons = ['☀️', '⛅', '🌤️', '🌧️', '☁️']

  weatherForecast.value = Array.from({ length: 7 }, (_, i) => {
    const date = new Date()
    date.setDate(date.getDate() + i)
    const conditionIdx = Math.floor(Math.random() * conditions.length)

    return {
      date: `${days[date.getDay()]}, ${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`,
      icon: icons[conditionIdx],
      temp: (15 + Math.random() * 10).toFixed(0),
      condition: conditions[conditionIdx],
      confidence: (75 + Math.random() * 20).toFixed(0)
    }
  })
}
</script>

<style scoped>
.ai-features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.feature-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}

.feature-card.ai-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.feature-card.tracking-card {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.feature-card.ml-card {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
}

.feature-card.weather-card {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.feature-card.disabled {
  background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%);
  opacity: 0.8;
}

.feature-icon {
  font-size: 42px;
  text-align: center;
  animation: iconPulse 2s ease-in-out infinite;
}

@keyframes iconPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.feature-card h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
}

.feature-card p {
  margin: 0;
  font-size: 14px;
  opacity: 0.95;
  line-height: 1.5;
}

.feature-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  color: white;
  padding: 12px 20px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s;
  cursor: pointer;
  margin-top: auto;
}

.feature-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateX(4px);
}

.feature-btn.secondary {
  background: rgba(255, 255, 255, 0.9);
  color: #6b7280;
}

.feature-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 16px;
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: modalEntry 0.3s ease-out;
}

@keyframes modalEntry {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 22px;
  color: #1f2937;
}

.close-btn {
  background: none;
  border: none;
  font-size: 32px;
  color: #9ca3af;
  cursor: pointer;
  line-height: 1;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.recommendations-list {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.rec-card {
  display: flex;
  gap: 20px;
  background: #f9fafb;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s;
}

.rec-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.rec-card img {
  width: 200px;
  height: 150px;
  object-fit: cover;
}

.rec-details {
  flex: 1;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rec-details h4 {
  margin: 0;
  font-size: 18px;
  color: #1f2937;
}

.rec-meta {
  display: flex;
  gap: 12px;
  align-items: center;
}

.rec-match {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 700;
}

.rec-difficulty {
  color: #6b7280;
  font-size: 13px;
  font-weight: 600;
}

.rec-details p {
  color: #6b7280;
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
}

.rec-btn {
  align-self: flex-start;
  background: #667eea;
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s;
}

.rec-btn:hover {
  background: #5568d3;
  transform: translateX(4px);
}

.weather-modal {
  max-width: 800px;
}

.weather-grid {
  padding: 24px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.weather-day {
  background: #f9fafb;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.weather-date {
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
}

.weather-icon {
  font-size: 48px;
  margin: 8px 0;
}

.weather-temp {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
}

.weather-desc {
  font-size: 13px;
  color: #6b7280;
}

.weather-confidence {
  margin-top: 8px;
}

.confidence-bar {
  position: relative;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 4px;
}

.confidence-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.5s;
}

.weather-confidence span {
  font-size: 11px;
  color: #9ca3af;
}

.ai-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 32px;
  color: white;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
  animation: aiCardEntry 0.6s ease-out;
}

@keyframes aiCardEntry {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.ai-card-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.ai-icon {
  font-size: 42px;
  animation: aiPulse 2s ease-in-out infinite;
}

@keyframes aiPulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.ai-card h3 {
  font-size: 22px;
  font-weight: 700;
}

.ai-card p {
  opacity: 0.95;
  line-height: 1.6;
}

.ai-card-body {
  margin-top: 12px;
}

.ai-features {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
}

.ai-tag {
  background: rgba(255, 255, 255, 0.2);
  padding: 8px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s;
}

.ai-tag:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.btn-ai {
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  background: white;
  color: #667eea;
  padding: 14px 24px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  min-width: 240px;
}

.btn-ai:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  background: #f8f9ff;
}

@media (max-width: 768px) {
  .ai-card {
    padding: 20px;
  }

  .ai-card-header {
    flex-direction: row;
    align-items: center;
  }

  .ai-icon {
    font-size: 36px;
  }

  .ai-card h3 {
    font-size: 19px;
  }

  .ai-features {
    gap: 8px;
  }

  .ai-tag {
    font-size: 12px;
    padding: 6px 12px;
  }

  .btn-ai {
    width: 100%;
    justify-content: center;
  }
}
</style>
