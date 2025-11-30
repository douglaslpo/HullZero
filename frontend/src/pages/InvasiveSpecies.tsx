import { useState } from 'react'
import {
  Box,
  VStack,
  Heading,
  Text,
  Card,
  CardBody,
  Select,
  FormControl,
  FormLabel,
  Input,
  Button,
  Grid,
  Badge,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  List,
  ListItem,
  ListIcon,
  HStack,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Divider,
  SimpleGrid,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Icon,
  Spinner,
  Center,
  Progress,
  Tag,
  useToast,
  Tooltip,
} from '@chakra-ui/react'
import { WarningIcon, CheckCircleIcon, InfoIcon } from '@chakra-ui/icons'
import { useQuery } from '@tanstack/react-query'
import { vesselService, invasiveSpeciesService, type InvasiveSpeciesRisk } from '../api/services'
import {
  BarChart, Bar, LineChart, Line, Cell,
  XAxis, YAxis, CartesianGrid, ResponsiveContainer, Legend, Tooltip as RechartsTooltip,
} from 'recharts'

const COLORS = ['#E53E3E', '#F56565', '#ED8936', '#ECC94B', '#48BB78']

// Componente de Mapa de Risco do Casco
const HullRiskMap = ({ risks }: { risks: InvasiveSpeciesRisk[] }) => {
  const getRiskForArea = (area: string) => {
    const areaRisks = risks.filter(r => {
      if (area === 'propeller' && r.species.includes('barnacle')) return true
      if (area === 'niche' && r.removal_difficulty > 0.7) return true
      if (area === 'flat' && r.growth_rate_multiplier > 1.5) return true
      return false
    })

    if (areaRisks.some(r => r.risk_level === 'critical')) return 'red.500'
    if (areaRisks.some(r => r.risk_level === 'high')) return 'orange.500'
    if (areaRisks.some(r => r.risk_level === 'medium')) return 'yellow.500'
    return 'green.500'
  }

  return (
    <Box position="relative" h="300px" bg="blue.50" borderRadius="md" p={4} overflow="hidden">
      <Heading size="sm" mb={4} textAlign="center">Mapa de Calor: Risco de Bioincrustação</Heading>

      <Center h="100%">
        <Box position="relative" w="80%" h="150px">
          {/* Proa */}
          <Box
            position="absolute" left="0" top="0" bottom="0" w="20%"
            bg={getRiskForArea('niche')}
            borderTopLeftRadius="100%" borderBottomLeftRadius="100%"
            opacity="0.8"
            _hover={{ opacity: 1, transform: 'scale(1.05)' }}
            transition="all 0.2s"
          >
            <Tooltip label="Proa / Bulbous Bow (Área de Nicho)">
              <Center h="100%"><Text fontSize="xs" fontWeight="bold" color="white">Proa</Text></Center>
            </Tooltip>
          </Box>

          {/* Meio do Navio (Fundo Plano) */}
          <Box
            position="absolute" left="20%" top="0" bottom="0" w="60%"
            bg={getRiskForArea('flat')}
            opacity="0.8"
            _hover={{ opacity: 1 }}
            transition="all 0.2s"
          >
            <Tooltip label="Fundo Plano (Flat Bottom)">
              <Center h="100%"><Text fontSize="xs" fontWeight="bold" color="white">Fundo Plano</Text></Center>
            </Tooltip>
          </Box>

          {/* Popa / Hélice */}
          <Box
            position="absolute" right="0" top="0" bottom="0" w="20%"
            bg={getRiskForArea('propeller')}
            borderTopRightRadius="20%" borderBottomRightRadius="20%"
            opacity="0.8"
            _hover={{ opacity: 1, transform: 'scale(1.05)' }}
            transition="all 0.2s"
          >
            <Tooltip label="Popa / Hélice / Leme (Área Crítica)">
              <Center h="100%"><Text fontSize="xs" fontWeight="bold" color="white">Popa</Text></Center>
            </Tooltip>
          </Box>

          {/* Sea Chests */}
          <Box
            position="absolute" left="30%" top="20%" w="10%" h="20%"
            bg="red.600" borderRadius="sm" zIndex="2"
            boxShadow="0 0 10px rgba(0,0,0,0.3)"
          >
            <Tooltip label="Sea Chest (Alto Risco)">
              <Box w="100%" h="100%" />
            </Tooltip>
          </Box>
          <Box
            position="absolute" left="60%" bottom="20%" w="10%" h="20%"
            bg="red.600" borderRadius="sm" zIndex="2"
            boxShadow="0 0 10px rgba(0,0,0,0.3)"
          >
            <Tooltip label="Sea Chest (Alto Risco)">
              <Box w="100%" h="100%" />
            </Tooltip>
          </Box>
        </Box>
      </Center>

      <HStack justify="center" mt={4} spacing={4}>
        <HStack><Box w="12px" h="12px" bg="green.500" borderRadius="full" /><Text fontSize="xs">Baixo Risco</Text></HStack>
        <HStack><Box w="12px" h="12px" bg="yellow.500" borderRadius="full" /><Text fontSize="xs">Médio Risco</Text></HStack>
        <HStack><Box w="12px" h="12px" bg="orange.500" borderRadius="full" /><Text fontSize="xs">Alto Risco</Text></HStack>
        <HStack><Box w="12px" h="12px" bg="red.500" borderRadius="full" /><Text fontSize="xs">Crítico</Text></HStack>
      </HStack>
    </Box>
  )
}

