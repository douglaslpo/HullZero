/**
 * Componente de Rota Protegida - HullZero
 */

import { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Spinner, Box } from '@chakra-ui/react'

interface ProtectedRouteProps {
  children: ReactNode
  requiredRole?: string
  requiredAnyRole?: string[]
  requiredPermission?: string
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole,
  requiredAnyRole,
}: ProtectedRouteProps) => {
  const { isAuthenticated, isLoading, hasRole, hasAnyRole } = useAuth()

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minH="100vh">
        <Spinner size="xl" />
      </Box>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // Verificar papel específico
  if (requiredRole && !hasRole(requiredRole)) {
    return <Navigate to="/" replace />
  }

  // Verificar qualquer um dos papéis
  if (requiredAnyRole && !hasAnyRole(requiredAnyRole)) {
    return <Navigate to="/" replace />
  }

  // Verificar permissão (se implementado)
  // Por enquanto, verificamos através dos papéis

  return <>{children}</>
}

