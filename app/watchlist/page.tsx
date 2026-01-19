'use client'

import { Box, Heading, Text, Center, VStack } from '@chakra-ui/react'
import { useWatchlistStore } from '@/store/useWatchlistStore'
import { CoinItem } from '@/components/screener/CoinItem'
import { useEffect, useState } from 'react'
import { useCoins } from '@/hooks/useCoins'

export default function WatchlistPage() {

  const { favorites } = useWatchlistStore();

  

  // Fetch only favorites from API

  const { data: watchlistCoins, isLoading: isQueryLoading } = useCoins(

    favorites.length > 0 ? favorites.join(',') : undefined

  );



  const [isHydrated, setIsHydrated] = useState(false);



  // Prevent hydration mismatch

  useEffect(() => {

    setIsHydrated(true);

  }, []);



  if (!isHydrated) {

    return <Box p={4}><Heading size="md">Watchlist</Heading></Box>; // Loading state

  }



  // If favorites list is empty, don't even wait for API

  if (favorites.length === 0) {

    return (

      <Box>

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

          pt="calc(10px + env(safe-area-inset-top))"

        >

          <Heading size="md" mb={2} textAlign="center">Watchlist</Heading>

        </Box>

        <Center h="60vh" flexDirection="column" px={8} textAlign="center">

          <Text fontSize="4xl" mb={4}>⭐</Text>

          <Heading size="sm" mb={2}>Your Watchlist is empty</Heading>

          <Text color="gray.500" fontSize="sm">

            Tap the star icon on any coin detail page to add it here.

          </Text>

        </Center>

      </Box>

    );

  }



  return (

    <Box>

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

        pt="calc(10px + env(safe-area-inset-top))"

      >

        <Heading size="md" mb={2} textAlign="center">Watchlist</Heading>

      </Box>



      {watchlistCoins && watchlistCoins.length > 0 ? (

        <VStack spacing={0} align="stretch" pb="20px">

          {watchlistCoins.map(coin => (

            <CoinItem key={coin.id} coin={coin} />

          ))}

        </VStack>

      ) : (

        <Center h="60vh">

           {isQueryLoading ? <Spinner color="brand.400" /> : <Text color="gray.500">Loading favorites...</Text>}

        </Center>

      )}

    </Box>

  )

}
