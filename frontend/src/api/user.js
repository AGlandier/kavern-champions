export class UserApi {
  #client

  constructor(client) {
    this.#client = client
  }

  isSecured(name) {
    return this.#client.get('/user/secured', { query: { name } })
  }

  getStats(name) {
    return this.#client.get('/user/stats', { query: { name } })
  }

  updateTeamlist(teamlist) {
    return this.#client.post('/user/teamlist', { body: { teamlist } })
  }

  getActiveBattle(name) {
    return this.#client.get('/user/active-battle', { query: { name } })
  }
}
