import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '@/services/api';
import type { User } from '@/types';
import gistHome from '@/assets/gist-home.avif';
import gistLogo from '@/assets/GISTLogo_Final.jpg';

interface LoginPageProps {
  onLogin: (user: User) => void;
}

export default function LoginPage({ onLogin }: LoginPageProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const authResponse = await authAPI.login({ email, password });
      localStorage.setItem('access_token', authResponse.access_token);
      
      const user = await authAPI.getCurrentUser();
      onLogin(user);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen flex flex-col bg-cover bg-center bg-no-repeat"
      style={{ backgroundImage: `url(${gistHome})` }}
    >
      {/* Overlay for better contrast */}
      <div className="absolute inset-0 bg-black/40"></div>

      {/* Header */}
      <div className="relative z-10 px-4 md:px-8 pt-6 md:pt-8">
        <div className="mx-auto max-w-6xl rounded-2xl border border-white/35 bg-white/20 backdrop-blur-xl shadow-2xl">
          <div className="flex flex-col md:flex-row items-center justify-center gap-4 md:gap-6 px-5 md:px-8 py-4 md:py-5 text-center">
            <img src={gistLogo} alt="GIST Logo" className="h-12 md:h-16 w-auto" />
            <div>
              <h2 className="text-xl md:text-3xl font-bold text-orange-500 mb-1">Geethanjali Institute of Science and Technology</h2>
              <p className="text-xs md:text-sm text-white/90">Autonomous | NAAC-A Grade | NBA Accredited IEEE, JCSE & MRCHS Approved by AICTE, New Delhi & Affiliated to JNTUA, Anantapuramu</p>
            </div>
          </div>
        </div>
      </div>

      {/* Login Form Container */}
      <div className="relative z-10 flex items-center justify-center flex-1">
        <div className="max-w-md w-full space-y-8 p-8 bg-white/20 backdrop-blur-md rounded-2xl shadow-2xl border border-white/30">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-white mb-2">GIST OMS</h1>
            <p className="text-white/80">Office Management System</p>
          </div>

          <form onSubmit={handleSubmit} className="mt-8 space-y-6">
            {error && (
              <div className="bg-red-500/30 backdrop-blur-sm border border-red-200/50 text-red-100 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-white/90 mb-1">
                  Email Address
                </label>
                <input
                  id="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg text-white placeholder-white/50 focus:ring-2 focus:ring-orange-400 focus:border-transparent focus:bg-white/30 transition-all"
                  placeholder="user@gist.edu"
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-white/90 mb-1">
                  Password
                </label>
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-4 py-3 pr-12 bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg text-white placeholder-white/50 focus:ring-2 focus:ring-orange-400 focus:border-transparent focus:bg-white/30 transition-all"
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((prev) => !prev)}
                    className="absolute inset-y-0 right-0 flex items-center px-3 text-white/70 hover:text-white focus:outline-none"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? (
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                      </svg>
                    ) : (
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.477 0 8.268 2.943 9.542 7-1.274 4.057-5.065 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 bg-orange-500 hover:bg-orange-600 text-white font-semibold rounded-lg shadow-lg focus:outline-none focus:ring-2 focus:ring-orange-400 focus:ring-offset-2 focus:ring-offset-white/20 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-white/80">
            <p className="font-semibold mb-2">Demo Credentials:</p>
            <div className="space-y-1 text-xs text-white/70">
              <p>Director: director@gist.edu / director123</p>
              <p>Principal: principal@gist.edu / principal123</p>
              <p>VP: vp@gist.edu / vp123</p>
              <p>HOD: hod.computerscience@gist.edu / hod123</p>
              <p>Employee: emp1.computerscience@gist.edu / emp123</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
