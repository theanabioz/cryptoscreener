'use client'

import { Box, Flex, Text, VStack, useColorModeValue } from '@chakra-ui/react'
import { LayoutList, Star, Bell, User, ScanLine } from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useHaptic } from '@/hooks/useHaptic'

const NAV_ITEMS = [
  { label: 'Home', icon: LayoutList, href: '/' },
  { label: 'Watchlist', icon: Star, href: '/watchlist' },
  { label: 'Screener', icon: ScanLine, href: '/screener' },
  { label: 'Alerts', icon: Bell, href: '/alerts' },
  { label: 'Profile', icon: User, href: '/profile' },
]

export const BottomNav = () => {
  const pathname = usePathname()
  const { impact } = useHaptic()
  
  const bg = useColorModeValue('white', 'gray.900')
  const borderColor = useColorModeValue('gray.200', 'gray.800')
  const activeColor = 'brand.400'
  const inactiveColor = 'gray.500'

  return (
    <Box
      position="fixed"
      bottom={0}
      left={0}
      right={0}
      bg={bg}
      borderTop="1px"
      borderColor={borderColor}
      pb="env(safe-area-inset-bottom)" // Handle iPhone Home Indicator
      zIndex={1000}
    >
      <Flex justify="space-around" align="center" h="60px">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href
          const Icon = item.icon
          
          return (
            <Link 
              key={item.label} 
              href={item.href} 
              style={{ textDecoration: 'none' }}
              onClick={() => impact('light')}
            >
              <VStack spacing={0.5} w="60px" cursor="pointer" justify="center">
                <Icon 
                  size={24} 
                  color={isActive ? 'var(--chakra-colors-brand-400)' : 'var(--chakra-colors-gray-500)'} 
                />
                <Text 
                  fontSize="10px" 
                  color={isActive ? activeColor : inactiveColor}
                  fontWeight={isActive ? 'bold' : 'medium'}
                >
                  {item.label}
                </Text>
              </VStack>
            </Link>
          )
        })}
      </Flex>
    </Box>
  )
}
