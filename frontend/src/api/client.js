export class ApiError extends Error {
  constructor(status, message) {
    super(message)
    this.status = status
  }
}

export class ApiClient {
  #baseUrl
  #token = null

  constructor(baseUrl) {
    this.#baseUrl = baseUrl.replace(/\/$/, '')
  }

  setToken(token) {
    this.#token = token
  }

  clearToken() {
    this.#token = null
  }

  async request(method, path, { body, query, adminKey } = {}) {
    const url = new URL(this.#baseUrl + path, window.location.origin)

    if (query) {
      for (const [k, v] of Object.entries(query)) {
        if (v !== undefined && v !== null) url.searchParams.set(k, v)
      }
    }

    const headers = { 'Content-Type': 'application/json' }
    if (this.#token) headers['Authorization'] = `Bearer ${this.#token}`
    if (adminKey) headers['X-Admin-Key'] = adminKey

    const res = await fetch(url, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })

    if (!res.ok) {
      const text = await res.text().catch(() => res.statusText)
      throw new ApiError(res.status, text)
    }

    const text = await res.text()
    return text ? JSON.parse(text) : null
  }

  get(path, options) { return this.request('GET', path, options) }
  post(path, options) { return this.request('POST', path, options) }
}
