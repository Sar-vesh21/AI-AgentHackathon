export const oauthConfig = {
  google: {
    clientId: process.env.GOOGLE_CLIENT_ID,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    callbackURL: process.env.NODE_ENV === 'production'
      ? 'https://your-domain.com/auth/callback/google'
      : 'http://localhost:3001/auth/callback/google',
    scope: ['profile', 'email']
  },
  github: {
    clientId: process.env.GITHUB_CLIENT_ID,
    clientSecret: process.env.GITHUB_CLIENT_SECRET,
    callbackURL: process.env.NODE_ENV === 'production'
      ? 'https://your-domain.com/auth/callback/github'
      : 'http://localhost:3001/auth/callback/github',
    scope: ['user:email']
  }
}; 