'use client';

import { useMemo } from 'react';
import { Player } from '@remotion/player';

import { cn } from '@/lib/utils';
import { EcosystemConstellation } from '@/components/ui/ecosystem-constellation';

interface EcosystemConstellationDemoProps {
  className?: string;
}

export function EcosystemConstellationDemo({
  className,
}: EcosystemConstellationDemoProps) {
  const props = useMemo(
    () => ({
      speed: 1,
      centerLabel: 'D',
      accentColor: '#8b5cf6',
    }),
    []
  );

  return (
    <div className={cn('w-full', className)}>
      <Player
        component={EcosystemConstellation as never}
        inputProps={props}
        durationInFrames={240}
        fps={30}
        compositionWidth={1280}
        compositionHeight={720}
        acknowledgeRemotionLicense
        autoPlay
        loop
        controls={false}
        clickToPlay={false}
        style={{
          width: '100%',
          height: 'auto',
          aspectRatio: '16 / 9',
          borderRadius: 28,
          overflow: 'hidden',
          background: '#050505',
          boxShadow: '0 36px 120px rgba(0,0,0,0.42)',
        }}
      />
    </div>
  );
}
