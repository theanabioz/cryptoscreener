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
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);

  // 1. Initialize Chart ONCE
  useEffect(() => {
    if (!chartContainerRef.current) return;

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
        borderVisible: false,
        barSpacing: 12, // Оптимальная ширина для мобильных (влезет ~30-40 свечей)
        rightOffset: 2,
      },
      rightPriceScale: {
        borderVisible: false,
      },
    });

    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#48BB78',
      downColor: '#F56565',
      borderVisible: false,
      wickUpColor: '#48BB78',
      wickDownColor: '#F56565',
    });
    
    chartRef.current = chart;
    seriesRef.current = candlestickSeries;

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
      chartRef.current = null;
      seriesRef.current = null;
    };
  }, []); // Run once on mount

  // 2. Update Data when klines change
  useEffect(() => {
    if (seriesRef.current && klines && klines.length > 0) {
      seriesRef.current.setData(klines as any);
      // chartRef.current?.timeScale().fitContent(); // Удалено для сохранения масштаба
    }
  }, [klines]);

  // Real-time chart update
  useEffect(() => {
    if (seriesRef.current && basePrice && klines && klines.length > 0) {
      const lastK = klines[klines.length - 1];
      
      // Helper to convert TF string to seconds
      const getTfSeconds = (tf: string): number => {
        const upper = tf.toUpperCase();
        const val = parseInt(upper);
        if (isNaN(val)) return 60;
        if (upper.endsWith('M')) return val * 60;
        if (upper.endsWith('H')) return val * 3600;
        if (upper.endsWith('D')) return val * 86400;
        if (upper.endsWith('W')) return val * 604800;
        return 60;
      };

      const tfSeconds = getTfSeconds(activeTf);
      // Floor current time to the start of the timeframe bucket (in seconds)
      const candleTime = Math.floor(Date.now() / 1000 / tfSeconds) * tfSeconds;

      if (candleTime === lastK.time) {
        // Updating current existing candle (the one fetched from history)
        seriesRef.current.update({
          time: lastK.time as any,
          open: lastK.open,
          high: Math.max(lastK.high, basePrice),
          low: Math.min(lastK.low, basePrice),
          close: basePrice,
        });
      } else if (candleTime > lastK.time) {
        // Creating a new live candle (minute/hour/day just changed)
        // Continuity: New Open MUST equal Previous Close
        seriesRef.current.update({
          time: candleTime as any,
          open: lastK.close,
          high: Math.max(lastK.close, basePrice),
          low: Math.min(lastK.close, basePrice),
          close: basePrice,
        });
      }
    }
  }, [basePrice, activeTf, klines]);

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
