import { useState, useMemo } from 'react'
import {
  Box,
  VStack,
  Heading,
  Text,
  Card,
  CardBody,
  Button,
  FormControl,
  FormLabel,
  Input,
  Select,
  Textarea,
  Grid,
  Alert,
  AlertIcon,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  ModalFooter,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  HStack,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Spinner,
  Center,
} from '@chakra-ui/react'
import { AddIcon } from '@chakra-ui/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { vesselService, maintenanceService, type MaintenanceEvent } from '../api/services'
import { format, parseISO } from 'date-fns'
import { ptBR } from 'date-fns/locale'

const getEventTypeColor = (type: string) => {
  switch (type) {
    case 'cleaning': return 'blue'
    case 'inspection': return 'purple'
    case 'dry_dock': return 'orange'
    case 'coating': return 'green'
    case 'application': return 'green'
    case 'repair': return 'red'
    default: return 'gray'
  }
}

const getEventTypeLabel = (type: string) => {
  switch (type) {
    case 'cleaning': return 'Limpeza'
    case 'inspection': return 'Inspeção'
    case 'dry_dock': return 'Doca Seca'
    case 'coating': return 'Revestimento'
    case 'application': return 'Aplicação de Tinta'
    case 'repair': return 'Reparo'
    default: return type
  }
}
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, ResponsiveContainer, Legend, Tooltip as RechartsTooltip,
} from 'recharts'


interface MaintenanceFormData {
  vessel_id: string
  event_type: string
  start_date: string
  end_date: string
  cleaning_method: string
  fouling_before_mm: number
  fouling_after_mm: number
  cost_brl: number
  port_name: string
  notes: string
}

const COLORS = ['#3182CE', '#805AD5', '#38A169', '#E53E3E', '#718096']

