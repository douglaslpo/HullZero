import { useState } from 'react'
import {
  Box,
  VStack,
  Heading,
  Text,
  Card,
  CardBody,
  Button,
  Badge,
  HStack,
  Input,
  InputGroup,
  InputLeftElement,
  Select,
  Grid,
  Alert,
  AlertIcon,
  Spinner,
  Center,
  Progress,
  Divider,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  IconButton,
  Tooltip,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  FormControl,
  FormLabel,
  useToast,
} from '@chakra-ui/react'
import { SearchIcon, EditIcon, InfoIcon, AddIcon } from '@chakra-ui/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { fleetManagementService, vesselService, type FleetSummary, type VesselDetailedStatus } from '../api/services'

function FleetManagement() {
  const [searchTerm, setSearchTerm] = useState('')
  const [vesselTypeFilter, setVesselTypeFilter] = useState('all')
  const [frFilter, setFrFilter] = useState('all')
  const navigate = useNavigate()
  const { isOpen, onOpen, onClose } = useDisclosure()
  const toast = useToast()
  const queryClient = useQueryClient()

  // Form state
  const [newVessel, setNewVessel] = useState({
    name: '',
    imo_number: '',
    vessel_type: 'suezmax',
    home_port: '',
    hull_area_m2: 0,
    length_m: 0,
    width_m: 0,
    draft_m: 0,
    paint_type: 'self_polishing',
    max_speed_knots: 0,
    typical_speed_knots: 0,
    engine_power_kw: 0,
    typical_consumption_kg_h: 0,
    fuel_type: 'HFO',
    engine_type: '2-stroke',
    call_sign: '',
    displacement_tonnes: 0,
    hull_material: 'steel'
  })

  // Buscar sumário da frota
  const { data: summary, isLoading: summaryLoading } = useQuery<FleetSummary>({
    queryKey: ['fleet-summary'],
    queryFn: () => fleetManagementService.getSummary(),
    refetchInterval: 60000, // Atualizar a cada minuto
  })

  // Buscar status detalhado
  const { data: detailedStatus, isLoading: statusLoading } = useQuery<{
    vessels: VesselDetailedStatus[]
    last_update: string
  }>({
    queryKey: ['fleet-detailed-status'],
    queryFn: () => fleetManagementService.getDetailedStatus(),
    refetchInterval: 60000,
  })

  const createVesselMutation = useMutation({
    mutationFn: (vesselData: any) => vesselService.create(vesselData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fleet-detailed-status'] })
      queryClient.invalidateQueries({ queryKey: ['fleet-summary'] })
      toast({
        title: 'Embarcação registrada.',
        description: "A nova embarcação foi adicionada à frota com sucesso.",
        status: 'success',
        duration: 5000,
        isClosable: true,
      })
      onClose()
      // Reset form
      setNewVessel({
        name: '',
        imo_number: '',
        vessel_type: 'suezmax',
        home_port: '',
        hull_area_m2: 0,
        length_m: 0,
        width_m: 0,
        draft_m: 0,
        paint_type: 'self_polishing',
        max_speed_knots: 0,
        typical_speed_knots: 0,
        engine_power_kw: 0,
        typical_consumption_kg_h: 0,
        fuel_type: 'HFO',
        engine_type: '2-stroke',
        call_sign: '',
        displacement_tonnes: 0,
        hull_material: 'steel'
      })
    },
    onError: (error) => {
      toast({
        title: 'Erro ao registrar.',
        description: "Ocorreu um erro ao tentar registrar a embarcação.",
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
      console.error(error)
    }
  })

  const handleCreateVessel = () => {
    createVesselMutation.mutate(newVessel)
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setNewVessel(prev => ({
      ...prev,
      [name]: ['hull_area_m2', 'length_m', 'width_m', 'draft_m', 'max_speed_knots', 'typical_speed_knots', 'engine_power_kw', 'typical_consumption_kg_h', 'displacement_tonnes'].includes(name)
        ? parseFloat(value) || 0
        : value
    }))
  }

  // Filtrar embarcações
  const filteredVessels = detailedStatus?.vessels.filter(vessel => {
    const matchesSearch = vessel.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      vessel.vessel_id.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = vesselTypeFilter === 'all' ||
      (vessel.vessel_class?.toLowerCase() || '').includes(vesselTypeFilter.toLowerCase())
    const matchesFr = frFilter === 'all' ||
      (frFilter === '0' && vessel.fr_level === 0) ||
      (frFilter === '1' && vessel.fr_level === 1) ||
      (frFilter === '2' && vessel.fr_level === 2) ||
      (frFilter === '3+' && vessel.fr_level >= 3)
    return matchesSearch && matchesType && matchesFr
  }) || []

  const getFrColor = (frLevel: number) => {
    switch (frLevel) {
      case 0: return 'green'
      case 1: return 'blue'
      case 2: return 'orange'
      case 3: return 'red'
      case 4: return 'red'
      default: return 'gray'
    }
  }

  const getAlertStatus = (alertType?: string): 'error' | 'warning' | 'info' | 'success' => {
    switch (alertType) {
      case 'critical': return 'error'
      case 'warning': return 'warning'
      case 'info': return 'info'
      default: return 'info'
    }
  }

  const getPerformanceColor = (loss: number) => {
    if (loss < 5) return 'green'
    if (loss < 15) return 'yellow'
    if (loss < 25) return 'orange'
    return 'red'
  }

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'N/A'
    try {
      const date = new Date(dateStr)
      return date.toLocaleDateString('pt-BR')
    } catch {
      return dateStr
    }
  }

  return (
    <VStack spacing={6} align="stretch">
      {/* Cabeçalho */}
      <HStack justify="space-between">
        <Box>
          <Heading size="xl" mb={2}>Monitoramento Preditivo de Bioincrustação</Heading>
          <Text color="gray.600">Status da Frota | Desafio Transpetro</Text>
          {summary && (
            <Text fontSize="sm" color="gray.500" mt={1}>
              Última Atualização: {new Date(summary.last_update).toLocaleString('pt-BR')}
            </Text>
          )}
        </Box>
        <Button leftIcon={<AddIcon />} colorScheme="blue" onClick={onOpen}>
          Registrar Embarcação
        </Button>
      </HStack>

      {/* Sumário da Frota */}
      {summaryLoading ? (
        <Center py={8}>
          <Spinner size="xl" />
        </Center>
      ) : summary && (
        <Card>
          <CardBody>
            <Heading size="md" mb={4}>Sumário da Frota</Heading>
            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
              <Stat>
                <StatLabel>Navios Monitorados</StatLabel>
                <StatNumber>{summary.monitored_vessels}</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Consumo Adicional Médio</StatLabel>
                <StatNumber color={summary.average_additional_consumption_percent > 5 ? 'orange.500' : 'green.500'}>
                  {summary.average_additional_consumption_percent}%
                </StatNumber>
                <StatHelpText>Resistência adicional média</StatHelpText>
              </Stat>
              <Box>
                <Text fontSize="sm" fontWeight="bold" mb={2}>Classificação de Risco (FR)</Text>
                <VStack align="stretch" spacing={2}>
                  <HStack justify="space-between">
                    <Text fontSize="sm">FR 0 - Limpo:</Text>
                    <Badge colorScheme="green">{summary.fr_distribution['FR 0']}</Badge>
                  </HStack>
                  <HStack justify="space-between">
                    <Text fontSize="sm">FR 1 - Microincrustação:</Text>
                    <Badge colorScheme="blue">{summary.fr_distribution['FR 1']}</Badge>
                  </HStack>
                  <HStack justify="space-between">
                    <Text fontSize="sm">FR 2 - Macro L. (Alerta):</Text>
                    <Badge colorScheme="orange">{summary.fr_distribution['FR 2']}</Badge>
                  </HStack>
                  <HStack justify="space-between">
                    <Text fontSize="sm">FR 3+4 - Alto Risco:</Text>
                    <Badge colorScheme="red">{summary.fr_distribution['FR 3+4']}</Badge>
                  </HStack>
                </VStack>
              </Box>
            </SimpleGrid>
          </CardBody>
        </Card>
      )}

      {/* Filtros */}
      <Card>
        <CardBody>
          <Grid templateColumns={{ base: '1fr', md: 'repeat(3, 1fr)' }} gap={4}>
            <InputGroup>
              <InputLeftElement pointerEvents="none">
                <SearchIcon color="gray.300" />
              </InputLeftElement>
              <Input
                placeholder="Buscar por nome ou ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </InputGroup>
            <Select value={vesselTypeFilter} onChange={(e) => setVesselTypeFilter(e.target.value)}>
              <option value="all">Todos os Tipos</option>
              <option value="suezmax">Suezmax</option>
              <option value="aframax">Aframax</option>
              <option value="panamax">Panamax</option>
              <option value="gaseiro">Gaseiro</option>
              <option value="produtos">Produtos</option>
            </Select>
            <Select value={frFilter} onChange={(e) => setFrFilter(e.target.value)}>
              <option value="all">Todos os FR</option>
              <option value="0">FR 0 - Limpo</option>
              <option value="1">FR 1 - Micro</option>
              <option value="2">FR 2 - Macro Leve</option>
              <option value="3+">FR 3+4 - Alto Risco</option>
            </Select>
          </Grid>
        </CardBody>
      </Card>

      {/* Status Detalhado da Frota */}
      {statusLoading ? (
        <Center py={8}>
          <Spinner size="xl" />
        </Center>
      ) : filteredVessels.length === 0 ? (
        <Alert status="info">
          <AlertIcon />
          Nenhuma embarcação encontrada com os filtros aplicados.
        </Alert>
      ) : (
        <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' }} gap={4}>
          {filteredVessels.map((vessel) => (
            <Card key={vessel.id} borderWidth={vessel.fr_level >= 3 ? 2 : 1}
              borderColor={vessel.fr_level >= 3 ? 'red.500' : 'gray.200'}>
              <CardBody>
                <VStack align="stretch" spacing={4}>
                  {/* Cabeçalho do Card */}
                  <Box>
                    <HStack justify="space-between" mb={2}>
                      <Heading size="md">{vessel.name}</Heading>
                      <Badge colorScheme={getFrColor(vessel.fr_level)} fontSize="md" px={2} py={1}>
                        FR {vessel.fr_level}
                      </Badge>
                    </HStack>
                    <HStack>
                      <Text fontSize="sm" color="gray.600">
                        {vessel.vessel_class || 'N/A'} | ID: {vessel.vessel_id}
                      </Text>
                    </HStack>
                  </Box>

                  <Divider />

                  {/* Perda de Performance */}
                  <Box>
                    <HStack justify="space-between" mb={2}>
                      <Text fontSize="sm" fontWeight="bold">
                        Perda de Performance (Resistência Adicional)
                      </Text>
                      <Text fontSize="sm" fontWeight="bold" color={`${getPerformanceColor(vessel.performance_loss_percent)}.500`}>
                        {vessel.performance_loss_percent}%
                      </Text>
                    </HStack>
                    <Progress
                      value={vessel.performance_loss_percent}
                      max={50}
                      colorScheme={getPerformanceColor(vessel.performance_loss_percent)}
                      size="md"
                      borderRadius="md"
                    />
                  </Box>

                  {/* Informações de Manutenção */}
                  <VStack align="stretch" spacing={2} fontSize="sm">
                    <HStack justify="space-between">
                      <Text color="gray.600">Última Limpeza:</Text>
                      <Text fontWeight="medium">{formatDate(vessel.last_cleaning_date)}</Text>
                    </HStack>
                    <HStack justify="space-between">
                      <Text color="gray.600">Última Pintura (AFS):</Text>
                      <Text fontWeight="medium">{formatDate(vessel.last_painting_date)}</Text>
                    </HStack>
                    <HStack justify="space-between">
                      <Text color="gray.600">Calibração Sensor:</Text>
                      <Text fontWeight="medium">{formatDate(vessel.sensor_calibration_date)}</Text>
                    </HStack>
                  </VStack>

                  <Divider />

                  {/* Risco Futuro */}
                  <Box>
                    <Text fontSize="sm" fontWeight="bold" mb={2}>Risco (15/30 dias)</Text>
                    <HStack justify="space-between">
                      <HStack>
                        <Text fontSize="sm" color="gray.600">15 dias:</Text>
                        <Badge colorScheme={getFrColor(vessel.risk_15_days)}>
                          FR {vessel.risk_15_days}
                        </Badge>
                      </HStack>
                      <HStack>
                        <Text fontSize="sm" color="gray.600">30 dias:</Text>
                        <Badge colorScheme={getFrColor(vessel.risk_30_days)}>
                          FR {vessel.risk_30_days}
                        </Badge>
                      </HStack>
                    </HStack>
                  </Box>

                  {/* Alerta */}
                  {vessel.alert_message && (
                    <Alert status={getAlertStatus(vessel.alert_type)} borderRadius="md">
                      <AlertIcon />
                      <Box fontSize="xs">
                        <Text fontWeight="bold" mb={1}>
                          {vessel.alert_type === 'critical' ? 'ALERTA:' : vessel.alert_type === 'warning' ? 'ALERTA:' : 'INFO:'}
                        </Text>
                        <Text>{vessel.alert_message}</Text>
                      </Box>
                    </Alert>
                  )}

                  {/* Ações */}
                  <HStack spacing={2} mt={2}>
                    <Button
                      size="sm"
                      leftIcon={<InfoIcon />}
                      colorScheme="blue"
                      variant="outline"
                      flex={1}
                      onClick={() => navigate(`/vessel/${vessel.id}`)}
                    >
                      Ver Detalhes
                    </Button>
                    <Tooltip label="Editar">
                      <IconButton
                        aria-label="Editar"
                        icon={<EditIcon />}
                        size="sm"
                        colorScheme="gray"
                        variant="outline"
                      />
                    </Tooltip>
                  </HStack>
                </VStack>
              </CardBody>
            </Card>
          ))}
        </Grid>
      )}

      {/* Alerta de Manutenção (Top 3 críticos) */}
      {detailedStatus && detailedStatus.vessels.filter(v => v.fr_level >= 2).length > 0 && (
        <Card>
          <CardBody>
            <Heading size="md" mb={4}>Alerta de Manutenção</Heading>
            <VStack align="stretch" spacing={3}>
              {detailedStatus.vessels
                .filter(v => v.fr_level >= 2)
                .sort((a, b) => b.fr_level - a.fr_level)
                .slice(0, 3)
                .map((vessel) => (
                  <Alert
                    key={vessel.id}
                    status={vessel.fr_level >= 4 ? 'error' : 'warning'}
                    borderRadius="md"
                  >
                    <AlertIcon />
                    <Box flex={1}>
                      <Text fontWeight="bold">
                        {vessel.name} (FR {vessel.fr_level}):
                      </Text>
                      <Text fontSize="sm" mt={1}>
                        {vessel.alert_message || `Perda: ${vessel.performance_loss_percent}%. Risco: FR ${vessel.risk_15_days} (15 dias).`}
                      </Text>
                    </Box>
                  </Alert>
                ))}
            </VStack>
          </CardBody>
        </Card>
      )}

      {/* Modal de Registro de Embarcação */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Registrar Nova Embarcação</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4}>
              <FormControl isRequired>
                <FormLabel>Nome da Embarcação</FormLabel>
                <Input name="name" value={newVessel.name} onChange={handleInputChange} />
              </FormControl>

              <HStack width="100%">
                <FormControl isRequired>
                  <FormLabel>IMO Number</FormLabel>
                  <Input name="imo_number" value={newVessel.imo_number} onChange={handleInputChange} />
                </FormControl>
                <FormControl isRequired>
                  <FormLabel>Call Sign</FormLabel>
                  <Input name="call_sign" value={newVessel.call_sign} onChange={handleInputChange} />
                </FormControl>
              </HStack>

              <HStack width="100%">
                <FormControl isRequired>
                  <FormLabel>Tipo</FormLabel>
                  <Select name="vessel_type" value={newVessel.vessel_type} onChange={handleInputChange}>
                    <option value="suezmax">Suezmax</option>
                    <option value="aframax">Aframax</option>
                    <option value="panamax">Panamax</option>
                    <option value="vlcc">VLCC</option>
                    <option value="gas_carrier">Gaseiro</option>
                  </Select>
                </FormControl>
                <FormControl isRequired>
                  <FormLabel>Porto de Origem</FormLabel>
                  <Input name="home_port" value={newVessel.home_port} onChange={handleInputChange} />
                </FormControl>
              </HStack>

              <Heading size="sm" alignSelf="start" mt={2}>Dimensões</Heading>
              <SimpleGrid columns={2} spacing={4} width="100%">
                <FormControl>
                  <FormLabel>Comprimento (m)</FormLabel>
                  <Input type="number" name="length_m" value={newVessel.length_m} onChange={handleInputChange} />
                </FormControl>
                <FormControl>
                  <FormLabel>Largura (m)</FormLabel>
                  <Input type="number" name="width_m" value={newVessel.width_m} onChange={handleInputChange} />
                </FormControl>
                <FormControl>
                  <FormLabel>Calado (m)</FormLabel>
                  <Input type="number" name="draft_m" value={newVessel.draft_m} onChange={handleInputChange} />
                </FormControl>
                <FormControl>
                  <FormLabel>Área do Casco (m²)</FormLabel>
                  <Input type="number" name="hull_area_m2" value={newVessel.hull_area_m2} onChange={handleInputChange} />
                </FormControl>
              </SimpleGrid>

              <Heading size="sm" alignSelf="start" mt={2}>Operacional</Heading>
              <SimpleGrid columns={2} spacing={4} width="100%">
                <FormControl>
                  <FormLabel>Velocidade Máx (nós)</FormLabel>
                  <Input type="number" name="max_speed_knots" value={newVessel.max_speed_knots} onChange={handleInputChange} />
                </FormControl>
                <FormControl>
                  <FormLabel>Velocidade Típica (nós)</FormLabel>
                  <Input type="number" name="typical_speed_knots" value={newVessel.typical_speed_knots} onChange={handleInputChange} />
                </FormControl>
                <FormControl>
                  <FormLabel>Potência Motor (kW)</FormLabel>
                  <Input type="number" name="engine_power_kw" value={newVessel.engine_power_kw} onChange={handleInputChange} />
                </FormControl>
                <FormControl>
                  <FormLabel>Consumo Típico (kg/h)</FormLabel>
                  <Input type="number" name="typical_consumption_kg_h" value={newVessel.typical_consumption_kg_h} onChange={handleInputChange} />
                </FormControl>
              </SimpleGrid>
            </VStack>
          </ModalBody>

          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancelar
            </Button>
            <Button colorScheme="blue" onClick={handleCreateVessel} isLoading={createVesselMutation.isPending}>
              Registrar
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </VStack>
  )
}

export default FleetManagement
