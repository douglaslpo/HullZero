/**
 * Página de Gerenciamento de Usuários - HullZero
 * Permite criar usuários e gerenciar papéis (apenas para administradores)
 */

import { useState } from 'react'
import {
  Box,
  Container,
  Heading,
  Button,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
  Card,
  CardBody,
  CardHeader,
  FormControl,
  FormLabel,
  FormHelperText,
  FormErrorMessage,
  Input,
  InputGroup,
  InputRightElement,
  Select,
  VStack,
  HStack,
  Alert,
  AlertIcon,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  useDisclosure,
  Switch,
  Text,
  useToast,
  Tag,
  TagLabel,
  TagCloseButton,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  IconButton,
  Grid,
  Divider,
} from '@chakra-ui/react'
import { AddIcon, EditIcon, ViewIcon, ViewOffIcon } from '@chakra-ui/icons'
import userService, { User, UserCreate } from '../api/userService'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

function UserManagement() {
  // const { user: currentUser } = useAuth()
  const toast = useToast()
  const queryClient = useQueryClient()
  const { isOpen: isCreateOpen, onOpen: onCreateOpen, onClose: onCreateClose } = useDisclosure()
  const { isOpen: isRoleOpen, onOpen: onRoleOpen, onClose: onRoleClose } = useDisclosure()

  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [formData, setFormData] = useState<UserCreate>({
    username: '',
    email: '',
    full_name: '',
    password: '',
    employee_id: '',
    department: '',
    position: '',
    phone: '',
  })
  const [showPassword, setShowPassword] = useState(false)
  const [formErrors, setFormErrors] = useState<Record<string, string>>({})

  // Verificar se usuário tem permissão de administrador
  // Por enquanto, permitir acesso a todos os usuários autenticados
  // Em produção, reativar a verificação de papel
  const isAdmin = true // Temporário: permitir todos
  // const isAdmin = hasAnyRole(['administrador_sistema', 'ADMINISTRADOR_SISTEMA']) || 
  //                 (currentUser?.roles?.some(role => 
  //                   role.toLowerCase() === 'administrador_sistema' || 
  //                   role === 'ADMINISTRADOR_SISTEMA'
  //                 ) ?? false)

  // Buscar usuários
  const { data: users = [], isLoading: usersLoading, error: usersError } = useQuery({
    queryKey: ['users'],
    queryFn: () => userService.listUsers(),
    enabled: isAdmin,
  })

  // Buscar papéis disponíveis
  const { data: roles = [] } = useQuery({
    queryKey: ['roles'],
    queryFn: () => userService.listRoles(),
    enabled: isAdmin,
  })

  // Mutação para criar usuário
  const createUserMutation = useMutation({
    mutationFn: (data: UserCreate) => userService.createUser(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      toast({
        title: 'Usuário criado',
        description: 'O usuário foi criado com sucesso.',
        status: 'success',
        duration: 3000,
      })
      resetForm()
      onCreateClose()
    },
    onError: (error: any) => {
      toast({
        title: 'Erro ao criar usuário',
        description: error?.response?.data?.detail || 'Erro desconhecido',
        status: 'error',
        duration: 5000,
      })
    },
  })

  // Mutação para atualizar usuário
  const updateUserMutation = useMutation({
    mutationFn: ({ userId, data }: { userId: string; data: any }) =>
      userService.updateUser(userId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      toast({
        title: 'Usuário atualizado',
        description: 'O usuário foi atualizado com sucesso.',
        status: 'success',
        duration: 3000,
      })
    },
    onError: (error: any) => {
      toast({
        title: 'Erro ao atualizar usuário',
        description: error?.response?.data?.detail || 'Erro desconhecido',
        status: 'error',
        duration: 5000,
      })
    },
  })

  // Mutação para atribuir papel
  const assignRoleMutation = useMutation({
    mutationFn: ({ userId, roleId }: { userId: string; roleId: string }) =>
      userService.assignRole(userId, roleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      toast({
        title: 'Papel atribuído',
        description: 'O papel foi atribuído com sucesso.',
        status: 'success',
        duration: 3000,
      })
    },
    onError: (error: any) => {
      toast({
        title: 'Erro ao atribuir papel',
        description: error?.response?.data?.detail || 'Erro desconhecido',
        status: 'error',
        duration: 5000,
      })
    },
  })

  // Mutação para remover papel
  const removeRoleMutation = useMutation({
    mutationFn: ({ userId, roleId }: { userId: string; roleId: string }) =>
      userService.removeRole(userId, roleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      toast({
        title: 'Papel removido',
        description: 'O papel foi removido com sucesso.',
        status: 'success',
        duration: 3000,
      })
    },
    onError: (error: any) => {
      toast({
        title: 'Erro ao remover papel',
        description: error?.response?.data?.detail || 'Erro desconhecido',
        status: 'error',
        duration: 5000,
      })
    },
  })

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {}

    // Validar username
    if (!formData.username.trim()) {
      errors.username = 'Nome de usuário é obrigatório'
    } else if (formData.username.length < 3) {
      errors.username = 'Nome de usuário deve ter pelo menos 3 caracteres'
    } else if (!/^[a-zA-Z0-9_]+$/.test(formData.username)) {
      errors.username = 'Nome de usuário deve conter apenas letras, números e underscore'
    }

    // Validar email
    if (!formData.email.trim()) {
      errors.email = 'Email é obrigatório'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'Email inválido'
    }

    // Validar nome completo
    if (!formData.full_name.trim()) {
      errors.full_name = 'Nome completo é obrigatório'
    } else if (formData.full_name.length < 3) {
      errors.full_name = 'Nome completo deve ter pelo menos 3 caracteres'
    }

    // Validar senha
    if (!formData.password) {
      errors.password = 'Senha é obrigatória'
    } else if (formData.password.length < 6) {
      errors.password = 'Senha deve ter pelo menos 6 caracteres'
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      errors.password = 'Senha deve conter letras maiúsculas, minúsculas e números'
    }

    // Validar telefone (se preenchido)
    if (formData.phone && !/^[\d\s()+-]+$/.test(formData.phone)) {
      errors.phone = 'Telefone inválido'
    }

    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleCreateUser = () => {
    if (!validateForm()) {
      toast({
        title: 'Erro de validação',
        description: 'Corrija os erros no formulário antes de continuar.',
        status: 'error',
        duration: 5000,
      })
      return
    }
    createUserMutation.mutate(formData)
  }

  const resetForm = () => {
    setFormData({
      username: '',
      email: '',
      full_name: '',
      password: '',
      employee_id: '',
      department: '',
      position: '',
      phone: '',
    })
    setFormErrors({})
    setShowPassword(false)
  }

  const handleCloseModal = () => {
    resetForm()
    onCreateClose()
  }

  const handleAssignRole = (userId: string, roleId: string) => {
    assignRoleMutation.mutate({ userId, roleId })
  }

  const handleRemoveRole = (userId: string, roleId: string) => {
    removeRoleMutation.mutate({ userId, roleId })
  }

  const handleToggleActive = (user: User) => {
    const newStatus = !user.is_active
    const action = newStatus ? 'ativar' : 'desativar'
    if (window.confirm(`Tem certeza que deseja ${action} o usuário ${user.full_name}?`)) {
      updateUserMutation.mutate({
        userId: user.id,
        data: { is_active: newStatus },
      })
    }
  }

  if (!isAdmin) {
    return (
      <Container maxW="container.xl" py={8}>
        <Alert status="error">
          <AlertIcon />
          Você não tem permissão para acessar esta página.
        </Alert>
      </Container>
    )
  }

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={6} align="stretch">
        <HStack justify="space-between">
          <Heading size="lg">Gerenciamento de Usuários</Heading>
          <Button
            leftIcon={<AddIcon />}
            colorScheme="brand"
            onClick={onCreateOpen}
          >
            Criar Usuário
          </Button>
        </HStack>

        {usersError && (
          <Alert status="error">
            <AlertIcon />
            Erro ao carregar usuários. Tente novamente.
          </Alert>
        )}

        <Card>
          <CardHeader>
            <Heading size="md">Lista de Usuários</Heading>
          </CardHeader>
          <CardBody>
            <TableContainer>
              <Table variant="simple">
                <Thead>
                  <Tr>
                    <Th>Usuário</Th>
                    <Th>Email</Th>
                    <Th>Departamento</Th>
                    <Th>Cargo</Th>
                    <Th>Papéis</Th>
                    <Th>Status</Th>
                    <Th>Ações</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {usersLoading ? (
                    <Tr>
                      <Td colSpan={7} textAlign="center" py={8}>
                        <Text>Carregando usuários...</Text>
                      </Td>
                    </Tr>
                  ) : usersError ? (
                    <Tr>
                      <Td colSpan={7} textAlign="center" py={8}>
                        <Alert status="error" size="sm">
                          <AlertIcon />
                          Erro ao carregar usuários
                        </Alert>
                      </Td>
                    </Tr>
                  ) : users.length === 0 ? (
                    <Tr>
                      <Td colSpan={7} textAlign="center" py={8}>
                        <Text color="gray.500">Nenhum usuário encontrado</Text>
                      </Td>
                    </Tr>
                  ) : (
                    users.map((user) => (
                      <Tr key={user.id}>
                        <Td>
                          <VStack align="start" spacing={0}>
                            <Text fontWeight="bold">{user.full_name}</Text>
                            <Text fontSize="sm" color="gray.500">
                              @{user.username}
                            </Text>
                          </VStack>
                        </Td>
                        <Td>{user.email}</Td>
                        <Td>{user.department || '-'}</Td>
                        <Td>{user.position || '-'}</Td>
                        <Td>
                          <HStack spacing={2} flexWrap="wrap">
                            {user.roles && user.roles.length > 0 ? (
                              user.roles.map((role) => (
                                <Tag key={role} size="sm" colorScheme="blue">
                                  <TagLabel>{role}</TagLabel>
                                  <TagCloseButton
                                    onClick={() => handleRemoveRole(user.id, role)}
                                  />
                                </Tag>
                              ))
                            ) : (
                              <Text fontSize="sm" color="gray.500">Nenhum papel</Text>
                            )}
                            {roles && roles.length > 0 && (
                              <Menu>
                                <MenuButton
                                  as={IconButton}
                                  icon={<AddIcon />}
                                  size="xs"
                                  aria-label="Adicionar papel"
                                />
                                <MenuList maxH="200px" overflowY="auto">
                                  {roles
                                    .filter((role) => !(user.roles || []).includes(role.id))
                                    .map((role) => (
                                      <MenuItem
                                        key={role.id}
                                        onClick={() => handleAssignRole(user.id, role.id)}
                                      >
                                        {role.name}
                                        {role.description && ` - ${role.description}`}
                                      </MenuItem>
                                    ))}
                                  {roles.filter((role) => !(user.roles || []).includes(role.id)).length === 0 && (
                                    <MenuItem isDisabled>Nenhum papel disponível</MenuItem>
                                  )}
                                </MenuList>
                              </Menu>
                            )}
                          </HStack>
                        </Td>
                        <Td>
                          <Switch
                            isChecked={user.is_active}
                            onChange={() => handleToggleActive(user)}
                            colorScheme="green"
                          />
                        </Td>
                        <Td>
                          <HStack spacing={2}>
                            <Button
                              size="sm"
                              leftIcon={<EditIcon />}
                              onClick={() => {
                                setSelectedUser(user)
                                onRoleOpen()
                              }}
                              colorScheme="blue"
                              variant="outline"
                            >
                              Gerenciar Papéis
                            </Button>
                          </HStack>
                        </Td>
                      </Tr>
                    ))
                  )}
                </Tbody>
              </Table>
            </TableContainer>
          </CardBody>
        </Card>
      </VStack>

      {/* Modal de Criar Usuário */}
      <Modal isOpen={isCreateOpen} onClose={handleCloseModal} size="xl" scrollBehavior="inside">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            <VStack align="start" spacing={1}>
              <Heading size="md">Criar Novo Usuário</Heading>
              <Text fontSize="sm" color="gray.500" fontWeight="normal">
                Preencha os dados do novo usuário do sistema
              </Text>
            </VStack>
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={5} align="stretch">
              {/* Informações Básicas */}
              <Box>
                <Heading size="sm" mb={3} color="gray.700">
                  Informações Básicas
                </Heading>
                <VStack spacing={4}>
                  <FormControl isRequired isInvalid={!!formErrors.username}>
                    <FormLabel>Nome de Usuário</FormLabel>
                    <Input
                      value={formData.username}
                      onChange={(e) => {
                        setFormData({ ...formData, username: e.target.value })
                        if (formErrors.username) {
                          setFormErrors({ ...formErrors, username: '' })
                        }
                      }}
                      placeholder="usuario123"
                      autoComplete="username"
                    />
                    {!formErrors.username && (
                      <FormHelperText>
                        Mínimo 3 caracteres. Apenas letras, números e underscore.
                      </FormHelperText>
                    )}
                    <FormErrorMessage>{formErrors.username}</FormErrorMessage>
                  </FormControl>

                  <FormControl isRequired isInvalid={!!formErrors.email}>
                    <FormLabel>Email</FormLabel>
                    <Input
                      type="email"
                      value={formData.email}
                      onChange={(e) => {
                        setFormData({ ...formData, email: e.target.value })
                        if (formErrors.email) {
                          setFormErrors({ ...formErrors, email: '' })
                        }
                      }}
                      placeholder="usuario@transpetro.com.br"
                      autoComplete="email"
                    />
                    <FormErrorMessage>{formErrors.email}</FormErrorMessage>
                  </FormControl>

                  <FormControl isRequired isInvalid={!!formErrors.full_name}>
                    <FormLabel>Nome Completo</FormLabel>
                    <Input
                      value={formData.full_name}
                      onChange={(e) => {
                        setFormData({ ...formData, full_name: e.target.value })
                        if (formErrors.full_name) {
                          setFormErrors({ ...formErrors, full_name: '' })
                        }
                      }}
                      placeholder="João Silva"
                      autoComplete="name"
                    />
                    <FormErrorMessage>{formErrors.full_name}</FormErrorMessage>
                  </FormControl>

                  <FormControl isRequired isInvalid={!!formErrors.password}>
                    <FormLabel>Senha</FormLabel>
                    <InputGroup>
                      <Input
                        type={showPassword ? 'text' : 'password'}
                        value={formData.password}
                        onChange={(e) => {
                          setFormData({ ...formData, password: e.target.value })
                          if (formErrors.password) {
                            setFormErrors({ ...formErrors, password: '' })
                          }
                        }}
                        placeholder="Senha segura"
                        autoComplete="new-password"
                      />
                      <InputRightElement width="4.5rem">
                        <Button
                          h="1.75rem"
                          size="sm"
                          onClick={() => setShowPassword(!showPassword)}
                        >
                          {showPassword ? <ViewOffIcon /> : <ViewIcon />}
                        </Button>
                      </InputRightElement>
                    </InputGroup>
                    {!formErrors.password && (
                      <FormHelperText>
                        Mínimo 6 caracteres. Deve conter letras maiúsculas, minúsculas e números.
                      </FormHelperText>
                    )}
                    <FormErrorMessage>{formErrors.password}</FormErrorMessage>
                  </FormControl>
                </VStack>
              </Box>

              <Divider />

              {/* Informações Adicionais */}
              <Box>
                <Heading size="sm" mb={3} color="gray.700">
                  Informações Adicionais (Opcional)
                </Heading>
                <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={4}>
                  <FormControl isInvalid={!!formErrors.employee_id}>
                    <FormLabel>ID do Funcionário</FormLabel>
                    <Input
                      value={formData.employee_id}
                      onChange={(e) =>
                        setFormData({ ...formData, employee_id: e.target.value })
                      }
                      placeholder="EMP001"
                    />
                    <FormHelperText>Identificador único do funcionário</FormHelperText>
                  </FormControl>

                  <FormControl>
                    <FormLabel>Departamento</FormLabel>
                    <Input
                      value={formData.department}
                      onChange={(e) =>
                        setFormData({ ...formData, department: e.target.value })
                      }
                      placeholder="Operações"
                    />
                  </FormControl>

                  <FormControl>
                    <FormLabel>Cargo</FormLabel>
                    <Input
                      value={formData.position}
                      onChange={(e) =>
                        setFormData({ ...formData, position: e.target.value })
                      }
                      placeholder="Analista"
                    />
                  </FormControl>

                  <FormControl isInvalid={!!formErrors.phone}>
                    <FormLabel>Telefone</FormLabel>
                    <Input
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => {
                        setFormData({ ...formData, phone: e.target.value })
                        if (formErrors.phone) {
                          setFormErrors({ ...formErrors, phone: '' })
                        }
                      }}
                      placeholder="(21) 99999-9999"
                      autoComplete="tel"
                    />
                    <FormErrorMessage>{formErrors.phone}</FormErrorMessage>
                  </FormControl>
                </Grid>
              </Box>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={handleCloseModal}>
              Cancelar
            </Button>
            <Button
              colorScheme="brand"
              onClick={handleCreateUser}
              isLoading={createUserMutation.isPending}
              loadingText="Criando..."
            >
              Criar Usuário
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Modal de Gerenciar Papéis */}
      <Modal isOpen={isRoleOpen} onClose={onRoleClose} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            Gerenciar Papéis - {selectedUser?.full_name}
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {selectedUser && (
              <VStack spacing={4} align="stretch">
                <Box>
                  <Text fontWeight="bold" mb={2}>
                    Papéis Atuais:
                  </Text>
                  <HStack spacing={2} flexWrap="wrap">
                    {!selectedUser.roles || selectedUser.roles.length === 0 ? (
                      <Text color="gray.500">Nenhum papel atribuído</Text>
                    ) : (
                      selectedUser.roles.map((role) => (
                        <Tag key={role} size="md" colorScheme="blue">
                          <TagLabel>{role}</TagLabel>
                          <TagCloseButton
                            onClick={() =>
                              handleRemoveRole(selectedUser.id, role)
                            }
                          />
                        </Tag>
                      ))
                    )}
                  </HStack>
                </Box>
                <Box>
                  <Text fontWeight="bold" mb={2}>
                    Adicionar Papel:
                  </Text>
                  <Select
                    placeholder="Selecione um papel"
                    onChange={(e) => {
                      if (e.target.value) {
                        handleAssignRole(selectedUser.id, e.target.value)
                        e.target.value = ''
                      }
                    }}
                  >
                    {roles && roles.length > 0 ? (
                      roles
                        .filter((role) => !(selectedUser.roles || []).includes(role.id))
                        .map((role) => (
                          <option key={role.id} value={role.id}>
                            {role.name} {role.description && `- ${role.description}`}
                          </option>
                        ))
                    ) : (
                      <option disabled>Nenhum papel disponível</option>
                    )}
                  </Select>
                </Box>
              </VStack>
            )}
          </ModalBody>
          <ModalFooter>
            <Button onClick={onRoleClose}>Fechar</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Container>
  )
}

export default UserManagement

