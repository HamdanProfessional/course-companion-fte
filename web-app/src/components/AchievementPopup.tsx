'use client';

/**
 * AchievementPopup Component - Phase 3 Gamification
 *
 * Celebratory popup for unlocked achievements with confetti animation.
 * Provides positive reinforcement for learner progress.
 */

import { useEffect, useState } from 'react';
import { Card } from './ui/Card';
import { Button } from './ui/Button';
import type { AchievementItem } from '@/lib/api-v3';

interface AchievementPopupProps {
  achievement: AchievementItem;
  isVisible: boolean;
  onClose: () => void;
}

export function AchievementPopup({ achievement, isVisible, onClose }: AchievementPopupProps) {
  const [showConfetti, setShowConfetti] = useState(false);

  useEffect(() => {
    if (isVisible) {
      setShowConfetti(true);
      // Play celebration sound if available
      // const audio = new Audio('/sounds/achievement.mp3');
      // audio.play().catch(() => {}); // Ignore autoplay errors
    }
  }, [isVisible]);

  if (!isVisible) return null;

  const rarityColors = {
    common: 'from-gray-500 to-gray-600',
    rare: 'from-blue-500 to-blue-600',
    epic: 'from-purple-500 to-purple-600',
    legendary: 'from-yellow-500 to-orange-500',
  };

  const rarityGlow = {
    common: 'shadow-gray-500/50',
    rare: 'shadow-blue-500/50',
    epic: 'shadow-purple-500/50',
    legendary: 'shadow-yellow-500/50',
  };

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        {/* Confetti Effect */}
        {showConfetti && <Confetti />}

        {/* Popup */}
        <div
          className="relative max-w-md w-full animate-achievement-pop"
          onClick={e => e.stopPropagation()}
        >
          <Card className="overflow-hidden">
            {/* Header with gradient background */}
            <div className={`bg-gradient-to-br ${rarityColors[achievement.rarity]} p-8 text-center relative`}>
              {/* Glow effect */}
              <div className={`absolute inset-0 ${rarityGlow[achievement.rarity]} blur-2xl opacity-30`}></div>

              {/* Icon */}
              <div className="relative text-7xl mb-4 animate-bounce">
                {achievement.icon}
              </div>

              {/* Achievement Badge */}
              <div className="relative">
                <div className="inline-block px-4 py-1 rounded-full bg-white/20 backdrop-blur-sm text-white text-sm font-semibold uppercase tracking-wide">
                  {achievement.rarity}
                </div>
              </div>
            </div>

            {/* Content */}
            <div className="p-6 text-center bg-bg-elevated">
              <h2 className="text-2xl font-bold text-text-primary mb-2">
                Achievement Unlocked!
              </h2>
              <h3 className="text-xl font-semibold text-accent-primary mb-3">
                {achievement.name}
              </h3>
              <p className="text-text-secondary mb-6">
                {achievement.description}
              </p>

              {/* Progress bar (if partial progress) */}
              {achievement.progress > 0 && achievement.progress < 100 && (
                <div className="mb-6">
                  <div className="w-full h-2 bg-bg-secondary rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-accent-primary to-accent-secondary transition-all duration-500"
                      style={{ width: `${achievement.progress}%` }}
                    />
                  </div>
                  <p className="text-xs text-text-muted mt-2">
                    {Math.round(achievement.progress)}% complete
                  </p>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-3">
                <Button variant="primary" onClick={onClose} className="flex-1">
                  Awesome!
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    // Share functionality
                    if (navigator.share) {
                      navigator.share({
                        title: `I just unlocked "${achievement.name}" in Course Companion!`,
                        text: achievement.description,
                      }).catch(() => {});
                    }
                  }}
                >
                  Share
                </Button>
              </div>
            </div>
          </Card>
        </div>
      </div>

      <style jsx>{`
        @keyframes achievement-pop {
          0% {
            transform: scale(0.5);
            opacity: 0;
          }
          50% {
            transform: scale(1.05);
          }
          100% {
            transform: scale(1);
            opacity: 1;
          }
        }
        .animate-achievement-pop {
          animation: achievement-pop 0.5s ease-out forwards;
        }
      `}</style>
    </>
  );
}

/**
 * Confetti component for celebration animation
 */
function Confetti() {
  const colors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A',
    '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2'
  ];

  const confetti = Array.from({ length: 50 }, (_, i) => {
    const style: React.CSSProperties = {
      position: 'fixed',
      width: Math.random() * 10 + 5 + 'px',
      height: Math.random() * 5 + 5 + 'px',
      backgroundColor: colors[Math.floor(Math.random() * colors.length)],
      left: Math.random() * 100 + '%',
      top: '-20px',
      opacity: Math.random() * 0.7 + 0.3,
      transform: `rotate(${Math.random() * 360}deg)`,
      animation: `confetti-fall ${Math.random() * 2 + 2}s linear forwards`,
      animationDelay: Math.random() * 0.5 + 's',
      pointerEvents: 'none',
    };

    return <div key={i} style={style} />;
  });

  return (
    <>
      {confetti}
      <style jsx>{`
        @keyframes confetti-fall {
          0% {
            top: '-20px';
            transform: translateX(0) rotate(0deg);
          }
          100% {
            top: '100vh';
            transform: translateX(${Math.random() * 200 - 100}px) rotate(720deg);
          }
        }
      `}</style>
    </>
  );
}

/**
 * Hook to trigger achievement popup
 */
export function useAchievementPopup() {
  const [achievement, setAchievement] = useState<AchievementItem | null>(null);
  const [isVisible, setIsVisible] = useState(false);

  const showAchievement = (ach: AchievementItem) => {
    setAchievement(ach);
    setIsVisible(true);

    // Auto-hide after 5 seconds
    setTimeout(() => {
      setIsVisible(false);
    }, 5000);
  };

  const closePopup = () => {
    setIsVisible(false);
  };

  return {
    achievement,
    isVisible,
    showAchievement,
    closePopup,
  };
}
