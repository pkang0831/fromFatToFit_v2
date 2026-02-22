import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token')?.value;
  const pathname = request.nextUrl.pathname;
  
  const isAuthPage = pathname.startsWith('/login') || pathname.startsWith('/register') || pathname.startsWith('/auth/callback');
  const isOnboarding = pathname.startsWith('/onboarding');
  const isDashboardPage = pathname.startsWith('/home') ||
                        pathname.startsWith('/calories') ||
                        pathname.startsWith('/food-camera') ||
                        pathname.startsWith('/workouts') ||
                        pathname.startsWith('/body-scan') ||
                        pathname.startsWith('/profile') ||
                        pathname.startsWith('/progress') ||
                        pathname.startsWith('/upgrade') ||
                        pathname.startsWith('/chat') ||
                        pathname.startsWith('/fasting');

  // Handle root path: authenticated users go to dashboard, others see landing page
  if (pathname === '/') {
    if (token) {
      return NextResponse.redirect(new URL('/home', request.url));
    }
    return NextResponse.next();
  }

  // Onboarding is accessible by authenticated users, not by unauthenticated
  if (isOnboarding) {
    if (!token) return NextResponse.redirect(new URL('/login', request.url));
    return NextResponse.next();
  }

  // Redirect authenticated users away from auth pages
  if (isAuthPage && token) {
    return NextResponse.redirect(new URL('/home', request.url));
  }

  // Redirect unauthenticated users away from dashboard pages
  if (isDashboardPage && !token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
