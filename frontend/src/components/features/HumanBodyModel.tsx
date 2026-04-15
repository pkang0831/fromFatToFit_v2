'use client';

import { useEffect, useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { useGLTF } from '@react-three/drei';
import * as THREE from 'three';

import type { RegionVisualization } from '@/types/api';

export interface HumanBodyModelProps {
  hovered?: boolean;
  glowIntensity?: number;
  bodyClarity?: number;
  scanlineSpeed?: number;
  highlightedRegion?: 'none' | 'abdomen' | 'chest' | 'arms' | 'whole';
  regionalMetrics?: {
    abdomen?: RegionVisualization;
    chest?: RegionVisualization;
    arms?: RegionVisualization;
  };
}

type HologramMaterial = THREE.ShaderMaterial & {
  uniforms: {
    uTime: { value: number };
    uGlowIntensity: { value: number };
    uBodyClarity: { value: number };
    uScanlineSpeed: { value: number };
    uHover: { value: number };
    uMinY: { value: number };
    uMaxY: { value: number };
    uMinX: { value: number };
    uMaxX: { value: number };
    uHighlightRegion: { value: number };
    uHighlightStrength: { value: number };
    uAbdomenIntensity: { value: number };
    uChestIntensity: { value: number };
    uArmsIntensity: { value: number };
    uAbdomenState: { value: number };
    uChestState: { value: number };
    uArmsState: { value: number };
  };
};

const HUMAN_MODEL_URL = '/api/assets/human-body-model';
const TARGET_HEIGHT = 3.45;

const hologramVertexShader = `
  varying vec3 vNormalWorld;
  varying vec3 vViewDirection;
  varying vec3 vLocalPosition;
  varying vec3 vWorldPosition;

  void main() {
    vec4 worldPosition = modelMatrix * vec4(position, 1.0);
    vec4 viewPosition = viewMatrix * worldPosition;

    vLocalPosition = position;
    vWorldPosition = worldPosition.xyz;
    vNormalWorld = normalize(mat3(modelMatrix) * normal);
    vViewDirection = normalize(cameraPosition - worldPosition.xyz);

    gl_Position = projectionMatrix * viewPosition;
  }
`;

const hologramFragmentShader = `
  uniform float uTime;
  uniform float uGlowIntensity;
  uniform float uBodyClarity;
  uniform float uScanlineSpeed;
  uniform float uHover;
  uniform float uMinY;
  uniform float uMaxY;
  uniform float uMinX;
  uniform float uMaxX;
  uniform float uHighlightRegion;
  uniform float uHighlightStrength;
  uniform float uAbdomenIntensity;
  uniform float uChestIntensity;
  uniform float uArmsIntensity;
  uniform float uAbdomenState;
  uniform float uChestState;
  uniform float uArmsState;

  varying vec3 vNormalWorld;
  varying vec3 vViewDirection;
  varying vec3 vLocalPosition;
  varying vec3 vWorldPosition;

  float hash(vec3 p) {
    p = fract(p * 0.3183099 + vec3(0.1, 0.2, 0.3));
    p *= 17.0;
    return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
  }

  void main() {
    float bodyHeight = max(uMaxY - uMinY, 0.001);
    float vertical = clamp((vLocalPosition.y - uMinY) / bodyHeight, 0.0, 1.0);
    float bodyWidth = max(uMaxX - uMinX, 0.001);
    float horizontal = clamp((vLocalPosition.x - uMinX) / bodyWidth, 0.0, 1.0);
    float absHorizontal = abs(horizontal - 0.5) * 2.0;

    vec3 lower = vec3(0.16, 0.70, 1.0);
    vec3 mid = vec3(0.26, 0.78, 1.0);
    vec3 upper = vec3(0.36, 0.86, 1.0);
    vec3 abdomenImprovedTint = vec3(0.26, 1.0, 0.46);
    vec3 abdomenRegressedTint = vec3(1.0, 0.34, 0.34);
    vec3 chestImprovedTint = vec3(0.32, 0.98, 0.48);
    vec3 chestRegressedTint = vec3(1.0, 0.38, 0.38);
    vec3 armsImprovedTint = vec3(0.36, 0.96, 0.52);
    vec3 armsRegressedTint = vec3(0.98, 0.40, 0.40);

    vec3 gradient = mix(lower, mid, smoothstep(0.0, 0.62, vertical));
    gradient = mix(gradient, upper, smoothstep(0.58, 1.0, vertical));

    float fresnel = pow(1.0 - max(dot(normalize(vNormalWorld), normalize(vViewDirection)), 0.0), 2.2);

    float scan = sin((vLocalPosition.y * 18.0) - (uTime * (1.15 + uScanlineSpeed * 0.9)));
    float scanBand = smoothstep(0.62, 1.0, scan) * 0.09;

    float shimmer = hash(vec3(vWorldPosition.xy * 0.8, floor(uTime * 8.0))) * 0.035;
    float pulse = 0.5 + 0.5 * sin(uTime * 1.15 + vertical * 5.5);
    float innerGlow = (0.05 + pulse * 0.025) * (0.58 + uGlowIntensity * 0.24 + uBodyClarity * 0.14);

    float abdomenCore = 1.0 - smoothstep(0.18, 0.42, absHorizontal);
    float chestCore = 1.0 - smoothstep(0.14, 0.36, absHorizontal);
    float armsLateral = smoothstep(0.56, 0.74, absHorizontal) * (1.0 - smoothstep(0.9, 0.98, absHorizontal));

    float abdomenMask = smoothstep(0.34, 0.4, vertical) * (1.0 - smoothstep(0.5, 0.57, vertical)) * abdomenCore;
    float chestMask = smoothstep(0.58, 0.64, vertical) * (1.0 - smoothstep(0.77, 0.84, vertical)) * chestCore;
    float armsMask = smoothstep(0.42, 0.48, vertical) * (1.0 - smoothstep(0.76, 0.84, vertical)) * armsLateral;
    float wholeMask = 1.0;

    float regionMask = 0.0;
    if (uHighlightRegion < 0.5) {
      regionMask = 0.0;
    } else if (uHighlightRegion < 1.5) {
      regionMask = abdomenMask;
    } else if (uHighlightRegion < 2.5) {
      regionMask = chestMask;
    } else if (uHighlightRegion < 3.5) {
      regionMask = armsMask;
    } else {
      regionMask = wholeMask;
    }

    float regionGlow = regionMask * uHighlightStrength * 0.22;

    float abdomenGlow = abdomenMask * uAbdomenIntensity;
    float chestGlow = chestMask * uChestIntensity;
    float armsGlow = armsMask * uArmsIntensity;

    vec3 abdomenTint = mix(abdomenRegressedTint, abdomenImprovedTint, step(0.0, uAbdomenState));
    vec3 chestTint = mix(chestRegressedTint, chestImprovedTint, step(0.0, uChestState));
    vec3 armsTint = mix(armsRegressedTint, armsImprovedTint, step(0.0, uArmsState));

    float abdomenTintMix = abdomenMask * abdomenGlow * (max(abs(uAbdomenState), 0.0) * 0.72);
    float chestTintMix = chestMask * chestGlow * (max(abs(uChestState), 0.0) * 0.58);
    float armsTintMix = armsMask * armsGlow * (max(abs(uArmsState), 0.0) * 0.52);

    vec3 color = gradient * (0.46 + innerGlow + scanBand * 0.55 + shimmer * 0.65 + regionGlow);
    color = mix(color, abdomenTint, clamp(abdomenTintMix, 0.0, 0.82));
    color = mix(color, chestTint, clamp(chestTintMix, 0.0, 0.72));
    color = mix(color, armsTint, clamp(armsTintMix, 0.0, 0.68));

    vec3 regionColor = vec3(0.0);
    regionColor += abdomenTint * abdomenGlow * max(abs(uAbdomenState), 0.0) * 0.52;
    regionColor += chestTint * chestGlow * max(abs(uChestState), 0.0) * 0.36;
    regionColor += armsTint * armsGlow * max(abs(uArmsState), 0.0) * 0.32;

    color += regionColor;
    color += gradient * fresnel * (0.22 + uGlowIntensity * 0.16 + uHover * 0.08 + regionGlow * 0.4);
    color += regionColor * (0.18 + fresnel * 0.18);
    color = color / (vec3(1.0) + color * 0.28);

    float alpha = 0.16 + uBodyClarity * 0.10 + fresnel * 0.22 + scanBand * 0.26 + shimmer + uHover * 0.03 + regionGlow * 0.30;
    alpha += abdomenGlow * 0.05 + chestGlow * 0.04 + armsGlow * 0.04;
    alpha = clamp(alpha, 0.16, 0.74);

    gl_FragColor = vec4(color, alpha);
  }
`;

function createHologramMaterial(
  minY: number,
  maxY: number,
  minX: number,
  maxX: number,
  glowIntensity: number,
  bodyClarity: number,
  scanlineSpeed: number,
): HologramMaterial {
  return new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 },
      uGlowIntensity: { value: glowIntensity },
      uBodyClarity: { value: bodyClarity },
      uScanlineSpeed: { value: scanlineSpeed },
      uHover: { value: 0 },
      uMinY: { value: minY },
      uMaxY: { value: maxY },
      uMinX: { value: minX },
      uMaxX: { value: maxX },
      uHighlightRegion: { value: 0 },
      uHighlightStrength: { value: 0 },
      uAbdomenIntensity: { value: 0 },
      uChestIntensity: { value: 0 },
      uArmsIntensity: { value: 0 },
      uAbdomenState: { value: 0 },
      uChestState: { value: 0 },
      uArmsState: { value: 0 },
    },
    vertexShader: hologramVertexShader,
    fragmentShader: hologramFragmentShader,
    transparent: true,
    depthWrite: false,
    side: THREE.DoubleSide,
    blending: THREE.NormalBlending,
  }) as HologramMaterial;
}

