<script setup>
import { ref } from 'vue'

defineProps({ loading: Boolean })
const emit = defineEmits(['submit'])

const password = ref('')
</script>

<template>
  <form class="login__form" @submit.prevent="emit('submit', password)">
    <input
      v-model="password"
      type="password"
      class="kc-input"
      placeholder="Mot de passe"
      autocomplete="current-password"
      autofocus
    />
    <button type="submit" class="kc-btn" :disabled="loading || !password">
      Se connecter
    </button>
  </form>
</template>
