import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { battleroom, ApiError } from '../../api/index.js'
import { useAdminAuth } from '../../composables/useAdminAuth.js'

export function useCreateRoomForm() {
  const router = useRouter()
  const { adminKey, clearAdminKey } = useAdminAuth()

  const roomName = ref('')
  const requiresTeamlist = ref(false)
  const creating = ref(false)
  const error = ref(null)

  async function createRoom() {
    const name = roomName.value.trim()
    if (!name) return
    creating.value = true
    error.value = null
    try {
      const created = await battleroom.create(name, requiresTeamlist.value, adminKey.value)
      roomName.value = ''
      router.push({ name: 'admin-room', params: { id: created.id } })
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        clearAdminKey()
        router.push({ name: 'admin-login' })
      } else {
        console.error('[createRoom]', e)
        error.value = 'Erreur lors de la création.'
      }
    } finally {
      creating.value = false
    }
  }

  return { roomName, requiresTeamlist, creating, error, createRoom }
}
