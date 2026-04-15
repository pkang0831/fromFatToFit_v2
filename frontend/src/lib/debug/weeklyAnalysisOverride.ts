import type { HomeSummaryResponse, WeeklyCheckinAnalysisResponse } from '@/types/api';

export const WEEKLY_ANALYSIS_OVERRIDE_STORAGE_KEY = 'devenira.demo.weeklyAnalysis';

export type DemoWeeklyScenario = 'baseline' | 'improved' | 'regressed' | 'low_confidence';

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

function isWeeklyCheckinAnalysisResponse(value: unknown): value is WeeklyCheckinAnalysisResponse {
  if (!isObject(value)) return false;
  return (
    typeof value.id === 'string' &&
    typeof value.progress_photo_id === 'string' &&
    typeof value.created_at === 'string' &&
    typeof value.taken_at === 'string' &&
    typeof value.analysis_version === 'string' &&
    isObject(value.image_quality) &&
    isObject(value.observations) &&
    isObject(value.estimated_ranges) &&
    Array.isArray(value.qualitative_summary) &&
    isObject(value.region_notes) &&
    isObject(value.derived_scores) &&
    typeof value.comparison_confidence === 'number' &&
    typeof value.weekly_status === 'string' &&
    typeof value.is_first_checkin === 'boolean' &&
    Array.isArray(value.regional_visualization) &&
    isObject(value.hologram_visualization)
  );
}

