'use client'

import { Box, Flex, Text, Image, Badge, VStack, HStack, Collapse, useDisclosure, Grid, GridItem, Progress } from '@chakra-ui/react'
import { Coin } from '@/lib/types'
import { TrendingUp, TrendingDown, ChevronDown, ChevronUp, BarChart2, Activity } from 'lucide-react'
import { PriceFlash } from '../ui/PriceFlash'
import { useHaptic } from '@/hooks/useHaptic'
import Link from 'next/link'

interface AccordionCoinItemProps {
  coin: Coin;
}

export const AccordionCoinItem = ({ coin }: AccordionCoinItemProps) => {
  const { isOpen, onToggle } = useDisclosure();
  const { impact } = useHaptic();

  const isPositive = (coin.price_change_percentage_24h || 0) >= 0;
  const badgeColor = isPositive ? 'green' : 'red';
  
  // Trend Logic
  const isBullish = coin.ema50 ? coin.current_price > coin.ema50 : null;
  
  const handleToggle = () => {
    impact('light');
    onToggle();
  };

  const formatVolume = (vol: number) => {
      if (vol >= 1e9) return `$${(vol / 1e9).toFixed(1)}B`;
      if (vol >= 1e6) return `$${(vol / 1e6).toFixed(1)}M`;
      return `$${(vol / 1e3).toFixed(1)}K`;
  };

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
        <HStack spacing={3} w="45%">
          <Image 
            src={coin.image} 
            alt={coin.name} 
            boxSize="36px" 
            borderRadius="full" 
            fallbackSrc="https://via.placeholder.com/32"
          />
          <VStack align="start" spacing={0} overflow="hidden">
            <HStack>
                <Text fontWeight="bold" fontSize="md" color="white">
                {coin.symbol.toUpperCase()}
                </Text>
                {/* Trend Badge in Header if available */}
                {isBullish !== null && (
                    <Badge 
                        colorScheme={isBullish ? 'green' : 'red'} 
                        variant="subtle" 
                        fontSize="xx-small" 
                        px={1}
                        h="14px"
                    >
                        {isBullish ? 'BULL' : 'BEAR'}
                    </Badge>
                )}
            </HStack>
            <Text fontSize="xs" color="gray.500" isTruncated>{coin.name}</Text>
          </VStack>
        </HStack>

        {/* Right: Price + Change + Chevron */}
        <HStack spacing={3} w="55%" justify="flex-end">
          <VStack align="end" spacing={0}>
            <PriceFlash price={coin.current_price} color="white" fontWeight="bold" fontSize="sm" />
            <Badge 
              colorScheme={badgeColor} 
              variant="solid" 
              fontSize="xs"
              borderRadius="sm"
              px={1.5}
              display="flex"
              alignItems="center"
            >
              {isPositive ? <TrendingUp size={12} style={{marginRight: '3px'}}/> : <TrendingDown size={12} style={{marginRight: '3px'}}/>}
              {Math.abs(coin.price_change_percentage_24h).toFixed(2)}%
            </Badge>
          </VStack>
          
          <Box color="gray.500">
            {isOpen ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
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