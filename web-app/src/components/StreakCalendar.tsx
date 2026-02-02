'use client';

/**
 * StreakCalendar Component - Phase 3 Gamification
 *
 * Visual calendar showing daily activity and streak information.
 * Helps users track their learning consistency over time.
 */

import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { Badge } from './uiBadge';
import { LoadingSpinner } from './ui/Loading';
import { useV3StreakCalendar } from '@/hooks/useV3';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { useState } from 'react';

interface StreakCalendarProps {
  className?: string;
}

export function StreakCalendar({ className }: StreakCalendarProps) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const { data: calendarData, isLoading } = useV3StreakCalendar(
    currentDate.getFullYear(),
    currentDate.getMonth() + 1
  );

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  const goToPreviousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1));
  };

  const goToNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1));
  };

  const getDaysInMonth = (year: number, month: number) => {
    return new Date(year, month, 0).getDate();
  };

  const getFirstDayOfMonth = (year: number, month: number) => {
    return new Date(year, month - 1, 1).getDay();
  };

  const renderCalendar = () => {
    if (!calendarData) return null;

    const year = currentDate.getFullYear();
    const month = currentDate.getMonth() + 1;
    const daysInMonth = getDaysInMonth(year, month);
    const firstDay = getFirstDayOfMonth(year, month);

    const days = [];

    // Day headers
    days.push(
      <div key="headers" className="grid grid-cols-7 gap-1 mb-2">
        {dayNames.map(day => (
          <div key={day} className="text-center text-xs font-semibold text-text-secondary py-2">
            {day}
          </div>
        ))}
      </div>
    );

    // Calendar grid
    const gridCells = [];

    // Empty cells for days before the first day of the month
    for (let i = 0; i < firstDay; i++) {
      gridCells.push(<div key={`empty-${i}`} className="aspect-square" />);
    }

    // Days of the month
    if (calendarData.days) {
      for (let day = 1; day <= daysInMonth; day++) {
        const dayData = calendarData.days.find(d => {
          const d = new Date(d.date);
          return d.getDate() === day &&
                 d.getMonth() === month - 1 &&
                 d.getFullYear() === year;
        });

        const isActive = dayData?.active || false;
        const streakDay = dayData?.streak_day || null;

        gridCells.push(
          <div
            key={day}
            className={`aspect-square rounded-lg flex items-center justify-center text-sm font-medium transition-all ${
              isActive
                ? 'bg-accent-primary text-white shadow-lg'
                : 'bg-bg-elevated text-text-secondary hover:bg-bg-hover'
            }`}
            title={isActive ? `Day ${streakDay} of your streak!` : 'No activity'}
          >
            {day}
            {isActive && streakDay && (
              <span className="absolute -top-1 -right-1 w-3 h-3 bg-accent-warning rounded-full text-[8px] flex items-center justify-center">
                🔥
              </span>
            )}
          </div>
        );
      }
    }

    days.push(
      <div key="grid" className="grid grid-cols-7 gap-1">
        {gridCells}
      </div>
    );

    return days;
  };

  if (isLoading) {
    return (
      <Card className={className}>
        <CardContent className="p-6">
          <div className="flex items-center justify-center h-64">
            <LoadingSpinner size="md" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-3">
            <span className="text-2xl">📅</span>
            Streak Calendar
          </CardTitle>
          <div className="flex items-center gap-2">
            <button
              onClick={goToPreviousMonth}
              className="p-2 rounded-lg hover:bg-bg-elevated transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <span className="text-sm font-semibold text-text-primary min-w-[140px] text-center">
              {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
            </span>
            <button
              onClick={goToNextMonth}
              className="p-2 rounded-lg hover:bg-bg-elevated transition-colors"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {calendarData && (
          <div className="space-y-6">
            {/* Stats */}
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-4 rounded-lg bg-bg-elevated">
                <div className="text-2xl font-bold text-accent-primary">
                  {calendarData.current_streak}
                </div>
                <div className="text-xs text-text-muted">Current Streak</div>
              </div>
              <div className="text-center p-4 rounded-lg bg-bg-elevated">
                <div className="text-2xl font-bold text-accent-warning">
                  {calendarData.longest_streak}
                </div>
                <div className="text-xs text-text-muted">Longest Streak</div>
              </div>
              <div className="text-center p-4 rounded-lg bg-bg-elevated">
                <div className="text-2xl font-bold text-accent-success">
                  {calendarData.total_active_days}
                </div>
                <div className="text-xs text-text-muted">Active Days</div>
              </div>
            </div>

            {/* Calendar */}
            <div className="p-4 rounded-lg bg-bg-secondary">
              {renderCalendar()}
            </div>

            {/* Legend */}
            <div className="flex items-center justify-center gap-6 text-xs text-text-muted">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded bg-accent-primary"></div>
                <span>Active day</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded bg-bg-elevated"></div>
                <span>No activity</span>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
