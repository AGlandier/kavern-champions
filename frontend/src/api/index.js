import { ApiClient } from './client.js'
import { AuthApi } from './auth.js'
import { UserApi } from './user.js'
import { BattleRoomApi } from './battleroom.js'
import { BattleApi } from './battle.js'

export const client = new ApiClient(import.meta.env.VITE_API_URL ?? 'http://localhost:5000')

export const auth = new AuthApi(client)
export const user = new UserApi(client)
export const battleroom = new BattleRoomApi(client)
export const battle = new BattleApi(client)

export { ApiError } from './client.js'
