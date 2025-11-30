/**
 * Página de Login - HullZero
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Container,
  FormControl,
  FormLabel,
  Input,
  Button,
  Alert,
  AlertIcon,
  VStack,
  Card,
  CardBody,
  Text,
} from '@chakra-ui/react'
import { useAuth } from '../contexts/AuthContext'

function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      await login({ username, password })
      navigate('/')
    } catch (err: any) {
      console.error('Login error:', err)
      const errorMessage = err?.response?.data?.detail ||
        err?.message ||
        'Erro ao fazer login. Verifique suas credenciais e se o backend está rodando em http://localhost:8000'
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Box
      minH="100vh"
      bg="gray.50"
      display="flex"
      alignItems="center"
      justifyContent="center"
      backgroundImage="linear-gradient(135deg, #E6F2FF 0%, #F5F7FA 50%, #E8F5E9 100%)"
      backgroundSize="cover"
    >
      <Container maxW="md">
        <Card boxShadow="2xl" borderRadius="2xl" border="1px solid" borderColor="brand.100">
          <CardBody p={8}>
            <VStack spacing={6} align="stretch">
              <Box textAlign="center" py={4}>
                <Box display="flex" justifyContent="center" mb={3}>
                  <img
                    src="/logo-login.svg"
                    alt="HullZero Logo"
                    style={{ height: '60px', maxWidth: '100%' }}
                  />
                </Box>
                <Text color="gray.600" mt={3} fontSize="sm" fontWeight="normal">
                  Sistema de Monitoramento de Bioincrustação
                </Text>
              </Box>

              {error && (
                <Alert status="error">
                  <AlertIcon />
                  {error}
                </Alert>
              )}

              <form onSubmit={handleSubmit}>
                <VStack spacing={4}>
                  <FormControl isRequired>
                    <FormLabel>Usuário</FormLabel>
                    <Input
                      type="text"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      placeholder="Digite seu usuário"
                      autoComplete="username"
                      autoFocus
                    />
                  </FormControl>

                  <FormControl isRequired>
                    <FormLabel>Senha</FormLabel>
                    <Input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Digite sua senha"
                      autoComplete="current-password"
                    />
                  </FormControl>

                  <Button
                    type="submit"
                    colorScheme="brand"
                    width="full"
                    size="lg"
                    isLoading={isLoading}
                    loadingText="Entrando..."
                  >
                    Entrar
                  </Button>
                </VStack>
              </form>

              <Box textAlign="center" fontSize="sm" color="gray.600">
                <Text>
                  Usuário padrão: <strong>admin</strong> / Senha: <strong>admin123</strong>
                </Text>
                <Text mt={2} fontSize="xs">
                  Altere a senha após o primeiro login
                </Text>
              </Box>
            </VStack>
          </CardBody>
        </Card>
      </Container>
    </Box>
  )
}

export default Login

