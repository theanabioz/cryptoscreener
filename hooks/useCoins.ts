import { useQuery } from '@tanstack/react-query';
import { Coin } from '@/lib/types';
import { MOCK_COINS } from '@/lib/mockData';

const fetchCoins = async (): Promise<Coin[]> => {
  const res = await fetch('/api/proxy/coins');
  if (!res.ok) {
    throw new Error('Network response was not ok');
  }
  return res.json();
};

export const useCoins = () => {
  return useQuery({
    queryKey: ['coins'],
    queryFn: fetchCoins,
    staleTime: 1000 * 60, // 1 minute cache
    retry: 1,
    // Fallback to MOCK data if API fails (for demo purposes)
    initialData: MOCK_COINS 
  });
};
