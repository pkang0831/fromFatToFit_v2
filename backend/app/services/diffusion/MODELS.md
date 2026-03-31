# CPU Diffusion Backends — Developer Guide

## Architecture

```
original image
    ↓
edit_prep   →  protect_mask, edit_mask, weight_map, feather_mask
    ↓
cut_warp    →  warped preview (deterministic geometry)
    ↓
cut_refine  →  PASS 1: seam repair (narrow contour mask, low strength)
            →  PASS 2: torso interior (abdomen/flanks, moderate strength)
            →  ROI crop → diffusion → composite back → final image
```

Both diffusion passes operate on a **small ROI crop** (~512px), not the
full image.  This makes CPU inference practical (30-90s per pass on a
modern CPU, vs. 5-15 min on the full image).

## Models

| Backend | Model | Size | Notes |
|---------|-------|------|-------|
| **sd15_inpaint_cpu** (primary) | `stable-diffusion-v1-5/stable-diffusion-inpainting` | ~4.3 GB | Fastest on CPU, native 512px |
| **sd2_inpaint_cpu** (fallback) | `sd2-community/stable-diffusion-2-inpainting` | ~5.2 GB | Better quality, slightly slower |
| **sd15_inpaint_openvino** (optional) | Same as sd15 + OpenVINO export | ~4.3 GB | 2-4x faster on Intel CPUs |

Neither model is gated — no HF token required for download.

## Quick start

```bash
# 1. Download the primary model (~4.3 GB):
python -m backend.app.tools.download_models download --profile sd15_only

# 2. Verify:
python -m backend.app.tools.download_models verify

# 3. Warm up (loads model, then unloads):
python -m backend.app.tools.download_models warmup

# 4. Test on a real image:
python -m backend.app.tools.download_models test-refine --image photo.jpg
```

## Configuration

All via environment variables or `backend/.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `BODY_DIFFUSION_BACKEND` | `sd15_inpaint_cpu` | `sd15_inpaint_cpu` / `sd2_inpaint_cpu` / `sd15_inpaint_openvino` |
| `HF_TOKEN` | _(empty)_ | Optional HF token |
| `HF_CACHE_DIR` | `~/.cache/huggingface/hub` | Model cache location |
| `DIFFUSION_ROI_MAX_PX` | `512` | Max side of the ROI crop |
| `DIFFUSION_NUM_STEPS` | `18` | Inference steps per pass |
| `DIFFUSION_USE_OPENVINO` | `false` | Informational flag |

### Switching backends

```bash
# SD 1.5 on CPU (primary — fastest):
BODY_DIFFUSION_BACKEND=sd15_inpaint_cpu

# SD 2 on CPU (fallback — better quality):
BODY_DIFFUSION_BACKEND=sd2_inpaint_cpu

# SD 1.5 via OpenVINO (Intel acceleration):
# Requires: pip install optimum[openvino]
BODY_DIFFUSION_BACKEND=sd15_inpaint_openvino
```

## ROI processing

Running SD on a full 1080p image on CPU would take 10+ minutes.
Instead:

1. `compute_roi()` finds the bounding box of the edit mask + safe margin
2. The ROI is resized to fit within `DIFFUSION_ROI_MAX_PX` (default 512)
3. Diffusion runs only on this small crop
4. The result is upscaled back and feather-composited into the full image

This reduces inference area by ~80-90%, making CPU turnaround practical.

## Two-pass refinement

**Pass 1 — Seam repair:**
- Mask: narrow 18px contour along edit_mask boundary
- Strength: low (0.30-0.50)
- Purpose: fix warp displacement artifacts at boundaries

**Pass 2 — Torso interior:**
- Mask: eroded edit_mask interior, gated by weight_map > 0.15
- Strength: moderate (0.35-0.60)
- Purpose: subtle abdomen/flank refinement, natural texture

## OpenVINO (optional Intel acceleration)

If your machine has an Intel CPU:

```bash
pip install optimum[openvino]
export BODY_DIFFUSION_BACKEND=sd15_inpaint_openvino
```

First load will export the model to OpenVINO IR format (takes a few
minutes).  Subsequent loads use the cached IR.  Expect 2-4x speedup.

If `optimum[openvino]` is not installed and `sd15_inpaint_openvino` is
requested, the loader automatically falls back to `sd15_inpaint_cpu`.

## Storage expectations

| What | Size |
|------|------|
| SD 1.5 Inpainting | ~4.3 GB |
| SD 2 Inpainting | ~5.2 GB |
| Both | ~9.5 GB |
| OpenVINO IR cache | +2-3 GB |

All cached under `~/.cache/huggingface/hub` (or `HF_CACHE_DIR`).

## Timing expectations (CPU, M-series Mac or modern x86)

| Operation | Approx. time |
|-----------|-------------|
| Model load (first time) | 15-30s |
| Model load (cached) | 8-15s |
| Pass 1 seam (512px, 15 steps) | 30-60s |
| Pass 2 torso (512px, 18 steps) | 40-90s |
| Full refine (both passes) | 70-150s |
| With OpenVINO | 30-60s total |

## Product constraints

- **Preserve:** face, hair, hands, phone, shorts, background
- **Geometry already done:** warp handles all shape changes
- **Diffusion only refines:** seam artifacts + subtle texture
- **Default preset:** `medium`
