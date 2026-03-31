export const ACCOUNT_DELETION_CONFIRM_PHRASE = 'DELETE';

export const ACCOUNT_DELETION_DELETED_IMMEDIATELY = [
  'Your Denevira auth account',
  'Profile, onboarding, goals, scans, chat history, food/workout/weight logs, streaks, challenge data, and notification settings stored in Denevira',
  'Stored progress photo files in Denevira private storage and their database rows',
];

export const ACCOUNT_DELETION_RETAINED_OUTSIDE_APP = [
  'Stripe, RevenueCat, Apple, or Google may keep billing records under their own policies',
  'Third-party AI providers may keep submitted inputs under their own retention policies',
  'Operational logs may retain limited metadata for security and debugging',
];

export const ACCOUNT_DELETION_BLOCKING_REQUIREMENT =
  'If you still have an active paid subscription, cancel billing first. Account deletion in Denevira does not cancel Stripe or app-store billing.';
