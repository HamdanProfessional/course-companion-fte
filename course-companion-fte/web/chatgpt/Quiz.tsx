import { useState } from "react";
import { useRequestDisplayMode } from "@gadgetinc/react-chatgpt-apps";
import { Button } from "@openai/apps-sdk-ui/components/Button";
import { Expand } from "@openai/apps-sdk-ui/components/Icon";

const QUIZ = {
  id: "quiz-1",
  title: "AI Agents Fundamentals Quiz",
  difficulty: "BEGINNER",
  questions: [
    {
      id: "q1",
      question_text: "What is an AI Agent?",
      options: {
        A: "A system that can perceive, reason, and act autonomously",
        B: "A simple chatbot",
        C: "A script that runs on a schedule",
        D: "A database query tool"
      },
      correct_answer: "A"
    },
    {
      id: "q2",
      question_text: "What does MCP stand for?",
      options: {
        A: "Model Context Protocol",
        B: "Machine Control Platform",
        C: "Multi-Cloud Processing",
        D: "Memory Cache Protocol"
      },
      correct_answer: "A"
    },
    {
      id: "q3",
      question_text: "What's a key difference between an AI Agent and a regular chatbot?",
      options: {
        A: "Agents can take actions, chatbots only respond",
        B: "Agents are faster",
        C: "Chatbots use more memory",
        D: "There's no difference"
      },
      correct_answer: "A"
    }
  ]
};

const Quiz = () => {
  const displayMode = useRequestDisplayMode();
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string>>({});
  const [submitted, setSubmitted] = useState(false);
  const [score, setScore] = useState(0);

  const question = QUIZ.questions[currentQuestion];
  const progress = ((currentQuestion + 1) / QUIZ.questions.length) * 100;

  const handleSelectAnswer = (optionKey: string) => {
    if (submitted) return;
    setSelectedAnswers({ ...selectedAnswers, [question.id]: optionKey });
  };

  const handleNext = () => {
    if (currentQuestion < QUIZ.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleSubmit = () => {
    const correctCount = Object.entries(selectedAnswers).filter(
      ([qid, answer]) => QUIZ.questions.find(q => q.id === qid)?.correct_answer === answer
    ).length;
    setScore(correctCount);
    setSubmitted(true);
  };

  const allAnswered = QUIZ.questions.every(q => selectedAnswers[q.id]);

  if (submitted) {
    const percentage = Math.round((score / QUIZ.questions.length) * 100);
    const passed = percentage >= 70;

    return (
      <div className="p-6 max-w-2xl mx-auto">
        <div className="text-center">
          <div className={`w-32 h-32 mx-auto rounded-full flex flex-col items-center justify-content-center mb-6 ${
            passed ? "bg-gradient-to-br from-green-500 to-green-600" : "bg-gradient-to-br from-red-500 to-red-600"
          } text-white`}>
            <div className="text-4xl font-bold">{percentage}%</div>
            <div className="text-xs">{passed ? "Passed!" : "Keep practicing"}</div>
          </div>

          <h2 className="text-xl font-semibold tracking-tight mb-2">Quiz Complete!</h2>
          <p className="text-gray-600 mb-6">
            You got {score} out of {QUIZ.questions.length} questions correct.
          </p>

          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-900">
              💡 {passed
                ? "Great job! You understand AI Agents fundamentals!"
                : "Review the course material and try again!"}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <div className="w-full flex justify-end mb-4">
        {displayMode && (
          <Button
            color="secondary"
            variant="soft"
            aria-label="Enter fullscreen"
            className="rounded-full size-10"
            onClick={() => displayMode("fullscreen")}
          >
            <Expand />
          </Button>
        )}
      </div>

      <div className="mb-6">
        <h2 className="text-xl font-semibold tracking-tight mb-2">{QUIZ.title}</h2>
        <div className="flex items-center gap-2 mb-4">
          <span className="px-2 py-0.5 rounded-full bg-green-100 text-green-700 text-xs font-semibold">
            {QUIZ.difficulty}
          </span>
        </div>

        <div className="relative h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="absolute top-0 left-0 h-full bg-gradient-to-r from-purple-500 to-indigo-600 transition-all"
            style={{ width: `${progress}%` }}
          />
          <span className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-xs font-semibold text-gray-700">
            {currentQuestion + 1} / {QUIZ.questions.length}
          </span>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <div className="text-xs text-gray-500 uppercase font-semibold mb-3">
          Question {currentQuestion + 1}
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-6">{question.question_text}</h3>

        <div className="flex flex-col gap-3">
          {Object.entries(question.options).map(([key, value]) => {
            const isSelected = selectedAnswers[question.id] === key;
            return (
              <button
                key={key}
                onClick={() => handleSelectAnswer(key)}
                disabled={submitted}
                className={`p-4 border-2 rounded-lg text-left transition-all ${
                  isSelected
                    ? "border-purple-500 bg-purple-50"
                    : "border-gray-200 hover:border-purple-300 hover:bg-purple-50/50"
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-7 h-7 rounded flex items-center justify-center font-semibold text-sm ${
                    isSelected ? "bg-purple-500 text-white" : "bg-gray-200 text-gray-700"
                  }`}>
                    {key}
                  </div>
                  <span className="flex-1">{value}</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      <div className="flex gap-3 justify-between">
        <Button
          color="secondary"
          variant="outline"
          onClick={handlePrevious}
          disabled={currentQuestion === 0 || submitted}
        >
          ← Previous
        </Button>

        {currentQuestion === QUIZ.questions.length - 1 ? (
          <Button
            color="primary"
            onClick={handleSubmit}
            disabled={!allAnswered || submitted}
          >
            {submitted ? "Submitted ✓" : "Submit Quiz"}
          </Button>
        ) : (
          <Button
            color="secondary"
            onClick={handleNext}
            disabled={submitted}
          >
            Next →
          </Button>
        )}
      </div>
    </div>
  );
};

export default Quiz;
