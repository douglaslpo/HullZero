import apiClient from './client';
import * as SecureStore from 'expo-secure-store';

export const authService = {
    login: async (username: string, password: string) => {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await apiClient.post('/api/auth/login', formData.toString(), {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        });

        if (response.data.access_token) {
            await SecureStore.setItemAsync('hullzero_access_token', response.data.access_token);
        }
        return response.data;
    },

    logout: async () => {
        try {
            await SecureStore.deleteItemAsync('hullzero_access_token');
        } catch (error) {
            console.error('Erro ao fazer logout:', error);
        }
    },

    isAuthenticated: async () => {
        try {
            const token = await SecureStore.getItemAsync('hullzero_access_token');
            return !!token;
        } catch {
            return false;
        }
    }
};
