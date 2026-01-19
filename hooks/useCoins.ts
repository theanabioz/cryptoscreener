import { useQuery } from '@tanstack/react-query';
import { Coin } from '@/lib/types';
import { MOCK_COINS } from '@/lib/mockData';

const fetchCoins = async (ids?: string): Promise<Coin[]> => {
  // Use our internal Next.js API route which acts as a secure proxy to the Python backend
  // Add timestamp to prevent caching and optional ids
  const url = ids 
    ? `/api/coins?ids=${ids}&ts=${new Date().getTime()}`
    : `/api/coins?ts=${new Date().getTime()}`;
    
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error('Network response was not ok');
  }
  return res.json();
};

export const useCoins = (ids?: string) => {
  return useQuery({
    queryKey: ['coins', ids],
    queryFn: () => fetchCoins(ids),
    staleTime: 1000, // 1 second fresh
    refetchInterval: 1000, // Poll every 1 second
    retry: 2,
  });
};
