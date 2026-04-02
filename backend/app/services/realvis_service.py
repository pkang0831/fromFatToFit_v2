"""RealVisXL V5.0 Lightning transformation pipeline.

Ported from Colab notebook (notebook_c_realvis_benchmark_batch.ipynb).
Implements the full crop-based two-pass img2img pipeline:

1. Auto torso mask (rounded rect + shoulder ellipse + cut-top + feather)
2. Crop bundle (mask bbox → expand → crop → resize)
3. Two-pass generation via Replicate (shape pass + polish pass)
4. Feathered compositing (edited crop blended back into original)
"""

from __future__ import annotations

import base64
import hashlib
import io
import logging
import math
import time
from dataclasses import dataclass
from typing import Any, Optional

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

from .transformation_types import TransformationMode

logger = logging.getLogger(__name__)

# ── Pipeline constants (from notebook) ────────────────────────────────────────

MAX_SIDE = 1024
CROP_MAX_SIDE = 1152
MASK_FEATHER = 14
CROP_BLEND_FEATHER = 10
CROP_EXPAND_X = 0.16
CROP_EXPAND_TOP = 0.12
CROP_EXPAND_BOTTOM = 0.10

# ── Lightning backend params ──────────────────────────────────────────────────

LIGHTNING_BACKEND = {
    "steps": 10,
    "cfg": 2.2,
    "min_effective_steps": 3,
    "max_step_multiplier": 1.5,
    "second_pass": {
        "enabled": True,
        "steps": 8,
        "cfg": 1.8,
        "strength": 0.09,
        "min_effective_steps": 2,
        "max_step_multiplier": 1.5,
    },
}

# ── Preset library (from notebook) ───────────────────────────────────────────

