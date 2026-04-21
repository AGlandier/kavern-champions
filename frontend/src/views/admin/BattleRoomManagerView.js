import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { battleroom, ApiError } from '../../api/index.js'
import { useAdminAuth } from '../../composables/useAdminAuth.js'

export function useBattleRoomManager() {
  const route = useRoute()
  const router = useRouter()
  const { adminKey, clearAdminKey } = useAdminAuth()

  const roomId = computed(() => Number(route.query.id))

  const room = ref(null)
  const battles = ref([])
  const displayRound = ref(1)
  const loading = ref(false)
  const error = ref(null)
  const nextRoundLoading = ref(false)

  const hasPrevRound = computed(() => displayRound.value > 1)
  const hasNextRound = computed(() => room.value && displayRound.value < room.value.round)
  const allBattlesFinished = computed(() =>
    !room.value || room.value.round === 0 || battles.value.every(b => b.finished)
  )

  function handleUnauthorized() {
    clearAdminKey()
    router.push({ name: 'admin-login' })
  }

  async function fetchRoom() {
    try {
      room.value = await battleroom.getById(roomId.value)
      displayRound.value = room.value.round
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) handleUnauthorized()
      else error.value = 'Room introuvable.'
    }
  }

  async function fetchBattles() {
    if (!room.value || displayRound.value === 0) return
    loading.value = true
    error.value = null
    try {
      const data = await battleroom.getBattles(roomId.value, { round: displayRound.value })
      battles.value = data.battles ?? data
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) handleUnauthorized()
      else error.value = 'Impossible de charger les battles.'
    } finally {
      loading.value = false
    }
  }

  async function goNextRound() {
    nextRoundLoading.value = true
    error.value = null
    try {
      const data = await battleroom.nextRound(roomId.value, adminKey.value)
      room.value.round = data.round
      displayRound.value = data.round
      await fetchBattles()
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) handleUnauthorized()
      else error.value = 'Erreur lors du passage au round suivant.'
    } finally {
      nextRoundLoading.value = false
    }
  }

  function onBattleEnded(battleId) {
    const b = battles.value.find(b => b.id === battleId)
    if (b) b.finished = true
  }

  function prevRound() { displayRound.value-- }
  function nextRound() { displayRound.value++ }

  watch(displayRound, fetchBattles)
  onMounted(async () => {
    await fetchRoom()
    await fetchBattles()
  })

  return {
    room, battles, displayRound, loading, error, nextRoundLoading,
    hasPrevRound, hasNextRound, allBattlesFinished,
    goNextRound, onBattleEnded, prevRound, nextRound,
  }
}
