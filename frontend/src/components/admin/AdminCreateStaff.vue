<template>
  <AppLayout title="Create New Trekking Staff">
    <div v-if="error" class="alert error">{{ error }}</div>
    <div v-if="success" class="alert success">{{ success }}</div>

    <form @submit.prevent="handleCreate" class="card" style="max-width:600px;">
      <div class="form-row">
        <div class="field"><label>Full Name</label><input v-model="form.name" required /></div>
        <div class="field"><label>Email Address</label><input v-model="form.email" type="email" required /></div>
      </div>
      <div class="form-row">
        <div class="field"><label>Contact Number</label><input v-model="form.contact_number" /></div>
        <div class="field"><label>Password</label><input v-model="form.password" type="password" required minlength="6" /></div>
      </div>
      <div class="form-row">
        <div class="field"><label>Confirm Password</label><input v-model="confirmPassword" type="password" required /></div>
        <div class="field"><label>Experience (years)</label><input v-model.number="form.experience_years" type="number" min="0" /></div>
      </div>
      <div class="field"><label>Specialization</label><input v-model="form.specialization" placeholder="e.g. High Altitude, First Aid" /></div>

      <div style="display:flex; gap:8px;">
        <button type="button" class="btn outline" @click="resetForm">Cancel</button>
        <button type="submit" class="btn" :disabled="loading">{{ loading ? 'Creating...' : 'Create Staff' }}</button>
      </div>
    </form>
  </AppLayout>
</template>

<script setup>
import { reactive, ref } from 'vue'
import AppLayout from '../shared/AppLayout.vue'
import api from '../../services/api'

const blank = () => ({ name: '', email: '', contact_number: '', password: '', specialization: '', experience_years: 0 })
const form = reactive(blank())
const confirmPassword = ref('')
const error = ref('')
const success = ref('')
const loading = ref(false)

function resetForm() {
  Object.assign(form, blank())
  confirmPassword.value = ''; error.value = ''; success.value = ''
}
async function handleCreate() {
  error.value = ''; success.value = ''
  if (form.password !== confirmPassword.value) { error.value = 'Passwords do not match'; return }
  loading.value = true
  try {
    await api.post('/staff', form)
    success.value = `Staff account created for ${form.name}.`
    resetForm()
  } catch (e) {
    error.value = e.response?.data?.error || 'Failed to create staff'
  } finally {
    loading.value = false
  }
}
</script>
