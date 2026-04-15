# Production Preflight Checklist

## Release Gate

- `frontend npm run lint`
- `frontend npm run build`
- `PYTHONPATH=backend pytest backend/tests -q`
- Verify frontend boots at `/login`, `/home`, `/progress`
- Verify backend health at `/health`

## Environment

- `OPENAI_API_KEY`
- `OPENAI_BODY_CHECKIN_MODEL`
- `WEEKLY_CHECKIN_ANALYSIS_VERSION`
- `NEXT_PUBLIC_API_URL`
- `NEXT_PUBLIC_WEB_PUSH_PUBLIC_KEY` if push is intended to be live
- All Supabase URL / anon / service-role secrets
- Any storage bucket env used for uploads and proof assets

## Database / Supabase

- Apply [supabase_weekly_checkins.sql](/Users/RBIPK031/.cursor/worktrees/fromFatToFit/hhu/backend/supabase_weekly_checkins.sql)
- Confirm `weekly_checkins` table exists in production
- Confirm RLS policy is active and scoped to `auth.uid() = user_id`
- Confirm `progress_photos` relation exists and matches FK assumptions
- Confirm upload/storage buckets exist and are writable by app flows

## Feature Flags / Demo Safety

- `NEXT_PUBLIC_ENABLE_WEEKLY_DEMO` must be unset or `false` in production
- Confirm browser `localStorage` demo overrides are ignored in production builds
- Confirm no `demoWeekly` links remain in user-facing navigation

## Weekly Check-In Flow

- Upload first check-in photo works end to end
- Structured OpenAI analysis returns schema-valid payload
- Observation normalization stores:
  - `image_quality`
  - `observations`
  - `estimated_ranges`
  - `region_notes`
- Derived scores compute and save:
  - `leanness_score`
  - `definition_score`
  - `proportion_score`
  - `goal_proximity_score`
- Second check-in computes delta and status:
  - `improved`
  - `stable`
  - `regressed`
  - `low_confidence`

## Dashboard / UX

- Home dashboard loads without demo data
- Hologram loads real human mesh
- Annotation cards do not cover the body excessively
- Language switch updates shell + dashboard copy
- Error states show retry actions instead of silent failure

## Progress / Performance

- `/progress` first paint is acceptable on production infra
- Check `Server-Timing` header on `/weight/projection`
- Watch backend logs for `goal_projection_timing`
- Confirm projection cache hit path works on repeat visits
- Confirm food/workout logging invalidates calorie-balance cache

## Payments / Limits

- Upgrade page loads credits correctly
- Food camera scan limits behave correctly for free vs premium
- Purchase verification updates entitlement state

## Notifications

- Notifications page loads and saves preferences
- Weekly proof reminder status reads correctly
- Push notifications are either fully configured or clearly disabled

## Known Non-Blockers

- Some older pages still contain legacy copy that can be polished later
- Deprecation warnings remain in a few backend tests but are not release blockers
