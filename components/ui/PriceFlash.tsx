'use client'

import { Text, Box } from '@chakra-ui/react';
import { motion, useAnimation } from 'framer-motion';
import { useEffect, useRef } from 'react';

interface PriceFlashProps {
  price: number;
  fontSize?: string;
  fontWeight?: string;
  color?: string;
}

const MotionBox = motion(Box);

export const PriceFlash = ({ price, fontSize = "sm", fontWeight = "medium", color = "white" }: PriceFlashProps) => {
  const prevPriceRef = useRef<number>(price);
  const controls = useAnimation();

  useEffect(() => {
    if (price > prevPriceRef.current) {
      // Flash Green
      controls.start({
        color: ['#48BB78', color],
        transition: { duration: 0.5 }
      });
    } else if (price < prevPriceRef.current) {
      // Flash Red
      controls.start({
        color: ['#F56565', color],
        transition: { duration: 0.5 }
      });
    }
    prevPriceRef.current = price;
  }, [price, color, controls]);

  return (
    <MotionBox animate={controls} style={{ color }}>
      <Text fontSize={fontSize} fontWeight={fontWeight}>
        ${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 6 })}
      </Text>
    </MotionBox>
  );
};
