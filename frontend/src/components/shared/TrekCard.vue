<template>
  <div class="trek-card">
    <div class="trek-img" :style="trek.image ? { backgroundImage: `url(${trek.image})` } : {}"></div>
    <div class="body">
      <h4>{{ trek.trek_name }}</h4>
      <div style="color:var(--muted); font-size:0.88rem; margin-bottom:8px;">{{ trek.location }}</div>
      <div style="display:flex; gap:6px; margin-bottom:8px;">
        <span class="badge" :class="difficultyClass">{{ trek.difficulty }}</span>
        <span class="badge gray">{{ trek.duration }} Days</span>
      </div>
      <div class="price">₹{{ trek.price?.toLocaleString() }} <span style="font-size:0.75rem; color:var(--muted); font-weight:400;">/ person</span></div>
      <div :style="{ color: trek.available_slots > 0 ? '#1a7431' : '#a4231d', fontSize: '0.88rem', margin: '6px 0' }">
        Slots Left: {{ trek.available_slots }}
      </div>
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ trek: { type: Object, required: true } })
const difficultyClass = computed(() => ({ Easy: 'green', Moderate: 'orange', Hard: 'red' }[props.trek.difficulty] || 'gray'))
</script>
