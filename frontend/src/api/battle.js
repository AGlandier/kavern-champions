export class BattleApi {
  #client

  constructor(client) {
    this.#client = client
  }

  getAll() {
    return this.#client.get('/battleroom/battle')
  }

  getById(battleId) {
    return this.#client.get(`/battleroom/battle/${battleId}`)
  }

  getByUser(username) {
    return this.#client.get(`/battleroom/battle/${username}`)
  }

  setRoom(battleId, championsRoomId) {
    return this.#client.post('/battleroom/battle/set-room', {
      body: { battle_id: battleId, champions_room_id: championsRoomId },
    })
  }

  end(battleId, result, adminKey) {
    return this.#client.post('/battleroom/battle/end', {
      body: { battle_id: battleId, ...(result !== undefined && { result }) },
      adminKey,
    })
  }
}
