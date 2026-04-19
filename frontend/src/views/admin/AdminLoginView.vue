<script setup>
import { useAdminLogin } from './AdminLoginView.js'
import '../../styles/admin.css'

const { keyInput, submit } = useAdminLogin()
</script>

<template>
  <div class="admin-login">
    <p class="admin-login__title">Accès administration</p>
    <form class="admin-login__form" @submit.prevent="submit">
      <input
        v-model="keyInput"
        type="password"
        class="kc-input"
        placeholder="Clé admin"
        autocomplete="current-password"
      />
      <button type="submit" class="kc-btn">Connexion</button>
    </form>
  </div>
</template>
