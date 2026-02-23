'use client';

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { Html5Qrcode, Html5QrcodeSupportedFormats } from 'html5-qrcode';
import { X, Camera, Loader2, Zap, ZapOff } from 'lucide-react';
import { foodDatabaseApi } from '@/lib/api/services';
import toast from 'react-hot-toast';

const BARCODE_FORMATS = [
  Html5QrcodeSupportedFormats.EAN_13,
  Html5QrcodeSupportedFormats.EAN_8,
  Html5QrcodeSupportedFormats.UPC_A,
  Html5QrcodeSupportedFormats.UPC_E,
  Html5QrcodeSupportedFormats.CODE_128,
  Html5QrcodeSupportedFormats.CODE_39,
  Html5QrcodeSupportedFormats.CODE_93,
  Html5QrcodeSupportedFormats.ITF,
  Html5QrcodeSupportedFormats.CODABAR,
];

interface BarcodeScannerProps {
  onFoodFound: (food: {
    food_name: string;
    brand: string;
    nutrition_per_100g: {
      calories: number;
      protein: number;
      carbs: number;
      fat: number;
    };
    serving_size: string;
    image_url?: string;
  }) => void;
  onClose: () => void;
}

export function BarcodeScanner({ onFoodFound, onClose }: BarcodeScannerProps) {
  const [status, setStatus] = useState<'scanning' | 'looking' | 'not_found'>('scanning');
  const [scannedCode, setScannedCode] = useState<string | null>(null);
  const [torchOn, setTorchOn] = useState(false);
  const [torchAvailable, setTorchAvailable] = useState(false);
  const scannerRef = useRef<Html5Qrcode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const containerId = useRef('bcr-' + Math.random().toString(36).slice(2, 8));
  const mountedRef = useRef(true);
  const processingRef = useRef(false);

  const killCamera = useCallback(() => {
    document.querySelectorAll('video').forEach(v => {
      if (v.srcObject && v.srcObject instanceof MediaStream) {
        v.srcObject.getTracks().forEach(t => t.stop());
        v.srcObject = null;
      }
    });
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop());
      streamRef.current = null;
    }
  }, []);

  const stopScanning = useCallback(async () => {
    try { if (scannerRef.current?.isScanning) await scannerRef.current.stop(); } catch {}
    try { scannerRef.current?.clear(); } catch {}
    scannerRef.current = null;
    killCamera();
  }, [killCamera]);

  const handleClose = useCallback(() => {
    stopScanning();
    onClose();
  }, [stopScanning, onClose]);

  const toggleTorch = useCallback(async () => {
    if (!streamRef.current) return;
    const track = streamRef.current.getVideoTracks()[0];
    if (!track) return;
    try {
      const newState = !torchOn;
      await track.applyConstraints({ advanced: [{ torch: newState } as MediaTrackConstraintSet] });
      setTorchOn(newState);
    } catch {}
  }, [torchOn]);

  const startCamera = useCallback(async () => {
    processingRef.current = false;
    setStatus('scanning');
    setScannedCode(null);
    setTorchOn(false);

    try {
      const scanner = new Html5Qrcode(containerId.current, {
        formatsToSupport: BARCODE_FORMATS,
        verbose: false,
      });
      scannerRef.current = scanner;

      await scanner.start(
        { facingMode: 'environment' },
        { fps: 30, disableFlip: false },
        async (decodedText) => {
          if (!mountedRef.current || processingRef.current) return;
          processingRef.current = true;
          setStatus('looking');
          setScannedCode(decodedText);

          if (navigator.vibrate) navigator.vibrate(100);

          await stopScanning();

          try {
            const response = await foodDatabaseApi.lookupBarcode(decodedText);
            const data = response.data;
            onFoodFound({
              food_name: data.brand ? `${data.food_name} (${data.brand})` : data.food_name,
              brand: data.brand,
              nutrition_per_100g: data.nutrition_per_100g,
              serving_size: data.serving_size,
              image_url: data.image_url,
            });
            toast.success(`Found: ${data.food_name}`);
            handleClose();
          } catch {
            if (mountedRef.current) setStatus('not_found');
          }
        },
        () => {}
      );

      const video = document.querySelector(`#${containerId.current} video`) as HTMLVideoElement;
      if (video?.srcObject instanceof MediaStream) {
        streamRef.current = video.srcObject;
        const track = video.srcObject.getVideoTracks()[0];
        if (track) {
          const caps = track.getCapabilities?.() as MediaTrackCapabilities & { torch?: boolean };
          if (caps?.torch) setTorchAvailable(true);
        }
      }
    } catch {
      if (mountedRef.current) {
        toast.error('Could not access camera. Check permissions.');
        onClose();
      }
    }
  }, [stopScanning, onFoodFound, handleClose, onClose]);

  useEffect(() => {
    mountedRef.current = true;
    startCamera();
    return () => { mountedRef.current = false; stopScanning(); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="fixed inset-0 z-50 flex flex-col bg-black">
      {/* Top buttons */}
      <div className="absolute top-4 right-4 z-[60] flex items-center gap-2">
        {torchAvailable && (
          <button
            onClick={toggleTorch}
            className="p-2 bg-black/60 hover:bg-black/80 rounded-full transition-colors"
            title={torchOn ? 'Turn off flashlight' : 'Turn on flashlight'}
          >
            {torchOn
              ? <Zap className="w-5 h-5 text-yellow-400" />
              : <ZapOff className="w-5 h-5 text-white" />}
          </button>
        )}
        <button
          onClick={handleClose}
          className="p-2 bg-black/60 hover:bg-black/80 rounded-full transition-colors"
        >
          <X className="w-6 h-6 text-white" />
        </button>
      </div>

      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3 bg-black/60 z-10">
        <Camera className="w-5 h-5 text-white" />
        <h3 className="font-semibold text-white">Scan Barcode</h3>
      </div>

      {/* Camera viewport */}
      <div className="flex-1 relative overflow-hidden">
        <div id={containerId.current} className="w-full h-full" />

        {/* Visual guide only — scanning happens on the entire frame */}
        {status === 'scanning' && (
          <div className="absolute inset-0 pointer-events-none" style={{ zIndex: 5 }}>
            {/* Center guide rectangle */}
            <div className="absolute left-1/2 top-1/2" style={{ width: '80%', maxWidth: 420, aspectRatio: '3/1', transform: 'translate(-50%, -50%)' }}>
              <div className="absolute top-0 left-0 w-10 h-10" style={{ borderTop: '3px solid rgba(255,255,255,0.85)', borderLeft: '3px solid rgba(255,255,255,0.85)', borderRadius: '8px 0 0 0' }} />
              <div className="absolute top-0 right-0 w-10 h-10" style={{ borderTop: '3px solid rgba(255,255,255,0.85)', borderRight: '3px solid rgba(255,255,255,0.85)', borderRadius: '0 8px 0 0' }} />
              <div className="absolute bottom-0 left-0 w-10 h-10" style={{ borderBottom: '3px solid rgba(255,255,255,0.85)', borderLeft: '3px solid rgba(255,255,255,0.85)', borderRadius: '0 0 0 8px' }} />
              <div className="absolute bottom-0 right-0 w-10 h-10" style={{ borderBottom: '3px solid rgba(255,255,255,0.85)', borderRight: '3px solid rgba(255,255,255,0.85)', borderRadius: '0 0 8px 0' }} />
              <div
                className="absolute left-4 right-4 h-0.5 bg-red-500"
                style={{ boxShadow: '0 0 12px 2px rgba(239, 68, 68, 0.5)', animation: 'scanline 2s ease-in-out infinite' }}
              />
            </div>
            {/* Text below guide */}
            <div className="absolute left-0 right-0 text-center" style={{ top: 'calc(50% + 12%)' }}>
              <p className="text-white text-sm font-medium drop-shadow-lg">Point camera at any barcode</p>
              <p className="text-gray-300 text-xs mt-1 drop-shadow">No need to align perfectly</p>
            </div>
          </div>
        )}

        {/* Looking up product */}
        {status === 'looking' && (
          <div className="absolute inset-0 bg-black/70 flex items-center justify-center z-20">
            <div className="text-center text-white">
              <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" />
              <p className="text-sm">Looking up product...</p>
              {scannedCode && <p className="text-xs text-gray-400 mt-1">Barcode: {scannedCode}</p>}
            </div>
          </div>
        )}

        {/* Product not found */}
        {status === 'not_found' && (
          <div className="absolute inset-0 bg-black/80 flex items-center justify-center z-20">
            <div className="text-center text-white max-w-xs mx-auto px-4">
              <div className="w-14 h-14 mx-auto mb-3 rounded-full bg-red-500/20 flex items-center justify-center">
                <X className="w-7 h-7 text-red-400" />
              </div>
              <p className="text-lg font-semibold mb-1">Product Not Found</p>
              {scannedCode && <p className="text-xs text-gray-400 mb-4">Barcode: {scannedCode}</p>}
              <p className="text-sm text-gray-300 mb-6">
                This product isn&apos;t in the database yet. You can scan another barcode or enter the food manually.
              </p>
              <div className="flex gap-3">
                <button
                  onClick={() => startCamera()}
                  className="flex-1 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl transition-colors"
                >
                  Scan Again
                </button>
                <button
                  onClick={handleClose}
                  className="flex-1 py-2.5 bg-white/15 hover:bg-white/25 text-white font-medium rounded-xl transition-colors"
                >
                  Enter Manually
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-4 bg-black/60 text-center space-y-3 z-10">
        <button
          onClick={handleClose}
          className="w-full py-2.5 bg-white/15 hover:bg-white/25 text-white font-medium rounded-xl transition-colors"
        >
          Cancel
        </button>
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        #${containerId.current} {
          width: 100% !important;
          height: 100% !important;
        }
        #${containerId.current}__dashboard_section {
          display: none !important;
        }
        @keyframes scanline {
          0%, 100% { top: 10%; }
          50% { top: 85%; }
        }
      `}} />
    </div>
  );
}
