'use client'

import { Box, Spinner, Center } from '@chakra-ui/react'
import { motion, useMotionValue, useTransform, useAnimation, PanInfo } from 'framer-motion'
import { useState, useEffect, ReactNode } from 'react'
import { useHaptic } from '@/hooks/useHaptic'

interface PullToRefreshProps {
  children: ReactNode;
  onRefresh: () => Promise<void>;
}

export const PullToRefresh = ({ children, onRefresh }: PullToRefreshProps) => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const y = useMotionValue(0);
  const controls = useAnimation();
  const { impact, notification } = useHaptic();
  
  // Spinner opacity and rotation based on pull distance
  const opacity = useTransform(y, [0, 60], [0, 1]);
  const rotate = useTransform(y, [0, 80], [0, 360]);

  const handlePanEnd = async (_: any, info: PanInfo) => {
    // Threshold to trigger refresh
    if (y.get() > 80 && window.scrollY === 0) {
      setIsRefreshing(true);
      impact('medium');
      
      // Snap to loading position
      await controls.start({ y: 60 });
      
      // Execute refresh
      await onRefresh();
      
      notification('success');
      setIsRefreshing(false);
      controls.start({ y: 0 });
    } else {
      controls.start({ y: 0 });
    }
  };

  const handlePan = (_: any, info: PanInfo) => {
    // Only allow pull down if at top of page and not already refreshing
    if (window.scrollY === 0 && !isRefreshing && info.offset.y > 0) {
      // Add resistance
      const newY = info.offset.y * 0.4;
      y.set(newY);
      controls.set({ y: newY });
    }
  };

  return (
    <Box position="relative" overflow="hidden">
      {/* Loading Spinner Container - Absolute at top */}
      <Box 
        position="absolute" 
        top={0} 
        left={0} 
        right={0} 
        height="60px" 
        display="flex" 
        justifyContent="center" 
        alignItems="center"
        zIndex={0}
      >
        <motion.div style={{ opacity, rotate }}>
          <Spinner color="brand.400" />
        </motion.div>
      </Box>

      {/* Main Content Wrapper */}
      <motion.div
        drag="y"
        dragConstraints={{ top: 0, bottom: 0 }} // We handle movement manually
        dragElastic={0} // Disable default elasticity
        onDrag={handlePan}
        onDragEnd={handlePanEnd}
        animate={controls}
        style={{ position: 'relative', zIndex: 1, touchAction: 'pan-y' }}
      >
        {children}
      </motion.div>
    </Box>
  )
}
