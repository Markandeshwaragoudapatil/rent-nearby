const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api/v1").replace(/\/$/, "")

let csrfTokenCache = null

export class ApiError extends Error {
  constructor(message, status, payload) {
    super(message)
    this.name = "ApiError"
    this.status = status
    this.payload = payload
  }
}

async function readResponse(response) {
  const contentType = response.headers.get("content-type") || ""
  if (contentType.includes("application/json")) {
    return response.json()
  }
  const text = await response.text()
  return text ? { error: { message: text } } : {}
}

async function getCsrfToken() {
  if (csrfTokenCache) return csrfTokenCache
  const response = await fetch(`${API_BASE_URL}/auth/csrf`, {
    method: "GET",
    credentials: "include",
    headers: { Accept: "application/json" },
  })
  const payload = await readResponse(response)
  if (!response.ok || !payload.csrf_token) {
    throw new ApiError(payload?.error?.message || "Could not start a secure session.", response.status, payload)
  }
  csrfTokenCache = payload.csrf_token
  return csrfTokenCache
}

export async function apiRequest(path, options = {}) {
  const method = (options.method || "GET").toUpperCase()
  const headers = new Headers(options.headers || {})
  headers.set("Accept", "application/json")
  let body = options.body

  if (body !== undefined && !(body instanceof FormData) && typeof body !== "string") {
    headers.set("Content-Type", "application/json")
    body = JSON.stringify(body)
  }

  if (!["GET", "HEAD", "OPTIONS"].includes(method)) {
    headers.set("X-CSRFToken", await getCsrfToken())
  }

  const response = await fetch(`${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`, {
    ...options,
    method,
    headers,
    body,
    credentials: "include",
  })
  const payload = await readResponse(response)

  if (!response.ok) {
    const message = payload?.error?.message || payload?.message || "The request could not be completed."
    if (response.status === 400 && /csrf/i.test(message)) csrfTokenCache = null
    throw new ApiError(message, response.status, payload)
  }

  if (["/auth/login", "/auth/register", "/auth/logout"].some(route => path === route)) {
    csrfTokenCache = null
  }
  return payload
}

export function resetCsrfToken() {
  csrfTokenCache = null
}
