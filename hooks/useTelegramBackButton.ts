'use client'

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export const useTelegramBackButton = () => {
  const router = useRouter();

  useEffect(() => {
    if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
      const tg = window.Telegram.WebApp;
      const backButton = tg.BackButton;

      const handleBack = () => {
        router.back();
      };

      backButton.show();
      backButton.onClick(handleBack);

      return () => {
        backButton.hide();
        backButton.offClick(handleBack);
      };
    }
  }, [router]);
};
