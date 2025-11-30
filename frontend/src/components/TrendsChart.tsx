import { Card, CardBody, Heading, Select, HStack, Box, Checkbox, VStack, Text, Spinner } from '@chakra-ui/react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { useState } from 'react'

interface TrendDataPoint {
  month: string
  economy_brl: number
  co2_tonnes: number
  compliance_rate_percent: number
  avg_fouling_mm: number
  avg_roughness_um: number
  monitored_vessels: number
  maintenance_events: number
}

interface TrendsChartProps {
  data: TrendDataPoint[]
  isLoading?: boolean
  period?: string
  onPeriodChange?: (period: string) => void
}

const COLORS = {
  economy: '#0066CC',
  co2: '#00A859',
  compliance: '#9C27B0',
  fouling: '#FF9800',
  roughness: '#F44336',
  vessels: '#2196F3',
  maintenance: '#795548'
}

export default function TrendsChart({ 
  data, 
  isLoading = false,
  period = '6_months',
  onPeriodChange 
}: TrendsChartProps) {
  const [selectedPeriod, setSelectedPeriod] = useState(period)
  const [visibleMetrics, setVisibleMetrics] = useState({
    economy: true,
    co2: true,
    compliance: false,
    fouling: false,
    roughness: false,
    vessels: false,
    maintenance: false
  })

  const handlePeriodChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newPeriod = e.target.value
    setSelectedPeriod(newPeriod)
    onPeriodChange?.(newPeriod)
  }

  const toggleMetric = (metric: keyof typeof visibleMetrics) => {
    setVisibleMetrics(prev => ({
      ...prev,
      [metric]: !prev[metric]
    }))
  }

  // Transformar dados para o formato do gráfico
  const chartData = data && Array.isArray(data) && data.length > 0 ? data.map(item => {
    if (!item) return null
    return {
      month: item.month || '',
      economy: (item.economy_brl || 0) / 1000000, // Converter para milhões
      co2: item.co2_tonnes || 0,
      compliance: item.compliance_rate_percent || 0,
      fouling: item.avg_fouling_mm || 0,
      roughness: (item.avg_roughness_um || 0) / 100, // Converter para mm para visualização
      vessels: item.monitored_vessels || 0,
      maintenance: item.maintenance_events || 0
    }
  }).filter(item => item !== null) : []

  // Contar quantas métricas estão visíveis
  const visibleCount = Object.values(visibleMetrics).filter(v => v).length

  return (
    <Card>
      <CardBody>
        <HStack justify="space-between" mb={4} flexWrap="wrap" gap={4}>
          <Heading size="md">Tendências</Heading>
          <HStack>
            <Select 
              value={selectedPeriod} 
              onChange={handlePeriodChange}
              width="200px"
              size="sm"
            >
              <option value="1_month">1 Mês</option>
              <option value="3_months">3 Meses</option>
              <option value="6_months">6 Meses</option>
              <option value="12_months">12 Meses</option>
            </Select>
          </HStack>
        </HStack>

        {/* Seletor de Métricas */}
        <Box mb={4} p={4} bg="gray.50" borderRadius="md">
          <Text fontSize="sm" fontWeight="bold" mb={2}>Métricas Visíveis:</Text>
          <HStack spacing={4} flexWrap="wrap">
            <Checkbox
              isChecked={visibleMetrics.economy}
              onChange={() => toggleMetric('economy')}
              colorScheme="blue"
            >
              <Text fontSize="sm">Economia (R$ M)</Text>
            </Checkbox>
            <Checkbox
              isChecked={visibleMetrics.co2}
              onChange={() => toggleMetric('co2')}
              colorScheme="teal"
            >
              <Text fontSize="sm">CO₂ (t)</Text>
            </Checkbox>
            <Checkbox
              isChecked={visibleMetrics.compliance}
              onChange={() => toggleMetric('compliance')}
              colorScheme="purple"
            >
              <Text fontSize="sm">Conformidade (%)</Text>
            </Checkbox>
            <Checkbox
              isChecked={visibleMetrics.fouling}
              onChange={() => toggleMetric('fouling')}
              colorScheme="orange"
            >
              <Text fontSize="sm">Bioincrustação Média (mm)</Text>
            </Checkbox>
            <Checkbox
              isChecked={visibleMetrics.roughness}
              onChange={() => toggleMetric('roughness')}
              colorScheme="red"
            >
              <Text fontSize="sm">Rugosidade Média (mm)</Text>
            </Checkbox>
            <Checkbox
              isChecked={visibleMetrics.vessels}
              onChange={() => toggleMetric('vessels')}
              colorScheme="cyan"
            >
              <Text fontSize="sm">Embarcações Monitoradas</Text>
            </Checkbox>
            <Checkbox
              isChecked={visibleMetrics.maintenance}
              onChange={() => toggleMetric('maintenance')}
              colorScheme="brown"
              sx={{
                ...(visibleMetrics.maintenance && visibleCount === 1 && {
                  '& .chakra-checkbox__control': {
                    transform: 'scale(1.2)',
                    boxShadow: '0 0 0 3px rgba(121, 85, 72, 0.2)',
                  },
                  '& .chakra-checkbox__label': {
                    fontWeight: 'bold',
                    color: COLORS.maintenance,
                  }
                })
              }}
            >
              <Text fontSize="sm" fontWeight={visibleMetrics.maintenance && visibleCount === 1 ? 'bold' : 'normal'}>
                Eventos de Manutenção
              </Text>
            </Checkbox>
          </HStack>
        </Box>
        
        {isLoading ? (
          <Box height="400px" display="flex" alignItems="center" justifyContent="center">
            <Spinner size="xl" />
          </Box>
        ) : !chartData || chartData.length === 0 ? (
          <Box height="400px" display="flex" alignItems="center" justifyContent="center">
            <VStack>
              <Text color="gray.500" fontSize="lg">Nenhum dado disponível</Text>
              <Text color="gray.400" fontSize="sm">Os dados de tendências ainda não foram gerados</Text>
              <Text color="gray.400" fontSize="xs" mt={2}>
                Dados recebidos: {data ? data.length : 0} pontos
              </Text>
            </VStack>
          </Box>
        ) : visibleCount === 0 ? (
          <Box height="400px" display="flex" alignItems="center" justifyContent="center">
            <Text color="gray.500">Selecione pelo menos uma métrica para visualizar</Text>
          </Box>
        ) : (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="month" 
                tick={{ fontSize: 12 }}
                interval={0}
              />
              
              {/* Eixo Y esquerdo - Valores monetários e percentuais */}
              {(visibleMetrics.economy || visibleMetrics.compliance) && (
                <YAxis 
                  yAxisId="left" 
                  label={{ 
                    value: visibleMetrics.economy ? 'Economia (R$ M)' : 'Conformidade (%)', 
                    angle: -90, 
                    position: 'insideLeft' 
                  }} 
                />
              )}
              
              {/* Eixo Y direito - CO₂ e outras métricas */}
              {(visibleMetrics.co2 || visibleMetrics.fouling || visibleMetrics.roughness) && (
                <YAxis 
                  yAxisId="right" 
                  orientation="right" 
                  label={{ 
                    value: visibleMetrics.co2 ? 'CO₂ (t)' : 'Outras Métricas', 
                    angle: 90, 
                    position: 'insideRight' 
                  }} 
                />
              )}
              
              {/* Eixo Y terceiro - Contadores */}
              {(visibleMetrics.vessels || visibleMetrics.maintenance) && (
                <YAxis 
                  yAxisId="count" 
                  orientation="right" 
                  label={{ 
                    value: 'Contadores', 
                    angle: 90, 
                    position: 'insideRight',
                    offset: 60
                  }} 
                />
              )}
              
              <Tooltip 
                formatter={(value: number, name: string) => {
                  if (name === 'economy') {
                    return [`R$ ${value.toFixed(2)}M`, 'Economia']
                  }
                  if (name === 'co2') {
                    return [`${value.toFixed(0)} t`, 'CO₂']
                  }
                  if (name === 'compliance') {
                    return [`${value.toFixed(1)}%`, 'Conformidade']
                  }
                  if (name === 'fouling') {
                    return [`${value.toFixed(2)} mm`, 'Bioincrustação Média']
                  }
                  if (name === 'roughness') {
                    return [`${value.toFixed(2)} mm`, 'Rugosidade Média']
                  }
                  if (name === 'vessels') {
                    return [`${value}`, 'Embarcações']
                  }
                  if (name === 'maintenance') {
                    return [`${value}`, 'Eventos de Manutenção']
                  }
                  return [value, name]
                }}
              />
              <Legend />
              
              {visibleMetrics.economy && (
                <Line 
                  yAxisId="left" 
                  type="monotone" 
                  dataKey="economy" 
                  stroke={COLORS.economy} 
                  name="Economia (R$ M)"
                  strokeWidth={visibleCount === 1 ? 4 : 2}
                  dot={{ r: visibleCount === 1 ? 6 : 4 }}
                  activeDot={{ r: visibleCount === 1 ? 8 : 6 }}
                />
              )}
              
              {visibleMetrics.co2 && (
                <Line 
                  yAxisId="right" 
                  type="monotone" 
                  dataKey="co2" 
                  stroke={COLORS.co2} 
                  name="CO₂ (t)"
                  strokeWidth={visibleCount === 1 ? 4 : 2}
                  dot={{ r: visibleCount === 1 ? 6 : 4 }}
                  activeDot={{ r: visibleCount === 1 ? 8 : 6 }}
                />
              )}
              
              {visibleMetrics.compliance && (
                <Line 
                  yAxisId="left" 
                  type="monotone" 
                  dataKey="compliance" 
                  stroke={COLORS.compliance} 
                  name="Conformidade (%)"
                  strokeWidth={visibleCount === 1 ? 4 : 2}
                  dot={{ r: visibleCount === 1 ? 6 : 4 }}
                  activeDot={{ r: visibleCount === 1 ? 8 : 6 }}
                />
              )}
              
              {visibleMetrics.fouling && (
                <Line 
                  yAxisId="right" 
                  type="monotone" 
                  dataKey="fouling" 
                  stroke={COLORS.fouling} 
                  name="Bioincrustação Média (mm)"
                  strokeWidth={visibleCount === 1 ? 4 : 2}
                  dot={{ r: visibleCount === 1 ? 6 : 4 }}
                  activeDot={{ r: visibleCount === 1 ? 8 : 6 }}
                />
              )}
              
              {visibleMetrics.roughness && (
                <Line 
                  yAxisId="right" 
                  type="monotone" 
                  dataKey="roughness" 
                  stroke={COLORS.roughness} 
                  name="Rugosidade Média (mm)"
                  strokeWidth={visibleCount === 1 ? 4 : 2}
                  dot={{ r: visibleCount === 1 ? 6 : 4 }}
                  activeDot={{ r: visibleCount === 1 ? 8 : 6 }}
                />
              )}
              
              {visibleMetrics.vessels && (
                <Line 
                  yAxisId="count" 
                  type="monotone" 
                  dataKey="vessels" 
                  stroke={COLORS.vessels} 
                  name="Embarcações Monitoradas"
                  strokeWidth={visibleCount === 1 ? 4 : 2}
                  dot={{ r: visibleCount === 1 ? 6 : 4 }}
                  activeDot={{ r: visibleCount === 1 ? 8 : 6 }}
                />
              )}
              
              {visibleMetrics.maintenance && (
                <Line 
                  yAxisId="count" 
                  type="monotone" 
                  dataKey="maintenance" 
                  stroke={COLORS.maintenance} 
                  name="Eventos de Manutenção"
                  strokeWidth={visibleCount === 1 ? 4 : 2}
                  dot={{ r: visibleCount === 1 ? 6 : 4 }}
                  activeDot={{ r: visibleCount === 1 ? 8 : 6 }}
                  strokeDasharray={visibleCount === 1 ? undefined : "0"}
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        )}
      </CardBody>
    </Card>
  )
}
