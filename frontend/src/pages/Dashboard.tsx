import { useState } from 'react'
import {
  Box,
  Grid,
  Heading,
  Text,
  VStack,
  Alert,
  AlertIcon,
  Spinner,
  Center,
} from '@chakra-ui/react'
import { useQuery } from '@tanstack/react-query'
import { dashboardService } from '../api/services'
import KPICard from '../components/KPICard'
import TrendsChart from '../components/TrendsChart'
import VesselCard from '../components/VesselCard'

// Interfaces importadas de services.ts
import type { DashboardKPIs, Trends, FleetStatus } from '../api/services'

function Dashboard() {
  const [selectedPeriod, setSelectedPeriod] = useState('6_months')

  // Buscar KPIs
  const { data: kpis, isLoading: kpisLoading, error: kpisError } = useQuery<DashboardKPIs>({
    queryKey: ['dashboard-kpis', selectedPeriod],
    queryFn: async () => {
      return await dashboardService.getKPIs(selectedPeriod)
    },
    refetchInterval: 30000, // Atualizar a cada 30 segundos
    retry: 2, // Tentar 2 vezes antes de falhar
    retryDelay: 1000, // Esperar 1s entre tentativas
  })

  // Buscar tendências
  const { data: trends, isLoading: trendsLoading, error: trendsError } = useQuery<Trends>({
    queryKey: ['dashboard-trends', selectedPeriod],
    queryFn: async () => {
      return await dashboardService.getTrends(selectedPeriod)
    },
    retry: 2,
    retryDelay: 1000,
  })

  // Buscar status da frota
  const { data: fleetStatus, isLoading: fleetLoading, error: fleetError } = useQuery<FleetStatus>({
    queryKey: ['fleet-status'],
    queryFn: async () => {
      return await dashboardService.getFleetStatus()
    },
    refetchInterval: 60000, // Atualizar a cada minuto
    retry: 2,
    retryDelay: 1000,
  })

  const formatCO2Comparison = (co2Tonnes: number) => {
    const cars = Math.round(co2Tonnes / 4.6)
    return `Equivale a ${cars} carros`
  }

  return (
    <VStack spacing={6} align="stretch">
      <Box>
        <Heading size="xl" mb={2}>Dashboard da Frota</Heading>
        <Text color="gray.600">Visão consolidada de todas as embarcações</Text>
      </Box>

      {/* KPIs */}
      <Grid templateColumns={{ base: '1fr', md: 'repeat(4, 1fr)' }} gap={4}>
        <KPICard
          label="Economia Acumulada"
          value={kpis?.accumulated_economy_brl || 0}
          helpText={`Últimos ${selectedPeriod.replace('_', ' ')}`}
          isLoading={kpisLoading}
          colorScheme="green"
        />
        <KPICard
          label="Redução de CO₂"
          value={`${kpis?.co2_reduction_tonnes.toFixed(0) || 0} t`}
          helpText={kpis ? formatCO2Comparison(kpis.co2_reduction_tonnes) : ''}
          isLoading={kpisLoading}
          colorScheme="teal"
        />
        <KPICard
          label="Taxa de Conformidade"
          value={`${kpis?.compliance_rate_percent.toFixed(0) || 0}%`}
          helpText="NORMAM 401"
          isLoading={kpisLoading}
          colorScheme={kpis && kpis.compliance_rate_percent >= 95 ? 'green' : kpis && kpis.compliance_rate_percent >= 80 ? 'yellow' : 'orange'}
        />
        <KPICard
          label="Embarcações"
          value={`${kpis?.monitored_vessels || 0}`}
          helpText="Monitoradas"
          isLoading={kpisLoading}
          colorScheme="blue"
        />
      </Grid>

      {/* Erros */}
      {(kpisError || trendsError || fleetError) && (
        <Alert status="error">
          <AlertIcon />
          Erro ao carregar dados do dashboard. Tente novamente.
        </Alert>
      )}

      {/* Gráfico de Tendências */}
      {trendsError && (
        <Alert status="warning" mb={4}>
          <AlertIcon />
          Erro ao carregar dados de tendências. Verifique se o backend está rodando.
        </Alert>
      )}
      <TrendsChart
        data={trends?.data || []}
        isLoading={trendsLoading}
        period={selectedPeriod}
        onPeriodChange={setSelectedPeriod}
      />

      {/* Status da Frota */}
      <Box>
        <Heading size="md" mb={4}>Status da Frota</Heading>
        {fleetLoading ? (
          <Center py={8}>
            <Spinner size="xl" />
          </Center>
        ) : fleetStatus && fleetStatus.vessels.length > 0 ? (
          <Grid templateColumns={{ base: '1fr', md: 'repeat(3, 1fr)' }} gap={4}>
            {fleetStatus.vessels.map((vessel) => (
              <VesselCard
                key={vessel.id}
                id={vessel.id}
                name={vessel.name}
                status={vessel.status}
                fouling_mm={vessel.fouling_mm}
                roughness_um={vessel.roughness_um}
                compliance_status={vessel.compliance_status}
                last_update={vessel.last_update}
              />
            ))}
          </Grid>
        ) : (
          <Alert status="info">
            <AlertIcon />
            Nenhuma embarcação encontrada.
          </Alert>
        )}
      </Box>
    </VStack>
  )
}

export default Dashboard

