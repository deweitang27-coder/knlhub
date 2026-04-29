import { create } from 'zustand'

interface AuthState {
  isAuthenticated: boolean
  user: { email: string; name: string } | null
  token: string | null

  login: (token: string, email: string, name: string) => void
  logout: () => void
  checkAuth: () => boolean
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  user: null,
  token: null,

  login: (token, email, name) => {
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify({ email, name }))
    set({ isAuthenticated: true, user: { email, name }, token })
  },

  logout: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    set({ isAuthenticated: false, user: null, token: null })
  },

  checkAuth: () => {
    const token = localStorage.getItem('token')
    const userStr = localStorage.getItem('user')
    if (token && userStr) {
      const user = JSON.parse(userStr)
      set({ isAuthenticated: true, user, token })
      return true
    }
    set({ isAuthenticated: false, user: null, token: null })
    return false
  },
}))
