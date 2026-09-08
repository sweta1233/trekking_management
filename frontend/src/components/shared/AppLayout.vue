<template>
  <div class="layout">
    <NavBar />
    <div style="flex:1; display:flex; flex-direction:column;">
      <div class="topbar">
        <h2>{{ title }}</h2>
        <div>Trekking Management Application</div>
      </div>
      <div class="content">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import NavBar from './NavBar.vue'
defineProps({ title: { type: String, default: '' } })
</script>
