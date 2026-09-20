import { createRouter, createWebHistory } from 'vue-router'
import { isLoggedIn, currentRole } from '../services/auth'

import LoginPage from '../components/auth/LoginPage.vue'
import RegisterPage from '../components/auth/RegisterPage.vue'

import AdminDashboard from '../components/admin/AdminDashboard.vue'
import AdminManageTreks from '../components/admin/AdminManageTreks.vue'
import AdminCreateStaff from '../components/admin/AdminCreateStaff.vue'
import AdminManageStaff from '../components/admin/AdminManageStaff.vue'
import AdminManageUsers from '../components/admin/AdminManageUsers.vue'
import AdminBookings from '../components/admin/AdminBookings.vue'
import AdminSearch from '../components/admin/AdminSearch.vue'
import AdminReports from '../components/admin/AdminReports.vue'
import AdminSettings from '../components/admin/AdminSettings.vue'

import StaffDashboard from '../components/staff/StaffDashboard.vue'
import StaffMyTreks from '../components/staff/StaffMyTreks.vue'
import StaffManageTrek from '../components/staff/StaffManageTrek.vue'
import StaffParticipants from '../components/staff/StaffParticipants.vue'
import StaffProfile from '../components/staff/StaffProfile.vue'

import UserDashboard from '../components/user/UserDashboard.vue'
import UserBrowseTreks from '../components/user/UserBrowseTreks.vue'
import UserMyBookings from '../components/user/UserMyBookings.vue'
import UserTrekkingHistory from '../components/user/UserTrekkingHistory.vue'
import UserProfile from '../components/user/UserProfile.vue'
import AIAssistant from '../components/user/AIAssistant.vue'
import TrekTracker from '../components/user/TrekTracker.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'login', component: LoginPage },
  { path: '/register', name: 'register', component: RegisterPage },

  { path: '/admin/dashboard', name: 'admin-dashboard', component: AdminDashboard, meta: { role: 'admin' } },
  { path: '/admin/treks', name: 'admin-treks', component: AdminManageTreks, meta: { role: 'admin' } },
  { path: '/admin/staff/create', name: 'admin-staff-create', component: AdminCreateStaff, meta: { role: 'admin' } },
  { path: '/admin/staff', name: 'admin-staff', component: AdminManageStaff, meta: { role: 'admin' } },
  { path: '/admin/users', name: 'admin-users', component: AdminManageUsers, meta: { role: 'admin' } },
  { path: '/admin/bookings', name: 'admin-bookings', component: AdminBookings, meta: { role: 'admin' } },
  { path: '/admin/search', name: 'admin-search', component: AdminSearch, meta: { role: 'admin' } },
  { path: '/admin/reports', name: 'admin-reports', component: AdminReports, meta: { role: 'admin' } },
  { path: '/admin/settings', name: 'admin-settings', component: AdminSettings, meta: { role: 'admin' } },

  { path: '/staff/dashboard', name: 'staff-dashboard', component: StaffDashboard, meta: { role: 'staff' } },
  { path: '/staff/my-treks', name: 'staff-my-treks', component: StaffMyTreks, meta: { role: 'staff' } },
  { path: '/staff/treks/:id', name: 'staff-manage-trek', component: StaffManageTrek, meta: { role: 'staff' } },
  { path: '/staff/participants', name: 'staff-participants', component: StaffParticipants, meta: { role: 'staff' } },
  { path: '/staff/profile', name: 'staff-profile', component: StaffProfile, meta: { role: 'staff' } },

  { path: '/user/dashboard', name: 'user-dashboard', component: UserDashboard, meta: { role: 'user' } },
  { path: '/user/treks', name: 'user-browse-treks', component: UserBrowseTreks, meta: { role: 'user' } },
  { path: '/user/my-bookings', name: 'user-my-bookings', component: UserMyBookings, meta: { role: 'user' } },
  { path: '/user/history', name: 'user-history', component: UserTrekkingHistory, meta: { role: 'user' } },
  { path: '/user/profile', name: 'user-profile', component: UserProfile, meta: { role: 'user' } },
  { path: '/user/ai-assistant', name: 'user-ai-assistant', component: AIAssistant, meta: { role: 'user' } },
  { path: '/user/trek-tracker/:id', name: 'user-trek-tracker', component: TrekTracker, meta: { role: 'user' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const publicPages = ['login', 'register']
  if (!publicPages.includes(to.name) && !isLoggedIn()) {
    return next({ name: 'login' })
  }
  if (to.meta.role && currentRole() !== to.meta.role) {
    if (isLoggedIn()) {
      const role = currentRole()
      if (role === 'admin') return next({ name: 'admin-dashboard' })
      if (role === 'staff') return next({ name: 'staff-dashboard' })
      if (role === 'user') return next({ name: 'user-dashboard' })
    }
    return next({ name: 'login' })
  }
  next()
})

export default router
