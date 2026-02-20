'use client';

import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import { User as UserIcon, Crown, LogOut, Settings } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, Button, Input, Select, Badge } from '@/components/ui';
import { useAuth } from '@/contexts/AuthContext';
import { useSubscription } from '@/lib/hooks/useSubscription';
import { formatDateLong } from '@/lib/utils/date';

export default function ProfilePage() {
  const router = useRouter();
  const { user, logout, updateProfile } = useAuth();
  const { isPremium, usageLimits } = useSubscription();
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogout = async () => {
    if (confirm('Are you sure you want to log out?')) {
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
    } catch (err: any) {
      setError(err.message || 'Failed to update profile');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold text-text">Profile & Settings</h1>
        <p className="text-text-secondary mt-1">
          Manage your account and preferences
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
                <CardTitle>{user?.full_name || 'User'}</CardTitle>
                <p className="text-sm text-text-secondary">{user?.email}</p>
              </div>
            </div>
            {isPremium && (
              <Badge variant="premium" className="text-base px-4 py-2">
                <Crown className="h-4 w-4 mr-2" />
                Premium Member
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between pt-4 border-t border-border-light">
            <p className="text-sm text-text-secondary">
              Member since {user?.created_at ? formatDateLong(user.created_at) : 'N/A'}
            </p>
            <Button variant="outline" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4 mr-2" />
              Sign Out
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Usage Limits Card (for free users) */}
      {!isPremium && usageLimits && (
        <Card>
          <CardHeader>
            <CardTitle>Usage Limits</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-surfaceAlt rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium text-text">Food Photo Scans</p>
                  <Badge variant={usageLimits.limits.food_scan.remaining > 0 ? 'info' : 'error'}>
                    {usageLimits.limits.food_scan.remaining} / {usageLimits.limits.food_scan.limit}
                  </Badge>
                </div>
                <div className="h-2 bg-border-light rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary transition-all duration-300"
                    style={{
                      width: `${(usageLimits.limits.food_scan.current_count / usageLimits.limits.food_scan.limit) * 100}%`
                    }}
                  />
                </div>
              </div>

              <div className="p-4 bg-surfaceAlt rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium text-text">Body Fat Scans</p>
                  <Badge variant={usageLimits.limits.body_fat_scan.remaining > 0 ? 'info' : 'error'}>
                    {usageLimits.limits.body_fat_scan.remaining} / {usageLimits.limits.body_fat_scan.limit}
                  </Badge>
                </div>
                <div className="h-2 bg-border-light rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary transition-all duration-300"
                    style={{
                      width: `${(usageLimits.limits.body_fat_scan.current_count / usageLimits.limits.body_fat_scan.limit) * 100}%`
                    }}
                  />
                </div>
              </div>

              <div className="p-4 bg-surfaceAlt rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium text-text">Percentile Scans</p>
                  <Badge variant={usageLimits.limits.percentile_scan.remaining > 0 ? 'info' : 'error'}>
                    {usageLimits.limits.percentile_scan.remaining} / {usageLimits.limits.percentile_scan.limit}
                  </Badge>
                </div>
                <div className="h-2 bg-border-light rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary transition-all duration-300"
                    style={{
                      width: `${(usageLimits.limits.percentile_scan.current_count / usageLimits.limits.percentile_scan.limit) * 100}%`
                    }}
                  />
                </div>
              </div>

              <div className="p-4 bg-surfaceAlt rounded-lg flex items-center justify-center">
                <Button
                  variant="primary"
                  onClick={() => router.push('/upgrade')}
                  className="bg-premium text-primary hover:bg-premium-dark"
                >
                  <Crown className="h-4 w-4 mr-2" />
                  Get Unlimited
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {isPremium && (
        <Card variant="elevated" className="bg-gradient-to-r from-premium/10 to-secondary/10">
          <CardContent className="p-8 text-center">
            <Crown className="h-12 w-12 text-premium mx-auto mb-4" />
            <h3 className="text-2xl font-bold text-text mb-2">Premium Member</h3>
            <p className="text-text-secondary">You have unlimited access to all features!</p>
          </CardContent>
        </Card>
      )}

      {/* Profile Settings Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center">
              <Settings className="h-5 w-5 mr-2" />
              Profile Information
            </CardTitle>
            {!isEditing && (
              <Button variant="outline" size="sm" onClick={() => setIsEditing(true)}>
                Edit Profile
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {isEditing ? (
            <form onSubmit={handleUpdateProfile} className="space-y-4">
              <Input
                name="full_name"
                label="Full Name"
                defaultValue={user?.full_name || ''}
                placeholder="John Doe"
              />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  name="height_cm"
                  label="Height (cm)"
                  type="number"
                  defaultValue={user?.height_cm || ''}
                  placeholder="170"
                />
                <Input
                  name="weight_kg"
                  label="Weight (kg)"
                  type="number"
                  step="0.1"
                  defaultValue={user?.weight_kg || ''}
                  placeholder="70"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  name="age"
                  label="Age"
                  type="number"
                  defaultValue={user?.age || ''}
                  placeholder="30"
                />
                <Select name="gender" label="Gender" defaultValue={user?.gender || ''}>
                  <option value="">Select...</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                </Select>
              </div>

              <Select name="ethnicity" label="Ethnicity" defaultValue={user?.ethnicity || ''}>
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

              <Select
                name="activity_level"
                label="Activity Level"
                defaultValue={user?.activity_level || 'sedentary'}
              >
                <option value="sedentary">Sedentary (Little to no exercise)</option>
                <option value="light">Light Exercise (1-3 days/week)</option>
                <option value="moderate">Moderate Exercise (3-5 days/week)</option>
                <option value="heavy">Heavy Exercise (6-7 days/week)</option>
                <option value="athlete">Athlete (Very heavy exercise, physical job)</option>
              </Select>

              <Input
                name="calorie_goal"
                label="Daily Calorie Goal"
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
                  Save Changes
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setIsEditing(false);
                    setError(null);
                  }}
                >
                  Cancel
                </Button>
              </div>
            </form>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <p className="text-sm text-text-secondary mb-1">Height</p>
                <p className="text-base font-medium text-text">
                  {user?.height_cm ? `${user.height_cm} cm` : 'Not set'}
                </p>
              </div>
              <div>
                <p className="text-sm text-text-secondary mb-1">Weight</p>
                <p className="text-base font-medium text-text">
                  {user?.weight_kg ? `${user.weight_kg} kg` : 'Not set'}
                </p>
              </div>
              <div>
                <p className="text-sm text-text-secondary mb-1">Age</p>
                <p className="text-base font-medium text-text">
                  {user?.age || 'Not set'}
                </p>
              </div>
              <div>
                <p className="text-sm text-text-secondary mb-1">Gender</p>
                <p className="text-base font-medium text-text capitalize">
                  {user?.gender || 'Not set'}
                </p>
              </div>
              <div>
                <p className="text-sm text-text-secondary mb-1">Ethnicity</p>
                <p className="text-base font-medium text-text">
                  {user?.ethnicity || 'Not set'}
                </p>
              </div>
              <div>
                <p className="text-sm text-text-secondary mb-1">Activity Level</p>
                <p className="text-base font-medium text-text capitalize">
                  {user?.activity_level?.replace('_', ' ') || 'Not set'}
                </p>
              </div>
              <div>
                <p className="text-sm text-text-secondary mb-1">Daily Calorie Goal</p>
                <p className="text-base font-medium text-text">
                  {user?.calorie_goal ? `${user.calorie_goal} kcal` : 'Not set'}
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
