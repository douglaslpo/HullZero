import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Button,
  VStack,
  Text,
  Box,
  Divider,
  Badge,
  HStack,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
} from '@chakra-ui/react'
import ContributionChart from './ContributionChart'

interface FeatureContribution {
  feature_name: string
  contribution: number
  percentage: number
  description: string
}

interface Explanation {
  prediction_id: string
  prediction_value: number
  base_value: number
  feature_contributions: FeatureContribution[]
  explanation_text: string
  confidence: number
  model_type: string
}

interface ExplanationModalProps {
  isOpen: boolean
  onClose: () => void
  explanation: Explanation | null
  title?: string
}

export default function ExplanationModal({
  isOpen,
  onClose,
  explanation,
  title = 'Explicação da Predição'
}: ExplanationModalProps) {
  if (!explanation) return null

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'green'
    if (confidence >= 0.6) return 'yellow'
    return 'orange'
  }

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.8) return 'Alta'
    if (confidence >= 0.6) return 'Média'
    return 'Baixa'
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl" scrollBehavior="inside">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>{title}</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack align="stretch" spacing={4}>
            {/* Valor Predito e Confiança */}
            <Box>
              <HStack justify="space-between" mb={2}>
                <Text fontWeight="bold">Valor Predito:</Text>
                <Text fontSize="xl" fontWeight="bold" color="blue.600">
                  {explanation.prediction_value.toFixed(2)} mm
                </Text>
              </HStack>
              <HStack justify="space-between">
                <Text color="gray.600">Confiança:</Text>
                <Badge colorScheme={getConfidenceColor(explanation.confidence)}>
                  {getConfidenceLabel(explanation.confidence)} ({(explanation.confidence * 100).toFixed(0)}%)
                </Badge>
              </HStack>
            </Box>

            <Divider />

            {/* Explicação Textual */}
            <Box>
              <Text fontWeight="bold" mb={2}>Explicação:</Text>
              <Text 
                whiteSpace="pre-line" 
                color="gray.700"
                bg="gray.50"
                p={3}
                borderRadius="md"
              >
                {explanation.explanation_text}
              </Text>
            </Box>

            <Divider />

            {/* Gráfico de Contribuições */}
            <Box>
              <ContributionChart
                contributions={explanation.feature_contributions}
                title="Contribuição de Cada Fator"
              />
            </Box>

            <Divider />

            {/* Detalhes das Contribuições */}
            <Accordion allowToggle>
              <AccordionItem>
                <AccordionButton>
                  <Box flex="1" textAlign="left">
                    <Text fontWeight="bold">Detalhes das Contribuições</Text>
                  </Box>
                  <AccordionIcon />
                </AccordionButton>
                <AccordionPanel pb={4}>
                  <VStack align="stretch" spacing={2}>
                    {explanation.feature_contributions
                      .sort((a, b) => Math.abs(b.contribution) - Math.abs(a.contribution))
                      .map((contrib, index) => (
                        <Box
                          key={index}
                          p={3}
                          bg="gray.50"
                          borderRadius="md"
                          borderLeft="4px solid"
                          borderLeftColor={contrib.contribution > 0 ? 'green.500' : 'red.500'}
                        >
                          <HStack justify="space-between" mb={1}>
                            <Text fontWeight="bold">{contrib.feature_name}</Text>
                            <Badge colorScheme={contrib.contribution > 0 ? 'green' : 'red'}>
                              {contrib.contribution > 0 ? '+' : ''}
                              {(contrib.contribution * 100).toFixed(1)}%
                            </Badge>
                          </HStack>
                          <Text fontSize="sm" color="gray.600">
                            {contrib.description}
                          </Text>
                          <Text fontSize="xs" color="gray.500" mt={1}>
                            Contribuição: {contrib.percentage.toFixed(1)}% do total
                          </Text>
                        </Box>
                      ))}
                  </VStack>
                </AccordionPanel>
              </AccordionItem>
            </Accordion>

            {/* Informações do Modelo */}
            <Box>
              <Text fontSize="xs" color="gray.500">
                Modelo: {explanation.model_type} | ID: {explanation.prediction_id}
              </Text>
            </Box>
          </VStack>
        </ModalBody>

        <ModalFooter>
          <Button colorScheme="blue" onClick={onClose}>
            Fechar
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}

