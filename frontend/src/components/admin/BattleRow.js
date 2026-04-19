import { battle, ApiError } from '../../api/index.js'
import { useAdminAuth } from '../../composables/useAdminAuth.js'
import { useRouter } from 'vue-router'

export function useBattleRow(props, emit) {
  const { adminKey, clearAdminKey } = useAdminAuth()
  const router = useRouter()

  async function forceEnd() {
    try {
      await battle.end(props.battle.id, { forced: true }, adminKey.value)
      emit('ended', props.battle.id)
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        clearAdminKey()
        router.push({ name: 'admin-login' })
      }
    }
  }

  return { forceEnd }
}
