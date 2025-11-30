import { useState } from 'react'
import {
  Box,
  VStack,
  Heading,
  Text,
  Card,
  CardBody,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  Grid,
  Button,
  HStack,
  Select,
  Spinner,
  Center,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  ModalFooter,
  useDisclosure,
  List,
  ListItem,
  ListIcon,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Progress,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Divider,
  SimpleGrid,
  IconButton,
  Tooltip,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
} from '@chakra-ui/react'
import {
  CheckCircleIcon,
  WarningIcon,
  InfoIcon,
  DownloadIcon,
  ViewIcon,
  ChevronDownIcon,
} from '@chakra-ui/icons'
import { useQuery } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import {
  dashboardService,
  complianceService,
  fleetManagementService,
  type FleetDetailedStatus,
  type ComplianceCheck
} from '../api/services'
import KPICard from '../components/KPICard'
import ComplianceReport from '../components/ComplianceReport'
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
  PieChart,
  Pie,
  Cell
} from 'recharts'



interface CorrectiveAction {
  action_id: string
  action_type: string
  priority: string
  title: string
  description: string
  deadline: string
  estimated_cost_brl: number
  estimated_duration_hours: number
  expected_compliance_restoration: string
  required_resources: string[]
  steps: string[]
  success_criteria: string[]
}

// Cores para gráficos
const COLORS = {
  compliant: '#48BB78',
  at_risk: '#ED8936',
  non_compliant: '#F56565',
  critical: '#C53030',
  compliant_light: '#C6F6D5',
  at_risk_light: '#FEEBC8',
  non_compliant_light: '#FED7D7',
  critical_light: '#FC8181'
}



