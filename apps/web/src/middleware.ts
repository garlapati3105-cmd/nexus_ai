import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // 1. Protect all /dashboard paths
  if (pathname.startsWith("/dashboard")) {
    const allCookies = request.cookies.getAll();

    // Check for Supabase auth cookies (typically starts with sb- and ends with -auth-token)
    const hasAuthCookie = allCookies.some(
      (cookie) => cookie.name.startsWith("sb-") && cookie.name.endsWith("-auth-token")
    );

    // Also support fallback development mock cookie check
    const hasLegacyCookie = request.cookies.has("nexus_auth");

    if (!hasAuthCookie && !hasLegacyCookie) {
      const loginUrl = new URL("/login", request.url);
      return NextResponse.redirect(loginUrl);
    }
  }

  // 2. Prevent logged in users from hitting /login
  if (pathname === "/login") {
    const allCookies = request.cookies.getAll();
    const hasAuthCookie = allCookies.some(
      (cookie) => cookie.name.startsWith("sb-") && cookie.name.endsWith("-auth-token")
    );
    const hasLegacyCookie = request.cookies.has("nexus_auth");

    if (hasAuthCookie || hasLegacyCookie) {
      const dashboardUrl = new URL("/dashboard", request.url);
      return NextResponse.redirect(dashboardUrl);
    }
  }

  return NextResponse.next();
}

export const config = {
  // Match /dashboard AND /dashboard/* paths
  matcher: ["/dashboard", "/dashboard/:path*", "/login"],
};
