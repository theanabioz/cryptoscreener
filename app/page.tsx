'use client'

import { Box, Flex, Heading, IconButton, Input, InputGroup, InputLeftElement, VStack, Text } from "@chakra-ui/react";
import { Search, SlidersHorizontal } from "lucide-react";
import { CoinItem } from "@/components/screener/CoinItem"; // Use simple CoinItem instead of Accordion
import { CoinSkeleton } from "@/components/screener/CoinSkeleton";
import { useState, useMemo, useEffect } from "react";
import { useHaptic } from "@/hooks/useHaptic";
import { useFilterStore } from "@/store/filterStore";
import Link from "next/link";
import { useCoins } from "@/hooks/useCoins";

export default function ScreenerPage() {
  const { impact } = useHaptic();
  const { data: coins, isLoading: isQueryLoading } = useCoins();
  
  // Use global filter store
  const { filters, setFilters, activeFilterCount } = useFilterStore();

  // isLoading in TanStack Query v5 is true only when there is no data in cache
  const isLoading = isQueryLoading && !coins;

  const filteredCoins = useMemo(() => {
    if (!coins) return [];
    
    return coins.filter(coin => {
      // 1. Search
      const matchesSearch = 
        coin.name.toLowerCase().includes(filters.search.toLowerCase()) || 
        coin.symbol.toLowerCase().includes(filters.search.toLowerCase());

      if (!matchesSearch) return false;

      // 2. Price Range
      const minP = parseFloat(filters.minPrice);
      const maxP = parseFloat(filters.maxPrice);
      if (!isNaN(minP) && coin.current_price < minP) return false;
      if (!isNaN(maxP) && coin.current_price > maxP) return false;

      // 3. Market Cap
      if (filters.marketCap === 'high' && coin.market_cap < 1_000_000_000) return false;
      if (filters.marketCap === 'mid' && (coin.market_cap < 100_000_000 || coin.market_cap >= 1_000_000_000)) return false;
      if (filters.marketCap === 'low' && coin.market_cap >= 100_000_000) return false;

      // 4. Price Change
      if (filters.priceChange === 'gainers' && coin.price_change_percentage_24h < 0) return false;
      if (filters.priceChange === 'losers' && coin.price_change_percentage_24h >= 0) return false;

      return true;
    }).sort((a, b) => (b.market_cap || 0) - (a.market_cap || 0));
  }, [filters, coins]);

  const activeCount = activeFilterCount();

  return (
    <Box>
      {/* Header & Search */}
      <Box 
        position="sticky" 
        top={0} 
        zIndex={10} 
        bg="gray.900" 
        borderBottomWidth="1px" 
        borderColor="gray.800"
        px={4}
        pb={3}
        pt="calc(10px + env(safe-area-inset-top))"
      >
        {/* Centered Title */}
        <Flex justify="center" align="center" h="40px" mb={2}>
          <Heading size="md">Market</Heading>
          <Box ml={2} w={2} h={2} borderRadius="full" bg="green.400" boxShadow="0 0 8px var(--chakra-colors-green-400)" />
        </Flex>
        
        {/* Search + Filter Row */}
        <Box display="flex" gap={2}>
          <InputGroup size="md">
            <InputLeftElement pointerEvents="none">
              <Search color="gray.500" size={18} />
            </InputLeftElement>
            <Input 
              placeholder="Search coins..." 
              variant="filled" 
              bg="gray.800" 
              _hover={{ bg: 'gray.700' }}
              _focus={{ bg: 'gray.700', borderColor: 'brand.400' }}
              borderRadius="lg"
              value={filters.search}
              onChange={(e) => setFilters({...filters, search: e.target.value})}
            />
          </InputGroup>

          <Link href="/filters" onClick={() => impact('medium')}>
            <Box position="relative">
              <IconButton 
                aria-label="Filters" 
                icon={<SlidersHorizontal size={20} />} 
                variant={activeCount > 0 ? "solid" : "outline"}
                colorScheme={activeCount > 0 ? "teal" : "gray"}
                borderColor="gray.700"
                bg={activeCount > 0 ? undefined : "gray.800"}
                _hover={{ bg: 'gray.700' }}
                // onClick handled by Link
              />
              {activeCount > 0 && (
                <Box 
                  position="absolute" 
                  top="-2px" 
                  right="-2px" 
                  bg="red.400" 
                  w="2" 
                  h="2" 
                  borderRadius="full" 
                  zIndex={2}
                />
              )}
            </Box>
          </Link>
        </Box>
      </Box>

      {/* Coins List */}
      <VStack spacing={0} align="stretch" pb="20px">
        {isLoading ? (
          Array.from({ length: 10 }).map((_, i) => (
            <CoinSkeleton key={i} />
          ))
        ) : (
          filteredCoins.length > 0 ? (
            filteredCoins.map((coin, index) => (
              <CoinItem key={coin.id} coin={coin} index={index} />
            ))
          ) : (
            <Box p={8} textAlign="center">
              <Text color="gray.500">No coins found matching filters.</Text>
            </Box>
          )
        )}
      </VStack>
    </Box>
  );
}
