<template>
  <AppLayout title="Search">
    <input v-model="query" @input="debouncedFetch" placeholder="Search users, staff, or treks..." style="max-width:420px; margin-bottom:14px;" />

    <div class="tabs">
      <button :class="{active: tab==='users'}" @click="tab='users'">Users ({{ users.length }})</button>
      <button :class="{active: tab==='staff'}" @click="tab='staff'">Trekking Staff ({{ staff.length }})</button>
      <button :class="{active: tab==='treks'}" @click="tab='treks'">Treks ({{ treks.length }})</button>
    </div>

    <div class="card">
      <table v-if="tab==='users'">
        <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Contact</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td>U{{ String(u.id).padStart(3,'0') }}</td><td>{{ u.name }}</td><td>{{ u.email }}</td><td>{{ u.phone || '-' }}</td>
            <td><span class="badge" :class="u.status==='active' ? 'green' : 'red'">{{ u.status }}</span></td>
          </tr>
          <tr v-if="!users.length" class="empty-row"><td colspan="5">{{ query ? 'No matching users.' : 'Type to search users.' }}</td></tr>
        </tbody>
      </table>
      <table v-if="tab==='staff'">
        <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Specialization</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="s in staff" :key="s.id">
            <td>TS{{ String(s.id).padStart(3,'0') }}</td><td>{{ s.name }}</td><td>{{ s.email }}</td><td>{{ s.specialization || '-' }}</td>
            <td><span class="badge" :class="s.status==='active' ? 'green' : 'red'">{{ s.status }}</span></td>
          </tr>
          <tr v-if="!staff.length" class="empty-row"><td colspan="5">{{ query ? 'No matching staff.' : 'Type to search staff.' }}</td></tr>
        </tbody>
      </table>
      <table v-if="tab==='treks'">
        <thead><tr><th>ID</th><th>Trek Name</th><th>Location</th><th>Price</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="t in treks" :key="t.id">
            <td>{{ t.id }}</td><td>{{ t.trek_name }}</td><td>{{ t.location }}</td><td>₹{{ t.price?.toLocaleString() }}</td>
            <td><span class="badge gray">{{ t.status }}</span></td>
          </tr>
          <tr v-if="!treks.length" class="empty-row"><td colspan="5">{{ query ? 'No matching treks.' : 'Type to search treks.' }}</td></tr>
        </tbody>
      </table>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref } from 'vue'
import AppLayout from '../shared/AppLayout.vue'
import api from '../../services/api'

const query = ref('')
const tab = ref('users')
const users = ref([])
const staff = ref([])
const treks = ref([])
let debounceTimer = null

async function runSearch() {
  if (!query.value) { users.value = []; staff.value = []; treks.value = []; return }
  const [uRes, sRes, tRes] = await Promise.all([
    api.get('/users', { params: { search: query.value, per_page: 20 } }),
    api.get('/staff', { params: { search: query.value, per_page: 20 } }),
    api.get('/treks', { params: { search: query.value, status: 'All', per_page: 20 } }),
  ])
  users.value = uRes.data.users; staff.value = sRes.data.staff; treks.value = tRes.data.treks
}
function debouncedFetch() { clearTimeout(debounceTimer); debounceTimer = setTimeout(runSearch, 350) }
</script>
