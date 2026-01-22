'use client'

import { createChart, ColorType, IChartApi, CandlestickSeries, ISeriesApi } from 'lightweight-charts';
import { useEffect, useRef, useState } from 'react';
import { Box, HStack, Button, Spinner, Center, Text } from '@chakra-ui/react';
// useKlines removed

export const TIMEFRAMES = ['1M', '3M', '5M', '15M', '30M', '1H', '4H', '1D', '1W'];

interface Kline {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
}

interface DetailChartProps {
  coinId: string; // This is actually 'btc', 'eth'
  symbol: string; // This should be 'BTC', 'ETH' for API
  basePrice: number;
  isPositive: boolean;
  klines: Kline[] | undefined;
  isLoading: boolean;
  isError: boolean;
  activeTf: string;
  onTfChange: (tf: string) => void;
}

export const DetailChart = ({ coinId, symbol, basePrice, isPositive, klines, isLoading, isError, activeTf, onTfChange }: DetailChartProps) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current || !klines || klines.length === 0) return;

    // Clean up previous chart if any (manual DOM cleanup to be sure)
    chartContainerRef.current.innerHTML = '';

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: '#A0AEC0',
      },
      grid: {
        vertLines: { color: '#2D3748' },
        horzLines: { color: '#2D3748' },
      },
      width: chartContainerRef.current.clientWidth,
      height: 300,
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
    });

    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#48BB78',
      downColor: '#F56565',
      borderVisible: false,
      wickUpColor: '#48BB78',
      wickDownColor: '#F56565',
    });
    
    candlestickSeries.setData(klines as any);
    seriesRef.current = candlestickSeries;
    
    chart.timeScale().fitContent();

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [klines]); // Re-run when data changes (tf change triggers klines change)

  // Real-time chart update
  useEffect(() => {
    if (seriesRef.current && klines && klines.length > 0 && basePrice) {
      const lastCandle = klines[klines.length - 1];
      const updatedCandle = {
        ...lastCandle,
        close: basePrice,
        high: Math.max(lastCandle.high, basePrice),
        low: Math.min(lastCandle.low, basePrice),
      };
      seriesRef.current.update(updatedCandle as any);
    }
  }, [basePrice, klines]);

  return (
    <Box w="full">
      <Box overflowX="auto" pb={2} px={4} sx={{
          '&::-webkit-scrollbar': { display: 'none' },
          'scrollbarWidth': 'none',
          '-ms-overflow-style': 'none'
      }}>
        <HStack spacing={2} minW="max-content">
            {TIMEFRAMES.map((tf) => (
            <Button
                key={tf}
                size="xs"
                variant={activeTf === tf ? 'solid' : 'outline'}
                colorScheme={activeTf === tf ? 'teal' : 'gray'}
                onClick={() => onTfChange(tf)}
                borderRadius="full"
                px={4}
                minW="45px"
            >
                {tf}
            </Button>
            ))}
        </HStack>
      </Box>
      
      <Box position="relative" w="full" h="300px">
        {isLoading && (
          <Center position="absolute" top={0} left={0} right={0} bottom={0} zIndex={10}>
            <Spinner color="brand.400" />
          </Center>
        )}
        {isError && (
          <Center position="absolute" top={0} left={0} right={0} bottom={0} zIndex={10}>
            <Text color="red.400" fontSize="sm">Error loading chart</Text>
          </Center>
        )}
        <Box ref={chartContainerRef} w="full" h="100%" />
      </Box>
    </Box>
  );
};
