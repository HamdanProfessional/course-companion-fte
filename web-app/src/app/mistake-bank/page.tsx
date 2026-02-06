'use client';

/**
 * Mistake Bank Page - Review and learn from your mistakes
 *
 * Features:
 * - Automatic cataloging of all wrong answers
 * - Filter by category, difficulty, mastery status
 * - Search functionality
 * - Mark mistakes as mastered
 * - Statistics and insights
 * - Export/Import functionality
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingSpinner } from '@/components/ui/Loading';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import {
  AlertCircle,
  CheckCircle2,
  TrendingUp,
  Search,
  Filter,
  Trash2,
  Download,
  Upload,
  RotateCcw,
  BookOpen,
  Brain,
  Award,
  XCircle,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import {
  getMistakes,
  getMistakeStats,
  markAsMastered,
  markForReview,
  deleteMistake,
  clearMastered,
  clearAllMistakes,
  filterMistakes,
  searchMistakes,
  exportMistakes,
  importMistakes,
  getMistakesForReview,
  type Mistake,
} from '@/lib/mistakeBank';

export default function MistakeBankPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [mistakes, setMistakes] = useState<Mistake[]>([]);
  const [stats, setStats] = useState(getMistakeStats());
  const [selectedMistake, setSelectedMistake] = useState<Mistake | null>(null);

  // Filter states
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [difficultyFilter, setDifficultyFilter] = useState<string>('all');
  const [masteryFilter, setMasteryFilter] = useState<string>('all');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    const userId = localStorage.getItem('user_id');
    if (!userId) {
      router.push('/login');
      return;
    }
    loadMistakes();
    setIsLoading(false);
  }, [router]);

  const loadMistakes = () => {
    const allMistakes = getMistakes();
    setMistakes(allMistakes);
    setStats(getMistakeStats());
  };

  // Apply filters
  const getFilteredMistakes = () => {
    let filtered = mistakes;

    // Search filter
    if (searchQuery) {
      filtered = searchMistakes(searchQuery);
    }

    // Category filter
    if (categoryFilter !== 'all') {
      filtered = filtered.filter(m => m.category === categoryFilter);
    }

    // Difficulty filter
    if (difficultyFilter !== 'all') {
      filtered = filtered.filter(m => m.difficulty === difficultyFilter);
    }

    // Mastery filter
    if (masteryFilter === 'mastered') {
      filtered = filtered.filter(m => m.mastered);
    } else if (masteryFilter === 'review') {
      filtered = filtered.filter(m => !m.mastered);
    }

    return filtered;
  };

  const filteredMistakes = getFilteredMistakes();

  // Get unique categories and difficulties
  const categories = ['all', ...Array.from(new Set(mistakes.map(m => m.category || 'General')))];
  const difficulties = ['all', ...Array.from(new Set(mistakes.map(m => m.difficulty)))];

  // Handle mastery toggle
  const handleToggleMastery = (mistake: Mistake) => {
    if (mistake.mastered) {
      markForReview(mistake.id);
    } else {
      markAsMastered(mistake.id);
    }
    loadMistakes();
  };

  // Handle delete
  const handleDelete = (mistakeId: string) => {
    if (confirm('Are you sure you want to delete this mistake?')) {
      deleteMistake(mistakeId);
      loadMistakes();
    }
  };

  // Handle clear mastered
  const handleClearMastered = () => {
    if (confirm('Remove all mastered mistakes from the bank?')) {
      clearMastered();
      loadMistakes();
    }
  };

  // Handle clear all
  const handleClearAll = () => {
    if (confirm('Are you sure you want to delete ALL mistakes? This cannot be undone.')) {
      clearAllMistakes();
      loadMistakes();
    }
  };

  // Handle export
  const handleExport = () => {
    const data = exportMistakes();
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `mistake-bank-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Handle import
  const handleImport = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'application/json';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
          const content = event.target?.result as string;
          if (importMistakes(content)) {
            alert('Mistakes imported successfully!');
            loadMistakes();
          } else {
            alert('Failed to import mistakes. Please check the file format.');
          }
        };
        reader.readAsText(file);
      }
    };
    input.click();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <PageContainer>
      <PageHeader
        title="Mistake Bank"
        description="Review your mistakes and ensure you don't make them again"
      />

      {/* Statistics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-danger/20 to-accent-danger/10 flex items-center justify-center">
                <AlertCircle className="w-6 h-6 text-accent-danger" />
              </div>
            </div>
            <h3 className="text-3xl font-bold text-text-primary">{stats.total}</h3>
            <p className="text-sm text-text-secondary">Total Mistakes</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-warning/20 to-accent-warning/10 flex items-center justify-center">
                <RotateCcw className="w-6 h-6 text-accent-warning" />
              </div>
            </div>
            <h3 className="text-3xl font-bold text-text-primary">{stats.remaining}</h3>
            <p className="text-sm text-text-secondary">Need Review</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-success/20 to-accent-success/10 flex items-center justify-center">
                <CheckCircle2 className="w-6 h-6 text-accent-success" />
              </div>
            </div>
            <h3 className="text-3xl font-bold text-accent-success">{stats.mastered}</h3>
            <p className="text-sm text-text-secondary">Mastered</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-cosmic-primary" />
              </div>
            </div>
            <h3 className="text-3xl font-bold text-text-primary">
              {stats.total > 0 ? Math.round((stats.mastered / stats.total) * 100) : 0}%
            </h3>
            <p className="text-sm text-text-secondary">Mastery Rate</p>
          </CardContent>
        </Card>
      </div>

      {/* Repeat Mistakes Alert */}
      {stats.repeatMistakes.length > 0 && (
        <Card className="mb-8 bg-gradient-to-r from-accent-warning/10 to-accent-danger/10 border-accent-warning/30">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-warning/20 to-accent-warning/10 flex items-center justify-center flex-shrink-0">
                <Brain className="w-6 h-6 text-accent-warning" />
              </div>
              <div className="flex-1">
                <h3 className="text-xl font-bold text-text-primary mb-2">
                  Repeat Mistakes Detected
                </h3>
                <p className="text-text-secondary mb-4">
                  You've made the same mistake multiple times. Focus on these topics to strengthen your understanding.
                </p>
                <div className="flex flex-wrap gap-2">
                  {stats.repeatMistakes.slice(0, 3).map((mistake) => (
                    <Badge key={mistake.id} variant="warning" className="text-sm">
                      {mistake.questionText.substring(0, 40)}...
                      <span className="ml-2 opacity-75">({mistake.timesWrong}x)</span>
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Search and Filters */}
      <Card className="mb-6">
        <CardContent className="p-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-text-muted" />
              <input
                type="text"
                placeholder="Search mistakes..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 rounded-lg border border-border-default bg-bg-elevated text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-cosmic-primary"
              />
            </div>
            <Button
              variant="outline"
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2"
            >
              <Filter className="w-4 h-4" />
              Filters
              {showFilters ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </Button>
          </div>

          {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-border-default">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Category
                </label>
                <select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  className="w-full px-4 py-2 rounded-lg border border-border-default bg-bg-elevated text-text-primary focus:outline-none focus:ring-2 focus:ring-cosmic-primary"
                >
                  {categories.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat === 'all' ? 'All Categories' : cat}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Difficulty
                </label>
                <select
                  value={difficultyFilter}
                  onChange={(e) => setDifficultyFilter(e.target.value)}
                  className="w-full px-4 py-2 rounded-lg border border-border-default bg-bg-elevated text-text-primary focus:outline-none focus:ring-2 focus:ring-cosmic-primary"
                >
                  {difficulties.map((diff) => (
                    <option key={diff} value={diff}>
                      {diff === 'all' ? 'All Difficulties' : diff}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Status
                </label>
                <select
                  value={masteryFilter}
                  onChange={(e) => setMasteryFilter(e.target.value)}
                  className="w-full px-4 py-2 rounded-lg border border-border-default bg-bg-elevated text-text-primary focus:outline-none focus:ring-2 focus:ring-cosmic-primary"
                >
                  <option value="all">All Status</option>
                  <option value="review">Need Review</option>
                  <option value="mastered">Mastered</option>
                </select>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-3 mb-6">
        <Button variant="outline" onClick={handleExport} className="flex items-center gap-2">
          <Download className="w-4 h-4" />
          Export
        </Button>
        <Button variant="outline" onClick={handleImport} className="flex items-center gap-2">
          <Upload className="w-4 h-4" />
          Import
        </Button>
        {stats.mastered > 0 && (
          <Button variant="outline" onClick={handleClearMastered} className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4" />
            Clear Mastered
          </Button>
        )}
        <Button variant="danger" onClick={handleClearAll} className="flex items-center gap-2">
          <Trash2 className="w-4 h-4" />
          Clear All
        </Button>
      </div>

      {/* Mistakes List */}
      {filteredMistakes.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-accent-success/20 to-accent-success/10 flex items-center justify-center mx-auto mb-4">
              <Award className="w-10 h-10 text-accent-success" />
            </div>
            <h3 className="text-2xl font-bold text-text-primary mb-2">No Mistakes Found!</h3>
            <p className="text-text-secondary mb-6">
              {searchQuery || categoryFilter !== 'all' || difficultyFilter !== 'all' || masteryFilter !== 'all'
                ? 'Try adjusting your filters or search query.'
                : 'Great job! Keep taking quizzes to build your mistake bank.'}
            </p>
            <Button variant="primary" onClick={() => router.push('/chapters')}>
              <BookOpen className="w-4 h-4 mr-2" />
              Take a Quiz
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-text-secondary">
              Showing {filteredMistakes.length} of {stats.total} mistakes
            </p>
          </div>

          {filteredMistakes.map((mistake) => (
            <Card
              key={mistake.id}
              className={`transition-all hover:shadow-lg ${
                mistake.mastered
                  ? 'bg-accent-success/5 border-accent-success/20'
                  : 'bg-bg-elevated border-border-default'
              }`}
            >
              <CardContent className="p-6">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    {/* Header */}
                    <div className="flex items-start gap-3 mb-3">
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                          mistake.mastered
                            ? 'bg-accent-success/20'
                            : 'bg-accent-danger/20'
                        }`}
                      >
                        {mistake.mastered ? (
                          <CheckCircle2 className="w-5 h-5 text-accent-success" />
                        ) : (
                          <XCircle className="w-5 h-5 text-accent-danger" />
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 flex-wrap mb-2">
                          <Badge
                            variant={mistake.mastered ? 'success' : 'danger'}
                            className="text-xs"
                          >
                            {mistake.mastered ? 'Mastered' : 'Needs Review'}
                          </Badge>
                          <Badge variant="info" className="text-xs">
                            {mistake.difficulty}
                          </Badge>
                          {mistake.timesWrong > 1 && (
                            <Badge variant="warning" className="text-xs">
                              {mistake.timesWrong}x wrong
                            </Badge>
                          )}
                          <span className="text-xs text-text-muted">
                            {new Date(mistake.date).toLocaleDateString()}
                          </span>
                        </div>
                        <p className="font-semibold text-text-primary">
                          {mistake.questionText}
                        </p>
                        {mistake.category && (
                          <p className="text-xs text-text-muted mt-1">
                            Category: {mistake.category}
                          </p>
                        )}
                      </div>
                    </div>

                    {/* Wrong vs Correct Answer */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                      <div className="p-3 rounded-lg bg-accent-danger/10 border border-accent-danger/30">
                        <p className="text-xs font-semibold text-accent-danger mb-1">
                          Your Answer
                        </p>
                        <p className="text-sm text-text-secondary">{mistake.wrongAnswer}</p>
                      </div>
                      <div className="p-3 rounded-lg bg-accent-success/10 border border-accent-success/30">
                        <p className="text-xs font-semibold text-accent-success mb-1">
                          Correct Answer
                        </p>
                        <p className="text-sm text-text-secondary">{mistake.correctAnswer}</p>
                      </div>
                    </div>

                    {/* Explanation */}
                    {mistake.explanation && (
                      <div className="p-3 rounded-lg bg-cosmic-primary/10 border border-cosmic-primary/30">
                        <p className="text-xs font-semibold text-cosmic-primary mb-1">
                          Explanation
                        </p>
                        <p className="text-sm text-text-secondary">{mistake.explanation}</p>
                      </div>
                    )}

                    {/* AI Feedback */}
                    {mistake.feedback && (
                      <div className="p-3 rounded-lg bg-accent-secondary/10 border border-accent-secondary/30 mt-3">
                        <p className="text-xs font-semibold text-accent-secondary mb-1">
                          AI Feedback
                        </p>
                        <p className="text-sm text-text-secondary">{mistake.feedback}</p>
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex flex-col gap-2">
                    <Button
                      variant={mistake.mastered ? 'outline' : 'success'}
                      size="sm"
                      onClick={() => handleToggleMastery(mistake)}
                    >
                      {mistake.mastered ? (
                        <>
                          <RotateCcw className="w-4 h-4 mr-1" />
                          Review
                        </>
                      ) : (
                        <>
                          <CheckCircle2 className="w-4 h-4 mr-1" />
                          Mastered
                        </>
                      )}
                    </Button>
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleDelete(mistake.id)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Tips Card */}
      <Card className="mt-8 bg-gradient-to-r from-cosmic-primary/10 to-cosmic-purple/10 border-cosmic-primary/30">
        <CardContent className="p-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cosmic-primary to-cosmic-purple flex items-center justify-center flex-shrink-0">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-text-primary mb-2">
                How to Use the Mistake Bank
              </h3>
              <ul className="space-y-2 text-text-secondary">
                <li className="flex items-start gap-2">
                  <span className="text-accent-primary mt-1">•</span>
                  <span>Review your mistakes regularly to reinforce correct understanding</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-accent-primary mt-1">•</span>
                  <span>Focus on repeat mistakes (marked with {`{times}x`}) - these need extra attention</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-accent-primary mt-1">•</span>
                  <span>Mark mistakes as "Mastered" when you fully understand the concept</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-accent-primary mt-1">•</span>
                  <span>Export your mistakes for backup or to share with your teacher</span>
                </li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </PageContainer>
  );
}
