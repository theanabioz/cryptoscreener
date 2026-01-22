'use client'

import { Box, Flex, Text, Image, Badge, VStack, HStack, Collapse, useDisclosure, Grid, GridItem, Progress } from '@chakra-ui/react'
import { Coin } from '@/lib/types'
import { TrendingUp, TrendingDown, ChevronDown, ChevronUp, BarChart2, Activity } from 'lucide-react'
import { PriceFlash } from '../ui/PriceFlash'
import { useHaptic } from '@/hooks/useHaptic'
import Link from 'next/link'
import { Sparkline } from '../ui/Sparkline'
import { usePriceStore } from '@/store/usePriceStore'

interface AccordionCoinItemProps {
  coin: Coin;
}

export const AccordionCoinItem = ({ coin }: AccordionCoinItemProps) => {
  const { isOpen, onToggle } = useDisclosure();
  const { impact } = useHaptic();
  
  // 1. Subscribe to live price updates (Access directly for subscription)
  const liveData = usePriceStore((state) => state.prices[coin.symbol]);
  
  // 2. Determine effective price
  const currentPrice = liveData?.c ?? coin.current_price;

  // 3. Recalculate 24h change if we have live data
  let priceChange = coin.price_change_percentage_24h;
  if (liveData && coin.current_price && coin.current_price !== 0) {
      // Back-calculate 24h Open Price from the snapshot data
      const open24h = coin.current_price / (1 + (coin.price_change_percentage_24h / 100));
      // Calculate new change %
      priceChange = ((currentPrice - open24h) / open24h) * 100;
  }

  const isPositive = (priceChange || 0) >= 0;
  const badgeColor = isPositive ? 'green' : 'red';
  
  // Trend Logic
  const isBullish = coin.ema50 ? currentPrice > coin.ema50 : null;
  
  const handleToggle = () => {
    impact('light');
    onToggle();
  };

  const formatVolume = (vol: number) => {
      if (vol >= 1e9) return `$${(vol / 1e9).toFixed(1)}B`;
      if (vol >= 1e6) return `$${(vol / 1e6).toFixed(1)}M`;
      return `$${(vol / 1e3).toFixed(1)}K`;
  };

  // Sparkline trend logic
  const sparklineData = coin.sparkline_in_7d?.price || [];
  const sparklineColor = sparklineData.length >= 2 
    ? (sparklineData[sparklineData.length - 1] >= sparklineData[0] ? 'green.400' : 'red.400')
    : (isPositive ? 'green.400' : 'red.400');

  return (
    <Box 
      borderBottomWidth="1px" 
      borderColor="gray.800"
      bg={isOpen ? "whiteAlpha.50" : "transparent"}
      transition="all 0.2s"
    >
      {/* Header Row (Always Visible) */}
      <Flex 
        p={3} 
        justify="space-between" 
        align="center" 
        onClick={handleToggle}
        cursor="pointer"
      >
        {/* Left: Icon + Name */}
        <HStack spacing={3} w="35%">
          <Image 
            src={coin.image} 
            alt={coin.name} 
            boxSize="32px" 
            borderRadius="full" 
          />
          <VStack align="start" spacing={0} overflow="hidden">
            <HStack spacing={1}>
                <Text fontWeight="bold" fontSize="sm" color="white">
                {coin.symbol.toUpperCase()}
                </Text>
                {isBullish !== null && (
                    <Badge 
                        colorScheme={isBullish ? 'green' : 'red'} 
                        variant="subtle" 
                        fontSize="8px" 
                        px={1}
                    >
                        {isBullish ? 'UP' : 'DN'}
                    </Badge>
                )}
            </HStack>
            <Text fontSize="10px" color="gray.500" isTruncated>{coin.name}</Text>
          </VStack>
        </HStack>

        {/* Center: Sparkline */}
        <Flex w="30%" justify="center" align="center">
           <Sparkline 
              data={sparklineData} 
              width={70} 
              height={25} 
              color={sparklineColor} 
           />
        </Flex>

        {/* Right: Price + Change + Chevron */}
        <HStack spacing={2} w="35%" justify="flex-end">
          <VStack align="end" spacing={0}>
            <PriceFlash price={currentPrice} color="white" fontWeight="bold" fontSize="sm" />
            <Badge 
              colorScheme={badgeColor} 
              variant="solid" 
              fontSize="10px"
              borderRadius="sm"
              px={1}
              display="flex"
              alignItems="center"
            >
              {isPositive ? <TrendingUp size={10} style={{marginRight: '2px'}}/> : <TrendingDown size={10} style={{marginRight: '2px'}}/>}
              {Math.abs(priceChange).toFixed(1)}%
            </Badge>
          </VStack>
          
          <Box color="gray.600">
            {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </Box>
        </HStack>
      </Flex>

      {/* Expanded Content */}
      <Collapse in={isOpen} animateOpacity>
        <Box px={3} pb={4} pt={1}>
          
          {/* RSI Visual Bar */}
          <Box mb={4} bg="whiteAlpha.100" p={3} borderRadius="md">
            <Flex justify="space-between" mb={1}>
                <Text fontSize="xs" color="gray.400">RSI (14)</Text>
                <Text fontSize="xs" fontWeight="bold" color={
                    (coin.rsi ?? 50) > 70 ? "red.300" : (coin.rsi ?? 50) < 30 ? "green.300" : "white"
                }>
                    {coin.rsi ? coin.rsi.toFixed(1) : 'N/A'}
                </Text>
            </Flex>
            <Box w="full" h="4px" bg="gray.700" borderRadius="full" position="relative">
                {/* Zones */}
                <Box position="absolute" left="0" w="30%" h="full" bg="green.900" opacity={0.3} borderLeftRadius="full" />
                <Box position="absolute" right="0" w="30%" h="full" bg="red.900" opacity={0.3} borderRightRadius="full" />
                
                {/* Indicator */}
                <Box 
                    position="absolute" 
                    left={`${Math.min(Math.max(coin.rsi || 50, 0), 100)}%`} 
                    top="-3px"
                    w="10px" 
                    h="10px" 
                    bg={
                        (coin.rsi ?? 50) > 70 ? "red.400" : (coin.rsi ?? 50) < 30 ? "green.400" : "blue.400"
                    } 
                    borderRadius="full"
                    transform="translateX(-50%)"
                    border="2px solid white"
                />
            </Box>
          </Box>

          {/* Key Metrics Grid */}
          <Grid templateColumns="repeat(3, 1fr)" gap={2} mb={4}>
            
            {/* Volume */}
            <GridItem bg="whiteAlpha.100" borderRadius="md" p={2} textAlign="center">
              <Text fontSize="10px" color="gray.400">Volume (24h)</Text>
              <Text fontWeight="bold" fontSize="sm">
                {formatVolume(coin.total_volume)}
              </Text>
            </GridItem>

            {/* MACD */}
            <GridItem bg="whiteAlpha.100" borderRadius="md" p={2} textAlign="center">
              <Text fontSize="10px" color="gray.400">MACD</Text>
              <Text fontWeight="bold" fontSize="sm" color={(coin.macd || 0) > 0 ? 'green.300' : 'red.300'}>
                {coin.macd ? coin.macd.toFixed(2) : '-'}
              </Text>
            </GridItem>

             {/* EMA Trend */}
             <GridItem bg="whiteAlpha.100" borderRadius="md" p={2} textAlign="center">
              <Text fontSize="10px" color="gray.400">Trend (EMA)</Text>
              <Text fontWeight="bold" fontSize="sm" color={isBullish ? 'green.300' : 'red.300'}>
                {isBullish === null ? '-' : (isBullish ? 'UP' : 'DOWN')}
              </Text>
            </GridItem>
          </Grid>

          {/* Action Button */}
          <Link href={`/coin/${coin.id}`} style={{ width: '100%' }}>
            <Box 
              as="button"
              w="full"
              py={3}
              bg="brand.500"
              color="white"
              borderRadius="xl"
              fontWeight="bold"
              fontSize="sm"
              _active={{ bg: 'brand.600', transform: 'scale(0.98)' }}
              transition="all 0.1s"
              display="flex"
              justifyContent="center"
              alignItems="center"
              gap={2}
              boxShadow="0 4px 12px rgba(0, 0, 0, 0.3)"
            >
              <BarChart2 size={18} />
              Full Analysis
            </Box>
          </Link>

        </Box>
      </Collapse>
    </Box>
  )
}