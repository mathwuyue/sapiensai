import type { NextAuthConfig } from 'next-auth';

export const authConfig = {
  callbacks: {
    authorized( {auth, request: {nextUrl} }) {
      const isLoggedIn = !!auth?.user;
      const isOnDashboard = nextUrl.pathname.startsWith('/dashboard');
      if (isOnDashboard) {
        if (isLoggedIn) return true;
        return false;
      } else if (isLoggedIn) {
        console.log("Redirecting to dashboard");
        return Response.redirect(new URL('/dashboard', nextUrl));
      }
      return true;
    },
  },
  providers: [],
  pages: {
    signIn: '/login',
  },
} satisfies NextAuthConfig;