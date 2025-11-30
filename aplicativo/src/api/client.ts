import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

// URL de Produção
const API_URL = 'https://hullzero.siog.com.br';

const apiClient = axios.create({
    baseURL: API_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor para adicionar token de autenticação
apiClient.interceptors.request.use(
    async (config) => {
        try {
            const token = await SecureStore.getItemAsync('hullzero_access_token');
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
        } catch (error) {
            console.error('Erro ao ler token:', error);
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Interceptor para tratamento de erros
apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // Se der 401 (Não autorizado), limpar token
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            try {
                await SecureStore.deleteItemAsync('hullzero_access_token');
                // A navegação para login será tratada pelo AuthContext
            } catch (e) {
                console.error('Erro ao limpar token:', e);
            }
        }
        return Promise.reject(error);
    }
);

export default apiClient;
