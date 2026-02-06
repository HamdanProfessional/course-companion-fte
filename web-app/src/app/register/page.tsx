'use client';

/**
 * Registration page - Nebula/Cosmic theme with glass-morphism.
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { GraduationCap, User, Users } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { LoadingSpinner } from '@/components/ui/Loading';

type UserRole = 'student' | 'teacher';

export default function RegisterPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    role: 'student' as UserRole,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Clear any existing auth data when register page is visited
  useEffect(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_role');
    localStorage.removeItem('user_tier');
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleRoleSelect = (role: UserRole) => {
    setFormData({ ...formData, role });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/api/v1/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
          role: formData.role,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Registration failed');
      }

      // Store in localStorage for client-side access
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user_id', data.user_id);
      localStorage.setItem('user_email', data.email);
      localStorage.setItem('user_role', data.role);
      localStorage.setItem('user_tier', data.tier);

      // Set cookie for middleware
      document.cookie = `token=${data.access_token}; path=/; max-age=${60 * 60 * 24 * 7}; SameSite=Lax`;

      window.location.href = '/dashboard';
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 -z-10">
        <motion.div
          animate={{
            backgroundPosition: ['0% 0%', '100% 100%', '0% 0%'],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: 'linear',
          }}
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage: `
              radial-gradient(circle at 20% 30%, rgba(139, 92, 246, 0.3) 0%, transparent 50%),
              radial-gradient(circle at 80% 70%, rgba(14, 165, 233, 0.3) 0%, transparent 50%),
              radial-gradient(circle at 50% 50%, rgba(236, 72, 153, 0.2) 0%, transparent 50%)
            `,
            backgroundSize: '200% 200%',
          }}
        />
      </div>

      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.5, type: 'spring' }}
        className="w-full max-w-md"
      >
        <Card variant="cosmic" glow className="border-l-4 border-l-cosmic-success">
          <CardHeader className="text-center">
            <motion.div
              animate={{ scale: [1, 1.05, 1] }}
              transition={{ duration: 4, repeat: Infinity, repeatDelay: 2 }}
              className="flex justify-center mb-4"
            >
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-cosmic-primary to-cosmic-blue flex items-center justify-center shadow-glow-purple">
                <GraduationCap className="w-8 h-8 text-white" />
              </div>
            </motion.div>
            <CardTitle className="text-3xl font-bold text-gradient">Create Account</CardTitle>
            <CardDescription className="text-text-secondary">
              Join as a student or teacher
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-5">
              {error && (
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="p-3 rounded-xl bg-red-500/20 border border-red-500/30 text-red-400 text-sm"
                >
                  {error}
                </motion.div>
              )}

              {/* Role Selection */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 }}
              >
                <label className="block text-sm font-semibold text-text-secondary mb-3">
                  I am a...
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {/* Student Option */}
                  <motion.button
                    type="button"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleRoleSelect('student')}
                    className={`p-4 rounded-xl border-2 text-center transition-all ${
                      formData.role === 'student'
                        ? 'border-cosmic-primary bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 shadow-glow-purple'
                        : 'border-glass-border hover:border-cosmic-primary/50 hover:bg-cosmic-primary/10 bg-glass-surface'
                    }`}
                  >
                    <div className="flex justify-center mb-2">
                      <User className={`w-8 h-8 ${formData.role === 'student' ? 'text-cosmic-primary' : 'text-text-primary'}`} />
                    </div>
                    <div className={`font-semibold ${formData.role === 'student' ? 'text-cosmic-primary' : 'text-text-primary'}`}>
                      Student
                    </div>
                    <div className="text-xs text-text-secondary mt-1">
                      Learn & grow
                    </div>
                  </motion.button>

                  {/* Teacher Option */}
                  <motion.button
                    type="button"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleRoleSelect('teacher')}
                    className={`p-4 rounded-xl border-2 text-center transition-all ${
                      formData.role === 'teacher'
                        ? 'border-cosmic-purple bg-gradient-to-br from-cosmic-purple/20 to-cosmic-pink/20 shadow-glow-purple'
                        : 'border-glass-border hover:border-cosmic-purple/50 hover:bg-cosmic-purple/10 bg-glass-surface'
                    }`}
                  >
                    <div className="flex justify-center mb-2">
                      <Users className={`w-8 h-8 ${formData.role === 'teacher' ? 'text-cosmic-purple' : 'text-text-primary'}`} />
                    </div>
                    <div className={`font-semibold ${formData.role === 'teacher' ? 'text-cosmic-purple' : 'text-text-primary'}`}>
                      Teacher
                    </div>
                    <div className="text-xs text-text-secondary mt-1">
                      Create & manage
                    </div>
                  </motion.button>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
              >
                <label htmlFor="email" className="block text-sm font-semibold text-text-secondary mb-2">
                  Email
                </label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="you@example.com"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  disabled={isLoading}
                  autoComplete="email"
                  className="bg-glass-surface border-glass-border"
                />
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.25 }}
              >
                <label htmlFor="password" className="block text-sm font-semibold text-text-secondary mb-2">
                  Password
                </label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  disabled={isLoading}
                  minLength={6}
                  autoComplete="new-password"
                  className="bg-glass-surface border-glass-border"
                />
                <p className="text-xs text-text-secondary mt-1">Minimum 6 characters</p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
              >
                <label htmlFor="confirmPassword" className="block text-sm font-semibold text-text-secondary mb-2">
                  Confirm Password
                </label>
                <Input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  placeholder="••••••••"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required
                  disabled={isLoading}
                  minLength={6}
                  autoComplete="new-password"
                  className="bg-glass-surface border-glass-border"
                />
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.35 }}
              >
                <Button
                  type="submit"
                  variant={formData.role === 'teacher' ? 'secondary' : 'primary'}
                  size="lg"
                  className="w-full"
                  disabled={isLoading}
                >
                  {isLoading ? <LoadingSpinner size="sm" /> : `Create ${formData.role === 'teacher' ? 'Teacher' : 'Student'} Account`}
                </Button>
              </motion.div>
            </form>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="mt-6 text-center text-sm text-text-secondary"
            >
              Already have an account?{' '}
              <Link href="/login" className="text-cosmic-primary hover:text-cosmic-purple font-semibold hover:underline transition-colors">
                Sign in
              </Link>
            </motion.div>
          </CardContent>
        </Card>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-4 p-4 rounded-xl bg-glass-surface border border-glass-border backdrop-blur-sm"
        >
          <p className="text-xs text-text-secondary text-center">
            {formData.role === 'teacher' ? (
              <>
                Teachers can create courses, manage students, and track progress.
                Start with <span className="font-semibold text-cosmic-primary">Free</span> tier (up to 20 students).
                Upgrade for unlimited students and advanced analytics.
              </>
            ) : (
              <>
                By signing up as a student, you'll start with our{' '}
                <span className="font-semibold text-cosmic-primary">Free</span> tier (access to first 3 chapters).
                Upgrade to <span className="font-semibold text-cosmic-purple">Premium</span> or <span className="font-semibold text-cosmic-blue">Pro</span> for full access.
              </>
            )}
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
}