PRESET_LIBRARY = {
    "male_cut": {
        "mask_cfg": {
            "upper_left": (0.30, 0.40),
            "lower_right": (0.70, 0.82),
            "shoulder_ellipse": (0.25, 0.34, 0.75, 0.53),
            "cut_top": 0.33,
            "feather": MASK_FEATHER,
        },
        "identity_prefix": (
            "same man, same person, same face, same hair, same skin tone, "
            "same lighting, same shadows, same color temperature, "
            "same bathroom or room, same camera angle, same pose, same phone pose, "
            "photorealistic, realistic skin texture, natural body proportions, "
            "consistent lighting with source photo"
        ),
        "polish_suffix": (
            "preserve identity, preserve pose, preserve background, preserve chest size, "
            "preserve shoulder size, preserve arm size, keep changes focused on abdomen and waist, "
            "match original skin texture and lighting exactly, realistic details"
        ),
        "common_neg": (
            "different person, changed face, changed hair, changed background, changed pose, "
            "different lighting, different shadows, different skin color, color shift, "
            "oversized chest, oversized shoulders, oversized arms, smaller chest, smaller shoulders, "
            "extreme v taper, tiny waist, fake abs, etched abs, overly symmetrical abs, steroid look, "
            "weight gain, bloated, thicker waist, wider midsection, "
            "airbrushed skin, plastic skin, CG render, smooth skin, washed out, "
            "overexposed, underexposed, desaturated, "
            "cartoon, illustration, blurry, low quality, bad anatomy, deformed"
        ),
        "stages": {
            "2_weeks": {
                "body_prompt": (
                    "slightly tighter midsection, slightly narrower waist, "
                    "smoother lower abdomen, beginning of torso definition, "
                    "natural early cut progress"
                ),
                "strength": 0.22,
            },
            "1_month": {
                "body_prompt": (
                    "noticeably tighter midsection, clearly narrower waist, "
                    "faint upper ab lines emerging, more defined torso shape, "
                    "chest and shoulders maintained, realistic mid-cut progress"
                ),
                "strength": 0.30,
            },
            "2_months": {
                "body_prompt": (
                    "lean athletic stomach, visible natural ab definition, "
                    "clearly narrower waist, oblique lines emerging, "
                    "athletic torso V-shape, realistic late-stage cut"
                ),
                "strength": 0.38,
            },
            "goal": {
                "body_prompt": (
                    "visible natural abs, lean athletic abdomen, defined obliques, "
                    "narrow athletic waist, same chest size, same shoulders, "
                    "realistic motivational transformation, not extreme"
                ),
                "strength": 0.42,
            },
        },
    },
    "male_bulk": {
        "mask_cfg": {
            "upper_left": (0.29, 0.38),
            "lower_right": (0.71, 0.82),
            "shoulder_ellipse": (0.23, 0.32, 0.77, 0.54),
            "cut_top": 0.31,
            "feather": MASK_FEATHER,
        },
        "identity_prefix": (
            "same man, same person, same face, same hair, same skin tone, "
            "same lighting, same shadows, same color temperature, "
            "same room, same camera angle, same pose, same phone pose, "
            "photorealistic, realistic skin texture, natural body proportions, "
            "consistent lighting with source photo"
        ),
        "polish_suffix": (
            "preserve identity, preserve pose, preserve background, maintain realistic proportions, "
            "natural lean-bulk progress, match original skin texture and lighting exactly, "
            "avoid exaggerated bodybuilder changes"
        ),
        "common_neg": (
            "different person, changed face, changed pose, changed background, bodybuilder, "
            "different lighting, different shadows, different skin color, color shift, "
            "massive chest, massive shoulders, extreme arms, steroid look, fake muscle striations, "
            "airbrushed skin, plastic skin, CG render, smooth skin, washed out, "
            "overexposed, underexposed, desaturated, "
            "cartoon, illustration, blurry, low quality, bad anatomy, deformed"
        ),
        "stages": {
            "2_weeks": {
                "body_prompt": (
                    "slightly thicker pectoral muscles, marginally wider shoulder caps, "
                    "firmer upper arm volume, same waist, same skin texture, "
                    "natural two-week lean bulk progress"
                ),
                "strength": 0.22,
            },
            "1_month": {
                "body_prompt": (
                    "fuller pectoral mass, visibly wider deltoid caps, increased arm circumference, "
                    "same waist, same abdominal area, "
                    "athletic one-month lean bulk progress"
                ),
                "strength": 0.30,
            },
            "2_months": {
                "body_prompt": (
                    "noticeably larger chest muscles, broader thicker shoulders, "
                    "thicker arms with visible bicep and tricep volume, "
                    "same waist circumference, realistic two-month lean bulk"
                ),
                "strength": 0.38,
            },
            "goal": {
                "body_prompt": (
                    "well-developed chest muscles, broad rounded shoulder caps, "
                    "thick defined arms, upper body clearly more muscular, "
                    "natural athletic lean bulk result, not extreme"
                ),
                "strength": 0.40,
            },
        },
    },
    "female_cut": {
        "mask_cfg": {
            "upper_left": (0.30, 0.42),
            "lower_right": (0.70, 0.82),
            "shoulder_ellipse": (0.26, 0.36, 0.74, 0.54),
            "cut_top": 0.35,
            "feather": MASK_FEATHER,
        },
        "identity_prefix": (
            "same woman, same person, same face, same hair, same skin tone, "
            "same lighting, same shadows, same color temperature, "
            "same room, same camera angle, same pose, same phone pose, "
            "photorealistic, realistic skin texture, natural body proportions, "
            "consistent lighting with source photo"
        ),
        "polish_suffix": (
            "preserve identity, preserve pose, preserve background, preserve bust shape, "
            "keep changes focused on waist and abdomen, "
            "match original skin texture and lighting exactly, "
            "realistic toned result, no exaggerated hourglass"
        ),
        "common_neg": (
            "different person, changed face, changed pose, changed background, altered bust shape, "
            "different lighting, different shadows, different skin color, color shift, "
            "tiny waist, exaggerated hourglass, fake abs, bodybuilder, "
            "weight gain, bloated, thicker waist, wider midsection, "
            "airbrushed skin, plastic skin, CG render, smooth skin, washed out, "
            "overexposed, underexposed, desaturated, "
            "cartoon, illustration, blurry, low quality, bad anatomy, deformed"
        ),
        "stages": {
            "2_weeks": {
                "body_prompt": (
                    "slightly tighter midsection, slightly narrower waist, "
                    "smoother lower abdomen, bust and shoulders unchanged, "
                    "natural early cut progress"
                ),
                "strength": 0.20,
            },
            "1_month": {
                "body_prompt": (
                    "noticeably tighter midsection, clearly narrower waist, "
                    "emerging torso tone, bust unchanged, "
                    "realistic mid-cut progress"
                ),
                "strength": 0.28,
            },
            "2_months": {
                "body_prompt": (
                    "lean toned waist, visible ab definition beginning, "
                    "clearly more athletic midsection, "
                    "realistic late-stage cut progress"
                ),
                "strength": 0.34,
            },
            "goal": {
                "body_prompt": (
                    "lean athletic waist, natural ab outline, toned midsection, "
                    "toned obliques, narrow waist, "
                    "realistic motivational cut result, not extreme"
                ),
                "strength": 0.36,
            },
        },
    },
    "female_bulk": {
        "mask_cfg": {
            "upper_left": (0.30, 0.42),
            "lower_right": (0.70, 0.82),
            "shoulder_ellipse": (0.26, 0.36, 0.74, 0.54),
            "cut_top": 0.35,
            "feather": MASK_FEATHER,
        },
        "identity_prefix": (
            "same woman, same person, same face, same hair, same skin tone, "
            "same lighting, same shadows, same color temperature, "
            "same room, same camera angle, same pose, same phone pose, "
            "photorealistic, realistic skin texture, natural body proportions, "
            "consistent lighting with source photo"
        ),
        "polish_suffix": (
            "preserve identity, preserve pose, preserve background, preserve bust shape, "
            "show realistic athletic muscle gain, "
            "match original skin texture and lighting exactly, "
            "avoid exaggerated bodybuilding look"
        ),
        "common_neg": (
            "different person, changed face, changed pose, changed background, altered bust shape, "
            "different lighting, different shadows, different skin color, color shift, "
            "bodybuilder, oversized shoulders, oversized arms, fake striations, steroid look, "
            "airbrushed skin, plastic skin, CG render, smooth skin, washed out, "
            "overexposed, underexposed, desaturated, "
            "cartoon, illustration, blurry, low quality, bad anatomy, deformed"
        ),
        "stages": {
            "2_weeks": {
                "body_prompt": (
                    "slightly firmer deltoid caps, marginally more arm definition, "
                    "same waist, same skin texture, "
                    "natural two-week female lean bulk progress"
                ),
                "strength": 0.20,
            },
            "1_month": {
                "body_prompt": (
                    "visibly rounder shoulder caps, firmer toned upper arms, "
                    "subtle upper back width increase, same waist, "
                    "realistic one-month female lean bulk"
                ),
                "strength": 0.28,
            },
            "2_months": {
                "body_prompt": (
                    "defined rounded shoulders, toned arms with visible muscle shape, "
                    "fuller upper torso, athletic feminine physique, "
                    "natural two-month female lean bulk progress"
                ),
                "strength": 0.34,
            },
            "goal": {
                "body_prompt": (
                    "well-defined toned shoulders, shapely athletic arms, "
                    "athletic feminine upper body, clearly more muscular, "
                    "realistic female lean bulk result, not extreme"
                ),
                "strength": 0.36,
            },
        },
    },
}

