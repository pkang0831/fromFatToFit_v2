'use client';

import { useState, useRef, ChangeEvent, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Scan, Crown, TrendingUp, Award, Sparkles, Wand2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, Button, Badge, Input, Select } from '@/components/ui';
import { useSubscription } from '@/lib/hooks/useSubscription';
import { useAuth } from '@/contexts/AuthContext';
import { bodyApi } from '@/lib/api/services';
import { compressAndConvertToBase64 } from '@/lib/utils/image';
import { BellCurveChart } from '@/components/charts/BellCurveChart';
import type { BodyScanRequest, BodyFatEstimateResponse, PercentileResponse, TransformationResponse, EnhancementResponse } from '@/types/api';

type ScanType = 'bodyfat' | 'percentile' | 'transformation' | 'enhancement';

export default function BodyScanPage() {
  const router = useRouter();
  const { user } = useAuth();
  const { isPremium, checkFeatureAccess, refreshLimits } = useSubscription();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [selectedType, setSelectedType] = useState<ScanType>('bodyfat');
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [results, setResults] = useState<{
    bodyfat?: BodyFatEstimateResponse;
    percentile?: PercentileResponse;
    transformation?: TransformationResponse;
    enhancement?: EnhancementResponse;
  }>({});
  const [error, setError] = useState<string | null>(null);
  
  // 🚀 프로필에서 자동으로 가져오기
  const [formDefaults, setFormDefaults] = useState({
    gender: '',
    age: '',
    height_cm: '',
    ethnicity: ''
  });

  // 🔧 Cleanup: Aggressive style reset on mount/unmount
  useEffect(() => {
    const cleanupStyles = () => {
      const html = document.documentElement;
      const body = document.body;
      
      html.style.cssText = 'opacity: 1 !important; filter: none !important; backdrop-filter: none !important;';
      body.style.cssText += ' opacity: 1 !important; filter: none !important; backdrop-filter: none !important; overflow: unset !important;';
      
      const mainContent = document.querySelector('main');
      const dashboardWrapper = document.querySelector('div.flex.min-h-screen');
      
      if (mainContent) {
        (mainContent as HTMLElement).style.cssText += ' opacity: 1 !important; filter: none !important;';
      }
      if (dashboardWrapper) {
        (dashboardWrapper as HTMLElement).style.cssText += ' opacity: 1 !important; filter: none !important;';
      }
    };
    
    cleanupStyles();
    const interval = setInterval(cleanupStyles, 500); // Continuous cleanup
    
    return () => {
      clearInterval(interval);
      cleanupStyles();
    };
  }, []);

  useEffect(() => {
    if (user) {
      setFormDefaults({
        gender: user.gender ? user.gender.toLowerCase() : '',
        age: user.age ? String(user.age) : '',
        height_cm: user.height_cm ? String(user.height_cm) : '',
        ethnicity: user.ethnicity || ''
      });
    }
  }, [user]);

  const bodyFatAccess = checkFeatureAccess('body_fat_scan');
  const percentileAccess = checkFeatureAccess('percentile_scan');
  const transformationAccess = checkFeatureAccess('transformation');
  const enhancementAccess = checkFeatureAccess('enhancement');

  const scanTypes = [
    {
      id: 'bodyfat' as ScanType,
      title: 'Body Fat Estimate',
      description: 'Estimate your body fat percentage from a photo',
      icon: Scan,
      access: bodyFatAccess,
      premium: false,
    },
    {
      id: 'percentile' as ScanType,
      title: 'Percentile Ranking',
      description: 'Compare your body composition to demographic groups',
      icon: Award,
      access: percentileAccess,
      premium: false,
    },
    {
      id: 'transformation' as ScanType,
      title: 'Transformation Preview',
      description: 'AI-generated preview of your body transformation',
      icon: Sparkles,
      access: transformationAccess,
      premium: true,
    },
    {
      id: 'enhancement' as ScanType,
      title: 'Photo Enhancement',
      description: 'Professional body profile retouching — same body, polished look',
      icon: Wand2,
      access: enhancementAccess,
      premium: true,
    },
  ];

  const handleFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      setError('Please select an image file');
      return;
    }

    setSelectedFile(file);

    const reader = new FileReader();
    reader.onloadend = () => {
      setSelectedImage(reader.result as string);
      setResults({});
      setError(null);
      
      // 🔧 Aggressive style cleanup after image selection
      const cleanupStyles = () => {
        const html = document.documentElement;
        const body = document.body;
        
        // Reset root elements
        html.style.cssText = 'opacity: 1 !important; filter: none !important; backdrop-filter: none !important;';
        body.style.cssText += ' opacity: 1 !important; filter: none !important; backdrop-filter: none !important; overflow: unset !important;';
        
        // Reset all parent containers
        const mainContent = document.querySelector('main');
        const dashboardWrapper = document.querySelector('div.flex.min-h-screen');
        
        if (mainContent) {
          (mainContent as HTMLElement).style.cssText += ' opacity: 1 !important; filter: none !important; backdrop-filter: none !important;';
        }
        if (dashboardWrapper) {
          (dashboardWrapper as HTMLElement).style.cssText += ' opacity: 1 !important; filter: none !important; backdrop-filter: none !important;';
        }
        
        // Remove any overlay elements
        const overlays = document.querySelectorAll('[class*="overlay"]:not(nav), [class*="backdrop"]:not(nav)');
        overlays.forEach(el => {
          if (!el.closest('nav') && !el.closest('aside')) {
            (el as HTMLElement).remove();
          }
        });
      };
      
      cleanupStyles();
      setTimeout(cleanupStyles, 50);
      requestAnimationFrame(cleanupStyles);
    };
    reader.readAsDataURL(file);
  };

  const handleScan = async (formData: any) => {
    if (!selectedImage || !selectedFile) {
      setError('No file selected');
      return;
    }

    // Validate required fields based on scan type
    if (selectedType === 'percentile' && !formData.ethnicity) {
      setError('Please enter your ethnicity for Percentile Ranking');
      return;
    }

    if (!formData.gender || !formData.age) {
      setError('Please fill in all required fields (Gender and Age)');
      return;
    }

    const scanAccess = scanTypes.find(t => t.id === selectedType)?.access;
    if (!scanAccess?.hasAccess && !isPremium) {
      setError('You have reached your scan limit. Upgrade to Premium for unlimited scans.');
      return;
    }

    setIsScanning(true);
    setError(null);

    try {
      const base64 = await compressAndConvertToBase64(selectedFile);

      const requestData: BodyScanRequest = {
        image_base64: base64,
        scan_type: selectedType,
        gender: formData.gender,
        age: formData.age ? Number(formData.age) : undefined,
        ethnicity: formData.ethnicity || undefined,
        height_cm: formData.height_cm ? Number(formData.height_cm) : undefined,
        target_bf: formData.target_bf ? Number(formData.target_bf) : undefined,
      };

      let response;
      switch (selectedType) {
        case 'bodyfat':
          response = await bodyApi.estimateBodyFat(requestData);
          break;
        case 'percentile':
          response = await bodyApi.calculatePercentile(requestData);
          break;
        case 'transformation':
          response = await bodyApi.generateTransformation(requestData);
          break;
        case 'enhancement':
          response = await bodyApi.generateEnhancement(requestData);
          break;
      }

      // Store result by type
      const newResults: any = {
        ...results,
        [selectedType]: response.data
      };
      
      // If percentile scan, also extract body fat data for the body fat tab
      if (selectedType === 'percentile' && response.data.percentile_data?.body_fat_percentage) {
        newResults.bodyfat = {
          body_fat_percentage: response.data.percentile_data.body_fat_percentage,
          confidence: 'medium',
          recommendations: [],
          scan_id: response.data.scan_id,
          usage_remaining: response.data.usage_remaining
        };
      }
      
      setResults(newResults);
      await refreshLimits();
    } catch (err: any) {
      console.error('Body scan error:', err);
      console.error('Error response:', err.response);
      console.error('Error data:', err.response?.data);
      
      if (err.response?.status === 402) {
        setError('You have reached your scan limit or this feature requires Premium.');
      } else {
        const errorMessage = err.response?.data?.detail || err.message || 'Failed to scan image';
        setError(errorMessage);
        console.error('Final error message:', errorMessage);
      }
    } finally {
      setIsScanning(false);
      
      // 🔧 Aggressive style cleanup after scan
      const cleanupStyles = () => {
        const html = document.documentElement;
        const body = document.body;
        
        html.style.cssText = 'opacity: 1 !important; filter: none !important; backdrop-filter: none !important;';
        body.style.cssText += ' opacity: 1 !important; filter: none !important; backdrop-filter: none !important; overflow: unset !important;';
        
        const mainContent = document.querySelector('main');
        const dashboardWrapper = document.querySelector('div.flex.min-h-screen');
        
        if (mainContent) {
          (mainContent as HTMLElement).style.cssText += ' opacity: 1 !important; filter: none !important; backdrop-filter: none !important;';
        }
        if (dashboardWrapper) {
          (dashboardWrapper as HTMLElement).style.cssText += ' opacity: 1 !important; filter: none !important; backdrop-filter: none !important;';
        }
        
        const overlays = document.querySelectorAll('[class*="overlay"]:not(nav), [class*="backdrop"]:not(nav)');
        overlays.forEach(el => {
          if (!el.closest('nav') && !el.closest('aside')) {
            (el as HTMLElement).remove();
          }
        });
      };
      
      cleanupStyles();
      setTimeout(cleanupStyles, 50);
      requestAnimationFrame(cleanupStyles);
    }
  };

  const renderResult = () => {
    const result = results[selectedType];
    if (!result) return null;

    switch (selectedType) {
      case 'bodyfat':
        const bfResult = result as BodyFatEstimateResponse;
        if (!bfResult || typeof bfResult.body_fat_percentage !== 'number') {
          return (
            <Card variant="elevated">
              <CardContent>
                <p className="text-text-secondary text-center">No body fat data available</p>
              </CardContent>
            </Card>
          );
        }
        return (
          <Card variant="elevated">
            <CardHeader>
              <CardTitle>Body Fat Estimate</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center mb-6">
                <p className="text-5xl font-bold text-primary mb-2">
                  {bfResult.body_fat_percentage.toFixed(1)}%
                </p>
                <Badge variant={
                  bfResult.confidence === 'high' ? 'success' :
                  bfResult.confidence === 'medium' ? 'warning' : 'error'
                }>
                  {bfResult.confidence || 'medium'} Confidence
                </Badge>
              </div>
              {bfResult.recommendations && bfResult.recommendations.length > 0 && (
                <div>
                  <h4 className="font-semibold text-text mb-3">Recommendations:</h4>
                  <ul className="space-y-2">
                    {bfResult.recommendations.map((rec, i) => (
                      <li key={i} className="text-text-secondary">• {rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        );

      case 'percentile':
        const percResult = result as PercentileResponse;
        if (!percResult.percentile_data) {
          return (
            <Card variant="elevated">
              <CardContent>
                <p className="text-text-secondary text-center">No percentile data available</p>
              </CardContent>
            </Card>
          );
        }
        return (
          <Card variant="elevated">
            <CardHeader>
              <CardTitle>Percentile Ranking</CardTitle>
            </CardHeader>
            <CardContent>
              {/* Top Stats */}
              <div className="grid grid-cols-2 gap-4 mb-8">
                <div className="text-center p-4 bg-gradient-to-br from-primary/10 to-primary/5 rounded-xl border border-primary/20">
                  <p className="text-sm text-text-secondary mb-1">Your Ranking</p>
                  <p className="text-4xl font-bold text-primary mb-1">
                    Top {(100 - percResult.percentile_data.percentile).toFixed(0)}%
                  </p>
                  <p className="text-sm font-medium text-primary">
                    {percResult.percentile_data.rank_text}
                  </p>
                </div>
                <div className="text-center p-4 bg-surfaceAlt rounded-xl border border-border">
                  <p className="text-sm text-text-secondary mb-1">Your Body Fat</p>
                  <p className="text-4xl font-bold text-text mb-1">
                    {percResult.percentile_data.body_fat_percentage.toFixed(1)}%
                  </p>
                  <p className="text-xs text-text-light">
                    {percResult.percentile_data.comparison_group}
                  </p>
                </div>
              </div>

              {/* Bell Curve Visualization */}
              {percResult.distribution_data && (
                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-text mb-4 text-center">
                    Population Distribution
                  </h4>
                  <BellCurveChart
                    mean={percResult.distribution_data.mean}
                    std={percResult.distribution_data.std}
                    userValue={percResult.distribution_data.user_value}
                    percentile={percResult.distribution_data.better_than_percent || percResult.percentile_data.percentile}
                    unit="%"
                  />
                </div>
              )}

              {/* Interpretation */}
              <div className="mt-6 p-4 bg-primary/10 border border-primary/30 rounded-lg">
                <p className="text-sm text-text">
                  <span className="font-semibold">What this means:</span> You have{' '}
                  <span className="font-bold text-primary">lower body fat</span> than{' '}
                  <span className="font-bold text-primary">
                    {percResult.percentile_data.percentile.toFixed(0)}%
                  </span>{' '}
                  of {percResult.percentile_data.comparison_group.toLowerCase()}. You're in the{' '}
                  <span className="font-bold text-primary">
                    top {(100 - percResult.percentile_data.percentile).toFixed(0)}%
                  </span>!
                </p>
              </div>
            </CardContent>
          </Card>
        );

      case 'transformation':
        const transResult = result as TransformationResponse;
        if (!transResult || !transResult.transformed_image_url) {
          return (
            <Card variant="elevated">
              <CardContent>
                <p className="text-text-secondary text-center">No transformation data available</p>
              </CardContent>
            </Card>
          );
        }
        const isCutting = transResult.direction === 'cutting';
        const directionLabel = isCutting ? 'Cutting' : 'Bulking';
        const directionColor = isCutting ? 'text-blue-600' : 'text-orange-600';
        const directionBg = isCutting ? 'bg-blue-50 border-blue-200' : 'bg-orange-50 border-orange-200';
        return (
          <Card variant="elevated">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Transformation Preview</CardTitle>
                {transResult.direction && (
                  <Badge variant={isCutting ? 'info' : 'warning'}>
                    {isCutting ? 'Cutting' : 'Bulking'}
                  </Badge>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4 mb-6">
                <div>
                  <p className="text-sm font-medium text-text-secondary mb-2">Current</p>
                  <img
                    src={selectedImage || ''}
                    alt="Current"
                    className="w-full rounded-lg"
                  />
                </div>
                <div>
                  <p className="text-sm font-medium text-text-secondary mb-2">Projected</p>
                  <img
                    src={transResult.transformed_image_url}
                    alt="Transformation"
                    className="w-full rounded-lg"
                  />
                </div>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                {transResult.current_bf != null && (
                  <div className="p-3 bg-surfaceAlt rounded-lg text-center">
                    <p className="text-xs text-text-secondary">현재 체지방</p>
                    <p className="text-xl font-bold text-text">{transResult.current_bf.toFixed(1)}%</p>
                  </div>
                )}
                {transResult.target_bf != null && (
                  <div className="p-3 bg-surfaceAlt rounded-lg text-center">
                    <p className="text-xs text-text-secondary">목표 체지방</p>
                    <p className="text-xl font-bold text-primary">{transResult.target_bf.toFixed(1)}%</p>
                  </div>
                )}
                {transResult.muscle_gain_estimate && (
                  <div className="p-3 bg-surfaceAlt rounded-lg text-center">
                    <p className="text-xs text-text-secondary">예상 근육 증가</p>
                    <p className="text-xl font-bold text-text">+{transResult.muscle_gain_estimate}</p>
                  </div>
                )}
                <div className="p-3 bg-surfaceAlt rounded-lg text-center">
                  <p className="text-xs text-text-secondary">예상 소요기간</p>
                  <p className="text-xl font-bold text-text">{transResult.estimated_timeline_weeks}주</p>
                </div>
              </div>

              {/* Direction Indicator */}
              {transResult.direction && (
                <div className={`p-3 rounded-lg border ${directionBg} mb-4`}>
                  <p className={`text-sm font-semibold ${directionColor}`}>
                    {isCutting
                      ? '체지방 감량 + 근육 유지/증가 목표'
                      : '근육량 증가 + 건강한 벌크업 목표'}
                  </p>
                </div>
              )}

              {transResult.recommendations && transResult.recommendations.length > 0 && (
                <div>
                  <h4 className="font-semibold text-text mb-2">Recommendations:</h4>
                  <ul className="space-y-1 text-sm text-text-secondary">
                    {transResult.recommendations.map((rec, i) => (
                      <li key={i}>• {rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        );

      case 'enhancement':
        const enhResult = result as EnhancementResponse;
        if (!enhResult || !enhResult.enhanced_image_url) {
          return (
            <Card variant="elevated">
              <CardContent>
                <p className="text-text-secondary text-center">No enhancement data available</p>
              </CardContent>
            </Card>
          );
        }
        const levelLabel = { subtle: 'Subtle', natural: 'Natural', studio: 'Studio' }[enhResult.enhancement_level] || 'Natural';
        return (
          <Card variant="elevated">
            <CardHeader>
              <CardTitle>Photo Enhancement</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4 mb-6">
                <div>
                  <p className="text-sm font-medium text-text-secondary mb-2">Original</p>
                  <img
                    src={selectedImage || ''}
                    alt="Original"
                    className="w-full rounded-lg"
                  />
                </div>
                <div>
                  <p className="text-sm font-medium text-text-secondary mb-2">Enhanced</p>
                  <img
                    src={enhResult.enhanced_image_url}
                    alt="Enhanced"
                    className="w-full rounded-lg"
                  />
                </div>
              </div>
              <div className="p-3 bg-surfaceAlt rounded-lg">
                <p className="text-sm text-text-secondary">Enhancement Level</p>
                <p className="text-lg font-bold text-text">{levelLabel}</p>
              </div>
              <p className="mt-4 text-xs text-text-light text-center">
                Body proportions unchanged — only lighting, skin tone, and muscle definition enhanced
              </p>
            </CardContent>
          </Card>
        );

      default:
        return null;
    }
  };

  const selectedScanType = scanTypes.find(t => t.id === selectedType);
  const canScan = selectedScanType?.access.hasAccess || isPremium;

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold text-text">Body Scanner</h1>
        <p className="text-text-secondary mt-1">
          AI-powered body composition analysis
        </p>
      </div>

      {/* Scan Type Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {scanTypes.map((type) => {
          const Icon = type.icon;
          const isSelected = selectedType === type.id;
          const hasAccess = type.access.hasAccess || isPremium;

          return (
            <Card
              key={type.id}
              variant={isSelected ? 'elevated' : 'outlined'}
              className={`cursor-pointer transition-all ${
                isSelected ? 'ring-2 ring-primary' : 'hover:shadow-md'
              }`}
              onClick={() => setSelectedType(type.id)}
            >
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <Icon className="h-8 w-8 text-primary" />
                  {type.premium && !isPremium && (
                    <Badge variant="premium">
                      <Crown className="h-3 w-3 mr-1" />
                      Premium
                    </Badge>
                  )}
                </div>
                <h3 className="font-semibold text-text mb-2">{type.title}</h3>
                <p className="text-sm text-text-secondary mb-3">{type.description}</p>
                {!isPremium && (
                  <Badge
                    variant={hasAccess ? 'info' : 'error'}
                    className="text-xs"
                  >
                    {hasAccess
                      ? `${type.access.remaining} / ${type.access.limit} remaining`
                      : 'Limit reached'}
                  </Badge>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Scan Interface */}
      <Card variant="elevated">
        <CardHeader>
          <CardTitle>{selectedScanType?.title}</CardTitle>
        </CardHeader>
        <CardContent>
          {!selectedImage ? (
            <div>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="hidden"
              />
              <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-border rounded-lg p-12 text-center cursor-pointer hover:border-primary transition-colors"
              >
                <Scan className="h-16 w-16 text-text-light mx-auto mb-4" />
                <p className="text-lg font-medium text-text mb-2">Upload Body Photo</p>
                <p className="text-sm text-text-secondary">
                  Click to select a full-body photo
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              <img
                src={selectedImage}
                alt="Selected"
                className="w-full max-h-96 object-contain rounded-lg"
              />

              {!results[selectedType] && (
                <form
                  key={JSON.stringify(formDefaults)}
                  onSubmit={(e) => {
                    e.preventDefault();
                    const formData = new FormData(e.currentTarget);
                    handleScan(Object.fromEntries(formData));
                  }}
                  className="space-y-4"
                >
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Select name="gender" label="Gender" required defaultValue={formDefaults.gender}>
                      <option value="">Select...</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                    </Select>
                    <Input 
                      name="age" 
                      label="Age" 
                      type="number" 
                      placeholder="30" 
                      defaultValue={formDefaults.age}
                    />
                  </div>

                  {selectedType === 'percentile' && (
                    <Select 
                      name="ethnicity" 
                      label="Ethnicity" 
                      defaultValue={formDefaults.ethnicity}
                      required
                    >
                      <option value="">Select...</option>
                      <option value="Asian">Asian</option>
                      <option value="Caucasian">Caucasian</option>
                      <option value="African">African</option>
                      <option value="Hispanic">Hispanic</option>
                      <option value="Middle Eastern">Middle Eastern</option>
                      <option value="Pacific Islander">Pacific Islander</option>
                      <option value="Mixed">Mixed</option>
                      <option value="Other">Other</option>
                    </Select>
                  )}

                  {selectedType === 'transformation' && (
                    <Input
                      name="target_bf"
                      label="목표 체지방률 (Target Body Fat %)"
                      type="number"
                      step="0.5"
                      min="3"
                      max="45"
                      placeholder="12"
                      required
                    />
                  )}

                  {selectedType === 'enhancement' && (
                    <Select name="enhancement_level" label="Enhancement Level" defaultValue="natural">
                      <option value="subtle">Subtle — 살짝 보정</option>
                      <option value="natural">Natural — 자연스러운 보정 (추천)</option>
                      <option value="studio">Studio — 스튜디오급 보정</option>
                    </Select>
                  )}

                  <Input 
                    name="height_cm" 
                    label="Height (cm)" 
                    type="number" 
                    placeholder="170" 
                    defaultValue={formDefaults.height_cm}
                  />

                  <Button
                    type="submit"
                    variant="primary"
                    size="lg"
                    isLoading={isScanning}
                    disabled={!canScan}
                    className="w-full"
                  >
                    <Scan className="h-5 w-5 mr-2" />
                    Start Scan
                  </Button>

                  {!canScan && (
                    <Button
                      type="button"
                      variant="primary"
                      onClick={() => router.push('/upgrade')}
                      className="w-full bg-premium text-primary hover:bg-premium-dark"
                    >
                      <Crown className="h-5 w-5 mr-2" />
                      Upgrade to Premium
                    </Button>
                  )}
                </form>
              )}
            </div>
          )}

          {error && (
            <div className="mt-4 p-4 bg-error/10 border border-error rounded-lg">
              <p className="text-sm text-error">{error}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Results */}
      {results[selectedType] && renderResult()}
    </div>
  );
}
