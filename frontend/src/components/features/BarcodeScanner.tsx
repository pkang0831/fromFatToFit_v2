'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Html5Qrcode } from 'html5-qrcode';
import { X, Camera, Loader2 } from 'lucide-react';
import { foodDatabaseApi } from '@/lib/api/services';
import toast from 'react-hot-toast';

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
  const [isScanning, setIsScanning] = useState(false);
  const [isLooking, setIsLooking] = useState(false);
  const scannerRef = useRef<Html5Qrcode | null>(null);
  const containerRef = useRef<string>('barcode-reader-' + Date.now());

  useEffect(() => {
    startScanning();
    return () => {
      stopScanning();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const startScanning = async () => {
    try {
      const scanner = new Html5Qrcode(containerRef.current);
      scannerRef.current = scanner;

      await scanner.start(
        { facingMode: 'environment' },
        {
          fps: 10,
          qrbox: { width: 250, height: 150 },
          aspectRatio: 1.0,
        },
        async (decodedText) => {
          await stopScanning();
          await lookupBarcode(decodedText);
        },
        () => {}
      );
      setIsScanning(true);
    } catch {
      toast.error('Could not access camera. Please check permissions.');
      onClose();
    }
  };

  const stopScanning = async () => {
    if (scannerRef.current && scannerRef.current.isScanning) {
      try {
        await scannerRef.current.stop();
      } catch {
        // Scanner already stopped
      }
    }
    setIsScanning(false);
  };

  const lookupBarcode = async (barcode: string) => {
    setIsLooking(true);
    try {
      const response = await foodDatabaseApi.lookupBarcode(barcode);
      const data = response.data;
      onFoodFound({
        food_name: data.brand ? `${data.food_name} (${data.brand})` : data.food_name,
        brand: data.brand,
        nutrition_per_100g: data.nutrition_per_100g,
        serving_size: data.serving_size,
        image_url: data.image_url,
      });
      toast.success(`Found: ${data.food_name}`);
      onClose();
    } catch {
      toast.error('Product not found. Try manual entry.');
      startScanning();
    } finally {
      setIsLooking(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-md w-full overflow-hidden">
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2">
            <Camera className="w-5 h-5 text-primary" />
            <h3 className="font-semibold text-gray-900 dark:text-white">Scan Barcode</h3>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        <div className="relative">
          <div id={containerRef.current} className="w-full" style={{ minHeight: 300 }} />

          {isLooking && (
            <div className="absolute inset-0 bg-black/60 flex items-center justify-center">
              <div className="text-center text-white">
                <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" />
                <p className="text-sm">Looking up product...</p>
              </div>
            </div>
          )}
        </div>

        <div className="p-4 text-center">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Point your camera at a barcode on any food package
          </p>
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
            Powered by Open Food Facts (3M+ products)
          </p>
        </div>
      </div>
    </div>
  );
}
