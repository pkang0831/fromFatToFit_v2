export const SITE_ORIGIN = 'https://www.devenira.com';
export const MEDIA_ORIGIN = SITE_ORIGIN;

export function absoluteUrl(path = '') {
  if (!path) return SITE_ORIGIN;
  return `${SITE_ORIGIN}${path.startsWith('/') ? path : `/${path}`}`;
}
