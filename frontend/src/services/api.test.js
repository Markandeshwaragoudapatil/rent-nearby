import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { apiRequest, resetCsrfToken } from "./api"

function jsonResponse(payload, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: new Headers({ "content-type": "application/json" }),
    json: vi.fn().mockResolvedValue(payload),
    text: vi.fn().mockResolvedValue(""),
  }
}

describe("API client", () => {
  beforeEach(() => {
    resetCsrfToken()
    vi.stubGlobal("fetch", vi.fn())
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("includes cookies on public GET requests", async () => {
    fetch.mockResolvedValueOnce(jsonResponse({ user: { id: "user-1" } }))
    const result = await apiRequest("/auth/me")
    expect(result.user.id).toBe("user-1")
    expect(fetch).toHaveBeenCalledTimes(1)
    expect(fetch.mock.calls[0][1].credentials).toBe("include")
  })

  it("fetches a CSRF token before unsafe requests", async () => {
    fetch
      .mockResolvedValueOnce(jsonResponse({ csrf_token: "csrf-test-token" }))
      .mockResolvedValueOnce(jsonResponse({ user: { id: "user-1" } }, 201))
    const result = await apiRequest("/auth/register", {
      method: "POST",
      body: { name: "Test User", email: "test@example.com", password: "correct horse battery staple" },
    })
    expect(result.user.id).toBe("user-1")
    expect(fetch).toHaveBeenCalledTimes(2)
    const request = fetch.mock.calls[1][1]
    expect(request.credentials).toBe("include")
    expect(request.headers.get("X-CSRFToken")).toBe("csrf-test-token")
    expect(JSON.parse(request.body).email).toBe("test@example.com")
  })

  it("returns structured API errors to the calling page", async () => {
    fetch.mockResolvedValueOnce(jsonResponse({ error: { message: "Invalid email or password." } }, 401))
    await expect(apiRequest("/auth/login")).rejects.toMatchObject({
      status: 401,
      message: "Invalid email or password.",
    })
  })
})
