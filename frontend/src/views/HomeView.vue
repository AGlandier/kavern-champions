<script setup>
import TwitchPlayer from '@/components/TwitchPlayer.vue'
import TwitchLoginCard from '@/components/TwitchLoginCard.vue'
import { useUserAuth } from '@/composables/useUserAuth.js'
import '@/styles/home.css'

const { isAuthenticated, currentUser } = useUserAuth()

const twitchParent = import.meta.env.VITE_TWITCH_PARENT || 'localhost'
</script>

<template>
  <div class="home">
    <TwitchLoginCard v-if="!isAuthenticated()" />
    <p v-else class="home__dashboard-hint">
      Pour participer, accédez à votre
      <RouterLink
        class="home__dashboard-link"
        :to="{ name: 'manager', query: { user: currentUser } }"
      >Dashboard</RouterLink>.
    </p>
    <TwitchPlayer channel="ksomon" :parent="twitchParent" />
  </div>
</template>
