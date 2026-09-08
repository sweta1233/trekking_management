<template>
  <AppLayout title="Participants">
    <div class="field" style="max-width:320px;">
      <label>Select Trek</label>
      <select v-model="selectedTrekId" @change="loadParticipants">
        <option :value="null">-- Choose a trek --</option>
        <option v-for="t in treks" :key="t.id" :value="t.id">{{ t.trek_name }} ({{ t.location }})</option>
      </select>
    </div>

    <div class="card">
      <table>
        <thead><tr><th>#</th><th>Name</th><th>Booking Date</th><th>Amount</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="(p, i) in participants" :key="p.id">
            <td>{{ i + 1 }}</td><td>{{ p.user_name }}</td><td>{{ formatDate(p.booking_date) }}</td>
            <td>₹{{ p.amount?.toLocaleString() }}</td>
            <td><span class="badge" :class="p.status==='Completed' ? 'green' : 'blue'">{{ p.status }}</span></td>
          </tr>
          <tr v-if="selectedTrekId && !participants.length" class="empty-row"><td colspan="5">No participants for this trek yet.</td></tr>
          <tr v-if="!selectedTrekId" class="empty-row"><td colspan="5">Select a trek above to view its participants.</td></tr>
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
const participants = ref([])
const selectedTrekId = ref(null)

onMounted(async () => { treks.value = (await api.get('/staff/me/dashboard')).data.treks })

async function loadParticipants() {
  participants.value = []
  if (!selectedTrekId.value) return
  participants.value = (await api.get(`/treks/${selectedTrekId.value}/participants`)).data.participants
}
function formatDate(d) { return d ? new Date(d).toLocaleDateString() : '' }
</script>
