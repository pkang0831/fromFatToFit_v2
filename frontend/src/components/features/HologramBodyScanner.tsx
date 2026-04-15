'use client';

import { Suspense, useCallback, useMemo, useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Line, PerspectiveCamera } from '@react-three/drei';
import * as THREE from 'three';

import { cn } from '@/lib/utils/cn';
import { HumanBodyModel } from '@/components/features/HumanBodyModel';
import type { RegionStatus, RegionVisualization } from '@/types/api';

type ScannerRegion = 'abdomen' | 'chest' | 'arms' | 'whole';

interface RegionCardLayout {
  x: number;
  y: number;
  anchorX: number;
  anchorY: number;
  align: 'left' | 'right';
}

const REGION_LAYOUT: Record<Exclude<ScannerRegion, 'whole'>, RegionCardLayout> = {
  chest: { x: 5, y: 14, anchorX: 49, anchorY: 31, align: 'left' },
  abdomen: { x: 6, y: 69, anchorX: 50, anchorY: 58, align: 'left' },
  arms: { x: 96, y: 56, anchorX: 68, anchorY: 53, align: 'right' },
};

const REGION_ORDER: Exclude<ScannerRegion, 'whole'>[] = ['chest', 'abdomen', 'arms'];

export interface HologramBodyScannerProps {
  size?: number;
  autoRotateSpeed?: number;
  glowIntensity?: number;
  bodyClarity?: number;
  pedestalProgress?: number;
  scanlineSpeed?: number;
  className?: string;
  regionalCards?: RegionVisualization[];
}

function statusColor(status: RegionStatus) {
  if (status === 'improved') return 'rgba(152, 255, 226, 0.95)';
  if (status === 'regressed') return 'rgba(255, 193, 152, 0.92)';
  return 'rgba(255,255,255,0.82)';
}

function RearScanArc() {
  const lineRef = useRef<THREE.Group>(null);

  useFrame((_, delta) => {
    if (!lineRef.current) return;
    lineRef.current.rotation.z += delta * 0.03;
  });

  const arcPoints = useMemo(
    () =>
      Array.from({ length: 96 }, (_, index) => {
        const angle = THREE.MathUtils.degToRad(30 + (index / 95) * 250);
        return [Math.cos(angle) * 1.9, Math.sin(angle) * 2.08, 0] as [number, number, number];
      }),
    [],
  );

  return (
    <group ref={lineRef} position={[0, 0.06, -0.96]}>
      <Line points={arcPoints} color="#d8d0ae" transparent opacity={0.08} lineWidth={0.75} />
    </group>
  );
}

function ScannerPedestal({ progress }: { progress: number }) {
  const ringRef = useRef<THREE.Mesh>(null);
  const progressRef = useRef<THREE.Mesh>(null);

  useFrame((state, delta) => {
    if (ringRef.current) {
      ringRef.current.rotation.z += delta * 0.1;
      const material = ringRef.current.material as THREE.MeshBasicMaterial;
      material.opacity = 0.18 + Math.sin(state.clock.getElapsedTime() * 0.8) * 0.02;
    }

    if (progressRef.current) {
      progressRef.current.rotation.z -= delta * 0.08;
      const material = progressRef.current.material as THREE.MeshBasicMaterial;
      material.opacity = 0.2 + progress * 0.18;
    }
  });

  return (
    <group position={[0, -1.88, 0]}>
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[1.18, 72]} />
        <meshBasicMaterial color="#071015" transparent opacity={0.22} depthWrite={false} />
      </mesh>

      <mesh ref={ringRef} rotation={[-Math.PI / 2, 0, 0]}>
        <torusGeometry args={[1.18, 0.024, 16, 96]} />
        <meshBasicMaterial color="#8fe7ff" transparent opacity={0.14} depthWrite={false} />
      </mesh>

      <mesh ref={progressRef} rotation={[-Math.PI / 2, 0, 0.12]}>
        <ringGeometry args={[1.1, 1.18, 96, 1, 0, Math.PI * 2 * Math.max(progress, 0.06)]} />
        <meshBasicMaterial color="#d7ffc5" transparent opacity={0.26} side={THREE.DoubleSide} depthWrite={false} />
      </mesh>
    </group>
  );
}

