import axios, { AxiosError } from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE ?? '/api/v1'

export function getToken() {
  return localStorage.getItem('access_token')
}

export function setToken(token: string | null) {
  if (token) {
    localStorage.setItem('access_token', token)
  } else {
    localStorage.removeItem('access_token')
  }
}

export const http = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
})

http.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string }>) => {
    if (error.response?.status === 401) {
      setToken(null)
    }
    const detail = error.response?.data?.detail
    return Promise.reject(new Error(detail || error.message || '请求失败'))
  }
)

export async function api<T>(path: string): Promise<T>
export async function api<T>(path: string, options: { method?: string; body?: string }): Promise<T>
export async function api<T>(path: string, options: { method?: string; body?: string } = {}): Promise<T> {
  const response = await http.request<T>({
    url: path,
    method: options.method || 'GET',
    data: options.body ? JSON.parse(options.body) : undefined
  })
  return response.data
}
