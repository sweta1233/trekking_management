<template>
  <div style="position:fixed; bottom:20px; right:20px; z-index:1000; display:flex; flex-direction:column; gap:8px;">
    <div v-for="t in toasts" :key="t.id" class="alert" :class="t.type === 'error' ? 'error' : 'success'" style="min-width:240px; box-shadow:0 2px 8px rgba(0,0,0,0.12); margin:0;">
      {{ t.message }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const toasts = ref([])
let counter = 0
function push(message, type = 'success') {
  const id = ++counter
  toasts.value.push({ id, message, type })
  setTimeout(() => { toasts.value = toasts.value.filter(t => t.id !== id) }, 3000)
}
defineExpose({ push })
</script>
