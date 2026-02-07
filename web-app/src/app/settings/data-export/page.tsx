'use client';

/**
 * Data Export Page - Phase 3 (GDPR Compliance)
 *
 * Allows users to export their personal data in various formats.
 * GDPR-compliant data portability feature.
 */

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingSpinner } from '@/components/ui/Loading';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import { Breadcrumbs } from '@/components/layout/Breadcrumbs';
import { useV3DataExport } from '@/hooks/useV3';
import { Info, BarChart3, FileEdit, Flame, Trophy, Check } from 'lucide-react';
import Link from 'next/link';

const DATA_CATEGORIES = {
  progress: {
    id: 'progress',
    name: 'Learning Progress',
    description: 'Chapter completion, current chapter, timestamps',
    icon: 'BarChart3',
  },
  quiz_history: {
    id: 'quiz_history',
    name: 'Quiz History',
    description: 'All quiz attempts, scores, answers, and timestamps',
    icon: 'FileEdit',
  },
  streaks: {
    id: 'streaks',
    name: 'Streak Data',
    description: 'Daily checkins, current and longest streaks',
    icon: 'Flame',
  },
  achievements: {
    id: 'achievements',
    name: 'Achievements',
    description: 'Unlocked achievements, unlock dates, progress',
    icon: 'Trophy',
  },
};

const EXPORT_FORMATS = [
  { value: 'json', label: 'JSON', description: 'Machine-readable format for developers' },
  { value: 'csv', label: 'CSV', description: 'Spreadsheet-compatible format' },
  { value: 'pdf', label: 'PDF', description: 'Human-readable report document' },
];

const getCategoryIcon = (iconName: string) => {
  const icons: Record<string, React.ReactNode> = {
    'BarChart3': <BarChart3 className="w-6 h-6 text-accent-primary" />,
    'FileEdit': <FileEdit className="w-6 h-6 text-accent-primary" />,
    'Flame': <Flame className="w-6 h-6 text-accent-primary" />,
    'Trophy': <Trophy className="w-6 h-6 text-accent-primary" />,
  };
  return icons[iconName] || <BarChart3 className="w-6 h-6 text-accent-primary" />;
};

