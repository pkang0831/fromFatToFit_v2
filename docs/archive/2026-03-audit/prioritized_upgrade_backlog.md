# Prioritized Upgrade Backlog

## P0
| Item | Why now | Readiness | Owner | Evidence | Files / systems | Tests |
|---|---|---|---|---|---|---|
| Replace raw `progress_photos.image_base64` storage with object storage | biggest trust + storage + payload risk | Blocked by architecture | Backend, Infra | `backend/app/routers/progress_photos.py:11-37,57-123` | `progress_photos`, storage bucket, progress UI | upload/get/delete integration, storage cleanup |
| Add explicit deletion and data-retention flow | privacy promise currently false in practice | Blocked by trust/legal | Product, Backend | `frontend/src/app/(legal)/privacy/page.tsx:173-244`, `frontend/src/app/(dashboard)/profile/page.tsx:16-320` | legal pages, profile, auth/data deletion backend | deletion e2e, storage tombstone |
| Complete Stripe customer linkage and subscription reconciliation | revenue contract integrity | Blocked by architecture | Backend | `backend/app/services/payment_service.py:21-33,116-214` | payments, subscriptions, webhook handling | lifecycle webhook tests |
| Add first-party moderation gate before vendor upload | sensitive image abuse / minors / non-consensual risk | Blocked by trust/legal | Backend | `backend/app/routers/body.py`, `backend/app/routers/guest.py`, `backend/app/services/openai_service.py`, `backend/app/services/replicate_service.py` | moderation service, body/guest routes | blocked-input route tests |
| Turn weekly reminder into either a real system or remove claim | current push promise is not operational | Blocked by architecture | Product, Backend, Frontend | `frontend/src/app/(dashboard)/profile/notifications/page.tsx:10-89`, `backend/app/services/notification_service.py:174-220` | notifications UI, push infra, scheduler | subscription + delivery tests |

## P1
| Item | Why now | Readiness | Owner | Evidence | Files / systems | Tests |
|---|---|---|---|---|---|---|
| Make home state-driven around planner / check-in / challenge | strongest path to retention | Ready | Product, Frontend | `frontend/src/app/(dashboard)/home/page.tsx:25-179` | home, gap-to-goal, challenge CTA | home state rendering tests |
| Convert progress compare from placeholder to proof surface | supports 30-day retention and sharing | Ready | Backend, Frontend | `backend/app/routers/progress_photos.py:94-123`, `frontend/src/app/(dashboard)/progress/page.tsx:326-380` | compare API, progress UI | compare metric tests |
| Build public-safe share route | current share is not acquisition | Ready | Product, Frontend, Backend | `frontend/src/components/ui/ShareButtons.tsx:11-35`, `frontend/src/components/features/ShareableResultCard.tsx:48-93` | share artifact, public route | anonymous share e2e |
| Reposition monetization from output credits to outcome loop | current pitch undersells repeat value | Blocked by data | Product, Growth | `frontend/src/app/(dashboard)/upgrade/page.tsx`, `frontend/src/app/(dashboard)/home/page.tsx:155-176` | pricing copy, upgrade, landing | checkout copy QA |
| Add retention analytics beyond onboarding/body-scan/paywall | loop blindness remains | Ready | Data, Frontend | `frontend/src/lib/analytics.ts`, retention surfaces largely uninstrumented | analytics layer, home/progress/challenge/share | event contract tests |

## P2
| Item | Why now | Readiness | Owner | Evidence | Files / systems | Tests |
|---|---|---|---|---|---|---|
| Mobile parity on planner / challenge / progress | important later, not now | Blocked by architecture | Mobile | thin shell only | mobile app | parity smoke |
| New generator modes | low retention leverage | Ready | Product | current product already novelty-heavy | body/gen routes | feature-specific tests |
| More paywall experiments | premature without retention backbone | Blocked by data | Growth | current story still fragmented | landing + upgrade | funnel A/B tracking |

## Approved P0/P1 For This Pass
| Item | Status | Reason |
|---|---|---|
| Non-Google register dead-end | Implemented | activation blocker |
| Register resilience + weak-password error contract | Implemented | activation + trust |
| Notification preferences 500 fallback | Implemented | retention settings dead screen |
| Push toggle hard-disabled without VAPID key | Implemented | trust / fake promise reduction |
| Guest 18+ gate | Implemented | trust / policy |
| `activity_level` enum mismatch | Implemented | onboarding/profile save failures |
| Free-tier transformation copy mismatch | Implemented | trust / monetization integrity |
