'use client'

import { Box, SimpleGrid, Text, VStack, Badge, HStack, Progress } from '@chakra-ui/react';
import { Coin } from '@/lib/types';

interface TechnicalIndicatorsProps {
  coinData: Partial<Coin>;
}

const IndicatorItem = ({ label, value, status, statusColor }: { label: string, value: string | number, status?: string, statusColor?: string }) => (
  <Box bg="gray.800" p={3} borderRadius="lg">
    <VStack align="start" spacing={1}>
      <Text fontSize="xs" color="gray.400" fontWeight="bold" textTransform="uppercase">{label}</Text>
      <HStack justify="space-between" w="full">
        <Text fontSize="lg" fontWeight="bold">{value}</Text>
        {status && (
          <Badge colorScheme={statusColor} variant="subtle" fontSize="10px">
            {status}
          </Badge>
        )}
      </HStack>
    </VStack>
  </Box>
);

export const TechnicalIndicators = ({ coinData }: TechnicalIndicatorsProps) => {
  if (!coinData.rsi) return null; // Don't render if no data

  // RSI Logic
  let rsiStatus = 'Neutral';
  let rsiColor = 'gray';
  if (coinData.rsi > 70) { rsiStatus = 'Overbought'; rsiColor = 'red'; }
  else if (coinData.rsi < 30) { rsiStatus = 'Oversold'; rsiColor = 'green'; }

  // MACD Logic
  const macdStatus = (coinData.macd || 0) > 0 ? 'Bullish' : 'Bearish';
  const macdColor = (coinData.macd || 0) > 0 ? 'green' : 'red';

  // EMA Logic
  const emaStatus = coinData.current_price > (coinData.ema50 || 0) ? 'Above' : 'Below';
  const emaColor = coinData.current_price > (coinData.ema50 || 0) ? 'green' : 'red';

  const indicators = [
    { label: 'RSI (14)', value: coinData.rsi, status: rsiStatus, color: rsiColor },
    { label: 'MACD', value: coinData.macd || '-', status: macdStatus, color: macdColor },
    { label: 'EMA (50)', value: coinData.ema50 || '-', status: emaStatus, color: emaColor },
    { label: 'Bollinger', value: coinData.bb_pos || 'Mid', status: 'Range', color: 'gray' },
  ];

  return (
    <Box mt={6}>
      <Text fontSize="sm" fontWeight="bold" mb={3} px={4} color="gray.300">
        TECHNICAL ANALYSIS (1H)
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
            <Text fontSize="xs" fontWeight="bold">{coinData.rsi}/100</Text>
          </HStack>
          <Progress 
            value={coinData.rsi} 
            size="xs" 
            colorScheme={rsiColor} 
            borderRadius="full" 
            bg="gray.700" 
          />
          <HStack justify="space-between" fontSize="10px" color="gray.600">
            <Text>Oversold (30)</Text>
            <Text>Overbought (70)</Text>
          </HStack>
        </VStack>
      </Box>
    </Box>
  );
};
