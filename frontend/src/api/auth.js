export class AuthApi {
  #client

  constructor(client) {
    this.#client = client
  }

  register(name, password) {
    return this.#client.post('/auth/register', {
      body: { name, ...(password !== undefined && { password }) },
    })
  }

  setPassword(name, password, currentPassword) {
    return this.#client.post('/auth/set-password', {
      body: {
        name,
        password,
        ...(currentPassword !== undefined && { current_password: currentPassword }),
      },
    })
  }

  async login(name, password) {
    const data = await this.#client.post('/auth/login', { body: { name, password } })
    this.#client.setToken(data.token)
    return data
  }

  me() {
    return this.#client.get('/auth/me')
  }

  logout() {
    this.#client.clearToken()
  }
}
