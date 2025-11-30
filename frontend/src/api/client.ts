import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Log de depuração para requisições
apiClient.interceptors.request.use((config) => {
  console.log(`[API] Request: ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`, config.headers);
  return config;
});

// Função para obter token sem dependência circular
const getAuthToken = (): string | null => {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('hullzero_access_token')
}

// Interceptor para adicionar token de autenticação
apiClient.interceptors.request.use(
  (config) => {
    const token = getAuthToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Listener para atualização de token
if (typeof window !== 'undefined') {
  window.addEventListener('auth-token-updated', ((event: CustomEvent) => {
    const token = event.detail?.token
    if (token) {
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`
    }
  }) as EventListener)

  window.addEventListener('auth-token-removed', () => {
    delete apiClient.defaults.headers.common['Authorization']
  })
}

// Inicializar token se existir
const initialToken = getAuthToken()
if (initialToken) {
  apiClient.defaults.headers.common['Authorization'] = `Bearer ${initialToken}`
}

// Interceptor para tratamento de erros e renovação de token
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Tratamento de timeout e conexão
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      console.error('API Timeout: Backend não está respondendo. Verifique se o servidor está rodando em http://localhost:8000')
      return Promise.reject(error)
    }

    if (error.code === 'ECONNREFUSED') {
      console.error('API Connection Refused: Backend não está rodando. Inicie o servidor com: python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload')
      return Promise.reject(error)
    }

    // Tratamento de 401 (não autorizado)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        // Importar dinamicamente para evitar dependência circular
        const { default: authService } = await import('./authService')
        const newToken = await authService.refreshAccessToken()
        if (newToken) {
          originalRequest.headers.Authorization = `Bearer ${newToken}`
          return apiClient(originalRequest)
        }
      } catch (refreshError) {
        // Refresh falhou, fazer logout
        if (typeof window !== 'undefined') {
          const { default: authService } = await import('./authService')
          authService.logout()
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }
        }
        return Promise.reject(refreshError)
      }
    }

    // Outros erros
    if (error.response) {
      console.error('API Error:', error.response.data?.detail || error.message)
    } else {
      console.error('API Error:', error.message || error)
    }

    return Promise.reject(error)
  }
)

export default apiClient

