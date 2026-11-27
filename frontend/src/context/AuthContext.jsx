import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react"
import { apiRequest } from "../services/api"

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [connectionError, setConnectionError] = useState("")

  const refreshUser = useCallback(async () => {
    try {
      const result = await apiRequest("/auth/me")
      setUser(result.user || null)
      setConnectionError("")
      return result.user || null
    } catch (error) {
      if (error.status === 401) {
        setUser(null)
        setConnectionError("")
        return null
      }
      setUser(null)
      setConnectionError(error.message || "The RentNearby API is unavailable.")
      return null
    }
  }, [])

  useEffect(() => {
    let active = true
    apiRequest("/auth/me")
      .then(result => {
        if (active) {
          setUser(result.user || null)
          setConnectionError("")
        }
      })
      .catch(error => {
        if (active) {
          setUser(null)
          if (error.status !== 401) setConnectionError(error.message || "The RentNearby API is unavailable.")
        }
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => { active = false }
  }, [])

  const login = useCallback(async credentials => {
    const result = await apiRequest("/auth/login", { method: "POST", body: credentials })
    setUser(result.user)
    setConnectionError("")
    return result.user
  }, [])

  const register = useCallback(async details => {
    const result = await apiRequest("/auth/register", { method: "POST", body: details })
    setUser(result.user)
    setConnectionError("")
    return result.user
  }, [])

  const logout = useCallback(async () => {
    await apiRequest("/auth/logout", { method: "POST" })
    setUser(null)
  }, [])

  const value = useMemo(() => ({
    user, loading, connectionError, login, register, logout, refreshUser,
  }), [user, loading, connectionError, login, register, logout, refreshUser])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error("useAuth must be used inside AuthProvider")
  return context
}
