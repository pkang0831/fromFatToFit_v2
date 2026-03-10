# Smoke Test Fixture Pack

Documented image categories for manual and scripted smoke testing of the
transformation journey. Use representative photos from each category to
verify the feature handles real-world input diversity.

## Running the smoke test

```bash
cd backend
# Plan-only (no Replicate calls, instant):
python scripts/smoke_test_journey.py --plan-only

# Full generation with a real photo:
python scripts/smoke_test_journey.py --image /path/to/photo.jpg

# Full generation with synthetic test image:
python scripts/smoke_test_journey.py
```

## Fixture Categories

Collect one test photo per category. Photos should be appropriately
consented and never committed to the repository.

### Body composition scenarios

| # | Category | Description | What to verify |
|---|----------|-------------|----------------|
| F1 | Male cut | Male, ~20-30% BF, front-facing | Stage images get progressively leaner. No muscle growth. |
| F2 | Female cut | Female, ~25-35% BF, front-facing | Female-appropriate descriptors. Stages monotonic. |
| F3 | Lean bulk | Male, ~10-14% BF, wants muscle | Slight size increase. Slight softening. Not dramatic. |
| F4 | Higher BF target | Male, ~12-15% BF, target 25% | Images get softer, not more muscular. Mass-gain mode. |
| F5 | Extreme low target | Any, target < 6% male / < 14% female | Warning/clamp fires. No fantasy physique generated. |

### Photo quality / environment scenarios

| # | Category | Description | What to verify |
|---|----------|-------------|----------------|
| F6 | Loose clothing | T-shirt + sweatpants | Body shape still readable. Identity preserved. |
| F7 | Fitted clothing | Tank top + shorts or compression wear | Clearer body detail. Clothing preserved across stages. |
| F8 | Poor lighting | Dim room, harsh shadows, warm tint | Lighting preserved across stages. No color shift. |
| F9 | Mirrored selfie | Phone visible in mirror | Mirror + phone preserved. No duplication artifacts. |
| F10 | Gym mirror | Full-length gym mirror, equipment visible | Background gym equipment preserved across stages. |

## Storage

Store fixture images locally in an untracked directory:

```
backend/fixtures/journey_smoke/
  male_cut.jpg
  female_cut.jpg
  lean_bulk.jpg
  higher_bf.jpg
  extreme_low.jpg
  loose_clothing.jpg
  fitted_clothing.jpg
  poor_lighting.jpg
  mirror_selfie.jpg
  gym_mirror.jpg
```

Add `backend/fixtures/` to `.gitignore` to prevent accidental commits.
