'use client';

import { useState, useRef, useEffect, ChangeEvent } from 'react';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import { Camera, Upload, X, Coins } from 'lucide-react';
import Image from 'next/image';
import { Card, CardHeader, CardTitle, CardContent, Button, Badge } from '@/components/ui';
import { useSubscription } from '@/lib/hooks/useSubscription';
import { foodApi, foodDecisionApi, paymentApi } from '@/lib/api/services';
import { compressAndConvertToBase64 } from '@/lib/utils/image';
import { FoodDecisionResult } from '@/components/features/FoodDecisionResult';
import { FoodRecommendations } from '@/components/features/FoodRecommendations';
import type { FoodAnalysisResponse, FoodItem } from '@/types/api';

const FOOD_SCAN_COST = 1;

export default function FoodCameraPage() {
  const router = useRouter();
  const { isPremium, checkFeatureAccess, refreshLimits } = useSubscription();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<FoodAnalysisResponse | null>(null);
  const [decisionResult, setDecisionResult] = useState<any | null>(null);
  const [showRecommendations, setShowRecommendations] = useState(false);
  const [recommendations, setRecommendations] = useState<any | null>(null);
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [flow, setFlow] = useState<'upload' | 'decision' | 'recommendations'>('upload');
  const [creditBalance, setCreditBalance] = useState<number | null>(null);

  const featureAccess = checkFeatureAccess('food_scan');

  const fetchCredits = async () => {
    try {
      const res = await paymentApi.getCreditBalance();
      setCreditBalance(res.data.total_credits);
    } catch {
      setCreditBalance(null);
    }
  };

  useEffect(() => { fetchCredits(); }, []);

  const canScan = creditBalance !== null && creditBalance >= FOOD_SCAN_COST;

  const handleFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('Please select an image file');
      return;
    }

    // Create preview URL
    const reader = new FileReader();
    reader.onloadend = () => {
      setSelectedImage(reader.result as string);
      setAnalysisResult(null);
      setError(null);
    };
    reader.readAsDataURL(file);
  };

  const handleAnalyze = async () => {
    if (!selectedImage) return;

    if (creditBalance !== null && creditBalance < FOOD_SCAN_COST) {
      setError(`Not enough credits. Food scan costs ${FOOD_SCAN_COST} credit but you have ${creditBalance}.`);
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      // Extract base64 from data URL
      const base64 = selectedImage.split(',')[1];

      // Call the new "Should I Eat?" API
      const response = await foodDecisionApi.shouldIEat(base64);
      setDecisionResult(response.data);
      setFlow('decision');
      await refreshLimits();
      await fetchCredits();
    } catch (err: any) {
      console.error('❌ Food decision error:', err);

      if (err.response?.status === 402) {
        setError('Not enough credits. Buy more credits to continue scanning.');
        toast.error('Not enough credits');
      } else {
        setError(err.response?.data?.detail || 'Failed to analyze image');
        toast.error('Failed to analyze image');
      }
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleClearImage = () => {
    setSelectedImage(null);
    setAnalysisResult(null);
    setDecisionResult(null);
    setRecommendations(null);
    setShowRecommendations(false);
    setFlow('upload');
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleEatAnyway = async () => {
    // User decided to eat the food
    setIsLoadingRecommendations(true);
    try {
      // Get recommendations for next meal
      const response = await foodDecisionApi.recommendFoods('dinner'); // Default to dinner
      setRecommendations(response.data);
      setFlow('recommendations');
    } catch (err: any) {
      console.error('❌ Error fetching recommendations:', err);
      setError('Failed to load recommendations');
      toast.error('Failed to load recommendations');
    } finally {
      setIsLoadingRecommendations(false);
    }
  };

  const handleFindAlternative = () => {
    // Navigate to food database or show alternatives
    router.push('/calories');
  };

  const handleSelectFood = (foodId: string) => {
    // Navigate to calorie tracker with pre-selected food
    router.push(`/calories?food=${foodId}`);
  };

  const getConfidenceBadge = (confidence: string) => {
    switch (confidence) {
      case 'high':
        return <Badge variant="success">High Confidence</Badge>;
      case 'medium':
        return <Badge variant="warning">Medium Confidence</Badge>;
      case 'low':
        return <Badge variant="error">Low Confidence</Badge>;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">AI Food Camera</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Scan food photos for instant nutritional information
        </p>
        
        {/* Credit Display */}
        <div data-tour="camera-credits" className="mt-4 flex items-center gap-3 p-3 bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-950/30 dark:to-orange-950/30 border border-amber-200 dark:border-amber-800 rounded-xl max-w-md">
          <div className="w-9 h-9 rounded-full bg-amber-100 flex items-center justify-center">
            <Coins className="h-4 w-4 text-amber-600" />
          </div>
          <div className="flex-1">
            <p className="text-xs text-amber-800 dark:text-amber-300 font-medium">Your Credits</p>
            <p className="text-lg font-bold text-amber-700 dark:text-amber-400">
              {creditBalance !== null ? creditBalance : '—'}
            </p>
          </div>
          <Badge variant="info" className="text-xs">
            <Coins className="h-3 w-3 mr-1" />
            {FOOD_SCAN_COST} per scan
          </Badge>
        </div>
      </div>

      {/* Image Upload Area */}
      <Card data-tour="camera-upload" variant="elevated">
        <CardContent className="p-8">
          {!selectedImage ? (
            <div className="text-center">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="hidden"
                capture="environment"
              />
              <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-gray-200 dark:border-gray-700 rounded-lg p-12 cursor-pointer hover:border-primary transition-colors"
              >
                <Camera className="h-16 w-16 text-gray-500 dark:text-gray-500 mx-auto mb-4" />
                <p className="text-lg font-medium text-gray-900 dark:text-white mb-2">Take or Upload a Photo</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Click to select an image of your food
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="relative">
                <Image
                  src={selectedImage}
                  alt="Selected food"
                  width={800}
                  height={600}
                  className="w-full rounded-lg object-cover max-h-96"
                  unoptimized
                />
                <button
                  onClick={handleClearImage}
                  className="absolute top-2 right-2 p-2 bg-white dark:bg-gray-800 rounded-full shadow-lg hover:bg-gray-100 dark:bg-gray-700 transition-colors"
                >
                  <X className="h-5 w-5 text-gray-900 dark:text-white" />
                </button>
              </div>

              {!analysisResult && (
                <Button
                  variant="primary"
                  size="lg"
                  onClick={handleAnalyze}
                  isLoading={isAnalyzing}
                  disabled={!canScan}
                  className="w-full"
                >
                  <Camera className="h-5 w-5 mr-2" />
                  Analyze Food
                </Button>
              )}
            </div>
          )}

          {error && (
            <div className="mt-4 p-4 bg-error/10 border border-error rounded-lg">
              <p className="text-sm text-error">{error}</p>
              {!canScan && (
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => router.push('/upgrade')}
                  className="mt-3"
                >
                  <Coins className="h-4 w-4 mr-2" />
                  Buy Credits
                </Button>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Decision Result */}
      {flow === 'decision' && decisionResult && (
        <div className="space-y-6">
          <FoodDecisionResult
            result={decisionResult}
            onEatAnyway={handleEatAnyway}
            onFindAlternative={handleFindAlternative}
          />
          
          <Button
            variant="outline"
            onClick={handleClearImage}
            className="w-full"
          >
            Analyze Again
          </Button>
        </div>
      )}

      {/* Recommendations */}
      {flow === 'recommendations' && recommendations && (
        <div className="space-y-6">
          <FoodRecommendations
            recommendations={recommendations}
            onSelectFood={handleSelectFood}
          />
          
          <Button
            variant="outline"
            onClick={handleClearImage}
            className="w-full"
          >
            Analyze New Photo
          </Button>
        </div>
      )}

      {/* Loading Recommendations */}
      {isLoadingRecommendations && (
        <Card>
          <CardContent className="p-12 text-center">
            <div className="animate-spin h-12 w-12 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">Preparing food recommendations...</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
