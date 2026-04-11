import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token')?.value;
  const pathname = request.nextUrl.pathname;
  
  const isAuthPage = pathname.startsWith('/login') || pathname.startsWith('/register') || pathname.startsWith('/try');
  const DASHBOARD_PREFIXES = [
    '/home', '/calories', '/food-camera', '/workouts', '/fasting',
    '/body-scan', '/beauty-scan', '/fashion', '/goal-planner', '/chat',
    '/profile', '/progress', '/upgrade', '/onboarding',
    '/mask-editor', '/body-editor', '/challenge', '/deadline',
  ];
  const isDashboardPage = DASHBOARD_PREFIXES.some((p) => pathname.startsWith(p));

  // Handle root path — show landing page to unauthenticated, redirect to dashboard for authenticated
  if (pathname === '/') {
    if (token) {
      return NextResponse.redirect(new URL('/home', request.url));
    }
    return NextResponse.next();
  }

  // Redirect authenticated users away from auth pages
  if (isAuthPage && token) {
    return NextResponse.redirect(new URL('/home', request.url));
  }

  // Redirect unauthenticated users away from dashboard pages
  if (isDashboardPage && !token) {
    const loginUrl = new URL('/login', request.url);
    const nextPath = `${pathname}${request.nextUrl.search}`;
    if (nextPath && nextPath !== '/login') {
      loginUrl.searchParams.set('next', nextPath);
    }
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
