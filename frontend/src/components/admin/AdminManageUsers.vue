<template>
  <AppLayout title="Users (Trekkers)">
    <input v-model="search" @input="debouncedFetch" placeholder="Search users..." style="max-width:280px; margin-bottom:14px;" />

    <div class="card">
      <table>
        <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Contact</th><th>Status</th><th>Action</th></tr></thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td>U{{ String(u.id).padStart(3,'0') }}</td>
            <td>{{ u.name }}</td>
            <td>{{ u.email }}</td>
            <td>{{ u.phone || '-' }}</td>
            <td><span class="badge" :class="statusBadge(u.status)">{{ capitalize(u.status) }}</span></td>
            <td>
              <button v-if="u.status !== 'blacklisted'" class="btn small danger" @click="setStatus(u, 'blacklisted')">Blacklist</button>
              <button v-else class="btn small outline" @click="setStatus(u, 'active')">Whitelist</button>
              <button v-if="u.status === 'active'" class="btn small outline" @click="setStatus(u, 'inactive')">Deactivate</button>
              <button v-else-if="u.status === 'inactive'" class="btn small outline" @click="setStatus(u, 'active')">Activate</button>
            </td>
          </tr>
          <tr v-if="!users.length" class="empty-row"><td colspan="6">No users found.</td></tr>
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

const users = ref([])
const search = ref('')
const toast = ref(null)
let debounceTimer = null

async function fetchUsers() {
  const res = await api.get('/users', { params: { search: search.value } })
  users.value = res.data.users
}
function debouncedFetch() { clearTimeout(debounceTimer); debounceTimer = setTimeout(fetchUsers, 350) }
async function setStatus(user, status) {
  await api.put(`/users/${user.id}/status`, { status })
  toast.value.push(`User status updated to ${status}`)
  fetchUsers()
}
function statusBadge(status) { return { active: 'green', inactive: 'gray', blacklisted: 'red' }[status] || 'gray' }
function capitalize(s) { return s ? s.charAt(0).toUpperCase() + s.slice(1) : '' }
onMounted(fetchUsers)
</script>