# ── Stage name mapping (planner stage_number -> notebook stage key) ──────────

STAGE_MAP = {1: "2_weeks", 2: "1_month", 3: "2_months", 4: "goal"}


# ── Image utilities (from notebook) ──────────────────────────────────────────

def resize_long_side(img: Image.Image, max_side: int = 1024, allow_upscale: bool = False) -> Image.Image:
    img = ImageOps.exif_transpose(img).convert("RGB")
    w, h = img.size
    raw_scale = max_side / max(w, h)
    scale = raw_scale if allow_upscale else min(raw_scale, 1.0)
    nw = max(64, int(round((w * scale) / 64) * 64))
    nh = max(64, int(round((h * scale) / 64) * 64))
    return img.resize((nw, nh), Image.LANCZOS)


def ensure_rgb(img: Image.Image, size: tuple[int, int] | None = None) -> Image.Image:
    img = ImageOps.exif_transpose(img).convert("RGB")
    if size is not None and img.size != size:
        img = img.resize(size, Image.LANCZOS)
    return img


def ensure_mask(mask: Image.Image | np.ndarray, size: tuple[int, int] | None = None) -> Image.Image:
    if isinstance(mask, Image.Image):
        m = mask.convert("L")
    else:
        m = Image.fromarray(mask).convert("L")
    if size is not None and m.size != size:
        m = m.resize(size, Image.LANCZOS)
    return m


