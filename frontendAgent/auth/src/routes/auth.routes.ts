import { Router } from 'express';
import { verifyToken } from '../middleware/auth.middleware';
import jwt from 'jsonwebtoken';
import fetch from 'node-fetch';


const router: ReturnType<typeof Router> = Router();

// Initial OAuth routes
router.get('/google', (req, res) => {
  const googleAuthUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
    `client_id=${process.env.GOOGLE_CLIENT_ID}` +
    `&redirect_uri=${process.env.NODE_ENV === 'production'
      ? 'https://your-domain.com/auth/callback/google'
      : 'http://localhost:3001/auth/callback/google'}` +
    `&response_type=code` +
    `&scope=email profile` +
    `&access_type=offline` +
    `&prompt=consent`;
  
  res.redirect(googleAuthUrl);
});

router.get('/github', (req, res) => {
  const githubAuthUrl = `https://github.com/login/oauth/authorize?` +
    `client_id=${process.env.GITHUB_CLIENT_ID}` +
    `&redirect_uri=${process.env.NODE_ENV === 'production'
      ? 'https://your-domain.com/auth/callback/github'
      : 'http://localhost:3001/auth/callback/github'}` +
    `&scope=user:email`;
  
  res.redirect(githubAuthUrl);
});

// OAuth callback routes
router.get('/callback/google', async (req, res) => {
  const { code } = req.query;
  
  try {
    // 1. Exchange the code for tokens
    const tokenResponse = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        code: code as string,
        client_id: process.env.GOOGLE_CLIENT_ID!,
        client_secret: process.env.GOOGLE_CLIENT_SECRET!,
        redirect_uri: process.env.NODE_ENV === 'production'
          ? 'https://your-domain.com/auth/callback/google'
          : 'http://localhost:3001/auth/callback/google',
        grant_type: 'authorization_code',
      }),
    });

    const tokens = await tokenResponse.json();

    console.log(tokens);

    // 2. Get user info using the access token
    const userResponse = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
      headers: {
        Authorization: `Bearer ${tokens.access_token}`,
      },
    });
    const userData = await userResponse.json();

    console.log(userData);

    // 3. Create our own JWT token
    const ourToken = jwt.sign(
      {
        id: userData.id,
        email: userData.email,
        name: userData.name,
        picture: userData.picture,
      },
      process.env.JWT_SECRET || 'your-secret-key',
      { expiresIn: '1d' }
    );

    console.log(process.env.JWT_SECRET);
    console.log(ourToken);

    // 4. Redirect to frontend with our token
    res.redirect(`http://localhost:5173/login?token=${ourToken}`);
  } catch (error) {
    console.error('OAuth callback error:', error);
    res.redirect('http://localhost:5173/login?error=oauth_error');
  }
});

router.get('/callback/github', async (req, res) => {
  const { code } = req.query;
  
  try {
    // 1. Exchange the code for tokens
    const tokenResponse = await fetch('https://github.com/login/oauth/access_token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({
        client_id: process.env.GITHUB_CLIENT_ID,
        client_secret: process.env.GITHUB_CLIENT_SECRET,
        code,
        redirect_uri: process.env.NODE_ENV === 'production'
          ? 'https://your-domain.com/auth/callback/github'
          : 'http://localhost:3001/auth/callback/github',
      }),
    });

    const tokens = await tokenResponse.json();

    // 2. Get user info using the access token
    const userResponse = await fetch('https://api.github.com/user', {
      headers: {
        Authorization: `Bearer ${tokens.access_token}`,
      },
    });
    const userData = await userResponse.json();

    // 3. Create our own JWT token
    const ourToken = jwt.sign(
      {
        id: userData.id,
        login: userData.login,
        name: userData.name,
        avatar_url: userData.avatar_url,
      },
      process.env.JWT_SECRET || 'your-secret-key',
      { expiresIn: '1d' }
    );

    // 4. Redirect to frontend with our token
    res.redirect(`http://localhost:5173/auth/callback?token=${ourToken}`);
  } catch (error) {
    console.error('OAuth callback error:', error);
    res.redirect('http://localhost:5173/auth/error');
  }
});

// Verify token endpoint
router.post('/verify', verifyToken, (req, res) => {
  // If we get here, the token is valid
  res.json({ 
    valid: true,
    user: req.user
  });
});

export default router; 