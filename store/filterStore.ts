import { create } from 'zustand'
import { ScreenerFilter } from '@/lib/types'

interface FilterState {
  filters: ScreenerFilter;
  setFilters: (filters: ScreenerFilter) => void;
  resetFilters: () => void;
  activeFilterCount: () => number;
}

const initialFilters: ScreenerFilter = {
  search: "",
  minPrice: "",
  maxPrice: "",
  marketCap: "all",
  priceChange: "all"
};

export const useFilterStore = create<FilterState>((set, get) => ({
  filters: initialFilters,
  setFilters: (newFilters) => set({ filters: newFilters }),
  resetFilters: () => set({ filters: { ...initialFilters, search: get().filters.search } }), // Keep search query
  activeFilterCount: () => {
    const { filters } = get();
    let count = 0;
    if (filters.minPrice) count++;
    if (filters.maxPrice) count++;
    if (filters.marketCap !== 'all') count++;
    if (filters.priceChange !== 'all') count++;
    return count;
  }
}))
