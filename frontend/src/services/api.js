import axios from 'axios'

// Determine base API URL:
// In local development: defaults to '/api' (proxied via Vite)
// In production (Vercel): configured via VITE_API_BASE_URL (e.g., https://tma-backend.onrender.com/api)
let baseURL = import.meta.env.VITE_API_BASE_URL || '/api'

// Normalize baseURL: trim trailing slashes
baseURL = baseURL.replace(/\/+$/, '')

// If a full URL is provided without '/api' suffix, append '/api'
if (baseURL.startsWith('http://') || baseURL.startsWith('https://')) {
  if (!baseURL.endsWith('/api')) {
    baseURL = `${baseURL}/api`
  }
} else if (!baseURL.startsWith('/')) {
  baseURL = `/${baseURL}`
}

const api = axios.create({
  baseURL,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('tma_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('tma_token')
      localStorage.removeItem('tma_user')
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
