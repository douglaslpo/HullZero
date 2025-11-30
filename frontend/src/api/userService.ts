/**
 * Serviço de Gerenciamento de Usuários - HullZero
 */

import apiClient from './client'

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

export interface UserCreate {
  username: string
  email: string
  full_name: string
  password: string
  employee_id?: string
  department?: string
  position?: string
  phone?: string
}

export interface UserUpdate {
  email?: string
  full_name?: string
  phone?: string
  department?: string
  position?: string
  is_active?: boolean
}

export interface Role {
  id: string
  name: string
  description?: string
  level: number
}

export interface RoleAssign {
  role_id: string
}

class UserService {
  /**
   * Listar todos os usuários
   */
  async listUsers(skip: number = 0, limit: number = 100): Promise<User[]> {
    const response = await apiClient.get<User[]>('/api/auth/users', {
      params: { skip, limit }
    })
    return response.data
  }

  /**
   * Criar novo usuário
   */
  async createUser(userData: UserCreate): Promise<User> {
    const response = await apiClient.post<User>('/api/auth/users', userData)
    return response.data
  }

  /**
   * Atualizar usuário
   */
  async updateUser(userId: string, userData: UserUpdate): Promise<User> {
    const response = await apiClient.put<User>(`/api/auth/users/${userId}`, userData)
    return response.data
  }

  /**
   * Listar todos os papéis disponíveis
   */
  async listRoles(): Promise<Role[]> {
    const response = await apiClient.get<Role[]>('/api/auth/roles')
    return response.data
  }

  /**
   * Atribuir papel a usuário
   */
  async assignRole(userId: string, roleId: string): Promise<User> {
    const response = await apiClient.post<User>(
      `/api/auth/users/${userId}/roles`,
      { role_id: roleId }
    )
    return response.data
  }

  /**
   * Remover papel de usuário
   */
  async removeRole(userId: string, roleId: string): Promise<User> {
    const response = await apiClient.delete<User>(
      `/api/auth/users/${userId}/roles/${roleId}`
    )
    return response.data
  }
}

const userService = new UserService()
export default userService

