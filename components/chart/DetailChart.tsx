'use client'

import { createChart, ColorType, IChartApi, CandlestickSeries } from 'lightweight-charts';
import { useEffect, useRef, useState } from 'react';
import { Box, HStack, Button } from '@chakra-ui/react';

interface DetailChartProps {
  coinId: string;
  basePrice: number;
  isPositive: boolean;
}

const TIMEFRAMES = ['1H', '4H', '1D', '1W'];

export const DetailChart = ({ coinId, basePrice, isPositive }: DetailChartProps) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const [activeTf, setActiveTf] = useState('1D');

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
      },
    });

    chartRef.current = chart;

    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#48BB78',
      downColor: '#F56565',
      borderVisible: false,
      wickUpColor: '#48BB78',
      wickDownColor: '#F56565',
    });

    // Generate mock candle data based on timeframe
    const generateData = () => {
      const stepMap: Record<string, number> = {
        '1H': 60,       // 1 minute candles (showing 1 hour)
        '4H': 300,      // 5 minute candles
        '1D': 3600,     // 1 hour candles
        '1W': 86400,    // 1 day candles
      };
      
      const step = stepMap[activeTf];
      let initialDate = Math.floor(new Date().getTime() / 1000) - (100 * step);
      let lastClose = basePrice;
      const data = [];

      for (let i = 0; i < 100; i++) {
        const open = lastClose;
        const volatility = basePrice * (activeTf === '1W' ? 0.1 : 0.02); // More volatility on 1W
        const change = (Math.random() - 0.5) * volatility;
        const close = open + change;
        const high = Math.max(open, close) + Math.random() * (volatility * 0.5);
        const low = Math.min(open, close) - Math.random() * (volatility * 0.5);
        
        data.push({
          time: initialDate + (i * step) as any,
          open,
          high,
          low,
          close,
        });
        
        lastClose = close;
      }
      return data;
    };

    const data = generateData();
    candlestickSeries.setData(data);

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
  }, [basePrice, activeTf]);

  return (
    <Box w="full">
      <HStack spacing={2} mb={4} px={4} justify="center">
        {TIMEFRAMES.map((tf) => (
          <Button
            key={tf}
            size="xs"
            variant={activeTf === tf ? 'solid' : 'outline'}
            colorScheme={activeTf === tf ? 'teal' : 'gray'}
            onClick={() => setActiveTf(tf)}
            borderRadius="full"
            px={4}
          >
            {tf}
          </Button>
        ))}
      </HStack>
      <Box ref={chartContainerRef} w="full" h="300px" />
    </Box>
  );
};
