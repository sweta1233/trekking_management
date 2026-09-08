<template>
  <AppLayout title="My Treks">
    <div class="card">
      <table>
        <thead><tr><th>Trek Name</th><th>Location</th><th>Difficulty</th><th>Dates</th><th>Slots</th><th>Status</th><th>Action</th></tr></thead>
        <tbody>
          <tr v-for="t in treks" :key="t.id">
            <td>{{ t.trek_name }}</td>
            <td>{{ t.location }}</td>
            <td>{{ t.difficulty }}</td>
            <td>{{ formatDate(t.start_date) }} - {{ formatDate(t.end_date) }}</td>
            <td>{{ t.available_slots }} / {{ t.total_slots }}</td>
            <td><span class="badge" :class="statusBadge(t.status)">{{ t.status }}</span></td>
            <td><router-link :to="`/staff/treks/${t.id}`" class="btn small">{{ t.status === 'Completed' ? 'View' : 'Manage' }}</router-link></td>
          </tr>
          <tr v-if="!treks.length" class="empty-row"><td colspan="7">No treks assigned yet.</td></tr>
        </tbody>
      </table>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '../shared/AppLayout.vue'
import api from '../../services/api'

const treks = ref([])
onMounted(async () => { treks.value = (await api.get('/staff/me/dashboard')).data.treks })
function formatDate(d) { return d ? new Date(d).toLocaleDateString() : '' }
function statusBadge(status) { return { Pending: 'gray', Approved: 'blue', Open: 'green', Closed: 'orange', Completed: 'blue' }[status] || 'gray' }
</script>
