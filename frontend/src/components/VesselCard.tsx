import { 
  Card, 
  CardBody, 
  VStack, 
  HStack, 
  Heading, 
  Text, 
  Badge, 
  Button,
  Progress,
  Box
} from '@chakra-ui/react'
import { Link } from 'react-router-dom'

interface VesselCardProps {
  id: string
  name: string
  status: string
  fouling_mm: number
  roughness_um: number
  compliance_status?: string
  last_update?: string
}

export default function VesselCard({
  id,
  name,
  status,
  fouling_mm,
  roughness_um,
  compliance_status,
  last_update
}: VesselCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'low': return 'green'
      case 'moderate': return 'yellow'
      case 'high': return 'orange'
      case 'critical': return 'red'
      default: return 'gray'
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'low': return 'Baixa'
      case 'moderate': return 'Moderada'
      case 'high': return 'Alta'
      case 'critical': return 'Crítica'
      default: return 'Desconhecido'
    }
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

  // Calcular porcentagem de bioincrustação (baseado no limite de 5mm)
  const foulingPercentage = Math.min(100, (fouling_mm / 5.0) * 100)

  return (
    <Card 
      as={Link} 
      to={`/vessel/${id}`}
      _hover={{ transform: 'translateY(-4px)', boxShadow: 'lg' }} 
      transition="all 0.2s"
      height="100%"
    >
      <CardBody>
        <VStack align="stretch" spacing={3}>
          <HStack justify="space-between">
            <Heading size="sm">{name}</Heading>
            <Badge colorScheme={getStatusColor(status)}>
              {getStatusLabel(status)}
            </Badge>
          </HStack>

          {compliance_status && (
            <HStack>
              <Text fontSize="xs" color="gray.600">Conformidade:</Text>
              <Badge colorScheme={getComplianceColor(compliance_status)} size="sm">
                {getComplianceLabel(compliance_status)}
              </Badge>
            </HStack>
          )}

          <Box>
            <HStack justify="space-between" mb={1}>
              <Text fontSize="sm" color="gray.600">Bioincrustação:</Text>
              <Text fontWeight="bold">{fouling_mm.toFixed(1)} mm</Text>
            </HStack>
            <Progress 
              value={foulingPercentage} 
              colorScheme={foulingPercentage > 80 ? 'red' : foulingPercentage > 60 ? 'orange' : 'green'}
              size="sm"
              borderRadius="md"
            />
            <Text fontSize="xs" color="gray.500" mt={1}>
              Limite: 5.0 mm
            </Text>
          </Box>

          <HStack justify="space-between">
            <Text fontSize="sm" color="gray.600">Rugosidade:</Text>
            <Text fontWeight="bold">{roughness_um.toFixed(0)} μm</Text>
          </HStack>

          {last_update && (
            <Text fontSize="xs" color="gray.500">
              Atualizado: {new Date(last_update).toLocaleDateString('pt-BR')}
            </Text>
          )}

          <Button size="sm" colorScheme="blue" mt={2} width="100%">
            Ver Detalhes
          </Button>
        </VStack>
      </CardBody>
    </Card>
  )
}

