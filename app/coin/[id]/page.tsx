'use client'

import { Box, Flex, IconButton, Text, Heading, VStack, HStack, Image, Badge, SimpleGrid, Stat, StatLabel, StatNumber } from '@chakra-ui/react';
import { TrendingUp, TrendingDown, Star } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { MOCK_COINS } from '@/lib/mockData';
import { DetailChart } from '@/components/chart/DetailChart';
import { TechnicalIndicators } from '@/components/chart/TechnicalIndicators';
import { use } from 'react';
import { useTelegramBackButton } from '@/hooks/useTelegramBackButton';
import { useWatchlistStore } from '@/store/useWatchlistStore';
import { useHaptic } from '@/hooks/useHaptic';

export default function CoinDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter();
  const resolvedParams = use(params);
  const id = resolvedParams.id;
  
  // Hooks
  useTelegramBackButton();
  const { impact, notification } = useHaptic();
  const { toggleCoin, favorites } = useWatchlistStore();
  
  // Check if favorite (simple check, for strict hydration safety we might use a useEffect wrapper, but this is fine for MVP)
  const isFav = favorites.includes(id);

  const handleToggleFavorite = () => {
    toggleCoin(id);
    if (!isFav) {
      notification('success');
    } else {
      impact('light');
    }
  };
  
  // Find coin (in real app, useQuery)
  const coin = MOCK_COINS.find(c => c.id === id);

  const isPositive = (coin?.price_change_percentage_24h || 0) >= 0;

  if (!coin) {
    return (
      <Box p={4}>
        <Text>Coin not found</Text>
      </Box>
    );
  }

  return (
    <Box pb="100px">
      {/* Header */}
      <Box 
        position="sticky" 
        top={0} 
        zIndex={10} 
        bg="gray.900" 
        borderBottomWidth="1px" 
        borderColor="gray.800"
        pt="calc(10px + env(safe-area-inset-top))"
        pb={3}
        px={4}
      >
        <Flex justify="center" align="center" position="relative" h="40px" mb={2}>
          {/* Back button space placeholder if needed, but native button handles navigation. 
              We just center the title. */}
          <Heading size="md">{coin.name}</Heading>
        </Flex>
      </Box>

      {/* Main Price Info */}
      <VStack p={4} align="start" spacing={1}>
        <Flex w="full" justify="space-between" align="center">
          <HStack align="center" spacing={3}>
             <Image src={coin.image} boxSize="40px" alt={coin.name} />
             <VStack align="start" spacing={-1}>
               <Text fontSize="3xl" fontWeight="bold">
                  ${coin.current_price.toLocaleString()}
               </Text>
             </VStack>
          </HStack>
          
          <IconButton 
            aria-label="Add to Watchlist" 
            icon={<Star size={24} fill={isFav ? "currentColor" : "none"} />} 
            variant="ghost" 
            color={isFav ? "yellow.400" : "gray.400"}
            size="lg"
            _hover={{ bg: 'gray.800' }}
            onClick={handleToggleFavorite}
          />
        </Flex>
        
        <Badge 
          colorScheme={isPositive ? 'green' : 'red'} 
          variant="solid" 
          fontSize="md"
          borderRadius="md"
          px={2}
          display="flex"
          alignItems="center"
        >
          {isPositive ? <TrendingUp size={16} style={{marginRight: '4px'}}/> : <TrendingDown size={16} style={{marginRight: '4px'}}/>}
          {Math.abs(coin.price_change_percentage_24h).toFixed(2)}% (24h)
        </Badge>
      </VStack>

      {/* Chart */}
      <Box w="full" mt={4} mb={8}>
        <DetailChart coinId={coin.id} basePrice={coin.current_price} isPositive={isPositive} />
      </Box>

      {/* Stats Grid */}
      <SimpleGrid columns={2} spacing={4} px={4} mt={4}>
        <Stat bg="gray.800" p={3} borderRadius="lg">
          <StatLabel color="gray.400">Market Cap</StatLabel>
          <StatNumber fontSize="md">${(coin.market_cap / 1e9).toFixed(2)}B</StatNumber>
        </Stat>
        <Stat bg="gray.800" p={3} borderRadius="lg">
          <StatLabel color="gray.400">Volume (24h)</StatLabel>
          <StatNumber fontSize="md">${(coin.total_volume / 1e6).toFixed(2)}M</StatNumber>
        </Stat>
        <Stat bg="gray.800" p={3} borderRadius="lg">
          <StatLabel color="gray.400">High (24h)</StatLabel>
          <StatNumber fontSize="md">${(coin.current_price * 1.05).toFixed(2)}</StatNumber>
        </Stat>
        <Stat bg="gray.800" p={3} borderRadius="lg">
          <StatLabel color="gray.400">Low (24h)</StatLabel>
          <StatNumber fontSize="md">${(coin.current_price * 0.95).toFixed(2)}</StatNumber>
        </Stat>
      </SimpleGrid>

      {/* Technical Indicators Section */}
      <TechnicalIndicators />
      
      {/* Description / About */}
      <Box p={4} mt={4}>
        <Heading size="sm" mb={2}>About {coin.name}</Heading>
        <Text fontSize="sm" color="gray.400">
          {coin.name} is a cryptocurrency operating on the blockchain. 
          Current supply is {Math.floor(Math.random() * 10000000).toLocaleString()} {coin.symbol.toUpperCase()}.
        </Text>
      </Box>

    </Box>
  );
}
