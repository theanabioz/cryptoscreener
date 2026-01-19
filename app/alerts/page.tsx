'use client'

import { Box, Heading, Text, Center } from '@chakra-ui/react'

export default function AlertsPage() {
  return (
    <Box p={4} pb="80px">
      <Heading size="md" mb={4}>Alerts</Heading>
      <Center h="50vh">
        <Text color="gray.500">No active alerts configured.</Text>
      </Center>
    </Box>
  )
}
