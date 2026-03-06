'use client';

import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Camera, Coins, Palette, Scissors, Droplets, Wand2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, Button, Badge } from '@/components/ui';
import { beautyApi, paymentApi } from '@/lib/api/services';
import { compressAndConvertToBase64 } from '@/lib/utils/image';
import type { BeautyAnalysis, StyledImage } from '@/types/api';

type Step = 'upload' | 'analyzing' | 'results';

export default function BeautyScanPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [step, setStep] = useState<Step>('upload');
  const [preview, setPreview] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [gender, setGender] = useState<string>('female');
  const [generateImages, setGenerateImages] = useState(false);
  const [analysis, setAnalysis] = useState<BeautyAnalysis | null>(null);
  const [styledImages, setStyledImages] = useState<StyledImage[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'hair' | 'color' | 'makeup' | 'styles'>('overview');

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f || !f.type.startsWith('image/')) return;
    setFile(f);
    const reader = new FileReader();
    reader.onloadend = () => setPreview(reader.result as string);
    reader.readAsDataURL(f);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setStep('analyzing');
    setError(null);

    try {
      const base64 = await compressAndConvertToBase64(file);
      const res = await beautyApi.analyze({
        image_base64: base64,
        gender,
        generate_images: generateImages,
      });
      setAnalysis(res.data.analysis);
      setStyledImages(res.data.styled_images || []);
      setStep('results');
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err.message || 'Analysis failed';
      setError(msg);
      setStep('upload');
    }
  };

  const tabs = [
    { id: 'overview' as const, label: 'Overview', icon: Sparkles },
    { id: 'color' as const, label: 'Personal Color', icon: Palette },
    { id: 'hair' as const, label: 'Hair', icon: Scissors },
    { id: 'makeup' as const, label: 'Makeup & Skin', icon: Droplets },
    ...(styledImages.length > 0 ? [{ id: 'styles' as const, label: 'AI Styles', icon: Wand2 }] : []),
  ];

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold text-text">
          AI <span className="gradient-text">Beauty Scan</span>
        </h1>
        <p className="text-text-secondary mt-1">
          Upload a selfie for AI-powered face shape, personal color, and styling analysis.
        </p>
      </div>

      {/* Upload / Analyzing */}
      {step !== 'results' && (
        <Card variant="elevated">
          <CardContent className="p-8">
            {step === 'upload' && (
              <div className="space-y-6">
                <input ref={fileInputRef} type="file" accept="image/*" onChange={handleFileSelect} className="hidden" />

                {!preview ? (
                  <div
                    onClick={() => fileInputRef.current?.click()}
                    className="border-2 border-dashed border-border rounded-2xl p-16 text-center cursor-pointer hover:border-primary/40 transition-colors"
                  >
                    <Camera className="h-16 w-16 text-text-light mx-auto mb-4" />
                    <p className="text-lg font-medium text-text mb-2">Upload a Selfie</p>
                    <p className="text-sm text-text-secondary">Front-facing photo with good lighting works best</p>
                  </div>
                ) : (
                  <div className="space-y-6">
                    <div className="flex justify-center">
                      <Image src={preview} alt="Preview" width={300} height={300} className="rounded-2xl object-cover max-h-80" unoptimized />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-text mb-1.5">Gender</label>
                        <select value={gender} onChange={(e) => setGender(e.target.value)} className="w-full rounded-xl border border-border bg-surface px-3 py-2 text-sm text-text">
                          <option value="female">Female</option>
                          <option value="male">Male</option>
                        </select>
                      </div>
                      <div className="flex items-end">
                        <label className="flex items-center gap-3 cursor-pointer">
                          <input type="checkbox" checked={generateImages} onChange={(e) => setGenerateImages(e.target.checked)} className="w-4 h-4 rounded border-border text-primary" />
                          <div>
                            <span className="text-sm font-medium text-text">Generate AI styled photos</span>
                            <span className="text-xs text-text-secondary block">+30 credits for 4 styled images</span>
                          </div>
                        </label>
                      </div>
                    </div>

                    <div className="flex gap-3">
                      <Button variant="outline" onClick={() => { setPreview(null); setFile(null); }}>Change Photo</Button>
                      <Button variant="primary" size="lg" onClick={handleAnalyze} className="flex-1">
                        <Sparkles className="h-5 w-5 mr-2" />
                        Analyze ({generateImages ? '40' : '10'} credits)
                      </Button>
                    </div>
                  </div>
                )}

                {error && (
                  <div className="p-4 bg-error/10 border border-error/20 rounded-xl">
                    <p className="text-sm text-error">{error}</p>
                  </div>
                )}
              </div>
            )}

            {step === 'analyzing' && (
              <div className="flex flex-col items-center justify-center py-20 gap-6">
                <div className="relative">
                  <div className="w-20 h-20 rounded-full border-4 border-white/10" />
                  <div className="absolute inset-0 w-20 h-20 rounded-full border-4 border-transparent border-t-primary animate-spin" />
                </div>
                <div className="text-center">
                  <p className="text-lg font-semibold text-text">Analyzing your features...</p>
                  <p className="text-sm text-text-secondary mt-1">This may take 15-30 seconds</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Results */}
      {step === 'results' && analysis && (
        <>
          {/* Tab navigation */}
          <div className="flex flex-wrap gap-2">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
                    activeTab === tab.id
                      ? 'bg-gradient-primary text-white shadow-glow-cyan'
                      : 'text-text-secondary hover:text-text hover:bg-surfaceAlt'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>

          <AnimatePresence mode="wait">
            <motion.div key={activeTab} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }}>

              {activeTab === 'overview' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <Card hover>
                    <CardContent className="p-6">
                      <h3 className="text-lg font-semibold text-text mb-2">Face Shape</h3>
                      <p className="text-3xl font-bold gradient-text capitalize mb-2">{analysis.face_shape}</p>
                      <p className="text-sm text-text-secondary">{analysis.face_shape_description}</p>
                    </CardContent>
                  </Card>
                  <Card hover>
                    <CardContent className="p-6">
                      <h3 className="text-lg font-semibold text-text mb-2">Skin Tone</h3>
                      <p className="text-3xl font-bold text-text capitalize mb-1">{analysis.skin_tone}</p>
                      <Badge variant={analysis.skin_undertone === 'warm' ? 'warning' : analysis.skin_undertone === 'cool' ? 'info' : 'default'}>
                        {analysis.skin_undertone} undertone
                      </Badge>
                    </CardContent>
                  </Card>
                  <Card hover className="md:col-span-2">
                    <CardContent className="p-6">
                      <h3 className="text-lg font-semibold text-text mb-2">Personal Color</h3>
                      <p className="text-2xl font-bold gradient-text capitalize mb-2">
                        {analysis.personal_color_sub?.replace(/_/g, ' ')}
                      </p>
                      <p className="text-sm text-text-secondary mb-4">{analysis.personal_color_description}</p>
                      <div className="flex gap-2 flex-wrap">
                        <span className="text-xs text-text-secondary mr-2">Best colors:</span>
                        {analysis.best_colors?.map((c, i) => (
                          <div key={i} className="w-8 h-8 rounded-lg border border-white/10 shadow-sm" style={{ backgroundColor: c }} title={c} />
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}

              {activeTab === 'color' && (
                <div className="space-y-6">
                  <Card>
                    <CardHeader><CardTitle>Your Best Colors</CardTitle></CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-6 md:grid-cols-12 gap-3">
                        {analysis.best_colors?.map((c, i) => (
                          <div key={i} className="flex flex-col items-center gap-1">
                            <div className="w-12 h-12 rounded-xl border border-white/10" style={{ backgroundColor: c }} />
                            <span className="text-[10px] text-text-light font-mono">{c}</span>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader><CardTitle>Colors to Avoid</CardTitle></CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-6 md:grid-cols-12 gap-3">
                        {analysis.avoid_colors?.map((c, i) => (
                          <div key={i} className="flex flex-col items-center gap-1 opacity-60">
                            <div className="w-12 h-12 rounded-xl border border-white/10 relative" style={{ backgroundColor: c }}>
                              <div className="absolute inset-0 flex items-center justify-center text-white text-lg font-bold">✕</div>
                            </div>
                            <span className="text-[10px] text-text-light font-mono">{c}</span>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}

              {activeTab === 'hair' && (
                <div className="space-y-6">
                  <Card>
                    <CardHeader><CardTitle>Hairstyle Recommendations</CardTitle></CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {analysis.hairstyle_recommendations?.map((h, i) => (
                          <div key={i} className="p-4 rounded-xl border border-border hover:border-primary/30 transition-colors">
                            <h4 className="font-semibold text-text mb-1">{h.style}</h4>
                            <p className="text-sm text-text-secondary">{h.reason}</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader><CardTitle>Hair Color Recommendations</CardTitle></CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {analysis.hair_color_recommendations?.map((h, i) => (
                          <div key={i} className="flex items-center gap-4 p-4 rounded-xl border border-border">
                            <div className="w-12 h-12 rounded-full border border-white/10 flex-shrink-0" style={{ backgroundColor: h.hex }} />
                            <div>
                              <h4 className="font-semibold text-text">{h.color}</h4>
                              <p className="text-sm text-text-secondary">{h.reason}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}

              {activeTab === 'makeup' && (
                <div className="space-y-6">
                  {analysis.makeup_recommendations && (
                    <Card>
                      <CardHeader><CardTitle>Makeup Recommendations</CardTitle></CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="p-4 rounded-xl border border-border">
                            <h4 className="font-semibold text-text mb-2">Foundation</h4>
                            <p className="text-sm text-text-secondary">{analysis.makeup_recommendations.foundation_tone}</p>
                          </div>
                          <div className="p-4 rounded-xl border border-border">
                            <h4 className="font-semibold text-text mb-2">Blush</h4>
                            <p className="text-sm text-text-secondary">{analysis.makeup_recommendations.blush}</p>
                          </div>
                          <div className="p-4 rounded-xl border border-border">
                            <h4 className="font-semibold text-text mb-2">Lip Colors</h4>
                            <div className="flex gap-2 flex-wrap">
                              {analysis.makeup_recommendations.lip_colors?.map((c, i) => (
                                <Badge key={i} variant="default">{c}</Badge>
                              ))}
                            </div>
                          </div>
                          <div className="p-4 rounded-xl border border-border">
                            <h4 className="font-semibold text-text mb-2">Eye Shadow</h4>
                            <div className="flex gap-2 flex-wrap">
                              {analysis.makeup_recommendations.eye_shadow?.map((c, i) => (
                                <Badge key={i} variant="default">{c}</Badge>
                              ))}
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  )}
                  <Card>
                    <CardHeader><CardTitle>Skincare Tips</CardTitle></CardHeader>
                    <CardContent>
                      <ul className="space-y-3">
                        {analysis.skincare_recommendations?.map((r, i) => (
                          <li key={i} className="flex items-start gap-3">
                            <div className="w-6 h-6 rounded-full bg-primary/10 text-primary flex items-center justify-center flex-shrink-0 mt-0.5 text-xs font-bold">{i + 1}</div>
                            <p className="text-text-secondary">{r}</p>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                </div>
              )}

              {activeTab === 'styles' && styledImages.length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {styledImages.map((img, i) => (
                    <Card key={i} hover>
                      <CardContent className="p-0 overflow-hidden rounded-2xl">
                        {img.image_url ? (
                          <Image src={img.image_url} alt={img.title} width={512} height={512} className="w-full aspect-square object-cover" unoptimized />
                        ) : (
                          <div className="w-full aspect-square bg-surfaceAlt flex items-center justify-center text-text-light">
                            Failed to generate
                          </div>
                        )}
                        <div className="p-4">
                          <h4 className="font-semibold text-text mb-1">{img.title}</h4>
                          <p className="text-sm text-text-secondary line-clamp-2">{img.description}</p>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </motion.div>
          </AnimatePresence>

          <Button variant="outline" onClick={() => { setStep('upload'); setPreview(null); setFile(null); setAnalysis(null); setStyledImages([]); }}>
            Scan Another Photo
          </Button>
        </>
      )}
    </div>
  );
}
