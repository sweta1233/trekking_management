<template>
  <div class="trek-tracker">
    <div class="tracker-header">
      <h2>🏔️ {{ trek.name }}</h2>
      <span class="live-badge">● LIVE</span>
    </div>

    <!-- Real-time Progress -->
    <div class="progress-section">
      <div class="progress-circle">
        <svg viewBox="0 0 200 200" class="progress-ring">
          <circle cx="100" cy="100" r="90" class="progress-bg" />
          <circle
            cx="100" cy="100" r="90"
            class="progress-fill"
            :style="{ strokeDashoffset: progressOffset }"
          />
        </svg>
        <div class="progress-text">
          <span class="progress-value">{{ completionPercent }}%</span>
          <span class="progress-label">Complete</span>
        </div>
      </div>
      <div class="progress-stats">
        <div class="stat-card">
          <div class="stat-icon">📍</div>
          <div class="stat-info">
            <span class="stat-value">{{ tracking.currentAltitude || 0 }}m</span>
            <span class="stat-label">Current Altitude</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">⏱️</div>
          <div class="stat-info">
            <span class="stat-value">{{ formatTime(tracking.timeElapsed) }}</span>
            <span class="stat-label">Time Elapsed</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🚶</div>
          <div class="stat-info">
            <span class="stat-value">{{ tracking.distanceCovered || 0 }}km</span>
            <span class="stat-label">Distance</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🌡️</div>
          <div class="stat-info">
            <span class="stat-value">{{ tracking.temperature || 'N/A' }}°C</span>
            <span class="stat-label">Temperature</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Interactive Map -->
    <div class="map-section">
      <h3>📍 Live Location Tracking</h3>
      <div class="map-container" ref="mapContainer">
        <div class="route-map">
          <canvas ref="mapCanvas" width="800" height="400"></canvas>
          <div class="map-markers">
            <div
              v-for="(checkpoint, idx) in checkpoints"
              :key="idx"
              class="checkpoint-marker"
              :style="{ left: checkpoint.x + '%', top: checkpoint.y + '%' }"
              :class="{ active: idx === currentCheckpoint, completed: idx < currentCheckpoint }"
            >
              <div class="marker-dot">
                <span v-if="idx < currentCheckpoint">✓</span>
                <span v-else-if="idx === currentCheckpoint">📍</span>
                <span v-else>{{ idx + 1 }}</span>
              </div>
              <div class="marker-label">{{ checkpoint.name }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ML-Powered Predictions -->
    <div class="predictions-section">
      <h3>🤖 AI Predictions</h3>
      <div class="prediction-grid">
        <div class="prediction-card">
          <div class="prediction-icon">⏰</div>
          <div class="prediction-content">
            <span class="prediction-label">Estimated Arrival</span>
            <span class="prediction-value">{{ mlPredictions.eta }}</span>
            <div class="prediction-confidence">
              <div class="confidence-bar" :style="{ width: mlPredictions.confidence + '%' }"></div>
              <span>{{ mlPredictions.confidence }}% confidence</span>
            </div>
          </div>
        </div>
        <div class="prediction-card">
          <div class="prediction-icon">☁️</div>
          <div class="prediction-content">
            <span class="prediction-label">Weather Forecast</span>
            <span class="prediction-value">{{ mlPredictions.weather }}</span>
            <span class="prediction-subtext">{{ mlPredictions.weatherDesc }}</span>
          </div>
        </div>
        <div class="prediction-card">
          <div class="prediction-icon">⚠️</div>
          <div class="prediction-content">
            <span class="prediction-label">Risk Assessment</span>
            <span class="prediction-value" :class="'risk-' + mlPredictions.riskLevel">
              {{ mlPredictions.riskLevel.toUpperCase() }}
            </span>
            <span class="prediction-subtext">{{ mlPredictions.riskReason }}</span>
          </div>
        </div>
        <div class="prediction-card">
          <div class="prediction-icon">💪</div>
          <div class="prediction-content">
            <span class="prediction-label">Energy Level</span>
            <div class="energy-bar">
              <div class="energy-fill" :style="{ width: mlPredictions.energyLevel + '%' }"></div>
              <span>{{ mlPredictions.energyLevel }}%</span>
            </div>
            <span class="prediction-subtext">{{ mlPredictions.energyAdvice }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Traffic & Group Info -->
    <div class="traffic-section">
      <h3>👥 Trail Traffic & Group</h3>
      <div class="traffic-info">
        <div class="traffic-card">
          <div class="traffic-level" :class="'traffic-' + trafficLevel">
            <div class="traffic-icon">🚶‍♂️</div>
            <span class="traffic-label">{{ trafficLevel.toUpperCase() }}</span>
          </div>
          <p class="traffic-desc">{{ trafficMessage }}</p>
        </div>
        <div class="group-info">
          <h4>Your Group</h4>
          <div class="group-members">
            <div v-for="member in groupMembers" :key="member.id" class="member-card">
              <div class="member-avatar">{{ member.name.charAt(0) }}</div>
              <div class="member-details">
                <span class="member-name">{{ member.name }}</span>
                <span class="member-status" :class="member.status">{{ member.status }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Real-time Alerts -->
    <div v-if="alerts.length > 0" class="alerts-section">
      <h3>⚠️ Active Alerts</h3>
      <div v-for="alert in alerts" :key="alert.id" class="alert-card" :class="'alert-' + alert.type">
        <div class="alert-icon">{{ alert.icon }}</div>
        <div class="alert-content">
          <strong>{{ alert.title }}</strong>
          <p>{{ alert.message }}</p>
          <span class="alert-time">{{ formatTimeAgo(alert.timestamp) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../services/api'

const route = useRoute()
const trek = ref({ name: 'Loading...' })
const tracking = ref({
  currentAltitude: 0,
  timeElapsed: 0,
  distanceCovered: 0,
  temperature: null
})

const mlPredictions = ref({
  eta: 'Calculating...',
  confidence: 85,
  weather: 'Clear',
  weatherDesc: 'Perfect conditions ahead',
  riskLevel: 'low',
  riskReason: 'All conditions favorable',
  energyLevel: 75,
  energyAdvice: 'Pace yourself, stay hydrated'
})

const checkpoints = ref([
  { name: 'Base Camp', x: 10, y: 80 },
  { name: 'Rest Point 1', x: 30, y: 60 },
  { name: 'Mid Camp', x: 50, y: 40 },
  { name: 'Rest Point 2', x: 70, y: 30 },
  { name: 'Summit', x: 90, y: 10 }
])

const currentCheckpoint = ref(2)
const trafficLevel = ref('moderate')
const trafficMessage = computed(() => {
  const messages = {
    low: 'Trail is clear - excellent trekking conditions',
    moderate: 'Moderate traffic - expect some fellow trekkers',
    high: 'Heavy traffic - popular time on the trail'
  }
  return messages[trafficLevel.value]
})

const groupMembers = ref([
  { id: 1, name: 'John Doe', status: 'on-pace' },
  { id: 2, name: 'Jane Smith', status: 'ahead' },
  { id: 3, name: 'Mike Wilson', status: 'behind' }
])

const alerts = ref([
  {
    id: 1,
    type: 'warning',
    icon: '⚠️',
    title: 'Weather Alert',
    message: 'Light rain expected in 2 hours',
    timestamp: Date.now() - 300000
  }
])

const completionPercent = computed(() => {
  return Math.round((currentCheckpoint.value / (checkpoints.value.length - 1)) * 100)
})

const progressOffset = computed(() => {
  const circumference = 2 * Math.PI * 90
  return circumference - (completionPercent.value / 100) * circumference
})

const mapCanvas = ref(null)

function drawRoute() {
  if (!mapCanvas.value) return
  const ctx = mapCanvas.value.getContext('2d')
  ctx.clearRect(0, 0, 800, 400)

  // Draw mountain background
  ctx.fillStyle = '#e8f4f8'
  ctx.fillRect(0, 0, 800, 400)

  // Draw route path
  ctx.strokeStyle = '#667eea'
  ctx.lineWidth = 4
  ctx.setLineDash([10, 5])
  ctx.beginPath()

  checkpoints.value.forEach((cp, idx) => {
    const x = (cp.x / 100) * 800
    const y = (cp.y / 100) * 400
    if (idx === 0) ctx.moveTo(x, y)
    else ctx.lineTo(x, y)
  })
  ctx.stroke()

  // Draw completed path
  ctx.strokeStyle = '#10b981'
  ctx.lineWidth = 6
  ctx.setLineDash([])
  ctx.beginPath()

  for (let i = 0; i <= currentCheckpoint.value && i < checkpoints.value.length; i++) {
    const x = (checkpoints.value[i].x / 100) * 800
    const y = (checkpoints.value[i].y / 100) * 400
    if (i === 0) ctx.moveTo(x, y)
    else ctx.lineTo(x, y)
  }
  ctx.stroke()
}

function formatTime(seconds) {
  const hrs = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  return `${hrs}h ${mins}m`
}

function formatTimeAgo(timestamp) {
  const mins = Math.floor((Date.now() - timestamp) / 60000)
  return mins < 60 ? `${mins}m ago` : `${Math.floor(mins / 60)}h ago`
}

let updateInterval = null

onMounted(async () => {
  // Load trek data
  try {
    const response = await api.get(`/treks/${route.params.id}`)
    trek.value = response.data
  } catch (error) {
    console.error('Failed to load trek:', error)
  }

  // Simulate real-time updates
  updateInterval = setInterval(() => {
    tracking.value.timeElapsed += 60
    tracking.value.distanceCovered += 0.1
    tracking.value.currentAltitude += Math.random() * 10
    tracking.value.temperature = (15 + Math.random() * 5).toFixed(1)

    // Update ML predictions
    mlPredictions.value.energyLevel = Math.max(20, mlPredictions.value.energyLevel - 0.5)
  }, 1000)

  // Draw initial route
  setTimeout(drawRoute, 100)
})

onUnmounted(() => {
  if (updateInterval) clearInterval(updateInterval)
})
</script>

<style scoped>
.trek-tracker {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.tracker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.tracker-header h2 {
  margin: 0;
  font-size: 28px;
  color: #1f2937;
}

.live-badge {
  background: #ef4444;
  color: white;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.progress-section {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 30px;
  margin-bottom: 40px;
}

.progress-circle {
  position: relative;
  width: 200px;
  height: 200px;
  margin: 0 auto;
}

.progress-ring {
  transform: rotate(-90deg);
  width: 100%;
  height: 100%;
}

.progress-bg {
  fill: none;
  stroke: #e5e7eb;
  stroke-width: 12;
}

.progress-fill {
  fill: none;
  stroke: url(#gradient);
  stroke-width: 12;
  stroke-linecap: round;
  stroke-dasharray: 565;
  transition: stroke-dashoffset 0.5s;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.progress-value {
  display: block;
  font-size: 36px;
  font-weight: 700;
  color: #667eea;
}

.progress-label {
  font-size: 14px;
  color: #6b7280;
}

.progress-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.stat-icon {
  font-size: 32px;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
}

.stat-label {
  font-size: 13px;
  color: #6b7280;
}

.map-section {
  margin-bottom: 40px;
}

.map-section h3 {
  margin-bottom: 16px;
  color: #1f2937;
}

.map-container {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}

.route-map {
  position: relative;
  width: 100%;
  height: 400px;
}

.route-map canvas {
  width: 100%;
  height: 100%;
  border-radius: 8px;
}

.map-markers {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.checkpoint-marker {
  position: absolute;
  transform: translate(-50%, -50%);
  text-align: center;
}

.marker-dot {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: white;
  border: 3px solid #9ca3af;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 16px;
  margin: 0 auto 8px;
  transition: all 0.3s;
}

.checkpoint-marker.completed .marker-dot {
  background: #10b981;
  border-color: #10b981;
  color: white;
}

.checkpoint-marker.active .marker-dot {
  background: #667eea;
  border-color: #667eea;
  color: white;
  animation: markerPulse 2s infinite;
}

@keyframes markerPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.marker-label {
  font-size: 12px;
  font-weight: 600;
  color: #374151;
  background: white;
  padding: 4px 8px;
  border-radius: 4px;
  white-space: nowrap;
}

.predictions-section {
  margin-bottom: 40px;
}

.predictions-section h3 {
  margin-bottom: 16px;
  color: #1f2937;
}

.prediction-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.prediction-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  display: flex;
  gap: 16px;
}

.prediction-icon {
  font-size: 36px;
}

.prediction-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.prediction-label {
  font-size: 13px;
  color: #6b7280;
  font-weight: 600;
}

.prediction-value {
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
}

.prediction-value.risk-low { color: #10b981; }
.prediction-value.risk-moderate { color: #f59e0b; }
.prediction-value.risk-high { color: #ef4444; }

.prediction-subtext {
  font-size: 12px;
  color: #9ca3af;
}

.prediction-confidence, .energy-bar {
  position: relative;
  background: #e5e7eb;
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
}

.confidence-bar, .energy-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.5s;
}

.prediction-confidence span, .energy-bar span {
  position: absolute;
  top: 10px;
  left: 0;
  font-size: 11px;
  color: #6b7280;
}

.traffic-section {
  margin-bottom: 40px;
}

.traffic-section h3 {
  margin-bottom: 16px;
  color: #1f2937;
}

.traffic-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.traffic-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.traffic-level {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.traffic-icon {
  font-size: 32px;
}

.traffic-label {
  font-size: 18px;
  font-weight: 700;
}

.traffic-low .traffic-label { color: #10b981; }
.traffic-moderate .traffic-label { color: #f59e0b; }
.traffic-high .traffic-label { color: #ef4444; }

.traffic-desc {
  color: #6b7280;
  margin: 0;
}

.group-info {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.group-info h4 {
  margin: 0 0 16px;
  color: #1f2937;
}

.group-members {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.member-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
}

.member-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 18px;
}

.member-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.member-name {
  font-weight: 600;
  color: #1f2937;
}

.member-status {
  font-size: 12px;
  font-weight: 600;
}

.member-status.on-pace { color: #10b981; }
.member-status.ahead { color: #3b82f6; }
.member-status.behind { color: #f59e0b; }

.alerts-section {
  margin-bottom: 40px;
}

.alerts-section h3 {
  margin-bottom: 16px;
  color: #1f2937;
}

.alert-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  display: flex;
  gap: 16px;
  border-left: 4px solid;
}

.alert-warning { border-left-color: #f59e0b; }
.alert-danger { border-left-color: #ef4444; }
.alert-info { border-left-color: #3b82f6; }

.alert-icon {
  font-size: 24px;
}

.alert-content {
  flex: 1;
}

.alert-content strong {
  display: block;
  margin-bottom: 4px;
  color: #1f2937;
}

.alert-content p {
  margin: 0 0 8px;
  color: #6b7280;
}

.alert-time {
  font-size: 12px;
  color: #9ca3af;
}

@media (max-width: 1024px) {
  .progress-section {
    grid-template-columns: 1fr;
  }

  .traffic-info {
    grid-template-columns: 1fr;
  }

  .prediction-grid {
    grid-template-columns: 1fr;
  }
}
</style>
