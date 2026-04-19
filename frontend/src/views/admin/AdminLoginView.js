import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminAuth } from '../../composables/useAdminAuth.js'

export function useAdminLogin() {
  const router = useRouter()
  const { setAdminKey } = useAdminAuth()

  const keyInput = ref('')

  function submit() {
    const key = keyInput.value.trim()
    if (!key) return
    setAdminKey(key)
    router.push({ name: 'admin' })
  }

  return { keyInput, submit }
}
