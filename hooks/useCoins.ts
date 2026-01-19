import { useQuery } from '@tanstack/react-query';
import { Coin } from '@/lib/types';
import { MOCK_COINS } from '@/lib/mockData';

const fetchCoins = async (): Promise<Coin[]> => {
  // Use our internal Next.js API route which acts as a secure proxy to the Python backend
  // Add timestamp to prevent caching
  const res = await fetch(`/api/coins?ts=${new Date().getTime()}`);
  if (!res.ok) {
    throw new Error('Network response was not ok');
  }
  return res.json();
};

export const useCoins = () => {
  return useQuery({
    queryKey: ['coins'],
    queryFn: fetchCoins,
    staleTime: 1000, // 1 second fresh
    refetchInterval: 1000, // Poll every 1 second
    retry: 2,
  });
};
