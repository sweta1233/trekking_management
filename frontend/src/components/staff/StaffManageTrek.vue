<template>
  <AppLayout :title="trek ? trek.trek_name : 'Manage Trek'">
    <router-link to="/staff/my-treks">&larr; Back to My Treks</router-link>

    <div v-if="trek" class="grid-3" style="margin-top:14px; align-items:start;">
      <div class="card" style="grid-column: span 1;">
        <h4 style="margin-top:0;">Trek Details</h4>
        <p style="color:var(--muted); font-size:0.82rem; margin-top:-6px;">Location, dates, and pricing are set by Admin. You can manage slots and status below.</p>
        <div class="field"><label>Location</label><input :value="trek.location" disabled /></div>
        <div class="field"><label>Difficulty</label><input :value="trek.difficulty" disabled /></div>
        <div class="field"><label>Price per person</label><input :value="'₹' + trek.price?.toLocaleString()" disabled /></div>
        <div class="form-row">
          <div class="field"><label>Start Date</label><input :value="formatDate(trek.start_date)" disabled /></div>
          <div class="field"><label>End Date</label><input :value="formatDate(trek.end_date)" disabled /></div>
        </div>
        <div class="form-row">
          <div class="field"><label>Available Slots (of {{ trek.total_slots }})</label><input type="number" min="0" :max="trek.total_slots" v-model.number="form.available_slots" /></div>
          <div class="field"><label>Trek Status</label>
            <select v-model="form.status"><option>Open</option><option>Closed</option></select>
          </div>
        </div>
        <div style="display:flex; gap:8px; flex-wrap:wrap;">
          <button class="btn small" @click="updateTrek" :disabled="trek.status==='Completed'">Update Trek</button>
          <button class="btn small outline" @click="completeTrek" :disabled="trek.status==='Completed'">Mark Completed</button>
        </div>
        <div v-if="msg" class="alert success" style="margin-top:12px; margin-bottom:0;">{{ msg }}</div>
      </div>

      <div class="card" style="grid-column: span 2;">
        <h4 style="margin-top:0;">Registered Participants ({{ participants.length }})</h4>
        <table>
          <thead><tr><th>#</th><th>Name</th><th>Booking Date</th><th>Amount</th><th>Status</th></tr></thead>
          <tbody>
            <tr v-for="(p, i) in participants" :key="p.id">
              <td>{{ i + 1 }}</td><td>{{ p.user_name }}</td><td>{{ formatDate(p.booking_date) }}</td>
              <td>₹{{ p.amount?.toLocaleString() }}</td>
              <td><span class="badge" :class="p.status==='Completed' ? 'green' : 'blue'">{{ p.status }}</span></td>
            </tr>
            <tr v-if="!participants.length" class="empty-row"><td colspan="5">No participants yet.</td></tr>
          </tbody>
        </table>
      </div>
    </div>
    <p v-else>Loading...</p>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '../shared/AppLayout.vue'
import api from '../../services/api'

const route = useRoute()
const trek = ref(null)
const participants = ref([])
const msg = ref('')
const form = reactive({ available_slots: 0, status: '' })

async function load() {
  const trekId = route.params.id
  trek.value = (await api.get(`/treks/${trekId}`)).data.trek
  form.available_slots = trek.value.available_slots
  form.status = trek.value.status === 'Closed' ? 'Closed' : 'Open'
  participants.value = (await api.get(`/treks/${trekId}/participants`)).data.participants
}
async function updateTrek() {
  trek.value = (await api.put(`/treks/${trek.value.id}`, { available_slots: form.available_slots, status: form.status })).data.trek
  msg.value = 'Trek updated successfully.'
  setTimeout(() => (msg.value = ''), 2500)
}
async function completeTrek() {
  trek.value = (await api.put(`/treks/${trek.value.id}/complete`)).data.trek
  msg.value = 'Trek marked as completed.'
  load()
}
function formatDate(d) { return d ? new Date(d).toLocaleDateString() : '' }
onMounted(load)
</script>