function ScannerScene({
  size,
  autoRotateSpeed,
  glowIntensity,
  bodyClarity,
  pedestalProgress,
  scanlineSpeed,
  hovered,
  highlightedRegion,
  regionStates,
  targetRotation,
  velocity,
  dragging,
}: {
  size: number;
  autoRotateSpeed: number;
  glowIntensity: number;
  bodyClarity: number;
  pedestalProgress: number;
  scanlineSpeed: number;
  hovered: boolean;
  highlightedRegion: 'none' | ScannerRegion;
  regionStates: Record<'abdomen' | 'chest' | 'arms', RegionVisualization | undefined>;
  targetRotation: React.MutableRefObject<number>;
  velocity: React.MutableRefObject<number>;
  dragging: React.MutableRefObject<boolean>;
}) {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((_, delta) => {
    if (!groupRef.current) return;

    if (!dragging.current) {
      if (Math.abs(velocity.current) > 0.00008) {
        targetRotation.current += velocity.current * delta * 60;
        velocity.current *= Math.pow(0.925, delta * 60);
      } else {
        targetRotation.current += autoRotateSpeed * delta;
        velocity.current = 0;
      }
    }

    groupRef.current.rotation.y = THREE.MathUtils.damp(groupRef.current.rotation.y, targetRotation.current, 6.5, delta);
  });

  return (
    <>
      <PerspectiveCamera makeDefault position={[0, 0.32, 8.5]} fov={27} />
      <group ref={groupRef} scale={size}>
        <RearScanArc />
        <ScannerPedestal progress={pedestalProgress} />
        <group position={[0, -1.88, 0]}>
          <Suspense fallback={null}>
            <HumanBodyModel
              hovered={hovered}
              glowIntensity={glowIntensity}
              bodyClarity={bodyClarity}
              scanlineSpeed={scanlineSpeed}
              highlightedRegion={highlightedRegion}
              regionalMetrics={{
                abdomen: regionStates.abdomen,
                chest: regionStates.chest,
                arms: regionStates.arms,
              }}
            />
          </Suspense>
        </group>
      </group>
    </>
  );
}