export function readWeeklyAnalysisOverride(): WeeklyCheckinAnalysisResponse | null {
  if (typeof window === 'undefined') return null;

  try {
    const raw = window.localStorage.getItem(WEEKLY_ANALYSIS_OVERRIDE_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as unknown;
    return isWeeklyCheckinAnalysisResponse(parsed) ? parsed : null;
  } catch {
    return null;
  }
}

export function writeWeeklyAnalysisOverride(value: WeeklyCheckinAnalysisResponse | null) {
  if (typeof window === 'undefined') return;

  try {
    if (value) {
      window.localStorage.setItem(WEEKLY_ANALYSIS_OVERRIDE_STORAGE_KEY, JSON.stringify(value));
    } else {
      window.localStorage.removeItem(WEEKLY_ANALYSIS_OVERRIDE_STORAGE_KEY);
    }
  } catch {
    /* noop */
  }
}

export function coerceDemoWeeklyScenario(value: string | null): DemoWeeklyScenario | null {
  if (value === 'baseline' || value === 'improved' || value === 'regressed' || value === 'low_confidence') {
    return value;
  }

  return null;
}

export function createDemoWeeklyAnalysis(
  scenario: DemoWeeklyScenario,
  summary?: HomeSummaryResponse | null,
): WeeklyCheckinAnalysisResponse {
  const lastScan = summary?.scan_summary.last_scan_date ?? '2026-03-10T14:00:00.000Z';
  const targetBodyFat = summary?.goal_summary.target_bf ?? 10;
  const progressPhotoCount = summary?.progress_summary.photo_count ?? 1;
  const photoDate = summary?.progress_summary.latest_photo_date ?? '2026-03-31T16:00:00.000Z';
  const now = new Date().toISOString();

  if (scenario === 'baseline') {
    return {
      id: 'demo-weekly-baseline',
      progress_photo_id: 'demo-progress-photo-baseline',
      previous_checkin_id: null,
      created_at: now,
      taken_at: now,
      analysis_version: 'demo-v1',
      image_quality: {
        frontal_pose: 0.92,
        body_visibility: 0.96,
        lighting_consistency: 0.82,
        pose_consistency: 0.84,
        comparison_confidence: 0.78,
        quality_flags: ['mirror_selfie'],
      },
      observations: {
        abdomen_softness: 6.8,
        lower_abdomen_protrusion: 6.3,
        ab_definition: 3.5,
        chest_definition: 5.8,
        arm_definition: 6.6,
        shoulder_roundness: 6.2,
        v_taper_visibility: 5.1,
        overall_visual_leanness: 5.0,
      },
      estimated_ranges: {
        body_fat_percent_min: 15,
        body_fat_percent_max: 19,
        body_fat_confidence: 0.58,
      },
      qualitative_summary: [
        'This is your starting weekly baseline.',
        'Use this as the reference point for future comparisons.',
      ],
      region_notes: {
        abdomen: 'Lower abdomen softness is visible in the baseline photo.',
        chest: 'Chest separation is moderate in the baseline photo.',
        arms: 'Arm definition is present but not yet sharply separated.',
        shoulders: 'Shoulder shape is visible with a mild taper.',
      },
      derived_scores: {
        leanness_score: 38.4,
        definition_score: 53.9,
        proportion_score: 56.8,
        goal_proximity_score: 45.8,
      },
      delta_from_previous: null,
      comparison_confidence: 0.78,
      weekly_status: 'stable',
      is_first_checkin: true,
      regional_visualization: [
        { region: 'abdomen', label: 'Abdomen', value: 'Baseline', note: 'Starting reference for your waist and midsection.', status: 'stable', intensity: 0.42 },
        { region: 'chest', label: 'Chest', value: 'Baseline', note: 'Upper torso definition reference.', status: 'stable', intensity: 0.34 },
        { region: 'arms', label: 'Arms', value: 'Baseline', note: 'Arm definition reference.', status: 'stable', intensity: 0.3 },
      ],
      hologram_visualization: {
        glow_intensity: 0.44,
        body_clarity: 0.55,
        pedestal_progress: 0.46,
      },
    };
  }

  if (scenario === 'improved') {
    return {
      id: 'demo-weekly-improved',
      progress_photo_id: 'demo-progress-photo-improved',
      previous_checkin_id: 'demo-weekly-prev',
      created_at: now,
      taken_at: now,
      analysis_version: 'demo-v1',
      image_quality: {
        frontal_pose: 0.92,
        body_visibility: 0.95,
        lighting_consistency: 0.81,
        pose_consistency: 0.82,
        comparison_confidence: 0.82,
        quality_flags: ['mirror_selfie'],
      },
      observations: {
        abdomen_softness: 6.2,
        lower_abdomen_protrusion: 5.8,
        ab_definition: 4.2,
        chest_definition: 6.0,
        arm_definition: 6.8,
        shoulder_roundness: 6.3,
        v_taper_visibility: 5.5,
        overall_visual_leanness: 5.5,
      },
      estimated_ranges: {
        body_fat_percent_min: 14,
        body_fat_percent_max: 18,
        body_fat_confidence: 0.61,
      },
      qualitative_summary: [
        'Midsection appears slightly tighter than the prior check-in.',
        'Arm definition appears stable.',
        'Upper torso looks marginally cleaner.',
      ],
      region_notes: {
        abdomen: 'Lower abdomen appears a bit flatter with slightly less softness.',
        chest: 'Chest separation looks mildly clearer.',
        arms: 'Arm definition looks largely unchanged.',
        shoulders: 'Shoulder shape remains stable.',
      },
      derived_scores: {
        leanness_score: 44.1,
        definition_score: 57.2,
        proportion_score: 59.6,
        goal_proximity_score: 50.3,
      },
      delta_from_previous: {
        abdomen_softness: -0.46,
        lower_abdomen_protrusion: -0.38,
        ab_definition: 0.53,
        chest_definition: 0.15,
        arm_definition: 0.15,
        overall_visual_leanness: 0.38,
        goal_proximity_score: 3.42,
      },
      comparison_confidence: 0.76,
      weekly_status: 'improved',
      is_first_checkin: false,
      regional_visualization: [
        { region: 'abdomen', label: 'Abdomen', value: 'Tighter', note: 'Midsection looks a bit cleaner than last week.', status: 'improved', intensity: 0.86 },
        { region: 'chest', label: 'Chest', value: 'Cleaner', note: 'Upper torso looks slightly more defined.', status: 'improved', intensity: 0.54 },
        { region: 'arms', label: 'Arms', value: 'Stable', note: 'Arm definition is holding steady.', status: 'stable', intensity: 0.16 },
      ],
      hologram_visualization: {
        glow_intensity: 0.46,
        body_clarity: 0.58,
        pedestal_progress: 0.5,
      },
    };
  }

  if (scenario === 'regressed') {
    return {
      id: 'demo-weekly-regressed',
      progress_photo_id: 'demo-progress-photo-regressed',
      previous_checkin_id: 'demo-weekly-prev',
      created_at: now,
      taken_at: now,
      analysis_version: 'demo-v1',
      image_quality: {
        frontal_pose: 0.9,
        body_visibility: 0.94,
        lighting_consistency: 0.79,
        pose_consistency: 0.81,
        comparison_confidence: 0.79,
        quality_flags: ['mirror_selfie'],
      },
      observations: {
        abdomen_softness: 7.4,
        lower_abdomen_protrusion: 6.9,
        ab_definition: 3.0,
        chest_definition: 5.5,
        arm_definition: 6.2,
        shoulder_roundness: 6.1,
        v_taper_visibility: 4.8,
        overall_visual_leanness: 4.6,
      },
      estimated_ranges: {
        body_fat_percent_min: 16,
        body_fat_percent_max: 20,
        body_fat_confidence: 0.59,
      },
      qualitative_summary: [
        'Midsection appears a bit softer than the prior check-in.',
        'Upper body definition looks slightly reduced.',
        'Overall leanness appears mildly lower.',
      ],
      region_notes: {
        abdomen: 'Lower abdomen looks a little fuller and less tight than before.',
        chest: 'Chest separation appears slightly reduced.',
        arms: 'Arm definition looks a touch softer.',
        shoulders: 'Shoulder shape remains mostly similar.',
      },
      derived_scores: {
        leanness_score: 33.0,
        definition_score: 50.5,
        proportion_score: 54.1,
        goal_proximity_score: 41.4,
      },
      delta_from_previous: {
        abdomen_softness: 0.46,
        lower_abdomen_protrusion: 0.46,
        ab_definition: -0.38,
        chest_definition: -0.23,
        arm_definition: -0.3,
        overall_visual_leanness: -0.3,
        goal_proximity_score: -3.34,
      },
      comparison_confidence: 0.76,
      weekly_status: 'regressed',
      is_first_checkin: false,
      regional_visualization: [
        { region: 'abdomen', label: 'Abdomen', value: 'Softer', note: 'Lower abdomen looks less tight than last week.', status: 'regressed', intensity: 0.84 },
        { region: 'chest', label: 'Chest', value: 'Less defined', note: 'Upper torso looks slightly softer.', status: 'regressed', intensity: 0.46 },
        { region: 'arms', label: 'Arms', value: 'Stable', note: 'Arm definition changed very little.', status: 'stable', intensity: 0.16 },
      ],
      hologram_visualization: {
        glow_intensity: 0.4,
        body_clarity: 0.52,
        pedestal_progress: 0.41,
      },
    };
  }

  return {
    id: 'demo-weekly-low-confidence',
    progress_photo_id: 'demo-progress-photo-low-confidence',
    previous_checkin_id: 'demo-weekly-prev',
    created_at: now,
    taken_at: now,
    analysis_version: 'demo-v1',
    image_quality: {
      frontal_pose: 0.7,
      body_visibility: 0.82,
      lighting_consistency: 0.42,
      pose_consistency: 0.47,
      comparison_confidence: 0.43,
      quality_flags: ['uneven_lighting', 'different_pose'],
    },
    observations: {
      abdomen_softness: 6.6,
      lower_abdomen_protrusion: 6.2,
      ab_definition: 3.6,
      chest_definition: 5.9,
      arm_definition: 6.4,
      shoulder_roundness: 6.1,
      v_taper_visibility: 5.1,
      overall_visual_leanness: 5.1,
    },
    estimated_ranges: {
      body_fat_percent_min: 15,
      body_fat_percent_max: 19,
      body_fat_confidence: 0.38,
    },
    qualitative_summary: [
      'This check-in is difficult to compare reliably to the prior photo.',
      'Lighting and pose differences reduce confidence.',
      'Treat this result as directional only.',
    ],
    region_notes: {
      abdomen: 'Midsection visibility is affected by changed pose and lighting.',
      chest: 'Chest definition cannot be compared confidently.',
      arms: 'Arm definition is harder to evaluate due to angle differences.',
      shoulders: 'Shoulder outline is visible but not directly comparable.',
    },
    derived_scores: {
      leanness_score: 40.1,
      definition_score: 54.8,
      proportion_score: 56.2,
      goal_proximity_score: 46.9,
    },
    delta_from_previous: {
      abdomen_softness: -0.09,
      lower_abdomen_protrusion: -0.04,
      ab_definition: 0.04,
      chest_definition: 0.04,
      arm_definition: -0.09,
      overall_visual_leanness: 0.04,
      goal_proximity_score: 0.51,
    },
    comparison_confidence: 0.43,
    weekly_status: 'low_confidence',
    is_first_checkin: false,
    regional_visualization: [
      { region: 'abdomen', label: 'Abdomen', value: 'Unclear', note: 'Pose and lighting changed too much to judge cleanly.', status: 'stable', intensity: 0.18 },
      { region: 'chest', label: 'Chest', value: 'Unclear', note: 'Upper torso comparison is not reliable this week.', status: 'stable', intensity: 0.16 },
      { region: 'arms', label: 'Arms', value: 'Unclear', note: 'Arm comparison confidence is low.', status: 'stable', intensity: 0.16 },
    ],
    hologram_visualization: {
      glow_intensity: 0.41,
      body_clarity: 0.4,
      pedestal_progress: 0.47,
    },
  };
}
