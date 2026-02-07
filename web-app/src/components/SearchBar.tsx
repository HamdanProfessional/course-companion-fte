'use client';

/**
 * SearchBar Component - Phase 3
 *
 * Global search functionality for course content.
 * Supports keyword search with real-time results.
 */

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent } from './ui/Card';
import { LoadingSpinner } from './ui/Loading';
import { useV3Search } from '@/hooks/useV3';

interface SearchBarProps {
  className?: string;
  placeholder?: string;
}

export function SearchBar({ className, placeholder = 'Search course content...' }: SearchBarProps) {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const router = useRouter();
  const searchRef = useRef<HTMLDivElement>(null);

  // Debounced search
  const [debouncedQuery, setDebouncedQuery] = useState('');
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
    }, 300);
    return () => clearTimeout(timer);
  }, [query]);

  const { data: searchResults, isLoading } = useV3Search(debouncedQuery);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      router.push(`/search?q=${encodeURIComponent(query)}`);
      setIsOpen(false);
    }
  };

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
    return safeText.replace(regex, '<mark class="bg-accent-warning/30 text-text-primary">$1</mark>');
  };

  const hasResults = searchResults && searchResults.results && searchResults.results.length > 0;

  return (
    <div ref={searchRef} className={`relative ${className}`}>
      <form onSubmit={handleSearch}>
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setIsOpen(true);
            }}
            onFocus={() => setIsOpen(true)}
            placeholder={placeholder}
            className="w-full px-4 py-2 pl-10 rounded-lg border border-border-default bg-bg-elevated text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent-primary focus:border-transparent"
          />
          <svg
            className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-text-muted"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          {query && (
            <button
              type="button"
              onClick={() => {
                setQuery('');
                setIsOpen(false);
              }}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      </form>

      {/* Dropdown Results */}
      {isOpen && query.length >= 2 && (
        <div className="absolute z-50 w-full mt-2">
          <Card className="max-h-96 overflow-y-auto">
            <CardContent className="p-0">
              {isLoading ? (
                <div className="p-4 flex items-center justify-center">
                  <LoadingSpinner size="sm" />
                </div>
              ) : hasResults ? (
                <div className="divide-y divide-border-default">
                  {searchResults.results.map((result: any, index: number) => (
                    <a
                      key={index}
                      href={`/chapters/${result.chapter_id}`}
                      onClick={() => setIsOpen(false)}
                      className="block p-4 hover:bg-bg-hover transition-colors"
                    >
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded bg-accent-primary/10 flex items-center justify-center flex-shrink-0">
                          <span className="text-accent-primary text-sm font-bold">
                            {result.title.charAt(0)}
                          </span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4
                            className="font-medium text-text-primary text-sm"
                            dangerouslySetInnerHTML={{
                              __html: highlightMatch(result.title, query),
                            }}
                          />
                          <p
                            className="text-sm text-text-muted mt-1 line-clamp-2"
                            dangerouslySetInnerHTML={{
                              __html: highlightMatch(result.snippet, query),
                            }}
                          />
                          <div className="flex items-center gap-2 mt-2">
                            <span className="text-xs text-text-muted">
                              Chapter {result.chapter_id}
                            </span>
                            {result.relevance_score && (
                              <span className="text-xs text-accent-secondary">
                                {Math.round(result.relevance_score * 100)}% match
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </a>
                  ))}
                </div>
              ) : (
                <div className="p-4 text-center text-text-muted">
                  <div className="w-12 h-12 mx-auto mb-2 rounded-lg bg-bg-elevated flex items-center justify-center">
                    <svg className="w-6 h-6 text-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </div>
                  <p className="text-sm">No results found for "{query}"</p>
                  <p className="text-xs mt-1">Try different keywords</p>
                </div>
              )}

              {hasResults && (
                <div className="p-3 border-t border-border-default bg-bg-elevated">
                  <a
                    href={`/search?q=${encodeURIComponent(query)}`}
                    onClick={() => setIsOpen(false)}
                    className="text-sm text-accent-primary hover:underline"
                  >
                    See all {searchResults.total} results →
                  </a>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
