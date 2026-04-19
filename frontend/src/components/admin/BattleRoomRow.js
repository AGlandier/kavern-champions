import { useRouter } from 'vue-router'
import { timeAgo } from '../../utils/timeAgo.js'

export function useBattleRoomRow(props) {
  const router = useRouter()

  function goToManager() {
    router.push({ name: 'admin-room', query: { id: props.room.id } })
  }

  return { timeAgo, goToManager }
}
