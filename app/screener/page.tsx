'use client'

import { Box, SimpleGrid, Heading, Text, VStack, Icon, Badge } from '@chakra-ui/react';
import { TrendingUp, BarChart2, Activity, Zap } from 'lucide-react';
import { useHaptic } from '@/hooks/useHaptic';

const STRATEGIES = [
  {
    id: 'pump-radar',
    title: 'Pump Radar',
    description: 'High volume & price spike in last 15m.',
    icon: Zap,
    color: 'yellow',
    gradient: 'linear(to-br, yellow.400, orange.500)',
  },
  {
    id: 'rsi-oversold',
    title: 'RSI Oversold',
    description: 'RSI < 30. Potential bounce candidates.',
    icon: Activity,
    color: 'green',
    gradient: 'linear(to-br, green.400, teal.500)',
  },
  {
    id: 'strong-trend',
    title: 'Strong Uptrend',
    description: 'Price > EMA 50 > EMA 200.',
    icon: TrendingUp,
    color: 'blue',
    gradient: 'linear(to-br, blue.400, purple.500)',
  },
  {
    id: 'volatility',
    title: 'High Volatility',
    description: 'Top movers of the day.',
    icon: BarChart2,
    color: 'red',
    gradient: 'linear(to-br, red.400, pink.500)',
  },
];

export default function ScreenerStrategiesPage() {
  const { impact } = useHaptic();

  return (
    <Box p={4} pt="calc(10px + env(safe-area-inset-top))">
      <Heading size="lg" mb={6}>Smart Screener</Heading>
      
      <SimpleGrid columns={1} spacing={4}>
        {STRATEGIES.map((strategy) => (
          <Box
            key={strategy.id}
            bg="gray.800"
            borderRadius="xl"
            p={4}
            position="relative"
            overflow="hidden"
            _active={{ transform: 'scale(0.98)' }}
            transition="all 0.2s"
            onClick={() => impact('medium')}
          >
            {/* Gradient Background Accent */}
            <Box 
              position="absolute" 
              top={0} 
              right={0} 
              w="100px" 
              h="100px" 
              bgGradient={strategy.gradient} 
              opacity={0.2} 
              filter="blur(40px)" 
              borderRadius="full"
            />

            <VStack align="start" spacing={3}>
              <Box 
                p={2} 
                borderRadius="lg" 
                bgGradient={strategy.gradient} 
                color="white"
              >
                <Icon as={strategy.icon} size={24} />
              </Box>
              
              <VStack align="start" spacing={1}>
                <Heading size="md">{strategy.title}</Heading>
                <Text fontSize="sm" color="gray.400">
                  {strategy.description}
                </Text>
              </VStack>

              <Badge colorScheme={strategy.color} variant="subtle" borderRadius="full" px={2}>
                Auto-Update
              </Badge>
            </VStack>
          </Box>
        ))}
      </SimpleGrid>
    </Box>
  );
}
