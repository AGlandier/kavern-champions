<script setup>
import NavBar from '../components/NavBar.vue'
import AppFooter from '../components/AppFooter.vue'
import '../styles/layout.css'
</script>

<template>
  <div class="default-layout">
    <NavBar />
    <main class="default-layout__content">
      <RouterView />
    </main>
    <AppFooter />
  </div>
</template>
