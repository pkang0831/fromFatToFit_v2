'use client';

import { Button } from './Button';

interface ShareButtonsProps {
  imageUrl: string;
  title?: string;
  description?: string;
}

export function ShareButtons({ imageUrl, title = 'My progress', description }: ShareButtonsProps) {
  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title,
          text: description,
          url: window.location.href,
        });
      } catch (err) {
        if ((err as Error).name !== 'AbortError') console.error(err);
      }
    } else {
      await navigator.clipboard.writeText(window.location.href);
    }
  };

  return (
    <div className="mt-2">
      <Button variant="outline" size="sm" onClick={handleShare}>
        Share
      </Button>
    </div>
  );
}
