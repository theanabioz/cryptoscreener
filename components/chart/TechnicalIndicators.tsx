'use client'

import { Box, SimpleGrid, Text, VStack, Badge, HStack, Progress } from '@chakra-ui/react';
import { Coin } from '@/lib/types';

interface TechnicalIndicatorsProps {
  coinData: Partial<Coin>;
  timeframe?: string;
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

export const TechnicalIndicators = ({ coinData, timeframe = '1H' }: TechnicalIndicatorsProps) => {
  if (!coinData.rsi) return null; // Don't render if no data

  const currentPrice = coinData.current_price ?? 0;
  const ema50 = coinData.ema50 ?? 0;
  const macd = coinData.macd ?? 0;
  const rsi = coinData.rsi ?? 0;

  // MACD Logic (Compare MACD line vs Signal line)
  // If macd > signal -> Bullish momentum
  const macdVal = coinData.macd ?? 0;
  const macdSig = coinData.macd_signal ?? 0;
  const macdStatus = macdVal > macdSig ? 'Bullish' : 'Bearish';
  const macdColor = macdVal > macdSig ? 'green' : 'red';

  // RSI Logic
  let rsiStatus = 'Neutral';
  let rsiColor = 'gray';
  if (rsi > 70) { rsiStatus = 'Overbought'; rsiColor = 'red'; }
  else if (rsi < 30) { rsiStatus = 'Oversold'; rsiColor = 'green'; }

  // EMA Logic
  const emaStatus = currentPrice > ema50 ? 'Above' : 'Below';
  const emaColor = currentPrice > ema50 ? 'green' : 'red';

  const indicators = [
    { label: `RSI (14)`, value: typeof rsi === 'number' ? rsi.toFixed(2) : rsi, status: rsiStatus, color: rsiColor },
    { label: 'MACD', value: typeof macd === 'number' ? macd.toFixed(2) : (macd || '-'), status: macdStatus, color: macdColor },
    { label: 'EMA (50)', value: typeof ema50 === 'number' ? ema50.toFixed(2) : (ema50 || '-'), status: emaStatus, color: emaColor },
    { label: 'Bollinger', value: coinData.bb_pos || 'Mid', status: 'Range', color: 'gray' },
  ];

  // --- COMPOSITE SCORE CALCULATION ---
  let score = 50; // Start at Neutral
  let totalWeight = 0;

  // 1. RSI (Weight 30)
  // <30 -> Buy (+), >70 -> Sell (-)
  if (rsi) {
      if (rsi < 30) score += 15; // Bullish
      else if (rsi > 70) score -= 15; // Bearish
      // else Neutral (no change)
      // Linear interpolation for more precision? Let's keep it simple signals first.
      // Better logic:
      // 0 (Overbought/Sell) ... 50 ... 100 (Oversold/Buy) <- Counter-intuitive?
      // Standard: 0=Sell, 100=Buy.
      // RSI > 70 is Sell. RSI < 30 is Buy.
      // Map RSI 0-100 to Score:
      // If RSI=80 (Sell) -> Score should decrease.
      // If RSI=20 (Buy) -> Score should increase.
  }
  
  // Let's use a simpler "Signal Count" approach for robustness
  let buySignals = 0;
  let sellSignals = 0;

  // RSI
  if (rsi < 35) buySignals++;
  if (rsi > 65) sellSignals++;

  // MACD
  if (macd !== undefined && coinData.macd_signal !== undefined) {
      if (macd > coinData.macd_signal) buySignals++;
      else sellSignals++;
  }

  // EMA
  if (currentPrice && ema50) {
      if (currentPrice > ema50) buySignals++;
      else sellSignals++;
  }

  // Bollinger
  if (currentPrice && coinData.bb_lower && coinData.bb_upper) {
      if (currentPrice < coinData.bb_lower) buySignals++; // Price too low -> Buy
      if (currentPrice > coinData.bb_upper) sellSignals++; // Price too high -> Sell
  }

  const totalSignals = buySignals + sellSignals;
  // Calculate percentage 0..100 (0 = All Sell, 100 = All Buy)
  // If no signals, 50.
  let finalScore = 50;
  if (totalSignals > 0) {
      finalScore = (buySignals / totalSignals) * 100;
  }

  // Determine Label and Color
  let ratingLabel = 'NEUTRAL';
  let ratingColor = 'gray';
  
  if (finalScore >= 80) { ratingLabel = 'STRONG BUY'; ratingColor = 'green'; }
  else if (finalScore >= 60) { ratingLabel = 'BUY'; ratingColor = 'green'; }
  else if (finalScore <= 20) { ratingLabel = 'STRONG SELL'; ratingColor = 'red'; }
  else if (finalScore <= 40) { ratingLabel = 'SELL'; ratingColor = 'red'; }

  return (
    <Box mt={6}>
      <Text fontSize="sm" fontWeight="bold" mb={3} px={4} color="gray.300">
        TECHNICAL ANALYSIS ({timeframe})
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

      {/* Signal Strength Gauge */}
      <Box px={4} mt={4}>
        <VStack align="stretch" spacing={2} bg="gray.800" p={3} borderRadius="lg">
          <HStack justify="space-between">
            <Text fontSize="xs" color="gray.400">Signal Strength</Text>
            <Text fontSize="sm" fontWeight="bold" color={`${ratingColor}.300`}>
                {ratingLabel}
            </Text>
          </HStack>
          
          <Box position="relative" w="full" h="6px">
             {/* Background Gradient */}
             <Box w="full" h="full" borderRadius="full" bgGradient="linear(to-r, red.500, gray.500, green.500)" opacity={0.3} />
             
             {/* Needle/Indicator */}
             <Box 
                position="absolute"
                left={`${finalScore}%`}
                top="-4px"
                bottom="-4px"
                w="4px"
                bg="white"
                borderRadius="full"
                boxShadow="0 0 8px white"
                transition="left 0.5s cubic-bezier(0.4, 0, 0.2, 1)"
             />
          </Box>

          <HStack justify="space-between" fontSize="10px" color="gray.500" pt={1}>
            <Text>Sell</Text>
            <Text>Neutral</Text>
            <Text>Buy</Text>
          </HStack>
        </VStack>
      </Box>
    </Box>
  );
};
