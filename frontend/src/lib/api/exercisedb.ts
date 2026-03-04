const BASE_URL = 'https://exercisedb-api.vercel.app/api/v1';

interface ExerciseDBResult {
  exerciseId: string;
  name: string;
  gifUrl: string;
  targetMuscles: string[];
  bodyParts: string[];
  equipments: string[];
  secondaryMuscles: string[];
  instructions: string[];
}

interface ExerciseDBResponse {
  success: boolean;
  data: ExerciseDBResult[];
}

const gifCache = new Map<string, string | null>();

const NO_GIF_EXERCISES = new Set([
  'tennis', 'basketball', 'soccer/football', 'swimming laps',
  'outdoor cycling', 'outdoor running', 'brisk walking',
  'zumba', 'dance cardio', 'spin class', 'stair running',
  'sprint intervals', 'incline walking', 'treadmill running',
  'aqua aerobics', 'step aerobics',
]);

function computeSimilarity(a: string, b: string): number {
  const wordsA = a.toLowerCase().split(/\s+/);
  const wordsB = b.toLowerCase().split(/\s+/);
  let matches = 0;
  for (const w of wordsA) {
    if (wordsB.some(wb => wb.includes(w) || w.includes(wb))) matches++;
  }
  return matches / Math.max(wordsA.length, 1);
}

export async function fetchExerciseGif(exerciseName: string): Promise<string | null> {
  const cacheKey = exerciseName.toLowerCase().trim();

  if (gifCache.has(cacheKey)) {
    return gifCache.get(cacheKey) ?? null;
  }

  if (NO_GIF_EXERCISES.has(cacheKey)) {
    gifCache.set(cacheKey, null);
    return null;
  }

  try {
    const res = await fetch(
      `${BASE_URL}/exercises/search?q=${encodeURIComponent(exerciseName)}&limit=5&threshold=0.3`,
      { signal: AbortSignal.timeout(5000) }
    );

    if (!res.ok) {
      gifCache.set(cacheKey, null);
      return null;
    }

    const json: ExerciseDBResponse = await res.json();

    if (!json.success || !json.data || json.data.length === 0) {
      gifCache.set(cacheKey, null);
      return null;
    }

    const exactMatch = json.data.find(
      d => d.name.toLowerCase() === cacheKey
    );

    if (exactMatch) {
      gifCache.set(cacheKey, exactMatch.gifUrl);
      return exactMatch.gifUrl;
    }

    const scored = json.data
      .map(d => ({ ...d, score: computeSimilarity(cacheKey, d.name) }))
      .filter(d => d.score >= 0.5)
      .sort((a, b) => b.score - a.score);

    if (scored.length === 0) {
      gifCache.set(cacheKey, null);
      return null;
    }

    const gifUrl = scored[0].gifUrl || null;
    gifCache.set(cacheKey, gifUrl);
    return gifUrl;
  } catch {
    gifCache.set(cacheKey, null);
    return null;
  }
}
