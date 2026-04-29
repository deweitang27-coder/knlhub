import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器：自动携带 token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth-storage')
  if (token) {
    try {
      const parsed = JSON.parse(token)
      if (parsed?.state?.token) {
        config.headers.Authorization = `Bearer ${parsed.state.token}`
      }
    } catch {
      // 忽略解析错误
    }
  }
  return config
})

// 响应拦截器：处理 401 未授权
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth-storage')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// 认证相关 API
export const authApi = {
  login: async (email: string, password: string) => {
    const { data } = await api.post('/auth/login', { email, password })
    return data
  },
  register: async (email: string, password: string, name: string) => {
    const { data } = await api.post('/auth/register', { email, password, name })
    return data
  },
}

export default api
