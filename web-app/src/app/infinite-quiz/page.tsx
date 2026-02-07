'use client';

/**
 * Infinite Quiz Page - Unlimited procedurally generated practice problems
 *
 * Features:
 * - Select from multiple topics and subtopics
 * - Choose difficulty level
 * - Generate unlimited unique questions
 * - Real-time feedback and explanations
 * - Session tracking and statistics
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingSpinner } from '@/components/ui/Loading';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import {
  Infinity,
  Zap,
  Target,
  TrendingUp,
  Play,
  RotateCcw,
  CheckCircle2,
  XCircle,
  Lightbulb,
  BarChart3,
  Sparkles,
  BookOpen,
  Code,
  Hash,
  Braces,
  Globe,
  Package,
  Activity,
  Beaker,
  Box,
  FileText,
} from 'lucide-react';
import {
  getTopics,
  getSubtopics,
  generateQuestions,
  generateMixedQuiz,
  type GeneratedQuestion,
  type Topic,
} from '@/lib/infiniteQuiz';

type QuizMode = 'practice' | 'timed' | 'exam';
type Difficulty = 'beginner' | 'intermediate' | 'advanced' | 'mixed';

export default function InfiniteQuizPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);

  // Quiz configuration
  const [selectedTopic, setSelectedTopic] = useState<string>('');
  const [selectedSubtopic, setSelectedSubtopic] = useState<string>('');
  const [difficulty, setDifficulty] = useState<Difficulty>('beginner');
  const [questionCount, setQuestionCount] = useState(10);
  const [mode, setMode] = useState<QuizMode>('practice');

  // Quiz state
  const [quizStarted, setQuizStarted] = useState(false);
  const [questions, setQuestions] = useState<GeneratedQuestion[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [showResults, setShowResults] = useState(false);
  const [sessionStats, setSessionStats] = useState({
    correct: 0,
    incorrect: 0,
    streak: 0,
    bestStreak: 0,
  });

  const topics = getTopics();
  const availableSubtopics = selectedTopic ? getSubtopics(selectedTopic) : [];

  useEffect(() => {
    const userId = localStorage.getItem('user_id');
    if (!userId) {
      router.push('/login');
      return;
    }
    setIsLoading(false);
  }, [router]);

  // Get topic icon
  const getTopicIcon = (icon: string) => {
    const icons: Record<string, React.ReactNode> = {
      'JS': <Code className="w-6 h-6" />,
      'python': <Braces className="w-6 h-6" />,
      'react': <Sparkles className="w-6 h-6" />,
      'api': <Globe className="w-6 h-6" />,
      'sql': <Target className="w-6 h-6" />,
      'git': <Package className="w-6 h-6" />,
      'docker': <Zap className="w-6 h-6" />,
      'typescript': <FileText className="w-6 h-6" />,
      'nodejs': <Activity className="w-6 h-6" />,
      'testing': <Beaker className="w-6 h-6" />,
      'data-structures': <Box className="w-6 h-6" />,
      'algorithms': <Zap className="w-6 h-6" />,
    };
    return icons[icon] || <BookOpen className="w-6 h-6" />;
  };

  // Start quiz
  const handleStartQuiz = () => {
    let generatedQuestions: GeneratedQuestion[];

    if (difficulty === 'mixed') {
      generatedQuestions = generateMixedQuiz(selectedTopic, selectedSubtopic, questionCount);
    } else {
      generatedQuestions = generateQuestions(selectedTopic, selectedSubtopic, questionCount, difficulty);
    }

    if (generatedQuestions.length === 0) {
      alert('No questions available for this selection. Please try a different topic.');
      return;
    }

    setQuestions(generatedQuestions);
    setCurrentQuestion(0);
    setAnswers({});
    setShowResults(false);
    setSessionStats({ correct: 0, incorrect: 0, streak: 0, bestStreak: 0 });
    setQuizStarted(true);
  };

  // Generate more questions (continue practice)
  const handleGenerateMore = () => {
    let newQuestions: GeneratedQuestion[];

    if (difficulty === 'mixed') {
      newQuestions = generateMixedQuiz(selectedTopic, selectedSubtopic, questionCount);
    } else {
      newQuestions = generateQuestions(selectedTopic, selectedSubtopic, questionCount, difficulty);
    }

    if (newQuestions.length > 0) {
      setQuestions(newQuestions);
      setCurrentQuestion(0);
      setAnswers({});
      setShowResults(false);
    }
  };

  // Handle answer selection
  const handleAnswer = (optionKey: string) => {
    const newAnswers = { ...answers, [currentQuestion]: optionKey };
    setAnswers(newAnswers);

    // Update session stats
    const question = questions[currentQuestion];
    const isCorrect = optionKey === question.correctAnswer;

    if (isCorrect) {
      setSessionStats(prev => ({
        ...prev,
        correct: prev.correct + 1,
        streak: prev.streak + 1,
        bestStreak: Math.max(prev.streak + 1, prev.bestStreak),
      }));
    } else {
      setSessionStats(prev => ({
        ...prev,
        incorrect: prev.incorrect + 1,
        streak: 0,
      }));
    }
  };

  // Submit quiz
  const handleSubmit = () => {
    setShowResults(true);
  };

  // Calculate score
  const calculateScore = () => {
    let correct = 0;
    questions.forEach((q, index) => {
      if (answers[index] === q.correctAnswer) {
        correct++;
      }
    });
    return {
      correct,
      total: questions.length,
      percentage: Math.round((correct / questions.length) * 100),
    };
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // Results view
  if (showResults) {
    const score = calculateScore();
    const passed = score.percentage >= 70;

    return (
      <PageContainer>
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <div className="mb-4 flex justify-center">
              <div className={`w-20 h-20 rounded-2xl bg-gradient-to-br ${
                passed
                  ? 'from-accent-success/20 to-accent-success/10'
                  : 'from-accent-warning/20 to-accent-warning/10'
              } flex items-center justify-center`}>
                {passed ? (
                  <CheckCircle2 className="w-12 h-12 text-accent-success" />
                ) : (
                  <XCircle className="w-12 h-12 text-accent-warning" />
                )}
              </div>
            </div>
            <h1 className="text-3xl font-bold text-text-primary mb-2">
              {passed ? 'Great Job!' : 'Keep Practicing!'}
            </h1>
            <p className="text-text-secondary">
              Infinite Quiz Session Complete
            </p>
          </div>

          {/* Score Card */}
          <Card className="mb-6">
            <CardContent className="p-8 text-center">
              <div className="text-7xl font-bold mb-3">
                <span className={passed ? 'text-accent-success' : 'text-accent-warning'}>
                  {score.percentage}%
                </span>
              </div>
              <p className="text-lg text-text-secondary mb-4">
                You scored {score.correct} out of {score.total}
              </p>
              <Badge variant={passed ? 'success' : 'warning'} className="text-base px-4 py-2 gap-1">
                {passed ? <><CheckCircle2 className="w-4 h-4" /> Passed</> : 'Keep practicing (70% required)'}
              </Badge>
            </CardContent>
          </Card>

          {/* Session Stats */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
                  <BarChart3 className="w-6 h-6 text-cosmic-primary" />
                </div>
                Session Statistics
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 rounded-lg bg-bg-elevated border border-border-default">
                  <div className="text-2xl font-bold text-accent-success">{sessionStats.correct}</div>
                  <div className="text-sm text-text-secondary">Correct</div>
                </div>
                <div className="text-center p-4 rounded-lg bg-bg-elevated border border-border-default">
                  <div className="text-2xl font-bold text-accent-danger">{sessionStats.incorrect}</div>
                  <div className="text-sm text-text-secondary">Incorrect</div>
                </div>
                <div className="text-center p-4 rounded-lg bg-bg-elevated border border-border-default">
                  <div className="text-2xl font-bold text-cosmic-primary">{sessionStats.streak}</div>
                  <div className="text-sm text-text-secondary">Current Streak</div>
                </div>
                <div className="text-center p-4 rounded-lg bg-bg-elevated border border-border-default">
                  <div className="text-2xl font-bold text-accent-warning">{sessionStats.bestStreak}</div>
                  <div className="text-sm text-text-secondary">Best Streak</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Question Review */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Question Review</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {questions.map((q, index) => {
                  const userAnswer = answers[index];
                  const isCorrect = userAnswer === q.correctAnswer;

                  return (
                    <div
                      key={q.id}
                      className={`p-4 rounded-lg border ${
                        isCorrect
                          ? 'bg-accent-success/10 border-accent-success/30'
                          : 'bg-accent-danger/10 border-accent-danger/30'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                          isCorrect ? 'bg-accent-success/20' : 'bg-accent-danger/20'
                        }`}>
                          {isCorrect ? (
                            <CheckCircle2 className="w-5 h-5 text-accent-success" />
                          ) : (
                            <XCircle className="w-5 h-5 text-accent-danger" />
                          )}
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-text-primary mb-2">
                            Q{index + 1}: {q.question}
                          </p>
                          <div className="text-sm space-y-1">
                            <p className="text-text-secondary">
                              Your answer:{' '}
                              <span className={isCorrect ? 'text-accent-success font-medium' : 'text-accent-danger font-medium'}>
                                {q.options[userAnswer] || 'Not answered'}
                              </span>
                            </p>
                            {!isCorrect && (
                              <p className="text-accent-success">
                                Correct answer: {q.options[q.correctAnswer]}
                              </p>
                            )}
                            <p className="text-text-muted italic text-xs mt-2 flex items-start gap-1">
                              <Lightbulb className="w-3 h-3 flex-shrink-0 mt-0.5" />
                              <span>{q.explanation}</span>
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-3">
            <Button variant="primary" onClick={handleGenerateMore}>
              <RotateCcw className="w-4 h-4 mr-2" />
              Generate More Questions
            </Button>
            <Button variant="outline" onClick={() => setQuizStarted(false)}>
              <Target className="w-4 h-4 mr-2" />
              Change Settings
            </Button>
            <Button variant="secondary" onClick={() => router.push('/chapters')}>
              <BookOpen className="w-4 h-4 mr-2" />
              Back to Chapters
            </Button>
          </div>
        </div>
      </PageContainer>
    );
  }

  // Quiz in progress
  if (quizStarted && questions.length > 0) {
    const question = questions[currentQuestion];
    const progress = ((currentQuestion + 1) / questions.length) * 100;
    const answered = answers[currentQuestion];

    return (
      <PageContainer>
        <div className="max-w-3xl mx-auto">
          {/* Header */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
              <Badge variant="info">{question.topic}</Badge>
              <Badge variant="secondary">{question.subtopic}</Badge>
              <Badge variant={question.difficulty === 'beginner' ? 'success' : question.difficulty === 'intermediate' ? 'warning' : 'danger'}>
                {question.difficulty}
              </Badge>
            </div>

            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-text-secondary">
                Question {currentQuestion + 1} of {questions.length}
              </span>
              <span className="text-sm font-bold text-accent-primary">
                {Math.round(progress)}%
              </span>
            </div>

            <div className="h-2 bg-bg-elevated rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-cosmic-primary to-cosmic-purple transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>

          {/* Session Stats */}
          <div className="grid grid-cols-3 gap-3 mb-6">
            <div className="text-center p-3 rounded-lg bg-accent-success/10 border border-accent-success/30">
              <div className="text-xl font-bold text-accent-success">{sessionStats.correct}</div>
              <div className="text-xs text-text-secondary">Correct</div>
            </div>
            <div className="text-center p-3 rounded-lg bg-accent-danger/10 border border-accent-danger/30">
              <div className="text-xl font-bold text-accent-danger">{sessionStats.incorrect}</div>
              <div className="text-xs text-text-secondary">Incorrect</div>
            </div>
            <div className="text-center p-3 rounded-lg bg-cosmic-primary/10 border border-cosmic-primary/30">
              <div className="text-xl font-bold text-cosmic-primary">{sessionStats.streak}</div>
              <div className="text-xs text-text-secondary">Streak</div>
            </div>
          </div>

          {/* Question Card */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-cosmic-primary/20 flex items-center justify-center">
                  <span className="text-cosmic-primary font-bold">{currentQuestion + 1}</span>
                </div>
                <span className="text-lg">Question {currentQuestion + 1}</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-lg text-text-primary leading-relaxed mb-6">{question.question}</p>

              {/* Answer Options */}
              <div className="space-y-3" role="radiogroup">
                {Object.entries(question.options).map(([key, value]) => {
                  const isSelected = answered === key;
                  const isCorrect = key === question.correctAnswer;

                  return (
                    <button
                      key={key}
                      onClick={() => !answered && handleAnswer(key)}
                      disabled={!!answered}
                      className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                        answered
                          ? isSelected
                            ? isCorrect
                              ? 'border-accent-success bg-accent-success/10'
                              : 'border-accent-danger bg-accent-danger/10'
                            : 'border-border-default bg-bg-elevated opacity-60'
                          : isSelected
                          ? 'border-cosmic-primary bg-cosmic-primary/10'
                          : 'border-border-default hover:border-cosmic-primary/50 hover:bg-bg-elevated'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 mt-0.5 ${
                          isSelected
                            ? answered
                              ? isCorrect
                                ? 'border-accent-success bg-accent-success'
                                : 'border-accent-danger bg-accent-danger'
                              : 'border-cosmic-primary bg-cosmic-primary'
                            : 'border-border-default'
                        }`}>
                          {isSelected && (
                            <div className={`w-2.5 h-2.5 rounded-full ${
                              answered && isCorrect ? 'bg-white' : answered && !isCorrect ? 'bg-white' : 'bg-white'
                            }`} />
                          )}
                        </div>
                        <span className="flex-1 text-text-primary">{value}</span>
                        {answered && isCorrect && (
                          <CheckCircle2 className="w-5 h-5 text-accent-success flex-shrink-0" />
                        )}
                        {answered && isSelected && !isCorrect && (
                          <XCircle className="w-5 h-5 text-accent-danger flex-shrink-0" />
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>

              {/* Explanation (shown after answering) */}
              {answered && (
                <div className="mt-6 p-4 rounded-lg bg-cosmic-primary/10 border border-cosmic-primary/30">
                  <p className="text-sm font-semibold text-cosmic-primary mb-2 flex items-center gap-2">
                    <Lightbulb className="w-4 h-4" />
                    Explanation
                  </p>
                  <p className="text-sm text-text-secondary">{question.explanation}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Navigation */}
          <div className="flex justify-between">
            <Button
              variant="outline"
              onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
              disabled={currentQuestion === 0}
            >
              ← Previous
            </Button>
            {currentQuestion < questions.length - 1 ? (
              <Button
                variant={answered ? 'primary' : 'secondary'}
                onClick={() => setCurrentQuestion(currentQuestion + 1)}
                disabled={!answered}
              >
                Next →
              </Button>
            ) : (
              <Button
                variant={answered ? 'primary' : 'secondary'}
                onClick={handleSubmit}
                disabled={!answered}
              >
                Submit Quiz
              </Button>
            )}
          </div>
        </div>
      </PageContainer>
    );
  }

  // Setup view (default)
  return (
    <PageContainer>
      <PageHeader
        title="Infinite Quiz Engine"
        description="Generate unlimited, unique practice problems - never run out of review material!"
      />

      {/* Feature Highlights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
                <Infinity className="w-6 h-6 text-cosmic-primary" />
              </div>
              <h3 className="text-lg font-bold text-text-primary">Unlimited Questions</h3>
            </div>
            <p className="text-text-secondary text-sm">
              Procedurally generated questions ensure you never see the same problem twice
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-success/20 to-accent-success/10 flex items-center justify-center">
                <Target className="w-6 h-6 text-accent-success" />
              </div>
              <h3 className="text-lg font-bold text-text-primary">Targeted Practice</h3>
            </div>
            <p className="text-text-secondary text-sm">
              Focus on specific topics and subtopics where you need the most improvement
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-warning/20 to-accent-warning/10 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-accent-warning" />
              </div>
              <h3 className="text-lg font-bold text-text-primary">Adaptive Difficulty</h3>
            </div>
            <p className="text-text-secondary text-sm">
              Choose your level or mix it up with questions across all difficulty levels
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quiz Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
              <Target className="w-6 h-6 text-cosmic-primary" />
            </div>
            Configure Your Quiz
          </CardTitle>
          <CardDescription>Choose your topic, difficulty, and number of questions</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Topic Selection */}
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-3">
              Select Topic
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {topics.map((topic) => (
                <button
                  key={topic.id}
                  onClick={() => {
                    setSelectedTopic(topic.id);
                    setSelectedSubtopic('');
                  }}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    selectedTopic === topic.id
                      ? 'border-cosmic-primary bg-cosmic-primary/10'
                      : 'border-border-default hover:border-cosmic-primary/50'
                  }`}
                >
                  <div className="flex flex-col items-center gap-2">
                    {getTopicIcon(topic.icon)}
                    <span className="text-sm font-medium text-text-primary">{topic.name}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Subtopic Selection */}
          {selectedTopic && availableSubtopics.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-3">
                Select Subtopic
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {availableSubtopics.map((subtopic) => (
                  <button
                    key={subtopic.id}
                    onClick={() => setSelectedSubtopic(subtopic.id)}
                    className={`p-3 rounded-lg border-2 transition-all ${
                      selectedSubtopic === subtopic.id
                        ? 'border-cosmic-primary bg-cosmic-primary/10'
                        : 'border-border-default hover:border-cosmic-primary/50'
                    }`}
                  >
                    <span className="text-sm font-medium text-text-primary">{subtopic.name}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Difficulty Selection */}
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-3">
              Difficulty Level
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {(['beginner', 'intermediate', 'advanced', 'mixed'] as Difficulty[]).map((diff) => (
                <button
                  key={diff}
                  onClick={() => setDifficulty(diff)}
                  className={`p-3 rounded-lg border-2 transition-all capitalize ${
                    difficulty === diff
                      ? 'border-cosmic-primary bg-cosmic-primary/10'
                      : 'border-border-default hover:border-cosmic-primary/50'
                  }`}
                >
                  <span className="text-sm font-medium text-text-primary">{diff}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Number of Questions */}
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-3">
              Number of Questions: {questionCount}
            </label>
            <input
              type="range"
              min="5"
              max="50"
              step="5"
              value={questionCount}
              onChange={(e) => setQuestionCount(parseInt(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-text-muted mt-1">
              <span>5</span>
              <span>50</span>
            </div>
          </div>

          {/* Quiz Mode */}
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-3">
              Quiz Mode
            </label>
            <div className="grid grid-cols-3 gap-3">
              {(['practice', 'timed', 'exam'] as QuizMode[]).map((quizMode) => (
                <button
                  key={quizMode}
                  onClick={() => setMode(quizMode)}
                  className={`p-3 rounded-lg border-2 transition-all capitalize ${
                    mode === quizMode
                      ? 'border-cosmic-primary bg-cosmic-primary/10'
                      : 'border-border-default hover:border-cosmic-primary/50'
                  }`}
                >
                  <div className="flex flex-col items-center gap-1">
                    <span className="text-sm font-medium text-text-primary">{quizMode}</span>
                    <span className="text-xs text-text-muted">
                      {quizMode === 'practice' && 'No time limit'}
                      {quizMode === 'timed' && 'Timed sessions'}
                      {quizMode === 'exam' && 'Test conditions'}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Start Button */}
          <Button
            variant="primary"
            size="lg"
            className="w-full"
            onClick={handleStartQuiz}
            disabled={!selectedTopic || !selectedSubtopic}
          >
            <Play className="w-5 h-5 mr-2" />
            Generate Quiz
          </Button>
        </CardContent>
      </Card>

      {/* Info Card */}
      <Card className="mt-6 bg-gradient-to-r from-cosmic-primary/10 to-cosmic-purple/10 border-cosmic-primary/30">
        <CardContent className="p-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cosmic-primary to-cosmic-purple flex items-center justify-center flex-shrink-0">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-text-primary mb-2">
                How Infinite Quiz Works
              </h3>
              <ul className="space-y-2 text-text-secondary">
                <li className="flex items-start gap-2">
                  <span className="text-accent-primary mt-1">•</span>
                  <span>Select your topic and subtopic to focus on specific areas</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-accent-primary mt-1">•</span>
                  <span>Questions are procedurally generated for unlimited variety</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-accent-primary mt-1">•</span>
                  <span>Get instant feedback with detailed explanations for each answer</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-accent-primary mt-1">•</span>
                  <span>Generate new questions anytime to continue practicing</span>
                </li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </PageContainer>
  );
}
