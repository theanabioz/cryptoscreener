'use client'

import { Box, Flex, Text, Image, Badge, VStack, HStack, useColorModeValue } from '@chakra-ui/react'
import { Coin } from '@/lib/types'
import { TrendingUp, TrendingDown } from 'lucide-react'
import { Sparkline } from '../ui/Sparkline'
import Link from 'next/link'
import { useHaptic } from '@/hooks/useHaptic'
import { useQueryClient } from '@tanstack/react-query'
import { useEffect } from 'react'
import { fetchKlines } from '@/hooks/useKlines'

import { PriceFlash } from '../ui/PriceFlash'

interface CoinItemProps {
  coin: Coin;
  index?: number;
}

export const CoinItem = ({ coin, index = 0 }: CoinItemProps) => {
  const isPositive = (coin.price_change_percentage_24h || 0) >= 0;
  const badgeColor = isPositive ? 'green' : 'red';
  
  const { impact } = useHaptic();
  const queryClient = useQueryClient();

  // Prefetch klines for the first 15 visible coins to make navigation instant
  useEffect(() => {
      if (index < 15 && coin.symbol) {
          queryClient.prefetchQuery({
              queryKey: ['klines', coin.symbol, '1h', 200], // Default timeframe/limit on Detail Page
              queryFn: () => fetchKlines(coin.symbol, '1h', 200),
              staleTime: 1000 * 60 * 5, // 5 minutes cache
          });
      }
  }, [coin.symbol, index, queryClient]);

  // Safe access to properties
  const price = coin.current_price || 0;
  const change = coin.price_change_percentage_24h || 0;
  const sparklineData = coin.sparkline_in_7d?.price || [];

  // Sparkline color based on data trend
  const sparklineColor = sparklineData.length >= 2
    ? (sparklineData[sparklineData.length - 1] >= sparklineData[0] ? 'green.400' : 'red.400')
    : (isPositive ? 'green.400' : 'red.400');

  return (
    <Link 
      href={`/coin/${coin.id}`} 
      style={{ textDecoration: 'none', display: 'block' }}
      onClick={() => impact('light')}
    >
      <Box 
        w="full" 
        p={3} 
        borderBottomWidth="1px" 
        borderColor="gray.800"
        bg="transparent"
        _active={{ bg: 'whiteAlpha.50' }}
        transition="background 0.2s"
      >
        <Flex justify="space-between" align="center">
          {/* Left: Icon + Name */}
          <HStack spacing={3} w="35%">
            <Image 
              src={coin.image} 
              alt={coin.name} 
              boxSize="32px" 
              borderRadius="full" 
              fallbackSrc="https://via.placeholder.com/32"
            />
            <VStack align="start" spacing={0} overflow="hidden">
              <Text fontWeight="bold" fontSize="sm" color="white" isTruncated maxW="full">
                {coin.symbol ? coin.symbol.toUpperCase() : '???'}
              </Text>
              <Text fontSize="xs" color="gray.500" isTruncated maxW="full">{coin.name || 'Unknown'}</Text>
            </VStack>
          </HStack>

          {/* Middle: Sparkline */}
          <Box w="30%" display="flex" justifyContent="center" alignItems="center">
            <Sparkline 
              data={sparklineData} 
              width={80} 
              height={30} 
              color={sparklineColor} 
            />
          </Box>

          {/* Right: Price + Change */}
          <VStack align="end" spacing={0} w="35%">
            <PriceFlash price={price} color="white" fontWeight="medium" fontSize="sm" />
            <Badge 
              colorScheme={badgeColor} 
              variant="solid" 
              fontSize="xs"
              borderRadius="sm"
              px={1}
              display="flex"
              alignItems="center"
            >
              {isPositive ? <TrendingUp size={10} style={{marginRight: '2px'}}/> : <TrendingDown size={10} style={{marginRight: '2px'}}/>}
              {Math.abs(change).toFixed(2)}%
            </Badge>
          </VStack>
        </Flex>
      </Box>
    </Link>
  )
}
