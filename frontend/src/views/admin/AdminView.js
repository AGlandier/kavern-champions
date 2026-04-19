import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { battleroom, ApiError } from '../../api/index.js'
import { useAdminAuth } from '../../composables/useAdminAuth.js'

const PAGE_SIZE = 5

export function useAdminView() {
  const router = useRouter()
  const { clearAdminKey } = useAdminAuth()

  const rooms = ref([])
  const playerCounts = ref({})
  const total = ref(0)
  const offset = ref(0)
  const loading = ref(false)
  const error = ref(null)

  const hasPrev = computed(() => offset.value > 0)
  const hasNext = computed(() => offset.value + PAGE_SIZE < total.value)

  function handleUnauthorized() {
    clearAdminKey()
    router.push({ name: 'admin-login' })
  }

  async function fetchRooms() {
    loading.value = true
    error.value = null
    try {
      const data = await battleroom.getAll({ limit: PAGE_SIZE, offset: offset.value, orderBy: 'date' })
      rooms.value = data.battlerooms ?? data
      total.value = data.total ?? rooms.value.length
      fetchPlayerCounts()
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) handleUnauthorized()
      else error.value = 'Impossible de charger les rooms.'
    } finally {
      loading.value = false
    }
  }

  async function fetchPlayerCounts() {
    const results = await Promise.allSettled(
      rooms.value.map(r => battleroom.getPlayers(r.id))
    )
    results.forEach((result, i) => {
      if (result.status === 'fulfilled') {
        const room = rooms.value[i]
        playerCounts.value[room.id] = (result.value.players ?? result.value).length
      }
    })
  }

  function prevPage() { offset.value = Math.max(0, offset.value - PAGE_SIZE) }
  function nextPage() { offset.value += PAGE_SIZE }

  watch(offset, fetchRooms)
  onMounted(fetchRooms)

  return {
    rooms, playerCounts, loading, error,
    hasPrev, hasNext,
    prevPage, nextPage,
  }
}