function InvasiveSpecies() {
  const toast = useToast()
  const [selectedVessel, setSelectedVessel] = useState<string>('')
  const [selectedSpecies, setSelectedSpecies] = useState<string>('')
  const [activeTab, setActiveTab] = useState(0)
  const [assessmentData, setAssessmentData] = useState({
    route_region: 'South_Atlantic',
    water_temperature_c: 25.0,
    salinity_psu: 32.5,
    depth_m: 20.0,
    seasonal_factor: 'summer',
  })

  // Buscar embarcações
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

  // Buscar embarcação selecionada
  const { data: vessel } = useQuery({
    queryKey: ['vessel', selectedVessel],
    queryFn: async () => {
      if (!selectedVessel) return null
      try {
        return await vesselService.getById(selectedVessel, true)
      } catch {
        return await vesselService.getById(selectedVessel, false)
      }
    },
    enabled: !!selectedVessel,
  })

  // Avaliar risco de espécies invasoras
  const { data: risks, isLoading, error } = useQuery<InvasiveSpeciesRisk[]>({
    queryKey: ['invasive-species-risk', selectedVessel, assessmentData],
    queryFn: async () => {
      if (!selectedVessel) return []
      return await invasiveSpeciesService.assessRisk(selectedVessel, assessmentData)
    },
    enabled: !!selectedVessel,
  })

  // Buscar informações detalhadas da espécie selecionada
  const { data: speciesInfo } = useQuery({
    queryKey: ['invasive-species-info', selectedSpecies],
    queryFn: async () => {
      if (!selectedSpecies) return null
      return await invasiveSpeciesService.getInfo(selectedSpecies)
    },
    enabled: !!selectedSpecies,
  })



  const getRiskColor = (level: string) => {
    switch (level) {
      case 'critical': return 'red'
      case 'high': return 'orange'
      case 'medium': return 'yellow'
      case 'low': return 'green'
      default: return 'gray'
    }
  }

  const getRiskLabel = (level: string) => {
    switch (level) {
      case 'critical': return 'Crítico'
      case 'high': return 'Alto'
      case 'medium': return 'Médio'
      case 'low': return 'Baixo'
      default: return level
    }
  }

  const formatSpeciesName = (name: string) => {
    return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
  }

  // Preparar dados para gráficos
  const riskChartData = risks?.map((risk) => ({
    name: formatSpeciesName(risk.species),
    risk: Math.round(risk.risk_score * 100),
    growth: risk.growth_rate_multiplier,
    difficulty: Math.round(risk.removal_difficulty * 100),
  })) || []

  const handleGenerateBFMP = () => {
    toast({
      title: 'Plano de Gestão Gerado',
      description: `O Biofouling Management Plan (BFMP) para ${vessel?.name || 'a embarcação'} foi gerado e enviado para aprovação.`,
      status: 'success',
      duration: 5000,
      isClosable: true,
    })
  }

  // Calcular Impacto Econômico
  const economicImpact = risks ? {
    fuelPenaltyPercent: risks.reduce((acc, r) => acc + (r.risk_score * 2), 0),
    cleaningCost: risks.reduce((acc, r) => acc + (r.removal_difficulty * 50000), 0),
    daysLost: Math.ceil(risks.reduce((acc, r) => acc + (r.risk_level === 'critical' ? 2 : 0), 0))
  } : null

  const seasonalData = risks?.flatMap((risk) =>
    Object.entries(risk.seasonal_factors).map(([season, factor]) => ({
      species: formatSpeciesName(risk.species),
      season: season === 'summer' ? 'Verão' : season === 'spring' ? 'Primavera' : season === 'autumn' ? 'Outono' : 'Inverno',
      factor: factor,
    }))
  ) || []

  return (
    <VStack spacing={6} align="stretch">
      <Box>
        <Heading size="xl" mb={2}>Análise de Espécies Invasoras</Heading>
        <Text color="gray.600">
          Avaliação de risco e métodos inovadores de controle biológico para espécies invasoras marinhas
        </Text>
      </Box>

      {/* Seleção de Embarcação */}
      <Card>
        <CardBody>
          <FormControl mb={4}>
            <FormLabel>Selecionar Embarcação</FormLabel>
            <Select
              value={selectedVessel}
              onChange={(e) => setSelectedVessel(e.target.value)}
              placeholder="Selecione uma embarcação..."
            >
              {vessels?.map((v: any) => (
                <option key={v.id} value={v.id}>
                  {v.name} {v.imo_number && `(${v.imo_number})`}
                </option>
              ))}
            </Select>
          </FormControl>

          {vessel && (
            <Alert status="info" mb={4}>
              <AlertIcon />
              <Box>
                <AlertTitle>Embarcação Selecionada</AlertTitle>
                <AlertDescription>
                  {vessel.name} - {vessel.vessel_class || vessel.vessel_type} -
                  Rotas: {vessel.operating_routes?.join(', ') || 'N/A'}
                </AlertDescription>
              </Box>
            </Alert>
          )}
        </CardBody>
      </Card>

      {/* Parâmetros de Avaliação */}
      {selectedVessel && (
        <Card>
          <CardBody>
            <Heading size="md" mb={4}>Parâmetros de Avaliação</Heading>
            <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' }} gap={4}>
              <FormControl>
                <FormLabel>Região de Operação</FormLabel>
                <Select
                  value={assessmentData.route_region}
                  onChange={(e) =>
                    setAssessmentData({ ...assessmentData, route_region: e.target.value })
                  }
                >
                  <option value="South_Atlantic">Atlântico Sul</option>
                  <option value="Brazil_Coast">Costa Brasileira</option>
                  <option value="Offshore">Offshore</option>
                  <option value="Tropical">Tropical</option>
                  <option value="Inland_Waterways">Vias Interiores</option>
                  <option value="Estuaries">Estuários</option>
                </Select>
              </FormControl>

              <FormControl>
                <FormLabel>Temperatura da Água (°C)</FormLabel>
                <Input
                  type="number"
                  value={assessmentData.water_temperature_c}
                  onChange={(e) =>
                    setAssessmentData({
                      ...assessmentData,
                      water_temperature_c: parseFloat(e.target.value),
                    })
                  }
                />
              </FormControl>

              <FormControl>
                <FormLabel>Salinidade (PSU)</FormLabel>
                <Input
                  type="number"
                  value={assessmentData.salinity_psu}
                  onChange={(e) =>
                    setAssessmentData({
                      ...assessmentData,
                      salinity_psu: parseFloat(e.target.value),
                    })
                  }
                />
              </FormControl>

              <FormControl>
                <FormLabel>Profundidade (m)</FormLabel>
                <Input
                  type="number"
                  value={assessmentData.depth_m}
                  onChange={(e) =>
                    setAssessmentData({
                      ...assessmentData,
                      depth_m: parseFloat(e.target.value),
                    })
                  }
                />
              </FormControl>

              <FormControl>
                <FormLabel>Fator Sazonal</FormLabel>
                <Select
                  value={assessmentData.seasonal_factor}
                  onChange={(e) =>
                    setAssessmentData({ ...assessmentData, seasonal_factor: e.target.value })
                  }
                >
                  <option value="summer">Verão</option>
                  <option value="spring">Primavera</option>
                  <option value="autumn">Outono</option>
                  <option value="winter">Inverno</option>
                </Select>
              </FormControl>
            </Grid>
          </CardBody>
        </Card>
      )}

      {/* Resultados da Avaliação */}
      {isLoading && (
        <Card>
          <CardBody>
            <Center py={8}>
              <Spinner size="xl" />
            </Center>
          </CardBody>
        </Card>
      )}

      {error && (
        <Alert status="error">
          <AlertIcon />
          Erro ao avaliar risco de espécies invasoras
        </Alert>
      )}

      {risks && risks.length > 0 && (
        <Tabs colorScheme="blue" isLazy index={activeTab} onChange={setActiveTab}>
          <TabList>
            <Tab>Visão Geral</Tab>
            <Tab>Análise Detalhada</Tab>
            <Tab>Métodos de Controle</Tab>
            <Tab>Dados Científicos</Tab>
          </TabList>

          <TabPanels>
            {/* Tab: Visão Geral */}
            <TabPanel>
              <VStack spacing={6} align="stretch">

                {/* Novos Cards: Conformidade e Impacto Econômico */}
                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                  {/* Conformidade IMO & BFMP */}
                  <Card borderLeft="4px" borderLeftColor={risks.some(r => r.risk_level === 'critical') ? 'red.500' : 'green.500'}>
                    <CardBody>
                      <HStack justify="space-between" mb={4}>
                        <Heading size="md">Conformidade IMO & BFMP</Heading>
                        <Icon as={CheckCircleIcon} color={risks.some(r => r.risk_level === 'critical') ? 'red.500' : 'green.500'} boxSize={6} />
                      </HStack>

                      <VStack align="stretch" spacing={3}>
                        <HStack justify="space-between">
                          <Text color="gray.600">Status IMO MEPC.207(62):</Text>
                          <Badge colorScheme={risks.some(r => r.risk_level === 'critical') ? 'red' : 'green'} fontSize="sm">
                            {risks.some(r => r.risk_level === 'critical') ? 'NÃO CONFORME' : 'CONFORME'}
                          </Badge>
                        </HStack>

                        <HStack justify="space-between">
                          <Text color="gray.600">Biofouling Management Plan:</Text>
                          <Text fontWeight="bold">{risks.length > 0 ? 'Requer Atualização' : 'Atualizado'}</Text>
                        </HStack>

                        <Button
                          colorScheme="blue"
                          size="sm"
                          leftIcon={<Icon as={CheckCircleIcon} />}
                          onClick={handleGenerateBFMP}
                          mt={2}
                        >
                          Gerar/Atualizar BFMP
                        </Button>
                      </VStack>
                    </CardBody>
                  </Card>

                  {/* Impacto Econômico Estimado */}
                  <Card>
                    <CardBody>
                      <Heading size="md" mb={4}>Impacto Econômico Estimado</Heading>
                      <SimpleGrid columns={2} spacing={4}>
                        <Box>
                          <Text fontSize="sm" color="gray.600">Penalidade de Combustível</Text>
                          <Text fontSize="2xl" fontWeight="bold" color="red.500">
                            +{economicImpact?.fuelPenaltyPercent.toFixed(1)}%
                          </Text>
                        </Box>
                        <Box>
                          <Text fontSize="sm" color="gray.600">Custo Est. Limpeza</Text>
                          <Text fontSize="2xl" fontWeight="bold" color="orange.500">
                            {economicImpact?.cleaningCost.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
                          </Text>
                        </Box>
                        <Box>
                          <Text fontSize="sm" color="gray.600">Dias Parados (Est.)</Text>
                          <Text fontSize="xl" fontWeight="bold">
                            {economicImpact?.daysLost} dias
                          </Text>
                        </Box>
                        <Box>
                          <Text fontSize="xs" color="gray.500" mt={2}>
                            *Estimativas baseadas no nível de risco atual e dificuldade de remoção.
                          </Text>
                        </Box>
                      </SimpleGrid>
                    </CardBody>
                  </Card>
                </SimpleGrid>

                {/* Estatísticas Gerais */}
                <SimpleGrid columns={{ base: 1, md: 4 }} spacing={4}>
                  <Card>
                    <CardBody>
                      <Stat>
                        <StatLabel>Espécies em Risco</StatLabel>
                        <StatNumber color="red.500">{risks.length}</StatNumber>
                        <StatHelpText>Identificadas nas condições atuais</StatHelpText>
                      </Stat>
                    </CardBody>
                  </Card>
                  <Card>
                    <CardBody>
                      <Stat>
                        <StatLabel>Risco Médio</StatLabel>
                        <StatNumber color="orange.500">
                          {Math.round((risks.reduce((sum, r) => sum + r.risk_score, 0) / risks.length) * 100)}%
                        </StatNumber>
                        <StatHelpText>Score médio de risco</StatHelpText>
                      </Stat>
                    </CardBody>
                  </Card>
                  <Card>
                    <CardBody>
                      <Stat>
                        <StatLabel>Espécies Críticas</StatLabel>
                        <StatNumber color="red.600">
                          {risks.filter((r) => r.risk_level === 'critical' || r.risk_level === 'high').length}
                        </StatNumber>
                        <StatHelpText>Requerem atenção imediata</StatHelpText>
                      </Stat>
                    </CardBody>
                  </Card>
                  <Card>
                    <CardBody>
                      <Stat>
                        <StatLabel>Dificuldade Média</StatLabel>
                        <StatNumber color="yellow.500">
                          {Math.round((risks.reduce((sum, r) => sum + r.removal_difficulty, 0) / risks.length) * 100)}%
                        </StatNumber>
                        <StatHelpText>Dificuldade de remoção</StatHelpText>
                      </Stat>
                    </CardBody>
                  </Card>
                </SimpleGrid>

                {/* Gráfico de Riscos */}
                <Card>
                  <CardBody>
                    <Heading size="md" mb={4}>Nível de Risco por Espécie</Heading>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={riskChartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis
                          dataKey="name"
                          angle={-45}
                          textAnchor="end"
                          height={100}
                          fontSize={12}
                        />
                        <YAxis
                          label={{ value: 'Risco (%)', angle: -90, position: 'insideLeft' }}
                        />
                        <RechartsTooltip
                          formatter={(value: number) => [`${value}%`, 'Risco']}
                        />
                        <Legend />
                        <Bar
                          dataKey="risk"
                          name="Risco (%)"
                          radius={[8, 8, 0, 0]}
                        >
                          {riskChartData.map((_entry, index) => {
                            const risk = risks[index]
                            return (
                              <Cell
                                key={`cell-${index}`}
                                fill={
                                  risk?.risk_level === 'critical' ? '#C53030' :
                                    risk?.risk_level === 'high' ? '#F56565' :
                                      risk?.risk_level === 'medium' ? '#ED8936' :
                                        '#ECC94B'
                                }
                              />
                            )
                          })}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </CardBody>
                </Card>

                {/* Distribuição de Risco */}
                <Card>
                  <CardBody>
                    <Heading size="md" mb={4}>Distribuição de Níveis de Risco</Heading>
                    <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
                      {['critical', 'high', 'medium', 'low'].map((level) => {
                        const count = risks.filter((r) => r.risk_level === level).length
                        const percentage = risks.length > 0 ? Math.round((count / risks.length) * 100) : 0
                        return (
                          <Box
                            key={level}
                            p={4}
                            bg={`${getRiskColor(level)}.50`}
                            borderRadius="md"
                            borderWidth="2px"
                            borderColor={`${getRiskColor(level)}.300`}
                            textAlign="center"
                          >
                            <Text fontSize="sm" fontWeight="bold" color={`${getRiskColor(level)}.700`} mb={1}>
                              {getRiskLabel(level)}
                            </Text>
                            <Text fontSize="3xl" fontWeight="bold" color={`${getRiskColor(level)}.600`}>
                              {count}
                            </Text>
                            <Text fontSize="xs" color="gray.600">
                              {percentage}% do total
                            </Text>
                          </Box>
                        )
                      })}
                    </SimpleGrid>
                  </CardBody>
                </Card>

                {/* Lista de Riscos */}
                <Card>
                  <CardBody>
                    <Heading size="md" mb={4}>Riscos Identificados</Heading>
                    <VStack spacing={4} align="stretch">
                      {risks
                        .sort((a, b) => b.risk_score - a.risk_score) // Ordenar por risco (maior primeiro)
                        .map((risk, index) => (
                          <Card key={index} borderWidth="2px" borderColor={`${getRiskColor(risk.risk_level)}.300`}>
                            <CardBody>
                              <HStack justify="space-between" mb={4}>
                                <VStack align="start" spacing={1}>
                                  <Heading size="md">{formatSpeciesName(risk.species)}</Heading>
                                  <HStack spacing={2}>
                                    <Badge colorScheme={getRiskColor(risk.risk_level)} fontSize="md" px={3} py={1}>
                                      {getRiskLabel(risk.risk_level)}
                                    </Badge>
                                    <Text fontSize="sm" color="gray.600">
                                      Score: {Math.round(risk.risk_score * 100)}%
                                    </Text>
                                  </HStack>
                                </VStack>
                                <Button
                                  size="md"
                                  colorScheme="blue"
                                  onClick={() => {
                                    setSelectedSpecies(risk.species)
                                    setActiveTab(2) // Mudar para aba "Métodos de Controle" (índice 2)
                                  }}
                                  rightIcon={<InfoIcon />}
                                >
                                  Ver Métodos de Controle
                                </Button>
                              </HStack>

                              <Progress
                                value={risk.risk_score * 100}
                                colorScheme={getRiskColor(risk.risk_level)}
                                size="lg"
                                mb={4}
                                borderRadius="full"
                              />

                              <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4} mb={4}>
                                <Box p={3} bg="blue.50" borderRadius="md">
                                  <Text fontSize="sm" fontWeight="bold" color="blue.700" mb={1}>
                                    Multiplicador de Crescimento
                                  </Text>
                                  <Text fontSize="2xl" fontWeight="bold" color="blue.600">
                                    {risk.growth_rate_multiplier.toFixed(2)}x
                                  </Text>
                                  <Text fontSize="xs" color="gray.600" mt={1}>
                                    {risk.growth_rate_multiplier > 1
                                      ? 'Crescimento mais rápido que espécies nativas'
                                      : 'Crescimento normal'}
                                  </Text>
                                </Box>

                                <Box p={3} bg="orange.50" borderRadius="md">
                                  <Text fontSize="sm" fontWeight="bold" color="orange.700" mb={1}>
                                    Dificuldade de Remoção
                                  </Text>
                                  <Text fontSize="2xl" fontWeight="bold" color="orange.600">
                                    {Math.round(risk.removal_difficulty * 100)}%
                                  </Text>
                                  <Text fontSize="xs" color="gray.600" mt={1}>
                                    {risk.removal_difficulty > 0.7 ? 'Muito difícil' : risk.removal_difficulty > 0.4 ? 'Moderada' : 'Fácil'}
                                  </Text>
                                </Box>

                                <Box p={3} bg="green.50" borderRadius="md">
                                  <Text fontSize="sm" fontWeight="bold" color="green.700" mb={1}>
                                    Regiões Afetadas
                                  </Text>
                                  <Text fontSize="2xl" fontWeight="bold" color="green.600">
                                    {risk.regions_affected.length}
                                  </Text>
                                  <HStack flexWrap="wrap" spacing={1} mt={2}>
                                    {risk.regions_affected.slice(0, 3).map((region, i) => (
                                      <Tag key={i} size="sm" colorScheme="green">{region}</Tag>
                                    ))}
                                    {risk.regions_affected.length > 3 && (
                                      <Tag size="sm" colorScheme="gray">+{risk.regions_affected.length - 3}</Tag>
                                    )}
                                  </HStack>
                                </Box>
                              </SimpleGrid>

                              {risk.recommendations && risk.recommendations.length > 0 && (
                                <Box mt={4} p={3} bg="yellow.50" borderRadius="md" borderLeftWidth="4px" borderLeftColor="yellow.400">
                                  <Text fontSize="sm" fontWeight="bold" color="yellow.800" mb={2}>
                                    Recomendações Iniciais:
                                  </Text>
                                  <List spacing={1}>
                                    {risk.recommendations.slice(0, 2).map((rec: string, i: number) => (
                                      <ListItem key={i} fontSize="sm" color="gray.700">
                                        <ListIcon as={WarningIcon} color="yellow.600" />
                                        {rec}
                                      </ListItem>
                                    ))}
                                  </List>
                                </Box>
                              )}
                            </CardBody>
                          </Card>
                        ))}
                    </VStack>
                  </CardBody>
                </Card>
              </VStack>
            </TabPanel>

            {/* Tab: Análise Detalhada */}
            <TabPanel>
              <VStack spacing={6} align="stretch">
                {/* Mapa de Risco do Casco */}
                <Card>
                  <CardBody>
                    <HullRiskMap risks={risks} />
                  </CardBody>
                </Card>

                {/* Gráfico de Fatores Sazonais */}
                <Card>
                  <CardBody>
                    <Heading size="md" mb={4}>Fatores Sazonais de Crescimento</Heading>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={seasonalData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="season" />
                        <YAxis />
                        <RechartsTooltip />
                        <Legend />
                        {risks.map((risk, idx) => (
                          <Line
                            key={idx}
                            type="monotone"
                            dataKey="factor"
                            data={seasonalData.filter((d) => d.species === formatSpeciesName(risk.species))}
                            name={formatSpeciesName(risk.species)}
                            stroke={COLORS[idx % COLORS.length]}
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </CardBody>
                </Card>

                {/* Análise Detalhada por Espécie */}
                {risks.map((risk, index) => (
                  <Card key={index}>
                    <CardBody>
                      <Heading size="md" mb={4}>{formatSpeciesName(risk.species)}</Heading>
                      <Divider mb={4} />

                      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
                        <Box>
                          <Text fontWeight="bold" mb={2}>Informações de Risco</Text>
                          <List spacing={2}>
                            <ListItem>
                              <ListIcon as={InfoIcon} color="blue.500" />
                              Nível de Risco: <Badge colorScheme={getRiskColor(risk.risk_level)}>{getRiskLabel(risk.risk_level)}</Badge>
                            </ListItem>
                            <ListItem>
                              <ListIcon as={InfoIcon} color="blue.500" />
                              Score de Risco: {Math.round(risk.risk_score * 100)}%
                            </ListItem>
                            <ListItem>
                              <ListIcon as={InfoIcon} color="blue.500" />
                              Crescimento: {risk.growth_rate_multiplier.toFixed(2)}x mais rápido que espécies nativas
                            </ListItem>
                            <ListItem>
                              <ListIcon as={InfoIcon} color="blue.500" />
                              Dificuldade de Remoção: {Math.round(risk.removal_difficulty * 100)}%
                            </ListItem>
                          </List>
                        </Box>

                        <Box>
                          <Text fontWeight="bold" mb={2}>Regiões Afetadas</Text>
                          <HStack flexWrap="wrap" spacing={2}>
                            {risk.regions_affected.map((region, i) => (
                              <Tag key={i} colorScheme="blue">{region}</Tag>
                            ))}
                          </HStack>

                          <Text fontWeight="bold" mt={4} mb={2}>Fatores Sazonais</Text>
                          <List spacing={2}>
                            {Object.entries(risk.seasonal_factors).map(([season, factor]) => (
                              <ListItem key={season}>
                                <ListIcon as={CheckCircleIcon} color="green.500" />
                                {season === 'summer' ? 'Verão' : season === 'spring' ? 'Primavera' : season === 'autumn' ? 'Outono' : 'Inverno'}: {factor.toFixed(2)}x
                              </ListItem>
                            ))}
                          </List>
                        </Box>
                      </SimpleGrid>

                      <Box mt={4}>
                        <Text fontWeight="bold" mb={2}>Recomendações Iniciais</Text>
                        <List spacing={2}>
                          {risk.recommendations.slice(0, 3).map((rec, i) => (
                            <ListItem key={i}>
                              <ListIcon
                                as={risk.risk_level === 'critical' ? WarningIcon : CheckCircleIcon}
                                color={getRiskColor(risk.risk_level)}
                              />
                              {rec}
                            </ListItem>
                          ))}
                        </List>
                      </Box>
                    </CardBody>
                  </Card>
                ))}
              </VStack>
            </TabPanel>

            {/* Tab: Métodos de Controle */}
            <TabPanel>
              <VStack spacing={6} align="stretch">
                <Alert status="info">
                  <AlertIcon />
                  <Box>
                    <AlertTitle>Métodos de Controle Inovadores</AlertTitle>
                    <AlertDescription>
                      Esta seção apresenta métodos de controle biológico e inovadores que minimizam
                      impactos ambientais e reduzem paradas de operação.
                    </AlertDescription>
                  </Box>
                </Alert>

                {/* Seletor de Espécie */}
                <Card>
                  <CardBody>
                    <FormControl>
                      <FormLabel>Selecionar Espécie para Ver Métodos de Controle</FormLabel>
                      <Select
                        value={selectedSpecies}
                        onChange={(e) => setSelectedSpecies(e.target.value)}
                        placeholder="Selecione uma espécie..."
                      >
                        {risks.map((risk) => (
                          <option key={risk.species} value={risk.species}>
                            {formatSpeciesName(risk.species)}
                          </option>
                        ))}
                      </Select>
                    </FormControl>
                  </CardBody>
                </Card>

                {/* Informações Detalhadas da Espécie Selecionada */}
                {speciesInfo && (
                  <VStack spacing={4} align="stretch">
                    {/* Informações Básicas */}
                    <Card>
                      <CardBody>
                        <Heading size="md" mb={4}>
                          {speciesInfo.common_name || formatSpeciesName(selectedSpecies)}
                        </Heading>
                        <Text mb={4}>{speciesInfo.impact_description}</Text>

                        {speciesInfo.real_data && (
                          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4} mb={4}>
                            <Box>
                              <Text fontWeight="bold" mb={2}>Dados Reais no Brasil</Text>
                              <List spacing={2}>
                                {Object.entries(speciesInfo.real_data).map(([key, value]) => (
                                  <ListItem key={key}>
                                    <Text as="span" fontWeight="semibold">
                                      {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                                    </Text>{' '}
                                    {String(value)}
                                  </ListItem>
                                ))}
                              </List>
                            </Box>
                          </SimpleGrid>
                        )}
                      </CardBody>
                    </Card>

                    {/* Controle Biológico */}
                    {speciesInfo.biological_control && (
                      <Accordion allowMultiple>
                        <AccordionItem>
                          <AccordionButton>
                            <Box flex="1" textAlign="left">
                              <Heading size="sm">🦠 Controle Biológico (Predadores Naturais)</Heading>
                            </Box>
                            <AccordionIcon />
                          </AccordionButton>
                          <AccordionPanel pb={4}>
                            <List spacing={2}>
                              {speciesInfo.biological_control.natural_predators?.map((predator: string, i: number) => (
                                <ListItem key={i}>
                                  <ListIcon as={CheckCircleIcon} color="green.500" />
                                  {predator}
                                </ListItem>
                              ))}
                            </List>
                            <Alert status="success" mt={4}>
                              <AlertIcon />
                              <AlertDescription>
                                {speciesInfo.biological_control.environmental_impact}
                              </AlertDescription>
                            </Alert>
                          </AccordionPanel>
                        </AccordionItem>

                        <AccordionItem>
                          <AccordionButton>
                            <Box flex="1" textAlign="left">
                              <Heading size="sm">💡 Métodos Inovadores</Heading>
                            </Box>
                            <AccordionIcon />
                          </AccordionButton>
                          <AccordionPanel pb={4}>
                            <List spacing={2}>
                              {speciesInfo.biological_control.innovative_methods?.map((method: string, i: number) => (
                                <ListItem key={i}>
                                  <ListIcon as={InfoIcon} color="blue.500" />
                                  {method}
                                </ListItem>
                              ))}
                            </List>
                          </AccordionPanel>
                        </AccordionItem>

                        <AccordionItem>
                          <AccordionButton>
                            <Box flex="1" textAlign="left">
                              <Heading size="sm">⚡ Métodos Sem Parada de Operação</Heading>
                            </Box>
                            <AccordionIcon />
                          </AccordionButton>
                          <AccordionPanel pb={4}>
                            <List spacing={2}>
                              {speciesInfo.biological_control.no_downtime_methods?.map((method: string, i: number) => (
                                <ListItem key={i}>
                                  <ListIcon as={CheckCircleIcon} color="green.500" />
                                  {method}
                                </ListItem>
                              ))}
                            </List>
                            <Alert status="info" mt={4}>
                              <AlertIcon />
                              <AlertDescription>
                                Estes métodos permitem controle contínuo sem interromper operações,
                                reduzindo custos e aumentando eficiência.
                              </AlertDescription>
                            </Alert>
                          </AccordionPanel>
                        </AccordionItem>
                      </Accordion>
                    )}

                    {/* Métodos Tradicionais */}
                    <Card>
                      <CardBody>
                        <Heading size="md" mb={4}>Métodos Tradicionais de Controle</Heading>
                        <List spacing={2}>
                          {speciesInfo.traditional_methods?.map((method: string, i: number) => (
                            <ListItem key={i}>
                              <ListIcon as={WarningIcon} color="orange.500" />
                              {method}
                            </ListItem>
                          ))}
                        </List>
                      </CardBody>
                    </Card>
                  </VStack>
                )}

                {!selectedSpecies && (
                  <Alert status="info">
                    <AlertIcon />
                    Selecione uma espécie acima para ver métodos de controle detalhados.
                  </Alert>
                )}
              </VStack>
            </TabPanel>

            {/* Tab: Dados Científicos */}
            <TabPanel>
              <VStack spacing={6} align="stretch">
                <Alert status="info">
                  <AlertIcon />
                  <Box>
                    <AlertTitle>Dados Científicos e Referências</AlertTitle>
                    <AlertDescription>
                      Informações baseadas em pesquisas científicas e dados reais sobre espécies invasoras no Brasil.
                    </AlertDescription>
                  </Box>
                </Alert>

                {risks.map((risk, index) => (
                  <Card key={index}>
                    <CardBody>
                      <Heading size="md" mb={4}>{formatSpeciesName(risk.species)}</Heading>
                      <Accordion allowMultiple>
                        <AccordionItem>
                          <AccordionButton>
                            <Box flex="1" textAlign="left">
                              <Text fontWeight="bold">Condições Ambientais Ideais</Text>
                            </Box>
                            <AccordionIcon />
                          </AccordionButton>
                          <AccordionPanel pb={4}>
                            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
                              <Box>
                                <Text fontWeight="semibold">Temperatura</Text>
                                <Text>Verificar no backend</Text>
                              </Box>
                              <Box>
                                <Text fontWeight="semibold">Salinidade</Text>
                                <Text>Verificar no backend</Text>
                              </Box>
                              <Box>
                                <Text fontWeight="semibold">Profundidade</Text>
                                <Text>Verificar no backend</Text>
                              </Box>
                            </SimpleGrid>
                          </AccordionPanel>
                        </AccordionItem>

                        <AccordionItem>
                          <AccordionButton>
                            <Box flex="1" textAlign="left">
                              <Text fontWeight="bold">Fatores Sazonais de Crescimento</Text>
                            </Box>
                            <AccordionIcon />
                          </AccordionButton>
                          <AccordionPanel pb={4}>
                            <SimpleGrid columns={{ base: 1, md: 4 }} spacing={4}>
                              {Object.entries(risk.seasonal_factors).map(([season, factor]) => (
                                <Box key={season} textAlign="center" p={4} bg="blue.50" borderRadius="md">
                                  <Text fontWeight="bold" mb={2}>
                                    {season === 'summer' ? 'Verão' : season === 'spring' ? 'Primavera' : season === 'autumn' ? 'Outono' : 'Inverno'}
                                  </Text>
                                  <Text fontSize="2xl" fontWeight="bold">{factor.toFixed(2)}x</Text>
                                </Box>
                              ))}
                            </SimpleGrid>
                          </AccordionPanel>
                        </AccordionItem>
                      </Accordion>
                    </CardBody>
                  </Card>
                ))}
              </VStack>
            </TabPanel>
          </TabPanels>
        </Tabs>
      )}

      {risks && risks.length === 0 && selectedVessel && (
        <Alert status="success">
          <AlertIcon />
          <AlertTitle>Nenhum risco identificado</AlertTitle>
          <AlertDescription>
            Não foram identificadas espécies invasoras de alto risco para as condições especificadas.
          </AlertDescription>
        </Alert>
      )}

      {!selectedVessel && (
        <Alert status="info">
          <AlertIcon />
          Selecione uma embarcação e configure os parâmetros para avaliar o risco de espécies invasoras.
        </Alert>
      )}
    </VStack>
  )
}

export default InvasiveSpecies
