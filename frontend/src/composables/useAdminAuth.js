import { ref } from 'vue'

const STORAGE_KEY = 'kc-admin-key'

const adminKey = ref(localStorage.getItem(STORAGE_KEY) ?? null)

export function useAdminAuth() {
  function setAdminKey(key) {
    adminKey.value = key
    localStorage.setItem(STORAGE_KEY, key)
  }

  function clearAdminKey() {
    adminKey.value = null
    localStorage.removeItem(STORAGE_KEY)
  }

  const isAuthenticated = () => !!adminKey.value

  return { adminKey, setAdminKey, clearAdminKey, isAuthenticated }
}
