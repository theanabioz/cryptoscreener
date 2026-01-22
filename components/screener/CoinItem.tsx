'use client'

import { Box, Flex, Text, Image, Badge, VStack, HStack, useColorModeValue } from '@chakra-ui/react'
import { Coin } from '@/lib/types'
import { TrendingUp, TrendingDown } from 'lucide-react'
import { Sparkline } from '../ui/Sparkline'
import Link from 'next/link'
import { useHaptic } from '@/hooks/useHaptic'
import { useQueryClient } from '@tanstack/react-query'
import { useEffect, useRef, useState } from 'react'
import { fetchKlines } from '@/hooks/useKlines'

import { PriceFlash } from '../ui/PriceFlash'
import { usePriceStore } from '@/store/usePriceStore'

interface CoinItemProps {
  coin: Coin;
  index?: number;
}

export const CoinItem = ({ coin, index = 0 }: CoinItemProps) => {
  const { impact } = useHaptic();
  const queryClient = useQueryClient();
  
  // Intersection Observer for Lazy Prefetching
  const ref = useRef<HTMLDivElement>(null);
  const [hasPrefetched, setHasPrefetched] = useState(false);

  // 1. Subscribe to live price updates (Access directly for subscription)
  const liveData = usePriceStore((state) => state.prices[coin.symbol]);
  
  // 2. Determine effective price
  const currentPrice = liveData?.c ?? coin.current_price ?? 0;

  // 3. Recalculate 24h change
  let change = coin.price_change_percentage_24h ?? 0;
  if (liveData && coin.current_price && coin.current_price !== 0) {
      const open24h = coin.current_price / (1 + (coin.price_change_percentage_24h / 100));
      change = ((currentPrice - open24h) / open24h) * 100;
  }

  const isPositive = change >= 0;
  const badgeColor = isPositive ? 'green' : 'red';

  useEffect(() => {
      if (!coin.symbol || hasPrefetched || !ref.current) return;

      const observer = new IntersectionObserver(
          (entries) => {
              if (entries[0].isIntersecting) {
                  // Coin is visible (or close to), prefetch data
                  queryClient.prefetchQuery({
                      queryKey: ['klines', coin.symbol, '1h', 200],
                      queryFn: () => fetchKlines(coin.symbol, '1h', 200),
                      staleTime: 1000 * 60 * 5,
                  });
                  
                  setHasPrefetched(true);
                  observer.disconnect(); // Stop observing once triggered
              }
          },
          { 
              rootMargin: '200px', // Prefetch 200px before item comes into view
              threshold: 0.1 
          }
      );

      observer.observe(ref.current);

      return () => observer.disconnect();
  }, [coin.symbol, hasPrefetched, queryClient]);

  // Sparkline data
  const sparklineData = coin.sparkline_in_7d?.price || [];

  // Sparkline color based on data trend (Live Price vs Start of 7d)
  const sparklineColor = sparklineData.length > 0
    ? (currentPrice >= sparklineData[0] ? 'green.400' : 'red.400')
    : (isPositive ? 'green.400' : 'red.400');

  return (
    <Link 
      href={`/coin/${coin.id}`} 
      style={{ textDecoration: 'none', display: 'block' }}
      onClick={() => impact('light')}
    >
      <Box 
        ref={ref}
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
            <PriceFlash price={currentPrice} color="white" fontWeight="medium" fontSize="sm" />
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
