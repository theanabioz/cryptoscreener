import { useEffect, useRef } from 'react';
import { useHaptic } from './useHaptic';

export const useScrollHaptic = (threshold: number = 50) => {
  const { selectionChanged } = useHaptic();
  const lastScrollY = useRef(0);
  const ticking = useRef(false);

  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      const diff = Math.abs(currentScrollY - lastScrollY.current);

      if (diff >= threshold) {
        if (!ticking.current) {
          window.requestAnimationFrame(() => {
            selectionChanged();
            lastScrollY.current = currentScrollY;
            ticking.current = false;
          });
          ticking.current = true;
        }
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });

    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, [threshold, selectionChanged]);
};
