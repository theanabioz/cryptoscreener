'use client'

import { Box, Heading, Text, Center, Flex } from '@chakra-ui/react'

export default function AlertsPage() {
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
        <Flex justify="center" align="center" h="40px" mb={2}>
          <Heading size="md">Alerts</Heading>
        </Flex>
      </Box>

      <Center h="60vh" flexDirection="column" px={8} textAlign="center">
        <Text fontSize="4xl" mb={4}>🔔</Text>
        <Heading size="sm" mb={2}>Coming Soon</Heading>
        <Text color="gray.500" fontSize="sm">
          Price alerts and notifications will be available in the next update.
        </Text>
      </Center>
    </Box>
  )
}