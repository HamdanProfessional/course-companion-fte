/**
 * Loading state for Profile page.
 * Shows skeleton cards while profile data is being fetched.
 */
import { Card, CardContent } from '@/components/ui/Card';

export default function ProfileLoading() {
  return (
    <div className="container py-8">
      {/* Header Skeleton */}
      <div className="mb-8">
        <div className="h-8 w-48 bg-bg-elevated rounded-lg animate-pulse mb-2" />
        <div className="h-4 w-80 bg-bg-elevated/50 rounded animate-pulse" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column Skeleton */}
        <div className="lg:col-span-2 space-y-6">
          {/* Account Information Skeleton */}
          <Card>
            <div className="p-6 border-b border-border-default">
              <div className="h-6 w-48 bg-bg-elevated rounded animate-pulse mb-2" />
              <div className="h-4 w-40 bg-bg-elevated/50 rounded animate-pulse" />
            </div>
            <div className="p-6 space-y-4">
              <div>
                <div className="h-4 w-28 bg-bg-elevated/50 rounded animate-pulse mb-2" />
                <div className="h-10 w-full bg-bg-elevated/30 rounded-lg animate-pulse" />
              </div>
              <div>
                <div className="h-4 w-28 bg-bg-elevated/50 rounded animate-pulse mb-2" />
                <div className="h-10 w-48 bg-bg-elevated/30 rounded-lg animate-pulse" />
              </div>
              <div>
                <div className="h-4 w-24 bg-bg-elevated/50 rounded animate-pulse mb-2" />
                <div className="h-10 w-full bg-bg-elevated/30 rounded-lg animate-pulse" />
              </div>
            </div>
          </Card>

          {/* Change Password Skeleton */}
          <Card>
            <div className="p-6 border-b border-border-default">
              <div className="h-6 w-36 bg-bg-elevated rounded animate-pulse mb-2" />
              <div className="h-4 w-32 bg-bg-elevated/50 rounded animate-pulse" />
            </div>
            <div className="p-6 space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i}>
                  <div className="h-4 w-32 bg-bg-elevated/50 rounded animate-pulse mb-2" />
                  <div className="h-10 w-full bg-bg-elevated/30 rounded-lg animate-pulse" />
                </div>
              ))}
              <div className="h-10 w-32 bg-bg-elevated/50 rounded-lg animate-pulse" />
            </div>
          </Card>
        </div>

        {/* Right Column Skeleton */}
        <div className="space-y-6">
          <Card>
            <div className="p-6 border-b border-border-default">
              <div className="h-6 w-28 bg-bg-elevated rounded animate-pulse mb-2" />
              <div className="h-4 w-32 bg-bg-elevated/50 rounded animate-pulse" />
            </div>
            <div className="p-6 space-y-4">
              <div className="p-4 rounded-lg border border-border-default">
                <div className="h-4 w-28 bg-bg-elevated/50 rounded animate-pulse mb-1" />
                <div className="h-6 w-24 bg-bg-elevated rounded animate-pulse mb-3" />
                <div className="space-y-2">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className="h-4 w-full bg-bg-elevated/30 rounded animate-pulse" />
                  ))}
                </div>
              </div>
              <div className="h-10 w-full bg-bg-elevated/50 rounded-lg animate-pulse" />
            </div>
          </Card>
        </div>
      </div>

      {/* Data Export Skeleton */}
      <Card className="mt-6">
        <div className="p-6 border-b border-border-default">
          <div className="h-6 w-32 bg-bg-elevated rounded animate-pulse mb-2" />
          <div className="h-4 w-56 bg-bg-elevated/50 rounded animate-pulse" />
        </div>
        <div className="p-6 flex gap-3">
          <div className="h-10 w-40 bg-bg-elevated/50 rounded-lg animate-pulse" />
          <div className="h-10 w-40 bg-bg-elevated/30 rounded-lg animate-pulse" />
        </div>
      </Card>
    </div>
  );
}
