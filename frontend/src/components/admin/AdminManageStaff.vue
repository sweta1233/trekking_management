<template>
  <AppLayout title="Trekking Staff">
    <div style="display:flex; justify-content:space-between; margin-bottom:14px;">
      <input v-model="search" @input="debouncedFetch" placeholder="Search trekking staff..." style="max-width:280px;" />
      <router-link to="/admin/staff/create" class="btn">+ Add Staff</router-link>
    </div>

    <div v-if="editingStaff" class="card" style="margin-bottom:16px;">
      <h4 style="margin-top:0;">Edit Staff — {{ editingStaff.name }}</h4>
      <div v-if="editError" class="alert error">{{ editError }}</div>
      <form @submit.prevent="saveEdit">
        <div class="form-row">
          <div class="field"><label>Full Name</label><input v-model="editForm.name" required /></div>
          <div class="field"><label>Contact Number</label><input v-model="editForm.contact_number" /></div>
        </div>
        <div class="form-row">
          <div class="field"><label>Specialization</label><input v-model="editForm.specialization" /></div>
          <div class="field"><label>Experience (years)</label><input v-model.number="editForm.experience_years" type="number" min="0" /></div>
        </div>
        <div style="display:flex; gap:8px;">
          <button type="button" class="btn outline" @click="editingStaff = null">Cancel</button>
          <button type="submit" class="btn">Save Changes</button>
        </div>
      </form>
    </div>

    <div class="card">
      <table>
        <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Contact</th><th>Specialization</th><th>Status</th><th>Action</th></tr></thead>
        <tbody>
          <tr v-for="s in staffList" :key="s.id">
            <td>TS{{ String(s.id).padStart(3,'0') }}</td>
            <td>{{ s.name }}</td>
            <td>{{ s.email }}</td>
            <td>{{ s.contact_number || '-' }}</td>
            <td>{{ s.specialization || '-' }}</td>
            <td><span class="badge" :class="statusBadge(s.status)">{{ capitalize(s.status) }}</span></td>
            <td>
              <button class="btn small outline" @click="openEdit(s)">Edit</button>
              <button v-if="s.status !== 'blacklisted'" class="btn small danger" @click="setStatus(s, 'blacklisted')">Blacklist</button>
              <button v-else class="btn small outline" @click="setStatus(s, 'active')">Whitelist</button>
              <button v-if="s.status === 'active'" class="btn small outline" @click="setStatus(s, 'inactive')">Deactivate</button>
              <button v-else-if="s.status === 'inactive'" class="btn small outline" @click="setStatus(s, 'active')">Activate</button>
              <button class="btn small outline" @click="removeStaff(s)">Delete</button>
            </td>
          </tr>
          <tr v-if="!staffList.length" class="empty-row"><td colspan="7">No staff found.</td></tr>
        </tbody>
      </table>
    </div>

    <ToastNotification ref="toast" />
  </AppLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import AppLayout from '../shared/AppLayout.vue'
import ToastNotification from '../shared/ToastNotification.vue'
import api from '../../services/api'

const staffList = ref([])
const search = ref('')
const toast = ref(null)
const editingStaff = ref(null)
const editForm = reactive({ name: '', contact_number: '', specialization: '', experience_years: 0 })
const editError = ref('')
let debounceTimer = null

async function fetchStaff() {
  const res = await api.get('/staff', { params: { search: search.value } })
  staffList.value = res.data.staff
}
function debouncedFetch() { clearTimeout(debounceTimer); debounceTimer = setTimeout(fetchStaff, 350) }

function openEdit(staff) {
  editingStaff.value = staff
  editError.value = ''
  Object.assign(editForm, {
    name: staff.name, contact_number: staff.contact_number, specialization: staff.specialization,
    experience_years: staff.experience_years,
  })
}
async function saveEdit() {
  editError.value = ''
  try {
    await api.put(`/staff/${editingStaff.value.id}`, editForm)
    toast.value.push('Staff details updated')
    editingStaff.value = null
    fetchStaff()
  } catch (e) {
    editError.value = e.response?.data?.error || 'Failed to update staff'
  }
}

async function setStatus(staff, status) {
  await api.put(`/staff/${staff.id}/status`, { status })
  toast.value.push(`Staff status updated to ${status}`)
  fetchStaff()
}
async function removeStaff(staff) {
  if (!confirm(`Delete staff "${staff.name}"?`)) return
  await api.delete(`/staff/${staff.id}`)
  toast.value.push('Staff deleted')
  fetchStaff()
}
function statusBadge(status) { return { active: 'green', inactive: 'gray', blacklisted: 'red' }[status] || 'gray' }
function capitalize(s) { return s ? s.charAt(0).toUpperCase() + s.slice(1) : '' }

onMounted(fetchStaff)
</script>
