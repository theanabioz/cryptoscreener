'use client'

import { Box, Flex, HStack, Skeleton, SkeletonCircle, SkeletonText, VStack } from '@chakra-ui/react'

export const CoinSkeleton = () => {
  return (
    <Box 
      w="full" 
      p={3} 
      borderBottomWidth="1px" 
      borderColor="gray.800"
    >
      <Flex justify="space-between" align="center">
        {/* Left: Icon + Name */}
        <HStack spacing={3} w="35%">
          <SkeletonCircle size="8" />
          <VStack align="start" spacing={1} width="full">
            <Skeleton height="14px" width="60%" />
            <Skeleton height="10px" width="80%" />
          </VStack>
        </HStack>

        {/* Middle: Sparkline */}
        <Box w="30%" display="flex" justifyContent="center">
          <Skeleton height="30px" width="80px" />
        </Box>

        {/* Right: Price + Change */}
        <VStack align="end" spacing={1} w="35%">
          <Skeleton height="14px" width="80%" />
          <Skeleton height="16px" width="50px" borderRadius="sm" />
        </VStack>
      </Flex>
    </Box>
  )
}
