'use client'

import { Box, Flex, Text, Image, Badge, VStack, HStack, useColorModeValue } from '@chakra-ui/react'
import { Coin } from '@/lib/types'
import { TrendingUp, TrendingDown } from 'lucide-react'
import { Sparkline } from '../ui/Sparkline'
import Link from 'next/link'

interface CoinItemProps {
  coin: Coin;
}

export const CoinItem = ({ coin }: CoinItemProps) => {
  const isPositive = coin.price_change_percentage_24h >= 0;
  const trendColor = isPositive ? 'green.400' : 'red.400';
  const badgeColor = isPositive ? 'green' : 'red';

  return (
    <Link href={`/coin/${coin.id}`} style={{ textDecoration: 'none', display: 'block' }}>
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
              <Text fontWeight="bold" fontSize="sm" color="white" isTruncated maxW="full">{coin.symbol.toUpperCase()}</Text>
              <Text fontSize="xs" color="gray.500" isTruncated maxW="full">{coin.name}</Text>
            </VStack>
          </HStack>

          {/* Middle: Sparkline */}
          <Box w="30%" display="flex" justifyContent="center">
            <Box color={trendColor}>
               <Sparkline data={coin.sparkline_in_7d.price} width={80} height={30} />
            </Box>
          </Box>

          {/* Right: Price + Change */}
          <VStack align="end" spacing={0} w="35%">
            <Text fontWeight="medium" fontSize="sm" color="white">
              ${coin.current_price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 6 })}
            </Text>
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
              {Math.abs(coin.price_change_percentage_24h).toFixed(2)}%
            </Badge>
          </VStack>
        </Flex>
      </Box>
    </Link>
  )
}
