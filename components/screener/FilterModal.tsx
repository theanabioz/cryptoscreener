'use client'

import { 
  Modal, 
  ModalOverlay, 
  ModalContent, 
  ModalHeader, 
  ModalFooter, 
  ModalBody, 
  ModalCloseButton,
  Button,
  VStack,
  Text,
  HStack,
  Input,
  SimpleGrid,
  useColorModeValue,
  Box
} from '@chakra-ui/react'
import { ScreenerFilter, MarketCapFilter, PriceChangeFilter } from '@/lib/types'
import { useState, useEffect } from 'react'

interface FilterModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentFilters: ScreenerFilter;
  onApply: (filters: ScreenerFilter) => void;
}

export const FilterModal = ({ isOpen, onClose, currentFilters, onApply }: FilterModalProps) => {
  const [localFilters, setLocalFilters] = useState<ScreenerFilter>(currentFilters);

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
      search: currentFilters.search, 
      minPrice: '',
      maxPrice: '',
      marketCap: 'all',
      priceChange: 'all'
    };
    setLocalFilters(resetState);
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
    >
      {label}
    </Button>
  );

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={onClose} 
      size="full" // Full screen approach for stability
      motionPreset="slideInBottom" // Slide up like a native page
    >
      <ModalContent 
        m={0}
        borderRadius={0}
        bg="gray.900" 
        containerProps={{
          zIndex: 2000 // Ensure it's on top of everything
        }}
      >
        <ModalHeader 
          borderBottomWidth="1px" 
          borderColor="gray.800"
          pt="calc(12px + env(safe-area-inset-top))" // Safe area padding
        >
          Filters
        </ModalHeader>
        <ModalCloseButton mt="calc(6px + env(safe-area-inset-top))" />
        
        <ModalBody py={6}>
          <VStack spacing={6} align="stretch">
            
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
        </ModalBody>

        <ModalFooter borderTopWidth="1px" borderColor="gray.800">
          <Button variant="ghost" mr={3} onClick={handleReset} color="gray.400">
            Reset
          </Button>
          <Button colorScheme="teal" onClick={handleApply}>
            Apply Filters
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}
