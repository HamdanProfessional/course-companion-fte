/**
 * Quiz taking page.
 */
import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Loading } from '@/components/ui/Loading';
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
        <Loading size="lg" />
      </div>
    );
  }

  if (!quiz) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold text-gray-900">Quiz not found</h1>
        <Link href="/chapters">
          <Button variant="outline" className="mt-4">
            ← Back to Chapters
          </Button>
        </Link>
      </div>
    );
  }

  if (showResults && submitMutation.data) {
    const result = submitMutation.data;
    return (
      <div className="max-w-3xl mx-auto space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">Quiz Results</h1>
          <p className="text-gray-600 mt-2">{quiz.title}</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-center">
              {result.passed ? '🎉 Congratulations!' : 'Keep Learning!'}
            </CardTitle>
          </CardHeader>
          <CardContent className="text-center">
            <div className="text-6xl font-bold text-primary-600 mb-2">
              {result.score}%
            </div>
            <p className="text-lg text-gray-600">
              You got {result.correct_answers} out of {result.total_questions} questions correct
            </p>
            {result.passed && (
              <p className="text-green-600 font-semibold mt-4">
                You passed! Great work! 🌟
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Detailed Results</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {result.results.map((item, index) => (
                <div
                  key={item.question_id}
                  className={`p-4 rounded-lg border ${
                    item.is_correct ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <span className="text-xl">{item.is_correct ? '✓' : '✗'}</span>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">Q{index + 1}: {item.question_text}</p>
                      <div className="mt-2 text-sm">
                        <p className="text-gray-600">
                          Your answer: <span className={item.is_correct ? 'text-green-700' : 'text-red-700'}>
                            {item.selected_answer}
                          </span>
                        </p>
                        {!item.is_correct && (
                          <p className="text-green-700">
                            Correct answer: {item.correct_answer}
                          </p>
                        )}
                        {item.explanation && (
                          <p className="text-gray-500 mt-1 italic">{item.explanation}</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <div className="flex space-x-3">
          <Link href="/chapters">
            <Button variant="primary">Continue Learning</Button>
          </Link>
          <Link href={`/quizzes/${params.id}`}>
            <Button variant="outline">Retake Quiz</Button>
          </Link>
        </div>
      </div>
    );
  }

  const question = quiz.questions[currentQuestion];
  const totalQuestions = quiz.questions.length;
  const progress = ((currentQuestion + 1) / totalQuestions) * 100;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <Link href="/chapters">
          <Button variant="ghost" className="mb-4">
            ← Back to Chapters
          </Button>
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">{quiz.title}</h1>
        <div className="flex items-center space-x-4 mt-2">
          <span className="text-sm text-gray-500">
            Question {currentQuestion + 1} of {totalQuestions}
          </span>
          <span className="text-sm px-2 py-1 rounded-full bg-blue-100 text-blue-700">
            {quiz.difficulty}
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-primary-600 h-2 rounded-full transition-all"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Question Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">Question {currentQuestion + 1}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <p className="text-lg text-gray-900">{question.question_text}</p>

          <div className="space-y-3">
            {Object.entries(question.options).map(([key, value]) => (
              <button
                key={key}
                onClick={() => setAnswers({ ...answers, [question.id]: key })}
                className={`w-full text-left p-4 border-2 rounded-lg transition-colors ${
                  answers[question.id] === key
                    ? 'border-primary-600 bg-primary-50'
                    : 'border-gray-200 hover:border-primary-300 hover:bg-gray-50'
                }`}
              >
                <span className="font-medium mr-3">{key}.</span>
                {value}
              </button>
            ))}
          </div>

          <div className="flex justify-between">
            <Button
              variant="outline"
              onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
              disabled={currentQuestion === 0}
            >
              Previous
            </Button>
            <Button
              variant="primary"
              onClick={() =>
                currentQuestion < totalQuestions - 1
                  ? setCurrentQuestion(currentQuestion + 1)
                  : submitMutation.mutate()
              }
              disabled={!answers[question.id] || submitMutation.isPending}
            >
              {currentQuestion < totalQuestions - 1 ? 'Next' : 'Submit Quiz'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
