<template>
  <AppLayout title="Trekking History">
    <div style="display:flex; justify-content:space-between; margin-bottom:14px;">
      <div class="tabs" style="border-bottom:none; margin-bottom:0;">
        <button :class="{active: filter==='All'}" @click="filter='All'">All</button>
        <button :class="{active: filter==='Booked'}" @click="filter='Booked'">Booked</button>
        <button :class="{active: filter==='Completed'}" @click="filter='Completed'">Completed</button>
        <button :class="{active: filter==='Cancelled'}" @click="filter='Cancelled'">Cancelled</button>
      </div>
      <button class="btn" @click="exportHistory" :disabled="exporting">{{ exporting ? 'Exporting...' : 'Export History' }}</button>
    </div>

    <div v-if="exportMsg" class="alert success">{{ exportMsg }}</div>

    <div class="card">
      <table>
        <thead><tr><th>Trek Name</th><th>Trek Dates</th><th>Amount</th><th>Completed On</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="b in filteredBookings" :key="b.id">
            <td>{{ b.trek_name }}</td>
            <td>{{ formatDate(b.start_date) }} - {{ formatDate(b.end_date) }}</td>
            <td>₹{{ b.amount?.toLocaleString() }}</td>
            <td>{{ b.completed_date ? formatDate(b.completed_date) : '-' }}</td>
            <td><span class="badge" :class="statusBadge(b.status)">{{ b.status }}</span></td>
          </tr>
          <tr v-if="!filteredBookings.length" class="empty-row"><td colspan="5">No records found.</td></tr>
        </tbody>
      </table>
    </div>

  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppLayout from '../shared/AppLayout.vue'
import api from '../../services/api'

const bookings = ref([])
const filter = ref('All')
const exporting = ref(false)
const exportMsg = ref('')

const filteredBookings = computed(() => filter.value === 'All' ? bookings.value : bookings.value.filter(b => b.status === filter.value))

async function fetchHistory() { bookings.value = (await api.get('/bookings')).data.bookings }

async function exportHistory() {
  exporting.value = true
  exportMsg.value = ''
  try {
    const res = await api.post('/bookings/export')
    pollExport(res.data.task_id)
  } catch (e) {
    exporting.value = false
  }
}
function pollExport(taskId) {
  const interval = setInterval(async () => {
    const res = await api.get(`/bookings/export/${taskId}`)
    if (res.data.state === 'SUCCESS') {
      clearInterval(interval)
      await downloadExport(taskId)
      exporting.value = false
    } else if (res.data.state === 'FAILURE') {
      clearInterval(interval)
      exporting.value = false
      exportMsg.value = 'Export failed. Please try again.'
    }
  }, 1500)
}

async function downloadExport(taskId) {
  try {
    const res = await api.get(`/bookings/export/${taskId}/download`, { responseType: 'blob' })
    const disposition = res.headers['content-disposition'] || ''
    const match = disposition.match(/filename="?([^"]+)"?/)
    const filename = match ? match[1] : 'booking_history.csv'

    const url = window.URL.createObjectURL(new Blob([res.data], { type: 'text/csv' }))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)

    exportMsg.value = 'Your booking history CSV has been downloaded.'
  } catch (e) {
    exportMsg.value = 'Could not download the export. Please try again.'
  }
}
function formatDate(d) { return d ? new Date(d).toLocaleDateString() : '' }
function statusBadge(status) { return { Booked: 'blue', Cancelled: 'red', Completed: 'green' }[status] || 'gray' }
onMounted(fetchHistory)
</script>
