import { useParams } from 'react-router-dom'
import { useState } from 'react'
import {
  Box,
  VStack,
  Heading,
  Text,
  Card,
  CardBody,
  Grid,
  Badge,
  HStack,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Button,
  Spinner,
  Center,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Divider,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  List,
  ListItem,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
  SimpleGrid,
} from '@chakra-ui/react'
import { ArrowBackIcon } from '@chakra-ui/icons'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  vesselService,
  foulingService,
  complianceService,
  operationalDataService,
  maintenanceService,
  type AdvancedFoulingPrediction
} from '../api/services'
import ExplanationModal from '../components/ExplanationModal'
import AdvancedPredictionCard from '../components/AdvancedPredictionCard'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import apiClient from '../api/client'

function VesselDetails() {
  const { id } = useParams()
  const [showExplanation, setShowExplanation] = useState(false)
  const [explanationType, setExplanationType] = useState<'fouling' | 'compliance' | null>(null)

  // Buscar dados da embarcação (tentar banco de dados primeiro)
  const { data: vessel, isLoading: vesselLoading } = useQuery({
    queryKey: ['vessel', id],
    queryFn: async () => {
      try {
        return await vesselService.getById(id!, true)
      } catch {
        return await vesselService.getById(id!, false)
      }
    },
    enabled: !!id,
  })

  // Buscar última predição de bioincrustação
  const { data: latestFouling } = useQuery({
    queryKey: ['latest-fouling', id],
    queryFn: async () => {
      try {
        return await foulingService.getLatest(id!)
      } catch {
        return null
      }
    },
    enabled: !!id,
  })

  // Buscar histórico de bioincrustação
  const { data: foulingHistory } = useQuery({
    queryKey: ['fouling-history', id],
    queryFn: async () => {
      try {
        return await foulingService.getHistory(id!, 90) // Últimos 90 dias
      } catch {
        return []
      }
    },
    enabled: !!id,
  })

  // Buscar dados operacionais recentes
  const { data: latestOperational } = useQuery({
    queryKey: ['latest-operational', id],
    queryFn: async () => {
      try {
        return await operationalDataService.getLatest(id!)
      } catch {
        return null
      }
    },
    enabled: !!id,
  })

  // Buscar histórico de manutenção
  const { data: maintenanceHistory } = useQuery({
    queryKey: ['maintenance-history', id],
    queryFn: async () => {
      try {
        return await maintenanceService.getHistory(id!)
      } catch {
        return []
      }
    },
    enabled: !!id,
  })

  // Buscar última manutenção
  const { data: latestMaintenance } = useQuery({
    queryKey: ['latest-maintenance', id],
    queryFn: async () => {
      try {
        return await maintenanceService.getLatest(id!)
      } catch {
        return null
      }
    },
    enabled: !!id,
  })

  // Buscar ações corretivas
  const { data: correctiveActions } = useQuery({
    queryKey: ['corrective-actions', id],
    queryFn: async () => {
      try {
        const thickness = latestFouling?.estimated_thickness_mm || 4.5
        const roughness = latestFouling?.estimated_roughness_um || 450
        return await complianceService.getCorrectiveActions(id!, thickness, roughness)
      } catch {
        return []
      }
    },
    enabled: !!id && !!latestFouling,
  })

  // Buscar métodos de limpeza recomendados
  const { data: cleaningMethods } = useQuery({
    queryKey: ['cleaning-methods', id],
    queryFn: async () => {
      try {
        const response = await apiClient.get('/api/cleaning-methods')
        return response.data
      } catch {
        return []
      }
    },
    enabled: !!id,
  })

  // Buscar explicação de bioincrustação
  const { data: foulingExplanation } = useQuery({
    queryKey: ['fouling-explanation', id],
    queryFn: async () => {
      const features = {
        vessel_id: id,
        time_since_cleaning_days: latestMaintenance ?
          Math.floor((Date.now() - new Date(latestMaintenance.end_date || latestMaintenance.start_date).getTime()) / (1000 * 60 * 60 * 24)) : 90,
        water_temperature_c: latestOperational?.water_temperature_c || 25.0,
        salinity_psu: latestOperational?.salinity_psu || 32.5,
        time_in_port_hours: 120,
        average_speed_knots: latestOperational?.speed_knots || vessel?.typical_speed_knots || 12.0,
        route_region: vessel?.operating_routes?.[0] || 'South_Atlantic',
        paint_type: vessel?.paint_type || 'Antifouling_Type_A',
        vessel_type: vessel?.vessel_type || 'tanker',
        hull_area_m2: vessel?.hull_area_m2 || 5000.0,
      }
      try {
        const response = await apiClient.post(`/api/vessels/${id}/fouling/predict/explain`, features)
        return response.data
      } catch {
        return null
      }
    },
    enabled: !!id && !!vessel,
  })

  // Buscar explicação de conformidade
  const { data: complianceExplanation } = useQuery({
    queryKey: ['compliance-explanation', id],
    queryFn: async () => {
      const thickness = latestFouling?.estimated_thickness_mm || 4.5
      const roughness = latestFouling?.estimated_roughness_um || 450
      try {
        const response = await apiClient.get(
          `/api/vessels/${id}/compliance/explain?fouling_thickness_mm=${thickness}&roughness_um=${roughness}&vessel_type=${vessel?.vessel_type || 'standard'}`
        )
        return response.data
      } catch {
        return null
      }
    },
    enabled: !!id && !!vessel,
  })

  // Buscar predição avançada (usa dados reais do banco automaticamente)
  const { data: advancedPrediction, isLoading: advancedLoading } = useQuery<AdvancedFoulingPrediction | null>({
    queryKey: ['advanced-prediction', id],
    queryFn: async () => {
      if (!vessel) return null
      try {
        // O endpoint do banco carrega dados reais automaticamente
        return await foulingService.predictAdvanced(id!, true)
      } catch (error) {
        console.warn('Erro ao buscar predição avançada:', error)
        return null
      }
    },
    enabled: !!id && !!vessel,
  })

  // Buscar status de conformidade
  const { data: compliance, isLoading: complianceLoading } = useQuery({
    queryKey: ['compliance', id],
    queryFn: async () => {
      const thickness = latestFouling?.estimated_thickness_mm || 4.5
      const roughness = latestFouling?.estimated_roughness_um || 450

      return await complianceService.checkCompliance(
        id!,
        thickness,
        roughness,
        vessel?.vessel_type || 'standard'
      )
    },
    enabled: !!id && !!vessel,
  })

  const handleShowExplanation = (type: 'fouling' | 'compliance') => {
    setExplanationType(type)
    setShowExplanation(true)
  }

  const getComplianceColor = (status?: string) => {
    switch (status) {
      case 'compliant': return 'green'
      case 'at_risk': return 'yellow'
      case 'non_compliant': return 'orange'
      case 'critical': return 'red'
      default: return 'gray'
    }
  }

  const getComplianceLabel = (status?: string) => {
    switch (status) {
      case 'compliant': return 'Conforme'
      case 'at_risk': return 'Em Risco'
      case 'non_compliant': return 'Não Conforme'
      case 'critical': return 'Crítico'
      default: return 'N/A'
    }
  }

  // Preparar dados para gráfico de histórico
  const chartData = foulingHistory?.slice(0, 30).reverse().map((item: any) => ({
    date: new Date(item.timestamp).toLocaleDateString('pt-BR', { month: 'short', day: 'numeric' }),
    thickness: item.estimated_thickness_mm || 0,
    roughness: (item.estimated_roughness_um || 0) / 100, // Converter para mm para visualização
  })) || []

  if (vesselLoading) {
    return (
      <Center py={20}>
        <Spinner size="xl" />
      </Center>
    )
  }

  if (!vessel) {
    return (
      <Alert status="error">
        <AlertIcon />
        Embarcação não encontrada.
      </Alert>
    )
  }

  return (
    <VStack spacing={6} align="stretch">
      <HStack>
        <Button as={Link} to="/" leftIcon={<ArrowBackIcon />} variant="ghost">
          Voltar
        </Button>
      </HStack>

      <Box>
        <HStack justify="space-between" align="start">
          <Box>
            <Heading size="xl" mb={2}>{vessel.name}</Heading>
            <Text color="gray.600" mb={1}>
              IMO: {vessel.imo_number || 'N/A'} | Call Sign: {vessel.call_sign || 'N/A'}
            </Text>
            <HStack spacing={4} mb={2}>
              <Badge colorScheme="blue">{vessel.vessel_class || vessel.vessel_type}</Badge>
              {vessel.fleet_category && (
                <Badge colorScheme="purple">{vessel.fleet_category}</Badge>
              )}
              <Badge colorScheme={vessel.status === 'active' ? 'green' : 'gray'}>
                {vessel.status === 'active' ? 'Ativo' : vessel.status}
              </Badge>
            </HStack>
            <Text fontSize="sm" color="gray.500">
              Porto Base: {vessel.home_port || 'N/A'} | Ano de Construção: {vessel.construction_year || 'N/A'} | País: {vessel.construction_country || 'N/A'}
            </Text>
          </Box>
        </HStack>
      </Box>

      <Tabs>
        <TabList>
          <Tab>Visão Geral</Tab>
          <Tab>Histórico</Tab>
          <Tab>Predição Avançada</Tab>
          <Tab>Conformidade NORMAM 401</Tab>
          <Tab>Manutenção</Tab>
          <Tab>Recomendações</Tab>
        </TabList>

        <TabPanels>
          {/* Aba: Visão Geral */}
          <TabPanel>
            <VStack spacing={6} align="stretch">
              {/* Estado Atual */}
              <Grid templateColumns={{ base: '1fr', md: 'repeat(4, 1fr)' }} gap={4}>
                <Card>
                  <CardBody>
                    <Stat>
                      <StatLabel>Bioincrustação</StatLabel>
                      <StatNumber fontSize="2xl">
                        {latestFouling?.estimated_thickness_mm?.toFixed(2) || '4.5'} mm
                      </StatNumber>
                      <StatLabel fontSize="sm">
                        Rugosidade: {latestFouling?.estimated_roughness_um?.toFixed(0) || '450'} μm
                      </StatLabel>
                      {latestFouling && (
                        <StatHelpText>
                          Confiança: {(latestFouling.confidence_score * 100).toFixed(0)}%
                        </StatHelpText>
                      )}
                      <Button
                        size="xs"
                        mt={2}
                        colorScheme="blue"
                        onClick={() => handleShowExplanation('fouling')}
                      >
                        Explicar
                      </Button>
                    </Stat>
                  </CardBody>
                </Card>

                <Card>
                  <CardBody>
                    <Stat>
                      <StatLabel>Impacto no Combustível</StatLabel>
                      <StatNumber fontSize="2xl">
                        +{latestFouling?.predicted_fuel_impact_percent?.toFixed(1) || advancedPrediction?.predicted_fuel_impact_percent?.toFixed(1) || '4.5'}%
                      </StatNumber>
                      <StatLabel fontSize="sm">Aumento estimado</StatLabel>
                    </Stat>
                  </CardBody>
                </Card>

                <Card>
                  <CardBody>
                    <Stat>
                      <StatLabel>Impacto em CO₂</StatLabel>
                      <StatNumber fontSize="2xl">
                        {latestFouling?.predicted_co2_impact_kg
                          ? (latestFouling.predicted_co2_impact_kg / 1000).toFixed(1) + ' t/h'
                          : advancedPrediction
                            ? (advancedPrediction.predicted_co2_impact_kg / 1000).toFixed(1) + ' t/h'
                            : '1.25 t/h'}
                      </StatNumber>
                      <StatLabel fontSize="sm">Emissões adicionais</StatLabel>
                    </Stat>
                  </CardBody>
                </Card>

                <Card>
                  <CardBody>
                    <Stat>
                      <StatLabel>Status</StatLabel>
                      <StatNumber fontSize="lg">
                        <Badge colorScheme={
                          latestFouling?.fouling_severity === 'severe' || latestFouling?.fouling_severity === 'critical' ? 'red' :
                            latestFouling?.fouling_severity === 'moderate' ? 'yellow' : 'green'
                        }>
                          {latestFouling?.fouling_severity === 'severe' ? 'Severa' :
                            latestFouling?.fouling_severity === 'moderate' ? 'Moderada' :
                              latestFouling?.fouling_severity === 'light' ? 'Leve' :
                                latestFouling?.fouling_severity === 'critical' ? 'Crítica' : 'Moderada'}
                        </Badge>
                      </StatNumber>
                      <StatLabel fontSize="sm">Bioincrustação</StatLabel>
                    </Stat>
                  </CardBody>
                </Card>
              </Grid>

              {/* Informações Completas da Embarcação */}
              <Card>
                <CardBody>
                  <Heading size="md" mb={4}>Informações da Embarcação</Heading>
                  <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
                    <Box>
                      <Text fontSize="sm" color="gray.600">Dimensões</Text>
                      <Text fontWeight="bold">{vessel.length_m || 'N/A'} m × {vessel.width_m || 'N/A'} m × {vessel.draft_m || 'N/A'} m</Text>
                    </Box>
                    <Box>
                      <Text fontSize="sm" color="gray.600">Área do Casco</Text>
                      <Text fontWeight="bold">{vessel.hull_area_m2?.toLocaleString('pt-BR') || 'N/A'} m²</Text>
                    </Box>
                    <Box>
                      <Text fontSize="sm" color="gray.600">Deslocamento</Text>
                      <Text fontWeight="bold">{vessel.displacement_tonnes?.toLocaleString('pt-BR') || 'N/A'} t</Text>
                    </Box>
                    <Box>
                      <Text fontSize="sm" color="gray.600">DWT</Text>
                      <Text fontWeight="bold">{vessel.dwt?.toLocaleString('pt-BR') || 'N/A'} t</Text>
                    </Box>
                    <Box>
                      <Text fontSize="sm" color="gray.600">Potência do Motor</Text>
                      <Text fontWeight="bold">{vessel.engine_power_kw?.toLocaleString('pt-BR') || 'N/A'} kW</Text>
                    </Box>
                    <Box>
                      <Text fontSize="sm" color="gray.600">Tipo de Motor</Text>
                      <Text fontWeight="bold">{vessel.engine_type || 'N/A'}</Text>
                    </Box>
                    <Box>
                      <Text fontSize="sm" color="gray.600">Velocidade Máxima</Text>
                      <Text fontWeight="bold">{vessel.max_speed_knots || 'N/A'} nós</Text>
                    </Box>
                    <Box>
                      <Text fontSize="sm" color="gray.600">Velocidade Típica</Text>
                      <Text fontWeight="bold">{vessel.typical_speed_knots || 'N/A'} nós</Text>
                    </Box>
                    <Box>
                      <Text fontSize="sm" color="gray.600">Consumo Típico</Text>
                      <Text fontWeight="bold">{vessel.typical_consumption_kg_h?.toLocaleString('pt-BR') || 'N/A'} kg/h</Text>
                    </Box>
                    <Box>
                      <Text fontSize="sm" color="gray.600">Tipo de Tinta</Text>
                      <Text fontWeight="bold">{vessel.paint_type || 'N/A'}</Text>
                    </Box>
                    <Box>
                      <Text fontSize="sm" color="gray.600">Material do Casco</Text>
                      <Text fontWeight="bold">{vessel.hull_material || 'N/A'}</Text>
                    </Box>
                    <Box>
                      <Text fontSize="sm" color="gray.600">Tipo de Combustível</Text>
                      <Text fontWeight="bold">{vessel.fuel_type || 'N/A'}</Text>
                    </Box>
                    {vessel.operating_routes && vessel.operating_routes.length > 0 && (
                      <Box>
                        <Text fontSize="sm" color="gray.600">Rotas Operacionais</Text>
                        <Text fontWeight="bold">{vessel.operating_routes.join(', ')}</Text>
                      </Box>
                    )}
                  </SimpleGrid>
                </CardBody>
              </Card>

              {/* Dados Operacionais Recentes */}
              {latestOperational && (
                <Card>
                  <CardBody>
                    <Heading size="md" mb={4}>Dados Operacionais Recentes</Heading>
                    <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
                      {latestOperational.latitude && latestOperational.longitude && (
                        <Box>
                          <Text fontSize="sm" color="gray.600">Posição</Text>
                          <Text fontWeight="bold">
                            {latestOperational.latitude.toFixed(4)}°, {latestOperational.longitude.toFixed(4)}°
                          </Text>
                        </Box>
                      )}
                      {latestOperational.speed_knots && (
                        <Box>
                          <Text fontSize="sm" color="gray.600">Velocidade</Text>
                          <Text fontWeight="bold">{latestOperational.speed_knots.toFixed(1)} nós</Text>
                        </Box>
                      )}
                      {latestOperational.water_temperature_c && (
                        <Box>
                          <Text fontSize="sm" color="gray.600">Temperatura da Água</Text>
                          <Text fontWeight="bold">{latestOperational.water_temperature_c.toFixed(1)} °C</Text>
                        </Box>
                      )}
                      {latestOperational.salinity_psu && (
                        <Box>
                          <Text fontSize="sm" color="gray.600">Salinidade</Text>
                          <Text fontWeight="bold">{latestOperational.salinity_psu.toFixed(1)} PSU</Text>
                        </Box>
                      )}
                      {latestOperational.fuel_consumption_kg_h && (
                        <Box>
                          <Text fontSize="sm" color="gray.600">Consumo de Combustível</Text>
                          <Text fontWeight="bold">{latestOperational.fuel_consumption_kg_h.toFixed(0)} kg/h</Text>
                        </Box>
                      )}
                    </SimpleGrid>
                  </CardBody>
                </Card>
              )}

              {/* Última Manutenção */}
              {latestMaintenance && (
                <Card>
                  <CardBody>
                    <Heading size="md" mb={4}>Última Manutenção</Heading>
                    <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                      <Box>
                        <Text fontSize="sm" color="gray.600">Tipo</Text>
                        <Text fontWeight="bold">{latestMaintenance.event_type}</Text>
                      </Box>
                      <Box>
                        <Text fontSize="sm" color="gray.600">Data</Text>
                        <Text fontWeight="bold">
                          {new Date(latestMaintenance.start_date).toLocaleDateString('pt-BR')}
                        </Text>
                      </Box>
                      {latestMaintenance.cleaning_method && (
                        <Box>
                          <Text fontSize="sm" color="gray.600">Método de Limpeza</Text>
                          <Text fontWeight="bold">{latestMaintenance.cleaning_method}</Text>
                        </Box>
                      )}
                      {latestMaintenance.fouling_before_mm && (
                        <Box>
                          <Text fontSize="sm" color="gray.600">Bioincrustação Antes</Text>
                          <Text fontWeight="bold">{latestMaintenance.fouling_before_mm.toFixed(2)} mm</Text>
                        </Box>
                      )}
                      {latestMaintenance.fouling_after_mm && (
                        <Box>
                          <Text fontSize="sm" color="gray.600">Bioincrustação Depois</Text>
                          <Text fontWeight="bold">{latestMaintenance.fouling_after_mm.toFixed(2)} mm</Text>
                        </Box>
                      )}
                      {latestMaintenance.cost_brl && (
                        <Box>
                          <Text fontSize="sm" color="gray.600">Custo</Text>
                          <Text fontWeight="bold">R$ {latestMaintenance.cost_brl.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</Text>
                        </Box>
                      )}
                    </SimpleGrid>
                  </CardBody>
                </Card>
              )}
            </VStack>
          </TabPanel>

          {/* Aba: Histórico */}
          <TabPanel>
            <VStack spacing={6} align="stretch">
              <Card>
                <CardBody>
                  <Heading size="md" mb={4}>Histórico de Bioincrustação (Últimos 30 dias)</Heading>
                  {chartData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis yAxisId="left" label={{ value: 'Espessura (mm)', angle: -90, position: 'insideLeft' }} />
                        <YAxis yAxisId="right" orientation="right" label={{ value: 'Rugosidade (mm)', angle: 90, position: 'insideRight' }} />
                        <Tooltip />
                        <Legend />
                        <Line yAxisId="left" type="monotone" dataKey="thickness" stroke="#0066CC" name="Espessura (mm)" strokeWidth={2} />
                        <Line yAxisId="right" type="monotone" dataKey="roughness" stroke="#00A859" name="Rugosidade (mm)" strokeWidth={2} />
                      </LineChart>
                    </ResponsiveContainer>
                  ) : (
                    <Alert status="info">
                      <AlertIcon />
                      Nenhum dado histórico disponível.
                    </Alert>
                  )}
                </CardBody>
              </Card>

              {foulingHistory && foulingHistory.length > 0 && (
                <Card>
                  <CardBody>
                    <Heading size="md" mb={4}>Registros Recentes</Heading>
                    <TableContainer>
                      <Table size="sm">
                        <Thead>
                          <Tr>
                            <Th>Data</Th>
                            <Th>Espessura (mm)</Th>
                            <Th>Rugosidade (μm)</Th>
                            <Th>Severidade</Th>
                            <Th>Confiança</Th>
                          </Tr>
                        </Thead>
                        <Tbody>
                          {foulingHistory.slice(0, 10).map((item: any) => (
                            <Tr key={item.id}>
                              <Td>{new Date(item.timestamp).toLocaleDateString('pt-BR')}</Td>
                              <Td>{item.estimated_thickness_mm?.toFixed(2) || 'N/A'}</Td>
                              <Td>{item.estimated_roughness_um?.toFixed(0) || 'N/A'}</Td>
                              <Td>
                                <Badge colorScheme={
                                  item.fouling_severity === 'severe' || item.fouling_severity === 'critical' ? 'red' :
                                    item.fouling_severity === 'moderate' ? 'yellow' : 'green'
                                }>
                                  {item.fouling_severity || 'N/A'}
                                </Badge>
                              </Td>
                              <Td>{(item.confidence_score * 100).toFixed(0)}%</Td>
                            </Tr>
                          ))}
                        </Tbody>
                      </Table>
                    </TableContainer>
                  </CardBody>
                </Card>
              )}
            </VStack>
          </TabPanel>

          {/* Aba: Predição Avançada */}
          <TabPanel>
            <VStack spacing={6} align="stretch">
              {advancedLoading ? (
                <Center py={8}>
                  <Spinner />
                </Center>
              ) : advancedPrediction ? (
                <AdvancedPredictionCard prediction={advancedPrediction} />
              ) : (
                <Alert status="info">
                  <AlertIcon />
                  <Box>
                    <AlertTitle>Predição Avançada</AlertTitle>
                    <AlertDescription>
                      Execute uma predição avançada para ver análise detalhada com ensemble de modelos de IA,
                      análise de espécies invasoras e recomendações de controle natural.
                    </AlertDescription>
                  </Box>
                </Alert>
              )}

              <Card>
                <CardBody>
                  <Text mb={4}>
                    A predição avançada utiliza ensemble de 4 algoritmos de IA e considera:
                  </Text>
                  <List spacing={2}>
                    <ListItem>• Análise de espécies invasoras (Coral Sol, etc.)</ListItem>
                    <ListItem>• Fatores ambientais (nutrientes, pH, turbidez)</ListItem>
                    <ListItem>• Sazonalidade e condições operacionais</ListItem>
                    <ListItem>• Recomendações de controle natural baseadas em pesquisas</ListItem>
                    <ListItem>• Feature importance e contribuições dos modelos</ListItem>
                  </List>
                </CardBody>
              </Card>
            </VStack>
          </TabPanel>

          {/* Aba: Conformidade NORMAM 401 */}
          <TabPanel>
            <VStack spacing={6} align="stretch">
              {complianceLoading ? (
                <Center py={8}>
                  <Spinner />
                </Center>
              ) : compliance ? (
                <>
                  <Card>
                    <CardBody>
                      <HStack justify="space-between" mb={4}>
                        <Heading size="md">Status de Conformidade</Heading>
                        <Badge
                          colorScheme={getComplianceColor(compliance.status)}
                          size="lg"
                          fontSize="md"
                          px={4}
                          py={2}
                        >
                          {getComplianceLabel(compliance.status)}
                        </Badge>
                      </HStack>

                      <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={4} mb={4}>
                        <Box>
                          <Text fontSize="sm" color="gray.600">Bioincrustação</Text>
                          <Text fontSize="xl" fontWeight="bold">
                            {compliance.fouling_thickness_mm?.toFixed(2) || 'N/A'} mm
                          </Text>
                          <Text fontSize="xs" color="gray.500">
                            Limite: {compliance.max_allowed_thickness_mm || 'N/A'} mm
                          </Text>
                        </Box>
                        <Box>
                          <Text fontSize="sm" color="gray.600">Rugosidade</Text>
                          <Text fontSize="xl" fontWeight="bold">
                            {compliance.roughness_um?.toFixed(0) || 'N/A'} μm
                          </Text>
                          <Text fontSize="xs" color="gray.500">
                            Limite: {compliance.max_allowed_roughness_um || 'N/A'} μm
                          </Text>
                        </Box>
                      </Grid>

                      <HStack>
                        <Text fontSize="sm" color="gray.600">Score de Conformidade:</Text>
                        <Badge colorScheme={compliance.compliance_rate >= 0.8 ? 'green' : compliance.compliance_rate >= 0.6 ? 'yellow' : 'orange'}>
                          {(compliance.compliance_rate * 100).toFixed(0)}%
                        </Badge>
                      </HStack>

                      <Button
                        size="sm"
                        mt={4}
                        colorScheme="blue"
                        onClick={() => handleShowExplanation('compliance')}
                      >
                        Explicar Status de Conformidade
                      </Button>

                      {compliance.violations && compliance.violations.length > 0 && (
                        <Box mt={4} p={4} bg="red.50" borderRadius="md" borderLeft="4px" borderColor="red.500">
                          <Text fontWeight="bold" mb={2} color="red.700">Violações:</Text>
                          {compliance.violations.map((violation: string, index: number) => (
                            <Text key={index} fontSize="sm" color="red.600">• {violation}</Text>
                          ))}
                        </Box>
                      )}

                      {compliance.warnings && compliance.warnings.length > 0 && (
                        <Box mt={4} p={4} bg="yellow.50" borderRadius="md" borderLeft="4px" borderColor="yellow.500">
                          <Text fontWeight="bold" mb={2} color="yellow.700">Avisos:</Text>
                          {compliance.warnings.map((warning: string, index: number) => (
                            <Text key={index} fontSize="sm" color="yellow.600">• {warning}</Text>
                          ))}
                        </Box>
                      )}

                      <Divider my={4} />

                      <Box>
                        <Text fontWeight="bold" mb={2}>Recomendações:</Text>
                        {compliance.recommendations && compliance.recommendations.length > 0 ? (
                          compliance.recommendations.map((rec: string, index: number) => (
                            <Text key={index} fontSize="sm" mb={2} color="gray.700">• {rec}</Text>
                          ))
                        ) : (
                          <Text fontSize="sm" color="gray.500">Nenhuma recomendação disponível.</Text>
                        )}
                      </Box>
                    </CardBody>
                  </Card>
                </>
              ) : (
                <Alert status="info">
                  <AlertIcon />
                  Dados de conformidade não disponíveis.
                </Alert>
              )}
            </VStack>
          </TabPanel>

          {/* Aba: Manutenção */}
          <TabPanel>
            <VStack spacing={6} align="stretch">
              {maintenanceHistory && maintenanceHistory.length > 0 ? (
                <Card>
                  <CardBody>
                    <Heading size="md" mb={4}>Histórico de Manutenção</Heading>
                    <TableContainer>
                      <Table size="sm">
                        <Thead>
                          <Tr>
                            <Th>Data</Th>
                            <Th>Tipo</Th>
                            <Th>Método</Th>
                            <Th>Antes (mm)</Th>
                            <Th>Depois (mm)</Th>
                            <Th>Custo (R$)</Th>
                          </Tr>
                        </Thead>
                        <Tbody>
                          {maintenanceHistory.map((event: any) => (
                            <Tr key={event.id}>
                              <Td>{new Date(event.start_date).toLocaleDateString('pt-BR')}</Td>
                              <Td>{event.event_type}</Td>
                              <Td>{event.cleaning_method || 'N/A'}</Td>
                              <Td>{event.fouling_before_mm?.toFixed(2) || 'N/A'}</Td>
                              <Td>{event.fouling_after_mm?.toFixed(2) || 'N/A'}</Td>
                              <Td>{event.cost_brl?.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) || 'N/A'}</Td>
                            </Tr>
                          ))}
                        </Tbody>
                      </Table>
                    </TableContainer>
                  </CardBody>
                </Card>
              ) : (
                <Alert status="info">
                  <AlertIcon />
                  Nenhum histórico de manutenção disponível.
                </Alert>
              )}

              {cleaningMethods && cleaningMethods.length > 0 && (
                <Card>
                  <CardBody>
                    <Heading size="md" mb={4}>Métodos de Limpeza Disponíveis</Heading>
                    <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                      {cleaningMethods.slice(0, 8).map((method: any) => (
                        <Box key={method.name} p={4} borderWidth="1px" borderRadius="md">
                          <HStack justify="space-between" mb={2}>
                            <Text fontWeight="bold">{method.name}</Text>
                            <Badge colorScheme={method.efficacy >= 0.8 ? 'green' : method.efficacy >= 0.6 ? 'yellow' : 'orange'}>
                              Eficácia: {(method.efficacy * 100).toFixed(0)}%
                            </Badge>
                          </HStack>
                          <Text fontSize="sm" color="gray.600" mb={2}>{method.description}</Text>
                          <HStack spacing={4} fontSize="xs">
                            <Text>Custo: R$ {method.cost_per_m2?.toFixed(2) || 'N/A'}/m²</Text>
                            <Text>Duração: {method.duration_hours || 'N/A'}h</Text>
                          </HStack>
                        </Box>
                      ))}
                    </SimpleGrid>
                  </CardBody>
                </Card>
              )}
            </VStack>
          </TabPanel>

          {/* Aba: Recomendações */}
          <TabPanel>
            <VStack spacing={6} align="stretch">
              {correctiveActions && correctiveActions.length > 0 ? (
                <Card>
                  <CardBody>
                    <Heading size="md" mb={4}>Ações Corretivas Recomendadas</Heading>
                    <VStack align="stretch" spacing={4}>
                      {correctiveActions.map((action: any) => (
                        <Box key={action.action_id} p={4} borderWidth="1px" borderRadius="md">
                          <HStack justify="space-between" mb={2}>
                            <Text fontWeight="bold">{action.title}</Text>
                            <Badge colorScheme={
                              action.priority === 'high' ? 'red' :
                                action.priority === 'medium' ? 'yellow' : 'blue'
                            }>
                              {action.priority === 'high' ? 'Alta' :
                                action.priority === 'medium' ? 'Média' : 'Baixa'}
                            </Badge>
                          </HStack>
                          <Text fontSize="sm" color="gray.600" mb={2}>{action.description}</Text>
                          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={2} fontSize="xs">
                            <Text>Custo: R$ {action.estimated_cost_brl?.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) || 'N/A'}</Text>
                            <Text>Duração: {action.estimated_duration_hours || 'N/A'}h</Text>
                            <Text>Prazo: {new Date(action.deadline).toLocaleDateString('pt-BR')}</Text>
                          </SimpleGrid>
                          {action.steps && action.steps.length > 0 && (
                            <Box mt={2}>
                              <Text fontSize="xs" fontWeight="bold" mb={1}>Passos:</Text>
                              {action.steps.map((step: string, index: number) => (
                                <Text key={index} fontSize="xs" color="gray.600">• {step}</Text>
                              ))}
                            </Box>
                          )}
                        </Box>
                      ))}
                    </VStack>
                  </CardBody>
                </Card>
              ) : (
                <Alert status="info">
                  <AlertIcon />
                  Nenhuma ação corretiva recomendada no momento.
                </Alert>
              )}
            </VStack>
          </TabPanel>
        </TabPanels>
      </Tabs>

      {/* Modal de Explicação */}
      <ExplanationModal
        isOpen={showExplanation}
        onClose={() => {
          setShowExplanation(false)
          setExplanationType(null)
        }}
        explanation={
          explanationType === 'fouling'
            ? foulingExplanation
            : explanationType === 'compliance'
              ? complianceExplanation
              : null
        }
        title={
          explanationType === 'fouling'
            ? 'Explicação da Predição de Bioincrustação'
            : explanationType === 'compliance'
              ? 'Explicação do Status de Conformidade'
              : 'Explicação'
        }
      />
    </VStack>
  )
}

export default VesselDetails
