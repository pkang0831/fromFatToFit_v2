'use client';

import { useState } from 'react';
import Image from 'next/image';
import { motion, AnimatePresence } from 'framer-motion';
import { Shirt, Sun, Leaf, Snowflake, CloudRain, Sparkles, Palette } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, Button, Badge } from '@/components/ui';
import { fashionApi } from '@/lib/api/services';
import { useAuth } from '@/contexts/AuthContext';
import type { OutfitRecommendation } from '@/types/api';

const seasons = [
  { id: 'spring', label: 'Spring', icon: Sun, gradient: 'from-pink-400 to-rose-500' },
  { id: 'summer', label: 'Summer', icon: CloudRain, gradient: 'from-cyan-400 to-blue-500' },
  { id: 'fall', label: 'Fall', icon: Leaf, gradient: 'from-amber-400 to-orange-500' },
  { id: 'winter', label: 'Winter', icon: Snowflake, gradient: 'from-slate-400 to-indigo-500' },
];

export default function FashionPage() {
  const { user } = useAuth();
  const [activeSeason, setActiveSeason] = useState('spring');
  const [outfits, setOutfits] = useState<Record<string, OutfitRecommendation[]>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [personalColor, setPersonalColor] = useState('');
  const [bestColors, setBestColors] = useState('');

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await fashionApi.recommend({
        season: activeSeason,
        gender: user?.gender || 'female',
        height_cm: user?.height_cm || undefined,
        personal_color: personalColor,
        best_colors: bestColors,
        generate_images: false,
      });

      setOutfits((prev) => ({
        ...prev,
        [activeSeason]: res.data.outfits,
      }));
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message || 'Failed to get recommendations');
    } finally {
      setLoading(false);
    }
  };

  const currentOutfits = outfits[activeSeason] || [];

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold text-text">
          AI <span className="gradient-text">Fashion Stylist</span>
        </h1>
        <p className="text-text-secondary mt-1">
          Get personalized outfit recommendations for every season based on your body and personal color.
        </p>
      </div>

      {/* Season tabs */}
      <div className="flex gap-3">
        {seasons.map((s) => {
          const Icon = s.icon;
          return (
            <button
              key={s.id}
              onClick={() => setActiveSeason(s.id)}
              className={`flex-1 flex flex-col items-center gap-2 py-4 rounded-2xl transition-all ${
                activeSeason === s.id
                  ? `bg-gradient-to-br ${s.gradient} text-white shadow-lg`
                  : 'bg-surface border border-border text-text-secondary hover:border-primary/30'
              }`}
            >
              <Icon className="w-6 h-6" />
              <span className="text-sm font-semibold">{s.label}</span>
            </button>
          );
        })}
      </div>

      {/* Optional personal color input */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-text mb-1.5">Personal Color Season (optional)</label>
              <input
                type="text"
                value={personalColor}
                onChange={(e) => setPersonalColor(e.target.value)}
                placeholder="e.g. bright_spring"
                className="w-full rounded-xl border border-border bg-surface px-3 py-2 text-sm text-text placeholder:text-text-light focus:ring-2 focus:ring-primary/40"
              />
              <p className="text-xs text-text-light mt-1">Get this from the Beauty Scan page</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-text mb-1.5">Best Colors (optional)</label>
              <input
                type="text"
                value={bestColors}
                onChange={(e) => setBestColors(e.target.value)}
                placeholder="e.g. #06b6d4, #8b5cf6"
                className="w-full rounded-xl border border-border bg-surface px-3 py-2 text-sm text-text placeholder:text-text-light focus:ring-2 focus:ring-primary/40"
              />
            </div>
          </div>
          <Button variant="primary" size="lg" onClick={handleGenerate} isLoading={loading} className="w-full mt-4">
            <Sparkles className="h-5 w-5 mr-2" />
            Get {seasons.find((s) => s.id === activeSeason)?.label} Outfits (5 credits)
          </Button>
          {error && (
            <div className="mt-4 p-3 bg-error/10 border border-error/20 rounded-xl">
              <p className="text-sm text-error">{error}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Outfit recommendations */}
      <AnimatePresence mode="wait">
        {currentOutfits.length > 0 && (
          <motion.div
            key={activeSeason}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-6"
          >
            {currentOutfits.map((outfit, i) => (
              <Card key={i} hover>
                <CardContent className="p-0 overflow-hidden rounded-2xl">
                  {outfit.image_url ? (
                    <Image src={outfit.image_url} alt={outfit.style_name} width={512} height={512} className="w-full aspect-[4/5] object-cover" unoptimized />
                  ) : (
                    <div className="w-full aspect-[4/5] bg-gradient-to-br from-surfaceAlt to-surface flex items-center justify-center">
                      <Shirt className="w-16 h-16 text-text-light" />
                    </div>
                  )}
                  <div className="p-5 space-y-3">
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-bold text-text">{outfit.style_name}</h3>
                      <Badge variant="default">{outfit.occasion}</Badge>
                    </div>

                    <div className="space-y-2 text-sm">
                      <div className="flex gap-2">
                        <span className="text-text-light w-16 flex-shrink-0">Top:</span>
                        <span className="text-text-secondary">{outfit.top}</span>
                      </div>
                      <div className="flex gap-2">
                        <span className="text-text-light w-16 flex-shrink-0">Bottom:</span>
                        <span className="text-text-secondary">{outfit.bottom}</span>
                      </div>
                      {outfit.outerwear && (
                        <div className="flex gap-2">
                          <span className="text-text-light w-16 flex-shrink-0">Outer:</span>
                          <span className="text-text-secondary">{outfit.outerwear}</span>
                        </div>
                      )}
                      {outfit.accessories?.length > 0 && (
                        <div className="flex gap-2">
                          <span className="text-text-light w-16 flex-shrink-0">Acc:</span>
                          <span className="text-text-secondary">{outfit.accessories.join(', ')}</span>
                        </div>
                      )}
                    </div>

                    {/* Color palette */}
                    <div className="flex items-center gap-2 pt-2">
                      <Palette className="w-4 h-4 text-text-light" />
                      <div className="flex gap-1.5">
                        {outfit.color_palette?.map((c, j) => (
                          <div key={j} className="w-6 h-6 rounded-md border border-white/10" style={{ backgroundColor: c }} title={c} />
                        ))}
                      </div>
                    </div>
                    {outfit.color_reasoning && (
                      <p className="text-xs text-text-light">{outfit.color_reasoning}</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
