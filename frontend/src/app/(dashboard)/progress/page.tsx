'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import Image from 'next/image';
import GoalProjectionChart from '@/components/features/GoalProjectionChart';
import WeightLogForm from '@/components/features/WeightLogForm';
import GoalSettingForm from '@/components/features/GoalSettingForm';
import { Modal } from '@/components/ui/Modal';
import { progressPhotoApi } from '@/lib/api/services';
import { compressAndConvertToBase64 } from '@/lib/utils/image';
import { Camera, ImageIcon, ArrowLeftRight, Trash2, X, Plus, ChevronLeft, ChevronRight, Check } from 'lucide-react';

interface ProgressPhoto {
  id: string;
  notes: string;
  weight_kg: number | null;
  body_fat_pct: number | null;
  taken_at: string;
  created_at: string;
  image_base64?: string;
}

interface CompareData {
  before: ProgressPhoto;
  after: ProgressPhoto;
  days_between: number | null;
  weight_change: number | null;
  bf_change: number | null;
}

type Tab = 'goals' | 'photos';

export default function ProgressPage() {
  const [activeTab, setActiveTab] = useState<Tab>('goals');
  const [showWeightLogModal, setShowWeightLogModal] = useState(false);
  const [showGoalModal, setShowGoalModal] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  // Photo state
  const [photos, setPhotos] = useState<ProgressPhoto[]>([]);
  const [loadingPhotos, setLoadingPhotos] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadNotes, setUploadNotes] = useState('');
  const [uploadWeight, setUploadWeight] = useState('');
  const [uploadBodyFat, setUploadBodyFat] = useState('');
  const [uploadPreview, setUploadPreview] = useState<string | null>(null);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Compare state
  const [compareMode, setCompareMode] = useState(false);
  const [selectedPhotos, setSelectedPhotos] = useState<string[]>([]);
  const [compareData, setCompareData] = useState<CompareData | null>(null);
  const [loadingCompare, setLoadingCompare] = useState(false);

  // Full-size view
  const [viewingPhoto, setViewingPhoto] = useState<ProgressPhoto | null>(null);
  const [loadingFullPhoto, setLoadingFullPhoto] = useState(false);

  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleWeightLogSuccess = () => {
    setShowWeightLogModal(false);
    setRefreshKey(prev => prev + 1);
  };

  const handleGoalSuccess = () => {
    setShowGoalModal(false);
    setRefreshKey(prev => prev + 1);
  };

  const fetchPhotos = useCallback(async () => {
    setLoadingPhotos(true);
    try {
      const res = await progressPhotoApi.getAll();
      setPhotos(res.data);
    } catch {
      console.error('Failed to fetch photos');
    } finally {
      setLoadingPhotos(false);
    }
  }, []);

  useEffect(() => {
    if (activeTab === 'photos') {
      fetchPhotos();
    }
  }, [activeTab, fetchPhotos]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadFile(file);
    const reader = new FileReader();
    reader.onload = () => setUploadPreview(reader.result as string);
    reader.readAsDataURL(file);
  };

  const handleUpload = async () => {
    if (!uploadFile) return;
    setUploading(true);
    try {
      const base64 = await compressAndConvertToBase64(uploadFile);
      await progressPhotoApi.upload(
        base64,
        uploadNotes || undefined,
        uploadWeight ? parseFloat(uploadWeight) : undefined,
        uploadBodyFat ? parseFloat(uploadBodyFat) : undefined
      );
      setShowUpload(false);
      setUploadPreview(null);
      setUploadFile(null);
      setUploadNotes('');
      setUploadWeight('');
      setUploadBodyFat('');
      fetchPhotos();
    } catch {
      console.error('Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleDeletePhoto = async (photoId: string) => {
    setDeletingId(photoId);
    try {
      await progressPhotoApi.delete(photoId);
      setPhotos(prev => prev.filter(p => p.id !== photoId));
      if (viewingPhoto?.id === photoId) setViewingPhoto(null);
    } catch {
      console.error('Delete failed');
    } finally {
      setDeletingId(null);
    }
  };

  const handleViewPhoto = async (photo: ProgressPhoto) => {
    setLoadingFullPhoto(true);
    setViewingPhoto(photo);
    try {
      const res = await progressPhotoApi.getOne(photo.id);
      setViewingPhoto(res.data);
    } catch {
      console.error('Failed to load photo');
    } finally {
      setLoadingFullPhoto(false);
    }
  };

  const togglePhotoSelection = (photoId: string) => {
    setSelectedPhotos(prev => {
      if (prev.includes(photoId)) return prev.filter(id => id !== photoId);
      if (prev.length >= 2) return [prev[1], photoId];
      return [...prev, photoId];
    });
  };

  const handleCompare = async () => {
    if (selectedPhotos.length !== 2) return;
    setLoadingCompare(true);
    try {
      const res = await progressPhotoApi.compare(selectedPhotos[0], selectedPhotos[1]);
      setCompareData(res.data);
    } catch {
      console.error('Compare failed');
    } finally {
      setLoadingCompare(false);
    }
  };

  const exitCompareMode = () => {
    setCompareMode(false);
    setSelectedPhotos([]);
    setCompareData(null);
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Goal Progress Tracking</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Track your weight, goals, and visual progress over time
          </p>
        </div>

        <div data-tour="progress-actions" className="flex gap-3">
          {activeTab === 'goals' && (
            <>
              <button
                onClick={() => setShowGoalModal(true)}
                className="px-4 py-2 bg-white dark:bg-gray-800 border-2 border-emerald-600 text-emerald-600 rounded-lg hover:bg-emerald-50 dark:hover:bg-gray-700 transition-colors font-medium"
              >
                🎯 Set Goal
              </button>
              <button
                onClick={() => setShowWeightLogModal(true)}
                className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors font-medium"
              >
                ⚖️ Log Weight
              </button>
            </>
          )}
          {activeTab === 'photos' && (
            <>
              <button
                onClick={() => compareMode ? exitCompareMode() : setCompareMode(true)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
                  compareMode
                    ? 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 border-2 border-amber-400'
                    : 'bg-white dark:bg-gray-800 border-2 border-emerald-600 text-emerald-600 hover:bg-emerald-50 dark:hover:bg-gray-700'
                }`}
              >
                <ArrowLeftRight className="w-4 h-4" />
                {compareMode ? 'Cancel Compare' : 'Compare'}
              </button>
              <button
                onClick={() => setShowUpload(true)}
                className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors font-medium flex items-center gap-2"
              >
                <Camera className="w-4 h-4" />
                Add Photo
              </button>
            </>
          )}
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
        <button
          onClick={() => { setActiveTab('goals'); exitCompareMode(); }}
          className={`flex-1 py-2.5 px-4 rounded-md text-sm font-medium transition-all ${
            activeTab === 'goals'
              ? 'bg-white dark:bg-gray-700 text-emerald-600 dark:text-emerald-400 shadow-sm'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'
          }`}
        >
          📊 Goals
        </button>
        <button
          onClick={() => setActiveTab('photos')}
          className={`flex-1 py-2.5 px-4 rounded-md text-sm font-medium transition-all ${
            activeTab === 'photos'
              ? 'bg-white dark:bg-gray-700 text-emerald-600 dark:text-emerald-400 shadow-sm'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'
          }`}
        >
          📸 Photos
        </button>
      </div>

      {/* ==================== GOALS TAB ==================== */}
      {activeTab === 'goals' && (
        <>
          {/* Info Card */}
          <div className="bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-950 dark:to-teal-950 border border-emerald-200 dark:border-emerald-800 rounded-lg p-6">
            <div className="flex items-start gap-4">
              <div className="text-4xl">📊</div>
              <div>
                <h3 className="font-semibold text-emerald-800 dark:text-emerald-300 mb-2">
                  3-Day Moving Average Based Prediction
                </h3>
                <p className="text-sm text-emerald-700 dark:text-emerald-400">
                  Averages weight changes over the last 3 days to calculate daily rate of change,
                  and provides an estimated goal date considering your current calorie deficit.
                </p>
                <p className="text-xs text-emerald-600 dark:text-emerald-500 mt-2">
                  💡 Tip: Weighing at the same time each day enables more accurate predictions.
                </p>
              </div>
            </div>
          </div>

          {/* Goal Projection Chart */}
          <div data-tour="progress-chart">
            <GoalProjectionChart key={refreshKey} daysHistory={30} />
          </div>
        </>
      )}

      {/* ==================== PHOTOS TAB ==================== */}
      {activeTab === 'photos' && (
        <div data-tour="progress-photos" className="space-y-6">
          {/* Compare mode banner */}
          {compareMode && !compareData && (
            <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4 flex items-center gap-3">
              <ArrowLeftRight className="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm font-medium text-amber-800 dark:text-amber-300">
                  Select 2 photos to compare side-by-side
                </p>
                <p className="text-xs text-amber-600 dark:text-amber-500">
                  {selectedPhotos.length}/2 selected
                </p>
              </div>
              {selectedPhotos.length === 2 && (
                <button
                  onClick={handleCompare}
                  disabled={loadingCompare}
                  className="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors font-medium text-sm disabled:opacity-50"
                >
                  {loadingCompare ? 'Loading...' : 'Compare Now'}
                </button>
              )}
            </div>
          )}

          {/* Compare View */}
          {compareData && (
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
              <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-semibold text-gray-800 dark:text-white flex items-center gap-2">
                  <ArrowLeftRight className="w-5 h-5 text-emerald-600" />
                  Side-by-Side Comparison
                </h3>
                <button
                  onClick={exitCompareMode}
                  className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="grid grid-cols-2 gap-0.5 bg-gray-200 dark:bg-gray-700">
                {[compareData.before, compareData.after].map((photo, idx) => (
                  <div key={photo.id} className="bg-white dark:bg-gray-800 p-4 space-y-3">
                    <div className="text-center">
                      <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                        idx === 0
                          ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400'
                          : 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400'
                      }`}>
                        {idx === 0 ? 'Before' : 'After'}
                      </span>
                    </div>
                    {photo.image_base64 && (
                      <div className="relative aspect-[3/4] w-full rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-900">
                        <Image
                          src={`data:image/jpeg;base64,${photo.image_base64}`}
                          alt={idx === 0 ? 'Before' : 'After'}
                          fill
                          className="object-cover"
                          unoptimized
                        />
                      </div>
                    )}
                    <div className="text-center space-y-1">
                      <p className="text-sm font-medium text-gray-800 dark:text-gray-200">
                        {formatDate(photo.taken_at)}
                      </p>
                      {photo.weight_kg && (
                        <p className="text-xs text-gray-500 dark:text-gray-400">{photo.weight_kg} kg</p>
                      )}
                      {photo.body_fat_pct && (
                        <p className="text-xs text-gray-500 dark:text-gray-400">{photo.body_fat_pct}% body fat</p>
                      )}
                      {photo.notes && (
                        <p className="text-xs text-gray-400 dark:text-gray-500 italic">{photo.notes}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Photo Grid */}
          {loadingPhotos ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="aspect-[3/4] rounded-xl bg-gray-200 dark:bg-gray-700 animate-pulse" />
              ))}
            </div>
          ) : photos.length === 0 ? (
            <div className="text-center py-16 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
              <ImageIcon className="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
              <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-200 mb-2">
                No progress photos yet
              </h3>
              <p className="text-gray-500 dark:text-gray-400 mb-6 max-w-sm mx-auto">
                Take your first photo to start tracking your visual transformation over time.
              </p>
              <button
                onClick={() => setShowUpload(true)}
                className="px-6 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors font-medium inline-flex items-center gap-2"
              >
                <Camera className="w-5 h-5" />
                Upload First Photo
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
              {photos.map(photo => {
                const isSelected = selectedPhotos.includes(photo.id);
                return (
                  <div
                    key={photo.id}
                    className={`group relative aspect-[3/4] rounded-xl overflow-hidden bg-gray-100 dark:bg-gray-800 border-2 transition-all cursor-pointer ${
                      isSelected
                        ? 'border-emerald-500 ring-2 ring-emerald-500/30'
                        : 'border-transparent hover:border-gray-300 dark:hover:border-gray-600'
                    }`}
                    onClick={() => compareMode ? togglePhotoSelection(photo.id) : handleViewPhoto(photo)}
                  >
                    {/* Thumbnail placeholder — the list endpoint doesn't return image_base64 */}
                    <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-800">
                      <ImageIcon className="w-10 h-10 text-gray-400 dark:text-gray-500" />
                    </div>

                    {/* Compare checkbox */}
                    {compareMode && (
                      <div className={`absolute top-2 right-2 w-6 h-6 rounded-full border-2 flex items-center justify-center z-10 ${
                        isSelected
                          ? 'bg-emerald-500 border-emerald-500 text-white'
                          : 'border-white bg-black/30 text-transparent'
                      }`}>
                        <Check className="w-4 h-4" />
                      </div>
                    )}

                    {/* Overlay info */}
                    <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent p-3 pt-8">
                      <p className="text-white text-sm font-medium">
                        {formatDate(photo.taken_at)}
                      </p>
                      <div className="flex items-center gap-2 mt-0.5">
                        {photo.weight_kg && (
                          <span className="text-white/80 text-xs">{photo.weight_kg} kg</span>
                        )}
                        {photo.body_fat_pct && (
                          <span className="text-white/80 text-xs">{photo.body_fat_pct}% BF</span>
                        )}
                      </div>
                      {photo.notes && (
                        <p className="text-white/60 text-xs mt-1 truncate">{photo.notes}</p>
                      )}
                    </div>

                    {/* Delete button */}
                    {!compareMode && (
                      <button
                        onClick={e => { e.stopPropagation(); handleDeletePhoto(photo.id); }}
                        disabled={deletingId === photo.id}
                        className="absolute top-2 right-2 p-1.5 rounded-full bg-black/40 text-white/80 opacity-0 group-hover:opacity-100 hover:bg-red-600 hover:text-white transition-all z-10"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* ==================== UPLOAD MODAL ==================== */}
      <Modal isOpen={showUpload} onClose={() => setShowUpload(false)} title="Upload Progress Photo" size="lg">
        <div className="space-y-4">
          {/* File picker */}
          <div
            onClick={() => fileInputRef.current?.click()}
            className="relative border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl p-8 text-center cursor-pointer hover:border-emerald-400 dark:hover:border-emerald-500 transition-colors"
          >
            {uploadPreview ? (
              <div className="relative aspect-[3/4] max-h-64 mx-auto overflow-hidden rounded-lg">
                <Image
                  src={uploadPreview}
                  alt="Preview"
                  fill
                  className="object-contain"
                  unoptimized
                />
              </div>
            ) : (
              <div>
                <Camera className="w-12 h-12 mx-auto text-gray-400 dark:text-gray-500 mb-3" />
                <p className="text-gray-600 dark:text-gray-400 font-medium">
                  Click to select a photo
                </p>
                <p className="text-gray-400 dark:text-gray-500 text-sm mt-1">
                  JPG, PNG up to 10MB
                </p>
              </div>
            )}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>

          {/* Optional metadata */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Weight (kg)
              </label>
              <input
                type="number"
                step="0.1"
                value={uploadWeight}
                onChange={e => setUploadWeight(e.target.value)}
                placeholder="e.g. 75.5"
                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Body Fat (%)
              </label>
              <input
                type="number"
                step="0.1"
                value={uploadBodyFat}
                onChange={e => setUploadBodyFat(e.target.value)}
                placeholder="e.g. 18.5"
                className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Notes
            </label>
            <textarea
              value={uploadNotes}
              onChange={e => setUploadNotes(e.target.value)}
              placeholder="How are you feeling? Any milestones?"
              rows={2}
              className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-emerald-500 focus:border-transparent resize-none"
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-2">
            <button
              onClick={() => { setShowUpload(false); setUploadPreview(null); setUploadFile(null); }}
              className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 font-medium"
            >
              Cancel
            </button>
            <button
              onClick={handleUpload}
              disabled={!uploadFile || uploading}
              className="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {uploading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Plus className="w-4 h-4" />
                  Upload
                </>
              )}
            </button>
          </div>
        </div>
      </Modal>

      {/* ==================== FULL PHOTO VIEW MODAL ==================== */}
      <Modal
        isOpen={!!viewingPhoto}
        onClose={() => setViewingPhoto(null)}
        title="Progress Photo"
        size="lg"
      >
        {viewingPhoto && (
          <div className="space-y-4">
            {loadingFullPhoto ? (
              <div className="aspect-[3/4] rounded-lg bg-gray-200 dark:bg-gray-700 animate-pulse flex items-center justify-center">
                <div className="w-8 h-8 border-3 border-emerald-200 border-t-emerald-600 rounded-full animate-spin" />
              </div>
            ) : viewingPhoto.image_base64 ? (
              <div className="relative aspect-[3/4] w-full rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-900">
                <Image
                  src={`data:image/jpeg;base64,${viewingPhoto.image_base64}`}
                  alt="Progress photo"
                  fill
                  className="object-contain"
                  unoptimized
                />
              </div>
            ) : (
              <div className="aspect-[3/4] rounded-lg bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                <ImageIcon className="w-16 h-16 text-gray-400" />
              </div>
            )}

            <div className="flex items-center justify-between">
              <div>
                <p className="text-lg font-semibold text-gray-900 dark:text-white">
                  {formatDate(viewingPhoto.taken_at)}
                </p>
                <div className="flex items-center gap-3 mt-1">
                  {viewingPhoto.weight_kg && (
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {viewingPhoto.weight_kg} kg
                    </span>
                  )}
                  {viewingPhoto.body_fat_pct && (
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {viewingPhoto.body_fat_pct}% body fat
                    </span>
                  )}
                </div>
                {viewingPhoto.notes && (
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-2 italic">
                    {viewingPhoto.notes}
                  </p>
                )}
              </div>
              <button
                onClick={() => handleDeletePhoto(viewingPhoto.id)}
                disabled={deletingId === viewingPhoto.id}
                className="px-3 py-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors flex items-center gap-1.5 text-sm font-medium"
              >
                <Trash2 className="w-4 h-4" />
                Delete
              </button>
            </div>
          </div>
        )}
      </Modal>

      {/* Weight Log Modal */}
      <Modal
        isOpen={showWeightLogModal}
        onClose={() => setShowWeightLogModal(false)}
        title="Log Weight"
      >
        <WeightLogForm
          onSuccess={handleWeightLogSuccess}
          onCancel={() => setShowWeightLogModal(false)}
        />
      </Modal>

      {/* Goal Setting Modal */}
      <Modal
        isOpen={showGoalModal}
        onClose={() => setShowGoalModal(false)}
        title="Set Goal"
      >
        <GoalSettingForm
          onSuccess={handleGoalSuccess}
          onCancel={() => setShowGoalModal(false)}
        />
      </Modal>
    </div>
  );
}
