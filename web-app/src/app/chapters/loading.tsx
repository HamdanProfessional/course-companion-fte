/**
 * Loading state for Chapters page.
 * Shows skeleton cards while chapters are being fetched.
 */
import { Card, CardContent } from '@/components/ui/Card';

export default function ChaptersLoading() {
  return (
    <div className="container py-8">
      {/* Header Skeleton */}
      <div className="mb-8">
        <div className="h-8 w-48 bg-bg-elevated rounded-lg animate-pulse mb-2" />
        <div className="h-4 w-96 bg-bg-elevated/50 rounded animate-pulse" />
      </div>

      {/* Progress Overview Skeleton */}
      <Card className="mb-6">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-3">
            <div className="h-4 w-24 bg-bg-elevated rounded animate-pulse" />
            <div className="h-4 w-16 bg-bg-elevated/50 rounded animate-pulse" />
          </div>
          <div className="h-2 bg-bg-elevated rounded-full animate-pulse" />
        </CardContent>
      </Card>

      {/* Chapters Grid Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <Card key={i}>
            <div className="p-6 border-b border-border-default">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="h-4 w-16 bg-bg-elevated/50 rounded animate-pulse mb-2" />
                  <div className="h-6 w-full bg-bg-elevated rounded animate-pulse mb-2" />
                  <div className="h-6 w-3/4 bg-bg-elevated/50 rounded animate-pulse" />
                </div>
                <div className="w-12 h-12 rounded-lg bg-bg-elevated animate-pulse" />
              </div>
              <div className="flex items-center gap-2">
                <div className="h-5 w-20 bg-bg-elevated/30 rounded-full animate-pulse" />
                <div className="h-5 w-16 bg-bg-elevated/30 rounded-full animate-pulse" />
              </div>
            </div>
            <div className="p-6 space-y-3">
              <div className="h-10 w-full bg-bg-elevated/50 rounded-lg animate-pulse" />
              <div className="h-10 w-full bg-bg-elevated/30 rounded-lg animate-pulse" />
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
