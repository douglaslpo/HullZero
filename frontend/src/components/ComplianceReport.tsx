
import {
  Box,
  VStack,
  HStack,
  Heading,
  Text,
  Divider,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Card,
  CardBody,
  List,
  ListItem,
  ListIcon,
  Progress,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
} from '@chakra-ui/react'
import { CheckCircleIcon, WarningIcon, InfoIcon } from '@chakra-ui/icons'
import { FleetDetailedStatus } from '../api/services'

interface ComplianceReportProps {
  fleetStatus: FleetDetailedStatus
  title?: string
  generatedDate?: string
  showPrintButton?: boolean
}

function ComplianceReport({
  fleetStatus,
  title = 'Relatório de Conformidade NORMAM 401',
  generatedDate,
  showPrintButton = false,
}: ComplianceReportProps) {
  const generatedAt = generatedDate || new Date().toLocaleString('pt-BR')

  // Calcular estatísticas
  const stats = {
    total: fleetStatus.vessels.length,
    compliant: fleetStatus.vessels.filter(v => v.fr_level <= 1).length,
    atRisk: fleetStatus.vessels.filter(v => v.fr_level === 2).length,
    nonCompliant: fleetStatus.vessels.filter(v => v.fr_level >= 3).length,
    complianceRate: (fleetStatus.vessels.filter(v => v.fr_level <= 1).length /
      fleetStatus.vessels.length) * 100,
    avgFouling: fleetStatus.vessels.reduce((sum, v) => sum + v.fouling_mm, 0) / fleetStatus.vessels.length,
    avgRoughness: fleetStatus.vessels.reduce((sum, v) => sum + v.roughness_um, 0) / fleetStatus.vessels.length,
    avgPerformanceLoss: fleetStatus.vessels.reduce((sum, v) => sum + v.performance_loss_percent, 0) / fleetStatus.vessels.length,
  }

  const getStatusColor = (frLevel: number) => {
    if (frLevel <= 1) return 'green'
    if (frLevel === 2) return 'yellow'
    if (frLevel === 3) return 'orange'
    return 'red'
  }

  const getStatusLabel = (frLevel: number) => {
    const labels = ['Sem Incrustação', 'Micro', 'Macro Leve', 'Macro Moderada', 'Macro Pesada']
    return labels[frLevel] || 'Desconhecido'
  }

  const getPriorityColor = (frLevel: number) => {
    if (frLevel <= 1) return 'success'
    if (frLevel === 2) return 'warning'
    if (frLevel === 3) return 'error'
    return 'error'
  }

  return (
    <Box
      p={8}
      bg="white"
      color="gray.800"
      minH="100vh"
      maxW="1200px"
      mx="auto"
      id="compliance-report"
    >
      {/* Cabeçalho */}
      <VStack spacing={4} align="stretch" mb={8}>
        <HStack justify="space-between" align="start">
          <VStack align="start" spacing={2}>
            <Heading size="xl" color="blue.600">
              {title}
            </Heading>
            <Text fontSize="sm" color="gray.600">
              Gerado em: {generatedAt}
            </Text>
            <Text fontSize="sm" color="gray.600">
              Transpetro - Sistema HullZero
            </Text>
          </VStack>
          {showPrintButton && (
            <Box>
              <button
                onClick={() => window.print()}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#3182CE',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                }}
              >
                Imprimir / Salvar PDF
              </button>
            </Box>
          )}
        </HStack>
        <Divider />
      </VStack>

      {/* Resumo Executivo */}
      <Card mb={6} boxShadow="md">
        <CardBody>
          <Heading size="md" mb={4} color="blue.700">
            Resumo Executivo
          </Heading>
          <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
            <Stat>
              <StatLabel>Total de Embarcações</StatLabel>
              <StatNumber>{stats.total}</StatNumber>
            </Stat>
            <Stat>
              <StatLabel>Taxa de Conformidade</StatLabel>
              <StatNumber>{stats.complianceRate.toFixed(1)}%</StatNumber>
              <StatHelpText>
                {stats.compliant} conforme(s) de {stats.total}
              </StatHelpText>
            </Stat>
            <Stat>
              <StatLabel>Em Risco</StatLabel>
              <StatNumber color="orange.500">{stats.atRisk}</StatNumber>
            </Stat>
            <Stat>
              <StatLabel>Não Conformes</StatLabel>
              <StatNumber color="red.500">{stats.nonCompliant}</StatNumber>
            </Stat>
          </SimpleGrid>
        </CardBody>
      </Card>

      {/* Métricas Médias */}
      <Card mb={6} boxShadow="md">
        <CardBody>
          <Heading size="md" mb={4} color="blue.700">
            Métricas Médias da Frota
          </Heading>
          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
            <Stat>
              <StatLabel>Espessura Média (mm)</StatLabel>
              <StatNumber>{stats.avgFouling.toFixed(2)}</StatNumber>
              <StatHelpText>
                Limite NORMAM: 5.0 mm
              </StatHelpText>
            </Stat>
            <Stat>
              <StatLabel>Rugosidade Média (μm)</StatLabel>
              <StatNumber>{stats.avgRoughness.toFixed(1)}</StatNumber>
              <StatHelpText>
                Limite NORMAM: 500 μm
              </StatHelpText>
            </Stat>
            <Stat>
              <StatLabel>Perda de Performance</StatLabel>
              <StatNumber>{stats.avgPerformanceLoss.toFixed(1)}%</StatNumber>
              <StatHelpText>
                Impacto médio no consumo
              </StatHelpText>
            </Stat>
          </SimpleGrid>
        </CardBody>
      </Card>

      {/* Distribuição de Status */}
      <Card mb={6} boxShadow="md">
        <CardBody>
          <Heading size="md" mb={4} color="blue.700">
            Distribuição de Status de Conformidade
          </Heading>
          <VStack spacing={3} align="stretch">
            <HStack>
              <Badge colorScheme="green" fontSize="md" px={3} py={1}>
                Conforme (FR 0-1)
              </Badge>
              <Text flex={1}>{stats.compliant} embarcações</Text>
              <Progress
                value={(stats.compliant / stats.total) * 100}
                colorScheme="green"
                flex={2}
                size="lg"
              />
              <Text fontWeight="bold" minW="60px" textAlign="right">
                {((stats.compliant / stats.total) * 100).toFixed(1)}%
              </Text>
            </HStack>
            <HStack>
              <Badge colorScheme="yellow" fontSize="md" px={3} py={1}>
                Em Risco (FR 2)
              </Badge>
              <Text flex={1}>{stats.atRisk} embarcações</Text>
              <Progress
                value={(stats.atRisk / stats.total) * 100}
                colorScheme="yellow"
                flex={2}
                size="lg"
              />
              <Text fontWeight="bold" minW="60px" textAlign="right">
                {((stats.atRisk / stats.total) * 100).toFixed(1)}%
              </Text>
            </HStack>
            <HStack>
              <Badge colorScheme="red" fontSize="md" px={3} py={1}>
                Não Conforme (FR 3-4)
              </Badge>
              <Text flex={1}>{stats.nonCompliant} embarcações</Text>
              <Progress
                value={(stats.nonCompliant / stats.total) * 100}
                colorScheme="red"
                flex={2}
                size="lg"
              />
              <Text fontWeight="bold" minW="60px" textAlign="right">
                {((stats.nonCompliant / stats.total) * 100).toFixed(1)}%
              </Text>
            </HStack>
          </VStack>
        </CardBody>
      </Card>

      {/* Tabela Detalhada */}
      <Card mb={6} boxShadow="md">
        <CardBody>
          <Heading size="md" mb={4} color="blue.700">
            Status Detalhado por Embarcação
          </Heading>
          <Box overflowX="auto">
            <Table variant="simple" size="sm">
              <Thead>
                <Tr>
                  <Th>Embarcação</Th>
                  <Th>Classe</Th>
                  <Th>FR</Th>
                  <Th>Espessura (mm)</Th>
                  <Th>Rugosidade (μm)</Th>
                  <Th>Perda (%)</Th>
                  <Th>Última Limpeza</Th>
                  <Th>Status</Th>
                </Tr>
              </Thead>
              <Tbody>
                {fleetStatus.vessels.map((vessel) => (
                  <Tr key={vessel.id}>
                    <Td fontWeight="medium">{vessel.name}</Td>
                    <Td>{vessel.vessel_class}</Td>
                    <Td>
                      <Badge colorScheme={getStatusColor(vessel.fr_level)}>
                        {vessel.fr_level} - {getStatusLabel(vessel.fr_level)}
                      </Badge>
                    </Td>
                    <Td>{vessel.fouling_mm.toFixed(2)}</Td>
                    <Td>{vessel.roughness_um.toFixed(1)}</Td>
                    <Td>{vessel.performance_loss_percent.toFixed(1)}%</Td>
                    <Td>{vessel.last_cleaning_date || 'N/A'}</Td>
                    <Td>
                      <Badge
                        colorScheme={getPriorityColor(vessel.fr_level)}
                        variant="subtle"
                      >
                        {vessel.fr_level <= 1 ? 'Conforme' :
                          vessel.fr_level === 2 ? 'Em Risco' :
                            'Não Conforme'}
                      </Badge>
                    </Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </Box>
        </CardBody>
      </Card>

      {/* Alertas Críticos */}
      {stats.nonCompliant > 0 && (
        <Card mb={6} boxShadow="md" borderColor="red.300" borderWidth={2}>
          <CardBody>
            <Alert status="error" mb={4}>
              <AlertIcon />
              <Box>
                <AlertTitle>Embarcações Não Conformes</AlertTitle>
                <AlertDescription>
                  {stats.nonCompliant} embarcação(ões) requerem ação imediata
                </AlertDescription>
              </Box>
            </Alert>
            <List spacing={2}>
              {fleetStatus.vessels
                .filter(v => v.fr_level >= 3)
                .map((vessel) => (
                  <ListItem key={vessel.id}>
                    <ListIcon
                      as={WarningIcon}
                      color="red.500"
                    />
                    <strong>{vessel.name}</strong> ({vessel.vessel_class}) -
                    FR {vessel.fr_level} - {vessel.alert_message}
                  </ListItem>
                ))}
            </List>
          </CardBody>
        </Card>
      )}

      {/* Recomendações */}
      <Card mb={6} boxShadow="md">
        <CardBody>
          <Heading size="md" mb={4} color="blue.700">
            Recomendações Gerais
          </Heading>
          <List spacing={3}>
            {stats.nonCompliant > 0 && (
              <ListItem>
                <ListIcon as={WarningIcon} color="red.500" />
                <strong>Ação Imediata:</strong> {stats.nonCompliant} embarcação(ões)
                não conforme(s) requerem limpeza imediata para restaurar conformidade NORMAM 401.
              </ListItem>
            )}
            {stats.atRisk > 0 && (
              <ListItem>
                <ListIcon as={InfoIcon} color="orange.500" />
                <strong>Monitoramento Intensificado:</strong> {stats.atRisk} embarcação(ões)
                em risco devem ter monitoramento aumentado e limpeza preventiva agendada.
              </ListItem>
            )}
            {stats.complianceRate < 80 && (
              <ListItem>
                <ListIcon as={WarningIcon} color="yellow.500" />
                <strong>Melhoria Necessária:</strong> Taxa de conformidade abaixo de 80%.
                Revisar protocolos de manutenção e limpeza.
              </ListItem>
            )}
            {stats.avgFouling > 3.0 && (
              <ListItem>
                <ListIcon as={InfoIcon} color="blue.500" />
                <strong>Espessura Média Elevada:</strong> Espessura média de {stats.avgFouling.toFixed(2)} mm
                indica necessidade de programa de limpeza preventiva mais frequente.
              </ListItem>
            )}
            {stats.complianceRate >= 80 && stats.nonCompliant === 0 && (
              <ListItem>
                <ListIcon as={CheckCircleIcon} color="green.500" />
                <strong>Status Excelente:</strong> Frota em conformidade. Manter protocolos
                de monitoramento e manutenção preventiva.
              </ListItem>
            )}
          </List>
        </CardBody>
      </Card>

      {/* Rodapé */}
      <Box mt={8} pt={4} borderTop="1px solid" borderColor="gray.200">
        <Text fontSize="xs" color="gray.600" textAlign="center">
          Este relatório foi gerado automaticamente pelo Sistema HullZero - Transpetro
        </Text>
        <Text fontSize="xs" color="gray.600" textAlign="center" mt={1}>
          Para mais informações, consulte a documentação NORMAM 401
        </Text>
      </Box>

      {/* Estilos para impressão */}
      <style>{`
        @media print {
          body * {
            visibility: hidden;
          }
          #compliance-report, #compliance-report * {
            visibility: visible;
          }
          #compliance-report {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
          }
          button {
            display: none !important;
          }
        }
      `}</style>
    </Box>
  )
}

export default ComplianceReport

