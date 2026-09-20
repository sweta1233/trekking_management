<template>
  <div class="auth-wrap">
    <div class="auth-shell">
      <div class="auth-hero">
        <div>
          <div class="hero-brand">Trekking Mgmt<small>Application</small></div>
        </div>
        <div class="hero-tagline">Plan. Track. Explore.</div>
        <div class="hero-sub">AI-powered trekking & itinerary management</div>
        <div class="hero-stats">
          <div><strong>3</strong><span>Roles</span></div>
          <div><strong>1000+</strong><span>Treks</span></div>
        </div>
      </div>
      <div class="auth-panel">
        <h2>Login</h2>
        <p class="subtitle">Select your role and verify</p>

        <div class="role-pick">
          <button v-for="r in roles" :key="r.value" @click="selectedRole = r.value" :class="['role-btn', { active: selectedRole === r.value }]">
            {{ r.label }}
          </button>
        </div>

        <form @submit.prevent="handleLogin" style="display:flex; flex-direction:column; gap:12px;">
          <input v-model="email" type="email" placeholder="Email" required style="padding:12px; border-radius:8px; border:1px solid #ccc;" />
          <input v-model="phone" type="tel" placeholder="Phone Number" required style="padding:12px; border-radius:8px; border:1px solid #ccc;" />
          <input v-model="otp" type="text" placeholder="OTP Code" required style="padding:12px; border-radius:8px; border:1px solid #ccc;" />
          <button type="submit" style="padding:12px; border-radius:8px; background:#1f6f54; color:white; border:none; font-weight:600; font-size:16px;">Verify & Login</button>
        </form>
        <p style="margin-top:12px; font-size:13px; color:#777;">Email + Phone OTP verification for Admin / Staff / User roles</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const email = ref('')
const phone = ref('')
const otp = ref('')
const selectedRole = ref('user')
const roles = [
  { label: 'Admin', value: 'admin' },
  { label: 'Staff', value: 'staff' },
  { label: 'User', value: 'user' }
]
function handleLogin() {
  import('../../services/auth').then(({ login }) => {
    login(email.value, phone.value, otp.value, selectedRole.value).then(u => {
      window.location.href = '/' + selectedRole.value + '/dashboard'
    }).catch(e => alert('OTP verification failed'))
  })
}
</script>

<style scoped>
.auth-wrap {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background:
    linear-gradient(160deg, rgba(15,40,32,0.55), rgba(15,40,32,0.72)),
    url('/trek-bg.jpg') center/cover no-repeat fixed;
}
.auth-shell {
  display: flex;
  width: 920px;
  max-width: 100%;
  min-height: 560px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 24px 60px rgba(0,0,0,0.35);
}
.auth-hero {
  flex: 1.1;
  position: relative;
  background: url('/trek-bg.jpg') center/cover no-repeat;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 36px 32px;
  color: #fff;
}
.auth-hero::before {
  content: "";
  position: absolute; inset: 0;
  background: linear-gradient(200deg, rgba(31,111,84,0.35) 0%, rgba(10,25,20,0.75) 100%);
}
.auth-hero > * { position: relative; z-index: 1; }
.auth-hero .hero-brand { font-size: 1.3rem; font-weight: 700; letter-spacing: 0.3px; }
.auth-hero .hero-brand small { display: block; font-weight: 400; opacity: 0.8; font-size: 0.8rem; margin-top: 2px; }
.auth-hero .hero-tagline { font-size: 1.5rem; font-weight: 700; line-height: 1.35; max-width: 320px; }
.auth-hero .hero-sub { font-size: 0.88rem; opacity: 0.85; margin-top: 10px; max-width: 300px; }
.auth-hero .hero-stats { display: flex; gap: 22px; }
.auth-hero .hero-stats div strong { display: block; font-size: 1.2rem; }
.auth-hero .hero-stats div span { font-size: 0.75rem; opacity: 0.8; }
.auth-panel {
  flex: 1;
  background: #fff;
  padding: 40px 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow-y: auto;
}
.auth-panel h2 { margin: 0 0 4px; font-size: 1.6rem; }
.auth-panel .subtitle { color: #767676; margin-bottom: 18px; font-size: 0.92rem; }
.role-pick { display: flex; gap: 8px; margin-bottom: 18px; }
.role-btn {
  flex: 1; padding: 10px 4px; border-radius: 10px; border: 1px solid #e2e5e4;
  background: #fbfcfb; cursor: pointer; font-size: 0.82rem; transition: all .15s ease;
}
.role-btn.active { background: #1f6f54; color: #fff; border-color: #1f6f54; box-shadow: 0 4px 10px rgba(31,111,84,0.28); }
.role-btn:hover:not(.active) { border-color: #1f6f54; color: #1f6f54; }
@media (max-width: 760px) {
  .auth-shell { flex-direction: column; min-height: 0; }
  .auth-hero { min-height: 180px; padding: 24px; }
  .auth-hero .hero-tagline { font-size: 1.1rem; }
  .auth-hero .hero-stats { display: none; }
  .auth-panel { padding: 28px 24px; }
}
</style>
