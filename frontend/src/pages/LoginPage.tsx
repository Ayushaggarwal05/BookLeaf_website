import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { BookOpen, Lock, Mail, AlertCircle, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const from = (location.state as any)?.from?.pathname || '/';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!email.trim() || !password.trim()) {
      setErrorMessage('Please enter both email and password.');
      return;
    }

    setIsSubmitting(true);
    try {
      const user = await login({ email: email.trim(), password: password.trim() });
      if (user.role === 'admin') {
        navigate('/admin', { replace: true });
      } else {
        const dest = !from || from === '/login' || from.startsWith('/admin') ? '/' : from;
        navigate(dest, { replace: true });
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Invalid credentials. Please verify your email and password.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleQuickFill = (demoEmail: string, isStaff: boolean = false) => {
    setEmail(demoEmail);
    setPassword(isStaff ? 'Admin@BookLeaf2026!' : 'Author@BookLeaf2026!');
    setErrorMessage(null);
  };

  return (
    <div className="min-h-screen bg-cream-100 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        {/* Brand Header: Logo and Title side-by-side */}
        <div className="flex items-center justify-center gap-3.5 mb-2">
          <div className="flex items-center justify-center w-12 h-12 rounded-2xl bg-brand-700 text-white shadow-card flex-shrink-0">
            <BookOpen className="w-6 h-6 text-brand-100" />
          </div>
          <div className="text-left">
            <h1 className="text-2xl sm:text-3xl font-serif font-bold text-brand-950 tracking-tight leading-none">
              BookLeaf
            </h1>
            <p className="mt-1 text-xs sm:text-sm text-brand-800 font-medium">
              Author Support & Royalty Portal
            </p>
          </div>
        </div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0">
        <div className="bg-white py-8 px-6 shadow-soft sm:rounded-2xl sm:px-10 border border-cream-300">
          <h2 className="text-xl font-serif text-gray-900 mb-6 font-semibold">
            Sign in to your author account
          </h2>

          {errorMessage && (
            <div className="mb-5 p-3.5 rounded-lg bg-rose-50 border border-rose-200 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" />
              <div className="text-xs text-rose-800 font-medium leading-relaxed">
                {errorMessage}
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1.5">
                Email Address
              </label>
              <div className="relative rounded-lg shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="author@example.com"
                  className="block w-full pl-10 pr-3.5 py-2.5 text-sm bg-cream-50/50 border border-cream-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-brand-600 focus:border-brand-600 transition"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1.5">
                Password
              </label>
              <div className="relative rounded-lg shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="block w-full pl-10 pr-3.5 py-2.5 text-sm bg-cream-50/50 border border-cream-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-brand-600 focus:border-brand-600 transition"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full flex justify-center items-center gap-2 py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-brand-700 hover:bg-brand-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-600 transition disabled:opacity-70 mt-2"
            >
              {isSubmitting ? (
                <LoadingSpinner size="sm" />
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Quick-Fill Demo Accounts Helper */}
          <div className="mt-8 pt-6 border-t border-cream-200">
            <span className="block text-[11px] font-semibold text-gray-500 uppercase tracking-wider text-center mb-3">
              Official Demo Accounts
            </span>
            <div className="space-y-2">
              <button
                type="button"
                onClick={() => handleQuickFill('admin@bookleaf.in', true)}
                className="w-full text-left px-3.5 py-2.5 rounded-lg border border-brand-300 bg-brand-50/60 hover:bg-brand-50 text-xs transition flex items-center justify-between"
              >
                <div>
                  <span className="font-semibold text-brand-950 block">Operations Specialist (Admin)</span>
                  <span className="text-[10px] text-brand-800 block">admin@bookleaf.in</span>
                </div>
                <span className="px-2 py-0.5 rounded bg-brand-700 text-white text-[10px] font-bold">
                  Staff Role
                </span>
              </button>

              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => handleQuickFill('priya.sharma@email.com', false)}
                  className="text-left px-3 py-2 rounded-lg border border-cream-300 hover:border-brand-400 bg-cream-50 hover:bg-white text-xs transition"
                >
                  <span className="font-semibold text-brand-950 block">Priya Sharma</span>
                  <span className="text-[10px] text-gray-500 block truncate">AUTH001 (Fiction)</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickFill('rohit.kapoor@email.com', false)}
                  className="text-left px-3 py-2 rounded-lg border border-cream-300 hover:border-brand-400 bg-cream-50 hover:bg-white text-xs transition"
                >
                  <span className="font-semibold text-brand-950 block">Rohit Kapoor</span>
                  <span className="text-[10px] text-gray-500 block truncate">AUTH002 (Tech/Business)</span>
                </button>
              </div>
            </div>
            <p className="mt-3 text-[11px] text-gray-400 text-center">
              Author Pass: <code className="bg-cream-100 px-1 py-0.5 rounded text-gray-700">Author@BookLeaf2026!</code> • Admin Pass: <code className="bg-cream-100 px-1 py-0.5 rounded text-gray-700">Admin@BookLeaf2026!</code>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