export default function DataExportPage() {
  const [selectedCategories, setSelectedCategories] = useState<Set<string>>(
    new Set(['progress', 'quiz_history', 'streaks', 'achievements'])
  );
  const [format, setFormat] = useState<'json' | 'csv' | 'pdf'>('json');
  const [exportId, setExportId] = useState<string | null>(null);

  const dataExport = useV3DataExport();

  const toggleCategory = (categoryId: string) => {
    const newCategories = new Set(selectedCategories);
    if (newCategories.has(categoryId)) {
      // Don't allow deselecting all categories
      if (newCategories.size > 1) {
        newCategories.delete(categoryId);
      }
    } else {
      newCategories.add(categoryId);
    }
    setSelectedCategories(newCategories);
  };

  const handleExport = async () => {
    try {
      const result = await dataExport.mutateAsync({
        include_progress: selectedCategories.has('progress'),
        include_quiz_history: selectedCategories.has('quiz_history'),
        include_streaks: selectedCategories.has('streaks'),
        format,
      });
      setExportId(result.export_id);

      // In production, would poll for status or use WebSocket
      if (result.download_url) {
        window.open(result.download_url, '_blank');
      }
    } catch (error) {
      console.error('Export failed:', error);
      alert('Export failed. Please try again.');
    }
  };

  return (
    <PageContainer>
      <Breadcrumbs />

      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-text-primary mb-2">Export Your Data</h1>
          <p className="text-text-secondary">
            Download all your personal data in your preferred format. This feature complies with
            GDPR data portability requirements.
          </p>
        </div>

        {/* Info Card */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-info/20 to-accent-info/10 flex items-center justify-center flex-shrink-0">
                <Info className="w-7 h-7 text-accent-info" />
              </div>
              <div>
                <h3 className="font-semibold text-text-primary mb-2">About Data Export</h3>
                <p className="text-sm text-text-secondary">
                  You can export your personal data at any time. Exports include all learning progress,
                  quiz history, streak data, and achievements. The export will be available for
                  7 days before being automatically deleted for security.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Data Categories */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Select Data to Export</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.values(DATA_CATEGORIES).map((category) => (
                <button
                  key={category.id}
                  onClick={() => toggleCategory(category.id)}
                  className={`p-4 rounded-lg border-2 text-left transition-all ${
                    selectedCategories.has(category.id)
                      ? 'border-accent-primary bg-accent-primary/5'
                      : 'border-border-default bg-bg-elevated hover:border-accent-primary/30'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <div className="text-2xl">{getCategoryIcon(category.icon)}</div>
                      <div>
                        <h4 className="font-medium text-text-primary">{category.name}</h4>
                        <p className="text-sm text-text-muted mt-1">{category.description}</p>
                      </div>
                    </div>
                    <div className={`w-6 h-6 rounded border-2 flex items-center justify-center flex-shrink-0 ${
                      selectedCategories.has(category.id)
                        ? 'border-accent-primary bg-accent-primary'
                        : 'border-border-default'
                    }`}>
                      {selectedCategories.has(category.id) && (
                        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Export Format */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Export Format</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {EXPORT_FORMATS.map((fmt) => (
                <button
                  key={fmt.value}
                  onClick={() => setFormat(fmt.value as any)}
                  className={`p-4 rounded-lg border-2 text-left transition-all ${
                    format === fmt.value
                      ? 'border-accent-primary bg-accent-primary/5'
                      : 'border-border-default bg-bg-elevated hover:border-accent-primary/30'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-medium text-text-primary mb-1">{fmt.label}</h4>
                      <p className="text-xs text-text-muted">{fmt.description}</p>
                    </div>
                    {format === fmt.value && (
                      <Badge variant="info" className="ml-2">
                        Selected
                      </Badge>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Export Actions */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-semibold text-text-primary mb-1">
                  {selectedCategories.size} categories selected
                </h4>
                <p className="text-sm text-text-muted">
                  Format: {format.toUpperCase()} • Expires in 7 days
                </p>
              </div>
              <Button
                variant="primary"
                onClick={handleExport}
                disabled={dataExport.isPending}
                isLoading={dataExport.isPending}
              >
                {dataExport.isPending ? 'Preparing...' : 'Export Data'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Export Status */}
        {exportId && (
          <Card className="mb-6 bg-accent-success/5">
            <CardContent className="p-6">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-full bg-accent-success/20 flex items-center justify-center flex-shrink-0">
                  <Check className="w-6 h-6 text-accent-success" />
                </div>
                <div className="flex-1">
                  <h4 className="font-semibold text-text-primary mb-1">Export Ready</h4>
                  <p className="text-sm text-text-secondary mb-3">
                    Your data export is being prepared. You'll be able to download it from the
                    link below or from your email.
                  </p>
                  <div className="text-xs text-text-muted">
                    Export ID: {exportId}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Additional Options */}
        <Card>
          <CardHeader>
            <CardTitle>Additional Options</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Link href="/settings/delete-account">
              <div className="p-4 rounded-lg border border-accent-danger/30 hover:bg-accent-danger/5 transition-colors">
                <h4 className="font-semibold text-accent-danger mb-1">Delete Account</h4>
                <p className="text-sm text-text-secondary">
                  Permanently delete your account and all associated data. This action cannot be
                  undone.
                </p>
              </div>
            </Link>

            <Link href="/settings/privacy">
              <div className="p-4 rounded-lg border border-border-default hover:bg-bg-elevated transition-colors">
                <h4 className="font-semibold text-text-primary mb-1">Privacy Policy</h4>
                <p className="text-sm text-text-secondary">
                  Learn how we collect, use, and protect your personal data.
                </p>
              </div>
            </Link>
          </CardContent>
        </Card>
      </div>
    </PageContainer>
  );
}
