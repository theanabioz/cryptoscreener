'use client'

import { useCallback } from 'react';

// Define types safely for TWA SDK
type ImpactStyle = 'light' | 'medium' | 'heavy' | 'rigid' | 'soft';
type NotificationType = 'error' | 'success' | 'warning';

export const useHaptic = () => {
  const impact = useCallback((style: ImpactStyle) => {
    // Check if running in browser environment first
    if (typeof window !== 'undefined') {
      // Dynamic import or check global object to avoid SSR issues
      // @ts-ignore
      const TWA = window.Telegram?.WebApp;
      if (TWA?.HapticFeedback) {
        TWA.HapticFeedback.impactOccurred(style);
      }
    }
  }, []);

  const notification = useCallback((type: NotificationType) => {
    if (typeof window !== 'undefined') {
      // @ts-ignore
      const TWA = window.Telegram?.WebApp;
      if (TWA?.HapticFeedback) {
        TWA.HapticFeedback.notificationOccurred(type);
      }
    }
  }, []);

  const selection = useCallback(() => {
    if (typeof window !== 'undefined') {
      // @ts-ignore
      const TWA = window.Telegram?.WebApp;
      if (TWA?.HapticFeedback) {
        TWA.HapticFeedback.selectionChanged();
      }
    }
  }, []);

  return { impact, notification, selection };
};
