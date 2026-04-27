export class BattleRoomApi {
  #client

  constructor(client) {
    this.#client = client
  }

  getAll({ limit, offset, query, orderBy } = {}) {
    return this.#client.get('/battleroom/', {
      query: { limit, offset, query, 'order-by': orderBy },
    })
  }

  getById(roomId) {
    return this.#client.get(`/battleroom/${roomId}`)
  }

  getBattles(roomId, { round, limit, offset } = {}) {
    return this.#client.get(`/battleroom/${roomId}/battles`, {
      query: { round, limit, offset },
    })
  }

  getPlayers(roomId, { limit, offset, query } = {}) {
    return this.#client.get(`/battleroom/${roomId}/players`, {
      query: { limit, offset, query },
    })
  }

  isPlayerInRoom(roomId, username) {
    return this.#client.get(`/battleroom/${roomId}/players/${username}`)
  }

  // Routes admin (X-Admin-Key requis)

  create(name, requiresTeamlist, adminKey) {
    return this.#client.post('/battleroom/create', { body: { name, requires_teamlist: requiresTeamlist }, adminKey })
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

  dropPlayer(battleroomId, username, adminKey) {
    return this.#client.post('/battleroom/drop', {
      body: { battleroom_id: battleroomId, username },
      adminKey,
    })
  }

  dropSelf(battleroomId) {
    return this.#client.post('/battleroom/drop', {
      body: { battleroom_id: battleroomId },
    })
  }

  // /battleroom/enter est intentionnellement absent — appelé par le bot Twitch uniquement
}
