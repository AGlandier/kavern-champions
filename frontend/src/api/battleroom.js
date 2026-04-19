export class BattleRoomApi {
  #client

  constructor(client) {
    this.#client = client
  }

  getAll() {
    return this.#client.get('/battleroom/')
  }

  getById(roomId) {
    return this.#client.get(`/battleroom/${roomId}`)
  }

  getBattles(roomId, round) {
    return this.#client.get(`/battleroom/${roomId}/battles`, {
      query: round !== undefined ? { round } : {},
    })
  }

  getPlayers(roomId) {
    return this.#client.get(`/battleroom/${roomId}/players`)
  }

  isPlayerInRoom(roomId, username) {
    return this.#client.get(`/battleroom/${roomId}/players/${username}`)
  }

  // Routes admin (X-Admin-Key requis)

  create(name, adminKey) {
    return this.#client.post('/battleroom/create', { body: { name }, adminKey })
  }

  nextRound(battleroomId, adminKey) {
    return this.#client.post('/battleroom/next', {
      body: { battleroom_id: battleroomId },
      adminKey,
    })
  }

  end(battleroomId, adminKey) {
    return this.#client.post('/battleroom/end', {
      body: { battleroom_id: battleroomId },
      adminKey,
    })
  }

  // /battleroom/enter est intentionnellement absent — appelé par le bot Twitch uniquement
}
