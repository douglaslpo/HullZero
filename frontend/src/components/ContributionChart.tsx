import { Box, VStack, Text, HStack } from '@chakra-ui/react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

interface FeatureContribution {
  feature_name: string
  contribution: number
  percentage: number
  description: string
}

interface ContributionChartProps {
  contributions: FeatureContribution[]
  title?: string
}

export default function ContributionChart({ contributions, title = 'Contribuições' }: ContributionChartProps) {
  // Ordenar por contribuição absoluta e pegar top 10
  const sortedContributions = [...contributions]
    .sort((a, b) => Math.abs(b.contribution) - Math.abs(a.contribution))
    .slice(0, 10)

  const chartData = sortedContributions.map(contrib => ({
    name: contrib.feature_name.length > 20 
      ? contrib.feature_name.substring(0, 20) + '...' 
      : contrib.feature_name,
    fullName: contrib.feature_name,
    contribution: contrib.contribution,
    percentage: contrib.percentage,
    description: contrib.description
  }))

  const getColor = (value: number) => {
    if (value > 0) return '#00A859' // Verde para positivo
    if (value < 0) return '#F44336' // Vermelho para negativo
    return '#9E9E9E' // Cinza para neutro
  }

  return (
    <VStack align="stretch" spacing={4}>
      {title && (
        <Text fontSize="lg" fontWeight="bold">
          {title}
        </Text>
      )}
      
      <ResponsiveContainer width="100%" height={Math.max(300, sortedContributions.length * 40)}>
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 150, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            type="number" 
            domain={[-1, 1]}
            label={{ value: 'Contribuição', position: 'insideBottom', offset: -5 }}
          />
          <YAxis 
            type="category" 
            dataKey="name" 
            width={140}
            tick={{ fontSize: 12 }}
          />
          <Tooltip
            formatter={(value: number) => `${(value * 100).toFixed(1)}%`}
            contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.95)' }}
            labelFormatter={(label, payload) => {
              if (payload && payload[0]) {
                return payload[0].payload.fullName
              }
              return label
            }}
          />
          <Bar dataKey="contribution" radius={[0, 4, 4, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getColor(entry.contribution)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      <Box>
        <Text fontSize="sm" color="gray.600" mb={2}>Legenda:</Text>
        <HStack spacing={4}>
          <HStack>
            <Box w={4} h={4} bg="#00A859" borderRadius="sm" />
            <Text fontSize="xs">Aumenta o valor</Text>
          </HStack>
          <HStack>
            <Box w={4} h={4} bg="#F44336" borderRadius="sm" />
            <Text fontSize="xs">Reduz o valor</Text>
          </HStack>
        </HStack>
      </Box>
    </VStack>
  )
}

