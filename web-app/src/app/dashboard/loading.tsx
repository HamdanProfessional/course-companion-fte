/**
 * Loading state for Dashboard page.
 * Shows skeleton cards while data is being fetched.
 */
import { Card, CardContent } from '@/components/ui/Card';
import { LoadingSpinner } from '@/components/ui/Loading';

export default function DashboardLoading() {
  return (
    <div className="container py-8">
      {/* Header Skeleton */}
      <div className="mb-8">
        <div className="h-8 w-48 bg-bg-elevated rounded-lg animate-pulse mb-2" />
        <div className="h-4 w-96 bg-bg-elevated/50 rounded animate-pulse" />
      </div>

      {/* Stats Grid Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i}>
            <CardContent className="p-6">
              <div className="h-4 w-24 bg-bg-elevated rounded animate-pulse mb-2" />
              <div className="h-8 w-16 bg-bg-elevated/50 rounded animate-pulse mb-1" />
              <div className="h-3 w-32 bg-bg-elevated/30 rounded animate-pulse" />
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Course Outline Skeleton */}
      <Card>
        <div className="p-6 border-b border-border-default">
          <div className="h-6 w-40 bg-bg-elevated rounded animate-pulse" />
        </div>
        <div className="p-6 space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="flex items-center justify-between p-4 rounded-lg border border-border-default">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-lg bg-bg-elevated animate-pulse" />
                <div className="space-y-2">
                  <div className="h-4 w-48 bg-bg-elevated/50 rounded animate-pulse" />
                  <div className="h-3 w-24 bg-bg-elevated/30 rounded animate-pulse" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
