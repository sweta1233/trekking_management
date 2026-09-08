<template>
  <AppLayout title="Treks">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
      <input v-model="search" @input="debouncedFetch" placeholder="Search treks..." style="max-width:280px;" />
      <button class="btn" @click="openCreate">+ Add New Trek</button>
    </div>

    <div v-if="showForm" class="card" style="margin-bottom:16px;">
      <h4 style="margin-top:0;">{{ editingTrek ? 'Edit Trek' : 'Add New Trek' }}</h4>
      <div v-if="formError" class="alert error">{{ formError }}</div>
      <form @submit.prevent="saveTrek">
        <div class="form-row">
          <div class="field"><label>Trek Name</label><input v-model="form.trek_name" required /></div>
          <div class="field"><label>Location</label><input v-model="form.location" required /></div>
        </div>
        <div class="form-row">
          <div class="field"><label>Difficulty</label>
            <select v-model="form.difficulty"><option>Easy</option><option>Moderate</option><option>Hard</option></select>
          </div>
          <div class="field"><label>Duration (days)</label><input v-model.number="form.duration" type="number" min="1" required /></div>
          <div class="field"><label>Price per person (₹)</label><input v-model.number="form.price" type="number" min="0" required /></div>
        </div>
        <div class="form-row">
          <div class="field"><label>Available Slots</label><input v-model.number="form.available_slots" type="number" min="0" required /></div>
          <div class="field"><label>Status</label>
            <select v-model="form.status"><option>Pending</option><option>Approved</option><option>Open</option><option>Closed</option><option>Completed</option></select>
            <small style="color:var(--muted);">Only "Open" treks are visible/bookable for trekkers.</small>
          </div>
        </div>
        <div class="form-row">
          <div class="field"><label>Start Date</label><input v-model="form.start_date" type="date" required /></div>
          <div class="field"><label>End Date</label><input v-model="form.end_date" type="date" required /></div>
        </div>
        <div class="field">
          <label>Assign Staff</label>
          <select v-model="form.assigned_staff_id">
            <option :value="null">-- Unassigned --</option>
            <option v-for="s in staffList" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select>
        </div>
        <div class="field"><label>Description</label><textarea v-model="form.description" rows="2"></textarea></div>
        <div class="field"><label>Image URL</label><input v-model="form.image" placeholder="https://..." /></div>

        <div style="display:flex; gap:8px;">
          <button type="button" class="btn outline" @click="showForm=false">Cancel</button>
          <button type="submit" class="btn">{{ editingTrek ? 'Save Changes' : 'Create Trek' }}</button>
        </div>
      </form>
    </div>

    <div class="card">
      <table>
        <thead><tr><th>ID</th><th>Trek Name</th><th>Location</th><th>Difficulty</th><th>Price</th><th>Slots</th><th>Status</th><th>Actions</th></tr></thead>
        <tbody>
          <tr v-for="t in treks" :key="t.id">
            <td>{{ t.id }}</td>
            <td>{{ t.trek_name }}</td>
            <td>{{ t.location }}</td>
            <td>{{ t.difficulty }}</td>
            <td>₹{{ t.price?.toLocaleString() }}</td>
            <td>{{ t.available_slots }} / {{ t.total_slots }}</td>
            <td><span class="badge" :class="statusBadge(t.status)">{{ t.status }}</span></td>
            <td>
              <button class="btn small outline" @click="openEdit(t)">Edit</button>
              <button class="btn small danger" @click="removeTrek(t)">Delete</button>
            </td>
          </tr>
          <tr v-if="!treks.length" class="empty-row"><td colspan="8">No treks found.</td></tr>
        </tbody>
      </table>
      <div class="pager" v-if="pages > 1">
        <button class="btn small outline" :disabled="page<=1" @click="page--; fetchTreks()">&lsaquo; Prev</button>
        <span>Page {{ page }} / {{ pages }}</span>
        <button class="btn small outline" :disabled="page>=pages" @click="page++; fetchTreks()">Next &rsaquo;</button>
      </div>
    </div>

    <ToastNotification ref="toast" />
  </AppLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import AppLayout from '../shared/AppLayout.vue'
import ToastNotification from '../shared/ToastNotification.vue'
import api from '../../services/api'

const treks = ref([])
const staffList = ref([])
const search = ref('')
const page = ref(1)
const pages = ref(1)
const editingTrek = ref(null)
const showForm = ref(false)
const formError = ref('')
const toast = ref(null)
let debounceTimer = null

const blankForm = () => ({
  trek_name: '', location: '', difficulty: 'Easy', duration: 1, price: 0, available_slots: 0,
  status: 'Open', start_date: '', end_date: '', assigned_staff_id: null, description: '', image: '',
})
const form = reactive(blankForm())

async function fetchTreks() {
  const res = await api.get('/treks', { params: { search: search.value, page: page.value } })
  treks.value = res.data.treks
  pages.value = res.data.pages
}
async function fetchStaff() {
  const res = await api.get('/staff', { params: { per_page: 100 } })
  staffList.value = res.data.staff
}
function debouncedFetch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => { page.value = 1; fetchTreks() }, 350)
}
function openCreate() {
  editingTrek.value = null
  Object.assign(form, blankForm())
  formError.value = ''
  showForm.value = true
}
function openEdit(trek) {
  editingTrek.value = trek
  Object.assign(form, {
    trek_name: trek.trek_name, location: trek.location, difficulty: trek.difficulty, duration: trek.duration,
    price: trek.price, available_slots: trek.available_slots, status: trek.status,
    start_date: trek.start_date, end_date: trek.end_date, assigned_staff_id: trek.assigned_staff_id,
    description: trek.description, image: trek.image,
  })
  formError.value = ''
  showForm.value = true
}
async function saveTrek() {
  formError.value = ''
  try {
    if (editingTrek.value) {
      await api.put(`/treks/${editingTrek.value.id}`, form)
      toast.value.push('Trek updated successfully')
    } else {
      await api.post('/treks', form)
      toast.value.push('Trek created successfully')
    }
    showForm.value = false
    fetchTreks()
  } catch (e) {
    formError.value = e.response?.data?.error || 'Failed to save trek'
  }
}
async function removeTrek(trek) {
  if (!confirm(`Delete trek "${trek.trek_name}"?`)) return
  await api.delete(`/treks/${trek.id}`)
  toast.value.push('Trek deleted')
  fetchTreks()
}
function statusBadge(status) {
  return { Pending: 'gray', Approved: 'blue', Open: 'green', Closed: 'orange', Completed: 'blue' }[status] || 'gray'
}

onMounted(() => { fetchTreks(); fetchStaff() })
</script>
