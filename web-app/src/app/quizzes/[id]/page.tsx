'use client';

/**
 * Quiz taking page with Professional/Modern SaaS theme.
 * One-question-at-a-time UI with keyboard navigation.
 */
import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/Loading';
import { Badge } from '@/components/ui/Badge';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import { Breadcrumbs } from '@/components/layout/Breadcrumbs';
import { useQuiz, backendApi } from '@/hooks';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import Link from 'next/link';

export default function QuizPage({ params }: { params: { id: string } }) {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [showResults, setShowResults] = useState(false);

  const queryClient = useQueryClient();
  const { data: quiz, isLoading } = useQuiz(params.id);

  const submitMutation = useMutation({
    mutationFn: () => backendApi.submitQuiz(params.id, answers),
    onSuccess: (data) => {
      setShowResults(true);
      // Update progress
      backendApi.updateProgress('00000000-0000-0000-0000-000000000001', quiz?.chapter_id || '');
      queryClient.invalidateQueries({ queryKey: ['progress'] });
    },
  });

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

  if (showResults && submitMutation.data) {
    const result = submitMutation.data;
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
          </div>

          {/* Score Card */}
          <Card className="mb-6" variant={result.passed ? 'elevated' : 'default'}>
            <CardContent className="p-8 text-center">
              <div className="text-7xl font-bold mb-3">
                <span className={result.passed ? 'text-accent-success' : 'text-accent-warning'}>
                  {result.score}%
                </span>
              </div>
              <p className="text-lg text-text-secondary mb-4">
                You got {result.correct_answers} out of {result.total_questions} questions correct
              </p>
              {result.passed ? (
                <Badge variant="success" className="text-base px-4 py-2">
                  ✓ Passed
                </Badge>
              ) : (
                <Badge variant="warning" className="text-base px-4 py-2">
                  Keep practicing
                </Badge>
              )}
            </CardContent>
          </Card>

          {/* Detailed Results */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Detailed Results</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {result.results.map((item, index) => (
                  <div
                    key={item.question_id}
                    className={`p-4 rounded-lg border transition-all ${
                      item.is_correct
                        ? 'bg-accent-success/10 border-accent-success/30'
                        : 'bg-accent-danger/10 border-accent-danger/30'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                        item.is_correct ? 'bg-accent-success/20' : 'bg-accent-danger/20'
                      }`}>
                        <span className={item.is_correct ? 'text-accent-success' : 'text-accent-danger'}>
                          {item.is_correct ? '✓' : '✗'}
                        </span>
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-text-primary mb-2">
                          Q{index + 1}: {item.question_text}
                        </p>
                        <div className="text-sm space-y-1">
                          <p className="text-text-secondary">
                            Your answer:{' '}
                            <span className={item.is_correct ? 'text-accent-success font-medium' : 'text-accent-danger font-medium'}>
                              {item.selected_answer}
                            </span>
                          </p>
                          {!item.is_correct && (
                            <p className="text-accent-success">Correct answer: {item.correct_answer}</p>
                          )}
                          {item.explanation && (
                            <p className="text-text-muted italic mt-2">💡 {item.explanation}</p>
                          )}
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
          </div>
        </div>
      </PageContainer>
    );
  }

  const question = quiz.questions[currentQuestion];
  const totalQuestions = quiz.questions.length;
  const progress = ((currentQuestion + 1) / totalQuestions) * 100;
  const answeredCount = Object.keys(answers).length;

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
        <Card variant="elevated">
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

            {/* Answer Options */}
            <div className="space-y-3" role="radiogroup" aria-label="Answer options">
              {Object.entries(question.options).map(([key, value]) => {
                const isSelected = answers[question.id] === key;
                return (
                  <button
                    key={key}
                    onClick={() => setAnswers({ ...answers, [question.id]: key })}
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
                variant={answers[question.id] ? 'primary' : 'secondary'}
                onClick={() =>
                  currentQuestion < totalQuestions - 1
                    ? setCurrentQuestion(currentQuestion + 1)
                    : submitMutation.mutate()
                }
                disabled={!answers[question.id] || submitMutation.isPending}
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
                const isAnswered = !!answers[quiz.questions[index].id];
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
