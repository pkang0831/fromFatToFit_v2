import { AxiosError } from 'axios';

/** Flattens FastAPI `detail` (string or structured body_photo_quality object). */
export function formatApiError(err: unknown): string {
  if (err instanceof AxiosError) {
    const isNetwork =
      err.code === 'ERR_NETWORK' ||
      err.message === 'Network Error' ||
      (!err.response && err.request);
    if (isNetwork) {
      return (
        'Cannot reach the API. Start the backend (port 8000), set NEXT_PUBLIC_API_URL in the frontend, ' +
        'and open the app at the same host you allow in CORS (use either localhost or 127.0.0.1 consistently).'
      );
    }
    const d = err.response?.data as { detail?: unknown } | undefined;
    const detail = d?.detail;
    if (typeof detail === 'string') return detail;
    if (detail && typeof detail === 'object' && 'messages' in detail) {
      const m = (detail as { messages: string[] }).messages;
      if (Array.isArray(m) && m.length) return m.join(' ');
    }
  }
  if (err instanceof Error) return err.message;
  return 'Something went wrong. Please try again.';
}