function Compliance() {
  const navigate = useNavigate()
  const [selectedVessel, setSelectedVessel] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [selectedTab, setSelectedTab] = useState(0)
  const [showReport, setShowReport] = useState(false)
  const { isOpen, onOpen, onClose } = useDisclosure()

  // Buscar status detalhado da frota
  const { data: fleetStatus, isLoading: fleetLoading, error: fleetError } = useQuery<FleetDetailedStatus>({
    queryKey: ['fleet-detailed-status'],
    queryFn: async () => {
      return await fleetManagementService.getDetailedStatus()
    },
    refetchInterval: 60000,
  })

  // Buscar KPIs de conformidade
  const { data: kpis } = useQuery({
    queryKey: ['dashboard-kpis'],
    queryFn: async () => {
      return await dashboardService.getKPIs('6_months')
    },
  })

  // Buscar ações corretivas para embarcação selecionada
  const { data: correctiveActions, isLoading: actionsLoading } = useQuery<CorrectiveAction[]>({
    queryKey: ['corrective-actions', selectedVessel],
    queryFn: async () => {
      if (!selectedVessel) return []
      const vessel = fleetStatus?.vessels.find(v => v.id === selectedVessel)
      if (!vessel) return []

      try {
        return await complianceService.getCorrectiveActions(
          selectedVessel,
          vessel.fouling_mm,
          vessel.roughness_um
        )
      } catch {
        return []
      }
    },
    enabled: !!selectedVessel && !!fleetStatus,
  })

  // Buscar verificação de conformidade detalhada para embarcação selecionada
  const { data: complianceCheck } = useQuery<ComplianceCheck | null>({
    queryKey: ['compliance-check', selectedVessel],
    queryFn: async () => {
      if (!selectedVessel) return null
      const vessel = fleetStatus?.vessels.find(v => v.id === selectedVessel)
      if (!vessel) return null

      try {
        return await complianceService.checkCompliance(
          selectedVessel,
          vessel.fouling_mm,
          vessel.roughness_um,
          vessel.vessel_class || 'standard'
        )
      } catch {
        return null
      }
    },
    enabled: !!selectedVessel && !!fleetStatus,
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'compliant': return 'green'
      case 'at_risk': return 'yellow'
      case 'non_compliant': return 'orange'
      case 'critical': return 'red'
      default: return 'gray'
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'compliant': return 'Conforme'
      case 'at_risk': return 'Em Risco'
      case 'non_compliant': return 'Não Conforme'
      case 'critical': return 'Crítico'
      default: return 'Desconhecido'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'immediate': return 'red'
      case 'high': return 'orange'
      case 'medium': return 'yellow'
      case 'low': return 'blue'
      default: return 'gray'
    }
  }

  const getPriorityLabel = (priority: string) => {
    switch (priority) {
      case 'immediate': return 'Imediata'
      case 'high': return 'Alta'
      case 'medium': return 'Média'
      case 'low': return 'Baixa'
      default: return priority
    }
  }

  // Calcular estatísticas
  const stats = fleetStatus ? {
    total: fleetStatus.vessels.length,
    compliant: fleetStatus.vessels.filter(v => {
      // Determinar status baseado em FR level
      if (v.fr_level === 0 || v.fr_level === 1) return true
      return false
    }).length,
    atRisk: fleetStatus.vessels.filter(v => v.fr_level === 2).length,
    nonCompliant: fleetStatus.vessels.filter(v => v.fr_level >= 3).length,
    complianceRate: (fleetStatus.vessels.filter(v => v.fr_level <= 1).length /
      fleetStatus.vessels.length) * 100,
    avgFouling: fleetStatus.vessels.reduce((sum, v) => sum + v.fouling_mm, 0) / fleetStatus.vessels.length,
    avgRoughness: fleetStatus.vessels.reduce((sum, v) => sum + v.roughness_um, 0) / fleetStatus.vessels.length,
  } : null

  // Filtrar embarcações
  const filteredVessels = fleetStatus?.vessels.filter(v => {
    if (statusFilter === 'all') return true
    if (statusFilter === 'compliant') return v.fr_level <= 1
    if (statusFilter === 'at_risk') return v.fr_level === 2
    if (statusFilter === 'non_compliant') return v.fr_level >= 3
    return true
  }) || []

  // Dados para gráfico de distribuição de conformidade
  const complianceDistributionData = stats ? [
    { name: 'Conformes', value: stats.compliant, color: COLORS.compliant },
    { name: 'Em Risco', value: stats.atRisk, color: COLORS.at_risk },
    { name: 'Não Conformes', value: stats.nonCompliant, color: COLORS.non_compliant },
  ] : []

  // Dados para gráfico de tendência de conformidade (simulado - em produção viria do backend)
  const complianceTrendData = [
    { month: 'Jan', rate: 92, vessels: 26 },
    { month: 'Fev', rate: 93, vessels: 26 },
    { month: 'Mar', rate: 94, vessels: 27 },
    { month: 'Abr', rate: 94.5, vessels: 27 },
    { month: 'Mai', rate: 95, vessels: 28 },
    { month: 'Jun', rate: stats?.complianceRate || 95, vessels: stats?.total || 28 },
  ]

  const handleViewDetails = (vesselId: string) => {
    setSelectedVessel(vesselId)
    onOpen()
  }

  const handleViewVessel = (vesselId: string) => {
    navigate(`/vessel/${vesselId}`)
  }

  // Funções de exportação
  const exportToCSV = () => {
    if (!fleetStatus || !filteredVessels.length) return

    const headers = [
      'Embarcação',
      'ID',
      'Classe',
      'FR Level',
      'FR Label',
      'Espessura (mm)',
      'Rugosidade (μm)',
      'Perda Performance (%)',
      'Status',
      'Última Limpeza',
      'Última Pintura',
      'Calibração Sensor',
      'Risco 15 dias',
      'Risco 30 dias',
      'Alerta',
    ]

    const rows = filteredVessels.map(vessel => {
      const status = vessel.fr_level <= 1 ? 'Conforme' :
        vessel.fr_level === 2 ? 'Em Risco' :
          'Não Conforme'

      return [
        vessel.name || '',
        vessel.vessel_id || '',
        vessel.vessel_class || '',
        vessel.fr_level.toString(),
        vessel.fr_label || '',
        vessel.fouling_mm.toFixed(2),
        vessel.roughness_um.toFixed(1),
        vessel.performance_loss_percent.toFixed(1),
        status,
        vessel.last_cleaning_date || 'N/A',
        vessel.last_painting_date || 'N/A',
        vessel.sensor_calibration_date || 'N/A',
        vessel.risk_15_days.toString(),
        vessel.risk_30_days.toString(),
        vessel.alert_message || '',
      ]
    })

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n')

    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `conformidade_normam401_${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const exportToExcel = () => {
    // Para Excel, vamos gerar um CSV com extensão .xlsx (compatível com Excel)
    // Em produção, poderia usar uma biblioteca como xlsx
    if (!fleetStatus || !filteredVessels.length) return

    const headers = [
      'Embarcação',
      'ID',
      'Classe',
      'FR Level',
      'FR Label',
      'Espessura (mm)',
      'Rugosidade (μm)',
      'Perda Performance (%)',
      'Status',
      'Última Limpeza',
      'Última Pintura',
      'Calibração Sensor',
      'Risco 15 dias',
      'Risco 30 dias',
      'Alerta',
    ]

    const rows = filteredVessels.map(vessel => {
      const status = vessel.fr_level <= 1 ? 'Conforme' :
        vessel.fr_level === 2 ? 'Em Risco' :
          'Não Conforme'

      return [
        vessel.name || '',
        vessel.vessel_id || '',
        vessel.vessel_class || '',
        vessel.fr_level.toString(),
        vessel.fr_label || '',
        vessel.fouling_mm.toFixed(2),
        vessel.roughness_um.toFixed(1),
        vessel.performance_loss_percent.toFixed(1),
        status,
        vessel.last_cleaning_date || 'N/A',
        vessel.last_painting_date || 'N/A',
        vessel.sensor_calibration_date || 'N/A',
        vessel.risk_15_days.toString(),
        vessel.risk_30_days.toString(),
        vessel.alert_message || '',
      ]
    })

    // Adicionar linha de resumo
    const summaryRow = [
      'RESUMO',
      '',
      '',
      '',
      '',
      stats?.avgFouling.toFixed(2) || '',
      stats?.avgRoughness.toFixed(1) || '',
      '',
      '',
      '',
      '',
      '',
      '',
      '',
      `Taxa de Conformidade: ${stats?.complianceRate.toFixed(1)}%`,
    ]

    const csvContent = [
      headers.join('\t'),
      ...rows.map(row => row.join('\t')),
      '',
      summaryRow.join('\t'),
    ].join('\n')

    const blob = new Blob(['\ufeff' + csvContent], { type: 'application/vnd.ms-excel;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `conformidade_normam401_${new Date().toISOString().split('T')[0]}.xls`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const exportToPDF = () => {
    // Abrir relatório em modo de impressão
    setShowReport(true)
    setTimeout(() => {
      window.print()
    }, 500)
  }

  if (fleetLoading) {
    return (
      <Center py={20}>
        <Spinner size="xl" />
      </Center>
    )
  }

  if (fleetError) {
    return (
      <Alert status="error">
        <AlertIcon />
        <Box>
          <AlertTitle>Erro ao carregar dados</AlertTitle>
          <AlertDescription>
            Não foi possível carregar os dados de conformidade. Tente novamente mais tarde.
          </AlertDescription>
        </Box>
      </Alert>
    )
  }

  // Se mostrar relatório, renderizar componente de relatório
  if (showReport && fleetStatus) {
    return (
      <ComplianceReport
        fleetStatus={fleetStatus}
        showPrintButton={true}
      />
    )
  }

  return (
    <VStack spacing={6} align="stretch">
      {/* Cabeçalho */}
      <Box>
        <HStack justify="space-between" align="start">
          <Box>
            <Heading size="xl" mb={2}>Conformidade NORMAM 401</Heading>
            <Text color="gray.600" mb={2}>
              Monitoramento regulatório e gestão de conformidade da frota
            </Text>
            <Text fontSize="sm" color="gray.500">
              NORMAM 401 - Diretoria de Portos e Costas (DPC) | Portaria DPC/DGN/MB nº 180/2025
            </Text>
          </Box>
          <HStack>
            <Menu>
              <MenuButton
                as={Button}
                leftIcon={<DownloadIcon />}
                rightIcon={<ChevronDownIcon />}
                colorScheme="blue"
                variant="outline"
                size="sm"
              >
                Exportar
              </MenuButton>
              <MenuList>
                <MenuItem icon={<DownloadIcon />} onClick={exportToCSV}>
                  Exportar CSV
                </MenuItem>
                <MenuItem icon={<DownloadIcon />} onClick={exportToExcel}>
                  Exportar Excel
                </MenuItem>
                <MenuItem icon={<DownloadIcon />} onClick={exportToPDF}>
                  Exportar PDF
                </MenuItem>
                <MenuItem icon={<DownloadIcon />} onClick={() => setShowReport(!showReport)}>
                  {showReport ? 'Fechar Relatório' : 'Ver Relatório Completo'}
                </MenuItem>
              </MenuList>
            </Menu>
            {showReport && (
              <Button
                leftIcon={<DownloadIcon />}
                colorScheme="green"
                size="sm"
                onClick={() => window.print()}
              >
                Imprimir / Salvar PDF
              </Button>
            )}
          </HStack>
        </HStack>
      </Box>

      {/* KPIs Principais */}
      <Grid templateColumns={{ base: '1fr', md: 'repeat(4, 1fr)' }} gap={4}>
        <KPICard
          label="Taxa de Conformidade"
          value={stats ? `${stats.complianceRate.toFixed(1)}%` : '0%'}
          helpText={`${stats?.compliant || 0} de ${stats?.total || 0} embarcações`}
          colorScheme={stats && stats.complianceRate >= 95 ? 'green' : stats && stats.complianceRate >= 80 ? 'yellow' : 'orange'}
        />
        <KPICard
          label="Conformes"
          value={stats?.compliant.toString() || "0"}
          helpText="FR 0-1 (Limpo/Micro)"
          colorScheme="green"
        />
        <KPICard
          label="Em Risco"
          value={stats?.atRisk.toString() || "0"}
          helpText="FR 2 (Macro Leve)"
          colorScheme="yellow"
        />
        <KPICard
          label="Não Conformes"
          value={stats?.nonCompliant.toString() || "0"}
          helpText="FR 3-4 (Crítico)"
          colorScheme="red"
        />
      </Grid>

      {/* Tabs para diferentes visualizações */}
      <Tabs index={selectedTab} onChange={setSelectedTab} colorScheme="blue">
        <TabList>
          <Tab>Visão Geral</Tab>
          <Tab>Análise Detalhada</Tab>
          <Tab>Tendências</Tab>
          <Tab>Documentação NORMAM 401</Tab>
        </TabList>

        <TabPanels>
          {/* Tab: Visão Geral */}
          <TabPanel>
            <VStack spacing={6} align="stretch">
              {/* Gráficos de Resumo */}
              <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={4}>
                {/* Gráfico de Pizza - Distribuição */}
                <Card>
                  <CardBody>
                    <Heading size="sm" mb={4}>Distribuição de Conformidade</Heading>
                    {complianceDistributionData.length > 0 ? (
                      <ResponsiveContainer width="100%" height={250}>
                        <PieChart>
                          <Pie
                            data={complianceDistributionData}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="value"
                          >
                            {complianceDistributionData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Pie>
                          <RechartsTooltip />
                        </PieChart>
                      </ResponsiveContainer>
                    ) : (
                      <Center py={8}>
                        <Text color="gray.500">Sem dados disponíveis</Text>
                      </Center>
                    )}
                  </CardBody>
                </Card>

                {/* Estatísticas Adicionais */}
                <Card>
                  <CardBody>
                    <Heading size="sm" mb={4}>Métricas de Conformidade</Heading>
                    <VStack spacing={4} align="stretch">
                      <Stat>
                        <StatLabel>Espessura Média</StatLabel>
                        <StatNumber fontSize="2xl">
                          {stats?.avgFouling.toFixed(2) || '0.00'} mm
                        </StatNumber>
                        <StatHelpText>
                          Limite máximo: 5.0 mm
                        </StatHelpText>
                        <Progress
                          value={(stats?.avgFouling || 0) / 5.0 * 100}
                          colorScheme={stats && stats.avgFouling > 4.0 ? 'red' : stats && stats.avgFouling > 3.0 ? 'yellow' : 'green'}
                          size="sm"
                          mt={2}
                        />
                      </Stat>
                      <Divider />
                      <Stat>
                        <StatLabel>Rugosidade Média</StatLabel>
                        <StatNumber fontSize="2xl">
                          {stats?.avgRoughness.toFixed(0) || '0'} μm
                        </StatNumber>
                        <StatHelpText>
                          Limite máximo: 500 μm
                        </StatHelpText>
                        <Progress
                          value={(stats?.avgRoughness || 0) / 500.0 * 100}
                          colorScheme={stats && stats.avgRoughness > 400 ? 'red' : stats && stats.avgRoughness > 300 ? 'yellow' : 'green'}
                          size="sm"
                          mt={2}
                        />
                      </Stat>
                      <Divider />
                      <Box>
                        <Text fontSize="sm" color="gray.600" mb={2}>Score de Conformidade</Text>
                        <HStack>
                          <Progress
                            value={kpis?.compliance_rate_percent || 0}
                            colorScheme={kpis && kpis.compliance_rate_percent >= 95 ? 'green' : kpis && kpis.compliance_rate_percent >= 80 ? 'yellow' : 'orange'}
                            flex={1}
                            size="lg"
                            borderRadius="md"
                          />
                          <Text fontWeight="bold" minW="60px" textAlign="right">
                            {kpis?.compliance_rate_percent.toFixed(1) || '0.0'}%
                          </Text>
                        </HStack>
                      </Box>
                    </VStack>
                  </CardBody>
                </Card>
              </Grid>

              {/* Tabela de Conformidade */}
              <Card>
                <CardBody>
                  <HStack justify="space-between" mb={4}>
                    <Heading size="md">Status por Embarcação</Heading>
                    <HStack>
                      <Select
                        width="200px"
                        size="sm"
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                      >
                        <option value="all">Todas</option>
                        <option value="compliant">Conformes</option>
                        <option value="at_risk">Em Risco</option>
                        <option value="non_compliant">Não Conformes</option>
                      </Select>
                      <Menu>
                        <MenuButton
                          as={Button}
                          size="sm"
                          variant="ghost"
                          leftIcon={<DownloadIcon />}
                          rightIcon={<ChevronDownIcon />}
                        >
                          Exportar
                        </MenuButton>
                        <MenuList>
                          <MenuItem icon={<DownloadIcon />} onClick={exportToCSV}>
                            Exportar CSV
                          </MenuItem>
                          <MenuItem icon={<DownloadIcon />} onClick={exportToExcel}>
                            Exportar Excel
                          </MenuItem>
                          <MenuItem icon={<DownloadIcon />} onClick={exportToPDF}>
                            Exportar PDF
                          </MenuItem>
                        </MenuList>
                      </Menu>
                    </HStack>
                  </HStack>

                  {filteredVessels.length > 0 ? (
                    <Table variant="simple" size="sm">
                      <Thead>
                        <Tr>
                          <Th>Embarcação</Th>
                          <Th>Classe</Th>
                          <Th>FR</Th>
                          <Th>Espessura (mm)</Th>
                          <Th>Rugosidade (μm)</Th>
                          <Th>Perda Performance</Th>
                          <Th>Status</Th>
                          <Th>Próxima Inspeção</Th>
                          <Th>Ações</Th>
                        </Tr>
                      </Thead>
                      <Tbody>
                        {filteredVessels.map((vessel) => {
                          const isCompliant = vessel.fr_level <= 1
                          const isAtRisk = vessel.fr_level === 2
                          const isNonCompliant = vessel.fr_level >= 3

                          return (
                            <Tr key={vessel.id} _hover={{ bg: 'gray.50' }}>
                              <Td>
                                <Link to={`/vessel/${vessel.id}`}>
                                  <Text fontWeight="medium" color="blue.600" _hover={{ textDecoration: 'underline' }}>
                                    {vessel.name}
                                  </Text>
                                </Link>
                                <Text fontSize="xs" color="gray.500">
                                  {vessel.vessel_id}
                                </Text>
                              </Td>
                              <Td>
                                <Badge colorScheme="blue" variant="outline">
                                  {vessel.vessel_class || 'N/A'}
                                </Badge>
                              </Td>
                              <Td>
                                <Badge
                                  colorScheme={
                                    vessel.fr_level === 0 ? 'green' :
                                      vessel.fr_level === 1 ? 'blue' :
                                        vessel.fr_level === 2 ? 'yellow' :
                                          vessel.fr_level === 3 ? 'orange' : 'red'
                                  }
                                  size="md"
                                >
                                  FR {vessel.fr_level}
                                </Badge>
                                <Text fontSize="xs" color="gray.500" mt={1}>
                                  {vessel.fr_label}
                                </Text>
                              </Td>
                              <Td>
                                <Text>
                                  {vessel.fouling_mm.toFixed(2)}
                                  <Text as="span" fontSize="xs" color="gray.500" ml={1}>
                                    / 5.0
                                  </Text>
                                </Text>
                                <Progress
                                  value={(vessel.fouling_mm / 5.0) * 100}
                                  colorScheme={vessel.fouling_mm > 4.0 ? 'red' : vessel.fouling_mm > 3.0 ? 'yellow' : 'green'}
                                  size="xs"
                                  mt={1}
                                />
                              </Td>
                              <Td>
                                <Text>
                                  {vessel.roughness_um.toFixed(0)}
                                  <Text as="span" fontSize="xs" color="gray.500" ml={1}>
                                    / 500
                                  </Text>
                                </Text>
                                <Progress
                                  value={(vessel.roughness_um / 500.0) * 100}
                                  colorScheme={vessel.roughness_um > 400 ? 'red' : vessel.roughness_um > 300 ? 'yellow' : 'green'}
                                  size="xs"
                                  mt={1}
                                />
                              </Td>
                              <Td>
                                <Text fontWeight="bold" color={vessel.performance_loss_percent > 20 ? 'red' : vessel.performance_loss_percent > 10 ? 'orange' : 'green'}>
                                  {vessel.performance_loss_percent.toFixed(1)}%
                                </Text>
                              </Td>
                              <Td>
                                <Badge
                                  colorScheme={
                                    isCompliant ? 'green' :
                                      isAtRisk ? 'yellow' :
                                        isNonCompliant ? 'red' : 'gray'
                                  }
                                >
                                  {isCompliant ? 'Conforme' : isAtRisk ? 'Em Risco' : 'Não Conforme'}
                                </Badge>
                                {vessel.alert_message && (
                                  <Tooltip label={vessel.alert_message}>
                                    <IconButton
                                      aria-label="Alerta"
                                      icon={<WarningIcon />}
                                      size="xs"
                                      colorScheme={vessel.alert_type === 'critical' ? 'red' : vessel.alert_type === 'warning' ? 'yellow' : 'blue'}
                                      variant="ghost"
                                      mt={1}
                                    />
                                  </Tooltip>
                                )}
                              </Td>
                              <Td>
                                <Text fontSize="sm">
                                  {vessel.last_cleaning_date
                                    ? new Date(vessel.last_cleaning_date).toLocaleDateString('pt-BR')
                                    : 'N/A'}
                                </Text>
                                <Text fontSize="xs" color="gray.500">
                                  {vessel.last_cleaning_date
                                    ? `${Math.floor((new Date().getTime() - new Date(vessel.last_cleaning_date).getTime()) / (1000 * 60 * 60 * 24))} dias`
                                    : ''}
                                </Text>
                              </Td>
                              <Td>
                                <HStack spacing={1}>
                                  <Tooltip label="Ver Detalhes">
                                    <IconButton
                                      aria-label="Ver detalhes"
                                      icon={<ViewIcon />}
                                      size="sm"
                                      colorScheme="blue"
                                      variant="ghost"
                                      onClick={() => handleViewVessel(vessel.id)}
                                    />
                                  </Tooltip>
                                  <Tooltip label="Análise de Conformidade">
                                    <IconButton
                                      aria-label="Análise"
                                      icon={<InfoIcon />}
                                      size="sm"
                                      colorScheme="purple"
                                      variant="ghost"
                                      onClick={() => handleViewDetails(vessel.id)}
                                    />
                                  </Tooltip>
                                </HStack>
                              </Td>
                            </Tr>
                          )
                        })}
                      </Tbody>
                    </Table>
                  ) : (
                    <Alert status="info">
                      <AlertIcon />
                      Nenhuma embarcação encontrada com o filtro selecionado.
                    </Alert>
                  )}
                </CardBody>
              </Card>
            </VStack>
          </TabPanel>

          {/* Tab: Análise Detalhada */}
          <TabPanel>
            <VStack spacing={6} align="stretch">
              {/* Alertas Críticos */}
              {fleetStatus && fleetStatus.vessels.filter(v => v.fr_level >= 3 || v.alert_type === 'critical').length > 0 && (
                <Alert status="error" borderRadius="md">
                  <AlertIcon />
                  <Box flex={1}>
                    <AlertTitle>Embarcações Críticas</AlertTitle>
                    <AlertDescription>
                      {fleetStatus.vessels.filter(v => v.fr_level >= 3 || v.alert_type === 'critical').length} embarcação(ões)
                      requerem ação imediata para conformidade com NORMAM 401.
                    </AlertDescription>
                  </Box>
                </Alert>
              )}

              {/* Análise por Classe */}
              <Card>
                <CardBody>
                  <Heading size="md" mb={4}>Análise por Classe de Embarcação</Heading>
                  {fleetStatus && fleetStatus.vessels.length > 0 ? (
                    <Table variant="simple" size="sm">
                      <Thead>
                        <Tr>
                          <Th>Classe</Th>
                          <Th>Total</Th>
                          <Th>Conformes</Th>
                          <Th>Em Risco</Th>
                          <Th>Não Conformes</Th>
                          <Th>Taxa Conformidade</Th>
                        </Tr>
                      </Thead>
                      <Tbody>
                        {Array.from(new Set(fleetStatus.vessels.map(v => v.vessel_class || 'N/A'))).map(className => {
                          const classVessels = fleetStatus.vessels.filter(v => (v.vessel_class || 'N/A') === className)
                          const compliant = classVessels.filter(v => v.fr_level <= 1).length
                          const atRisk = classVessels.filter(v => v.fr_level === 2).length
                          const nonCompliant = classVessels.filter(v => v.fr_level >= 3).length
                          const rate = (compliant / classVessels.length) * 100

                          return (
                            <Tr key={className}>
                              <Td fontWeight="medium">{className}</Td>
                              <Td>{classVessels.length}</Td>
                              <Td>
                                <Badge colorScheme="green">{compliant}</Badge>
                              </Td>
                              <Td>
                                <Badge colorScheme="yellow">{atRisk}</Badge>
                              </Td>
                              <Td>
                                <Badge colorScheme="red">{nonCompliant}</Badge>
                              </Td>
                              <Td>
                                <HStack>
                                  <Progress value={rate} colorScheme={rate >= 95 ? 'green' : rate >= 80 ? 'yellow' : 'orange'} flex={1} size="sm" />
                                  <Text fontSize="sm" fontWeight="bold" minW="50px">
                                    {rate.toFixed(1)}%
                                  </Text>
                                </HStack>
                              </Td>
                            </Tr>
                          )
                        })}
                      </Tbody>
                    </Table>
                  ) : (
                    <Alert status="info">
                      <AlertIcon />
                      Nenhum dado disponível.
                    </Alert>
                  )}
                </CardBody>
              </Card>

              {/* Fatores de Risco */}
              <Card>
                <CardBody>
                  <Heading size="md" mb={4}>Fatores de Risco Identificados</Heading>
                  <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                    {fleetStatus && fleetStatus.vessels.filter(v => v.fr_level >= 2).map(vessel => (
                      <Card key={vessel.id} variant="outline" borderColor={vessel.fr_level >= 3 ? 'red.300' : 'yellow.300'}>
                        <CardBody>
                          <HStack justify="space-between" mb={2}>
                            <Text fontWeight="bold">{vessel.name}</Text>
                            <Badge colorScheme={vessel.fr_level >= 3 ? 'red' : 'yellow'}>
                              FR {vessel.fr_level}
                            </Badge>
                          </HStack>
                          {vessel.alert_message && (
                            <Alert status={vessel.alert_type === 'critical' ? 'error' : 'warning'} size="sm" borderRadius="md" mb={2}>
                              <AlertIcon />
                              <Text fontSize="xs">{vessel.alert_message}</Text>
                            </Alert>
                          )}
                          <VStack align="stretch" spacing={1} fontSize="sm">
                            <HStack justify="space-between">
                              <Text color="gray.600">Espessura:</Text>
                              <Text fontWeight="bold">{vessel.fouling_mm.toFixed(2)} mm</Text>
                            </HStack>
                            <HStack justify="space-between">
                              <Text color="gray.600">Rugosidade:</Text>
                              <Text fontWeight="bold">{vessel.roughness_um.toFixed(0)} μm</Text>
                            </HStack>
                            <HStack justify="space-between">
                              <Text color="gray.600">Perda Performance:</Text>
                              <Text fontWeight="bold" color="red.600">{vessel.performance_loss_percent.toFixed(1)}%</Text>
                            </HStack>
                            <HStack justify="space-between">
                              <Text color="gray.600">Risco 30 dias:</Text>
                              <Badge colorScheme={vessel.risk_30_days >= 3 ? 'red' : vessel.risk_30_days === 2 ? 'yellow' : 'green'}>
                                FR {vessel.risk_30_days}
                              </Badge>
                            </HStack>
                          </VStack>
                          <Button
                            size="xs"
                            colorScheme="blue"
                            variant="outline"
                            mt={3}
                            width="100%"
                            onClick={() => handleViewDetails(vessel.id)}
                          >
                            Ver Análise Completa
                          </Button>
                        </CardBody>
                      </Card>
                    ))}
                  </SimpleGrid>
                  {fleetStatus && fleetStatus.vessels.filter(v => v.fr_level >= 2).length === 0 && (
                    <Alert status="success">
                      <AlertIcon />
                      Nenhum fator de risco crítico identificado. Todas as embarcações estão em conformidade ou com risco controlado.
                    </Alert>
                  )}
                </CardBody>
              </Card>
            </VStack>
          </TabPanel>

          {/* Tab: Tendências */}
          <TabPanel>
            <VStack spacing={6} align="stretch">
              <Card>
                <CardBody>
                  <Heading size="md" mb={4}>Tendência de Conformidade (6 meses)</Heading>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={complianceTrendData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis yAxisId="left" label={{ value: 'Taxa (%)', angle: -90, position: 'insideLeft' }} />
                      <YAxis yAxisId="right" orientation="right" label={{ value: 'Embarcações', angle: 90, position: 'insideRight' }} />
                      <RechartsTooltip />
                      <Legend />
                      <Line
                        yAxisId="left"
                        type="monotone"
                        dataKey="rate"
                        stroke="#48BB78"
                        name="Taxa de Conformidade (%)"
                        strokeWidth={2}
                        dot={{ r: 4 }}
                      />
                      <Line
                        yAxisId="right"
                        type="monotone"
                        dataKey="vessels"
                        stroke="#4299E1"
                        name="Embarcações Monitoradas"
                        strokeWidth={2}
                        dot={{ r: 4 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardBody>
              </Card>

              <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={4}>
                <Card>
                  <CardBody>
                    <Heading size="sm" mb={4}>Distribuição FR (Atual)</Heading>
                    {fleetStatus && (
                      <ResponsiveContainer width="100%" height={200}>
                        <BarChart data={[
                          { name: 'FR 0', value: fleetStatus.vessels.filter(v => v.fr_level === 0).length },
                          { name: 'FR 1', value: fleetStatus.vessels.filter(v => v.fr_level === 1).length },
                          { name: 'FR 2', value: fleetStatus.vessels.filter(v => v.fr_level === 2).length },
                          { name: 'FR 3', value: fleetStatus.vessels.filter(v => v.fr_level === 3).length },
                          { name: 'FR 4', value: fleetStatus.vessels.filter(v => v.fr_level === 4).length },
                        ]}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="name" />
                          <YAxis />
                          <RechartsTooltip />
                          <Bar dataKey="value" fill="#4299E1" />
                        </BarChart>
                      </ResponsiveContainer>
                    )}
                  </CardBody>
                </Card>

                <Card>
                  <CardBody>
                    <Heading size="sm" mb={4}>Evolução de Espessura Média</Heading>
                    <ResponsiveContainer width="100%" height={200}>
                      <LineChart data={complianceTrendData.map((d, i) => ({
                        month: d.month,
                        avgFouling: stats ? stats.avgFouling * (1 - (i * 0.02)) : 0
                      }))}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="month" />
                        <YAxis label={{ value: 'mm', angle: -90, position: 'insideLeft' }} />
                        <RechartsTooltip />
                        <Line
                          type="monotone"
                          dataKey="avgFouling"
                          stroke="#F56565"
                          name="Espessura Média (mm)"
                          strokeWidth={2}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardBody>
                </Card>
              </Grid>
            </VStack>
          </TabPanel>

          {/* Tab: Documentação NORMAM 401 */}
          <TabPanel>
            <VStack spacing={6} align="stretch">
              <Card>
                <CardBody>
                  <Heading size="md" mb={4}>Sobre a NORMAM 401</Heading>
                  <VStack align="stretch" spacing={4}>
                    <Box>
                      <Heading size="sm" mb={2}>O que é a NORMAM 401?</Heading>
                      <Text fontSize="sm" color="gray.700">
                        A NORMAM 401, estabelecida pela Diretoria de Portos e Costas (DPC), regulamenta o controle
                        de bioincrustação em cascos de embarcações que operam em águas brasileiras. Esta norma visa
                        prevenir a introdução e dispersão de espécies invasoras e garantir a eficiência operacional
                        das embarcações.
                      </Text>
                    </Box>

                    <Divider />

                    <Box>
                      <Heading size="sm" mb={2}>Limites de Conformidade</Heading>
                      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                        <Box p={4} bg="blue.50" borderRadius="md">
                          <Text fontWeight="bold" mb={2}>Espessura de Bioincrustação</Text>
                          <List spacing={2} fontSize="sm">
                            <ListItem>
                              <ListIcon as={CheckCircleIcon} color="green.500" />
                              <strong>Limite máximo:</strong> 5.0 mm (geral)
                            </ListItem>
                            <ListItem>
                              <ListIcon as={CheckCircleIcon} color="green.500" />
                              <strong>Container:</strong> 4.5 mm (mais rigoroso)
                            </ListItem>
                            <ListItem>
                              <ListIcon as={WarningIcon} color="orange.500" />
                              <strong>Zona de alerta:</strong> 4.0 mm (80% do limite)
                            </ListItem>
                          </List>
                        </Box>
                        <Box p={4} bg="green.50" borderRadius="md">
                          <Text fontWeight="bold" mb={2}>Rugosidade</Text>
                          <List spacing={2} fontSize="sm">
                            <ListItem>
                              <ListIcon as={CheckCircleIcon} color="green.500" />
                              <strong>Limite máximo:</strong> 500 μm (geral)
                            </ListItem>
                            <ListItem>
                              <ListIcon as={CheckCircleIcon} color="green.500" />
                              <strong>Container:</strong> 450 μm (mais rigoroso)
                            </ListItem>
                            <ListItem>
                              <ListIcon as={WarningIcon} color="orange.500" />
                              <strong>Zona de alerta:</strong> 400 μm (80% do limite)
                            </ListItem>
                          </List>
                        </Box>
                      </SimpleGrid>
                    </Box>

                    <Divider />

                    <Box>
                      <Heading size="sm" mb={2}>Frequência de Inspeções</Heading>
                      <List spacing={2} fontSize="sm">
                        <ListItem>
                          <ListIcon as={InfoIcon} color="blue.500" />
                          <strong>Mínimo:</strong> Trimestral (90 dias)
                        </ListItem>
                        <ListItem>
                          <ListIcon as={WarningIcon} color="orange.500" />
                          <strong>Alto risco:</strong> Mensal (30 dias) recomendado
                        </ListItem>
                        <ListItem>
                          <ListIcon as={CheckCircleIcon} color="green.500" />
                          <strong>Documentação:</strong> Registro obrigatório de todas as inspeções
                        </ListItem>
                      </List>
                    </Box>

                    <Divider />

                    <Box>
                      <Heading size="sm" mb={2}>Classificação FR (Fouling Risk)</Heading>
                      <Accordion allowToggle>
                        <AccordionItem>
                          <AccordionButton>
                            <Box flex="1" textAlign="left">
                              <Badge colorScheme="green" mr={2}>FR 0</Badge>
                              <Text as="span" fontWeight="bold">Sem Incrustação</Text>
                            </Box>
                            <AccordionIcon />
                          </AccordionButton>
                          <AccordionPanel pb={4}>
                            <Text fontSize="sm">
                              Bioincrustação &lt; 1mm. Casco limpo, sem necessidade de limpeza imediata.
                              Manter monitoramento preventivo.
                            </Text>
                          </AccordionPanel>
                        </AccordionItem>

                        <AccordionItem>
                          <AccordionButton>
                            <Box flex="1" textAlign="left">
                              <Badge colorScheme="blue" mr={2}>FR 1</Badge>
                              <Text as="span" fontWeight="bold">Microincrustação</Text>
                            </Box>
                            <AccordionIcon />
                          </AccordionButton>
                          <AccordionPanel pb={4}>
                            <Text fontSize="sm">
                              Bioincrustação entre 1mm e 3mm. Conforme com NORMAM 401.
                              Planejar limpeza preventiva nos próximos 30-60 dias.
                            </Text>
                          </AccordionPanel>
                        </AccordionItem>

                        <AccordionItem>
                          <AccordionButton>
                            <Box flex="1" textAlign="left">
                              <Badge colorScheme="yellow" mr={2}>FR 2</Badge>
                              <Text as="span" fontWeight="bold">Macro Leve (Alerta)</Text>
                            </Box>
                            <AccordionIcon />
                          </AccordionButton>
                          <AccordionPanel pb={4}>
                            <Text fontSize="sm">
                              Bioincrustação entre 3mm e 4mm. Em risco de não conformidade.
                              Limpeza reativa recomendada dentro de 15-30 dias.
                            </Text>
                          </AccordionPanel>
                        </AccordionItem>

                        <AccordionItem>
                          <AccordionButton>
                            <Box flex="1" textAlign="left">
                              <Badge colorScheme="orange" mr={2}>FR 3</Badge>
                              <Text as="span" fontWeight="bold">Macro Moderada</Text>
                            </Box>
                            <AccordionIcon />
                          </AccordionButton>
                          <AccordionPanel pb={4}>
                            <Text fontSize="sm">
                              Bioincrustação entre 4mm e 5mm. Não conforme com NORMAM 401.
                              Limpeza reativa urgente necessária (7-15 dias).
                            </Text>
                          </AccordionPanel>
                        </AccordionItem>

                        <AccordionItem>
                          <AccordionButton>
                            <Box flex="1" textAlign="left">
                              <Badge colorScheme="red" mr={2}>FR 4</Badge>
                              <Text as="span" fontWeight="bold">Macro Pesada (Crítico)</Text>
                            </Box>
                            <AccordionIcon />
                          </AccordionButton>
                          <AccordionPanel pb={4}>
                            <Text fontSize="sm">
                              Bioincrustação ≥ 5mm. CRÍTICO - Não conforme. Docagem a seco reativa urgente.
                              Notificar autoridades competentes.
                            </Text>
                          </AccordionPanel>
                        </AccordionItem>
                      </Accordion>
                    </Box>

                    <Divider />

                    <Box>
                      <Heading size="sm" mb={2}>Requisitos de Documentação</Heading>
                      <List spacing={2} fontSize="sm">
                        <ListItem>
                          <ListIcon as={CheckCircleIcon} color="green.500" />
                          Registro de todas as inspeções realizadas
                        </ListItem>
                        <ListItem>
                          <ListIcon as={CheckCircleIcon} color="green.500" />
                          Medições de espessura e rugosidade
                        </ListItem>
                        <ListItem>
                          <ListIcon as={CheckCircleIcon} color="green.500" />
                          Histórico de limpezas e métodos utilizados
                        </ListItem>
                        <ListItem>
                          <ListIcon as={CheckCircleIcon} color="green.500" />
                          Certificados de conformidade
                        </ListItem>
                        <ListItem>
                          <ListIcon as={CheckCircleIcon} color="green.500" />
                          Relatórios de não conformidade (quando aplicável)
                        </ListItem>
                      </List>
                    </Box>

                    <Alert status="info" borderRadius="md">
                      <AlertIcon />
                      <Box>
                        <AlertTitle>Referência Regulatória</AlertTitle>
                        <AlertDescription fontSize="sm">
                          Portaria DPC/DGN/MB nº 180, de 10 de junho de 2025 - Capítulo 3:
                          Sistemas Antiincrustantes Danosos. Para mais informações, consulte a
                          Diretoria de Portos e Costas (DPC).
                        </AlertDescription>
                      </Box>
                    </Alert>
                  </VStack>
                </CardBody>
              </Card>
            </VStack>
          </TabPanel>
        </TabPanels>
      </Tabs>

      {/* Modal de Análise Detalhada */}
      <Modal isOpen={isOpen} onClose={onClose} size="4xl" scrollBehavior="inside">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            Análise de Conformidade - {fleetStatus?.vessels.find(v => v.id === selectedVessel)?.name}
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {selectedVessel && fleetStatus ? (
              (() => {
                const vessel = fleetStatus.vessels.find(v => v.id === selectedVessel)
                if (!vessel) return <Alert status="error">Embarcação não encontrada</Alert>

                return (
                  <VStack spacing={6} align="stretch">
                    {/* Status Atual */}
                    <Card>
                      <CardBody>
                        <Heading size="sm" mb={4}>Status Atual de Conformidade</Heading>
                        <Grid templateColumns={{ base: '1fr', md: 'repeat(3, 1fr)' }} gap={4}>
                          <Stat>
                            <StatLabel>Nível FR</StatLabel>
                            <StatNumber>
                              <Badge colorScheme={
                                vessel.fr_level === 0 ? 'green' :
                                  vessel.fr_level === 1 ? 'blue' :
                                    vessel.fr_level === 2 ? 'yellow' :
                                      vessel.fr_level === 3 ? 'orange' : 'red'
                              } fontSize="lg" p={2}>
                                FR {vessel.fr_level} - {vessel.fr_label}
                              </Badge>
                            </StatNumber>
                          </Stat>
                          <Stat>
                            <StatLabel>Espessura</StatLabel>
                            <StatNumber fontSize="xl">
                              {vessel.fouling_mm.toFixed(2)} mm
                            </StatNumber>
                            <StatHelpText>
                              Limite: 5.0 mm
                            </StatHelpText>
                            <Progress
                              value={(vessel.fouling_mm / 5.0) * 100}
                              colorScheme={vessel.fouling_mm > 4.0 ? 'red' : vessel.fouling_mm > 3.0 ? 'yellow' : 'green'}
                              size="sm"
                              mt={2}
                            />
                          </Stat>
                          <Stat>
                            <StatLabel>Rugosidade</StatLabel>
                            <StatNumber fontSize="xl">
                              {vessel.roughness_um.toFixed(0)} μm
                            </StatNumber>
                            <StatHelpText>
                              Limite: 500 μm
                            </StatHelpText>
                            <Progress
                              value={(vessel.roughness_um / 500.0) * 100}
                              colorScheme={vessel.roughness_um > 400 ? 'red' : vessel.roughness_um > 300 ? 'yellow' : 'green'}
                              size="sm"
                              mt={2}
                            />
                          </Stat>
                        </Grid>
                      </CardBody>
                    </Card>

                    {/* Verificação de Conformidade */}
                    {complianceCheck ? (
                      <Card>
                        <CardBody>
                          <Heading size="sm" mb={4}>Verificação NORMAM 401</Heading>
                          <VStack align="stretch" spacing={4}>
                            <HStack justify="space-between">
                              <Text fontWeight="bold">Status:</Text>
                              <Badge colorScheme={getStatusColor(complianceCheck.status || 'unknown')} size="lg">
                                {getStatusLabel(complianceCheck.status || 'unknown')}
                              </Badge>
                            </HStack>
                            <HStack justify="space-between">
                              <Text fontWeight="bold">Score de Conformidade:</Text>
                              <Text fontSize="lg" fontWeight="bold">
                                {(complianceCheck.compliance_rate * 100).toFixed(1)}%
                              </Text>
                            </HStack>
                            <Progress
                              value={complianceCheck.compliance_rate * 100}
                              colorScheme={complianceCheck.compliance_rate >= 0.95 ? 'green' : complianceCheck.compliance_rate >= 0.8 ? 'yellow' : 'orange'}
                              size="lg"
                              borderRadius="md"
                            />
                            <HStack justify="space-between">
                              <Text fontWeight="bold">Próxima Inspeção:</Text>
                              <Text>
                                {complianceCheck.next_inspection_due ? new Date(complianceCheck.next_inspection_due).toLocaleDateString('pt-BR') : 'N/A'}
                              </Text>
                            </HStack>

                            {complianceCheck.violations.length > 0 && (
                              <Box>
                                <Text fontWeight="bold" mb={2} color="red.600">Violações:</Text>
                                <List spacing={2}>
                                  {complianceCheck.violations.map((violation: string, idx: number) => (
                                    <ListItem key={idx}>
                                      <ListIcon as={WarningIcon} color="red.500" />
                                      {violation}
                                    </ListItem>
                                  ))}
                                </List>
                              </Box>
                            )}

                            {complianceCheck.warnings && complianceCheck.warnings.length > 0 && (
                              <Box>
                                <Text fontWeight="bold" mb={2} color="orange.600">Avisos:</Text>
                                <List spacing={2}>
                                  {complianceCheck.warnings && complianceCheck.warnings.map((warning: string, idx: number) => (
                                    <ListItem key={idx}>
                                      <ListIcon as={WarningIcon} color="orange.500" />
                                      {warning}
                                    </ListItem>
                                  ))}
                                </List>
                              </Box>
                            )}

                            {complianceCheck.recommendations.length > 0 && (
                              <Box>
                                <Text fontWeight="bold" mb={2}>Recomendações:</Text>
                                <List spacing={2}>
                                  {complianceCheck.recommendations.map((rec: string, idx: number) => (
                                    <ListItem key={idx}>
                                      <ListIcon as={InfoIcon} color="blue.500" />
                                      {rec}
                                    </ListItem>
                                  ))}
                                </List>
                              </Box>
                            )}
                          </VStack>
                        </CardBody>
                      </Card>
                    ) : (
                      <Alert status="info">
                        <AlertIcon />
                        Carregando verificação de conformidade...
                      </Alert>
                    )}

                    {/* Predições de Risco */}
                    <Card>
                      <CardBody>
                        <Heading size="sm" mb={4}>Predições de Risco</Heading>
                        <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={4}>
                          <Box p={4} bg="blue.50" borderRadius="md">
                            <Text fontWeight="bold" mb={2}>Risco em 15 dias</Text>
                            <Badge
                              colorScheme={vessel.risk_15_days >= 3 ? 'red' : vessel.risk_15_days === 2 ? 'yellow' : 'green'}
                              fontSize="md"
                              p={2}
                            >
                              FR {vessel.risk_15_days}
                            </Badge>
                          </Box>
                          <Box p={4} bg="orange.50" borderRadius="md">
                            <Text fontWeight="bold" mb={2}>Risco em 30 dias</Text>
                            <Badge
                              colorScheme={vessel.risk_30_days >= 3 ? 'red' : vessel.risk_30_days === 2 ? 'yellow' : 'green'}
                              fontSize="md"
                              p={2}
                            >
                              FR {vessel.risk_30_days}
                            </Badge>
                          </Box>
                        </Grid>
                      </CardBody>
                    </Card>

                    {/* Ações Corretivas */}
                    {actionsLoading ? (
                      <Center py={4}>
                        <Spinner />
                      </Center>
                    ) : correctiveActions && correctiveActions.length > 0 ? (
                      <Card>
                        <CardBody>
                          <Heading size="sm" mb={4}>Ações Corretivas Recomendadas</Heading>
                          <VStack align="stretch" spacing={4}>
                            {correctiveActions.map((action) => (
                              <Box key={action.action_id} p={4} borderWidth={1} borderRadius="md">
                                <HStack justify="space-between" mb={2}>
                                  <Heading size="xs">{action.title}</Heading>
                                  <Badge colorScheme={getPriorityColor(action.priority)}>
                                    {getPriorityLabel(action.priority)}
                                  </Badge>
                                </HStack>
                                <Text fontSize="sm" color="gray.600" mb={3}>
                                  {action.description}
                                </Text>
                                <VStack align="stretch" spacing={1} fontSize="xs">
                                  <HStack justify="space-between">
                                    <Text fontWeight="bold">Prazo:</Text>
                                    <Text>{new Date(action.deadline).toLocaleDateString('pt-BR')}</Text>
                                  </HStack>
                                  <HStack justify="space-between">
                                    <Text fontWeight="bold">Custo:</Text>
                                    <Text>
                                      {action.estimated_cost_brl.toLocaleString('pt-BR', {
                                        style: 'currency',
                                        currency: 'BRL'
                                      })}
                                    </Text>
                                  </HStack>
                                  <HStack justify="space-between">
                                    <Text fontWeight="bold">Duração:</Text>
                                    <Text>{action.estimated_duration_hours.toFixed(0)} horas</Text>
                                  </HStack>
                                </VStack>
                                {action.steps && action.steps.length > 0 && (
                                  <Box mt={3}>
                                    <Text fontWeight="bold" mb={2} fontSize="xs">Passos:</Text>
                                    <List spacing={1}>
                                      {action.steps.map((step, index) => (
                                        <ListItem key={index} fontSize="xs">
                                          <ListIcon as={CheckCircleIcon} color="green.500" />
                                          {step}
                                        </ListItem>
                                      ))}
                                    </List>
                                  </Box>
                                )}
                              </Box>
                            ))}
                          </VStack>
                        </CardBody>
                      </Card>
                    ) : (
                      <Alert status="success">
                        <AlertIcon />
                        Nenhuma ação corretiva necessária no momento. Embarcação em conformidade.
                      </Alert>
                    )}

                    {/* Informações Adicionais */}
                    <Card>
                      <CardBody>
                        <Heading size="sm" mb={4}>Informações Adicionais</Heading>
                        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4} fontSize="sm">
                          <Box>
                            <Text color="gray.600">Última Limpeza:</Text>
                            <Text fontWeight="bold">
                              {vessel.last_cleaning_date
                                ? new Date(vessel.last_cleaning_date).toLocaleDateString('pt-BR')
                                : 'N/A'}
                            </Text>
                          </Box>
                          <Box>
                            <Text color="gray.600">Última Pintura:</Text>
                            <Text fontWeight="bold">
                              {vessel.last_painting_date
                                ? new Date(vessel.last_painting_date).toLocaleDateString('pt-BR')
                                : 'N/A'}
                            </Text>
                          </Box>
                          <Box>
                            <Text color="gray.600">Calibração Sensor:</Text>
                            <Text fontWeight="bold">
                              {vessel.sensor_calibration_date
                                ? new Date(vessel.sensor_calibration_date).toLocaleDateString('pt-BR')
                                : 'N/A'}
                            </Text>
                          </Box>
                          <Box>
                            <Text color="gray.600">Perda de Performance:</Text>
                            <Text fontWeight="bold" color="red.600">
                              {vessel.performance_loss_percent.toFixed(1)}%
                            </Text>
                          </Box>
                        </SimpleGrid>
                      </CardBody>
                    </Card>
                  </VStack>
                )
              })()
            ) : (
              <Center py={8}>
                <Spinner />
              </Center>
            )}
          </ModalBody>
          <ModalFooter>
            <Button colorScheme="blue" mr={3} onClick={() => selectedVessel && handleViewVessel(selectedVessel)}>
              Ver Detalhes Completos
            </Button>
            <Button variant="ghost" onClick={onClose}>
              Fechar
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </VStack>
  )
}

export default Compliance