def pil_to_base64(img: Image.Image, fmt: str = "JPEG", quality: int = 92) -> str:
    buf = io.BytesIO()
    img.save(buf, format=fmt, quality=quality)
    return base64.b64encode(buf.getvalue()).decode()


def base64_to_pil(b64: str) -> Image.Image:
    raw = base64.b64decode(b64)
    return Image.open(io.BytesIO(raw)).convert("RGB")


# ── Masking (from notebook) ──────────────────────────────────────────────────

def make_auto_torso_mask(img: Image.Image, cfg: dict) -> Image.Image:
    w, h = img.size
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)

    x0 = int(cfg["upper_left"][0] * w)
    y0 = int(cfg["upper_left"][1] * h)
    x1 = int(cfg["lower_right"][0] * w)
    y1 = int(cfg["lower_right"][1] * h)
    d.rounded_rectangle((x0, y0, x1, y1), radius=max(12, int(0.04 * w)), fill=255)

    ex0 = int(cfg["shoulder_ellipse"][0] * w)
    ey0 = int(cfg["shoulder_ellipse"][1] * h)
    ex1 = int(cfg["shoulder_ellipse"][2] * w)
    ey1 = int(cfg["shoulder_ellipse"][3] * h)
    d.ellipse((ex0, ey0, ex1, ey1), fill=255)

    cut_y = int(cfg["cut_top"] * h)
    d.rectangle((0, 0, w, cut_y), fill=0)
    return m.filter(ImageFilter.GaussianBlur(cfg["feather"]))


# ── Crop bundle (from notebook) ──────────────────────────────────────────────

def mask_bbox(mask: Image.Image, threshold: int = 12) -> tuple[int, int, int, int]:
    m = ensure_mask(mask)
    arr = np.asarray(m)
    ys, xs = np.where(arr >= threshold)
    if len(xs) == 0 or len(ys) == 0:
        return (0, 0, m.size[0], m.size[1])
    return (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)


def expand_box(
    box: tuple[int, int, int, int],
    image_size: tuple[int, int],
    expand_x: float = CROP_EXPAND_X,
    expand_top: float = CROP_EXPAND_TOP,
    expand_bottom: float = CROP_EXPAND_BOTTOM,
) -> tuple[int, int, int, int]:
    x0, y0, x1, y1 = box
    img_w, img_h = image_size
    box_w = max(1, x1 - x0)
    box_h = max(1, y1 - y0)

    pad_x = int(round(box_w * expand_x))
    pad_top = int(round(box_h * expand_top))
    pad_bottom = int(round(box_h * expand_bottom))

    x0 = max(0, x0 - pad_x)
    x1 = min(img_w, x1 + pad_x)
    y0 = max(0, y0 - pad_top)
    y1 = min(img_h, y1 + pad_bottom)
    return (x0, y0, x1, y1)


@dataclass
class CropBundle:
    crop_box: tuple[int, int, int, int]
    source_crop: Image.Image
    mask_crop: Image.Image
    gen_source: Image.Image
    gen_mask: Image.Image


def build_crop_bundle(source_img: Image.Image, mask_img: Image.Image, crop_max_side: int = CROP_MAX_SIDE) -> CropBundle:
    crop_box = expand_box(mask_bbox(mask_img), source_img.size)
    source_crop = source_img.crop(crop_box)
    mask_crop = ensure_mask(mask_img.crop(crop_box), size=source_crop.size)
    gen_source = resize_long_side(source_crop, crop_max_side, allow_upscale=True)
    gen_mask = ensure_mask(mask_crop, size=gen_source.size)

    return CropBundle(
        crop_box=crop_box,
        source_crop=source_crop,
        mask_crop=mask_crop,
        gen_source=gen_source,
        gen_mask=gen_mask,
    )


