<template>
  <AppLayout title="Edit Profile">
    <div v-if="error" class="alert error">{{ error }}</div>
    <div v-if="success" class="alert success">{{ success }}</div>

    <form @submit.prevent="save" class="card" style="max-width:480px;">
      <div class="field"><label>Full Name</label><input v-model="form.name" required /></div>
      <div class="field"><label>Email Address</label><input :value="authState.user?.email" disabled /></div>
      <div class="field"><label>Contact Number</label><input v-model="form.phone" /></div>
      <div class="field"><label>New Password (leave blank to keep current)</label><input v-model="form.password" type="password" minlength="6" /></div>
      <button type="submit" class="btn" :disabled="loading">{{ loading ? 'Saving...' : 'Save Changes' }}</button>
    </form>
  </AppLayout>
</template>

<script setup>
import { reactive, ref } from 'vue'
import AppLayout from '../shared/AppLayout.vue'
import api from '../../services/api'
import { authState } from '../../services/auth'

const form = reactive({ name: authState.user?.name || '', phone: authState.user?.phone || '', password: '' })
const error = ref('')
const success = ref('')
const loading = ref(false)

async function save() {
  error.value = ''; success.value = ''
  loading.value = true
  try {
    const payload = { name: form.name, phone: form.phone }
    if (form.password) payload.password = form.password
    const res = await api.put('/users/profile', payload)
    authState.user = res.data.user
    localStorage.setItem('tma_user', JSON.stringify(res.data.user))
    success.value = 'Profile updated successfully.'
    form.password = ''
  } catch (e) {
    error.value = e.response?.data?.error || 'Failed to update profile'
  } finally {
    loading.value = false
  }
}
</script>
