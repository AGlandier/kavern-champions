<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { user } from '../api/index.js'
import { useUserAuth } from '../composables/useUserAuth.js'
import UpdateTeamlistForm from '../components/UpdateTeamlistForm.vue'
import '../styles/admin.css'
import '../styles/manager.css'

const route = useRoute()
const router = useRouter()
const { currentUser } = useUserAuth()

const username = route.query.user
const teamlist = ref('')
const loading = ref(false)
const loadError = ref(null)
const saveSuccess = ref(false)
const saveError = ref(null)

onMounted(async () => {
  if (!currentUser.value || currentUser.value !== username) {
    router.push({ name: 'login' })
    return
  }
  loading.value = true
  try {
    const stats = await user.getStats(username)
    teamlist.value = stats.teamlist ?? ''
  } catch {
    loadError.value = 'Impossible de charger les données.'
  } finally {
    loading.value = false
  }
})

async function handleSave(newTeamlist) {
  saveSuccess.value = false
  saveError.value = null
  loading.value = true
  try {
    await user.updateTeamlist(newTeamlist)
    teamlist.value = newTeamlist
    saveSuccess.value = true
  } catch {
    saveError.value = 'Erreur lors de la sauvegarde.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="manager">
    <h1 class="manager__title">Mon espace — {{ username }}</h1>

    <p v-if="loadError" class="manager__error">{{ loadError }}</p>

    <template v-else>
      <section class="manager__section">
        <h2 class="manager__section-title">Teamlist</h2>
        <UpdateTeamlistForm :model-value="teamlist" :loading="loading" @submit="handleSave" />
        <p v-if="saveSuccess" class="manager__success">Teamlist mise à jour.</p>
        <p v-if="saveError" class="manager__error">{{ saveError }}</p>
      </section>
    </template>
  </div>
</template>
