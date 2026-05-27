import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { http, getToken, setToken } from '../api/client'
import type { TokenResponse, UserProfile } from '../types/finance'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(getToken())
  const user = ref<UserProfile | null>(null)
  const isAuthenticated = computed(() => Boolean(token.value))

  function applyToken(nextToken: string | null) {
    token.value = nextToken
    setToken(nextToken)
    if (!nextToken) user.value = null
  }

  async function login(email: string, password: string) {
    const { data } = await http.post<TokenResponse>('/auth/login', { email, password })
    applyToken(data.access_token)
    await loadMe()
  }

  async function register(email: string, password: string, displayName: string) {
    const { data } = await http.post<TokenResponse>('/auth/register', {
      email,
      password,
      display_name: displayName
    })
    applyToken(data.access_token)
    await loadMe()
  }

  async function loadMe() {
    if (!token.value) return
    const { data } = await http.get<UserProfile>('/me')
    user.value = data
  }

  async function logout() {
    try {
      if (token.value) await http.post('/auth/logout')
    } finally {
      applyToken(null)
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    applyToken,
    login,
    register,
    loadMe,
    logout
  }
})
