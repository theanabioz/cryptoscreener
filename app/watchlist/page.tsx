'use client'

import { Box, Heading, Text, Center } from '@chakra-ui/react'

export default function WatchlistPage() {
  return (
    <Box p={4} pb="80px">
      <Heading size="md" mb={4}>Watchlist</Heading>
      <Center h="50vh">
        <Text color="gray.500">Your favorite coins will appear here.</Text>
      </Center>
    </Box>
  )
}
