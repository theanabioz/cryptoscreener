'use client'

import { Box } from '@chakra-ui/react'

interface SparklineProps {
  data: number[];
  color?: string;
  width?: number;
  height?: number;
}

export const Sparkline = ({ data, color = 'green.400', width = 60, height = 30 }: SparklineProps) => {
  if (!data || data.length < 2) return null;

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1; // Avoid division by zero

  const points = data.map((price, index) => {
    const x = (index / (data.length - 1)) * width;
    const y = height - ((price - min) / range) * height;
    return `${x},${y}`;
  }).join(' ');

  return (
    <Box width={`${width}px`} height={`${height}px`} color={color}>
      <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} fill="none">
        <polyline
          points={points}
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </Box>
  )
}
