'use client'

import { Box, Flex, IconButton, Text, Heading, VStack, HStack, Image, Badge, SimpleGrid, Stat, StatLabel, StatNumber } from '@chakra-ui/react';
import { TrendingUp, TrendingDown, Star } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { MOCK_COINS } from '@/lib/mockData';
import { DetailChart } from '@/components/chart/DetailChart';
import { TechnicalIndicators } from '@/components/chart/TechnicalIndicators';
import { use, useState, useMemo, useEffect } from 'react';
import { useTelegramBackButton } from '@/hooks/useTelegramBackButton';
import { useWatchlistStore } from '@/store/useWatchlistStore';
import { useHaptic } from '@/hooks/useHaptic';
import { useCoins } from '@/hooks/useCoins';
import { useKlines } from '@/hooks/useKlines';
import { PriceFlash } from '@/components/ui/PriceFlash';
import { calculateRSI, calculateMACD, calculateEMA, calculateBollinger } from '@/lib/indicators';

export default function CoinDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter();
  const resolvedParams = use(params);
  const id = resolvedParams.id;
  
  // Hooks
  useTelegramBackButton();
  const { impact, notification } = useHaptic();
  const { toggleCoin, favorites } = useWatchlistStore();
  const { data: coins } = useCoins();
  
  // State for Timeframe and History Limit
  const [activeTf, setActiveTf] = useState('1H');
  const [historyLimit, setHistoryLimit] = useState(200); 
  
  // Reset limit when timeframe changes to ensure fast load
  const handleTfChange = (newTf: string) => {
      setActiveTf(newTf);
      setHistoryLimit(200);
  };
  
  // Find coin in loaded data
  const coin = coins?.find(c => c.id === id);
  const symbol = coin?.symbol || '';

  // Load Klines for Chart and Indicators
  const apiInterval = activeTf.toLowerCase();
  
  // Enable placeholder only when fetching heavy history (limit > 200), 
  // so switching timeframes (limit=200) shows a loading state immediately.
  const { data: klines, isLoading: isChartLoading, isError: isChartError, isPlaceholderData } = useKlines(symbol, apiInterval, historyLimit, historyLimit > 200);

  // Progressive Loading Effect
  // Once initial data (200) is loaded, fetch full history (3000) in background
  useEffect(() => {
      if (klines && klines.length >= 100 && historyLimit === 200 && !isChartLoading) {
          const timer = setTimeout(() => {
              setHistoryLimit(3000);
          }, 1000); // Wait 1s after render before fetching heavy history
          return () => clearTimeout(timer);
      }
  }, [klines, historyLimit, isChartLoading]);

  // Calculate Indicators dynamically based on Klines
  const dynamicIndicators = useMemo(() => {
      if (!klines || klines.length < 50) return coin || {}; // Fallback to static data if not enough klines

      const closePrices = klines.map(k => k.close);
      
      const rsiSeries = calculateRSI(closePrices, 14);
      const emaSeries = calculateEMA(closePrices, 50);
      const macdData = calculateMACD(closePrices, 12, 26, 9);
      const bbData = calculateBollinger(closePrices, 20, 2);

      const lastIndex = closePrices.length - 1;

      return {
          ...coin,
          rsi: rsiSeries[lastIndex],
          ema50: emaSeries[lastIndex],
          
          // TechnicalIndicators expects MACD Line and Signal Line for comparison
          macd: macdData.macdLine[lastIndex],
          macd_signal: macdData.signalLine[lastIndex],
          
          bb_upper: bbData.upper[lastIndex],
          bb_lower: bbData.lower[lastIndex],
          // Current price from klines to match indicators
          current_price: closePrices[lastIndex] 
      };
  }, [klines, coin]);

  // Check if favorite
  const isFav = favorites.includes(id);

  const handleToggleFavorite = () => {
    toggleCoin(id);
    if (!isFav) {
      notification('success');
    } else {
      impact('light');
    }
  };
  
  const isPositive = (coin?.price_change_percentage_24h || 0) >= 0;

  if (!coin) {
    return (
      <Box p={4} pt="calc(10px + env(safe-area-inset-top))">
        <Text>Coin not found</Text>
      </Box>
    );
  }

  return (
    <Box pb="100px" overflowX="hidden" w="100vw">
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
          <Heading size="md">{coin.name}</Heading>
        </Flex>
      </Box>

      {/* Main Price Info */}
      <VStack p={4} align="start" spacing={1}>
        <Flex w="full" justify="space-between" align="center">
        <HStack align="center" spacing={3}>
           <Image src={coin.image} boxSize="40px" alt={coin.name} />
           <VStack align="start" spacing={-1}>
             <PriceFlash price={coin.current_price} fontSize="3xl" fontWeight="bold" />
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
        <DetailChart 
          coinId={coin.id} 
          symbol={coin.symbol} 
          basePrice={coin.current_price} 
          isPositive={isPositive}
          klines={klines}
          isLoading={isChartLoading && !isPlaceholderData} // Only show spinner on initial hard load
          isError={isChartError}
          activeTf={activeTf}
          onTfChange={handleTfChange}
        />
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
      <TechnicalIndicators coinData={dynamicIndicators} timeframe={activeTf} isLoading={isChartLoading} />
      
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
