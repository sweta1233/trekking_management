<template>
  <div style="min-height:100vh; display:flex; align-items:center; justify-content:center; background: linear-gradient(135deg, #667eea 0%, #feca57 100%); padding:20px;">
    <div style="background:white; padding:40px; border-radius:16px; max-width:420px; width:100%; text-align:center; box-shadow:0 20px 60px rgba(0,0,0,0.25);">
      <h2 style="margin-bottom:8px; font-size:22px;">Login</h2>
      <form @submit.prevent="handleLogin" style="display:flex; flex-direction:column; gap:12px;">
        <input v-model="email" type="email" placeholder="Email" required style="padding:12px; border-radius:8px; border:1px solid #ccc;" />
        <input v-model="password" type="password" placeholder="Password" required style="padding:12px; border-radius:8px; border:1px solid #ccc;" />
        <button type="submit" style="padding:12px; border-radius:8px; background:#667eea; color:white; border:none; font-weight:600; font-size:16px;">Login</button>
      </form>
      <p style="margin-top:12px; font-size:13px; color:#777;">Clean centered design — no sidebars. <router-link to="/register" style="color:#667eea;">Register new user →</router-link></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const email = ref('')
const password = ref('')
function handleLogin() {
  // Call real auth service
  import('../../services/auth').then(({ login }) => {
    login(email.value, password.value, 'user').then(u => {
      window.location.href = '/user/dashboard'
    }).catch(e => alert('Login failed'))
  })
}
</script>
