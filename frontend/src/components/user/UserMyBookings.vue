<template>
  <AppLayout title="My Bookings">
    <div class="card">
      <table>
        <thead><tr><th>Trek Name</th><th>Location</th><th>Trek Dates</th><th>Amount</th><th>Payment</th><th>Status</th><th>Action</th></tr></thead>
        <tbody>
          <tr v-for="b in bookings" :key="b.id">
            <td>{{ b.trek_name }}</td>
            <td>{{ b.location }}</td>
            <td>{{ formatDate(b.start_date) }} - {{ formatDate(b.end_date) }}</td>
            <td>₹{{ b.amount?.toLocaleString() }}</td>
            <td>{{ b.payment_method }}</td>
            <td><span class="badge blue">{{ b.status }}</span></td>
            <td><button class="btn small danger" @click="cancelBooking(b)">Cancel</button></td>
          </tr>
          <tr v-if="!bookings.length" class="empty-row"><td colspan="7">You have no active bookings. <router-link to="/user/treks">Browse treks</router-link> to book one.</td></tr>
        </tbody>
      </table>
    </div>
    <ToastNotification ref="toast" />
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '../shared/AppLayout.vue'
import ToastNotification from '../shared/ToastNotification.vue'
import api from '../../services/api'

const bookings = ref([])
const toast = ref(null)

async function fetchBookings() {
  bookings.value = (await api.get('/bookings', { params: { status: 'Booked' } })).data.bookings
}
async function cancelBooking(b) {
  if (!confirm(`Cancel booking for "${b.trek_name}"? Amount will be refunded.`)) return
  await api.put(`/bookings/${b.id}/cancel`)
  toast.value.push('Booking cancelled and refund simulated')
  fetchBookings()
}
function formatDate(d) { return d ? new Date(d).toLocaleDateString() : '' }
onMounted(fetchBookings)
</script>