# ── Color matching (LAB space) ────────────────────────────────────────────────

def match_color_lab(
    source: Image.Image,
    target: Image.Image,
    mask: Image.Image | None = None,
    strength: float = 0.85,
) -> Image.Image:
    """Match the color/lighting of *target* to *source* in LAB space.

    Uses mean/std transfer on each LAB channel so the generated image
    inherits the original photo's lighting and skin tone.  When *mask*
    is provided only the masked region is sampled for statistics, but
    the correction is applied to the full image.

    *strength* blends between the raw target (0.0) and fully corrected (1.0).
    """
    src_arr = np.asarray(source.convert("RGB")).astype(np.float32)
    tgt_arr = np.asarray(target.convert("RGB")).astype(np.float32)

    # RGB → LAB (approximate via linear transform, good enough for color transfer)
    def rgb_to_lab(img_f32: np.ndarray) -> np.ndarray:
        # sRGB → linear
        lin = np.where(img_f32 / 255.0 > 0.04045,
                       ((img_f32 / 255.0 + 0.055) / 1.055) ** 2.4,
                       img_f32 / 255.0 / 12.92)
        # linear RGB → XYZ (D65)
        x = lin[..., 0] * 0.4124564 + lin[..., 1] * 0.3575761 + lin[..., 2] * 0.1804375
        y = lin[..., 0] * 0.2126729 + lin[..., 1] * 0.7151522 + lin[..., 2] * 0.0721750
        z = lin[..., 0] * 0.0193339 + lin[..., 1] * 0.1191920 + lin[..., 2] * 0.9503041
        # XYZ → LAB
        xn, yn, zn = 0.95047, 1.0, 1.08883
        def f(t):
            return np.where(t > 0.008856, t ** (1/3), 7.787 * t + 16/116)
        fx, fy, fz = f(x / xn), f(y / yn), f(z / zn)
        L = 116 * fy - 16
        a = 500 * (fx - fy)
        b = 200 * (fy - fz)
        return np.stack([L, a, b], axis=-1)

    def lab_to_rgb(lab: np.ndarray) -> np.ndarray:
        L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
        fy = (L + 16) / 116
        fx = a / 500 + fy
        fz = fy - b / 200
        def finv(t):
            return np.where(t > 0.206893, t ** 3, (t - 16/116) / 7.787)
        xn, yn, zn = 0.95047, 1.0, 1.08883
        x = finv(fx) * xn
        y = finv(fy) * yn
        z = finv(fz) * zn
        r = x * 3.2404542 + y * -1.5371385 + z * -0.4985314
        g = x * -0.9692660 + y * 1.8760108 + z * 0.0415560
        bl = x * 0.0556434 + y * -0.2040259 + z * 1.0572252
        lin = np.stack([r, g, bl], axis=-1)
        lin = np.clip(lin, 0, None)
        srgb = np.where(lin > 0.0031308,
                        1.055 * (lin ** (1/2.4)) - 0.055,
                        12.92 * lin)
        return np.clip(srgb * 255, 0, 255).astype(np.uint8)

    src_lab = rgb_to_lab(src_arr)
    tgt_lab = rgb_to_lab(tgt_arr)

    # Compute stats (optionally masked)
    if mask is not None:
        m = np.asarray(mask.convert("L").resize(source.size, Image.LANCZOS)) > 127
        src_pixels = src_lab[m]
        m_tgt = np.asarray(mask.convert("L").resize(target.size, Image.LANCZOS)) > 127
        tgt_pixels = tgt_lab[m_tgt]
    else:
        src_pixels = src_lab.reshape(-1, 3)
        tgt_pixels = tgt_lab.reshape(-1, 3)

    if len(src_pixels) < 100 or len(tgt_pixels) < 100:
        return target

    for ch in range(3):
        src_mean, src_std = src_pixels[:, ch].mean(), max(src_pixels[:, ch].std(), 1e-6)
        tgt_mean, tgt_std = tgt_pixels[:, ch].mean(), max(tgt_pixels[:, ch].std(), 1e-6)
        corrected = (tgt_lab[..., ch] - tgt_mean) * (src_std / tgt_std) + src_mean
        tgt_lab[..., ch] = tgt_lab[..., ch] * (1 - strength) + corrected * strength

    result_arr = lab_to_rgb(tgt_lab)
    return Image.fromarray(result_arr)


