import 'next-auth';

declare module 'next-auth' {
  interface Session {
    accessToken?: string;
    user: {
      email: string;
      id: string;
    };
  }

  interface User {
    id: string;
    email: string;
    accessToken: string;
  }
}