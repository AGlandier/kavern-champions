import { ref } from 'vue'
import { auth, client } from '../api/index.js'

const TOKEN_KEY = 'kc-user-token'
const USER_KEY = 'kc-user-name'

const currentUser = ref(localStorage.getItem(USER_KEY) ?? null)

const savedToken = localStorage.getItem(TOKEN_KEY)
if (savedToken) client.setToken(savedToken)

export function useUserAuth() {
  async function login(name, password) {
    const data = await auth.login(name, password)
    localStorage.setItem(TOKEN_KEY, data.token)
    localStorage.setItem(USER_KEY, name)
    currentUser.value = name
    return data
  }

  function logout() {
    auth.logout()
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    currentUser.value = null
  }

  const isAuthenticated = () => !!currentUser.value

  return { currentUser, login, logout, isAuthenticated }
}
