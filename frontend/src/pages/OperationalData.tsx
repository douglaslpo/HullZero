import { useState } from 'react'
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
  HStack,
  Spinner,
  Center,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Badge,
  Divider,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Progress,
} from '@chakra-ui/react'
import { AddIcon, DownloadIcon } from '@chakra-ui/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { 
  LineChart, 
  Line, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip as RechartsTooltip, 
  Legend, 
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  ComposedChart,
  Area,
  AreaChart,
} from 'recharts'
import { vesselService, operationalDataService } from '../api/services'
import type { OperationalData } from '../api/services'

interface OperationalDataFormData {
  vessel_id: string
  latitude: number
  longitude: number
  speed_knots: number
  engine_power_kw: number
  fuel_consumption_kg_h: number
  water_temperature_c: number
  wind_speed_knots: number
  wave_height_m: number
}

function OperationalData() {
  const { isOpen, onOpen, onClose } = useDisclosure()
  const [selectedVessel, setSelectedVessel] = useState<string>('')
  const [selectedTab, setSelectedTab] = useState(0)
  const queryClient = useQueryClient()
  const { register, handleSubmit, formState: { errors }, reset } = useForm<OperationalDataFormData>()

  // Buscar embarcações para o select
  const { data: vessels } = useQuery({
    queryKey: ['vessels'],
    queryFn: async () => {
      try {
        return await vesselService.getAll(true)
      } catch {
        return await vesselService.getAll(false)
      }
    },
  })

  // Buscar dados operacionais
  const { data: operationalData, isLoading } = useQuery<OperationalData[]>({
    queryKey: ['operational-data', selectedVessel],
    queryFn: async () => {
      if (!selectedVessel) return []
      return await operationalDataService.getHistory(selectedVessel)
    },
    enabled: !!selectedVessel,
    refetchInterval: 60000, // Atualizar a cada minuto
  })

  // Buscar últimos dados
  const { data: latestData } = useQuery<OperationalData>({
    queryKey: ['operational-data-latest', selectedVessel],
    queryFn: async () => {
      if (!selectedVessel) throw new Error('No vessel selected')
      return await operationalDataService.getLatest(selectedVessel)
    },
    enabled: !!selectedVessel,
    refetchInterval: 30000, // Atualizar a cada 30 segundos
  })

  // Mutação para criar dados operacionais
  const createMutation = useMutation({
    mutationFn: async (data: OperationalDataFormData) => {
      return await operationalDataService.create(data.vessel_id, data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['operational-data'] })
      onClose()
      reset()
    },
  })

  const onSubmit = (data: OperationalDataFormData) => {
    createMutation.mutate(data)
  }

  // Calcular estatísticas
  const stats = operationalData && operationalData.length > 0 ? {
    avgSpeed: operationalData.reduce((sum, d) => sum + d.speed_knots, 0) / operationalData.length,
    avgPower: operationalData.reduce((sum, d) => sum + d.engine_power_kw, 0) / operationalData.length,
    avgFuel: operationalData.reduce((sum, d) => sum + d.fuel_consumption_kg_h, 0) / operationalData.length,
    avgWaterTemp: operationalData.reduce((sum, d) => sum + d.water_temperature_c, 0) / operationalData.length,
    avgWind: operationalData.reduce((sum, d) => sum + d.wind_speed_knots, 0) / operationalData.length,
    avgWave: operationalData.reduce((sum, d) => sum + d.wave_height_m, 0) / operationalData.length,
    maxSpeed: Math.max(...operationalData.map(d => d.speed_knots)),
    minSpeed: Math.min(...operationalData.map(d => d.speed_knots)),
    totalFuel: operationalData.reduce((sum, d) => sum + d.fuel_consumption_kg_h, 0),
    dataPoints: operationalData.length,
  } : null

  // Preparar dados para gráficos (últimos 30 pontos ou todos se menos)
  const chartData = operationalData 
    ? operationalData.slice(0, 30).reverse().map((d, i) => ({
        time: new Date(d.timestamp).toLocaleString('pt-BR', { 
          month: 'short', 
          day: 'numeric', 
          hour: '2-digit',
          minute: '2-digit'
        }),
        speed: d.speed_knots,
        power: d.engine_power_kw,
        fuel: d.fuel_consumption_kg_h,
        waterTemp: d.water_temperature_c,
        wind: d.wind_speed_knots,
        wave: d.wave_height_m,
        index: i,
      }))
    : []

  // Dados para gráfico de correlação
  const correlationData = operationalData 
    ? operationalData.slice(0, 50).map(d => ({
        speed: d.speed_knots,
        fuel: d.fuel_consumption_kg_h,
        power: d.engine_power_kw,
      }))
    : []

  // Função de exportação
  const exportToCSV = () => {
    if (!operationalData || !operationalData.length) return

    const headers = [
      'Data/Hora',
      'Latitude',
      'Longitude',
      'Velocidade (nós)',
      'Potência (kW)',
      'Consumo Combustível (kg/h)',
      'Temp. Água (°C)',
      'Velocidade Vento (nós)',
      'Altura Ondas (m)',
    ]

    const rows = operationalData.map(data => [
      new Date(data.timestamp).toLocaleString('pt-BR'),
      data.latitude.toFixed(4),
      data.longitude.toFixed(4),
      data.speed_knots.toFixed(1),
      data.engine_power_kw.toFixed(0),
      data.fuel_consumption_kg_h.toFixed(1),
      data.water_temperature_c.toFixed(1),
      data.wind_speed_knots.toFixed(1),
      data.wave_height_m.toFixed(2),
    ])

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n')

    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `dados_operacionais_${selectedVessel}_${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <VStack spacing={6} align="stretch">
      <HStack justify="space-between">
        <Box>
          <Heading size="xl" mb={2}>Dados Operacionais</Heading>
          <Text color="gray.600">Monitoramento em tempo real e histórico de dados operacionais das embarcações</Text>
        </Box>
        <Button leftIcon={<AddIcon />} colorScheme="blue" onClick={onOpen}>
          Registrar Dados
        </Button>
      </HStack>

      {/* Filtro de Embarcação */}
      <Card>
        <CardBody>
          <HStack spacing={4}>
            <FormControl flex={1}>
              <FormLabel>Selecionar Embarcação</FormLabel>
              <Select
                value={selectedVessel}
                onChange={(e) => setSelectedVessel(e.target.value)}
                placeholder="Selecione uma embarcação..."
                size="md"
              >
                {vessels?.map((vessel: any) => (
                  <option key={vessel.id} value={vessel.id}>
                    {vessel.name} {vessel.imo_number ? `(${vessel.imo_number})` : ''}
                  </option>
                ))}
              </Select>
            </FormControl>
            {selectedVessel && operationalData && operationalData.length > 0 && (
              <Button
                leftIcon={<DownloadIcon />}
                colorScheme="green"
                variant="outline"
                onClick={exportToCSV}
                mt={8}
              >
                Exportar CSV
              </Button>
            )}
          </HStack>
        </CardBody>
      </Card>

      {!selectedVessel ? (
        <Alert status="info" borderRadius="md">
          <AlertIcon />
          Selecione uma embarcação para visualizar os dados operacionais.
        </Alert>
      ) : isLoading ? (
        <Center py={20}>
          <Spinner size="xl" />
        </Center>
      ) : operationalData && operationalData.length > 0 ? (
        <>
          {/* Últimos Dados em Tempo Real */}
          {latestData && (
            <Card borderColor="blue.300" borderWidth={2}>
              <CardBody>
                <Heading size="md" mb={4} color="blue.600">
                  Dados Atuais (Tempo Real)
                </Heading>
                <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
                  <Stat>
                    <StatLabel>Velocidade</StatLabel>
                    <StatNumber>{latestData.speed_knots.toFixed(1)} nós</StatNumber>
                    <StatHelpText>
                      {new Date(latestData.timestamp).toLocaleString('pt-BR')}
                    </StatHelpText>
                  </Stat>
                  <Stat>
                    <StatLabel>Potência do Motor</StatLabel>
                    <StatNumber>{(latestData.engine_power_kw / 1000).toFixed(1)} MW</StatNumber>
                    <StatHelpText>
                      {latestData.engine_power_kw.toFixed(0)} kW
                    </StatHelpText>
                  </Stat>
                  <Stat>
                    <StatLabel>Consumo de Combustível</StatLabel>
                    <StatNumber>{latestData.fuel_consumption_kg_h.toFixed(1)} kg/h</StatNumber>
                    <StatHelpText>
                      {(latestData.fuel_consumption_kg_h * 24).toFixed(0)} kg/dia
                    </StatHelpText>
                  </Stat>
                  <Stat>
                    <StatLabel>Localização</StatLabel>
                    <StatNumber fontSize="lg">
                      {latestData.latitude.toFixed(4)}, {latestData.longitude.toFixed(4)}
                    </StatNumber>
                    <StatHelpText>
                      Temp. Água: {latestData.water_temperature_c.toFixed(1)}°C
                    </StatHelpText>
                  </Stat>
                </SimpleGrid>
              </CardBody>
            </Card>
          )}

          {/* Estatísticas Gerais */}
          {stats && (
            <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
              <Card>
                <CardBody>
                  <Stat>
                    <StatLabel>Velocidade Média</StatLabel>
                    <StatNumber>{stats.avgSpeed.toFixed(1)} nós</StatNumber>
                    <StatHelpText>
                      {stats.minSpeed.toFixed(1)} - {stats.maxSpeed.toFixed(1)} nós
                    </StatHelpText>
                  </Stat>
                </CardBody>
              </Card>
              <Card>
                <CardBody>
                  <Stat>
                    <StatLabel>Potência Média</StatLabel>
                    <StatNumber>{(stats.avgPower / 1000).toFixed(1)} MW</StatNumber>
                    <StatHelpText>
                      {stats.avgPower.toFixed(0)} kW
                    </StatHelpText>
                  </Stat>
                </CardBody>
              </Card>
              <Card>
                <CardBody>
                  <Stat>
                    <StatLabel>Consumo Médio</StatLabel>
                    <StatNumber>{stats.avgFuel.toFixed(1)} kg/h</StatNumber>
                    <StatHelpText>
                      {(stats.avgFuel * 24).toFixed(0)} kg/dia
                    </StatHelpText>
                  </Stat>
                </CardBody>
              </Card>
              <Card>
                <CardBody>
                  <Stat>
                    <StatLabel>Total de Registros</StatLabel>
                    <StatNumber>{stats.dataPoints}</StatNumber>
                    <StatHelpText>
                      Últimos 30 dias
                    </StatHelpText>
                  </Stat>
                </CardBody>
              </Card>
            </SimpleGrid>
          )}

          {/* Tabs para diferentes visualizações */}
          <Tabs index={selectedTab} onChange={setSelectedTab} colorScheme="blue">
            <TabList>
              <Tab>Gráficos</Tab>
              <Tab>Tabela</Tab>
              <Tab>Análise</Tab>
            </TabList>

            <TabPanels>
              {/* Tab: Gráficos */}
              <TabPanel>
                <VStack spacing={6} align="stretch">
                  <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={4}>
                    {/* Gráfico de Velocidade */}
                    <Card>
                      <CardBody>
                        <Heading size="sm" mb={4}>Velocidade ao Longo do Tempo</Heading>
                        <ResponsiveContainer width="100%" height={250}>
                          <AreaChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="time" angle={-45} textAnchor="end" height={80} fontSize={10} />
                            <YAxis label={{ value: 'Velocidade (nós)', angle: -90, position: 'insideLeft' }} />
                            <RechartsTooltip />
                            <Area type="monotone" dataKey="speed" stroke="#3182CE" fill="#3182CE" fillOpacity={0.3} />
                          </AreaChart>
                        </ResponsiveContainer>
                      </CardBody>
                    </Card>

                    {/* Gráfico de Consumo de Combustível */}
                    <Card>
                      <CardBody>
                        <Heading size="sm" mb={4}>Consumo de Combustível</Heading>
                        <ResponsiveContainer width="100%" height={250}>
                          <LineChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="time" angle={-45} textAnchor="end" height={80} fontSize={10} />
                            <YAxis label={{ value: 'Consumo (kg/h)', angle: -90, position: 'insideLeft' }} />
                            <RechartsTooltip />
                            <Legend />
                            <Line type="monotone" dataKey="fuel" stroke="#E53E3E" strokeWidth={2} name="Combustível" />
                          </LineChart>
                        </ResponsiveContainer>
                      </CardBody>
                    </Card>

                    {/* Gráfico de Potência */}
                    <Card>
                      <CardBody>
                        <Heading size="sm" mb={4}>Potência do Motor</Heading>
                        <ResponsiveContainer width="100%" height={250}>
                          <BarChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="time" angle={-45} textAnchor="end" height={80} fontSize={10} />
                            <YAxis label={{ value: 'Potência (kW)', angle: -90, position: 'insideLeft' }} />
                            <RechartsTooltip />
                            <Bar dataKey="power" fill="#38A169" />
                          </BarChart>
                        </ResponsiveContainer>
                      </CardBody>
                    </Card>

                    {/* Gráfico de Condições Ambientais */}
                    <Card>
                      <CardBody>
                        <Heading size="sm" mb={4}>Condições Ambientais</Heading>
                        <ResponsiveContainer width="100%" height={250}>
                          <ComposedChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="time" angle={-45} textAnchor="end" height={80} fontSize={10} />
                            <YAxis yAxisId="left" label={{ value: 'Temp. Água (°C)', angle: -90, position: 'insideLeft' }} />
                            <YAxis yAxisId="right" orientation="right" label={{ value: 'Vento (nós) / Ondas (m)', angle: 90, position: 'insideRight' }} />
                            <RechartsTooltip />
                            <Legend />
                            <Line yAxisId="left" type="monotone" dataKey="waterTemp" stroke="#00B5D8" name="Temp. Água (°C)" />
                            <Line yAxisId="right" type="monotone" dataKey="wind" stroke="#F6AD55" name="Vento (nós)" />
                            <Line yAxisId="right" type="monotone" dataKey="wave" stroke="#805AD5" name="Ondas (m)" />
                          </ComposedChart>
                        </ResponsiveContainer>
                      </CardBody>
                    </Card>
                  </Grid>

                  {/* Gráfico de Correlação Velocidade vs Consumo */}
                  <Card>
                    <CardBody>
                      <Heading size="sm" mb={4}>Correlação: Velocidade vs Consumo de Combustível</Heading>
                      <ResponsiveContainer width="100%" height={300}>
                        <ScatterChart data={correlationData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis 
                            type="number" 
                            dataKey="speed" 
                            name="Velocidade" 
                            unit=" nós"
                            label={{ value: 'Velocidade (nós)', position: 'insideBottom', offset: -5 }}
                          />
                          <YAxis 
                            type="number" 
                            dataKey="fuel" 
                            name="Consumo" 
                            unit=" kg/h"
                            label={{ value: 'Consumo (kg/h)', angle: -90, position: 'insideLeft' }}
                          />
                          <RechartsTooltip cursor={{ strokeDasharray: '3 3' }} />
                          <Scatter name="Dados" data={correlationData} fill="#3182CE" />
                        </ScatterChart>
                      </ResponsiveContainer>
                    </CardBody>
                  </Card>
                </VStack>
              </TabPanel>

              {/* Tab: Tabela */}
              <TabPanel>
                <Card>
                  <CardBody>
                    <Heading size="md" mb={4}>Histórico de Dados Operacionais</Heading>
                    <Box overflowX="auto">
                      <Table variant="simple" size="sm">
                        <Thead>
                          <Tr>
                            <Th>Data/Hora</Th>
                            <Th>Localização</Th>
                            <Th>Velocidade</Th>
                            <Th>Potência</Th>
                            <Th>Consumo</Th>
                            <Th>Temp. Água</Th>
                            <Th>Vento</Th>
                            <Th>Ondas</Th>
                          </Tr>
                        </Thead>
                        <Tbody>
                          {operationalData.slice(0, 50).map((data) => (
                            <Tr key={data.id} _hover={{ bg: 'gray.50' }}>
                              <Td>
                                {new Date(data.timestamp).toLocaleString('pt-BR', {
                                  day: '2-digit',
                                  month: '2-digit',
                                  year: 'numeric',
                                  hour: '2-digit',
                                  minute: '2-digit'
                                })}
                              </Td>
                              <Td>
                                <Text fontSize="xs">
                                  {data.latitude.toFixed(4)}, {data.longitude.toFixed(4)}
                                </Text>
                              </Td>
                              <Td>
                                <Badge colorScheme="blue">
                                  {data.speed_knots.toFixed(1)} nós
                                </Badge>
                              </Td>
                              <Td>
                                {(data.engine_power_kw / 1000).toFixed(1)} MW
                                <Text fontSize="xs" color="gray.500">
                                  {data.engine_power_kw.toFixed(0)} kW
                                </Text>
                              </Td>
                              <Td>
                                <Text fontWeight="bold" color="red.600">
                                  {data.fuel_consumption_kg_h.toFixed(1)} kg/h
                                </Text>
                              </Td>
                              <Td>
                                <Badge colorScheme="cyan">
                                  {data.water_temperature_c.toFixed(1)}°C
                                </Badge>
                              </Td>
                              <Td>{data.wind_speed_knots.toFixed(1)} nós</Td>
                              <Td>{data.wave_height_m.toFixed(2)} m</Td>
                            </Tr>
                          ))}
                        </Tbody>
                      </Table>
                    </Box>
                    {operationalData.length > 50 && (
                      <Text fontSize="sm" color="gray.500" mt={4} textAlign="center">
                        Mostrando 50 de {operationalData.length} registros
                      </Text>
                    )}
                  </CardBody>
                </Card>
              </TabPanel>

              {/* Tab: Análise */}
              <TabPanel>
                <VStack spacing={6} align="stretch">
                  {stats && (
                    <>
                      <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={4}>
                        <Card>
                          <CardBody>
                            <Heading size="sm" mb={4}>Eficiência Operacional</Heading>
                            <VStack spacing={4} align="stretch">
                              <Box>
                                <HStack justify="space-between" mb={2}>
                                  <Text fontSize="sm">Consumo por Velocidade</Text>
                                  <Text fontSize="sm" fontWeight="bold">
                                    {(stats.avgFuel / stats.avgSpeed).toFixed(2)} kg/h por nó
                                  </Text>
                                </HStack>
                                <Progress 
                                  value={(stats.avgSpeed / stats.maxSpeed) * 100} 
                                  colorScheme="blue"
                                  size="sm"
                                />
                              </Box>
                              <Divider />
                              <Box>
                                <HStack justify="space-between" mb={2}>
                                  <Text fontSize="sm">Eficiência Energética</Text>
                                  <Text fontSize="sm" fontWeight="bold">
                                    {(stats.avgSpeed / (stats.avgPower / 1000)).toFixed(2)} nós/MW
                                  </Text>
                                </HStack>
                                <Progress 
                                  value={((stats.avgSpeed / (stats.avgPower / 1000)) / 20) * 100} 
                                  colorScheme="green"
                                  size="sm"
                                />
                              </Box>
                            </VStack>
                          </CardBody>
                        </Card>

                        <Card>
                          <CardBody>
                            <Heading size="sm" mb={4}>Condições Ambientais Médias</Heading>
                            <VStack spacing={4} align="stretch">
                              <Stat>
                                <StatLabel>Temperatura da Água</StatLabel>
                                <StatNumber>{stats.avgWaterTemp.toFixed(1)}°C</StatNumber>
                                <StatHelpText>
                                  Variação: {Math.min(...operationalData!.map(d => d.water_temperature_c)).toFixed(1)}°C - 
                                  {Math.max(...operationalData!.map(d => d.water_temperature_c)).toFixed(1)}°C
                                </StatHelpText>
                              </Stat>
                              <Divider />
                              <Stat>
                                <StatLabel>Velocidade do Vento</StatLabel>
                                <StatNumber>{stats.avgWind.toFixed(1)} nós</StatNumber>
                                <StatHelpText>
                                  Média dos últimos {stats.dataPoints} registros
                                </StatHelpText>
                              </Stat>
                              <Divider />
                              <Stat>
                                <StatLabel>Altura das Ondas</StatLabel>
                                <StatNumber>{stats.avgWave.toFixed(2)} m</StatNumber>
                                <StatHelpText>
                                  Condições: {stats.avgWave < 2 ? 'Calmo' : stats.avgWave < 3 ? 'Moderado' : 'Agitado'}
                                </StatHelpText>
                              </Stat>
                            </VStack>
                          </CardBody>
                        </Card>
                      </Grid>

                      <Card>
                        <CardBody>
                          <Heading size="sm" mb={4}>Análise de Consumo</Heading>
                          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
                            <Box p={4} bg="blue.50" borderRadius="md">
                              <Text fontSize="sm" color="gray.600" mb={1}>Consumo Total Estimado</Text>
                              <Text fontSize="2xl" fontWeight="bold" color="blue.600">
                                {(stats.totalFuel * 24 / 1000).toFixed(1)} ton/dia
                              </Text>
                              <Text fontSize="xs" color="gray.500" mt={1}>
                                Baseado em {stats.dataPoints} pontos de dados
                              </Text>
                            </Box>
                            <Box p={4} bg="green.50" borderRadius="md">
                              <Text fontSize="sm" color="gray.600" mb={1}>Consumo Médio por Hora</Text>
                              <Text fontSize="2xl" fontWeight="bold" color="green.600">
                                {stats.avgFuel.toFixed(1)} kg/h
                              </Text>
                              <Text fontSize="xs" color="gray.500" mt={1}>
                                {(stats.avgFuel * 24).toFixed(0)} kg em 24h
                              </Text>
                            </Box>
                            <Box p={4} bg="orange.50" borderRadius="md">
                              <Text fontSize="sm" color="gray.600" mb={1}>Faixa de Consumo</Text>
                              <Text fontSize="2xl" fontWeight="bold" color="orange.600">
                                {Math.min(...operationalData!.map(d => d.fuel_consumption_kg_h)).toFixed(1)} - 
                                {Math.max(...operationalData!.map(d => d.fuel_consumption_kg_h)).toFixed(1)} kg/h
                              </Text>
                              <Text fontSize="xs" color="gray.500" mt={1}>
                                Mínimo - Máximo
                              </Text>
                            </Box>
                          </SimpleGrid>
                        </CardBody>
                      </Card>
                    </>
                  )}
                </VStack>
              </TabPanel>
            </TabPanels>
          </Tabs>
        </>
      ) : (
        <Alert status="info" borderRadius="md">
          <AlertIcon />
          Nenhum dado operacional encontrado para esta embarcação.
        </Alert>
      )}

      {/* Modal de Registro */}
      <Modal isOpen={isOpen} onClose={onClose} size="lg" scrollBehavior="inside">
        <ModalOverlay />
        <ModalContent>
          <form onSubmit={handleSubmit(onSubmit)}>
            <ModalHeader>Registrar Dados Operacionais</ModalHeader>
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
                  <FormControl isInvalid={!!errors.latitude}>
                    <FormLabel>Latitude *</FormLabel>
                    <Input type="number" step="0.0001" {...register('latitude', { required: true, valueAsNumber: true })} />
                  </FormControl>
                  <FormControl isInvalid={!!errors.longitude}>
                    <FormLabel>Longitude *</FormLabel>
                    <Input type="number" step="0.0001" {...register('longitude', { required: true, valueAsNumber: true })} />
                  </FormControl>
                  <FormControl isInvalid={!!errors.speed_knots}>
                    <FormLabel>Velocidade (nós) *</FormLabel>
                    <Input type="number" step="0.1" {...register('speed_knots', { required: true, valueAsNumber: true })} />
                  </FormControl>
                  <FormControl isInvalid={!!errors.engine_power_kw}>
                    <FormLabel>Potência do Motor (kW) *</FormLabel>
                    <Input type="number" step="0.1" {...register('engine_power_kw', { required: true, valueAsNumber: true })} />
                  </FormControl>
                  <FormControl isInvalid={!!errors.fuel_consumption_kg_h}>
                    <FormLabel>Consumo de Combustível (kg/h) *</FormLabel>
                    <Input type="number" step="0.1" {...register('fuel_consumption_kg_h', { required: true, valueAsNumber: true })} />
                  </FormControl>
                  <FormControl isInvalid={!!errors.water_temperature_c}>
                    <FormLabel>Temperatura da Água (°C) *</FormLabel>
                    <Input type="number" step="0.1" {...register('water_temperature_c', { required: true, valueAsNumber: true })} />
                  </FormControl>
                  <FormControl isInvalid={!!errors.wind_speed_knots}>
                    <FormLabel>Velocidade do Vento (nós) *</FormLabel>
                    <Input type="number" step="0.1" {...register('wind_speed_knots', { required: true, valueAsNumber: true })} />
                  </FormControl>
                  <FormControl isInvalid={!!errors.wave_height_m}>
                    <FormLabel>Altura das Ondas (m) *</FormLabel>
                    <Input type="number" step="0.1" {...register('wave_height_m', { required: true, valueAsNumber: true })} />
                  </FormControl>
                </Grid>
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

export default OperationalData
