<template>
  <AppLayout title="All Bookings">
    <div class="form-row" style="margin-bottom:14px; max-width:520px;">
      <div class="field"><input v-model="search" @input="debouncedFetch" placeholder="Search by user or trek name..." /></div>
      <div class="field">
        <select v-model="status" @change="fetchBookings">
          <option value="">All Status</option>
          <option>Booked</option><option>Cancelled</option><option>Completed</option>
        </select>
      </div>
    </div>

    <div class="card">
      <table>
        <thead><tr><th>ID</th><th>User</th><th>Trek</th><th>Amount</th><th>Payment</th><th>Trek Dates</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="b in bookings" :key="b.id">
            <td>#{{ b.id }}</td>
            <td>{{ b.user_name }}</td>
            <td>{{ b.trek_name }}</td>
            <td>₹{{ b.amount?.toLocaleString() }}</td>
            <td>{{ b.payment_method }} · <span class="badge outline">{{ b.payment_status }}</span></td>
            <td>{{ formatDate(b.start_date) }} - {{ formatDate(b.end_date) }}</td>
            <td><span class="badge" :class="statusBadge(b.status)">{{ b.status }}</span></td>
          </tr>
          <tr v-if="!bookings.length" class="empty-row"><td colspan="7">No bookings found.</td></tr>
        </tbody>
      </table>
      <div class="pager" v-if="pages > 1">
        <button class="btn small outline" :disabled="page<=1" @click="page--; fetchBookings()">&lsaquo; Prev</button>
        <span>Page {{ page }} / {{ pages }}</span>
        <button class="btn small outline" :disabled="page>=pages" @click="page++; fetchBookings()">Next &rsaquo;</button>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '../shared/AppLayout.vue'
import api from '../../services/api'

const bookings = ref([])
const search = ref('')
const status = ref('')
const page = ref(1)
const pages = ref(1)
let debounceTimer = null

async function fetchBookings() {
  const res = await api.get('/bookings', { params: { search: search.value, status: status.value, page: page.value } })
  bookings.value = res.data.bookings
  pages.value = res.data.pages
}
function debouncedFetch() { clearTimeout(debounceTimer); debounceTimer = setTimeout(() => { page.value = 1; fetchBookings() }, 350) }
function formatDate(d) { return d ? new Date(d).toLocaleDateString() : '' }
function statusBadge(status) { return { Booked: 'blue', Cancelled: 'red', Completed: 'green' }[status] || 'gray' }
onMounted(fetchBookings)
</script>
