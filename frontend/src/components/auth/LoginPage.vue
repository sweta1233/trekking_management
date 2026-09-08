<template>
  <div class="auth-wrap">
    <div class="auth-shell">
      <div class="auth-hero">
        <div class="hero-brand">Trekking Mgmt<small>Application</small></div>
        <div>
          <div class="hero-tagline">Adventure awaits at every trail.</div>
          <div class="hero-sub">Plan, book, and manage treks across the Himalayas — from base camps to summit trails.</div>
        </div>
      </div>

      <div class="auth-panel">
        <h2>Welcome Back</h2>
        <div class="subtitle">Login to your Trekking Management account</div>

        <label>I am logging in as</label>
        <div class="role-pick">
          <button :class="{active: role==='admin'}" @click="selectRole('admin')">Admin</button>
          <button :class="{active: role==='staff'}" @click="selectRole('staff')">Trekking Staff</button>
          <button :class="{active: role==='user'}" @click="selectRole('user')">User (Trekker)</button>
        </div>

        <div v-if="error" class="alert error">{{ error }}</div>
        <div v-if="info" class="alert info">{{ info }}</div>

        <div v-if="role !== 'admin'" class="role-pick" style="margin-bottom:16px;">
          <button :class="{active: mode==='password'}" @click="switchMode('password')">Password</button>
          <button :class="{active: mode==='otp'}" @click="switchMode('otp')">Login with OTP</button>
        </div>

        <form v-if="mode==='password'" @submit.prevent="handleLogin">
          <div class="field">
            <label>Email address</label>
            <input v-model="email" type="email" required placeholder="you@example.com" />
          </div>
          <div class="field">
            <label>Password</label>
            <input v-model="password" type="password" required placeholder="••••••••" />
          </div>
          <button type="submit" class="btn block" :disabled="loading">{{ loading ? 'Logging in...' : 'Login' }}</button>
        </form>

        <form v-else-if="!otpSent" @submit.prevent="handleRequestOtp">
          <div class="field">
            <label>Email address</label>
            <input v-model="email" type="email" required placeholder="you@example.com" />
          </div>
          <button type="submit" class="btn block" :disabled="loading">{{ loading ? 'Sending code...' : 'Send OTP' }}</button>
        </form>

        <form v-else @submit.prevent="handleVerifyOtp">
          <div class="field">
            <label>Enter the 6-digit code sent to {{ email }}</label>
            <input v-model="otp" inputmode="numeric" maxlength="6" required placeholder="123456" />
          </div>
          <button type="submit" class="btn block" :disabled="loading">{{ loading ? 'Verifying...' : 'Verify & Login' }}</button>
          <button type="button" class="btn outline block" style="margin-top:8px;" :disabled="loading" @click="handleRequestOtp">Resend code</button>
        </form>

        <p v-if="role==='user'" style="text-align:center; margin-top:14px;">
          Don't have an account? <router-link to="/register">Register as User (Trekker)</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login, requestOtp, loginWithOtp } from '../../services/auth'

const router = useRouter()
const role = ref('admin')
const mode = ref('password')   // 'password' | 'otp' - admin is always forced to 'password'
const email = ref('')
const password = ref('')
const otp = ref('')
const otpSent = ref(false)
const error = ref('')
const info = ref('')
const loading = ref(false)

function selectRole(newRole) {
  role.value = newRole
  if (newRole === 'admin') mode.value = 'password'
  resetFormState()
}

function switchMode(newMode) {
  mode.value = newMode
  resetFormState()
}

function resetFormState() {
  error.value = ''
  info.value = ''
  password.value = ''
  otp.value = ''
  otpSent.value = false
}

function goToDashboard(user) {
  router.push(user.role === 'admin' ? '/admin/dashboard' : user.role === 'staff' ? '/staff/dashboard' : '/user/dashboard')
}

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    const user = await login(email.value, password.value, role.value)
    goToDashboard(user)
  } catch (e) {
    error.value = e.response?.data?.error || 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}

async function handleRequestOtp() {
  error.value = ''
  info.value = ''
  loading.value = true
  try {
    await requestOtp(email.value)
    otpSent.value = true
    info.value = `If that email is registered, a code was sent to ${email.value}. It expires in 5 minutes.`
  } catch (e) {
    error.value = e.response?.data?.error || 'Could not send OTP. Please try again.'
  } finally {
    loading.value = false
  }
}

async function handleVerifyOtp() {
  error.value = ''
  loading.value = true
  try {
    const user = await loginWithOtp(email.value, otp.value)
    goToDashboard(user)
  } catch (e) {
    error.value = e.response?.data?.error || 'Invalid or expired OTP. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