function Maintenance() {
  const { isOpen, onOpen, onClose } = useDisclosure()
  const [selectedVessel, setSelectedVessel] = useState<string>('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const queryClient = useQueryClient()
  const { register, handleSubmit, formState: { errors }, reset } = useForm<MaintenanceFormData>()

  // Buscar embarcações
  const { data: vessels } = useQuery({
    queryKey: ['vessels'],
    queryFn: () => vesselService.getAll(),
  })

  // Buscar histórico de manutenção
  const { data: maintenanceHistory, isLoading } = useQuery<MaintenanceEvent[]>({
    queryKey: ['maintenance-history', selectedVessel],
    queryFn: () => maintenanceService.getHistory(selectedVessel),
    enabled: !!selectedVessel,
  })

  // Calcular estatísticas
  // Calcular estatísticas
  const statistics = useMemo(() => {
    if (!maintenanceHistory) return {
      totalCost: 0,
      totalEvents: 0,
      averageCost: 0,
      cleaningEfficiency: 0,
      totalCleaningEvents: 0,
      eventsByType: {} as Record<string, number>
    }

    const totalCost = maintenanceHistory.reduce((acc, event) => acc + (event.total_cost_brl || 0), 0)
    const totalEvents = maintenanceHistory.length
    const averageCost = totalEvents > 0 ? totalCost / totalEvents : 0

    // Calcular eficiência média de limpeza (redução de fouling)
    const cleaningEvents = maintenanceHistory.filter(e => e.event_type === 'cleaning' && e.fouling_before_mm !== undefined && e.fouling_after_mm !== undefined)
    const totalEfficiency = cleaningEvents.reduce((acc, event) => {
      const before = event.fouling_before_mm || 0
      const after = event.fouling_after_mm || 0
      if (before === 0) return acc
      const reduction = (before - after) / before
      return acc + reduction
    }, 0)
    const cleaningEfficiency = cleaningEvents.length > 0 ? (totalEfficiency / cleaningEvents.length) * 100 : 0

    // Contagem por tipo
    const eventsByType = maintenanceHistory.reduce((acc, event) => {
      const type = event.event_type || 'unknown'
      acc[type] = (acc[type] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    return {
      totalCost,
      totalEvents,
      averageCost,
      cleaningEfficiency,
      totalCleaningEvents: cleaningEvents.length,
      eventsByType
    }
  }, [maintenanceHistory])

  const chartData = useMemo(() => {
    if (!maintenanceHistory) return []

    return maintenanceHistory
      .slice()
      .sort((a, b) => new Date(a.start_date).getTime() - new Date(b.start_date).getTime())
      .map(event => ({
        date: format(parseISO(event.start_date), 'dd/MM', { locale: ptBR }),
        cost: event.total_cost_brl || event.cost_brl || 0,
        type: event.event_type,
        event_type: event.event_type
      }))
  }, [maintenanceHistory])

  const pieData = useMemo(() => {
    if (!statistics.eventsByType) return []

    return Object.entries(statistics.eventsByType).map(([type, count]) => ({
      name: getEventTypeLabel(type),
      value: count
    }))
  }, [statistics])

  // Mutação para criar evento de manutenção
  const createMutation = useMutation({
    mutationFn: async (data: MaintenanceFormData) => {
      let photos_paths: string[] = []

      if (selectedFile) {
        try {
          const uploadResult = await maintenanceService.uploadImage(selectedFile)
          photos_paths.push(uploadResult.path)
        } catch (error) {
          console.error("Erro ao fazer upload da imagem:", error)
          // Continuar mesmo se falhar o upload? Por enquanto sim, mas logar erro
        }
      }

      return await maintenanceService.create(data.vessel_id, {
        ...data,
        photos_paths
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['maintenance-history'] })
      onClose()
      reset()
      setSelectedFile(null)
    },
  })

  const onSubmit = (data: MaintenanceFormData) => {
    createMutation.mutate(data)
  }

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0])
    }
  }



  return (
    <VStack spacing={6} align="stretch">
      {/* ... (existing header and vessel select) ... */}
      <HStack justify="space-between">
        <Box>
          <Heading size="xl" mb={2}>Manutenção</Heading>
          <Text color="gray.600">Registro e histórico de eventos de manutenção</Text>
        </Box>
        <Button leftIcon={<AddIcon />} colorScheme="blue" onClick={onOpen}>
          Registrar Manutenção
        </Button>
      </HStack>

      {/* Filtro de Embarcação */}
      <Card>
        <CardBody>
          <FormControl>
            <FormLabel>Selecionar Embarcação</FormLabel>
            <Select
              value={selectedVessel}
              onChange={(e) => setSelectedVessel(e.target.value)}
              placeholder="Selecione uma embarcação..."
            >
              {vessels?.map((vessel: any) => (
                <option key={vessel.id} value={vessel.id}>
                  {vessel.name} ({vessel.imo_number || vessel.vessel_id})
                </option>
              ))}
            </Select>
          </FormControl>
        </CardBody>
      </Card>

      {/* Conteúdo Principal com Tabs */}
      {selectedVessel && (
        <Tabs isLazy colorScheme="blue">
          <TabList>
            <Tab>Visão Geral</Tab>
            <Tab>Gráficos</Tab>
            <Tab>Histórico Detalhado</Tab>
          </TabList>

          <TabPanels>
            {/* Tab: Visão Geral */}
            <TabPanel>
              {isLoading ? (
                <Center py={8}>
                  <Spinner size="xl" />
                </Center>
              ) : maintenanceHistory && maintenanceHistory.length > 0 ? (
                <VStack spacing={6} align="stretch">
                  {/* ... (existing stats) ... */}
                  <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={4}>
                    <Stat>
                      <StatLabel>Total Investido</StatLabel>
                      <StatNumber>
                        {statistics.totalCost.toLocaleString('pt-BR', {
                          style: 'currency',
                          currency: 'BRL',
                        })}
                      </StatNumber>
                      <StatHelpText>{statistics.totalEvents} eventos</StatHelpText>
                    </Stat>
                    <Stat>
                      <StatLabel>Custo Médio por Evento</StatLabel>
                      <StatNumber>
                        {statistics.averageCost.toLocaleString('pt-BR', {
                          style: 'currency',
                          currency: 'BRL',
                        })}
                      </StatNumber>
                      <StatHelpText>Média geral</StatHelpText>
                    </Stat>
                    <Stat>
                      <StatLabel>Eficiência de Limpeza</StatLabel>
                      <StatNumber>
                        {statistics.cleaningEfficiency.toFixed(1)}%
                      </StatNumber>
                      <StatHelpText>
                        {statistics.totalCleaningEvents} limpezas realizadas
                      </StatHelpText>
                    </Stat>
                    <Stat>
                      <StatLabel>Total de Eventos</StatLabel>
                      <StatNumber>{statistics.totalEvents}</StatNumber>
                      <StatHelpText>Histórico completo</StatHelpText>
                    </Stat>
                  </SimpleGrid>

                  {/* Distribuição por Tipo */}
                  <Card>
                    <CardBody>
                      <Heading size="md" mb={4}>Distribuição por Tipo de Evento</Heading>
                      <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
                        {Object.entries(statistics.eventsByType).map(([type, count]) => (
                          <Box key={type} textAlign="center" p={4} bg={`${getEventTypeColor(type)}.50`} borderRadius="md">
                            <Badge colorScheme={getEventTypeColor(type)} fontSize="lg" mb={2}>
                              {getEventTypeLabel(type)}
                            </Badge>
                            <Text fontSize="2xl" fontWeight="bold">{count}</Text>
                            <Text fontSize="sm" color="gray.600">eventos</Text>
                          </Box>
                        ))}
                      </SimpleGrid>
                    </CardBody>
                  </Card>

                  {/* Últimos Eventos */}
                  <Card>
                    <CardBody>
                      <Heading size="md" mb={4}>Últimos 5 Eventos</Heading>
                      <Table variant="simple">
                        <Thead>
                          <Tr>
                            <Th>Tipo</Th>
                            <Th>Data</Th>
                            <Th>Método</Th>
                            <Th>Custo</Th>
                            <Th>Porto</Th>
                            <Th>Fotos</Th>
                          </Tr>
                        </Thead>
                        <Tbody>
                          {maintenanceHistory.slice(0, 5).map((event) => (
                            <Tr key={event.id}>
                              <Td>
                                <Badge colorScheme={getEventTypeColor(event.event_type)}>
                                  {getEventTypeLabel(event.event_type)}
                                </Badge>
                              </Td>
                              <Td>{format(parseISO(event.start_date), 'dd/MM/yyyy', { locale: ptBR })}</Td>
                              <Td>{event.cleaning_method || 'N/A'}</Td>
                              <Td>
                                {(event.total_cost_brl || event.cost_brl || 0).toLocaleString('pt-BR', {
                                  style: 'currency',
                                  currency: 'BRL',
                                })}
                              </Td>
                              <Td>{event.port_name}</Td>
                              <Td>
                                {event.photos_paths && event.photos_paths.length > 0 ? (
                                  <Badge colorScheme="green">Sim</Badge>
                                ) : (
                                  <Text color="gray.400">-</Text>
                                )}
                              </Td>
                            </Tr>
                          ))}
                        </Tbody>
                      </Table>
                    </CardBody>
                  </Card>
                </VStack>
              ) : (
                <Alert status="info">
                  <AlertIcon />
                  Nenhum evento de manutenção encontrado para esta embarcação.
                </Alert>
              )}
            </TabPanel>

            {/* Tab: Gráficos */}
            <TabPanel>
              {isLoading ? (
                <Center py={8}>
                  <Spinner size="xl" />
                </Center>
              ) : chartData.length > 0 ? (
                <VStack spacing={6} align="stretch">
                  {/* Custo ao Longo do Tempo */}
                  <Card>
                    <CardBody>
                      <Heading size="md" mb={4}>Custo de Manutenção ao Longo do Tempo</Heading>
                      <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={chartData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" />
                          <YAxis />
                          <RechartsTooltip />
                          <Legend />
                          <Line
                            type="monotone"
                            dataKey="cost"
                            stroke="#3182CE"
                            strokeWidth={2}
                            name="Custo (R$)"
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </CardBody>
                  </Card>

                  {/* Distribuição por Tipo */}
                  <Card>
                    <CardBody>
                      <Heading size="md" mb={4}>Distribuição de Eventos por Tipo</Heading>
                      <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                          <Pie
                            data={pieData}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                            outerRadius={100}
                            fill="#8884d8"
                            dataKey="value"
                          >
                            {pieData.map((_entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <RechartsTooltip />
                        </PieChart>
                      </ResponsiveContainer>
                    </CardBody>
                  </Card>

                  {/* Eficiência de Limpeza */}
                  {chartData.filter((d) => d.event_type === 'cleaning').length > 0 && (
                    <Card>
                      <CardBody>
                        <Heading size="md" mb={4}>Eficiência de Limpeza (Redução de Bioincrustação)</Heading>
                        <ResponsiveContainer width="100%" height={300}>
                          <BarChart data={chartData.filter((d) => d.event_type === 'cleaning')}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" />
                            <YAxis />
                            <RechartsTooltip />
                            <Legend />
                            <Bar dataKey="reduction" fill="#38A169" name="Redução (%)" />
                          </BarChart>
                        </ResponsiveContainer>
                      </CardBody>
                    </Card>
                  )}

                  {/* Bioincrustação Antes vs Depois */}
                  {chartData.filter((d) => d.event_type === 'cleaning').length > 0 && (
                    <Card>
                      <CardBody>
                        <Heading size="md" mb={4}>Bioincrustação Antes vs Depois (Limpezas)</Heading>
                        <ResponsiveContainer width="100%" height={300}>
                          <BarChart data={chartData.filter((d) => d.event_type === 'cleaning')}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" />
                            <YAxis />
                            <RechartsTooltip />
                            <Legend />
                            <Bar dataKey="fouling_before" fill="#E53E3E" name="Antes (mm)" />
                            <Bar dataKey="fouling_after" fill="#38A169" name="Depois (mm)" />
                          </BarChart>
                        </ResponsiveContainer>
                      </CardBody>
                    </Card>
                  )}
                </VStack>
              ) : (
                <Alert status="info">
                  <AlertIcon />
                  Nenhum dado disponível para visualização.
                </Alert>
              )}
            </TabPanel>

            {/* Tab: Histórico Detalhado */}
            <TabPanel>
              {isLoading ? (
                <Center py={8}>
                  <Spinner size="xl" />
                </Center>
              ) : maintenanceHistory && maintenanceHistory.length > 0 ? (
                <Card>
                  <CardBody>
                    <Table variant="simple">
                      <Thead>
                        <Tr>
                          <Th>Tipo</Th>
                          <Th>Data Início</Th>
                          <Th>Data Fim</Th>
                          <Th>Duração (h)</Th>
                          <Th>Método</Th>
                          <Th>Bioincrustação Antes (mm)</Th>
                          <Th>Bioincrustação Depois (mm)</Th>
                          <Th>Custo (R$)</Th>
                          <Th>Porto</Th>
                          <Th>Fotos</Th>
                        </Tr>
                      </Thead>
                      <Tbody>
                        {maintenanceHistory.map((event) => (
                          <Tr key={event.id}>
                            <Td>
                              <Badge colorScheme={getEventTypeColor(event.event_type)}>
                                {getEventTypeLabel(event.event_type)}
                              </Badge>
                            </Td>
                            <Td>{format(parseISO(event.start_date), 'dd/MM/yyyy', { locale: ptBR })}</Td>
                            <Td>{event.end_date ? format(parseISO(event.end_date), 'dd/MM/yyyy', { locale: ptBR }) : 'N/A'}</Td>
                            <Td>{event.duration_hours?.toFixed(1) || 'N/A'}</Td>
                            <Td>{event.cleaning_method || 'N/A'}</Td>
                            <Td>{event.fouling_before_mm?.toFixed(2) || 'N/A'}</Td>
                            <Td>{event.fouling_after_mm?.toFixed(2) || 'N/A'}</Td>
                            <Td>
                              {(event.total_cost_brl || event.cost_brl || 0).toLocaleString('pt-BR', {
                                style: 'currency',
                                currency: 'BRL',
                              })}
                            </Td>
                            <Td>{event.port_name}</Td>
                            <Td>
                              {event.photos_paths && event.photos_paths.length > 0 ? (
                                <Badge colorScheme="green">Sim</Badge>
                              ) : (
                                <Text color="gray.400">-</Text>
                              )}
                            </Td>
                          </Tr>
                        ))}
                      </Tbody>
                    </Table>
                  </CardBody>
                </Card>
              ) : (
                <Alert status="info">
                  <AlertIcon />
                  Nenhum evento de manutenção encontrado para esta embarcação.
                </Alert>
              )}
            </TabPanel>
          </TabPanels>
        </Tabs>
      )}

      {!selectedVessel && (
        <Alert status="info">
          <AlertIcon />
          Selecione uma embarcação para visualizar o histórico.
        </Alert>
      )}

      {/* Modal de Registro */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl" scrollBehavior="inside">
        <ModalOverlay />
        <ModalContent>
          <form onSubmit={handleSubmit(onSubmit)}>
            <ModalHeader>Registrar Evento de Manutenção</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <VStack spacing={4}>
                <FormControl isInvalid={!!errors.vessel_id}>
                  <FormLabel>Embarcação *</FormLabel>
                  <Select {...register('vessel_id', { required: 'Embarcação é obrigatória' })}>
                    <option value="">Selecione...</option>
                    {vessels?.map((vessel: any) => (
                      <option key={vessel.id} value={vessel.id}>
                        {vessel.name}
                      </option>
                    ))}
                  </Select>
                </FormControl>

                <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={4} width="100%">
                  <FormControl isInvalid={!!errors.event_type}>
                    <FormLabel>Tipo de Evento *</FormLabel>
                    <Select {...register('event_type', { required: 'Tipo é obrigatório' })}>
                      <option value="">Selecione...</option>
                      <option value="cleaning">Limpeza</option>
                      <option value="painting">Pintura</option>
                      <option value="inspection">Inspeção</option>
                      <option value="repair">Reparo</option>
                    </Select>
                  </FormControl>
                  <FormControl isInvalid={!!errors.cleaning_method}>
                    <FormLabel>Método de Limpeza *</FormLabel>
                    <Select {...register('cleaning_method', { required: 'Método é obrigatório' })}>
                      <option value="">Selecione...</option>
                      <option value="dry_dock">Estaleiro</option>
                      <option value="underwater">Subaquática</option>
                      <option value="high_pressure">Alta Pressão</option>
                    </Select>
                  </FormControl>
                  <FormControl isInvalid={!!errors.start_date}>
                    <FormLabel>Data de Início *</FormLabel>
                    <Input type="datetime-local" {...register('start_date', { required: true })} />
                  </FormControl>
                  <FormControl isInvalid={!!errors.end_date}>
                    <FormLabel>Data de Fim *</FormLabel>
                    <Input type="datetime-local" {...register('end_date', { required: true })} />
                  </FormControl>
                  <FormControl isInvalid={!!errors.fouling_before_mm}>
                    <FormLabel>Bioincrustação Antes (mm) *</FormLabel>
                    <Input type="number" step="0.01" {...register('fouling_before_mm', { required: true, valueAsNumber: true })} />
                  </FormControl>
                  <FormControl isInvalid={!!errors.fouling_after_mm}>
                    <FormLabel>Bioincrustação Depois (mm) *</FormLabel>
                    <Input type="number" step="0.01" {...register('fouling_after_mm', { required: true, valueAsNumber: true })} />
                  </FormControl>
                  <FormControl isInvalid={!!errors.cost_brl}>
                    <FormLabel>Custo (R$) *</FormLabel>
                    <Input type="number" step="0.01" {...register('cost_brl', { required: true, valueAsNumber: true })} />
                  </FormControl>
                  <FormControl isInvalid={!!errors.port_name}>
                    <FormLabel>Porto *</FormLabel>
                    <Input {...register('port_name', { required: true })} />
                  </FormControl>
                </Grid>

                <FormControl>
                  <FormLabel>Foto do Evento</FormLabel>
                  <Input
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    p={1}
                  />
                  {selectedFile && (
                    <Text fontSize="sm" color="green.500" mt={1}>
                      Arquivo selecionado: {selectedFile.name}
                    </Text>
                  )}
                </FormControl>

                <FormControl>
                  <FormLabel>Observações</FormLabel>
                  <Textarea {...register('notes')} rows={3} />
                </FormControl>
              </VStack>
            </ModalBody>
            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onClose}>
                Cancelar
              </Button>
              <Button
                type="submit"
                colorScheme="blue"
                isLoading={createMutation.isPending}
              >
                Registrar
              </Button>
            </ModalFooter>
          </form>
        </ModalContent>
      </Modal>
    </VStack>
  )
}

export default Maintenance
