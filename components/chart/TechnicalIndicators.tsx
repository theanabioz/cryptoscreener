'use client'

import { Box, SimpleGrid, Text, VStack, Badge, HStack, Progress } from '@chakra-ui/react';

interface IndicatorProps {
  label: string;
  value: string | number;
  status?: string;
  statusColor?: string;
}

const IndicatorItem = ({ label, value, status, statusColor }: IndicatorProps) => (
  <Box bg="gray.800" p={3} borderRadius="lg" borderLeftWidth="4px" borderLeftColor={statusColor || 'gray.600'}>
    <VStack align="start" spacing={1}>
      <Text fontSize="xs" color="gray.400" fontWeight="bold" textTransform="uppercase">{label}</Text>
      <HStack justify="space-between" w="full">
        <Text fontSize="lg" fontWeight="bold">{value}</Text>
        {status && (
          <Badge colorScheme={statusColor === 'green.400' ? 'green' : statusColor === 'red.400' ? 'red' : 'gray'} variant="subtle" fontSize="10px">
            {status}
          </Badge>
        )}
      </HStack>
    </VStack>
  </Box>
);

export const TechnicalIndicators = () => {
  // Mock data for indicators
  const indicators = [
    { label: 'RSI (14)', value: '68.5', status: 'Neutral', color: 'gray.400' },
    { label: 'MACD', value: '1.24', status: 'Bullish', color: 'green.400' },
    { label: 'EMA (20)', value: 'Above', status: 'Strong Buy', color: 'green.400' },
    { label: 'Bollinger', value: 'Mid', status: 'Neutral', color: 'gray.400' },
  ];

  return (
    <Box mt={6}>
      <Text fontSize="sm" fontWeight="bold" mb={3} px={4} color="gray.300">
        TECHNICAL ANALYSIS (1D)
      </Text>
      
      <SimpleGrid columns={2} spacing={3} px={4}>
        {indicators.map((ind) => (
          <IndicatorItem 
            key={ind.label} 
            label={ind.label} 
            value={ind.value} 
            status={ind.status} 
            statusColor={ind.color}
          />
        ))}
      </SimpleGrid>

      {/* RSI Gauge visualization */}
      <Box px={4} mt={4}>
        <VStack align="stretch" spacing={1} bg="gray.800" p={3} borderRadius="lg">
          <HStack justify="space-between">
            <Text fontSize="xs" color="gray.400">RSI Strength</Text>
            <Text fontSize="xs" fontWeight="bold">68.5/100</Text>
          </HStack>
          <Progress value={68.5} size="xs" colorScheme="orange" borderRadius="full" bg="gray.700" />
          <HStack justify="space-between" fontSize="10px" color="gray.600">
            <Text>Oversold (30)</Text>
            <Text>Overbought (70)</Text>
          </HStack>
        </VStack>
      </Box>
    </Box>
  );
};
