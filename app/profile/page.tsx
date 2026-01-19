'use client'

import { Box, Heading, Text, VStack, Avatar, Divider, Button } from '@chakra-ui/react'

export default function ProfilePage() {
  return (
    <Box p={4} pb="80px">
      <Heading size="md" mb={6}>Profile</Heading>
      
      <VStack spacing={4} align="start">
        <Box display="flex" alignItems="center" gap={4}>
          <Avatar size="lg" name="User" bg="brand.500" />
          <Box>
            <Text fontWeight="bold" fontSize="lg">Telegram User</Text>
            <Text color="gray.500" fontSize="sm">@username</Text>
          </Box>
        </Box>

        <Divider my={4} />

        <Button w="full" variant="outline" colorScheme="gray">Settings</Button>
        <Button w="full" variant="outline" colorScheme="gray">Theme</Button>
        <Button w="full" variant="outline" colorScheme="red">Log Out</Button>
      </VStack>
    </Box>
  )
}
