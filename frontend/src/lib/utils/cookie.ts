const isProduction = process.env.NODE_ENV === 'production';
const COOKIE_MAX_AGE = 60 * 60 * 48; // 48 hours

export function setAuthCookie(name: string, value: string) {
  const secure = isProduction ? '; Secure' : '';
  document.cookie = `${name}=${value}; path=/; max-age=${COOKIE_MAX_AGE}; SameSite=Lax${secure}`;
}

export function clearAuthCookie(name: string) {
  document.cookie = `${name}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT`;
}