# ── Compositing (from notebook) ──────────────────────────────────────────────

def blended_composite(edited_img: Image.Image, original_img: Image.Image, mask_img: Image.Image, feather: int = 24) -> Image.Image:
    edited_img = ensure_rgb(edited_img, size=original_img.size)
    original_img = ensure_rgb(original_img)
    mask_img = ensure_mask(mask_img, size=original_img.size)
    soft_mask = mask_img.filter(ImageFilter.GaussianBlur(feather))
    return Image.composite(edited_img, original_img, soft_mask)


def composite_crop_back(
    edited_gen_img: Image.Image,
    bundle: CropBundle,
    original_img: Image.Image,
    feather: int = CROP_BLEND_FEATHER,
) -> tuple[Image.Image, Image.Image]:
    edited_crop = ensure_rgb(edited_gen_img, size=bundle.source_crop.size)
    edited_crop = match_color_lab(
        bundle.source_crop, edited_crop, mask=bundle.mask_crop, strength=0.85,
    )
    blended_crop = blended_composite(
        edited_crop, bundle.source_crop, bundle.mask_crop, feather=feather,
    )
    final = ensure_rgb(original_img).copy()
    final.paste(blended_crop, bundle.crop_box)
    return final, blended_crop


# ── Step calculation (from notebook) ─────────────────────────────────────────

def effective_denoise_steps(num_inference_steps: int, strength: float) -> int:
    return min(int(math.ceil(num_inference_steps * strength)), num_inference_steps)


def choose_safe_steps(
    base_steps: int,
    strength: float,
    min_effective_steps: int = 3,
    max_step_multiplier: float = 1.5,
) -> tuple[int, int]:
    strength = float(max(strength, 1e-6))
    base_steps = int(base_steps)
    needed_steps = int(math.ceil(min_effective_steps / strength))
    max_steps = max(base_steps, int(math.ceil(base_steps * max_step_multiplier)))
    safe_steps = min(max(base_steps, needed_steps), max_steps)
    eff_steps = effective_denoise_steps(safe_steps, strength)
    if eff_steps < 1:
        raise ValueError(
            f"effective denoise steps became {eff_steps} "
            f"(base_steps={base_steps}, safe_steps={safe_steps}, strength={strength})"
        )
    return safe_steps, eff_steps


# ── Seed strategy (from notebook) ────────────────────────────────────────────

def stable_case_seed(case_id: str, base_seed: int = 20260316) -> int:
    digest = hashlib.sha1(case_id.encode("utf-8")).hexdigest()
    offset = int(digest[:8], 16) % 100000
    return int(base_seed + offset)


# ── Prompt builders (from notebook) ──────────────────────────────────────────

def make_stage_prompt(preset: dict, stage_info: dict, extra: str = "") -> str:
    parts = [preset["identity_prefix"], stage_info["body_prompt"]]
    if extra:
        parts.append(extra)
    return ", ".join(parts)


def make_polish_prompt(preset: dict, stage_info: dict, extra: str = "") -> str:
    parts = [preset["identity_prefix"], stage_info["body_prompt"], preset["polish_suffix"]]
    if extra:
        parts.append(extra)
    return ", ".join(parts)


# ── Preset selection ─────────────────────────────────────────────────────────

def select_preset_key(gender: str, mode: TransformationMode) -> str:
    gender_prefix = "male" if gender == "male" else "female"
    if mode in (TransformationMode.CUT, TransformationMode.RECOMP):
        return f"{gender_prefix}_cut"
    return f"{gender_prefix}_bulk"


# ── Main pipeline ────────────────────────────────────────────────────────────

