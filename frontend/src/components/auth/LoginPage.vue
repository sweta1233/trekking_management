<template>
  <div class="auth-wrap">
    <!-- Project Info Banner at Top -->
    <div class="project-banner">
      <div class="banner-container">
        <div class="banner-left">
          <h1 class="banner-title">🏔️ TrekMate AI</h1>
          <p class="banner-desc">AI-Powered Trekking Platform | RAG + LangGraph + Vector Search + ML</p>
        </div>
        <div class="banner-right">
          <a href="https://github.com/sweta1233/Trekking-management-app" target="_blank" rel="noopener" class="banner-link github-link">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
            GitHub
          </a>
          <a href="https://trekking-management-sand.vercel.app" target="_blank" rel="noopener" class="banner-link demo-link">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
            </svg>
            Live Demo
          </a>
        </div>
      </div>
    </div>

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
