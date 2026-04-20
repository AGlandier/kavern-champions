<script setup>
import { ref } from 'vue'

defineProps({ loading: Boolean })
const emit = defineEmits(['submit'])

const password = ref('')
const confirm = ref('')
const localError = ref(null)

function submit() {
  localError.value = null
  if (password.value.length < 6) {
    localError.value = 'Le mot de passe doit contenir au moins 6 caractères.'
    return
  }
  if (password.value !== confirm.value) {
    localError.value = 'Les mots de passe ne correspondent pas.'
    return
  }
  emit('submit', password.value)
}
</script>

<template>
  <form class="login__form login__form--column" @submit.prevent="submit">
    <p class="login__info">Créez un mot de passe pour sécuriser votre compte.</p>
    <input
      v-model="password"
      type="password"
      class="kc-input"
      placeholder="Mot de passe"
      autocomplete="new-password"
      autofocus
    />
    <input
      v-model="confirm"
      type="password"
      class="kc-input"
      placeholder="Confirmer le mot de passe"
      autocomplete="new-password"
    />
    <p v-if="localError" class="login__error">{{ localError }}</p>
    <button type="submit" class="kc-btn" :disabled="loading || !password || !confirm">
      Créer mon mot de passe
    </button>
  </form>
</template>
