# Transformation Benchmark Workflow

This benchmark flow now validates the production CUT ROI 2-pass pipeline
instead of the older RealVis XL batch transformation flow.

The notebook at
[notebook_c_realvis_benchmark_batch.ipynb](/Users/RBIPK031/.cursor/worktrees/fromFatToFit/hhu/colab_notebook/notebook_c_realvis_benchmark_batch.ipynb)
benchmarks the same path that produced the good `sample_image.jpg`
result:

1. deterministic CUT warp
2. pass 1 seam repair
3. pass 2 torso texture refine

## Goal

- Validate whether the production CUT pipeline gives the same identity-
  preserving UX on many valid user photos, not just on one successful sample.
- Measure safety, preservation, and torso refinement quality on photos that
  already pass your product intake gate.
- Produce structured outputs for manual review before rollout.

## Current scope

- Best fit: shirtless upper-body male photos
- Best fit: mirror selfies or direct front torso photos
- Best fit: decent lighting and clear torso visibility
- This notebook uses the current production CUT prompts and masks
- This notebook does not implement a separate ROI bulk / recomp path yet

If a manifest row is tagged as `bulk`, the notebook still runs the CUT
production path and treats that row as a stress test, not a real bulk
benchmark.

## Files

- Benchmark case manifest:
  [benchmark_cases.template.csv](/Users/RBIPK031/.cursor/worktrees/fromFatToFit/hhu/colab_notebook/benchmark_cases.template.csv)
- Manual scoring template:
  [benchmark_scores.template.csv](/Users/RBIPK031/.cursor/worktrees/fromFatToFit/hhu/colab_notebook/benchmark_scores.template.csv)
- Batch Colab notebook:
  [notebook_c_realvis_benchmark_batch.ipynb](/Users/RBIPK031/.cursor/worktrees/fromFatToFit/hhu/colab_notebook/notebook_c_realvis_benchmark_batch.ipynb)

## Recommended cohort

Start with 8 to 24 subjects that match your production intake criteria.

- Prefer shirtless upper-body photos
- Prefer mirror selfie or front torso framing
- Include soft / overweight cases
- Include lean / skinny-fat cases
- Vary lighting, skin tone, and phone/background context

The point is not to cover every internet photo. The point is to cover
the valid photo domain your app will actually accept.

## Manifest columns

Required in practice:

- `case_id`
- `enabled`
- `image_uri`

Useful metadata:

- `goal_mode`
- `body_type_start`
- `preset_key`
- `ethnicity_if_known`
- `pose_type`
- `lighting_quality`
- `crop_type`
- `extra_prompt`
- `extra_negative_prompt`
- `notes`

`image_uri` may be:

- a local Colab path
- a Google Drive path
- an HTTP/HTTPS URL

The notebook records metadata columns into outputs, but the current
production CUT benchmark does not inject manifest prompt columns into the
diffusion prompts. It uses the backend production prompts directly.

## Presets

The notebook uses CUT warp/refine strength presets:

- `mild`
- `medium`
- `strong`

You can set a global default in the notebook config cell and optionally
override per row with columns such as `refine_preset`, `cut_preset`, or
`preset` if you add them to the manifest.

## Output layout

Each benchmark run writes to a timestamped folder under the notebook's
configured `OUTPUT_ROOT`, for example:

```text
/content/drive/MyDrive/SD/cut_refine_benchmark_runs/run_YYYYMMDD_HHMMSS/
```

Expected artifacts:

- `manifest_snapshot.csv`
- `manifest_snapshot.json`
- `materialized_cases.csv`
- `run_meta.json`
- `all_metrics.json`
- `case_summary.csv`
- `review_template.csv`
- `summary_stats.json`
- `overall_summary_strip.png`
- `report.html`
- one folder per case under `test_cases/`
- one folder per case under `eval/`

Per-case eval folders include:

- original image
- warped image
- seam mask
- torso refine mask
- pass 1 output
- final refined output
- comparison grid
- pass 2 debug overlays

## Manual review

Review each case for:

- same-person feel
- silhouette preservation
- abdomen improvement quality
- fake texture / fake abs
- shoulder or arm leakage
- background or phone drift

Suggested scoring columns:

- `same_person_score`
- `silhouette_preservation_score`
- `torso_texture_score`
- `artifact_score`
- `overall_score`
- `production_pass`
- `notes`

Useful failure tags:

- `identity_drift`
- `shoulder_leak`
- `arm_leak`
- `phone_changed`
- `fake_abs`
- `plastic_skin`
- `lower_belly_regression`
- `background_drift`

## Practical workflow

1. Put the benchmark export in Drive and set `BENCHMARK_MANIFEST_PATH`
   and `IMAGE_ROOT`.
2. Point the notebook at the local SD15 inpainting model if available.
3. Run the notebook in Colab.
4. Review `case_summary.csv`, `overall_summary_strip.png`, and
   `report.html`.
5. Fill in `review_template.csv`.
6. Treat repeated failure patterns as product blockers, not isolated noise.

## Product guidance

Do not treat one strong sample as production proof.

Treat the CUT pipeline as ready only when:

- valid user-photo cases repeatedly preserve identity and silhouette
- protect-region leakage stays low
- lower-belly regression is rare
- artifact clusters are understood and acceptable
- the benchmark reflects the same intake gate you use in production
