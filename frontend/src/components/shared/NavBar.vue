<template>
  <div class="sidebar">
    <div class="brand">Trekking Mgmt<small>Application</small></div>

    <div class="who">
      <div class="name">{{ userName }}</div>
      <div class="role">{{ role }}</div>
    </div>

    <nav v-if="role === 'admin'">
      <router-link to="/admin/dashboard"><span>Dashboard</span></router-link>
      <router-link to="/admin/treks"><span>Treks</span></router-link>
      <router-link to="/admin/staff"><span>Trekking Staff</span></router-link>
      <router-link to="/admin/users"><span>Users (Trekkers)</span></router-link>
      <router-link to="/admin/bookings"><span>Bookings</span></router-link>
      <router-link to="/admin/search"><span>Search</span></router-link>
      <router-link to="/admin/reports"><span>Reports</span></router-link>
      <router-link to="/admin/settings"><span>Settings</span></router-link>
      <a href="#" @click.prevent="handleLogout"><span>Logout</span></a>
    </nav>

    <nav v-else-if="role === 'staff'">
      <router-link to="/staff/dashboard"><span>Dashboard</span></router-link>
      <router-link to="/staff/my-treks"><span>My Treks</span></router-link>
      <router-link to="/staff/participants"><span>Participants</span></router-link>
      <router-link to="/staff/profile"><span>Profile</span></router-link>
      <a href="#" @click.prevent="handleLogout"><span>Logout</span></a>
    </nav>

    <nav v-else-if="role === 'user'">
      <router-link to="/user/dashboard"><span>Dashboard</span></router-link>
      <router-link to="/user/treks"><span>Browse Treks</span></router-link>
      <router-link to="/user/my-bookings"><span>My Bookings</span></router-link>
      <router-link to="/user/history"><span>History</span></router-link>
      <router-link to="/user/profile"><span>Profile</span></router-link>
      <a href="#" @click.prevent="handleLogout"><span>Logout</span></a>
    </nav>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { authState, logout } from '../../services/auth'

const router = useRouter()
const role = computed(() => authState.user?.role)
const userName = computed(() => authState.user?.name || 'Guest')

function handleLogout() {
  logout()
  router.push('/login')
}
</script>
