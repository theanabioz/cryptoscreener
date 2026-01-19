'use client'

import { Box, Button, Heading, HStack, Input, SimpleGrid, Text, VStack, useColorModeValue } from '@chakra-ui/react'
import { useRouter } from 'next/navigation'
import { useTelegramBackButton } from '@/hooks/useTelegramBackButton'
import { useFilterStore } from '@/store/filterStore'
import { MarketCapFilter, PriceChangeFilter } from '@/lib/types'
import { useEffect, useState } from 'react'

export default function FiltersPage() {
  const router = useRouter();
  useTelegramBackButton(); // Enable Back Button
  
  const { filters, setFilters, resetFilters } = useFilterStore();
  
  // Local state for editing (apply only on "Show Results")
  // Or in this case, we can update global store directly?
  // Let's update global directly for simplicity, or use local state if we want "Cancel" behavior.
  // Standard mobile pattern: Apply immediately or "Show X Results" button. 
  // Let's stick to "Apply" button pattern for clarity.
  const [localFilters, setLocalFilters] = useState(filters);

  const handleApply = () => {
    setFilters(localFilters);
    router.back();
  };

  const handleReset = () => {
    const resetState = {
      ...localFilters,
      minPrice: '',
      maxPrice: '',
      marketCap: 'all' as MarketCapFilter,
      priceChange: 'all' as PriceChangeFilter
    };
    setLocalFilters(resetState);
    // Optional: reset global too?
    // resetFilters(); 
  };

  const MCapButton = ({ label, value }: { label: string, value: MarketCapFilter }) => (
    <Button 
      size="sm" 
      variant={localFilters.marketCap === value ? 'solid' : 'outline'}
      colorScheme={localFilters.marketCap === value ? 'teal' : 'gray'}
      onClick={() => setLocalFilters({...localFilters, marketCap: value})}
      whiteSpace="normal"
      h="auto"
      py={2}
      fontSize="xs"
      borderColor="gray.600"
    >
      {label}
    </Button>
  );

  return (
    <Box pb="100px" minH="100vh" bg="gray.900">
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
        <Flex justify="center" align="center" h="40px" mb={2}>
          <Heading size="md">Filters</Heading>
        </Flex>
      </Box>

      {/* Content */}
      <VStack spacing={6} align="stretch" p={4}>
        
        {/* Price Range */}
        <Box>
          <Text fontSize="sm" fontWeight="bold" mb={2} color="gray.300">Price ($)</Text>
          <HStack>
            <Input 
              placeholder="Min" 
              type="number" 
              value={localFilters.minPrice}
              onChange={(e) => setLocalFilters({...localFilters, minPrice: e.target.value})}
              bg="gray.800"
              borderColor="gray.600"
            />
            <Text>-</Text>
            <Input 
              placeholder="Max" 
              type="number" 
              value={localFilters.maxPrice}
              onChange={(e) => setLocalFilters({...localFilters, maxPrice: e.target.value})}
              bg="gray.800"
              borderColor="gray.600"
            />
          </HStack>
        </Box>

        {/* Market Cap */}
        <Box>
          <Text fontSize="sm" fontWeight="bold" mb={2} color="gray.300">Market Cap</Text>
          <SimpleGrid columns={2} spacing={2}>
            <MCapButton label="All" value="all" />
            <MCapButton label="High (>1B)" value="high" />
            <MCapButton label="Mid (100M-1B)" value="mid" />
            <MCapButton label="Low (<100M)" value="low" />
          </SimpleGrid>
        </Box>

        {/* 24h Change */}
        <Box>
          <Text fontSize="sm" fontWeight="bold" mb={2} color="gray.300">24h Change</Text>
          <HStack spacing={2} width="full">
            {['all', 'gainers', 'losers'].map((type) => (
               <Button
                key={type}
                flex={1}
                size="sm"
                variant={localFilters.priceChange === type ? 'solid' : 'outline'}
                colorScheme={localFilters.priceChange === type ? 'teal' : 'gray'}
                onClick={() => setLocalFilters({...localFilters, priceChange: type as PriceChangeFilter})}
                borderColor="gray.600"
               >
                 {type.charAt(0).toUpperCase() + type.slice(1)}
               </Button>
            ))}
          </HStack>
        </Box>

      </VStack>

      {/* Footer Buttons */}
      <Box p={4} borderTopWidth="1px" borderColor="gray.800" mt="auto">
        <HStack spacing={4}>
            <Button variant="ghost" flex={1} onClick={handleReset} color="gray.400">
                Reset
            </Button>
            <Button colorScheme="teal" flex={2} onClick={handleApply}>
                Show Results
            </Button>
        </HStack>
      </Box>
    </Box>
  )
}

import { Flex } from '@chakra-ui/react';
