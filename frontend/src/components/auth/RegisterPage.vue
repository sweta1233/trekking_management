<template>
  <div class="auth-wrap">
    <div class="auth-shell">
      <div class="auth-hero">
        <div class="hero-brand">Trekking Mgmt<small>Application</small></div>
        <div>
          <div class="hero-tagline">Your next trail starts here.</div>
          <div class="hero-sub">Create your trekker account to browse treks, book your spot, and track your trekking history.</div>
        </div>
      </div>

      <div class="auth-panel">
        <h2>Create Account</h2>
        <div class="subtitle">Register as a Trekker</div>

        <div v-if="error" class="alert error">{{ error }}</div>
        <div v-if="success" class="alert success">{{ success }}</div>

        <form @submit.prevent="handleRegister">
          <div class="field"><label>Full Name</label><input v-model="form.name" required /></div>
          <div class="field"><label>Email address</label><input v-model="form.email" type="email" required /></div>
          <div class="form-row">
            <div class="field"><label>Password</label><input v-model="form.password" type="password" required minlength="6" /></div>
            <div class="field"><label>Confirm Password</label><input v-model="confirmPassword" type="password" required /></div>
          </div>
          <div class="field"><label>Contact Number</label><input v-model="form.phone" /></div>
          <button type="submit" class="btn block" :disabled="loading">{{ loading ? 'Creating account...' : 'Register' }}</button>
        </form>

        <p style="text-align:center; margin-top:14px;">Already have an account? <router-link to="/login">Login here</router-link></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '../../services/auth'

const router = useRouter()
const form = reactive({ name: '', email: '', password: '', phone: '' })
const confirmPassword = ref('')
const error = ref('')
const success = ref('')
const loading = ref(false)

async function handleRegister() {
  error.value = ''; success.value = ''
  if (form.password !== confirmPassword.value) { error.value = 'Passwords do not match'; return }
  loading.value = true
  try {
    await register(form)
    success.value = 'Registration successful! Redirecting to login...'
    setTimeout(() => router.push('/login'), 1200)
  } catch (e) {
    error.value = e.response?.data?.error || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>
