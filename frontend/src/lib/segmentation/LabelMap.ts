/**
 * Canonical label map: Uint8Array where each pixel = class ID (0-7).
 * Row-major: index = y * width + x.
 *
 * This is the single source of truth for segmentation.
 * The visible overlay is rendered FROM this, never the reverse.
 *
 * SAM2 integration: call fillFromMask(binaryMask, classId).
 */

import { getClassColor } from './constants';

export class LabelMap {
  readonly width: number;
  readonly height: number;
  readonly data: Uint8Array;

  constructor(width: number, height: number, source?: Uint8Array) {
    this.width = width;
    this.height = height;
    this.data = source ? new Uint8Array(source) : new Uint8Array(width * height);
  }

  setPixel(x: number, y: number, classId: number): void {
    if (x < 0 || x >= this.width || y < 0 || y >= this.height) return;
    this.data[y * this.width + x] = classId;
  }

  paintCircle(cx: number, cy: number, radius: number, classId: number): void {
    const r = Math.round(radius);
    const r2 = r * r;
    const x0 = Math.max(0, cx - r);
    const x1 = Math.min(this.width - 1, cx + r);
    const y0 = Math.max(0, cy - r);
    const y1 = Math.min(this.height - 1, cy + r);
    for (let y = y0; y <= y1; y++) {
      const dy = y - cy;
      const dy2 = dy * dy;
      const row = y * this.width;
      for (let x = x0; x <= x1; x++) {
        const dx = x - cx;
        if (dx * dx + dy2 <= r2) this.data[row + x] = classId;
      }
    }
  }

  paintLine(x0: number, y0: number, x1: number, y1: number, radius: number, classId: number): void {
    const dx = Math.abs(x1 - x0);
    const dy = Math.abs(y1 - y0);
    const dist = Math.max(dx, dy, 1);
    const sx = (x1 - x0) / dist;
    const sy = (y1 - y0) / dist;
    for (let i = 0; i <= dist; i++) {
      this.paintCircle(Math.round(x0 + sx * i), Math.round(y0 + sy * i), radius, classId);
    }
  }

  eraseCircle(cx: number, cy: number, radius: number): void {
    this.paintCircle(cx, cy, radius, 0);
  }

  eraseLine(x0: number, y0: number, x1: number, y1: number, radius: number): void {
    this.paintLine(x0, y0, x1, y1, radius, 0);
  }

  /** Import a binary mask for a class. SAM2 integration point. */
  fillFromMask(mask: Uint8Array, classId: number): void {
    const len = Math.min(mask.length, this.data.length);
    for (let i = 0; i < len; i++) {
      if (mask[i] > 128) this.data[i] = classId;
    }
  }

  clear(): void { this.data.fill(0); }

  clone(): LabelMap { return new LabelMap(this.width, this.height, this.data); }

  /** Create a new label map at (targetW, targetH) by nearest-neighbor sampling from this. */
  scaleTo(targetW: number, targetH: number): LabelMap {
    const out = new LabelMap(targetW, targetH);
    const xRatio = this.width / targetW;
    const yRatio = this.height / targetH;
    for (let dy = 0; dy < targetH; dy++) {
      const sy = Math.min(Math.floor(dy * yRatio), this.height - 1);
      const srcRow = sy * this.width;
      const dstRow = dy * targetW;
      for (let dx = 0; dx < targetW; dx++) {
        const sx = Math.min(Math.floor(dx * xRatio), this.width - 1);
        out.data[dstRow + dx] = this.data[srcRow + sx];
      }
    }
    return out;
  }

  hasLabels(): boolean {
    for (let i = 0; i < this.data.length; i++) {
      if (this.data[i] !== 0) return true;
    }
    return false;
  }

  /** Render overlay at display resolution. Nearest-neighbor sampling. */
  toOverlayImageData(displayWidth: number, displayHeight: number, opacity: number): ImageData {
    const out = new ImageData(displayWidth, displayHeight);
    const px = out.data;
    const alpha = Math.round(opacity * 255);
    const sx = this.width / displayWidth;
    const sy = this.height / displayHeight;

    for (let dy = 0; dy < displayHeight; dy++) {
      const srcY = Math.min(Math.floor(dy * sy), this.height - 1);
      const srcRow = srcY * this.width;
      const dstRow = dy * displayWidth;
      for (let dx = 0; dx < displayWidth; dx++) {
        const srcX = Math.min(Math.floor(dx * sx), this.width - 1);
        const cid = this.data[srcRow + srcX];
        if (cid === 0) continue;
        const [r, g, b] = getClassColor(cid);
        const i = (dstRow + dx) * 4;
        px[i] = r; px[i + 1] = g; px[i + 2] = b; px[i + 3] = alpha;
      }
    }
    return out;
  }
}
