'use client';

import { useState, useCallback } from 'react';
import { Check, Download, Share2 } from 'lucide-react';
import { Button } from './Button';

const PUBLIC_TRY_URL = 'https://devenira.com/try';

interface ShareButtonsProps {
  imageUrl: string;
  title?: string;
  description?: string;
}

export function ShareButtons({
  imageUrl,
  title = 'My AI body transformation — Devenira',
  description = 'See your goal body before you get there. Try it free at devenira.com',
}: ShareButtonsProps) {
  const [copied, setCopied] = useState(false);
  const [sharing, setSharing] = useState(false);

  const fetchImageBlob = useCallback(async (): Promise<Blob | null> => {
    try {
      const res = await fetch(imageUrl, { mode: 'cors' });
      if (!res.ok) return null;
      return await res.blob();
    } catch {
      return null;
    }
  }, [imageUrl]);

  const handleShare = useCallback(async () => {
    setSharing(true);
    try {
      const blob = await fetchImageBlob();

      if (blob && navigator.share && navigator.canShare) {
        const file = new File([blob], 'transformation.png', { type: blob.type || 'image/png' });
        if (navigator.canShare({ files: [file] })) {
          await navigator.share({ title, text: description, files: [file] });
          return;
        }
      }

      // Fallback: share the public landing URL
      if (navigator.share) {
        await navigator.share({ title, text: description, url: PUBLIC_TRY_URL });
        return;
      }

      // Final fallback: download the image
      if (blob) {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.download = 'transformation.png';
        link.href = url;
        link.click();
        URL.revokeObjectURL(url);
      }
    } catch (err) {
      if ((err as Error).name !== 'AbortError') console.error(err);
    } finally {
      setSharing(false);
    }
  }, [fetchImageBlob, title, description]);

  const handleDownload = useCallback(async () => {
    const blob = await fetchImageBlob();
    if (!blob) return;
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.download = 'transformation.png';
    link.href = url;
    link.click();
    URL.revokeObjectURL(url);
  }, [fetchImageBlob]);

  const handleCopyLink = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(`${title}\n\n${PUBLIC_TRY_URL}`);
    } catch {
      // ignore clipboard errors
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [title]);

  return (
    <div className="flex gap-2 mt-2">
      <Button variant="outline" size="sm" onClick={handleShare} disabled={sharing}>
        <Share2 className="w-4 h-4 mr-1.5" />
        Share
      </Button>
      <Button variant="outline" size="sm" onClick={handleDownload}>
        <Download className="w-4 h-4 mr-1.5" />
        Save
      </Button>
      <Button variant="outline" size="sm" onClick={handleCopyLink}>
        {copied ? <Check className="w-4 h-4" /> : <Share2 className="w-4 h-4" />}
      </Button>
    </div>
  );
}
