'use client';

/**
 * Registration page - Professional/Modern SaaS theme.
 */

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
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

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleRoleSelect = (role: UserRole) => {
    setFormData({ ...formData, role });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validate passwords match
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    // Validate password length
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

      // Store auth token and user info
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user_id', data.user_id);
      localStorage.setItem('user_email', data.email);
      localStorage.setItem('user_role', data.role);
      localStorage.setItem('user_tier', data.tier);

      // Redirect to dashboard using window.location for reliable navigation
      window.location.href = '/dashboard';
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg-primary px-4">
      <div className="w-full max-w-md">
        <Card variant="elevated" className="border-l-4 border-l-accent-success">
          <CardHeader className="text-center">
            <div className="text-4xl mb-2">🎓</div>
            <CardTitle className="text-2xl">Create Account</CardTitle>
            <CardDescription>
              Join as a student or teacher
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="p-3 rounded-lg bg-accent-danger/10 border border-accent-danger/30 text-accent-danger text-sm">
                  {error}
                </div>
              )}

              {/* Role Selection */}
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  I am a...
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {/* Student Option */}
                  <button
                    type="button"
                    onClick={() => handleRoleSelect('student')}
                    className={`p-4 rounded-lg border-2 text-center transition-all ${
                      formData.role === 'student'
                        ? 'border-accent-primary bg-accent-primary/10 shadow-md'
                        : 'border-border-default hover:border-accent-primary/50 hover:bg-bg-elevated'
                    }`}
                  >
                    <div className="text-3xl mb-2">👨‍🎓</div>
                    <div className={`font-semibold ${formData.role === 'student' ? 'text-accent-primary' : 'text-text-primary'}`}>
                      Student
                    </div>
                    <div className="text-xs text-text-muted mt-1">
                      Learn & grow
                    </div>
                  </button>

                  {/* Teacher Option */}
                  <button
                    type="button"
                    onClick={() => handleRoleSelect('teacher')}
                    className={`p-4 rounded-lg border-2 text-center transition-all ${
                      formData.role === 'teacher'
                        ? 'border-accent-secondary bg-accent-secondary/10 shadow-md'
                        : 'border-border-default hover:border-accent-secondary/50 hover:bg-bg-elevated'
                    }`}
                  >
                    <div className="text-3xl mb-2">👨‍🏫</div>
                    <div className={`font-semibold ${formData.role === 'teacher' ? 'text-accent-secondary' : 'text-text-primary'}`}>
                      Teacher
                    </div>
                    <div className="text-xs text-text-muted mt-1">
                      Create & manage
                    </div>
                  </button>
                </div>
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-text-secondary mb-1.5">
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
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-text-secondary mb-1.5">
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
                />
                <p className="text-xs text-text-muted mt-1">Minimum 6 characters</p>
              </div>

              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-text-secondary mb-1.5">
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
                />
              </div>

              <Button
                type="submit"
                variant={formData.role === 'teacher' ? 'secondary' : 'primary'}
                size="lg"
                className="w-full"
                disabled={isLoading}
              >
                {isLoading ? <LoadingSpinner size="sm" /> : `Create ${formData.role === 'teacher' ? 'Teacher' : 'Student'} Account`}
              </Button>
            </form>

            <div className="mt-6 text-center text-sm text-text-secondary">
              Already have an account?{' '}
              <Link href="/login" className="text-accent-primary hover:text-accent-primary/80 font-medium">
                Sign in
              </Link>
            </div>
          </CardContent>
        </Card>

        <div className="mt-4 p-4 rounded-lg bg-bg-elevated border border-border-default">
          <p className="text-xs text-text-secondary text-center">
            {formData.role === 'teacher' ? (
              <>
                Teachers can create courses, manage students, and track progress.
                Start with <span className="font-medium">Free</span> tier (up to 20 students).
                Upgrade for unlimited students and advanced analytics.
              </>
            ) : (
              <>
                By signing up as a student, you'll start with our{' '}
                <span className="font-medium">Free</span> tier (access to first 3 chapters).
                Upgrade to <span className="font-medium">Premium</span> or <span className="font-medium">Pro</span> for full access.
              </>
            )}
          </p>
        </div>
      </div>
    </div>
  );
}
