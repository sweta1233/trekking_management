<template>
  <AppLayout title="Reports & Statistics">
    <div class="grid-3" style="margin-bottom:20px;">
      <div class="card stat"><div class="label">Total Users</div><div class="value">{{ report.total_users ?? '-' }}</div></div>
      <div class="card stat"><div class="label">Total Staff</div><div class="value">{{ report.total_staff ?? '-' }}</div></div>
      <div class="card stat"><div class="label">Active Treks</div><div class="value">{{ report.active_treks ?? '-' }}</div></div>
      <div class="card stat"><div class="label">Completed Treks</div><div class="value">{{ report.completed_treks ?? '-' }}</div></div>
      <div class="card stat"><div class="label">Total Revenue</div><div class="value">₹{{ (report.total_revenue ?? 0).toLocaleString() }}</div></div>
    </div>

    <div class="grid-3">
      <div class="card">
        <h4 style="margin-top:0;">Popular Destinations</h4>
        <div v-for="d in report.popular_destinations" :key="d.location" style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid var(--border);">
          {{ d.location }} <strong>{{ d.count }}</strong>
        </div>
        <p v-if="!report.popular_destinations?.length" style="color:var(--muted);">No data yet.</p>
      </div>
      <div class="card">
        <h4 style="margin-top:0;">Monthly Participation</h4>
        <div v-for="m in report.monthly_participation" :key="m.month" style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid var(--border);">
          {{ monthNames[m.month - 1] }} <strong>{{ m.count }}</strong>
        </div>
        <p v-if="!report.monthly_participation?.length" style="color:var(--muted);">No data yet.</p>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '../shared/AppLayout.vue'
import api from '../../services/api'

const report = ref({})
const monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
onMounted(async () => { report.value = (await api.get('/reports')).data })
</script>
