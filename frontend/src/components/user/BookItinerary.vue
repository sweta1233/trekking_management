<template>
  <div class="book-itinerary-card card">
    <h3>Book Itinerary</h3>
    <p>Plan and confirm your trekking itinerary.</p>
    <form @submit.prevent="submitBooking" style="display:flex; flex-direction:column; gap:10px;">
      <input v-model="form.trek" placeholder="Trek Name" required style="padding:10px; border-radius:8px; border:1px solid #ccc;" />
      <input v-model="form.start" type="date" required style="padding:10px; border-radius:8px; border:1px solid #ccc;" />
      <input v-model="form.end" type="date" required style="padding:10px; border-radius:8px; border:1px solid #ccc;" />
      <input v-model="form.participants" type="number" placeholder="Participants" min="1" required style="padding:10px; border-radius:8px; border:1px solid #ccc;" />
      <button type="submit" style="padding:12px; border-radius:8px; background:#1f6f54; color:white; border:none; font-weight:600;">Confirm Booking</button>
    </form>
    <p v-if="msg" style="margin-top:8px; font-size:13px; color:#1f6f54;">{{ msg }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const form = ref({ trek: '', start: '', end: '', participants: 1 })
const msg = ref('')
function submitBooking() {
  msg.value = 'Booking confirmed for ' + form.value.trek + ' — check My Bookings.'
  form.value = { trek: '', start: '', end: '', participants: 1 }
}
</script>
