'use client'

import { Box, Heading, Text, VStack, Avatar, Divider, Button, Flex } from '@chakra-ui/react'
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
          <Heading size="md">Profile</Heading>
        </Flex>
      </Box>
      
      <VStack spacing={4} align="stretch" p={4} pb="80px">
        <Box display="flex" alignItems="center" gap={4} p={2}>
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

        <VStack spacing={3}>
          <Button w="full" variant="outline" colorScheme="gray" justifyContent="start" py={6}>Settings</Button>
          <Button w="full" variant="outline" colorScheme="gray" justifyContent="start" py={6}>Theme</Button>
          <Button w="full" variant="outline" colorScheme="red" justifyContent="start" py={6}>Log Out</Button>
        </VStack>

        {!user && (
          <Text fontSize="xs" color="gray.600" mt={8} textAlign="center">
            Open this app in Telegram to see your profile.
          </Text>
        )}
      </VStack>
    </Box>
  )
}