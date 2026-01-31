/**
 * Course Companion FTE - ChatGPT App UI Components
 * React components for quiz interface and progress tracking
 */

import React, { useState, useEffect, useCallback } from 'react';
import ReactDOM from 'react-dom/client';

// ============= TYPE DEFINITIONS =============

declare global {
  interface Window {
    openai: OpenAIAPI & OpenAIGlobals;
  }
}

interface ToolResponse {
  content: Array<{ type: string; text: string }>;
  isError?: boolean;
}

interface QuizData {
  title: string;
  difficulty: string;
  id: string;
  chapter_id: string;
  questions: Question[];
}

interface Question {
  question_text: string;
  options: {
    A: string;
    B: string;
    C: string;
    D: string;
  };
  explanation: string;
  order: number;
  id: string;
  quiz_id: string;
}

interface OpenAIAPI {
  callTool: (name: string, args: Record<string, unknown>) => Promise<ToolResponse>;
  requestClose: () => void;
  sendFollowUpMessage: (args: { prompt: string }) => Promise<void>;
  setWidgetState: (state: WidgetState) => Promise<void>;
  requestDisplayMode: (args: { mode: 'pip' | 'inline' | 'fullscreen' }) => Promise<{
    mode: 'pip' | 'inline' | 'fullscreen';
  }>;
}

interface OpenAIGlobals {
  theme: 'light' | 'dark';
  locale: string;
  maxHeight: number;
  displayMode: 'pip' | 'inline' | 'fullscreen';
  toolInput: Record<string, unknown>;
  toolOutput: QuizData | null;
  widgetState: WidgetState | null;
}

interface WidgetState {
  currentQuestionIndex?: number;
  answers?: Record<number, string>;
  score?: number;
  completed?: boolean;
}

// ============= STYLES =============

const styles = {
  container: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    padding: '20px',
    color: '#fff',
  },
  quizContainer: {
    backgroundColor: '#2d2d2d',
    borderRadius: '12px',
    padding: '24px',
    marginBottom: '16px',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
  },
  title: {
    fontSize: '20px',
    fontWeight: 'bold',
    margin: 0,
  },
  progressContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  progressBar: {
    display: 'flex',
    gap: '4px',
  },
  progressDot: (filled: boolean) => ({
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    backgroundColor: filled ? '#10a37f' : '#4d4d4d',
  }),
  questionText: {
    fontSize: '16px',
    lineHeight: '1.5',
    marginBottom: '20px',
    fontWeight: '500',
  },
  optionsContainer: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '12px',
  },
  optionButton: (isCorrect: boolean | null, isSelected: boolean) => ({
    padding: '16px',
    borderRadius: '8px',
    border: '2px solid',
    borderColor: isCorrect === true
      ? '#10a37f'
      : isCorrect === false
        ? '#ef4444'
        : '#4d4d4d',
    backgroundColor: isSelected
      ? 'rgba(16, 163, 127, 0.1)'
      : 'transparent',
    color: '#fff',
    cursor: 'pointer',
    transition: 'all 0.2s',
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  }),
  optionLabel: (label: string) => ({
    width: '32px',
    height: '32px',
    borderRadius: '50%',
    backgroundColor: '#10a37f',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: 'bold',
  }),
  optionText: {
    flex: 1,
    textAlign: 'left' as const,
  },
  feedbackContainer: {
    marginTop: '20px',
    padding: '16px',
    borderRadius: '8px',
    backgroundColor: 'rgba(16, 163, 127, 0.1)',
    border: '1px solid #10a37f',
  },
  buttonContainer: {
    display: 'flex',
    gap: '12px',
    marginTop: '20px',
  },
  button: (primary: boolean) => ({
    padding: '12px 24px',
    borderRadius: '8px',
    border: 'none',
    backgroundColor: primary ? '#10a37f' : '#4d4d4d',
    color: '#fff',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.2s',
    flex: 1,
  }),
  resultsContainer: {
    backgroundColor: '#2d2d2d',
    borderRadius: '12px',
    padding: '24px',
    textAlign: 'center' as const,
  },
  scoreText: {
    fontSize: '48px',
    fontWeight: 'bold',
    color: '#10a37f',
    margin: '20px 0',
  },
  statsContainer: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '16px',
    margin: '20px 0',
  },
  statBox: {
    backgroundColor: '#3d3d3d',
    padding: '16px',
    borderRadius: '8px',
  },
  statLabel: {
    fontSize: '14px',
    color: '#999',
    marginBottom: '8px',
  },
  statValue: {
    fontSize: '24px',
    fontWeight: 'bold',
  },
};

// ============= COMPONENTS =============

function QuizOption({
  label,
  text,
  onClick,
  isCorrect = null,
  isSelected = false
}: {
  label: string;
  text: string;
  onClick: () => void;
  isCorrect?: boolean | null;
  isSelected?: boolean;
}) {
  return (
    <button
      style={styles.optionButton(isCorrect, isSelected)}
      onClick={onClick}
    >
      <span style={styles.optionLabel(label)}>{label}</span>
      <span style={styles.optionText}>{text}</span>
      {isCorrect === true && <span>✅</span>}
      {isCorrect === false && <span>❌</span>}
    </button>
  );
}

