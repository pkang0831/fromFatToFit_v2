'use client';

/**
 * Mask Editor Page
 *
 * Flow: upload image → call POST /body/auto-segment → receive label map
 *       → init BodyMaskEditor with SAM2-generated initial segmentation
 *       → user corrects → export corrected masks at original resolution.
 */

import React, { useState, useCallback, useRef } from 'react';
import { Upload, Loader2 } from 'lucide-react';
import dynamic from 'next/dynamic';
import { importLabelMapPng, type SegmentationExport, type LabelMap } from '@/lib/segmentation';

const BodyMaskEditor = dynamic(
  () => import('@/components/features/BodyMaskEditor'),
  { ssr: false },
);

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

type Phase = 'upload' | 'segmenting' | 'editing';

export default function MaskEditorPage() {
  const [phase, setPhase] = useState<Phase>('upload');
  const [imageBase64, setImageBase64] = useState<string | null>(null);
  const [initialLabelMap, setInitialLabelMap] = useState<LabelMap | null>(null);
  const [segError, setSegError] = useState<string | null>(null);
  const [exportResult, setExportResult] = useState<SegmentationExport | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async () => {
      const dataUrl = reader.result as string;
      setImageBase64(dataUrl);
      setExportResult(null);
      setSegError(null);
      setPhase('segmenting');

      // Strip the data:image/...;base64, prefix for the API
      const raw = dataUrl.split(',')[1];

      try {
        const resp = await fetch(`${API_URL}/body/auto-segment`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image_base64: raw }),
        });

        if (!resp.ok) {
          const detail = await resp.text();
          throw new Error(`Segmentation failed (${resp.status}): ${detail}`);
        }

        const data = await resp.json();
        const lm = await importLabelMapPng(data.label_map_base64, data.width, data.height);
        setInitialLabelMap(lm);
        setPhase('editing');
      } catch (err: unknown) {
        console.error('Auto-segment error:', err);
        setSegError(err instanceof Error ? err.message : 'Segmentation failed');
        // Fall through to blank editor so user can still paint manually
        setInitialLabelMap(null);
        setPhase('editing');
      }
    };
    reader.readAsDataURL(file);
  }, []);

  const handleExport = useCallback((result: SegmentationExport) => {
    setExportResult(result);
    console.log('Export metadata:', result.metadata);
    console.log('Per-class masks:', Object.keys(result.perClassMasks));
  }, []);

  const handleReset = useCallback(() => {
    setPhase('upload');
    setImageBase64(null);
    setInitialLabelMap(null);
    setExportResult(null);
    setSegError(null);
  }, []);

  return (
    <div className="min-h-screen bg-gray-950 text-white p-4 md:p-8">
      <div className="max-w-2xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Segmentation Mask Editor</h1>
          <p className="text-gray-400 text-sm mt-1">
            Upload a photo. SAM2 segments it automatically, then you correct the mask.
          </p>
        </div>

        {/* Upload */}
        {phase === 'upload' && (
          <button
            onClick={() => fileInputRef.current?.click()}
            className="w-full border-2 border-dashed border-gray-700 rounded-xl p-12 flex flex-col items-center gap-3 hover:border-cyan-600 hover:bg-gray-900/50 transition-colors"
          >
            <Upload size={32} className="text-gray-500" />
            <span className="text-gray-400 text-sm">Click to upload a body photo</span>
          </button>
        )}
        <input ref={fileInputRef} type="file" accept="image/*"
          onChange={handleFileSelect} className="hidden" />

        {/* Segmenting */}
        {phase === 'segmenting' && (
          <div className="flex flex-col items-center gap-4 py-16">
            <Loader2 size={40} className="animate-spin text-cyan-400" />
            <span className="text-gray-300">Running SAM2 segmentation...</span>
            <span className="text-xs text-gray-500">This may take 15-30 seconds</span>
          </div>
        )}

        {/* Seg error banner */}
        {segError && phase === 'editing' && (
          <div className="p-3 bg-yellow-900/30 border border-yellow-700 rounded-lg text-sm text-yellow-300">
            SAM2 segmentation unavailable: {segError}.
            You can still paint masks manually.
          </div>
        )}

        {/* Editor */}
        {phase === 'editing' && imageBase64 && (
          <>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">
                {initialLabelMap ? 'Correct the auto-generated segmentation' : 'Paint body-part labels manually'}
              </span>
              <button onClick={handleReset}
                className="text-xs text-gray-500 hover:text-gray-300 transition-colors">
                Change photo
              </button>
            </div>

            <BodyMaskEditor
              imageBase64={imageBase64}
              initialLabelMap={initialLabelMap ?? undefined}
              onExport={handleExport}
            />
          </>
        )}

        {/* Export results */}
        {exportResult && (
          <div className="space-y-4 p-4 bg-gray-900 rounded-lg border border-gray-700">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-gray-200">Exported Masks</h3>
              <span className="text-xs text-gray-500">
                {exportResult.metadata.width} x {exportResult.metadata.height} px
              </span>
            </div>
            <div className="space-y-1">
              <span className="text-xs text-gray-400">Label map (class IDs as grayscale)</span>
              <img src={`data:image/png;base64,${exportResult.labelMapPng}`}
                alt="label map"
                className="w-full max-w-xs rounded border border-gray-700 bg-gray-800"
                style={{ imageRendering: 'pixelated' }} />
            </div>
            <div className="space-y-1">
              <span className="text-xs text-gray-400">Per-class binary masks</span>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {Object.entries(exportResult.perClassMasks).map(([key, b64]) => (
                  <div key={key} className="space-y-1">
                    <span className="text-xs text-gray-500">{key}</span>
                    <img src={`data:image/png;base64,${b64}`} alt={key}
                      className="w-full rounded border border-gray-700 bg-gray-800" />
                  </div>
                ))}
              </div>
            </div>
            <details className="text-xs text-gray-500">
              <summary className="cursor-pointer hover:text-gray-300">Metadata JSON</summary>
              <pre className="mt-2 p-2 bg-gray-800 rounded overflow-auto text-[10px]">
                {JSON.stringify(exportResult.metadata, null, 2)}
              </pre>
            </details>
          </div>
        )}
      </div>
    </div>
  );
}
