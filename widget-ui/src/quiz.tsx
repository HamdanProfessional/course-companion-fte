// Quiz Widget for Course Companion FTE
import React, { useState, useEffect } from 'react';

// Types
interface Question {
  id: string;
  question_text: string;
  options: {
    A: string;
    B: string;
    C: string;
    D: string;
  };
  explanation: string;
  order: number;
}

interface QuizData {
  title: string;
  difficulty: string;
  questions: Question[];
}

// Main Quiz Component
function QuizWidget() {
  const [quiz, setQuiz] = useState<QuizData | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string>>({});
  const [showResults, setShowResults] = useState(false);
  const [loading, setLoading] = useState(true);
  const [submitted, setSubmitted] = useState(false);
  const [score, setScore] = useState(0);

  // Get quiz data from tool output
  useEffect(() => {
    try {
      const toolOutput = (window.openai as any)?.toolOutput as QuizData;
      if (toolOutput?.questions) {
        setQuiz(toolOutput);
      }
      setLoading(false);
    } catch (err) {
      setLoading(false);
    }
  }, []);

  // Select an answer
  function selectAnswer(option: string) {
    if (submitted) return;
    setSelectedAnswers({ ...selectedAnswers, [currentQuestion]: option });
  }

  // Submit quiz
  async function submitQuiz() {
    try {
      setSubmitted(true);
      const callTool = (window.openai as any)?.callTool;

      if (callTool && quiz) {
        // Calculate score
        let correctCount = 0;
        quiz.questions.forEach((q, idx) => {
          // Assuming A is always correct for now - in real app, would come from backend
          if (selectedAnswers[idx] === 'A') {
            correctCount++;
          }
        });

        setScore(correctCount);
        setShowResults(true);

        // Submit to backend
        await callTool('submit_quiz', {
          quiz_id: (window as any).quizId,
          answers: selectedAnswers
        });

        // Send follow-up message
        (window.openai as any)?.sendFollowUpMessage(
          `Quiz completed! Score: ${correctCount}/${quiz.questions.length} correct.`
        );
      }
    } catch (err) {
      console.error('Failed to submit quiz:', err);
    }
  }

  // Next question
  function nextQuestion() {
    if (quiz && currentQuestion < quiz.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  }

  // Previous question
  function prevQuestion() {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  }

  if (loading) {
    return (
      <div className="quiz-widget">
        <div className="loading">Loading quiz...</div>
      </div>
    );
  }

  if (!quiz) {
    return (
      <div className="quiz-widget">
        <div className="error">Failed to load quiz</div>
      </div>
    );
  }

  const question = quiz.questions[currentQuestion];
  const progress = ((currentQuestion + 1) / quiz.questions.length) * 100;

  if (showResults) {
    const percentage = Math.round((score / quiz.questions.length) * 100);
    const passed = percentage >= 70;

    return (
      <div className="quiz-widget">
        <div className="results">
          <div className={`score-circle ${passed ? 'passed' : 'failed'}`}>
            <div className="score">{percentage}%</div>
            <div className="label">{passed ? 'Passed!' : 'Keep practicing'}</div>
          </div>

          <h2>Quiz Complete!</h2>
          <p className="score-detail">
            You got {score} out of {quiz.questions.length} questions correct.
          </p>

          <div className="review">
            <h3>Review Answers:</h3>
            {quiz.questions.map((q, idx) => {
              const isCorrect = selectedAnswers[idx] === 'A'; // Simplified logic
              return (
                <div key={q.id} className={`review-item ${isCorrect ? 'correct' : 'incorrect'}`}>
                  <span className="question-number">Q{idx + 1}</span>
                  <span className="answer">
                    Your answer: {selectedAnswers[idx] || 'Not answered'} {isCorrect ? '✓' : '✗'}
                  </span>
                  {!isCorrect && (
                    <div className="explanation">
                      <strong>Explanation:</strong> {q.explanation}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  }

  const hasAnsweredAll = Object.keys(selectedAnswers).length === quiz.questions.length;

  return (
    <div className="quiz-widget">
      <header>
        <div className="title">
          <h2>{quiz.title}</h2>
          <span className="difficulty">{quiz.difficulty}</span>
        </div>
        <div className="progress">
          <div className="progress-bar" style={{ width: `${progress}%` }}></div>
          <span className="progress-text">{currentQuestion + 1} / {quiz.questions.length}</span>
        </div>
      </header>

      <div className="question-card">
        <div className="question-header">
          <span className="question-number">Question {currentQuestion + 1}</span>
        </div>

        <h3 className="question-text">{question.question_text}</h3>

        <div className="options">
          {Object.entries(question.options).map(([key, value]) => {
            const isSelected = selectedAnswers[currentQuestion] === key;
            return (
              <button
                key={key}
                className={`option ${isSelected ? 'selected' : ''}`}
                onClick={() => selectAnswer(key)}
                disabled={submitted}
              >
                <span className="option-key">{key}</span>
                <span className="option-value">{value}</span>
                {isSelected && <span className="checkmark">✓</span>}
              </button>
            );
          })}
        </div>

        <div className="navigation">
          <button
            onClick={prevQuestion}
            disabled={currentQuestion === 0 || submitted}
            className="nav-btn"
          >
            ← Previous
          </button>

          {currentQuestion === quiz.questions.length - 1 ? (
            <button
              onClick={submitQuiz}
              disabled={!hasAnsweredAll || submitted}
              className="submit-btn"
            >
              {submitted ? 'Submitted ✓' : 'Submit Quiz'}
            </button>
          ) : (
            <button
              onClick={nextQuestion}
              className="nav-btn"
            >
              Next →
            </button>
          )}
        </div>

        {submitted && question.explanation && (
          <div className="explanation-box">
            <strong>💡 Explanation:</strong> {question.explanation}
          </div>
        )}
      </div>
    </div>
  );
}

// Mount the widget
const root = document.getElementById('root');
if (root) {
  // @ts-ignore
  ReactDOM.createRoot(root).render(<QuizWidget />);
}

export default QuizWidget;
