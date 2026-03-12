'use client';

/**
 * Semantic label-map editor.
 *
 * Architecture:
 *   Source of truth: LabelMap (Uint8Array at original image resolution)
 *   Display: 3 stacked canvases at viewport-scaled resolution
 *   Overlay: rendered FROM the label map, never the reverse
 *   Export: reads the label map directly
 *
 * The editor can start from:
 *   - a SAM2-generated initialLabelMap  (normal flow)
 *   - a blank state                     (manual-only flow)
 *
 * left/right = person's anatomical left/right.
 */

import React, { useRef, useState, useCallback, useEffect } from 'react';
import {
  Paintbrush, Eraser, Undo2, Redo2, RotateCcw,
  Download, Eye, EyeOff,
} from 'lucide-react';
import {
  LabelMap, UndoManager, PAINTABLE_CLASSES, exportAll,
  type SegClass, type SegmentationExport,
} from '@/lib/segmentation';

// ── Props ───────────────────────────────────────────────────────────────────

export interface BodyMaskEditorProps {
  imageBase64: string;
  initialLabelMap?: LabelMap;
  onExport?: (result: SegmentationExport) => void;
}

type Tool = 'brush' | 'erase';

// ── Component ───────────────────────────────────────────────────────────────

export default function BodyMaskEditor({
  imageBase64,
  initialLabelMap,
  onExport,
}: BodyMaskEditorProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const baseCanvasRef = useRef<HTMLCanvasElement>(null);
  const overlayCanvasRef = useRef<HTMLCanvasElement>(null);
  const cursorCanvasRef = useRef<HTMLCanvasElement>(null);

  const labelMapRef = useRef<LabelMap | null>(null);
  const undoMgrRef = useRef(new UndoManager());
  const origImageRef = useRef<HTMLImageElement | null>(null);
  const isDrawingRef = useRef(false);
  const lastPosRef = useRef<{ x: number; y: number } | null>(null);

  const [tool, setTool] = useState<Tool>('brush');
  const [activeClass, setActiveClass] = useState<SegClass>(PAINTABLE_CLASSES[2]);
  const [brushSize, setBrushSize] = useState(24);
  const [opacity, setOpacity] = useState(0.45);
  const [showOverlay, setShowOverlay] = useState(true);
  const [canUndo, setCanUndo] = useState(false);
  const [canRedo, setCanRedo] = useState(false);
  const [displaySize, setDisplaySize] = useState({ w: 0, h: 0 });
  const [origSize, setOrigSize] = useState({ w: 0, h: 0 });

  const opacityRef = useRef(opacity);
  opacityRef.current = opacity;
  const showOverlayRef = useRef(showOverlay);
  showOverlayRef.current = showOverlay;

  // ── Overlay rendering (stable ref) ─────────────────────────────────────

  const renderOverlay = useCallback(() => {
    const oc = overlayCanvasRef.current;
    const lm = labelMapRef.current;
    if (!oc || !lm) return;
    const ctx = oc.getContext('2d');
    if (!ctx) return;
    if (!showOverlayRef.current) { ctx.clearRect(0, 0, oc.width, oc.height); return; }
    ctx.putImageData(lm.toOverlayImageData(oc.width, oc.height, opacityRef.current), 0, 0);
  }, []);

  useEffect(() => { renderOverlay(); }, [renderOverlay, showOverlay, opacity]);

  // ── Load image & init label map ─────────────────────────────────────────

  useEffect(() => {
    const img = new Image();
    img.onload = () => {
      origImageRef.current = img;
      const w = img.naturalWidth, h = img.naturalHeight;
      setOrigSize({ w, h });

      if (initialLabelMap && initialLabelMap.width === w && initialLabelMap.height === h) {
        labelMapRef.current = initialLabelMap.clone();
      } else {
        labelMapRef.current = new LabelMap(w, h);
      }
      undoMgrRef.current.clear();
      setCanUndo(false);
      setCanRedo(false);

      requestAnimationFrame(() => layoutCanvases(img));
    };
    const prefix = imageBase64.startsWith('data:') ? '' : 'data:image/jpeg;base64,';
    img.src = `${prefix}${imageBase64}`;
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [imageBase64, initialLabelMap]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const ro = new ResizeObserver(() => {
      if (origImageRef.current) layoutCanvases(origImageRef.current);
    });
    ro.observe(container);
    return () => ro.disconnect();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const layoutCanvases = useCallback((img: HTMLImageElement) => {
    const container = containerRef.current;
    if (!container) return;
    const maxW = container.clientWidth;
    const scale = Math.min(maxW / img.naturalWidth, 1);
    const w = Math.round(img.naturalWidth * scale);
    const h = Math.round(img.naturalHeight * scale);
    setDisplaySize({ w, h });
    for (const ref of [baseCanvasRef, overlayCanvasRef, cursorCanvasRef]) {
      if (ref.current) { ref.current.width = w; ref.current.height = h; }
    }
    const ctx = baseCanvasRef.current?.getContext('2d');
    if (ctx) ctx.drawImage(img, 0, 0, w, h);
    renderOverlay();
  }, [renderOverlay]);

  // ── Coordinates ─────────────────────────────────────────────────────────

  const displayToOrig = useCallback(
    (dx: number, dy: number) => {
      if (!displaySize.w || !origSize.w) return { x: 0, y: 0 };
      return {
        x: Math.round(dx * origSize.w / displaySize.w),
        y: Math.round(dy * origSize.h / displaySize.h),
      };
    }, [displaySize, origSize],
  );

  const brushRadiusOrig = useCallback(() => {
    if (!displaySize.w || !origSize.w) return brushSize;
    return Math.max(1, Math.round(brushSize * origSize.w / displaySize.w));
  }, [brushSize, displaySize, origSize]);

  const getPointerPos = useCallback((e: React.PointerEvent) => {
    const c = cursorCanvasRef.current;
    if (!c) return { x: 0, y: 0 };
    const r = c.getBoundingClientRect();
    return {
      x: ((e.clientX - r.left) / r.width) * c.width,
      y: ((e.clientY - r.top) / r.height) * c.height,
    };
  }, []);

  // ── History ─────────────────────────────────────────────────────────────

  const syncHistory = useCallback(() => {
    setCanUndo(undoMgrRef.current.canUndo);
    setCanRedo(undoMgrRef.current.canRedo);
  }, []);

  const doUndo = useCallback(() => {
    const lm = labelMapRef.current;
    if (!lm) return;
    const prev = undoMgrRef.current.undo(lm.data);
    if (prev) { lm.data.set(prev); renderOverlay(); syncHistory(); }
  }, [renderOverlay, syncHistory]);

  const doRedo = useCallback(() => {
    const lm = labelMapRef.current;
    if (!lm) return;
    const next = undoMgrRef.current.redo(lm.data);
    if (next) { lm.data.set(next); renderOverlay(); syncHistory(); }
  }, [renderOverlay, syncHistory]);

  const doReset = useCallback(() => {
    const lm = labelMapRef.current;
    if (!lm) return;
    undoMgrRef.current.push(lm.data);
    lm.clear();
    renderOverlay();
    syncHistory();
  }, [renderOverlay, syncHistory]);

  // ── Drawing ─────────────────────────────────────────────────────────────

  const handlePointerDown = useCallback((e: React.PointerEvent) => {
    e.preventDefault();
    (e.target as HTMLElement).setPointerCapture(e.pointerId);
    const lm = labelMapRef.current;
    if (!lm) return;
    undoMgrRef.current.push(lm.data);
    isDrawingRef.current = true;
    const dp = getPointerPos(e);
    const op = displayToOrig(dp.x, dp.y);
    lastPosRef.current = op;
    const r = brushRadiusOrig();
    if (tool === 'brush') lm.paintCircle(op.x, op.y, r, activeClass.id);
    else lm.eraseCircle(op.x, op.y, r);
    renderOverlay();
    syncHistory();
  }, [tool, activeClass, getPointerPos, displayToOrig, brushRadiusOrig, renderOverlay, syncHistory]);

  const handlePointerMove = useCallback((e: React.PointerEvent) => {
    const dp = getPointerPos(e);
    const cc = cursorCanvasRef.current;
    if (cc) {
      const ctx = cc.getContext('2d');
      if (ctx) {
        ctx.clearRect(0, 0, cc.width, cc.height);
        ctx.beginPath();
        ctx.arc(dp.x, dp.y, brushSize, 0, Math.PI * 2);
        if (tool === 'brush') {
          const [r, g, b] = activeClass.color;
          ctx.strokeStyle = `rgba(${r},${g},${b},0.9)`;
          ctx.fillStyle = `rgba(${r},${g},${b},0.15)`;
          ctx.fill();
        } else {
          ctx.strokeStyle = 'rgba(255,80,80,0.9)';
        }
        ctx.lineWidth = 2;
        ctx.stroke();
      }
    }
    if (!isDrawingRef.current) return;
    const lm = labelMapRef.current;
    if (!lm) return;
    const op = displayToOrig(dp.x, dp.y);
    const last = lastPosRef.current || op;
    const r = brushRadiusOrig();
    if (tool === 'brush') lm.paintLine(last.x, last.y, op.x, op.y, r, activeClass.id);
    else lm.eraseLine(last.x, last.y, op.x, op.y, r);
    lastPosRef.current = op;
    renderOverlay();
  }, [tool, activeClass, brushSize, getPointerPos, displayToOrig, brushRadiusOrig, renderOverlay]);

  const handlePointerUp = useCallback(() => {
    isDrawingRef.current = false;
    lastPosRef.current = null;
  }, []);

  const handlePointerLeave = useCallback(() => {
    const cc = cursorCanvasRef.current;
    if (cc) { const ctx = cc.getContext('2d'); if (ctx) ctx.clearRect(0, 0, cc.width, cc.height); }
    isDrawingRef.current = false;
    lastPosRef.current = null;
  }, []);

  // ── Keyboard shortcuts ──────────────────────────────────────────────────

  useEffect(() => {
    const h = (e: KeyboardEvent) => {
      const meta = e.metaKey || e.ctrlKey;
      if (e.key === 'b' && !meta) { setTool('brush'); e.preventDefault(); }
      if (e.key === 'e' && !meta) { setTool('erase'); e.preventDefault(); }
      if (e.key === '[') { setBrushSize((s) => Math.max(2, s - 4)); e.preventDefault(); }
      if (e.key === ']') { setBrushSize((s) => Math.min(80, s + 4)); e.preventDefault(); }
      if (e.key === 'z' && meta && !e.shiftKey) { doUndo(); e.preventDefault(); }
      if (e.key === 'z' && meta && e.shiftKey) { doRedo(); e.preventDefault(); }
    };
    window.addEventListener('keydown', h);
    return () => window.removeEventListener('keydown', h);
  }, [doUndo, doRedo]);

  // ── Export ──────────────────────────────────────────────────────────────

  const handleExport = useCallback(() => {
    const lm = labelMapRef.current;
    if (!lm) return;
    onExport?.(exportAll(lm));
  }, [onExport]);

  // ── Render ──────────────────────────────────────────────────────────────

  const cs: React.CSSProperties = { position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' };

  return (
    <div className="w-full space-y-3">
      {/* Class selector */}
      <div className="flex items-center gap-1.5 flex-wrap p-2 bg-gray-800/60 rounded-lg border border-gray-700">
        {PAINTABLE_CLASSES.map((cls) => (
          <button
            key={cls.id}
            onClick={() => { setActiveClass(cls); setTool('brush'); }}
            className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeClass.id === cls.id && tool === 'brush'
                ? 'ring-2 ring-white/60 bg-gray-700 text-white'
                : 'text-gray-400 hover:bg-gray-700/50 hover:text-gray-200'
            }`}
          >
            <span className="w-3 h-3 rounded-full border border-white/30 flex-shrink-0"
              style={{ backgroundColor: `rgb(${cls.color.join(',')})` }} />
            {cls.label}
          </button>
        ))}
      </div>

      {/* Toolbar */}
      <div className="flex items-center gap-2 flex-wrap p-2 bg-gray-800/60 rounded-lg border border-gray-700">
        <Btn active={tool === 'brush'} onClick={() => setTool('brush')} title="Brush (B)"><Paintbrush size={16} /></Btn>
        <Btn active={tool === 'erase'} onClick={() => setTool('erase')} title="Erase (E)"><Eraser size={16} /></Btn>
        <div className="w-px h-6 bg-gray-600 mx-1" />
        <span className="text-xs text-gray-400 w-6 text-right">{brushSize}</span>
        <input type="range" min={2} max={80} value={brushSize}
          onChange={(e) => setBrushSize(Number(e.target.value))}
          className="w-20 accent-cyan-500" title="Brush size" />
        <div className="w-px h-6 bg-gray-600 mx-1" />
        <span className="text-[10px] text-gray-500">Opacity</span>
        <input type="range" min={10} max={80} value={Math.round(opacity * 100)}
          onChange={(e) => setOpacity(Number(e.target.value) / 100)}
          className="w-16 accent-cyan-500" />
        <div className="w-px h-6 bg-gray-600 mx-1" />
        <Btn onClick={() => setShowOverlay((v) => !v)} title="Toggle overlay">
          {showOverlay ? <Eye size={16} /> : <EyeOff size={16} />}
        </Btn>
        <Btn onClick={doUndo} title="Undo" disabled={!canUndo}><Undo2 size={16} /></Btn>
        <Btn onClick={doRedo} title="Redo" disabled={!canRedo}><Redo2 size={16} /></Btn>
        <Btn onClick={doReset} title="Reset"><RotateCcw size={16} /></Btn>
        <div className="flex-1" />
        <button onClick={handleExport}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium bg-cyan-700 hover:bg-cyan-600 text-white transition-colors">
          <Download size={14} /> Export
        </button>
      </div>

      {/* Canvas stack */}
      <div ref={containerRef}
        className="relative w-full rounded-lg overflow-hidden border border-gray-700 bg-black"
        style={{ height: displaySize.h || 400, touchAction: 'none', cursor: 'none' }}>
        <canvas ref={baseCanvasRef} style={cs} />
        <canvas ref={overlayCanvasRef} style={cs} />
        <canvas ref={cursorCanvasRef} style={{ ...cs, zIndex: 10 }}
          onPointerDown={handlePointerDown}
          onPointerMove={handlePointerMove}
          onPointerUp={handlePointerUp}
          onPointerLeave={handlePointerLeave} />
        {displaySize.w === 0 && (
          <div className="absolute inset-0 flex items-center justify-center text-gray-500 text-sm">Loading image...</div>
        )}
      </div>

      {/* Legend + shortcuts */}
      <div className="flex items-center gap-3 flex-wrap text-[11px] text-gray-500">
        <span>Classes:</span>
        {PAINTABLE_CLASSES.map((cls) => (
          <span key={cls.id} className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-sm" style={{ backgroundColor: `rgb(${cls.color.join(',')})` }} />
            {cls.label}
          </span>
        ))}
      </div>
      <div className="text-[10px] text-gray-600 flex gap-4 flex-wrap">
        <span>B = brush</span><span>E = erase</span><span>[ / ] = size</span>
        <span>Cmd+Z = undo</span><span>Shift+Cmd+Z = redo</span>
      </div>
    </div>
  );
}

function Btn({ children, active, onClick, title, disabled }: {
  children: React.ReactNode; active?: boolean; onClick: () => void; title: string; disabled?: boolean;
}) {
  return (
    <button onClick={onClick} title={title} disabled={disabled}
      className={`p-2 rounded-md transition-colors ${
        active ? 'bg-cyan-600 text-white' : 'text-gray-400 hover:bg-gray-700 hover:text-gray-200'
      } ${disabled ? 'opacity-30 cursor-not-allowed' : ''}`}>{children}</button>
  );
}
