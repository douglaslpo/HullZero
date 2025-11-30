import { Card, CardBody, Stat, StatLabel, StatNumber, StatHelpText, Skeleton, Box } from '@chakra-ui/react'
import { useMemo } from 'react'

interface KPICardProps {
  label: string
  value: string | number
  helpText?: string
  isLoading?: boolean
  colorScheme?: string  // Usado para determinar cor do badge/estilo, não removido
  icon?: React.ReactNode
}

export default function KPICard({ 
  label, 
  value, 
  helpText, 
  isLoading = false,
  colorScheme: _colorScheme = 'blue',  // Mantido na interface para compatibilidade, mas não usado no componente
  icon 
}: KPICardProps) {
  const formattedValue = useMemo(() => {
    if (typeof value === 'number') {
      if (value >= 1000000) {
        return `R$ ${(value / 1000000).toFixed(1)}M`
      } else if (value >= 1000) {
        return `R$ ${(value / 1000).toFixed(1)}k`
      } else if (value < 1 && value > 0) {
        return `${(value * 100).toFixed(1)}%`
      } else {
        return value.toLocaleString('pt-BR', { 
          style: 'currency', 
          currency: 'BRL',
          maximumFractionDigits: 0
        })
      }
    }
    return value
  }, [value])

  return (
    <Card>
      <CardBody>
        <Skeleton isLoaded={!isLoading}>
          <Stat>
            {icon && (
              <Box mb={2}>
                {icon}
              </Box>
            )}
            <StatLabel>{label}</StatLabel>
            <StatNumber fontSize="2xl">
              {formattedValue}
            </StatNumber>
            {helpText && <StatHelpText>{helpText}</StatHelpText>}
          </Stat>
        </Skeleton>
      </CardBody>
    </Card>
  )
}

