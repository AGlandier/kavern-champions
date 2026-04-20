<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { auth, user, ApiError } from '../api/index.js'
import { useUserAuth } from '../composables/useUserAuth.js'
import LoginForm from '../components/LoginForm.vue'
import SetPasswordForm from '../components/SetPasswordForm.vue'
import '../styles/login.css'
import '../styles/admin.css'

const router = useRouter()
const { login } = useUserAuth()

const step = ref('username')
const username = ref('')
const isNewUser = ref(false)
const error = ref(null)
const loading = ref(false)

async function checkUser() {
  error.value = null
  const name = username.value.trim()
  if (!name) return
  loading.value = true
  try {
    const data = await user.isSecured(name)
    step.value = data.secured ? 'login' : 'set-password'
    isNewUser.value = false
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) {
      step.value = 'set-password'
      isNewUser.value = true
    } else {
      error.value = 'Erreur lors de la vérification du pseudo.'
    }
  } finally {
    loading.value = false
  }
}

async function handleLogin(password) {
  error.value = null
  loading.value = true
  try {
    await login(username.value.trim(), password)
    loading.value = false
    router.push({ name: 'home' })
  } catch {
    loading.value = false
    error.value = 'Mot de passe incorrect.'
  }
}

async function handleSetPassword(password) {
  error.value = null
  loading.value = true
  try {
    if (isNewUser.value) {
      await auth.register(username.value.trim(), password)
    } else {
      await auth.setPassword(username.value.trim(), password)
    }
    await login(username.value.trim(), password)
    loading.value = false
    router.push({ name: 'home' })
  } catch {
    loading.value = false
    error.value = 'Erreur lors de la création du mot de passe.'
  }
}

function back() {
  step.value = 'username'
  error.value = null
}
</script>

<template>
  <div class="login">
    <p class="login__title">Connexion</p>

    <template v-if="step === 'username'">
      <form class="login__form" @submit.prevent="checkUser">
        <input
          v-model="username"
          type="text"
          class="kc-input"
          placeholder="Pseudo Twitch"
          autocomplete="username"
          autofocus
        />
        <button type="submit" class="kc-btn" :disabled="loading || !username.trim()">
          Continuer
        </button>
      </form>
    </template>

    <template v-else>
      <p class="login__username">{{ username }}</p>
      <LoginForm v-if="step === 'login'" :loading="loading" @submit="handleLogin" />
      <SetPasswordForm v-else :loading="loading" @submit="handleSetPassword" />
      <button class="login__back" type="button" @click="back">← Changer de pseudo</button>
    </template>

    <p v-if="error" class="login__error">{{ error }}</p>
  </div>
</template>
