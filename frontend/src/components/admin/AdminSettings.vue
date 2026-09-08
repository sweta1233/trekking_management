<template>
  <AppLayout title="Settings">
    <div v-if="error" class="alert error">{{ error }}</div>
    <div v-if="success" class="alert success">{{ success }}</div>

    <div class="card" style="max-width:520px; margin-bottom:16px;">
      <h4 style="margin-top:0;">Admin Account</h4>
      <form @submit.prevent="save">
        <div class="field"><label>Full Name</label><input v-model="form.name" required /></div>
        <div class="field"><label>Email Address</label><input :value="authState.user?.email" disabled /></div>
        <div class="field"><label>New Password (leave blank to keep current)</label><input v-model="form.password" type="password" minlength="6" /></div>
        <button type="submit" class="btn" :disabled="loading">{{ loading ? 'Saving...' : 'Save Changes' }}</button>
      </form>
    </div>

    <div class="card" style="max-width:520px;">
      <h4 style="margin-top:0;">Application Info</h4>
      <ul style="color:var(--muted); font-size:0.88rem; margin:0; padding-left:18px;">
        <li>Redis caching: used for trek listings</li>
        <li>Celery: daily reminders + monthly reports scheduled</li>
        <li>Database: SQLite, stored in backend/instances/</li>
      </ul>
    </div>
  </AppLayout>
</template>

<script setup>
import { reactive, ref } from 'vue'
import AppLayout from '../shared/AppLayout.vue'
import api from '../../services/api'
import { authState } from '../../services/auth'

const form = reactive({ name: authState.user?.name || '', password: '' })
const error = ref('')
const success = ref('')
const loading = ref(false)

async function save() {
  error.value = ''; success.value = ''
  loading.value = true
  try {
    const payload = { name: form.name }
    if (form.password) payload.password = form.password
    const res = await api.put('/users/profile', payload)
    authState.user = res.data.user
    localStorage.setItem('tma_user', JSON.stringify(res.data.user))
    success.value = 'Settings updated successfully.'
    form.password = ''
  } catch (e) {
    error.value = e.response?.data?.error || 'Failed to update settings'
  } finally {
    loading.value = false
  }
}
</script>
