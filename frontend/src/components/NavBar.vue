<script setup>
import { RouterLink } from 'vue-router'
import { useTheme } from '../composables/useTheme.js'
import { useUserAuth } from '../composables/useUserAuth.js'
import '../styles/navbar.css'

const { theme, toggleTheme } = useTheme()
const { currentUser, logout } = useUserAuth()
</script>

<template>
  <nav class="navbar">
    <RouterLink to="/" class="navbar__home">Accueil</RouterLink>

    <span class="navbar__title">Les Champions de la Kaverne</span>

    <div class="navbar__right">
      <button v-if="currentUser" class="navbar__logout" aria-label="Se déconnecter" @click="logout">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="navbar__logout-icon" aria-hidden="true">
          <path fill-rule="evenodd" d="M12 2.25a.75.75 0 0 1 .75.75v9a.75.75 0 0 1-1.5 0V3a.75.75 0 0 1 .75-.75ZM6.166 5.106a.75.75 0 0 1 0 1.06 8.25 8.25 0 1 0 11.668 0 .75.75 0 1 1 1.06-1.06c3.808 3.807 3.808 9.98 0 13.788-3.807 3.808-9.98 3.808-13.788 0-3.808-3.807-3.808-9.98 0-13.788a.75.75 0 0 1 1.06 0Z" clip-rule="evenodd"/>
        </svg>
      </button>
      <RouterLink v-if="currentUser" :to="{ path: '/manager', query: { user: currentUser } }" class="navbar__user">
        {{ currentUser }}
      </RouterLink>
    
      <RouterLink v-else :to="{ name: 'login' }" class="navbar__login-btn">
        Se connecter
      </RouterLink>

      <button
        class="navbar__theme-toggle"
        :aria-label="theme === 'dark' ? 'Passer au thème clair' : 'Passer au thème sombre'"
        @click="toggleTheme"
      >
        <!-- Soleil (thème sombre actif → proposer le clair) -->
        <svg v-if="theme === 'dark'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="navbar__theme-icon" aria-hidden="true">
          <path d="M12 2.25a.75.75 0 0 1 .75.75v2.25a.75.75 0 0 1-1.5 0V3a.75.75 0 0 1 .75-.75ZM7.5 12a4.5 4.5 0 1 1 9 0 4.5 4.5 0 0 1-9 0ZM18.894 6.166a.75.75 0 0 0-1.06-1.06l-1.591 1.59a.75.75 0 1 0 1.06 1.061l1.591-1.59ZM21.75 12a.75.75 0 0 1-.75.75h-2.25a.75.75 0 0 1 0-1.5H21a.75.75 0 0 1 .75.75ZM17.834 18.894a.75.75 0 0 0 1.06-1.06l-1.59-1.591a.75.75 0 1 0-1.061 1.06l1.59 1.591ZM12 18a.75.75 0 0 1 .75.75V21a.75.75 0 0 1-1.5 0v-2.25A.75.75 0 0 1 12 18ZM7.758 17.303a.75.75 0 0 0-1.061-1.06l-1.591 1.59a.75.75 0 0 0 1.06 1.061l1.591-1.59ZM6 12a.75.75 0 0 1-.75.75H3a.75.75 0 0 1 0-1.5h2.25A.75.75 0 0 1 6 12ZM6.697 7.757a.75.75 0 0 0 1.06-1.06l-1.59-1.591a.75.75 0 0 0-1.061 1.06l1.59 1.591Z"/>
        </svg>
        <!-- Lune (thème clair actif → proposer le sombre) -->
        <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="navbar__theme-icon" aria-hidden="true">
          <path fill-rule="evenodd" d="M9.528 1.718a.75.75 0 0 1 .162.819A8.97 8.97 0 0 0 9 6a9 9 0 0 0 9 9 8.97 8.97 0 0 0 3.463-.69.75.75 0 0 1 .981.98 10.503 10.503 0 0 1-9.694 6.46c-5.799 0-10.5-4.7-10.5-10.5 0-4.368 2.667-8.112 6.46-9.694a.75.75 0 0 1 .818.162Z" clip-rule="evenodd"/>
        </svg>
      </button>

      <a
        href="https://twitch.tv/ksomon"
        target="_blank"
        rel="noopener noreferrer"
        class="navbar__twitch"
        aria-label="Chaîne Twitch ksomon"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="navbar__twitch-icon" aria-hidden="true">
          <path d="M11.571 4.714h1.715v5.143H11.57zm4.715 0H18v5.143h-1.714zM6 0L1.714 4.286v15.428h5.143V24l4.286-4.286h3.428L22.286 12V0zm14.571 11.143l-3.428 3.428h-3.429l-3 3v-3H6.857V1.714h13.714z"/>
        </svg>
      </a>
    </div>
  </nav>
</template>
