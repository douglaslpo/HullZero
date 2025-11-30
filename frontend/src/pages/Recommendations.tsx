import { Box, VStack, Heading, Text, Card, CardBody } from '@chakra-ui/react'

function Recommendations() {
  return (
    <VStack spacing={6} align="stretch">
      <Box>
        <Heading size="xl" mb={2}>Recomendações de Limpeza</Heading>
        <Text color="gray.600">Análise de custo-benefício e otimização</Text>
      </Box>

      <Card>
        <CardBody>
          <Text>Página de recomendações em desenvolvimento...</Text>
        </CardBody>
      </Card>
    </VStack>
  )
}

export default Recommendations

