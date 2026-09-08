<template>
  <AppLayout title="Dashboard">
    <div class="grid-3" style="margin-bottom:20px;">
      <div class="card stat">
        <div class="label">Total Treks</div>
        <div class="value">{{ stats.total_treks ?? '-' }}</div>
      </div>
      <div class="card stat">
        <div class="label">Total Users (Trekkers)</div>
        <div class="value">{{ stats.total_users ?? '-' }}</div>
      </div>
      <div class="card stat">
        <div class="label">Total Trekking Staff</div>
        <div class="value">{{ stats.total_staff ?? '-' }}</div>
      </div>
      <div class="card stat">
        <div class="label">Total Bookings</div>
        <div class="value">{{ stats.total_bookings ?? '-' }}</div>
      </div>
      <div class="card stat">
        <div class="label">Total Revenue</div>
        <div class="value">₹{{ (stats.total_revenue ?? 0).toLocaleString() }}</div>
      </div>
    </div>

    <div class="grid-3" style="margin-bottom:20px;">
      <div class="card">
        <h4 style="margin-top:0;">Most Popular Treks</h4>
        <div v-if="stats.popular_treks?.length">
          <div v-for="t in stats.popular_treks" :key="t.trek_name" style="margin-bottom:8px;">
            <div style="display:flex; justify-content:space-between; font-size:0.88rem;">
              <span>{{ t.trek_name }}</span><span>{{ t.count }}</span>
            </div>
            <div style="background:#eee; border-radius:4px; height:8px;">
              <div style="background:var(--primary); height:8px; border-radius:4px;" :style="{ width: barWidth(t.count, maxPopular) }"></div>
            </div>
          </div>
        </div>
        <p v-else style="color:var(--muted); font-size:0.9rem;">No bookings yet.</p>
      </div>

      <div class="card">
        <h4 style="margin-top:0;">Monthly Participation</h4>
        <div v-if="stats.monthly_participation?.length">
          <div v-for="m in stats.monthly_participation" :key="m.month" style="margin-bottom:8px;">
            <div style="display:flex; justify-content:space-between; font-size:0.88rem;">
              <span>{{ monthNames[m.month - 1] }}</span><span>{{ m.count }}</span>
            </div>
            <div style="background:#eee; border-radius:4px; height:8px;">
              <div style="background:var(--accent); height:8px; border-radius:4px;" :style="{ width: barWidth(m.count, maxMonthly) }"></div>
            </div>
          </div>
        </div>
        <p v-else style="color:var(--muted); font-size:0.9rem;">No data yet.</p>
      </div>

      <div class="card">
        <h4 style="margin-top:0;">Booking Trends</h4>
        <div v-if="stats.booking_trends?.length">
          <div v-for="t in stats.booking_trends" :key="t.status" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <span class="badge" :class="statusBadge(t.status)">{{ t.status }}</span>
            <strong>{{ t.count }}</strong>
          </div>
        </div>
        <p v-else style="color:var(--muted); font-size:0.9rem;">No data yet.</p>
      </div>
    </div>

    <div class="card">
      <h4 style="margin-top:0;">Recent Bookings</h4>
      <table>
        <thead><tr><th>Booking ID</th><th>User</th><th>Trek</th><th>Amount</th><th>Date</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="b in stats.recent_bookings" :key="b.id">
            <td>#{{ b.id }}</td>
            <td>{{ b.user_name }}</td>
            <td>{{ b.trek_name }}</td>
            <td>₹{{ b.amount?.toLocaleString() }}</td>
            <td>{{ formatDate(b.booking_date) }}</td>
            <td><span class="badge" :class="statusBadge(b.status)">{{ b.status }}</span></td>
          </tr>
          <tr v-if="!stats.recent_bookings?.length" class="empty-row"><td colspan="6">No bookings yet.</td></tr>
        </tbody>
      </table>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import AppLayout from '../shared/AppLayout.vue'
import api from '../../services/api'

const stats = ref({})
const monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

const maxPopular = computed(() => Math.max(1, ...(stats.value.popular_treks || []).map(t => t.count)))
const maxMonthly = computed(() => Math.max(1, ...(stats.value.monthly_participation || []).map(m => m.count)))

function barWidth(count, max) {
  return Math.max(6, Math.round((count / max) * 100)) + '%'
}

function formatDate(d) { return d ? new Date(d).toLocaleDateString() : '' }
function statusBadge(status) {
  return { Booked: 'blue', Cancelled: 'red', Completed: 'green' }[status] || 'gray'
}

onMounted(async () => {
  const res = await api.get('/dashboard/admin')
  stats.value = res.data
})
</script>