export function HologramBodyScanner({
  size = 0.92,
  autoRotateSpeed = 0.07,
  glowIntensity = 0.82,
  bodyClarity = 0.74,
  pedestalProgress = 0.52,
  scanlineSpeed = 1,
  className,
  regionalCards = [],
}: HologramBodyScannerProps) {
  const targetRotation = useRef(0.22);
  const velocity = useRef(0);
  const dragging = useRef(false);
  const lastPointerX = useRef<number | null>(null);

  const [hovered, setHovered] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [hoveredRegion, setHoveredRegion] = useState<ScannerRegion | 'none'>('none');

  const visibleCards = useMemo(
    () =>
      REGION_ORDER.map((region) => regionalCards.find((card) => card.region === region))
        .filter(Boolean)
        .slice(0, 3) as RegionVisualization[],
    [regionalCards],
  );

  const regionStates = useMemo(
    () => ({
      abdomen: visibleCards.find((card) => card.region === 'abdomen'),
      chest: visibleCards.find((card) => card.region === 'chest'),
      arms: visibleCards.find((card) => card.region === 'arms'),
    }),
    [visibleCards],
  );

  const handlePointerDown = useCallback((event: React.PointerEvent<HTMLDivElement>) => {
    dragging.current = true;
    setIsDragging(true);
    lastPointerX.current = event.clientX;
    event.currentTarget.setPointerCapture(event.pointerId);
  }, []);

  const handlePointerMove = useCallback((event: React.PointerEvent<HTMLDivElement>) => {
    if (!dragging.current || lastPointerX.current == null) return;
    const deltaX = event.clientX - lastPointerX.current;
    lastPointerX.current = event.clientX;

    targetRotation.current += deltaX * 0.0086;
    velocity.current = deltaX * 0.00135;
  }, []);

  const handlePointerEnd = useCallback((event: React.PointerEvent<HTMLDivElement>) => {
    dragging.current = false;
    setIsDragging(false);
    lastPointerX.current = null;
    try {
      event.currentTarget.releasePointerCapture(event.pointerId);
    } catch {
      /* noop */
    }
  }, []);

  return (
    <div
      className={cn(
        'relative isolate h-full min-h-[560px] overflow-hidden rounded-[34px] bg-[#0b0a08] touch-none select-none ring-1 ring-white/[0.04] shadow-[inset_0_1px_0_rgba(255,255,255,0.03)]',
        className,
      )}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerEnd}
      onPointerCancel={handlePointerEnd}
      onPointerEnter={() => setHovered(true)}
      onPointerLeave={() => {
        setHovered(false);
        dragging.current = false;
        setIsDragging(false);
        lastPointerX.current = null;
        setHoveredRegion('none');
      }}
      style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
      aria-label="Interactive hologram body scanner"
    >
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(720px_520px_at_54%_46%,rgba(205,190,150,0.08),transparent_46%),linear-gradient(180deg,rgba(255,255,255,0.02),transparent_18%,transparent_55%)]" />

      <div className="absolute inset-0">
        <Canvas
          dpr={[1, 1.75]}
          gl={{ alpha: true, antialias: true, powerPreference: 'high-performance' }}
          onCreated={({ gl }) => {
            gl.setClearColor(0x000000, 0);
          }}
        >
          <ScannerScene
            size={size}
            autoRotateSpeed={autoRotateSpeed}
            glowIntensity={glowIntensity}
            bodyClarity={bodyClarity}
            pedestalProgress={pedestalProgress}
            scanlineSpeed={scanlineSpeed}
            hovered={hovered}
            highlightedRegion={hoveredRegion}
            regionStates={regionStates}
            targetRotation={targetRotation}
            velocity={velocity}
            dragging={dragging}
          />
        </Canvas>
      </div>

      {visibleCards.length > 0 ? (
        <>
          <svg
            className="pointer-events-none absolute inset-0 h-full w-full"
            viewBox="0 0 100 100"
            preserveAspectRatio="none"
            aria-hidden="true"
          >
            {visibleCards.map((card) => {
              const layout = REGION_LAYOUT[card.region as Exclude<ScannerRegion, 'whole'>];
              const active = hoveredRegion === card.region;
              const cardAnchorX = layout.align === 'right' ? layout.x - 9 : layout.x + 9;
              const cardAnchorY = layout.y + 7.5;
              const color = statusColor(card.status);

              return (
                <g key={card.region}>
                  <line
                    x1={layout.anchorX}
                    y1={layout.anchorY}
                    x2={cardAnchorX}
                    y2={cardAnchorY}
                    stroke={active ? color : 'rgba(255,255,255,0.16)'}
                    strokeWidth={active ? 0.24 : 0.16}
                    strokeLinecap="round"
                  />
                  <circle
                    cx={layout.anchorX}
                    cy={layout.anchorY}
                    r={active ? 0.72 : 0.5}
                    fill={active ? color : 'rgba(255,255,255,0.44)'}
                  />
                </g>
              );
            })}
          </svg>

          <div className="absolute inset-0">
            {visibleCards.map((card) => {
              const layout = REGION_LAYOUT[card.region as Exclude<ScannerRegion, 'whole'>];
              const active = hoveredRegion === card.region;

              return (
                <div
                  key={card.region}
                  className="absolute"
                  style={{
                    left: `${layout.x}%`,
                    top: `${layout.y}%`,
                    transform: layout.align === 'right' ? 'translate(-100%, 0)' : 'translate(0, 0)',
                  }}
                >
                  <div
                    role="group"
                    tabIndex={0}
                    aria-label={`${card.label}: ${card.value}`}
                    onPointerDown={(event) => event.stopPropagation()}
                    onPointerEnter={() => setHoveredRegion(card.region)}
                    onPointerLeave={() => setHoveredRegion((current) => (current === card.region ? 'none' : current))}
                    onFocus={() => setHoveredRegion(card.region)}
                    onBlur={() => setHoveredRegion((current) => (current === card.region ? 'none' : current))}
                    className={cn(
                      'w-[156px] rounded-[18px] bg-[#0f0e0c]/82 px-4 py-3 text-left backdrop-blur-[6px] transition-all duration-200',
                      'ring-1 ring-white/[0.06] shadow-[0_16px_34px_rgba(0,0,0,0.16)]',
                      active && 'bg-[#14120f]/94 ring-white/[0.12] shadow-[0_18px_40px_rgba(0,0,0,0.22)]',
                    )}
                  >
                    <p className="text-[11px] font-medium uppercase tracking-[0.08em] text-white/44">
                      {card.label}
                    </p>
                    <p className="mt-1 text-[1.05rem] font-semibold tracking-[-0.03em] text-white">
                      {card.value}
                    </p>
                    <p className="mt-1 text-[12px] leading-5 text-white/54">{card.note}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </>
      ) : null}

      <div className="pointer-events-none absolute right-6 top-5 text-[11px] font-medium uppercase tracking-[0.08em] text-white/40">
        Drag to rotate
      </div>
    </div>
  );
}
