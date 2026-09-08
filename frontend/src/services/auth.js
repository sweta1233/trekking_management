import { reactive } from 'vue'
import api from './api'

const VALID_ROLES = ['admin', 'staff', 'user']

function loadStoredUser() {
  const raw = localStorage.getItem('tma_user')
  if (!raw) return null
  try {
    const parsed = JSON.parse(raw)
    if (parsed && VALID_ROLES.includes(parsed.role)) return parsed
  } catch (e) {
    // fall through to cleanup below
  }
  // Malformed or outdated cached user data (e.g. from an older app version) - wipe it
  // rather than let it silently break routing/navigation.
  localStorage.removeItem('tma_user')
  localStorage.removeItem('tma_token')
  return null
}

export const authState = reactive({
  token: localStorage.getItem('tma_token') || null,
  user: loadStoredUser(),
})

// If we have a token but no valid user (or vice versa), treat as logged out to avoid a broken half-state.
if (!authState.user || !authState.token) {
  authState.token = null
  authState.user = null
  localStorage.removeItem('tma_token')
  localStorage.removeItem('tma_user')
}

export function isLoggedIn() {
  return !!authState.token && !!authState.user
}

export function currentRole() {
  return authState.user ? authState.user.role : null
}

export async function login(email, password, role) {
  const res = await api.post('/auth/login', { email, password, role })
  authState.token = res.data.access_token
  authState.user = res.data.user
  localStorage.setItem('tma_token', authState.token)
  localStorage.setItem('tma_user', JSON.stringify(authState.user))
  return res.data.user
}

export async function register(payload) {
  const res = await api.post('/auth/register', payload)
  return res.data
}

export async function requestOtp(email) {
  const res = await api.post('/auth/otp/request', { email })
  return res.data
}

export async function loginWithOtp(email, otp) {
  const res = await api.post('/auth/otp/verify', { email, otp })
  authState.token = res.data.access_token
  authState.user = res.data.user
  localStorage.setItem('tma_token', authState.token)
  localStorage.setItem('tma_user', JSON.stringify(authState.user))
  return res.data.user
}

export function logout() {
  authState.token = null
  authState.user = null
  localStorage.removeItem('tma_token')
  localStorage.removeItem('tma_user')
}
