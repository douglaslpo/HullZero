import {
  Card,
  CardBody,
  Heading,
  VStack,
  HStack,
  Badge,
  Text,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Divider,
  List,
  ListItem,
  ListIcon,
  Alert,
  AlertIcon,
  Box,
} from '@chakra-ui/react'
import { InfoIcon } from '@chakra-ui/icons'
import type { AdvancedFoulingPrediction } from '../api/services'

interface AdvancedPredictionCardProps {
  prediction: AdvancedFoulingPrediction
}

function AdvancedPredictionCard({ prediction }: AdvancedPredictionCardProps) {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'red'
      case 'severe': return 'orange'
      case 'moderate': return 'yellow'
      case 'light': return 'green'
      default: return 'gray'
    }
  }

  const getSeverityLabel = (severity: string) => {
    switch (severity) {
      case 'critical': return 'Crítico'
      case 'severe': return 'Severo'
      case 'moderate': return 'Moderado'
      case 'light': return 'Leve'
      default: return severity
    }
  }

  return (
    <Card>
      <CardBody>
        <VStack spacing={4} align="stretch">
          <HStack justify="space-between">
            <Heading size="md">Predição Avançada de Bioincrustação</Heading>
            <Badge colorScheme={getSeverityColor(prediction.fouling_severity)} fontSize="md">
              {getSeverityLabel(prediction.fouling_severity)}
            </Badge>
          </HStack>

          <Divider />

          {/* Métricas Principais */}
          <HStack spacing={4}>
            <Stat>
              <StatLabel>Espessura Estimada</StatLabel>
              <StatNumber>{prediction.estimated_thickness_mm.toFixed(2)} mm</StatNumber>
              <StatHelpText>Confiança: {(prediction.confidence_score * 100).toFixed(0)}%</StatHelpText>
            </Stat>

            <Stat>
              <StatLabel>Rugosidade</StatLabel>
              <StatNumber>{prediction.estimated_roughness_um.toFixed(0)} μm</StatNumber>
            </Stat>

            <Stat>
              <StatLabel>Impacto no Combustível</StatLabel>
              <StatNumber>{prediction.predicted_fuel_impact_percent.toFixed(1)}%</StatNumber>
              <StatHelpText>
                CO₂: {(prediction.predicted_co2_impact_kg / 1000).toFixed(1)} toneladas
              </StatHelpText>
            </Stat>
          </HStack>

          {/* Espécies Invasoras */}
          {Object.keys(prediction.invasive_species_risk).length > 0 && (
            <Box>
              <Heading size="sm" mb={2}>Riscos de Espécies Invasoras</Heading>
              <VStack align="stretch" spacing={2}>
                {Object.entries(prediction.invasive_species_risk).map(([species, risk]) => (
                  <HStack key={species} justify="space-between">
                    <Text fontSize="sm">{species.replace(/_/g, ' ')}</Text>
                    <Badge colorScheme={risk > 0.7 ? 'red' : risk > 0.4 ? 'yellow' : 'green'}>
                      {(risk * 100).toFixed(0)}%
                    </Badge>
                  </HStack>
                ))}
              </VStack>
            </Box>
          )}

          {/* Recomendações de Controle Natural */}
          {prediction.natural_control_recommendations.length > 0 && (
            <Box>
              <Heading size="sm" mb={2}>Recomendações de Controle Natural</Heading>
              <List spacing={2}>
                {prediction.natural_control_recommendations.map((rec, i) => (
                  <ListItem key={i}>
                    <ListIcon as={InfoIcon} color="blue.500" />
                    {rec}
                  </ListItem>
                ))}
              </List>
            </Box>
          )}

          {/* Contribuições do Ensemble */}
          {Object.keys(prediction.model_ensemble_contributions).length > 0 && (
            <Box>
              <Heading size="sm" mb={2}>Contribuições dos Modelos</Heading>
              <VStack align="stretch" spacing={1}>
                {Object.entries(prediction.model_ensemble_contributions).map(([model, value]) => (
                  <HStack key={model} justify="space-between">
                    <Text fontSize="xs">{model.toUpperCase()}</Text>
                    <Text fontSize="xs" fontWeight="bold">
                      {value.toFixed(2)} mm
                    </Text>
                  </HStack>
                ))}
              </VStack>
            </Box>
          )}

          {/* Feature Importance */}
          {Object.keys(prediction.feature_importance).length > 0 && (
            <Box>
              <Heading size="sm" mb={2}>Importância das Features</Heading>
              <VStack align="stretch" spacing={1}>
                {Object.entries(prediction.feature_importance)
                  .sort(([, a], [, b]) => b - a)
                  .slice(0, 5)
                  .map(([feature, importance]) => (
                    <HStack key={feature} justify="space-between">
                      <Text fontSize="xs">{feature.replace(/_/g, ' ')}</Text>
                      <Badge colorScheme="blue" fontSize="xs">
                        {(importance * 100).toFixed(1)}%
                      </Badge>
                    </HStack>
                  ))}
              </VStack>
            </Box>
          )}

          <Alert status="info" borderRadius="md">
            <AlertIcon />
            <Box>
              <Text fontSize="sm" fontWeight="bold">Modelo Avançado</Text>
              <Text fontSize="xs">
                Predição usando ensemble de 4 algoritmos de IA com análise de espécies invasoras
              </Text>
            </Box>
          </Alert>
        </VStack>
      </CardBody>
    </Card>
  )
}

export default AdvancedPredictionCard

