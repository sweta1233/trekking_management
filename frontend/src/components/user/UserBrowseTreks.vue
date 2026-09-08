<template>
  <AppLayout title="Browse Treks">
    <div class="form-row" style="margin-bottom:16px; flex-wrap:wrap;">
      <div class="field" style="max-width:260px;"><input v-model="filters.search" @input="debouncedFetch" placeholder="Search treks..." /></div>
      <div class="field" style="max-width:180px;">
        <select v-model="filters.difficulty" @change="fetchTreks">
          <option value="All">Difficulty: All</option><option>Easy</option><option>Moderate</option><option>Hard</option>
        </select>
      </div>
      <div class="field" style="max-width:180px;">
        <select v-model="filters.location" @change="fetchTreks">
          <option value="All">Location: All</option>
          <option v-for="loc in locations" :key="loc" :value="loc">{{ loc }}</option>
        </select>
      </div>
      <div class="field" style="max-width:180px;">
        <select v-model="durationBucket" @change="onDurationChange">
          <option value="any">Duration: Any</option>
          <option value="1-3">1–3 Days</option>
          <option value="4-7">4–7 Days</option>
          <option value="8-14">8–14 Days</option>
          <option value="15-999">15+ Days</option>
        </select>
      </div>
      <div class="field" style="max-width:160px;">
        <select v-model="filters.status" @change="fetchTreks">
          <option value="Open">Open Only</option><option value="All">All Status</option>
        </select>
      </div>
    </div>

    <div v-if="msg" class="alert success">{{ msg }}</div>

    <div class="grid-3">
      <TrekCard v-for="t in treks" :key="t.id" :trek="t">
        <p style="font-size:0.85rem; color:var(--muted);">{{ t.description }}</p>
        <button class="btn block" :disabled="t.available_slots<=0 || t.status!=='Open'" @click="openPayment(t)">
          {{ t.status!=='Open' ? 'Not Available' : (t.available_slots > 0 ? 'Book Now' : 'Not Available') }}
        </button>
      </TrekCard>
    </div>
    <p v-if="!treks.length" style="color:var(--muted);">No treks match your search/filters.</p>

    <div class="pager" v-if="pages > 1">
      <button class="btn small outline" :disabled="page<=1" @click="page--; fetchTreks()">&lsaquo; Prev</button>
      <span>Page {{ page }} / {{ pages }}</span>
      <button class="btn small outline" :disabled="page>=pages" @click="page++; fetchTreks()">Next &rsaquo;</button>
    </div>

    <PaymentModal v-if="selectedTrek" :trek="selectedTrek" @close="closePayment" @booked="onBooked" />
  </AppLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import AppLayout from '../shared/AppLayout.vue'
import TrekCard from '../shared/TrekCard.vue'
import PaymentModal from '../shared/PaymentModal.vue'
import api from '../../services/api'

const treks = ref([])
const locations = ref([])
const page = ref(1)
const pages = ref(1)
const msg = ref('')
const selectedTrek = ref(null)
const durationBucket = ref('any')
const filters = reactive({ search: '', difficulty: 'All', location: 'All', status: 'Open' })
let debounceTimer = null

async function fetchTreks() {
  const params = { ...filters, page: page.value }
  if (durationBucket.value !== 'any') {
    const [min, max] = durationBucket.value.split('-').map(Number)
    params.min_duration = min
    params.max_duration = max
  }
  const res = await api.get('/treks', { params })
  treks.value = res.data.treks
  pages.value = res.data.pages
  const locs = new Set(treks.value.map(t => t.location))
  locs.forEach(l => { if (!locations.value.includes(l)) locations.value.push(l) })
}
function debouncedFetch() { clearTimeout(debounceTimer); debounceTimer = setTimeout(() => { page.value = 1; fetchTreks() }, 350) }
function onDurationChange() { page.value = 1; fetchTreks() }

function openPayment(trek) { selectedTrek.value = trek }
function closePayment() { selectedTrek.value = null; fetchTreks() }
function onBooked(booking) {
  msg.value = `Booked "${selectedTrek.value.trek_name}" successfully — payment confirmed.`
  setTimeout(() => (msg.value = ''), 4000)
}

onMounted(fetchTreks)
</script>
