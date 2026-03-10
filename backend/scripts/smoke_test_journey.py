#!/usr/bin/env python3
"""Staging-only smoke test for the transformation journey pipeline.

Runs 3-5 representative scenarios against the *real* Replicate provider
to verify end-to-end image generation without touching production billing.

Usage:
    # From backend/ directory, with .env loaded:
    python scripts/smoke_test_journey.py [--image path/to/photo.jpg]

    If --image is omitted, generates a tiny 100x150 solid-blue test image.

Requirements:
    - REPLICATE_API_KEY must be set in environment or .env
    - This script does NOT call the API server — it calls the planner
      and replicate service directly, bypassing auth/credits.

Output:
    For each scenario, prints:
    - mode, stage count, timeline
    - per-stage latency
    - whether each stage image was generated
    - total wall-clock time
    - warnings (if any)
"""

import asyncio
import base64
import io
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.transformation_planner import build_plan
from app.services.transformation_types import MuscleGainSpec
from app.services.transformation_prompts import render_stage_prompt


def _make_test_image_b64() -> str:
    """Create a minimal JPEG test image (solid blue, 100x150)."""
    from PIL import Image
    img = Image.new("RGB", (100, 150), color=(70, 130, 180))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=80)
    return base64.b64encode(buf.getvalue()).decode()


SCENARIOS = [
    {
        "name": "Male cut (25% -> 12%)",
        "current_bf": 25, "target_bf": 12, "gender": "male",
        "weight_kg": 80, "height_cm": 178, "age": 30,
    },
    {
        "name": "Female cut (30% -> 22%)",
        "current_bf": 30, "target_bf": 22, "gender": "female",
        "weight_kg": 65, "height_cm": 165, "age": 28,
    },
    {
        "name": "Lean bulk (12% -> 15%, +3kg muscle)",
        "current_bf": 12, "target_bf": 15, "gender": "male",
        "weight_kg": 72, "muscle_gains": MuscleGainSpec(chest_kg=1, shoulders_kg=1, arms_kg=1),
    },
    {
        "name": "Higher body-fat target (15% -> 25%)",
        "current_bf": 15, "target_bf": 25, "gender": "male",
        "weight_kg": 75,
    },
    {
        "name": "Extreme low target (25% -> 3%, expect clamp)",
        "current_bf": 25, "target_bf": 3, "gender": "male",
    },
]


def run_plan_only(scenario: dict) -> dict:
    """Run the planner without image generation."""
    plan = build_plan(
        current_bf=scenario["current_bf"],
        target_bf=scenario["target_bf"],
        gender=scenario["gender"],
        muscle_gains=scenario.get("muscle_gains"),
        weight_kg=scenario.get("weight_kg"),
        height_cm=scenario.get("height_cm"),
        age=scenario.get("age"),
    )
    return {
        "mode": plan.mode.value,
        "target_bf_effective": plan.target_bf,
        "clamped": plan.target_bf_clamped,
        "total_weeks": plan.total_weeks,
        "stage_count": len(plan.stages),
        "warnings": plan.warnings,
        "stages": [
            {"num": s.stage_number, "bf": s.bf_pct, "week": s.week, "label": s.label}
            for s in plan.stages
        ],
    }


async def run_with_images(scenario: dict, image_b64: str) -> dict:
    """Run planner + Replicate image generation."""
    from app.services import replicate_service

    plan = build_plan(
        current_bf=scenario["current_bf"],
        target_bf=scenario["target_bf"],
        gender=scenario["gender"],
        muscle_gains=scenario.get("muscle_gains"),
        weight_kg=scenario.get("weight_kg"),
        height_cm=scenario.get("height_cm"),
        age=scenario.get("age"),
    )

    prompts = [
        (s.stage_number, s.prompt) for s in plan.stages if s.stage_number > 0 and s.prompt
    ]

    t0 = time.monotonic()
    results = await replicate_service.generate_journey_images(image_b64, prompts)
    total_ms = round((time.monotonic() - t0) * 1000, 1)

    return {
        "mode": plan.mode.value,
        "total_weeks": plan.total_weeks,
        "warnings": plan.warnings,
        "stages_requested": len(prompts),
        "stages_succeeded": len(results),
        "stage_latencies_ms": {r["stage_number"]: r.get("latency_ms", 0) for r in results},
        "total_generation_ms": total_ms,
        "image_sizes_kb": {r["stage_number"]: round(len(r["image_data_uri"]) * 3 / 4 / 1024, 1) for r in results},
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Smoke test transformation journey")
    parser.add_argument("--image", type=str, help="Path to a body photo JPEG")
    parser.add_argument("--plan-only", action="store_true", help="Skip image generation")
    args = parser.parse_args()

    if args.image:
        with open(args.image, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode()
        print(f"Using image: {args.image}")
    else:
        image_b64 = _make_test_image_b64()
        print("Using generated test image (solid blue 100x150)")

    print(f"\nRunning {len(SCENARIOS)} scenarios...\n")
    print("=" * 70)

    for sc in SCENARIOS:
        print(f"\n--- {sc['name']} ---")

        if args.plan_only:
            result = run_plan_only(sc)
            print(json.dumps(result, indent=2))
        else:
            try:
                result = asyncio.run(run_with_images(sc, image_b64))
                print(json.dumps(result, indent=2))
            except Exception as e:
                print(f"  FAILED: {e}")

        print()

    print("=" * 70)
    print("Smoke test complete.")


if __name__ == "__main__":
    main()
