import { io } from 'socket.io-client'

let socket = null

export function useSocket() {
  if (!socket) {
    // En dev, VITE_API_URL est une URL complète (ex: http://localhost:5000).
    // En prod avec nginx, VITE_API_URL est un chemin relatif (/api) : on se
    // connecte à l'origine courante et nginx proxie /socket.io/ vers le backend.
    const apiUrl = import.meta.env.VITE_API_URL ?? ''
    const socketUrl = apiUrl.startsWith('http') ? apiUrl : window.location.origin
    socket = io(socketUrl)
  }
  return socket
}
