<template>
  <div class="book-itinerary">
    <h3>Book Itinerary</h3>
    <p>Plan and confirm your trekking itinerary.</p>
    <form @submit.prevent="submitBooking" style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
      <div class="field">
        <label>Trek Name</label>
        <input v-model="form.trek" placeholder="e.g. Annapurna Base Camp" required />
      </div>
      <div class="field">
        <label>Start Date</label>
        <input v-model="form.start" type="date" required />
      </div>
      <div class="field">
        <label>End Date</label>
        <input v-model="form.end" type="date" required />
      </div>
      <div class="field">
        <label>Participants</label>
        <input v-model.number="form.participants" type="number" min="1" required />
      </div>
      <div class="field" style="grid-column: span 2;">
        <label>Budget (₹)</label>
        <input v-model.number="form.budget" type="number" placeholder="Estimated budget" />
      </div>
      <button type="submit" class="btn" style="grid-column: span 2;">Confirm Booking</button>
    </form>
    <p v-if="msg" style="margin-top:8px; font-size:13px; color:#1f6f54;">{{ msg }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const form = ref({ trek: '', start: '', end: '', participants: 1, budget: null })
const msg = ref('')
function submitBooking() {
  msg.value = 'Booking confirmed for "' + form.value.trek + '" from ' + form.value.start + ' to ' + form.value.end
  form.value = { trek: '', start: '', end: '', participants: 1, budget: null }
}
</script>

<style scoped>
.book-itinerary {
  background: #fff;
  border: 1px solid #e2e5e4;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 24px;
}
.book-itinerary h3 { margin: 0 0 4px; font-size: 1.1rem; color: #1f6f54; }
.book-itinerary p { margin: 0 0 12px; font-size: 0.85rem; color: #767676; }
.field label { font-size: 0.8rem; color: #767676; margin-bottom: 4px; }
.field input {
  width: 100%; padding: 9px 10px; border: 1px solid #e2e5e4;
  border-radius: 8px; font-size: 0.95rem; background: #fff;
}
</style>
