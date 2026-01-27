/**
 * User profile and settings page.
 */
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useAuth } from '@/hooks';
import Link from 'next/link';

export default function ProfilePage() {
  const { data: user } = useAuth();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Profile & Settings</h1>
        <p className="text-gray-600 mt-2">
          Manage your account and preferences
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Account Info */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Account Information</CardTitle>
              <CardDescription>Your account details</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <Input value={user?.email || 'student@example.com'} disabled />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Member Since
                </label>
                <Input
                  value={user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'January 2026'}
                  disabled
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Change Password</CardTitle>
              <CardDescription>Update your password</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Current Password
                </label>
                <Input type="password" placeholder="Enter current password" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  New Password
                </label>
                <Input type="password" placeholder="Enter new password" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Confirm New Password
                </label>
                <Input type="password" placeholder="Confirm new password" />
              </div>
              <Button variant="primary">Update Password</Button>
            </CardContent>
          </Card>
        </div>

        {/* Subscription */}
        <Card>
          <CardHeader>
            <CardTitle>Subscription</CardTitle>
            <CardDescription>Your current plan</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="text-sm font-medium text-blue-900 mb-1">
                Current Tier
              </div>
              <div className="text-2xl font-bold text-blue-700 capitalize">
                {user?.tier || 'Free'}
              </div>
            </div>

            <div className="space-y-2">
              <h3 className="font-medium text-gray-900">Plan Benefits</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                {(user?.tier === 'free' ? [
                  '✓ First 3 chapters',
                  '✓ Basic quizzes',
                  '✓ Progress tracking',
                  '✗ All 10 chapters',
                  '✗ Advanced quizzes',
                ] : [
                  '✓ All 10 chapters',
                  '✓ Advanced quizzes',
                  '✓ Progress tracking',
                  '✓ Certificates',
                  '✓ Priority support',
                ]).map((benefit, i) => (
                  <li key={i}>{benefit}</li>
                ))}
              </ul>
            </div>

            {user?.tier === 'free' && (
              <Button variant="primary" className="w-full">
                Upgrade to Premium - $9.99/mo
              </Button>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Data Export */}
      <Card>
        <CardHeader>
          <CardTitle>Data Export</CardTitle>
          <CardDescription>Download your learning data (GDPR)</CardDescription>
        </CardHeader>
        <CardContent>
          <Button variant="outline">Export All Data (JSON)</Button>
        </CardContent>
      </Card>

      {/* Danger Zone */}
      <Card className="border-red-200">
        <CardHeader>
          <CardTitle className="text-red-600">Danger Zone</CardTitle>
          <CardDescription>Irreversible actions</CardDescription>
        </CardHeader>
        <CardContent>
          <Button variant="outline" className="text-red-600 border-red-600 hover:bg-red-50">
            Delete Account
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
