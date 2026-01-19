'use client'

import { Box, Heading, Text, VStack, Avatar, Divider, Button } from '@chakra-ui/react'
import { useEffect, useState } from 'react'

interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
}

export default function ProfilePage() {
  const [user, setUser] = useState<TelegramUser | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
      const tgUser = window.Telegram.WebApp.initDataUnsafe?.user;
      if (tgUser) {
        setUser(tgUser as TelegramUser);
      }
    }
  }, []);

  return (
    <Box p={4} pb="80px" pt="calc(20px + env(safe-area-inset-top))">
      <Heading size="md" mb={6}>Profile</Heading>
      
      <VStack spacing={4} align="start">
        <Box display="flex" alignItems="center" gap={4}>
          <Avatar 
            size="lg" 
            name={user?.first_name || "Guest User"} 
            src={user?.photo_url} 
            bg="brand.500" 
          />
          <Box>
            <Text fontWeight="bold" fontSize="lg">
              {user ? `${user.first_name} ${user.last_name || ''}` : 'Guest User'}
            </Text>
            <Text color="gray.500" fontSize="sm">
              {user?.username ? `@${user.username}` : 'Not connected'}
            </Text>
          </Box>
        </Box>

        <Divider my={4} borderColor="gray.700" />

        <Button w="full" variant="outline" colorScheme="gray">Settings</Button>
        <Button w="full" variant="outline" colorScheme="gray">Theme</Button>
        <Button w="full" variant="outline" colorScheme="red">Log Out</Button>
      </VStack>

      {!user && (
        <Text fontSize="xs" color="gray.600" mt={4} textAlign="center">
          Open this app in Telegram to see your profile.
        </Text>
      )}
    </Box>
  )
}
