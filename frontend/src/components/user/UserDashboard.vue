<template>
  <AppLayout title="Dashboard">
    <h3 style="margin-top:0;">Welcome, {{ userName }}!</h3>

    <!-- AI Assistant Card -->
    <div class="ai-card">
      <div class="ai-card-header">
        <div class="ai-icon">🤖</div>
        <div>
          <h3 style="margin:0 0 4px;">TrekMate AI Assistant</h3>
          <p style="margin:0; font-size:13px; opacity:0.9;">Powered by RAG, LangGraph & Vector Search</p>
        </div>
      </div>
      <div class="ai-card-body">
        <p style="margin:0 0 12px; font-size:14px;">
          Get personalized trek recommendations, trip planning assistance, packing lists, fitness advice, and answers to all your trekking questions.
        </p>
        <div class="ai-features">
          <span class="ai-tag">🏔️ Trek Recommendations</span>
          <span class="ai-tag">🗺️ Trip Planning</span>
          <span class="ai-tag">🎒 Packing Lists</span>
          <span class="ai-tag">💪 Fitness Tips</span>
        </div>
        <router-link to="/user/ai-assistant" class="btn-ai">
          <span>Chat with AI Assistant</span>
          <span style="font-size:18px;">→</span>
        </router-link>
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
onMounted(async () => { data.value = (await api.get('/dashboard/user')).data })
function formatDate(d) { return d ? new Date(d).toLocaleDateString() : '' }
</script>

<style scoped>
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
