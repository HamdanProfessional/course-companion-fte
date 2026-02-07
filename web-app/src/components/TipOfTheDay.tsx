'use client';

/**
 * TipOfTheDay Component - Displays a random learning tip on the dashboard
 * Part of the gamification features
 */

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Lightbulb, RefreshCw } from 'lucide-react';
import { GlassCard } from '@/components/ui/GlassCard';
import { Badge } from '@/components/ui/Badge';
import { tutorApi, TipItem } from '@/lib/api-v3';

interface TipOfTheDayProps {
  className?: string;
}

export function TipOfTheDay({ className = '' }: TipOfTheDayProps) {
  const [tip, setTip] = useState<TipItem | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchTip = async (showRefreshAnimation = false) => {
    try {
      if (showRefreshAnimation) {
        setIsRefreshing(true);
      } else {
        setIsLoading(true);
      }

      const randomTip = await tutorApi.getRandomTip();
      setTip(randomTip);
    } catch (error) {
      console.error('Failed to fetch tip:', error);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchTip();
  }, []);

  const handleRefresh = () => {
    fetchTip(true);
  };

  const getCategoryBadge = (category: string) => {
    const badges: Record<string, { variant: 'beginner' | 'intermediate' | 'advanced' | 'success' | 'warning' | 'cosmic'; label: string }> = {
      study_habits: { variant: 'beginner', label: 'Study Habits' },
      quiz_strategy: { variant: 'intermediate', label: 'Quiz Strategy' },
      motivation: { variant: 'success', label: 'Motivation' },
      course_tips: { variant: 'cosmic', label: 'Course Tips' },
    };
    return badges[category] || { variant: 'beginner' as const, label: category };
  };

  if (isLoading) {
    return (
      <GlassCard className={`p-6 ${className}`}>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-cosmic-primary/20 animate-pulse" />
          <div className="flex-1">
            <div className="h-4 bg-glass-border rounded animate-pulse mb-2" />
            <div className="h-3 bg-glass-border rounded animate-pulse w-3/4" />
          </div>
        </div>
      </GlassCard>
    );
  }

  if (!tip) {
    return null;
  }

  const categoryBadge = getCategoryBadge(tip.category);

  return (
    <GlassCard className={`p-6 ${className}`}>
      <div className="flex items-start gap-4">
        <motion.div
          animate={{ rotate: isRefreshing ? 360 : 0 }}
          transition={{ duration: 0.5 }}
          className="flex-shrink-0"
        >
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cosmic-primary to-cosmic-purple flex items-center justify-center">
            <Lightbulb className="w-5 h-5 text-white" />
          </div>
        </motion.div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="font-semibold text-text-primary">Tip of the Day</h3>
            <Badge variant={categoryBadge.variant}>{categoryBadge.label}</Badge>
          </div>

          <p className="text-text-secondary text-sm leading-relaxed">
            {tip.content}
          </p>

          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="mt-3 flex items-center gap-2 text-sm text-cosmic-primary hover:text-cosmic-purple transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            {isRefreshing ? 'Loading...' : 'Get another tip'}
          </button>
        </div>
      </div>
    </GlassCard>
  );
}
