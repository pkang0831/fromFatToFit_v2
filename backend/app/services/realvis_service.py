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
            "same bathroom or room, same camera angle, same pose, same phone pose, "
            "photorealistic, realistic skin texture, natural body proportions"
        ),
        "polish_suffix": (
            "preserve identity, preserve pose, preserve background, preserve chest size, "
            "preserve shoulder size, preserve arm size, keep changes focused on abdomen and waist, "
            "clean natural skin texture, realistic details"
        ),
        "common_neg": (
            "different person, changed face, changed hair, changed background, changed pose, "
            "oversized chest, oversized shoulders, oversized arms, smaller chest, smaller shoulders, "
            "extreme v taper, tiny waist, fake abs, etched abs, overly symmetrical abs, steroid look, "
            "cartoon, illustration, blurry, low quality, bad anatomy, deformed"
        ),
        "stages": {
            "2_weeks": {
                "body_prompt": (
                    "noticeably flatter lower stomach, early waist tightening visible, "
                    "smoother midsection, beginning of torso definition, natural early cut progress"
                ),
                "strength": 0.22,
            },
            "1_month": {
                "body_prompt": (
                    "visibly leaner midsection, clear waist reduction, emerging upper ab lines, "
                    "more defined torso shape, chest and shoulders maintained, realistic mid-cut progress"
                ),
                "strength": 0.30,
            },
            "2_months": {
                "body_prompt": (
                    "lean athletic stomach, visible natural ab definition, clearly narrower waist, "
                    "oblique lines beginning to show, athletic torso shape, realistic late-stage cut"
                ),
                "strength": 0.38,
            },
            "goal": {
                "body_prompt": (
                    "defined natural abs, lean athletic abdomen, visible defined obliques, "
                    "noticeably leaner waist, same chest size, same shoulders, "
                    "realistic motivational transformation, not extreme"
                ),
                "strength": 0.46,
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
            "same room, same camera angle, same pose, same phone pose, photorealistic, "
            "realistic skin texture, natural body proportions"
        ),
        "polish_suffix": (
            "preserve identity, preserve pose, preserve background, maintain realistic proportions, "
            "natural lean-bulk progress, avoid exaggerated bodybuilder changes"
        ),
        "common_neg": (
            "different person, changed face, changed pose, changed background, bodybuilder, "
            "massive chest, massive shoulders, extreme arms, steroid look, fake muscle striations, "
            "cartoon, illustration, blurry, low quality, bad anatomy, deformed"
        ),
        "stages": {
            "2_weeks": {
                "body_prompt": (
                    "noticeably fuller upper torso, visible chest and shoulder fullness, "
                    "firmer arm definition, natural early lean bulk progress"
                ),
                "strength": 0.22,
            },
            "1_month": {
                "body_prompt": (
                    "clearly fuller chest, visibly broader shoulders, defined arm fullness, "
                    "same waist, athletic mid lean bulk progress"
                ),
                "strength": 0.30,
            },
            "2_months": {
                "body_prompt": (
                    "athletically built chest and shoulders, thicker stronger arms, "
                    "visible upper body mass gain, same waist, realistic late lean bulk progress"
                ),
                "strength": 0.38,
            },
            "goal": {
                "body_prompt": (
                    "noticeably stronger athletic upper torso, full muscular chest, broad shoulders, "
                    "well-defined arms, natural lean bulk result, not extreme"
                ),
                "strength": 0.46,
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
            "same room, same camera angle, same pose, same phone pose, photorealistic, "
            "realistic skin texture, natural body proportions"
        ),
        "polish_suffix": (
            "preserve identity, preserve pose, preserve background, preserve bust shape, "
            "keep changes focused on waist and abdomen, realistic toned result, no exaggerated hourglass"
        ),
        "common_neg": (
            "different person, changed face, changed pose, changed background, altered bust shape, "
            "tiny waist, exaggerated hourglass, fake abs, bodybuilder, plastic skin, cartoon, "
            "illustration, blurry, low quality, bad anatomy, deformed"
        ),
        "stages": {
            "2_weeks": {
                "body_prompt": (
                    "noticeably flatter lower stomach, early waist tightening visible, "
                    "smoother midsection, bust and shoulders unchanged, natural early cut progress"
                ),
                "strength": 0.20,
            },
            "1_month": {
                "body_prompt": (
                    "visibly flatter stomach, clear waist reduction, emerging torso tone, "
                    "bust unchanged, realistic mid-cut progress"
                ),
                "strength": 0.28,
            },
            "2_months": {
                "body_prompt": (
                    "lean toned waist, visible ab definition beginning, clearly more athletic midsection, "
                    "realistic late-stage cut progress"
                ),
                "strength": 0.34,
            },
            "goal": {
                "body_prompt": (
                    "lean athletic waist, defined natural ab outline, toned athletic midsection, "
                    "realistic motivational cut result, not extreme"
                ),
                "strength": 0.40,
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
            "same room, same camera angle, same pose, same phone pose, photorealistic, "
            "realistic skin texture, natural body proportions"
        ),
        "polish_suffix": (
            "preserve identity, preserve pose, preserve background, preserve bust shape, "
            "show realistic athletic muscle gain, avoid exaggerated bodybuilding look"
        ),
        "common_neg": (
            "different person, changed face, changed pose, changed background, altered bust shape, "
            "bodybuilder, oversized shoulders, oversized arms, fake striations, steroid look, "
            "cartoon, illustration, blurry, low quality, bad anatomy, deformed"
        ),
        "stages": {
            "2_weeks": {
                "body_prompt": (
                    "noticeably firmer upper torso, visible shoulder and arm tone, "
                    "same waist, natural early lean bulk progress"
                ),
                "strength": 0.20,
            },
            "1_month": {
                "body_prompt": (
                    "visibly more athletic upper torso, clear shoulder definition, firmer toned arms, "
                    "same waist, realistic mid lean bulk progress"
                ),
                "strength": 0.28,
            },
            "2_months": {
                "body_prompt": (
                    "athletically stronger shoulders and arms, fuller defined upper torso, "
                    "visible muscle tone, natural female late lean bulk progress"
                ),
                "strength": 0.34,
            },
            "goal": {
                "body_prompt": (
                    "clearly stronger athletic upper torso, defined toned shoulders and arms, "
                    "athletic feminine physique, realistic female lean bulk result, not extreme"
                ),
                "strength": 0.40,
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

async def generate_realvis_journey(
    image_base64: str,
    gender: str,
    mode: TransformationMode,
    user_id: str = "",
    stage_numbers: list[int] | None = None,
) -> list[dict]:
    """Generate transformation images for all requested stages.

    Returns a list of dicts: [{stage_number, stage_name, image_data_uri, latency_ms}, ...]
    """
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

    results: list[dict] = []

    for stage_number in stage_numbers:
        stage_name = STAGE_MAP.get(stage_number)
        if not stage_name or stage_name not in preset["stages"]:
            logger.warning(f"Unknown stage_number {stage_number}, skipping")
            continue

        stage_info = preset["stages"][stage_name]
        t0 = time.monotonic()

        # Pass 1: shape
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

        pass1_img = await run_realvis_img2img(
            image=crop_bundle.gen_source,
            prompt=shape_prompt,
            negative_prompt=preset["common_neg"],
            strength=shape_strength,
            num_inference_steps=shape_steps,
            guidance_scale=backend["cfg"],
            seed=family_seed,
        )

        final_gen = pass1_img

        # Pass 2: polish
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

            final_gen = await run_realvis_img2img(
                image=pass1_img,
                prompt=polish_prompt,
                negative_prompt=preset["common_neg"],
                strength=sp["strength"],
                num_inference_steps=polish_steps,
                guidance_scale=sp["cfg"],
                seed=pass2_seed,
            )

        # Composite back into original
        final_full, _ = composite_crop_back(final_gen, crop_bundle, source_img, feather=CROP_BLEND_FEATHER)

        latency_ms = round((time.monotonic() - t0) * 1000, 1)
        logger.info(f"[realvis:{stage_name}] completed in {latency_ms}ms")

        final_b64 = pil_to_base64(final_full)
        results.append({
            "stage_number": stage_number,
            "stage_name": stage_name,
            "image_data_uri": f"data:image/jpeg;base64,{final_b64}",
            "latency_ms": latency_ms,
        })

    return results
