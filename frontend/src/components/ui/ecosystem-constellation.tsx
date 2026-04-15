'use client';

import type { ComponentType } from 'react';
import {
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { Activity, Apple, Camera, ImageIcon, ScanFace, Target } from 'lucide-react';

export interface EcosystemConstellationProps {
  satelliteCount?: number;
  centerLabel?: string;
  accentColor?: string;
  speed?: number;
  className?: string;
}

const FONT_FAMILY =
  'var(--font-geist-sans), -apple-system, BlinkMacSystemFont, sans-serif';

interface SatelliteNode {
  Icon: ComponentType<{ className?: string }>;
  bg: string;
}

const SATELLITE_NODES: SatelliteNode[] = [
  { Icon: Target, bg: '#121826' },
  { Icon: ScanFace, bg: '#1d4ed8' },
  { Icon: ImageIcon, bg: '#4338ca' },
  { Icon: Activity, bg: '#0f766e' },
  { Icon: Apple, bg: '#14532d' },
  { Icon: Camera, bg: '#7c3aed' },
];

export function EcosystemConstellation({
  satelliteCount = 6,
  centerLabel = 'D',
  accentColor = '#8b5cf6',
  speed = 1,
  className,
}: EcosystemConstellationProps) {
  const frame = useCurrentFrame() * speed;
  const { fps } = useVideoConfig();

  const count = Math.max(3, Math.min(SATELLITE_NODES.length, Math.floor(satelliteCount)));
  const pulse = (Math.sin(frame / 12) + 1) / 2;
  const centerScale = 1 + pulse * 0.06;

  const cx = 640;
  const cy = 360;
  const baseRadiusX = 250;
  const baseRadiusY = 190;
  const offscreenRadius = 1200;

  const satellites = Array.from({ length: count }).map((_, i) => {
    const stagger = i * 4;
    const sp = spring({
      frame: frame - stagger,
      fps,
      config: { mass: 1.1, damping: 16, stiffness: 70 },
      durationInFrames: 50,
    });
    const radiusFactor = interpolate(sp, [0, 1], [offscreenRadius, 1]);

    const orbitOffset = i * 18;
    const rX = baseRadiusX + orbitOffset;
    const rY = baseRadiusY + orbitOffset * 0.7;
    const angularSpeed = 0.012 - i * 0.0008;
    const baseAngle = (i / count) * Math.PI * 2;
    const angle = baseAngle + frame * angularSpeed;

    const x = cx + Math.cos(angle) * rX * radiusFactor;
    const y = cy + Math.sin(angle) * rY * radiusFactor;

    const activeIdx = Math.floor(frame / 30) % count;
    const isActive = activeIdx === i;
    const localFrame = frame - Math.floor(frame / 30) * 30;
    const lineOpacity = isActive
      ? interpolate(localFrame, [0, 8, 22, 30], [0.2, 0.92, 0.92, 0.2], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        })
      : 0.16;
    const satScale = isActive
      ? interpolate(localFrame, [0, 8, 22, 30], [1, 1.14, 1.14, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        })
      : 1;

    const node = SATELLITE_NODES[i % SATELLITE_NODES.length];
    return {
      x,
      y,
      Icon: node.Icon,
      color: node.bg,
      lineOpacity,
      satScale,
      visible: sp > 0.02,
    };
  });

  return (
    <div
      className={className}
      style={{
        position: 'absolute',
        inset: 0,
        overflow: 'hidden',
        background:
          'radial-gradient(circle at 50% 45%, rgba(113,74,255,0.16) 0%, rgba(11,8,21,0.92) 40%, #05030a 100%)',
        fontFamily: FONT_FAMILY,
      }}
    >
      <svg
        width="100%"
        height="100%"
        viewBox="0 0 1280 720"
        style={{ position: 'absolute', inset: 0 }}
      >
        {satellites.map((s, i) => (
          <line
            key={`line-${i}`}
            x1={cx}
            y1={cy}
            x2={s.x}
            y2={s.y}
            stroke={accentColor}
            strokeWidth={2}
            strokeLinecap="round"
            opacity={s.visible ? s.lineOpacity : 0}
          />
        ))}

        <circle cx={cx} cy={cy} r={84 + pulse * 10} fill={accentColor} opacity={0.1} />
        <circle cx={cx} cy={cy} r={56 + pulse * 5} fill={accentColor} opacity={0.18} />
      </svg>

      <div
        style={{
          position: 'absolute',
          left: cx,
          top: cy,
          width: 108,
          height: 108,
          marginLeft: -54,
          marginTop: -54,
          borderRadius: 28,
          background: `linear-gradient(180deg, ${accentColor} 0%, ${accentColor}cc 100%)`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontWeight: 800,
          fontSize: 56,
          letterSpacing: '-0.05em',
          transform: `scale(${centerScale})`,
          boxShadow: `0 0 80px ${accentColor}55, inset 0 1px 0 rgba(255,255,255,0.25)`,
          border: '1px solid rgba(255,255,255,0.18)',
        }}
      >
        {centerLabel}
      </div>

      {satellites.map((s, i) => {
        const Icon = s.Icon;
        return (
          <div
            key={`sat-${i}`}
            style={{
              position: 'absolute',
              left: s.x,
              top: s.y,
              width: 60,
              height: 60,
              marginLeft: -30,
              marginTop: -30,
              borderRadius: 18,
              background: `linear-gradient(180deg, ${s.color} 0%, ${s.color}dd 100%)`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transform: `scale(${s.satScale})`,
              boxShadow: `0 10px 32px ${s.color}55, inset 0 1px 0 rgba(255,255,255,0.16)`,
              border: '1px solid rgba(255,255,255,0.12)',
              opacity: s.visible ? 1 : 0,
              willChange: 'transform',
            }}
          >
            <Icon className="h-7 w-7 text-white" />
          </div>
        );
      })}
    </div>
  );
}
