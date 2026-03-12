/**
 * Export/import for canonical label map at ORIGINAL image resolution.
 * Export reads the label map directly — never depends on overlay colors.
 */

import { LabelMap } from './LabelMap';
import { SEG_CLASSES, PAINTABLE_CLASSES } from './constants';

export interface ExportMetadata {
  width: number;
  height: number;
  classes: { id: number; key: string; label: string }[];
  note: string;
}

export interface SegmentationExport {
  labelMapPng: string;
  perClassMasks: Record<string, string>;
  metadata: ExportMetadata;
}

function canvasToBase64(canvas: HTMLCanvasElement): string {
  return canvas.toDataURL('image/png').split(',')[1];
}

function makeGrayscaleCanvas(w: number, h: number, values: Uint8Array): HTMLCanvasElement {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  const ctx = c.getContext('2d')!;
  const img = ctx.createImageData(w, h);
  const px = img.data;
  for (let i = 0; i < values.length; i++) {
    const v = values[i];
    const j = i * 4;
    px[j] = v; px[j+1] = v; px[j+2] = v; px[j+3] = 255;
  }
  ctx.putImageData(img, 0, 0);
  return c;
}

export function exportLabelMapPng(lm: LabelMap): string {
  return canvasToBase64(makeGrayscaleCanvas(lm.width, lm.height, lm.data));
}

export function exportPerClassMasks(lm: LabelMap): Record<string, string> {
  const masks: Record<string, string> = {};
  for (const cls of PAINTABLE_CLASSES) {
    const bin = new Uint8Array(lm.data.length);
    let has = false;
    for (let i = 0; i < lm.data.length; i++) {
      if (lm.data[i] === cls.id) { bin[i] = 255; has = true; }
    }
    if (has) masks[cls.key] = canvasToBase64(makeGrayscaleCanvas(lm.width, lm.height, bin));
  }
  return masks;
}

export function exportMetadata(lm: LabelMap): ExportMetadata {
  return {
    width: lm.width,
    height: lm.height,
    classes: SEG_CLASSES.map((c) => ({ id: c.id, key: c.key, label: c.label })),
    note: 'left/right = person\'s anatomical left/right',
  };
}

export function exportAll(lm: LabelMap): SegmentationExport {
  return {
    labelMapPng: exportLabelMapPng(lm),
    perClassMasks: exportPerClassMasks(lm),
    metadata: exportMetadata(lm),
  };
}

export function importLabelMapPng(base64: string, width: number, height: number): Promise<LabelMap> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      const c = document.createElement('canvas');
      c.width = width; c.height = height;
      const ctx = c.getContext('2d')!;
      ctx.drawImage(img, 0, 0, width, height);
      const px = ctx.getImageData(0, 0, width, height).data;
      const data = new Uint8Array(width * height);
      for (let i = 0; i < data.length; i++) data[i] = px[i * 4];
      resolve(new LabelMap(width, height, data));
    };
    img.onerror = reject;
    img.src = `data:image/png;base64,${base64}`;
  });
}
