'use client';

/**
 * Search Results Page - Phase 3
 *
 * Dedicated page for displaying comprehensive search results.
 * Supports keyword search with filtering and sorting.
 */

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/Loading';
import { Badge } from '@/components/ui/Badge';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import { SearchBar } from '@/components/SearchBar';
import { useV3Search } from '@/hooks/useV3';

export default function SearchPage() {
  const searchParams = useSearchParams();
  const query = searchParams.get('q') || '';
  const [filterType, setFilterType] = useState<'all' | 'beginner' | 'intermediate' | 'advanced'>('all');
  const router = useRouter();

  const { data: searchResults, isLoading } = useV3Search(query, 50);

  const filteredResults = searchResults?.results?.filter((result: any) => {
    if (filterType === 'all') return true;
    // Would need difficulty level in search results
    return true;
  }) || [];

  const highlightMatch = (text: string, query: string) => {
    if (!query) return text;

    // Escape HTML special characters in text to prevent XSS
    const escapeHtml = (str: string) => {
      const div = document.createElement('div');
      div.textContent = str;
      return div.innerHTML;
    };

    const safeText = escapeHtml(text);
    const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

    const regex = new RegExp(`(${escapedQuery})`, 'gi');
    return safeText.replace(regex, '<mark class="bg-accent-warning/30 text-text-primary px-0.5 rounded">$1</mark>');
  };

  return (
    <PageContainer>
      <PageHeader
        title="Search"
        description="Find what you need across all course content"
      />

      {/* Search Bar */}
      <div className="max-w-2xl mx-auto mb-8">
        <SearchBar placeholder={query || 'Search course content...'} />
      </div>

      {query && (
        <>
          {/* Results Summary */}
          <div className="mb-6">
            <div className="flex items-center justify-between">
              <p className="text-text-secondary">
                {isLoading ? (
                  'Searching...'
                ) : (
                  <>
                    Found {searchResults?.total || 0} result{searchResults?.total !== 1 ? 's' : ''} for "{query}"
                  </>
                )}
              </p>

              {/* Filters */}
              <div className="flex gap-2">
                <button
                  onClick={() => setFilterType('all')}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition-all ${
                    filterType === 'all'
                      ? 'bg-accent-primary text-white'
                      : 'bg-bg-elevated text-text-secondary hover:bg-bg-hover'
                  }`}
                >
                  All
                </button>
                <button
                  onClick={() => setFilterType('beginner')}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition-all ${
                    filterType === 'beginner'
                      ? 'bg-accent-primary text-white'
                      : 'bg-bg-elevated text-text-secondary hover:bg-bg-hover'
                  }`}
                >
                  Beginner
                </button>
                <button
                  onClick={() => setFilterType('intermediate')}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition-all ${
                    filterType === 'intermediate'
                      ? 'bg-accent-primary text-white'
                      : 'bg-bg-elevated text-text-secondary hover:bg-bg-hover'
                  }`}
                >
                  Intermediate
                </button>
                <button
                  onClick={() => setFilterType('advanced')}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition-all ${
                    filterType === 'advanced'
                      ? 'bg-accent-primary text-white'
                      : 'bg-bg-elevated text-text-secondary hover:bg-bg-hover'
                  }`}
                >
                  Advanced
                </button>
              </div>
            </div>
          </div>

          {/* Results */}
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <LoadingSpinner size="lg" />
            </div>
          ) : filteredResults.length > 0 ? (
            <div className="space-y-4">
              {filteredResults.map((result: any, index: number) => (
                <Card key={index} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-start gap-4">
                      {/* Chapter Icon/Number */}
                      <div className="w-12 h-12 rounded-lg bg-accent-primary/10 flex items-center justify-center flex-shrink-0">
                        <span className="text-accent-primary font-bold">
                          {result.title.charAt(0)}
                        </span>
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <a href={`/chapters/${result.chapter_id}`}>
                          <h3
                            className="text-lg font-semibold text-text-primary hover:text-accent-primary transition-colors"
                            dangerouslySetInnerHTML={{
                              __html: highlightMatch(result.title, query),
                            }}
                          />
                        </a>

                        <p
                          className="text-text-secondary mt-2 line-clamp-2"
                          dangerouslySetInnerHTML={{
                            __html: highlightMatch(result.snippet, query),
                          }}
                        />

                        <div className="flex items-center gap-3 mt-3">
                          <Badge variant="info">Chapter {result.chapter_id}</Badge>
                          {result.relevance_score && (
                            <span className="text-xs text-text-muted">
                              {Math.round(result.relevance_score * 100)}% relevant
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Action */}
                      <a href={`/chapters/${result.chapter_id}`}>
                        <Button variant="outline" size="sm">
                          View →
                        </Button>
                      </a>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            /* No Results */
            <Card>
              <CardContent className="p-12 text-center">
                <div className="text-6xl mb-4">🔍</div>
                <h3 className="text-xl font-semibold text-text-primary mb-2">
                  No results found
                </h3>
                <p className="text-text-secondary mb-6">
                  We couldn't find any content matching "{query}"
                </p>
                <div className="max-w-md mx-auto">
                  <p className="text-sm text-text-muted mb-4">Try:</p>
                  <ul className="text-sm text-text-secondary space-y-2">
                    <li>• Using different keywords</li>
                    <li>• Checking for typos</li>
                    <li>• Using more general terms</li>
                    <li>• Browsing chapters directly</li>
                  </ul>
                </div>
                <div className="mt-6">
                  <Button variant="primary" onClick={() => router.push('/chapters')}>
                    Browse All Chapters
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}

      {!query && (
        /* Initial State */
        <Card>
          <CardContent className="p-12 text-center">
            <div className="text-6xl mb-4">🔎</div>
            <h3 className="text-xl font-semibold text-text-primary mb-2">
              Search Course Content
            </h3>
            <p className="text-text-secondary mb-6">
              Enter keywords above to search across all chapters, quizzes, and learning materials.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mx-auto mt-8">
              <div className="p-4 rounded-lg bg-bg-elevated">
                <div className="text-2xl mb-2">📖</div>
                <h4 className="font-medium text-text-primary mb-1">Chapters</h4>
                <p className="text-xs text-text-muted">Search all course content</p>
              </div>
              <div className="p-4 rounded-lg bg-bg-elevated">
                <div className="text-2xl mb-2">❓</div>
                <h4 className="font-medium text-text-primary mb-1">Quizzes</h4>
                <p className="text-xs text-text-muted">Find quiz questions</p>
              </div>
              <div className="p-4 rounded-lg bg-bg-elevated">
                <div className="text-2xl mb-2">💡</div>
                <h4 className="font-medium text-text-primary mb-1">Concepts</h4>
                <p className="text-xs text-text-muted">Explore topics</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </PageContainer>
  );
}
