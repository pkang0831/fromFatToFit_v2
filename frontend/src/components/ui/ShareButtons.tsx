'use client';

import React from 'react';
import { Share2, Download, Twitter } from 'lucide-react';
import toast from 'react-hot-toast';

interface ShareButtonsProps {
  imageUrl: string;
  title?: string;
  description?: string;
}

export function ShareButtons({ imageUrl, title = 'My Transformation Preview', description = 'Check out my fitness transformation preview!' }: ShareButtonsProps) {
  const handleDownload = async () => {
    try {
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'transformation-preview.png';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      toast.success('Image downloaded!');
    } catch {
      toast.error('Failed to download image');
    }
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        const response = await fetch(imageUrl);
        const blob = await response.blob();
        const file = new File([blob], 'transformation.png', { type: 'image/png' });
        await navigator.share({
          title,
          text: description,
          files: [file],
        });
      } catch {
        // User cancelled share
      }
    } else {
      try {
        await navigator.clipboard.writeText(description);
        toast.success('Copied to clipboard!');
      } catch {
        toast.error('Sharing not supported');
      }
    }
  };

  const handleTwitterShare = () => {
    const text = encodeURIComponent(`${description} 💪 #FitnessTransformation #FromFatToFit`);
    window.open(`https://twitter.com/intent/tweet?text=${text}`, '_blank');
  };

  return (
    <div className="flex items-center gap-2 mt-4">
      <button
        onClick={handleDownload}
        className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-xl hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-sm font-medium"
      >
        <Download className="w-4 h-4" />
        Save
      </button>
      <button
        onClick={handleShare}
        className="flex items-center gap-2 px-4 py-2 bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 rounded-xl hover:bg-blue-200 dark:hover:bg-blue-900/60 transition-colors text-sm font-medium"
      >
        <Share2 className="w-4 h-4" />
        Share
      </button>
      <button
        onClick={handleTwitterShare}
        className="flex items-center gap-2 px-4 py-2 bg-sky-100 dark:bg-sky-900/40 text-sky-700 dark:text-sky-300 rounded-xl hover:bg-sky-200 dark:hover:bg-sky-900/60 transition-colors text-sm font-medium"
      >
        <Twitter className="w-4 h-4" />
        Tweet
      </button>
    </div>
  );
}
