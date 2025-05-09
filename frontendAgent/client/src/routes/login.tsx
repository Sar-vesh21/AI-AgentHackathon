import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../providers/authContext';

const Login = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { login } = useAuth();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check if we have a token in the URL (from OAuth callback)
    const token = searchParams.get('token');
    if (token) {
      login(token)
        .then(() => {
          navigate('/');
        })
        .catch((err) => {
          setError('Failed to verify token. Please try again.');
          console.error('Login error:', err);
        });
    }
  }, [searchParams, login, navigate]);

  const handleGoogleLogin = () => {
    window.location.href = 'http://localhost:3001/auth/google';
  };

  const handleGithubLogin = () => {
    window.location.href = 'http://localhost:3001/auth/github';
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-dark">
      <div className="max-w-md w-full bg-white p-8 rounded-xl shadow-lg flex flex-col items-center">
        {/* Logo */}
        <div className="mb-6">
          <img src="/tsLogo.png" alt="Logo" className="h-12 mx-auto" />
        </div>
        <h2 className="text-2xl font-bold text-center mb-2 text-emerald-600">Welcome</h2>
        <p className="text-gray-600 text-center mb-6">
          Please login <span className="font-semibold">here</span> to continue to <span className="font-semibold"> HyperInsight</span>.
        </p>
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative mb-4 w-full text-center" role="alert">
            <span className="block sm:inline">{error}</span>
          </div>
        )}
        {/* Social login buttons */}
        <button
          onClick={handleGoogleLogin}
          className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-100 mb-3"
        >
          <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
            <path
              fill="currentColor"
              d="M21.805 10.023h-9.18v3.954h5.557c-.24 1.26-1.44 3.7-5.557 3.7-3.34 0-6.06-2.76-6.06-6.154s2.72-6.154 6.06-6.154c1.9 0 3.18.81 3.91 1.5l2.67-2.6C17.1 2.7 15.1 1.7 12.8 1.7 7.7 1.7 3.7 5.7 3.7 10.8s4 9.1 9.1 9.1c5.2 0 8.6-3.7 8.6-8.9 0-.6-.1-1.1-.2-1.6z"
            />
          </svg>
          Continue with Google
        </button>
        <button
          onClick={handleGithubLogin}
          className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-100"
        >
          <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
            <path
              fill="currentColor"
              d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.438 9.8 8.207 11.387.6.11.793-.26.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-.89-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.108-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.565 21.8 24 17.3 24 12c0-6.63-5.37-12-12-12z"
            />
          </svg>
          Continue with GitHub
        </button>
        {/* Divider */}
        <div className="flex items-center my-6 w-full">
          <div className="flex-grow border-t border-gray-200"></div>
          <span className="mx-4 text-gray-400">or</span>
          <div className="flex-grow border-t border-gray-200"></div>
        </div>
        {/* Sign up link (optional) */}
        <div className="text-center w-full">
          <span className="text-gray-600">Don't have an account?</span>
          <a href="#" className="ml-1 text-blue-600 font-medium hover:underline">Sign up</a>
        </div>
      </div>
    </div>
  );
};

export default Login;
