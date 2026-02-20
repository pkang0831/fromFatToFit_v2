'use client';

import { useState, useRef, ChangeEvent } from 'react';
import { useRouter } from 'next/navigation';
import { Camera, Upload, X, Crown } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, Button, Badge } from '@/components/ui';
import { useSubscription } from '@/lib/hooks/useSubscription';
import { foodApi, foodDecisionApi } from '@/lib/api/services';
import { compressAndConvertToBase64 } from '@/lib/utils/image';
import { FoodDecisionResult } from '@/components/features/FoodDecisionResult';
import { FoodRecommendations } from '@/components/features/FoodRecommendations';
import type { FoodAnalysisResponse, FoodItem } from '@/types/api';

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

  const featureAccess = checkFeatureAccess('food_scan');

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

    // Check usage limits
    if (!featureAccess.hasAccess && !isPremium) {
      setError('You have reached your free scan limit. Upgrade to Premium for unlimited scans.');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      console.log('🔍 Starting food decision analysis...');

      // Extract base64 from data URL
      const base64 = selectedImage.split(',')[1];

      // Call the new "Should I Eat?" API
      const response = await foodDecisionApi.shouldIEat(base64);
      console.log('✅ Decision analysis received:', response.data);

      setDecisionResult(response.data);
      setFlow('decision');
      await refreshLimits();
    } catch (err: any) {
      console.error('❌ Food decision error:', err);

      if (err.response?.status === 402) {
        setError('You have reached your scan limit. Upgrade to Premium for unlimited scans.');
      } else {
        setError(err.response?.data?.detail || 'Failed to analyze image');
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
        <h1 className="text-3xl font-bold text-text">AI Food Camera</h1>
        <p className="text-text-secondary mt-1">
          Scan food photos for instant nutritional information
        </p>
        
        {/* Usage Limits Display */}
        <div className="mt-4 flex items-center gap-4">
          {isPremium ? (
            <Badge variant="premium" className="text-base px-4 py-2">
              <Crown className="h-4 w-4 mr-2" />
              Unlimited Scans
            </Badge>
          ) : (
            <Badge variant={featureAccess.remaining > 0 ? 'info' : 'error'} className="text-base px-4 py-2">
              {featureAccess.remaining} / {featureAccess.limit} Scans Remaining
            </Badge>
          )}
        </div>
      </div>

      {/* Image Upload Area */}
      <Card variant="elevated">
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
                className="border-2 border-dashed border-border rounded-lg p-12 cursor-pointer hover:border-primary transition-colors"
              >
                <Camera className="h-16 w-16 text-text-light mx-auto mb-4" />
                <p className="text-lg font-medium text-text mb-2">Take or Upload a Photo</p>
                <p className="text-sm text-text-secondary">
                  Click to select an image of your food
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="relative">
                <img
                  src={selectedImage}
                  alt="Selected food"
                  className="w-full rounded-lg object-cover max-h-96"
                />
                <button
                  onClick={handleClearImage}
                  className="absolute top-2 right-2 p-2 bg-surface rounded-full shadow-lg hover:bg-surfaceAlt transition-colors"
                >
                  <X className="h-5 w-5 text-text" />
                </button>
              </div>

              {!analysisResult && (
                <Button
                  variant="primary"
                  size="lg"
                  onClick={handleAnalyze}
                  isLoading={isAnalyzing}
                  disabled={!featureAccess.hasAccess && !isPremium}
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
              {!isPremium && (
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => router.push('/upgrade')}
                  className="mt-3 bg-premium text-primary hover:bg-premium-dark"
                >
                  <Crown className="h-4 w-4 mr-2" />
                  Upgrade to Premium
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
            분석 다시 하기
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
            새로운 사진 분석
          </Button>
        </div>
      )}

      {/* Loading Recommendations */}
      {isLoadingRecommendations && (
        <Card>
          <CardContent className="p-12 text-center">
            <div className="animate-spin h-12 w-12 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-gray-600">추천 음식을 준비하고 있어요...</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