function QuizInterface() {
  const [quizData, setQuizData] = useState<QuizData | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);
  const [score, setScore] = useState(0);
  const [completed, setCompleted] = useState(false);

  // Load quiz data from window.openai
  useEffect(() => {
    const toolOutput = window.openai?.toolOutput as QuizData | null;
    if (toolOutput?.questions) {
      setQuizData(toolOutput);
    }
  }, []);

  // Load saved state
  useEffect(() => {
    const widgetState = window.openai?.widgetState as WidgetState | null;
    if (widgetState) {
      if (widgetState.currentQuestionIndex !== undefined) {
        setCurrentQuestion(widgetState.currentQuestionIndex);
      }
      if (widgetState.score !== undefined) {
        setScore(widgetState.score);
      }
      if (widgetState.completed) {
        setCompleted(true);
      }
    }
  }, []);

  const handleAnswerSelect = useCallback((optionKey: string) => {
    if (showFeedback) return; // Don't allow changing after feedback

    setSelectedAnswer(optionKey);
    const correct = quizData!.questions[currentQuestion].options;
    const correctKey = Object.keys(correct).find(key => {
      // For now, we'll assume the first option is correct
      // In production, you'd get the correct_answer from the quiz data
      return key === 'A'; // TODO: Use actual correct_answer from data
    });

    setIsCorrect(optionKey === correctKey);
    setShowFeedback(true);

    if (optionKey === correctKey) {
      setScore(s => s + 1);
    }
  }, [currentQuestion, quizData, showFeedback]);

  const handleNext = useCallback(async () => {
    // Save state
    const newState: WidgetState = {
      currentQuestionIndex: currentQuestion + 1,
      score: isCorrect ? score + 1 : score,
    };
    await window.openai?.setWidgetState(newState);

    if (currentQuestion < quizData!.questions.length - 1) {
      setCurrentQuestion(c => c + 1);
      setSelectedAnswer(null);
      setShowFeedback(false);
      setIsCorrect(false);
    } else {
      // Quiz complete
      setCompleted(true);
      await window.openai?.setWidgetState({
        ...newState,
        completed: true,
        score: isCorrect ? score + 1 : score,
      });

      // Send follow-up message
      await window.openai?.sendFollowUpMessage({
        prompt: `I completed the quiz and scored ${isCorrect ? score + 1 : score} out of ${quizData!.questions.length}. What should I do next?`
      });
    }
  }, [currentQuestion, quizData, score, isCorrect]);

  const handleClose = useCallback(() => {
    window.openai?.requestClose();
  }, []);

  if (!quizData) {
    return (
      <div style={styles.container}>
        <div style={styles.quizContainer}>
          <p style={{ textAlign: 'center', color: '#999' }}>Loading quiz...</p>
        </div>
      </div>
    );
  }

  if (completed) {
    const percentage = Math.round((score / quizData.questions.length) * 100);

    return (
      <div style={styles.container}>
        <div style={styles.resultsContainer}>
          <h2 style={{ ...styles.title, textAlign: 'center' }}>🎉 Quiz Complete!</h2>

          <div style={styles.scoreText}>{score}/{quizData.questions.length}</div>

          <div style={styles.statsContainer}>
            <div style={styles.statBox}>
              <div style={styles.statLabel}>Percentage</div>
              <div style={styles.statValue}>{percentage}%</div>
            </div>
            <div style={styles.statBox}>
              <div style={styles.statLabel}>Questions</div>
              <div style={styles.statValue}>{quizData.questions.length}</div>
            </div>
          </div>

          <p style={{ margin: '20px 0', color: '#ccc' }}>
            {percentage >= 80
              ? '🔥 Excellent work! You really know this stuff!'
              : percentage >= 60
                ? '👍 Good job! Keep learning and improving!'
                : '💪 Keep practicing! You\'ve got this!'}
          </p>

          <button style={styles.button(true)} onClick={handleClose}>
            Done
          </button>
        </div>
      </div>
    );
  }

  const question = quizData.questions[currentQuestion];
  const progress = ((currentQuestion) / quizData.questions.length) * 100;

  return (
    <div style={styles.container}>
      <div style={styles.quizContainer}>
        <div style={styles.header}>
          <h3 style={styles.title}>{quizData.title}</h3>
          <div style={styles.progressContainer}>
            <span style={{ fontSize: '14px', color: '#999' }}>
              {currentQuestion + 1}/{quizData.questions.length}
            </span>
          </div>
        </div>

        {/* Progress Bar */}
        <div style={{ ...styles.progressBar, marginBottom: '20px' }}>
          {quizData.questions.map((_, idx) => (
            <div
              key={idx}
              style={styles.progressDot(idx < currentQuestion)}
            />
          ))}
        </div>

        {/* Question */}
        <div style={styles.questionText}>
          {question.question_text}
        </div>

        {/* Options */}
        <div style={styles.optionsContainer}>
          {Object.entries(question.options).map(([key, value]) => (
            <QuizOption
              key={key}
              label={key}
              text={value}
              onClick={() => handleAnswerSelect(key)}
              isCorrect={showFeedback && isCorrect && selectedAnswer === key ? true : showFeedback && !isCorrect && selectedAnswer === key ? false : null}
              isSelected={selectedAnswer === key}
            />
          ))}
        </div>

        {/* Feedback */}
        {showFeedback && (
          <div style={styles.feedbackContainer}>
            {isCorrect ? (
              <p><strong>✅ Correct!</strong> {question.explanation}</p>
            ) : (
              <p><strong>❌ Not quite.</strong> {question.explanation}</p>
            )}
          </div>
        )}

        {/* Buttons */}
        <div style={styles.buttonContainer}>
          {showFeedback ? (
            <button
              style={styles.button(true)}
              onClick={handleNext}
            >
              {currentQuestion < quizData.questions.length - 1 ? 'Next Question' : 'See Results'}
            </button>
          ) : (
            <button
              style={{ ...styles.button(false), opacity: 0.5, cursor: 'not-allowed' }}
              disabled
            >
              Select an answer
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// ============= MOUNT =============

function App() {
  // Wait for DOM to be ready
  useEffect(() => {
    const root = document.getElementById('root');
    if (root) {
      ReactDOM.createRoot(root).render(<QuizInterface />);
    }
  }, []);

  return null;
}

export default App;
