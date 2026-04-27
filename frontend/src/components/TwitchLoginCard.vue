<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('')

function submit() {
  const name = username.value.trim().toLowerCase()
  if (!name) return
  router.push({ name: 'login', query: { username: name } })
}
</script>

<template>
  <div class="twitch-login-card">
    <p class="twitch-login-card__title">Entrez votre pseudo Twitch</p>
    <form class="twitch-login-card__form" @submit.prevent="submit">
      <input
        v-model="username"
        type="text"
        class="kc-input"
        placeholder="Pseudo Twitch"
        autocomplete="username"
      />
      <button type="submit" class="kc-btn" :disabled="!username.trim()">
        Continuer
      </button>
    </form>
  </div>
</template>
