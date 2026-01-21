import { useQuery } from '@tanstack/react-query';
import { Coin } from '@/lib/types';
import { MOCK_COINS } from '@/lib/mockData';

const fetchCoins = async (ids?: string, strategy?: string): Promise<Coin[]> => {
  // Use our internal Next.js API route which acts as a secure proxy to the Python backend
  const params = new URLSearchParams();
  if (ids) params.append('ids', ids);
  if (strategy) params.append('strategy', strategy);
  params.append('ts', new Date().getTime().toString());

  const res = await fetch(`/api/coins?${params.toString()}`);
  if (!res.ok) {
    throw new Error('Network response was not ok');
  }
  return res.json();
};

export const useCoins = (ids?: string, strategy?: string) => {
  return useQuery({
    queryKey: ['coins', ids, strategy],
    queryFn: () => fetchCoins(ids, strategy),
    staleTime: 1000, 
    refetchInterval: 1000, 
    retry: 2,
  });
};
