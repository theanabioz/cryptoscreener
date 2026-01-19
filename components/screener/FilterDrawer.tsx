'use client'

import { 
  Drawer, 
  DrawerBody, 
  DrawerFooter, 
  DrawerHeader, 
  DrawerOverlay, 
  DrawerContent, 
  DrawerCloseButton,
  Button,
  VStack,
  Text,
  HStack,
  Input,
  InputGroup,
  InputLeftElement,
  SimpleGrid,
  useColorModeValue
} from '@chakra-ui/react'
import { ScreenerFilter, MarketCapFilter, PriceChangeFilter } from '@/lib/types'
import { useState, useEffect } from 'react'

interface FilterDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  currentFilters: ScreenerFilter;
  onApply: (filters: ScreenerFilter) => void;
}

export const FilterDrawer = ({ isOpen, onClose, currentFilters, onApply }: FilterDrawerProps) => {
  // Local state for the drawer (don't apply until user clicks Apply)
  const [localFilters, setLocalFilters] = useState<ScreenerFilter>(currentFilters);

  // Sync local state when drawer opens with current applied filters
  useEffect(() => {
    if (isOpen) {
      setLocalFilters(currentFilters);
    }
  }, [isOpen, currentFilters]);

  const handleApply = () => {
    onApply(localFilters);
    onClose();
  };

  const handleReset = () => {
    const resetState: ScreenerFilter = {
      search: currentFilters.search, // Keep search
      minPrice: '',
      maxPrice: '',
      marketCap: 'all',
      priceChange: 'all'
    };
    setLocalFilters(resetState);
  };

  const bgButton = useColorModeValue('gray.100', 'gray.700');
  const bgActive = 'brand.500';
  const textActive = 'white';

  const MCapButton = ({ label, value }: { label: string, value: MarketCapFilter }) => (
    <Button 
      size="sm" 
      variant={localFilters.marketCap === value ? 'solid' : 'outline'}
      colorScheme={localFilters.marketCap === value ? 'teal' : 'gray'}
      onClick={() => setLocalFilters({...localFilters, marketCap: value})}
    >
      {label}
    </Button>
  );

  return (
    <Drawer isOpen={isOpen} placement="bottom" onClose={onClose}>
      <DrawerOverlay />
      <DrawerContent borderTopRadius="20px">
        <DrawerCloseButton />
        <DrawerHeader>Filters</DrawerHeader>

        <DrawerBody>
          <VStack spacing={6} align="stretch">
            
            {/* Price Range */}
            <Box>
              <Text fontSize="sm" fontWeight="bold" mb={2}>Price ($)</Text>
              <HStack>
                <Input 
                  placeholder="Min" 
                  type="number" 
                  value={localFilters.minPrice}
                  onChange={(e) => setLocalFilters({...localFilters, minPrice: e.target.value})}
                />
                <Text>-</Text>
                <Input 
                  placeholder="Max" 
                  type="number" 
                  value={localFilters.maxPrice}
                  onChange={(e) => setLocalFilters({...localFilters, maxPrice: e.target.value})}
                />
              </HStack>
            </Box>

            {/* Market Cap */}
            <Box>
              <Text fontSize="sm" fontWeight="bold" mb={2}>Market Cap</Text>
              <SimpleGrid columns={2} spacing={2}>
                <MCapButton label="All" value="all" />
                <MCapButton label="High (> $1B)" value="high" />
                <MCapButton label="Mid ($100M - 1B)" value="mid" />
                <MCapButton label="Low (< $100M)" value="low" />
              </SimpleGrid>
            </Box>

            {/* 24h Change */}
            <Box>
              <Text fontSize="sm" fontWeight="bold" mb={2}>24h Change</Text>
              <HStack spacing={2} width="full">
                {['all', 'gainers', 'losers'].map((type) => (
                   <Button
                    key={type}
                    flex={1}
                    size="sm"
                    variant={localFilters.priceChange === type ? 'solid' : 'outline'}
                    colorScheme={localFilters.priceChange === type ? 'teal' : 'gray'}
                    onClick={() => setLocalFilters({...localFilters, priceChange: type as PriceChangeFilter})}
                   >
                     {type.charAt(0).toUpperCase() + type.slice(1)}
                   </Button>
                ))}
              </HStack>
            </Box>

          </VStack>
        </DrawerBody>

        <DrawerFooter borderTopWidth="1px">
          <Button variant="outline" mr={3} onClick={handleReset}>
            Reset
          </Button>
          <Button colorScheme="teal" onClick={handleApply} width="full">
            Apply Filters
          </Button>
        </DrawerFooter>
      </DrawerContent>
    </Drawer>
  )
}

import { Box } from '@chakra-ui/react';
