import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

interface WatchlistState {
  favorites: string[];
  addCoin: (id: string) => void;
  removeCoin: (id: string) => void;
  toggleCoin: (id: string) => void;
  isFavorite: (id: string) => boolean;
}

export const useWatchlistStore = create<WatchlistState>()(
  persist(
    (set, get) => ({
      favorites: [],
      addCoin: (id) => set((state) => ({ favorites: [...state.favorites, id] })),
      removeCoin: (id) => set((state) => ({ favorites: state.favorites.filter((fid) => fid !== id) })),
      toggleCoin: (id) => {
        const { favorites } = get();
        if (favorites.includes(id)) {
          set({ favorites: favorites.filter((fid) => fid !== id) });
        } else {
          set({ favorites: [...favorites, id] });
        }
      },
      isFavorite: (id) => get().favorites.includes(id),
    }),
    {
      name: 'watchlist-storage', // name of the item in the storage (must be unique)
      storage: createJSONStorage(() => localStorage), // (optional) by default, 'localStorage' is used
    }
  )
)