async def _process_single_stage(
    stage_number: int,
    preset: dict,
    backend: dict,
    crop_bundle: CropBundle,
    source_img: Image.Image,
    family_seed: int,
    run_img2img,
) -> dict | None:
    """Process one stage (shape pass + polish pass + composite). Runs independently."""
    stage_name = STAGE_MAP.get(stage_number)
    if not stage_name or stage_name not in preset["stages"]:
        logger.warning(f"Unknown stage_number {stage_number}, skipping")
        return None

    stage_info = preset["stages"][stage_name]
    t0 = time.monotonic()

    shape_prompt = make_stage_prompt(preset, stage_info)
    shape_strength = stage_info["strength"]
    shape_steps, shape_eff = choose_safe_steps(
        backend["steps"], shape_strength,
        min_effective_steps=backend["min_effective_steps"],
        max_step_multiplier=backend["max_step_multiplier"],
    )

    logger.info(
        f"[realvis:{stage_name}:shape] seed={family_seed} strength={shape_strength:.2f} "
        f"steps={shape_steps} eff={shape_eff}"
    )

    pass1_img = await run_img2img(
        image=crop_bundle.gen_source,
        prompt=shape_prompt,
        negative_prompt=preset["common_neg"],
        strength=shape_strength,
        num_inference_steps=shape_steps,
        guidance_scale=backend["cfg"],
        seed=family_seed,
    )

    final_gen = pass1_img

    sp = backend["second_pass"]
    if sp["enabled"]:
        stage_idx = stage_number - 1
        pass2_seed = family_seed + 1000 + stage_idx
        polish_prompt = make_polish_prompt(preset, stage_info)
        polish_steps, polish_eff = choose_safe_steps(
            sp["steps"], sp["strength"],
            min_effective_steps=sp["min_effective_steps"],
            max_step_multiplier=sp["max_step_multiplier"],
        )

        logger.info(
            f"[realvis:{stage_name}:polish] seed={pass2_seed} strength={sp['strength']:.2f} "
            f"steps={polish_steps} eff={polish_eff}"
        )

        final_gen = await run_img2img(
            image=pass1_img,
            prompt=polish_prompt,
            negative_prompt=preset["common_neg"],
            strength=sp["strength"],
            num_inference_steps=polish_steps,
            guidance_scale=sp["cfg"],
            seed=pass2_seed,
        )

    final_full, _ = composite_crop_back(final_gen, crop_bundle, source_img, feather=CROP_BLEND_FEATHER)

    latency_ms = round((time.monotonic() - t0) * 1000, 1)
    logger.info(f"[realvis:{stage_name}] completed in {latency_ms}ms")

    final_b64 = pil_to_base64(final_full)
    return {
        "stage_number": stage_number,
        "stage_name": stage_name,
        "image_data_uri": f"data:image/jpeg;base64,{final_b64}",
        "latency_ms": latency_ms,
    }


async def generate_realvis_journey(
    image_base64: str,
    gender: str,
    mode: TransformationMode,
    user_id: str = "",
    stage_numbers: list[int] | None = None,
) -> list[dict]:
    """Generate transformation images for all requested stages in parallel.

    Returns a list of dicts: [{stage_number, stage_name, image_data_uri, latency_ms}, ...]
    """
    import asyncio
    from .replicate_service import run_realvis_img2img

    if stage_numbers is None:
        stage_numbers = [1, 2, 3, 4]

    preset_key = select_preset_key(gender, mode)
    preset = PRESET_LIBRARY[preset_key]
    backend = LIGHTNING_BACKEND

    source_img = base64_to_pil(image_base64)
    source_img = resize_long_side(source_img, MAX_SIDE)

    mask_img = make_auto_torso_mask(source_img, preset["mask_cfg"])
    crop_bundle = build_crop_bundle(source_img, mask_img, CROP_MAX_SIDE)

    case_id = f"{user_id}_{int(time.time())}"
    family_seed = stable_case_seed(case_id)

    t_total = time.monotonic()

    raw_results = await asyncio.gather(*[
        _process_single_stage(
            sn, preset, backend, crop_bundle, source_img,
            family_seed, run_realvis_img2img,
        )
        for sn in stage_numbers
    ])

    results = [r for r in raw_results if r is not None]
    results.sort(key=lambda r: r["stage_number"])

    total_ms = round((time.monotonic() - t_total) * 1000, 1)
    logger.info(f"[realvis:journey] all {len(results)} stages completed in {total_ms}ms (parallel)")

    return results
