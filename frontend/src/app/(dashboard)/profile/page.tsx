'use client';

import { useState, useEffect, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { User as UserIcon, Crown, LogOut, Settings, Bell, Coins, Camera, Scan, BarChart3, Sparkles, Dumbbell, Play, AlertTriangle, Trash2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, Button, Input, Select, Badge, Modal } from '@/components/ui';
import { useAuth } from '@/contexts/AuthContext';
import { useSubscription } from '@/lib/hooks/useSubscription';
import { TOUR_START_EVENT, resetAllTours } from '@/components/tour/FeatureTour';
import { paymentApi } from '@/lib/api/services';
import { formatDateLong } from '@/lib/utils/date';
import { useLanguage } from '@/contexts/LanguageContext';
import type { SubscriptionResponse } from '@/types/api';
import {
  ACCOUNT_DELETION_BLOCKING_REQUIREMENT,
  ACCOUNT_DELETION_CONFIRM_PHRASE,
  ACCOUNT_DELETION_DELETED_IMMEDIATELY,
  ACCOUNT_DELETION_RETAINED_OUTSIDE_APP,
} from '@/lib/constants/accountDeletion';

export default function ProfilePage() {
  const router = useRouter();
  const { t } = useLanguage();
  const { user, logout, deleteAccount, updateProfile } = useAuth();
  const { isPremium } = useSubscription();
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [creditBalance, setCreditBalance] = useState<number | null>(null);
  const [subscriptionStatus, setSubscriptionStatus] = useState<SubscriptionResponse | null>(null);
  const [subscriptionStatusLoaded, setSubscriptionStatusLoaded] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState('');
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [isDeletingAccount, setIsDeletingAccount] = useState(false);
  const [isOpeningBillingPortal, setIsOpeningBillingPortal] = useState(false);

  useEffect(() => {
    paymentApi.getCreditBalance()
      .then(res => setCreditBalance(res.data.total_credits))
      .catch(() => setCreditBalance(null));

    paymentApi.getSubscriptionStatus()
      .then(res => setSubscriptionStatus(res.data))
      .catch(() => setSubscriptionStatus(null))
      .finally(() => setSubscriptionStatusLoaded(true));
  }, []);

  const hasActiveBilling = subscriptionStatus?.deletion_blocked ?? false;
  const billingStatusUnknown = !subscriptionStatusLoaded || subscriptionStatus === null;

  const deletionBlockMessage = billingStatusUnknown
    ? 'We could not verify your billing status yet. Retry once billing status loads, or open billing management first.'
    : subscriptionStatus?.deletion_block_reason === 'billing_state_mismatch_requires_reconciliation'
    ? 'We cannot verify that your billing is fully canceled yet. Open billing management first, then try deleting your account again.'
    : ACCOUNT_DELETION_BLOCKING_REQUIREMENT;

  const handleLogout = async () => {
    if (confirm(t('profile.confirmLogout'))) {
      await logout();
      router.push('/login');
    }
  };

  const handleUpdateProfile = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setIsSaving(true);

    const formData = new FormData(e.currentTarget);
    const data = {
      full_name: formData.get('full_name') as string || undefined,
      height_cm: formData.get('height_cm') ? Number(formData.get('height_cm')) : undefined,
      weight_kg: formData.get('weight_kg') ? Number(formData.get('weight_kg')) : undefined,
      age: formData.get('age') ? Number(formData.get('age')) : undefined,
      gender: (formData.get('gender') as any) || undefined,
      ethnicity: (formData.get('ethnicity') as string) || undefined,
      activity_level: (formData.get('activity_level') as any) || undefined,
      calorie_goal: formData.get('calorie_goal') ? Number(formData.get('calorie_goal')) : undefined,
    };

    try {
      await updateProfile(data);
      setIsEditing(false);
      toast.success(t('profile.profileUpdated'));
    } catch (err: any) {
      setError(err.message || t('profile.failedToUpdate'));
      toast.error(t('profile.failedToUpdate'));
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteAccount = async () => {
    setDeleteError(null);

    if (billingStatusUnknown) {
      setDeleteError(deletionBlockMessage);
      return;
    }

    if (hasActiveBilling) {
      setDeleteError(deletionBlockMessage);
      return;
    }

    if (deleteConfirmText.trim().toUpperCase() !== ACCOUNT_DELETION_CONFIRM_PHRASE) {
      setDeleteError(`Type ${ACCOUNT_DELETION_CONFIRM_PHRASE} to confirm account deletion.`);
      return;
    }

    try {
      setIsDeletingAccount(true);
      await deleteAccount();
    } catch (err: any) {
      const message = err?.message || 'Failed to delete account';
      setDeleteError(message);
      toast.error(message);
    } finally {
      setIsDeletingAccount(false);
    }
  };

  const handleManageBilling = async () => {
    try {
      setIsOpeningBillingPortal(true);
      const response = await paymentApi.createBillingPortalSession(window.location.href);
      window.location.href = response.data.url;
    } catch (err: any) {
      toast.error(err?.message || 'Failed to open billing management');
    } finally {
      setIsOpeningBillingPortal(false);
    }
  };

  const featureList = [
    { nameKey: 'profile.foodCamera', cost: 1, icon: Camera, color: 'text-green-600' },
    { nameKey: 'profile.foodRecommendation', cost: 2, icon: Sparkles, color: 'text-blue-600' },
    { nameKey: 'profile.bodyfatScan', cost: 10, icon: Scan, color: 'text-purple-600' },
    { nameKey: 'profile.percentileScan', cost: 10, icon: BarChart3, color: 'text-indigo-600' },
    { nameKey: 'profile.formCheck', cost: 3, icon: Dumbbell, color: 'text-orange-600' },
    { nameKey: 'profile.transformation', cost: 30, icon: Sparkles, color: 'text-pink-600' },
  ];

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white dark:text-white">{t('profile.title')}</h1>
        <p className="text-gray-600 dark:text-gray-400 dark:text-gray-400 mt-1">
          {t('profile.subtitle')}
        </p>
      </div>

      {/* User Info Card */}
      <Card variant="elevated">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-4 bg-primary/10 rounded-full">
                <UserIcon className="h-8 w-8 text-primary" />
              </div>
              <div>
                <CardTitle>{user?.full_name || t('profile.user')}</CardTitle>
                <p className="text-sm text-gray-600 dark:text-gray-400 dark:text-gray-400">{user?.email}</p>
              </div>
            </div>
            {isPremium && (
              <Badge variant="premium" className="text-base px-4 py-2">
                <Crown className="h-4 w-4 mr-2" />
                {t('dashboard.premiumMember')}
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between pt-4 border-t border-gray-100 dark:border-gray-700 dark:border-gray-700">
            <p className="text-sm text-gray-600 dark:text-gray-400 dark:text-gray-400">
              {t('profile.memberSince', { date: user?.created_at ? formatDateLong(user.created_at) : 'N/A' })}
            </p>
            <div className="flex items-center gap-2">
              <Link
                href="/profile/notifications"
                className="inline-flex items-center rounded-lg border-2 border-primary/30 bg-transparent px-3.5 py-1.5 text-sm font-semibold text-primary transition-all duration-200 hover:bg-primary/10 hover:border-primary/50 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:ring-offset-2 focus:ring-offset-background"
              >
                <Bell className="h-4 w-4 mr-2" />
                {t('profile.notifications')}
              </Link>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                <LogOut className="h-4 w-4 mr-2" />
                {t('profile.signOut')}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Credits & Feature Costs */}
      <Card data-tour="profile-credits">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center">
              <Coins className="h-5 w-5 mr-2 text-amber-600" />
              {t('profile.creditsFeatures')}
            </CardTitle>
            <div className="flex items-center gap-2 px-4 py-2 bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-800 rounded-xl">
              <Coins className="w-5 h-5 text-amber-600" />
              <span className="text-lg font-bold text-amber-700 dark:text-amber-300">
                {creditBalance ?? 0}
              </span>
              <span className="text-sm text-amber-500 dark:text-amber-400">credits</span>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {featureList.map((feature) => (
              <div key={feature.nameKey} className="flex items-center justify-between p-3 bg-gray-100 dark:bg-gray-700 dark:bg-gray-800 rounded-lg">
                <div className="flex items-center gap-2">
                  <feature.icon className={`w-4 h-4 ${feature.color}`} />
                  <span className="text-sm font-medium text-gray-900 dark:text-white dark:text-white">{t(feature.nameKey)}</span>
                </div>
                <Badge variant="info">{feature.cost} {t('profile.cr')}</Badge>
              </div>
            ))}
          </div>
          <div className="mt-4 flex items-center justify-between pt-4 border-t border-gray-100 dark:border-gray-700 dark:border-gray-700">
            <p className="text-sm text-gray-600 dark:text-gray-400 dark:text-gray-400">{t('profile.aiCoachFree')}</p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => router.push('/upgrade')}
              className="text-amber-700 border-amber-200 bg-amber-50 hover:bg-amber-100"
            >
              <Coins className="h-4 w-4 mr-2" />
              {t('profile.buyCredits')}
            </Button>
          </div>
        </CardContent>
      </Card>

      {isPremium && (
        <Card variant="elevated" className="bg-gradient-to-r from-premium/10 to-secondary/10">
          <CardContent className="p-8 text-center">
            <Crown className="h-12 w-12 text-premium mx-auto mb-4" />
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white dark:text-white mb-2">{t('profile.premiumMember')}</h3>
            <p className="text-gray-600 dark:text-gray-400 dark:text-gray-400">{t('profile.unlimitedAccess')}</p>
          </CardContent>
        </Card>
      )}

      {/* Feature Tour */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-lg">
                <Play className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white dark:text-white">{t('profile.featureTour')}</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 dark:text-gray-400">{t('profile.featureTourDesc')}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  resetAllTours();
                  window.dispatchEvent(new Event(TOUR_START_EVENT));
                }}
              >
                <Play className="h-4 w-4 mr-1" />
                {t('profile.startTour')}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Profile Settings Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center">
              <Settings className="h-5 w-5 mr-2" />
              {t('profile.profileInfo')}
            </CardTitle>
            {!isEditing && (
              <Button variant="outline" size="sm" onClick={() => setIsEditing(true)}>
                {t('profile.editProfile')}
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {isEditing ? (
            <form onSubmit={handleUpdateProfile} className="space-y-4">
              <Input
                name="full_name"
                label={t('auth.fullName')}
                defaultValue={user?.full_name || ''}
                placeholder="John Doe"
              />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  name="height_cm"
                  label={`${t('auth.height')} (${t('profile.cm')})`}
                  type="number"
                  defaultValue={user?.height_cm || ''}
                  placeholder="170"
                />
                <Input
                  name="weight_kg"
                  label={`${t('auth.weight')} (${t('profile.kg')})`}
                  type="number"
                  step="0.1"
                  defaultValue={user?.weight_kg || ''}
                  placeholder="70"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  name="age"
                  label={t('auth.age')}
                  type="number"
                  defaultValue={user?.age || ''}
                  placeholder="30"
                />
                <Select name="gender" label={t('auth.gender')} defaultValue={user?.gender || ''}>
                  <option value="">{t('auth.select')}</option>
                  <option value="male">{t('auth.male')}</option>
                  <option value="female">{t('auth.female')}</option>
                </Select>
              </div>

              <Select name="ethnicity" label={t('auth.ethnicity')} defaultValue={user?.ethnicity || ''}>
                <option value="">{t('auth.select')}</option>
                <option value="Asian">{t('auth.ethnicity_options.asian')}</option>
                <option value="Caucasian">{t('auth.ethnicity_options.caucasian')}</option>
                <option value="African">{t('auth.ethnicity_options.african')}</option>
                <option value="Hispanic">{t('auth.ethnicity_options.hispanic')}</option>
                <option value="Middle Eastern">{t('auth.ethnicity_options.middleEastern')}</option>
                <option value="Pacific Islander">{t('auth.ethnicity_options.pacificIslander')}</option>
                <option value="Mixed">{t('auth.ethnicity_options.mixed')}</option>
                <option value="Other">{t('auth.ethnicity_options.other')}</option>
              </Select>

              <Select
                name="activity_level"
                label={t('auth.activityLevel')}
                defaultValue={user?.activity_level || 'sedentary'}
              >
                <option value="sedentary">{t('auth.activityLevel_sedentary')}</option>
                <option value="light">{t('auth.activityLevel_light')}</option>
                <option value="moderate">{t('auth.activityLevel_moderate')}</option>
                <option value="active">{t('auth.activityLevel_heavy')}</option>
                <option value="very_active">{t('auth.activityLevel_athlete')}</option>
              </Select>

              <Input
                name="calorie_goal"
                label={t('profile.dailyCalorieGoal')}
                type="number"
                defaultValue={user?.calorie_goal || 2000}
                placeholder="2000"
              />

              {error && (
                <div className="p-3 bg-error/10 border border-error rounded-lg">
                  <p className="text-sm text-error">{error}</p>
                </div>
              )}

              <div className="flex gap-3">
                <Button type="submit" variant="primary" isLoading={isSaving} className="flex-1">
                  {t('profile.saveChanges')}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setIsEditing(false);
                    setError(null);
                  }}
                >
                  {t('common.cancel')}
                </Button>
              </div>
            </form>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 dark:text-gray-400 mb-1">{t('auth.height')}</p>
                <p className="text-base font-medium text-gray-900 dark:text-white dark:text-white">
                  {user?.height_cm ? `${user.height_cm} ${t('profile.cm')}` : t('profile.notSet')}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 dark:text-gray-400 mb-1">{t('auth.weight')}</p>
                <p className="text-base font-medium text-gray-900 dark:text-white dark:text-white">
                  {user?.weight_kg ? `${user.weight_kg} ${t('profile.kg')}` : t('profile.notSet')}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 dark:text-gray-400 mb-1">{t('auth.age')}</p>
                <p className="text-base font-medium text-gray-900 dark:text-white dark:text-white">
                  {user?.age || t('profile.notSet')}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 dark:text-gray-400 mb-1">{t('auth.gender')}</p>
                <p className="text-base font-medium text-gray-900 dark:text-white dark:text-white capitalize">
                  {user?.gender || t('profile.notSet')}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 dark:text-gray-400 mb-1">{t('auth.ethnicity')}</p>
                <p className="text-base font-medium text-gray-900 dark:text-white dark:text-white">
                  {user?.ethnicity || t('profile.notSet')}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 dark:text-gray-400 mb-1">{t('auth.activityLevel')}</p>
                <p className="text-base font-medium text-gray-900 dark:text-white dark:text-white capitalize">
                  {user?.activity_level?.replace('_', ' ') || t('profile.notSet')}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 dark:text-gray-400 mb-1">{t('profile.dailyCalorieGoal')}</p>
                <p className="text-base font-medium text-gray-900 dark:text-white dark:text-white">
                  {user?.calorie_goal ? `${user.calorie_goal} ${t('profile.kcal')}` : t('profile.notSet')}
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="border-red-200 dark:border-red-900/40">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-red-700 dark:text-red-300">
            <AlertTriangle className="h-5 w-5" />
            Delete Account
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-gray-700 dark:text-gray-300">
            This permanently deletes your Devenira account and app data. It also removes stored progress photo files from Devenira storage.
          </p>

          <div>
            <p className="text-sm font-semibold text-gray-900 dark:text-white mb-2">Deleted immediately</p>
            <ul className="list-disc pl-5 space-y-1 text-sm text-gray-600 dark:text-gray-400">
              {ACCOUNT_DELETION_DELETED_IMMEDIATELY.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>

          <div>
            <p className="text-sm font-semibold text-gray-900 dark:text-white mb-2">Not deleted from third parties</p>
            <ul className="list-disc pl-5 space-y-1 text-sm text-gray-600 dark:text-gray-400">
              {ACCOUNT_DELETION_RETAINED_OUTSIDE_APP.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>

          {hasActiveBilling && (
            <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800 dark:border-amber-900/40 dark:bg-amber-950/30 dark:text-amber-300">
              <div className="space-y-3">
                <p>{deletionBlockMessage}</p>
                {subscriptionStatus?.billing_portal_available && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleManageBilling}
                    disabled={isOpeningBillingPortal}
                    className="border-amber-300 bg-white/80 text-amber-900 hover:bg-white"
                  >
                    {isOpeningBillingPortal ? 'Opening billing...' : 'Manage billing'}
                  </Button>
                )}
              </div>
            </div>
          )}

          <Button
            variant="danger"
            onClick={() => {
              setDeleteError(null);
              setDeleteConfirmText('');
              setShowDeleteModal(true);
            }}
            className="w-full md:w-auto"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Delete Account
          </Button>
        </CardContent>
      </Card>

      <Modal
        isOpen={showDeleteModal}
        onClose={() => {
          if (isDeletingAccount) return;
          setShowDeleteModal(false);
          setDeleteError(null);
          setDeleteConfirmText('');
        }}
        title="Delete Account"
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-700 dark:text-gray-300">
            This deletes your Devenira account immediately. If you still have active billing, cancel it first because this flow does not cancel Stripe or app-store subscriptions.
          </p>

          {hasActiveBilling && subscriptionStatus?.billing_portal_available && (
            <Button
              variant="outline"
              onClick={handleManageBilling}
              disabled={isOpeningBillingPortal}
              className="w-full"
            >
              {isOpeningBillingPortal ? 'Opening billing...' : 'Manage billing first'}
            </Button>
          )}

          <div className="rounded-lg border border-gray-200 dark:border-gray-700 p-3">
            <p className="text-sm font-medium text-gray-900 dark:text-white mb-2">Type {ACCOUNT_DELETION_CONFIRM_PHRASE} to confirm</p>
            <Input
              value={deleteConfirmText}
              onChange={(e) => setDeleteConfirmText(e.target.value)}
              placeholder={ACCOUNT_DELETION_CONFIRM_PHRASE}
            />
          </div>

          {deleteError && (
            <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900/40 dark:bg-red-950/30 dark:text-red-300">
              {deleteError}
            </div>
          )}

          <div className="flex gap-3 justify-end">
            <Button
              variant="outline"
              onClick={() => {
                setShowDeleteModal(false);
                setDeleteError(null);
                setDeleteConfirmText('');
              }}
              disabled={isDeletingAccount}
            >
              {t('common.cancel')}
            </Button>
            <Button variant="danger" onClick={handleDeleteAccount} disabled={isDeletingAccount}>
              {isDeletingAccount ? 'Deleting...' : 'Delete account'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
