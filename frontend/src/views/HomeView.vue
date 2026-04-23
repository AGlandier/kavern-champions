<script setup>
import TwitchPlayer from '@/components/TwitchPlayer.vue'
import TwitchLoginCard from '@/components/TwitchLoginCard.vue'
import { useUserAuth } from '@/composables/useUserAuth.js'
import '@/styles/home.css'

const { isAuthenticated } = useUserAuth()
</script>

<template>
  <div class="home">
    <TwitchLoginCard v-if="!isAuthenticated()" />
    <TwitchPlayer channel="ksomon" />
  </div>
</template>
