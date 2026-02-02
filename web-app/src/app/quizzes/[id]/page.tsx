'use client';

/**
 * Quiz taking page with Professional/Modern SaaS theme.
 * One-question-at-a-time UI with keyboard navigation.
 * Phase 3: LLM-powered grading support
 */
import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/Loading';
import { Badge } from '@/components/ui/Badge';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import { Breadcrumbs } from '@/components/layout/Breadcrumbs';
import { useQuiz, useCanAccessPhase2 } from '@/hooks';
import { useV3QuizSubmit } from '@/hooks/useV3';
import type { QuizSubmission, QuizGradingResult } from '@/lib/api-v3';
import Link from 'next/link';

type GradingMode = 'auto' | 'llm' | 'hybrid';

export default function QuizPage({ params }: { params: { id: string } }) {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [openEndedAnswers, setOpenEndedAnswers] = useState<Record<string, string>>({});
  const [showResults, setShowResults] = useState(false);
  const [gradingMode, setGradingMode] = useState<GradingMode>('auto');
  const [result, setResult] = useState<QuizGradingResult | null>(null);

  const { data: quiz, isLoading } = useQuiz(params.id);
  const { canAccess: canAccessLLM, tier } = useCanAccessPhase2();
  const submitMutation = useV3QuizSubmit();

  // Auto-select LLM mode for premium users
  useEffect(() => {
    if (canAccessLLM && tier === 'PRO') {
      setGradingMode('llm');
    } else if (canAccessLLM) {
      setGradingMode('hybrid');
    }
  }, [canAccessLLM, tier]);

  const handleSubmit = async () => {
    const allAnswers: Record<string, any> = { ...answers };

    // Include open-ended answers
    Object.entries(openEndedAnswers).forEach(([qId, answer]) => {
      if (answer.trim()) {
        allAnswers[qId] = answer;
      }
    });

    const submission: QuizSubmission = {
      answers: allAnswers,
      grading_mode: canAccessLLM ? gradingMode : 'auto',
    };

    try {
      const data = await submitMutation.mutateAsync({ quizId: params.id, submission });
      setResult(data as QuizGradingResult);
      setShowResults(true);
    } catch (error) {
      console.error('Quiz submission failed:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!quiz) {
    return (
      <PageContainer>
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📝</div>
          <h1 className="text-2xl font-bold text-text-primary">Quiz not found</h1>
          <p className="text-text-secondary mt-2">The quiz you're looking for doesn't exist.</p>
          <Link href="/chapters">
            <Button variant="outline" className="mt-6">
              ← Back to Chapters
            </Button>
          </Link>
        </div>
      </PageContainer>
    );
  }

  if (showResults && result) {
    return (
      <PageContainer>
        <Breadcrumbs />
        <div className="max-w-3xl mx-auto">
          {/* Results Header */}
          <div className="text-center mb-8">
            <div className="text-6xl mb-4">{result.passed ? '🎉' : '📚'}</div>
            <h1 className="text-3xl font-bold text-text-primary mb-2">
              {result.passed ? 'Congratulations!' : 'Keep Learning!'}
            </h1>
            <p className="text-text-secondary">{quiz.title}</p>
            {result.grading_mode !== 'auto' && (
              <Badge variant="info" className="mt-2">
                ✨ AI-Graded ({result.grading_mode})
              </Badge>
            )}
          </div>

          {/* Score Card */}
          <Card className="mb-6">
            <CardContent className="p-8 text-center">
              <div className="text-7xl font-bold mb-3">
                <span className={result.passed ? 'text-accent-success' : 'text-accent-warning'}>
                  {result.percentage}%
                </span>
              </div>
              <p className="text-lg text-text-secondary mb-4">
                You scored {result.total_score} out of {result.max_score} points
              </p>
              {result.passed ? (
                <Badge variant="success" className="text-base px-4 py-2">
                  ✓ Passed
                </Badge>
              ) : (
                <Badge variant="warning" className="text-base px-4 py-2">
                  Keep practicing (70% required)
                </Badge>
              )}
            </CardContent>
          </Card>

          {/* LLM Summary (if available) */}
          {result.summary && result.grading_mode !== 'auto' && (
            <Card className="mb-6 bg-accent-primary/5">
              <CardContent className="p-6">
                <h3 className="font-semibold text-text-primary mb-3 flex items-center gap-2">
                  <span className="text-xl">🤖</span>
                  AI Feedback Summary
                </h3>
                <p className="text-text-secondary">{result.summary}</p>
              </CardContent>
            </Card>
          )}

          {/* Detailed Results */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Detailed Results</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {result.results.map((item, index) => (
                  <div
                    key={item.question_id}
                    className={`p-4 rounded-lg border ${
                      item.is_correct ?? item.points_earned > 0
                        ? 'bg-accent-success/10 border-accent-success/30'
                        : 'bg-accent-danger/10 border-accent-danger/30'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                        item.is_correct ?? item.points_earned > 0
                          ? 'bg-accent-success/20'
                          : 'bg-accent-danger/20'
                      }`}>
                        <span className={item.is_correct ?? item.points_earned > 0 ? 'text-accent-success' : 'text-accent-danger'}>
                          {item.is_correct ?? item.points_earned > 0 ? '✓' : '✗'}
                        </span>
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-text-primary mb-2">
                          Q{index + 1}: {item.question_text}
                        </p>
                        <div className="text-sm space-y-2">
                          <p className="text-text-secondary">
                            Your answer:{' '}
                            <span className={item.is_correct ?? item.points_earned > 0 ? 'text-accent-success font-medium' : 'text-accent-danger font-medium'}>
                              {item.selected_answer || '(Open-ended)'}
                            </span>
                          </p>
                          {!item.is_correct && item.correct_answer && (
                            <p className="text-accent-success">Correct answer: {item.correct_answer}</p>
                          )}
                          {item.explanation && (
                            <p className="text-text-muted italic">💡 {item.explanation}</p>
                          )}
                          {item.feedback && (
                            <div className="mt-2 p-3 rounded bg-bg-elevated border-l-4 border-accent-secondary">
                              <p className="text-sm font-medium text-text-primary mb-1">AI Feedback:</p>
                              <p className="text-sm text-text-secondary">{item.feedback}</p>
                            </div>
                          )}
                          <div className="text-xs text-text-muted">
                            Points: {item.points_earned} / {item.max_points}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-3">
            <Link href="/chapters">
              <Button variant="primary">Continue Learning</Button>
            </Link>
            <Link href={`/quizzes/${params.id}`}>
              <Button variant="outline">Retake Quiz</Button>
            </Link>
            <Link href={`/quizzes/${params.id}/insights`}>
              <Button variant="secondary">View Insights</Button>
            </Link>
          </div>
        </div>
      </PageContainer>
    );
  }

  const question = quiz.questions[currentQuestion];
  const totalQuestions = quiz.questions.length;
  const progress = ((currentQuestion + 1) / totalQuestions) * 100;
  const answeredCount = Object.keys(answers).length + Object.keys(openEndedAnswers).filter(k => openEndedAnswers[k].trim()).length;

  return (
    <PageContainer>
      <Breadcrumbs />

      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <Link href="/chapters">
            <Button variant="ghost" size="sm" className="mb-4">
              ← Back to Chapters
            </Button>
          </Link>
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-text-primary mb-2">{quiz.title}</h1>
              <div className="flex items-center gap-3 flex-wrap">
                <span className="text-sm text-text-secondary">
                  Question {currentQuestion + 1} of {totalQuestions}
                </span>
                <Badge variant="info">{quiz.difficulty}</Badge>
                <span className="text-sm text-text-muted">
                  {answeredCount} of {totalQuestions} answered
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Grading Mode Selector (for premium users) */}
        {canAccessLLM && (
          <Card className="mb-6">
            <CardContent className="p-4">
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div>
                  <h4 className="font-semibold text-text-primary flex items-center gap-2">
                    <span>✨</span>
                    Grading Mode
                  </h4>
                  <p className="text-sm text-text-muted">
                    {gradingMode === 'llm' && 'AI evaluates all answers with detailed feedback'}
                    {gradingMode === 'hybrid' && 'Auto for multiple choice, AI for open-ended'}
                    {gradingMode === 'auto' && 'Fast rule-based grading'}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setGradingMode('auto')}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      gradingMode === 'auto'
                        ? 'bg-accent-primary text-white'
                        : 'bg-bg-elevated text-text-secondary hover:bg-bg-hover'
                    }`}
                  >
                    Auto
                  </button>
                  {canAccessLLM && (
                    <>
                      <button
                        onClick={() => setGradingMode('hybrid')}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                          gradingMode === 'hybrid'
                            ? 'bg-accent-secondary text-white'
                            : 'bg-bg-elevated text-text-secondary hover:bg-bg-hover'
                        }`}
                      >
                        Hybrid ⚡
                      </button>
                      <button
                        onClick={() => setGradingMode('llm')}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                          gradingMode === 'llm'
                            ? 'bg-accent-secondary text-white'
                            : 'bg-bg-elevated text-text-secondary hover:bg-bg-hover'
                        }`}
                      >
                        AI Only 🤖
                      </button>
                    </>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-text-secondary">Progress</span>
            <span className="text-sm font-bold text-accent-primary">{Math.round(progress)}%</span>
          </div>
          <div className="h-2 bg-bg-elevated rounded-full overflow-hidden">
            <div
              className="h-full bg-accent-primary transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Question Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-accent-primary/20 flex items-center justify-center">
                <span className="text-accent-primary font-bold">{currentQuestion + 1}</span>
              </div>
              <span className="text-lg">Question {currentQuestion + 1}</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <p className="text-lg text-text-primary leading-relaxed">{question.question_text}</p>

            {/* Open-ended option for premium users */}
            {canAccessLLM && gradingMode !== 'auto' && (
              <div className="p-4 rounded-lg bg-accent-secondary/10 border border-accent-secondary/30">
                <label className="flex items-center gap-2 mb-3">
                  <input
                    type="checkbox"
                    checked={!!openEndedAnswers[question.id]}
                    onChange={(e) => {
                      if (!e.target.checked) {
                        setOpenEndedAnswers(prev => {
                          const newAnswers = { ...prev };
                          delete newAnswers[question.id];
                          return newAnswers;
                        });
                      }
                    }}
                    className="w-4 h-4"
                  />
                  <span className="font-medium text-text-primary">
                    ✨ Write your own answer (AI-graded, up to 30 points)
                  </span>
                </label>
                <textarea
                  value={openEndedAnswers[question.id] || ''}
                  onChange={(e) => setOpenEndedAnswers({ ...openEndedAnswers, [question.id]: e.target.value })}
                  placeholder="Provide a detailed explanation..."
                  className="w-full px-4 py-3 rounded-lg border border-border-default bg-bg-elevated text-text-primary placeholder:text-text-muted resize-none focus:outline-none focus:ring-2 focus:ring-accent-secondary"
                  rows={3}
                />
                <p className="text-xs text-text-muted mt-2">
                  Minimum 100 characters for AI evaluation
                </p>
              </div>
            )}

            {/* Answer Options */}
            {!openEndedAnswers[question.id] && (
              <div className="space-y-3" role="radiogroup" aria-label="Answer options">
                {Object.entries(question.options).map(([key, value]) => {
                  const isSelected = answers[question.id] === key;
                  return (
                    <button
                      key={key}
                      onClick={() => {
                        setAnswers({ ...answers, [question.id]: key });
                        // Clear open-ended if selecting multiple choice
                        if (openEndedAnswers[question.id]) {
                          setOpenEndedAnswers(prev => {
                            const newAnswers = { ...prev };
                            delete newAnswers[question.id];
                            return newAnswers;
                          });
                        }
                      }}
                      className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                        isSelected
                          ? 'border-accent-primary bg-accent-primary/10 shadow-md'
                          : 'border-border-default hover:border-accent-primary/50 hover:bg-bg-elevated'
                      }`}
                      role="radio"
                      aria-checked={isSelected}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 mt-0.5 ${
                          isSelected
                            ? 'border-accent-primary bg-accent-primary'
                            : 'border-border-default'
                        }`}>
                          {isSelected && (
                            <div className="w-2.5 h-2.5 rounded-full bg-white" />
                          )}
                        </div>
                        <span className="flex-1 text-text-primary">{value}</span>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}

            {/* Navigation Buttons */}
            <div className="flex justify-between pt-4 border-t border-border-default">
              <Button
                variant="outline"
                onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
                disabled={currentQuestion === 0}
              >
                ← Previous
              </Button>
              <Button
                variant={(answers[question.id] || openEndedAnswers[question.id]) ? 'primary' : 'secondary'}
                onClick={() =>
                  currentQuestion < totalQuestions - 1
                    ? setCurrentQuestion(currentQuestion + 1)
                    : handleSubmit()
                }
                disabled={!answers[question.id] && !openEndedAnswers[question.id]}
                isLoading={submitMutation.isPending}
              >
                {currentQuestion < totalQuestions - 1 ? 'Next →' : 'Submit Quiz'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Question Navigator */}
        <Card className="mt-6">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-medium text-text-secondary">Question Navigator</span>
              <span className="text-xs text-text-muted">Click to jump</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {quiz.questions.map((_, index) => {
                const isAnswered = !!answers[quiz.questions[index].id] || !!openEndedAnswers[quiz.questions[index].id];
                const isCurrent = index === currentQuestion;

                return (
                  <button
                    key={index}
                    onClick={() => setCurrentQuestion(index)}
                    className={`w-10 h-10 rounded-lg font-medium text-sm transition-all ${
                      isCurrent
                        ? 'bg-accent-primary text-white shadow-md'
                        : isAnswered
                        ? 'bg-accent-success/20 text-accent-success border border-accent-success/30'
                        : 'bg-bg-elevated text-text-secondary border border-border-default'
                    }`}
                  >
                    {index + 1}
                  </button>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </PageContainer>
  );
}
