export class UserApi {
  #client

  constructor(client) {
    this.#client = client
  }

  isSecured(name) {
    return this.#client.get('/user/secured', { query: { name } })
  }

  getStats(name, battleroom_id = null) {
    const query = { name }
    if (battleroom_id !== null) query.battleroom_id = battleroom_id
    return this.#client.get('/user/stats', { query })
  }

  getBattleroom() {
    return this.#client.get('/user/battleroom')
  }

  updateTeamlist(battleroom_id, teamlist) {
    return this.#client.post('/user/teamlist', { body: { battleroom_id, teamlist } })
  }

  getActiveBattle(name) {
    return this.#client.get('/user/active-battle', { query: { name } })
  }
}
