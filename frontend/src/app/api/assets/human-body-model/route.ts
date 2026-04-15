import { readFile } from 'fs/promises';
import path from 'path';

const HUMAN_BODY_MODEL_CANDIDATES = [
  path.resolve(process.cwd(), 'human-converted.glb'),
  path.resolve(process.cwd(), '..', 'human-converted.glb'),
  path.resolve(process.cwd(), 'public', 'assets', 'human-converted.glb'),
];

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET() {
  for (const candidate of HUMAN_BODY_MODEL_CANDIDATES) {
    try {
      const buffer = await readFile(candidate);

      return new Response(buffer, {
        headers: {
          'Content-Type': 'model/gltf-binary',
          'Cache-Control': 'public, max-age=3600',
        },
      });
    } catch {
      // Try next candidate.
    }
  }

  return new Response(
    `Missing required asset. Looked for: ${HUMAN_BODY_MODEL_CANDIDATES.join(', ')}`,
    {
      status: 404,
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Cache-Control': 'no-store',
      },
    },
  );
}
