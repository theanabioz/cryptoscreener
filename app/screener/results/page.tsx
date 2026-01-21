'use client'

import { Box, VStack, Heading, Text, Center, Spinner, IconButton } from "@chakra-ui/react";
import { ArrowLeft } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { AccordionCoinItem } from "@/components/screener/AccordionCoinItem";
import { useCoins } from "@/hooks/useCoins";
import { useTelegramBackButton } from "@/hooks/useTelegramBackButton";
import { Suspense } from "react";

function ResultsContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const strategy = searchParams.get('strategy') || '';
  
  // Custom hook for Telegram back button
  useTelegramBackButton();

  const { data: coins, isLoading } = useCoins(undefined, strategy);

  const getTitle = (s: string) => {
    switch(s) {
      case 'rsi-oversold': return 'RSI Oversold (<30)';
      case 'strong-trend': return 'Strong Uptrend';
      case 'pump-radar': return 'Pump Radar';
      case 'volatility': return 'High Volatility';
      default: return 'Results';
    }
  };

  return (
    <Box pt="calc(10px + env(safe-area-inset-top))">
      {/* Header */}
      <Box 
        position="sticky" 
        top={0} 
        zIndex={10} 
        bg="gray.900" 
        borderBottomWidth="1px" 
        borderColor="gray.800"
        px={4}
        pb={3}
      >
        <Box display="flex" alignItems="center" h="40px" mb={2}>
          <IconButton 
            aria-label="Back" 
            icon={<ArrowLeft size={24} />} 
            variant="ghost" 
            color="white"
            onClick={() => router.back()}
            mr={2}
          />
          <Heading size="md">{getTitle(strategy)}</Heading>
        </Box>
        <Text fontSize="xs" color="gray.500" px={2}>
          Showing matches based on live data.
        </Text>
      </Box>

      {/* List */}
      <VStack spacing={0} align="stretch" pb="20px">
        {isLoading ? (
          <Center h="200px">
            <Spinner color="brand.400" />
          </Center>
        ) : (
          coins && coins.length > 0 ? (
            coins.map(coin => (
              <AccordionCoinItem key={coin.id} coin={coin} />
            ))
          ) : (
            <Center h="200px" flexDirection="column">
              <Text color="gray.500" mb={2}>No coins found matching criteria.</Text>
              <Text fontSize="xs" color="gray.600">Try checking back later.</Text>
            </Center>
          )
        )}
      </VStack>
    </Box>
  );
}

export default function ScreenerResultsPage() {
  return (
    <Suspense fallback={<Center h="100vh"><Spinner /></Center>}>
      <ResultsContent />
    </Suspense>
  );
}
