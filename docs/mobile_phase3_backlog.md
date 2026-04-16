# Mobile Phase 3 Backlog

## Current Status

Mobile Phase 2 is now in a usable state.

Verified on a real Android device:
- Home loads
- Progress opens and falls back safely when data is incomplete
- Calorie Tracker opens
- Food Camera modal opens
- Workout opens
- Profile opens
- Paywall opens
- Weekly Body Scan opens
- Camera permission prompt appears when starting a weekly check-in

Recently fixed:
- Expo SDK upgraded to 55
- Expo Go compatibility issues resolved
- Android real-device Metro + local API loop verified with `adb reverse`
- Navigation modal back-button asset crash fixed by replacing the default image-based back icon with an `Ionicons` back button
- Major mobile UI hierarchy cleanup and screen polish across core flows

## What Is Still Not "Done"

The mobile app is no longer blocked at the runtime/navigation layer, but it is not yet fully production-complete.

Remaining work falls into four buckets:
- native purchase flow
- production mobile build pipeline
- deeper edge-case QA
- visual polish and consistency

## P0: Must-Finish Before Mobile Release

### 1. Real IAP Flow

The current paywall is entitlement-aware, but it is not a complete shipping in-app purchase experience.

Needed:
- wire `react-native-purchases` or store-native IAP to actual products
- support purchase flow, restore purchases, error handling, and pending states
- verify App Store / Play Store product IDs
- connect successful purchase state to subscription refresh and mobile UI unlocks

Success looks like:
- tapping the premium CTA opens a real purchase flow
- restore works
- entitlement refreshes without needing manual debugging

### 2. Production Build Validation

Expo Go is enough for development QA, but not for final release confidence.

Needed:
- generate an Android dev build or production build
- verify camera, image picker, fonts, icons, splash, permissions, and navigation in the built app
- validate package IDs, app name, icons, splash, and deep-link behavior

Success looks like:
- installable Android build works without Expo Go
- release candidate build matches expected branding and app behavior

### 3. Mobile Auth + Session Hardening

Core auth works, but release readiness needs a more explicit pass.

Needed:
- verify login, logout, session restore, token refresh
- verify cold start with an existing session
- verify expired or invalid auth states recover cleanly

Success looks like:
- app opens into the right authenticated state after restart
- auth failures lead to recoverable UI, not silent loops

## P1: High-Value Product Completion

### 4. Progress Data Completeness

`Progress` currently handles incomplete data safely, which is good, but the goal is to make it feel complete.

Needed:
- verify target weight onboarding path exists on mobile
- let users save/update target weight from mobile if missing
- tighten wording when partial data is shown

Success looks like:
- a new user can fully set up a usable goal path from the mobile app alone

### 5. Weekly Check-In Result Surface

The check-in entry flow is working, but the result experience can go further.

Needed:
- richer result summary after scan
- clearer visual explanation of improved/stable/regressed states
- stronger empty / first-check-in / low-confidence handling

Success looks like:
- the full weekly proof loop feels native on mobile, not just functional

### 6. Mobile UI Consistency Pass

The mobile UI is much better now, but still needs one more deliberate pass.

Needed:
- tighten typography and spacing consistency across cards
- reduce copy length where cards are still too dense
- make empty states more elegant
- ensure tab and header behaviors feel intentionally mobile-first

Success looks like:
- no obviously awkward wrapping, cramped stat cards, or mixed visual tone

## P2: Reliability and Polish

### 7. Error Surface Audit

Needed:
- verify all main flows show actionable errors
- avoid dead-end spinners
- unify retry language across screens

Focus screens:
- Progress
- Calorie Tracker
- Food Camera
- Weekly Body Scan
- Paywall
- Profile refresh

### 8. Camera and Media Edge Cases

Needed:
- deny camera permission
- deny photo library permission
- select unsupported image
- cancel camera
- cancel gallery picker
- retry after failure

Success looks like:
- every branch returns users to a stable screen with a clear next action

### 9. Performance Pass

Needed:
- measure cold start in build, not just Expo Go
- measure heavy screens on device:
  - Progress
  - Body Scan
  - Food Camera
- reduce layout jank during loading

## Suggested Execution Order

1. Production build setup
2. Real IAP wiring
3. Auth/session hardening
4. Progress goal-path completion
5. Weekly check-in result polish
6. Full UI consistency pass
7. Error/permission edge-case QA
8. Final release candidate smoke QA

## Release Gate For Mobile

Before calling mobile "ready", all of these should be true:
- real-device build works without Expo Go
- purchase flow works end to end
- login/session persistence is stable
- weekly check-in works from capture to result
- progress path is understandable for new users
- error states are visible and recoverable
- final branding and icons are correct

## Notes

This backlog assumes:
- web production is already live
- mobile Phase 2 code is merged
- the next bottlenecks are no longer "can the app open?" but "can it ship like a real product?"
