<template>
  <div class="trip-plan-container">
    <div class="trip-header" style="background: linear-gradient(135deg, #ff6b6b, #feca57); color:white; padding:24px; border-radius:12px;">
      <h2>Plan Your Trip</h2>
      <p>5-day budget itinerary generator with live updates</p>
    </div>
    <div class="trip-body" style="padding:20px;">
      <div class="form-row" style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
        <label>Budget ₹<input v-model="budget" type="number" placeholder="15000" style="padding:8px; border-radius:6px; width:120px;" /></label>
        <label>Days<input v-model="days" type="number" placeholder="5" style="padding:8px; border-radius:6px; width:60px;" /></label>
        <label>City<input v-model="city" placeholder="Manali / Himalaya" style="padding:8px; border-radius:6px; width:160px;" /></label>
        <button @click="generatePlan" style="background:#667eea; color:white; padding:8px 16px; border:none; border-radius:6px; font-weight:600;">Generate Plan</button>
      </div>
      <div v-if="plan" style="margin-top:20px; background:linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding:20px; border-radius:12px; color:white;">
        <h3>Itinerary for {{ city || 'your destination' }}</h3>
        <div v-for="(item,i) in plan.itinerary" :key="i" style="margin-bottom:12px; padding:14px; background:rgba(255,255,255,0.15); border-radius:10px; backdrop-filter:blur(8px); border-left:4px solid #feca57;">
          <strong>Day {{ item.day }} — {{ item.place }}</strong><br/>
          <span style="font-size:0.9rem; opacity:0.9;">{{ item.activity }}</span><br/>
          <span style="font-size:0.85rem; opacity:0.8;">Ticket: ₹{{ item.ticket }} | Time left: {{ timeLeft(i) }}</span>
        </div>
        <div style="margin-top:14px; font-weight:700; font-size:1.2rem;">Remaining Budget: ₹{{ remainingBudget }}</div>
      </div>
      <p style="margin-top:12px; font-size:0.85rem; color:#777;">Live update every few seconds: budget, days remaining, itinerary.</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TripPlan',
  data() {
    return {
      budget: 15000,
      days: 5,
      city: 'Manali',
      plan: null,
      timer: null,
    }
  },
  computed: {
    remainingBudget() {
      if (!this.plan) return this.budget
      const spent = this.plan.itinerary.reduce((s, item) => s + item.ticket, 0)
      return Math.max(0, this.budget - spent)
    }
  },
  methods: {
    generatePlan() {
      const d = parseInt(this.days) || 5
      const places = ['Base Camp', 'Lake View', 'Temple Trail', 'Mountain Top', 'Local Market', 'Forest Path', 'Waterfall']
      const itinerary = Array.from({ length: d }, (_, i) => ({
        day: i + 1,
        place: places[i % places.length],
        activity: i % 3 === 0 ? 'Trekking & Sightseeing' : (i % 3 === 1 ? 'Rest & Photography' : 'Hostel & Local Food'),
        ticket: Math.round(800 + Math.random() * 1200),
      }))
      this.plan = { itinerary }
      // Live update simulation
      if (this.timer) clearInterval(this.timer)
      this.timer = setInterval(() => {
        // simulate time passing reducing budget slightly
        this.budget = Math.max(0, this.budget - 50)
      }, 3000)
    },
    timeLeft(idx) {
      const left = Math.max(0, (this.days || 5) - (idx + 1))
      return left + ' day(s) left to visit'
    }
  },
  beforeUnmount() {
    if (this.timer) clearInterval(this.timer)
  }
}
</script>

<style scoped>
.trip-plan-container {
  max-width: 900px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}
</style>
