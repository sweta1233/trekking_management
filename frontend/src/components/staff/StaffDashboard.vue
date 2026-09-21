<template>
  <AppLayout title="My Dashboard">
    <div class="grid-3" style="margin-bottom:20px;">
      <div class="card stat"><div class="label">Assigned Treks</div><div class="value">{{ data.assigned_treks_count ?? '-' }}</div></div>
      <div class="card stat"><div class="label">Total Participants</div><div class="value">{{ data.total_participants ?? '-' }}</div></div>
      <div class="card stat"><div class="label">Ongoing Treks</div><div class="value">{{ data.ongoing_treks ?? '-' }}</div></div>
    </div>

    <BookItinerary />

    <div class="card">
      <h4 style="margin-top:0;">My Assigned Treks</h4>
      <table>
        <thead><tr><th>Trek Name</th><th>Dates</th><th>Participants</th><th>Slots</th><th>Status</th><th>Action</th></tr></thead>
        <tbody>
          <tr v-for="t in data.treks" :key="t.id">
            <td>{{ t.trek_name }}</td>
            <td>{{ formatDate(t.start_date) }} - {{ formatDate(t.end_date) }}</td>
            <td>{{ t.total_slots - t.available_slots }}</td>
            <td>{{ t.available_slots }} / {{ t.total_slots }}</td>
            <td><span class="badge" :class="statusBadge(t.status)">{{ t.status }}</span></td>
            <td><router-link :to="`/staff/treks/${t.id}`" class="btn small">{{ t.status === 'Completed' ? 'View' : 'Manage' }}</router-link></td>
          </tr>
          <tr v-if="!data.treks?.length" class="empty-row"><td colspan="6">No treks assigned yet.</td></tr>
        </tbody>
      </table>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '../shared/AppLayout.vue'
import api from '../../services/api'
import BookItinerary from './BookItinerary.vue'

const data = ref({})
onMounted(async () => { data.value = (await api.get('/staff/me/dashboard')).data })
function formatDate(d) { return d ? new Date(d).toLocaleDateString() : '' }
function statusBadge(status) { return { Pending: 'gray', Approved: 'blue', Open: 'green', Closed: 'orange', Completed: 'blue' }[status] || 'gray' }
</script>
