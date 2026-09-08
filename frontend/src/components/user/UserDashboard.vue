<template>
  <AppLayout title="Dashboard">
    <h3 style="margin-top:0;">Welcome, {{ userName }}!</h3>

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
