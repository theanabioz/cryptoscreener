'use client'

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export const useTelegramBackButton = () => {
  const router = useRouter();

  useEffect(() => {
    // Check for window existence and Telegram object
    if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
      const tg = window.Telegram.WebApp;
      const backButton = tg.BackButton;

      const handleBack = () => {
        router.back();
      };

      if (backButton) {
        backButton.show();
        backButton.onClick(handleBack);
      }

      return () => {
        if (backButton) {
          backButton.hide();
          backButton.offClick(handleBack);
        }
      };
    }
  }, [router]);
};