export function HumanBodyModel({
  hovered = false,
  glowIntensity = 0.82,
  bodyClarity = 0.74,
  scanlineSpeed = 1,
  highlightedRegion = 'none',
  regionalMetrics,
}: HumanBodyModelProps) {
  const gltf = useGLTF(HUMAN_MODEL_URL);
  const materialsRef = useRef<HologramMaterial[]>([]);

  const highlightRegionValue = useMemo(() => {
    if (highlightedRegion === 'abdomen') return 1;
    if (highlightedRegion === 'chest') return 2;
    if (highlightedRegion === 'arms') return 3;
    if (highlightedRegion === 'whole') return 4;
    return 0;
  }, [highlightedRegion]);

  const regionStateValues = useMemo(() => {
    const normalizeState = (status?: RegionVisualization['status']) => {
      if (status === 'improved') return 1;
      if (status === 'regressed') return -1;
      return 0;
    };

    return {
      abdomenIntensity: regionalMetrics?.abdomen?.intensity ?? 0,
      chestIntensity: regionalMetrics?.chest?.intensity ?? 0,
      armsIntensity: regionalMetrics?.arms?.intensity ?? 0,
      abdomenState: normalizeState(regionalMetrics?.abdomen?.status),
      chestState: normalizeState(regionalMetrics?.chest?.status),
      armsState: normalizeState(regionalMetrics?.arms?.status),
    };
  }, [regionalMetrics]);

  const scene = useMemo(() => {
    const clonedScene = gltf.scene.clone(true);
    materialsRef.current = [];

    clonedScene.updateMatrixWorld(true);

    const rawBounds = new THREE.Box3().setFromObject(clonedScene);
    const rawSize = new THREE.Vector3();
    const rawCenter = new THREE.Vector3();
    rawBounds.getSize(rawSize);
    rawBounds.getCenter(rawCenter);

    const uniformScale = rawSize.y > 0 ? TARGET_HEIGHT / rawSize.y : 1;
    clonedScene.scale.setScalar(uniformScale);
    clonedScene.updateMatrixWorld(true);

    const scaledBounds = new THREE.Box3().setFromObject(clonedScene);
    const scaledCenter = new THREE.Vector3();
    scaledBounds.getCenter(scaledCenter);

    clonedScene.position.set(-scaledCenter.x, -scaledBounds.min.y, -scaledCenter.z);
    clonedScene.updateMatrixWorld(true);

    clonedScene.traverse((child) => {
      if (!(child instanceof THREE.Mesh)) return;

      child.geometry = child.geometry.clone();
      child.geometry.computeBoundingBox();
      if (!child.geometry.attributes.normal) {
        child.geometry.computeVertexNormals();
      }

      const bounds = child.geometry.boundingBox;
      const minY = bounds?.min.y ?? -1;
      const maxY = bounds?.max.y ?? 1;
      const minX = bounds?.min.x ?? -1;
      const maxX = bounds?.max.x ?? 1;

      const hologramMaterial = createHologramMaterial(
        minY,
        maxY,
        minX,
        maxX,
        glowIntensity,
        bodyClarity,
        scanlineSpeed,
      );
      child.material = hologramMaterial;
      child.frustumCulled = false;
      child.renderOrder = 2;
      materialsRef.current.push(hologramMaterial);
    });

    return clonedScene;
  }, [gltf.scene, glowIntensity, bodyClarity, scanlineSpeed]);

  useFrame((state, delta) => {
    const elapsed = state.clock.getElapsedTime();

    for (const material of materialsRef.current) {
      material.uniforms.uTime.value = elapsed;
      material.uniforms.uHover.value = THREE.MathUtils.damp(
        material.uniforms.uHover.value,
        hovered ? 1 : 0,
        4.5,
        delta,
      );
      material.uniforms.uHighlightRegion.value = highlightRegionValue;
      material.uniforms.uHighlightStrength.value = THREE.MathUtils.damp(
        material.uniforms.uHighlightStrength.value,
        highlightRegionValue > 0 ? 1 : 0,
        5.2,
        delta,
      );
      material.uniforms.uGlowIntensity.value = glowIntensity;
      material.uniforms.uBodyClarity.value = bodyClarity;
      material.uniforms.uScanlineSpeed.value = scanlineSpeed;
      material.uniforms.uAbdomenIntensity.value = regionStateValues.abdomenIntensity;
      material.uniforms.uChestIntensity.value = regionStateValues.chestIntensity;
      material.uniforms.uArmsIntensity.value = regionStateValues.armsIntensity;
      material.uniforms.uAbdomenState.value = regionStateValues.abdomenState;
      material.uniforms.uChestState.value = regionStateValues.chestState;
      material.uniforms.uArmsState.value = regionStateValues.armsState;
    }
  });

  useEffect(() => {
    return () => {
      for (const material of materialsRef.current) {
        material.dispose();
      }
      materialsRef.current = [];
    };
  }, []);

  return <primitive object={scene} />;
}

useGLTF.preload(HUMAN_MODEL_URL);
