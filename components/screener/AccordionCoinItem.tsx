'use client'

import { Box, Flex, Text, Image, Badge, VStack, HStack, Collapse, IconButton, useDisclosure, Grid, GridItem } from '@chakra-ui/react'
import { Coin } from '@/lib/types'
import { TrendingUp, TrendingDown, ChevronDown, ChevronUp, BarChart2 } from 'lucide-react'
import { PriceFlash } from '../ui/PriceFlash'
import { useHaptic } from '@/hooks/useHaptic'
import Link from 'next/link'
import { DetailChart } from '../chart/DetailChart'

interface AccordionCoinItemProps {
  coin: Coin;
}

export const AccordionCoinItem = ({ coin }: AccordionCoinItemProps) => {
  const { isOpen, onToggle } = useDisclosure();
  const { impact } = useHaptic();

  const isPositive = (coin.price_change_percentage_24h || 0) >= 0;
  const badgeColor = isPositive ? 'green' : 'red';
  
  const handleToggle = () => {
    impact('light');
    onToggle();
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
        <HStack spacing={3} w="40%">
          <Image 
            src={coin.image} 
            alt={coin.name} 
            boxSize="32px" 
            borderRadius="full" 
            fallbackSrc="https://via.placeholder.com/32"
          />
          <VStack align="start" spacing={0} overflow="hidden">
            <Text fontWeight="bold" fontSize="sm" color="white">
              {coin.symbol.toUpperCase()}
            </Text>
            <HStack spacing={1}>
              <Badge 
                colorScheme="gray" 
                variant="subtle" 
                fontSize="9px" 
                px={1} 
                borderRadius="sm"
              >
                #{1}
              </Badge>
            </HStack>
          </VStack>
        </HStack>

        {/* Right: Price + Change + Chevron */}
        <HStack spacing={4} w="60%" justify="flex-end">
          <VStack align="end" spacing={0}>
            <PriceFlash price={coin.current_price} color="white" fontWeight="medium" fontSize="sm" />
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
          
          <Box color="gray.500">
            {isOpen ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </Box>
        </HStack>
      </Flex>

      {/* Expanded Content */}
      <Collapse in={isOpen} animateOpacity>
        <Box px={3} pb={4} pt={1}>
          
          {/* 1. Key Metrics Grid */}
          <Grid templateColumns="repeat(3, 1fr)" gap={2} mb={4}>
            <GridItem bg="whiteAlpha.100" borderRadius="md" p={2} textAlign="center">
              <Text fontSize="10px" color="gray.400">RSI (14)</Text>
              <Text fontWeight="bold" fontSize="sm" color={coin.rsi > 70 ? "red.300" : coin.rsi < 30 ? "green.300" : "white"}>
                {coin.rsi || 50}
              </Text>
            </GridItem>
            <GridItem bg="whiteAlpha.100" borderRadius="md" p={2} textAlign="center">
              <Text fontSize="10px" color="gray.400">Vol (24h)</Text>
              <Text fontWeight="bold" fontSize="sm">
                ${(coin.total_volume / 1e6).toFixed(0)}M
              </Text>
            </GridItem>
            <GridItem bg="whiteAlpha.100" borderRadius="md" p={2} textAlign="center">
              <Text fontSize="10px" color="gray.400">M. Cap</Text>
              <Text fontWeight="bold" fontSize="sm">
                -
              </Text>
            </GridItem>
          </Grid>

          {/* 2. Mini Chart (Only render if open to save resources) */}
          {isOpen && (
            <Box h="150px" w="full" mb={4} pointerEvents="none">
               {/* We reuse DetailChart but maybe we want a simpler version later */}
               {/* For now, let's keep it simple: just a button to open full chart */}
               <Flex justify="center" align="center" h="full" bg="whiteAlpha.50" borderRadius="md">
                  <Text fontSize="xs" color="gray.500">Mini Chart Coming Soon</Text>
               </Flex>
            </Box>
          )}

          {/* 3. Action Button */}
          <Link href={`/coin/${coin.id}`} style={{ width: '100%' }}>
            <Box 
              as="button"
              w="full"
              py={2}
              bg="brand.500"
              color="white"
              borderRadius="md"
              fontWeight="bold"
              fontSize="sm"
              _active={{ bg: 'brand.600' }}
              display="flex"
              justifyContent="center"
              alignItems="center"
              gap={2}
            >
              <BarChart2 size={16} />
              Open Full Chart Analysis
            </Box>
          </Link>

        </Box>
      </Collapse>
    </Box>
  )
}
