'use client'

import { createChart, ColorType, IChartApi, CandlestickSeries } from 'lightweight-charts';
import { useEffect, useRef } from 'react';
import { Box } from '@chakra-ui/react';

interface DetailChartProps {
  coinId: string;
  basePrice: number;
  isPositive: boolean;
}

export const DetailChart = ({ coinId, basePrice, isPositive }: DetailChartProps) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

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

    // Generate mock candle data
    const generateData = () => {
      let initialDate = Math.floor(new Date().getTime() / 1000) - (100 * 3600); // 100 hours ago
      let lastClose = basePrice;
      const data = [];

      for (let i = 0; i < 100; i++) {
        const open = lastClose;
        const volatility = basePrice * 0.02; // 2% volatility
        const change = (Math.random() - 0.5) * volatility;
        const close = open + change;
        const high = Math.max(open, close) + Math.random() * (volatility * 0.5);
        const low = Math.min(open, close) - Math.random() * (volatility * 0.5);
        
        data.push({
          time: initialDate + (i * 3600),
          open,
          high,
          low,
          close,
        });
        
        lastClose = close;
      }
      return data;
    };

    const data: any = generateData();
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
  }, [basePrice]);

  return <Box ref={chartContainerRef} w="full" h="300px" />;
};
