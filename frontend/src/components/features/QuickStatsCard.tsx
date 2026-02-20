import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { LucideIcon } from 'lucide-react';

interface QuickStatsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  progress?: {
    current: number;
    max: number;
  };
}

export function QuickStatsCard({ title, value, subtitle, icon: Icon, progress }: QuickStatsCardProps) {
  return (
    <Card variant="elevated" className="hover:shadow-xl transition-shadow">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-text-secondary mb-1">{title}</p>
            <p className="text-3xl font-bold text-text">{value}</p>
            {subtitle && <p className="text-sm text-text-light mt-1">{subtitle}</p>}
          </div>
          <div className="p-3 bg-primary/10 rounded-lg">
            <Icon className="h-6 w-6 text-primary" />
          </div>
        </div>
        {progress && (
          <div className="mt-4">
            <ProgressBar value={progress.current} max={progress.max} size="sm" />
          </div>
        )}
      </CardContent>
    </Card>
  );
}
