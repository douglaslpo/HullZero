/**
 * Serviço de Autenticação - HullZero
 */

import axios from 'axios'

export interface LoginCredentials {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface User {
  id: string
  username: string
  email: string
  full_name: string
  is_active: boolean
  is_verified: boolean
  employee_id?: string
  department?: string
  position?: string
  roles: string[]
}

export interface PasswordChange {
  current_password: string
  new_password: string
}

class AuthService {
  private readonly TOKEN_KEY = 'hullzero_access_token'
  private readonly REFRESH_TOKEN_KEY = 'hullzero_refresh_token'
  private readonly USER_KEY = 'hullzero_user'
  private apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    timeout: 30000,
  })

  /**
   * Login
   */
  async login(credentials: LoginCredentials): Promise<TokenResponse> {
    const formData = new URLSearchParams()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)

    const response = await this.apiClient.post<TokenResponse>('/api/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })

    // Armazenar tokens
    this.setTokens(response.data.access_token, response.data.refresh_token)

    // Buscar informações do usuário
    await this.fetchCurrentUser()

    return response.data
  }

  /**
   * Logout
   */
  logout(): void {
    localStorage.removeItem(this.TOKEN_KEY)
    localStorage.removeItem(this.REFRESH_TOKEN_KEY)
    localStorage.removeItem(this.USER_KEY)
    this.removeAuthHeader()
  }

  /**
   * Obter usuário atual
   */
  async getCurrentUser(): Promise<User | null> {
    try {
      const token = this.getAccessToken()
      if (!token) return null

      const response = await this.apiClient.get<User>('/api/auth/me', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      this.setUser(response.data)
      return response.data
    } catch (error) {
      this.logout()
      return null
    }
  }

  /**
   * Buscar e armazenar usuário atual
   */
  async fetchCurrentUser(): Promise<User | null> {
    return this.getCurrentUser()
  }

  /**
   * Verificar se está autenticado
   */
  isAuthenticated(): boolean {
    return !!this.getAccessToken()
  }

  /**
   * Obter token de acesso
   */
  getAccessToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY)
  }

  /**
   * Obter refresh token
   */
  getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_TOKEN_KEY)
  }

  /**
   * Obter usuário armazenado
   */
  getUser(): User | null {
    const userStr = localStorage.getItem(this.USER_KEY)
    if (!userStr) return null
    try {
      return JSON.parse(userStr)
    } catch {
      return null
    }
  }

  /**
   * Armazenar tokens
   */
  private setTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem(this.TOKEN_KEY, accessToken)
    localStorage.setItem(this.REFRESH_TOKEN_KEY, refreshToken)
    this.setAuthHeader(accessToken)
  }

  /**
   * Armazenar usuário
   */
  private setUser(user: User): void {
    localStorage.setItem(this.USER_KEY, JSON.stringify(user))
  }

  /**
   * Configurar header de autenticação
   */
  setAuthHeader(token: string): void {
    // Será configurado no client.ts
    if (typeof window !== 'undefined') {
      const event = new CustomEvent('auth-token-updated', { detail: { token } })
      window.dispatchEvent(event)
    }
  }

  /**
   * Remover header de autenticação
   */
  removeAuthHeader(): void {
    if (typeof window !== 'undefined') {
      const event = new CustomEvent('auth-token-removed')
      window.dispatchEvent(event)
    }
  }

  /**
   * Renovar access token
   */
  async refreshAccessToken(): Promise<string | null> {
    const refreshToken = this.getRefreshToken()
    if (!refreshToken) {
      this.logout()
      return null
    }

    try {
      const response = await this.apiClient.post<TokenResponse>('/api/auth/refresh', {
        refresh_token: refreshToken,
      })

      this.setTokens(response.data.access_token, response.data.refresh_token)
      return response.data.access_token
    } catch (error) {
      this.logout()
      return null
    }
  }

  /**
   * Alterar senha
   */
  async changePassword(data: PasswordChange): Promise<void> {
    const token = this.getAccessToken()
    await this.apiClient.post('/api/auth/change-password', data, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
  }

  /**
   * Verificar se usuário tem papel
   */
  hasRole(role: string): boolean {
    const user = this.getUser()
    if (!user) return false
    return user.roles.includes(role)
  }

  /**
   * Verificar se usuário tem algum dos papéis
   */
  hasAnyRole(roles: string[]): boolean {
    const user = this.getUser()
    if (!user) return false
    return roles.some(role => user.roles.includes(role))
  }
}

// Instância singleton do serviço de autenticação
const authService = new AuthService()

export default authService

