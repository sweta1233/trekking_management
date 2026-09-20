<template>
  <div style="min-height:100vh; display:flex; flex-direction:column;">
    <div style="padding:20px; text-align:center;">
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
defineProps({ title: { type: String, default: '' } })
</script>
