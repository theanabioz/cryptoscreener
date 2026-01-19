'use client'

import { Box, Flex, Heading, IconButton, Input, InputGroup, InputLeftElement, VStack, useDisclosure, Text } from "@chakra-ui/react";
import { Search, SlidersHorizontal } from "lucide-react";
import { MOCK_COINS } from "@/lib/mockData";
import { CoinItem } from "@/components/screener/CoinItem";
import { FilterDrawer } from "@/components/screener/FilterDrawer";
import { useState, useMemo } from "react";
import { ScreenerFilter } from "@/lib/types";

export default function ScreenerPage() {
  const { isOpen, onOpen, onClose } = useDisclosure();
  
  const [filters, setFilters] = useState<ScreenerFilter>({
    search: "",
    minPrice: "",
    maxPrice: "",
    marketCap: "all",
    priceChange: "all"
  });

  const filteredCoins = useMemo(() => {
    return MOCK_COINS.filter(coin => {
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
    });
  }, [filters]);

  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (filters.minPrice) count++;
    if (filters.maxPrice) count++;
    if (filters.marketCap !== 'all') count++;
    if (filters.priceChange !== 'all') count++;
    return count;
  }, [filters]);

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
        py={3}
      >
        <Flex justify="space-between" align="center" mb={3}>
          <Heading size="md">Market</Heading>
          
          <Box position="relative">
            <IconButton 
              aria-label="Filters" 
              icon={<SlidersHorizontal size={20} />} 
              variant={activeFilterCount > 0 ? "solid" : "ghost"}
              colorScheme={activeFilterCount > 0 ? "teal" : "gray"}
              size="sm"
              onClick={onOpen}
            />
            {activeFilterCount > 0 && (
              <Box 
                position="absolute" 
                top="-2px" 
                right="-2px" 
                bg="red.400" 
                w="2" 
                h="2" 
                borderRadius="full" 
              />
            )}
          </Box>
        </Flex>
        
        <InputGroup size="sm">
          <InputLeftElement pointerEvents="none">
            <Search color="gray.500" size={16} />
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
      </Box>

      {/* Coins List */}
      <VStack spacing={0} align="stretch" pb="20px">
        {filteredCoins.length > 0 ? (
          filteredCoins.map(coin => (
            <CoinItem key={coin.id} coin={coin} />
          ))
        ) : (
          <Box p={8} textAlign="center">
            <Text color="gray.500">No coins found matching filters.</Text>
          </Box>
        )}
      </VStack>

      <FilterDrawer 
        isOpen={isOpen} 
        onClose={onClose} 
        currentFilters={filters}
        onApply={(newFilters) => setFilters(newFilters)}
      />
    </Box>
  );
}