<script setup>
import TwitchPlayer from '@/components/TwitchPlayer.vue'
import TwitchLoginCard from '@/components/TwitchLoginCard.vue'
import { useUserAuth } from '@/composables/useUserAuth.js'
import '@/styles/home.css'

const { isAuthenticated } = useUserAuth()

const twitchParent = import.meta.env.VITE_TWITCH_PARENT || 'localhost'
</script>

<template>
  <div class="home">
    <TwitchLoginCard v-if="!isAuthenticated()" />
    <TwitchPlayer channel="ksomon" :parent="twitchParent" />
  </div>
</template>
