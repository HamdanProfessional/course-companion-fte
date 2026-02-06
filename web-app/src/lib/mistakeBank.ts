/**
 * Mistake Bank - Tracks and manages student mistakes for review
 * Automatically catalogs every wrong answer into a "Review Later" folder
 */

export interface Mistake {
  id: string;
  questionId: string;
  quizId: string;
  quizTitle: string;
  questionText: string;
  wrongAnswer: string;
  correctAnswer: string;
  explanation?: string;
  feedback?: string;
  category?: string;
  difficulty: string;
  date: string;
  mastered: boolean;
  timesWrong: number;
  lastReviewed?: string;
}

const MISTAKE_BANK_KEY = 'mistake_bank';

/**
 * Get all mistakes from localStorage
 */
export const getMistakes = (): Mistake[] => {
  if (typeof window === 'undefined') return [];

  try {
    const stored = localStorage.getItem(MISTAKE_BANK_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch (error) {
    console.error('Error reading mistakes:', error);
    return [];
  }
};

/**
 * Save mistakes to localStorage
 */
const saveMistakes = (mistakes: Mistake[]): void => {
  if (typeof window === 'undefined') return;

  try {
    localStorage.setItem(MISTAKE_BANK_KEY, JSON.stringify(mistakes));
  } catch (error) {
    console.error('Error saving mistakes:', error);
  }
};

/**
 * Add a new mistake to the bank
 * If the same question was already wrong before, increment the counter
 */
export const addMistake = (mistake: Omit<Mistake, 'id' | 'date' | 'mastered' | 'timesWrong'>): void => {
  const mistakes = getMistakes();

  // Check if this question was already wrong before
  const existingMistake = mistakes.find(
    m => m.questionId === mistake.questionId && m.quizId === mistake.quizId
  );

  if (existingMistake) {
    // Update existing mistake
    existingMistake.wrongAnswer = mistake.wrongAnswer;
    existingMistake.timesWrong += 1;
    existingMistake.mastered = false; // Reset mastered status
    existingMistake.lastReviewed = new Date().toISOString();
  } else {
    // Add new mistake
    const newMistake: Mistake = {
      ...mistake,
      id: `${mistake.questionId}-${Date.now()}`,
      date: new Date().toISOString(),
      mastered: false,
      timesWrong: 1,
    };
    mistakes.push(newMistake);
  }

  saveMistakes(mistakes);
};

/**
 * Add mistakes from quiz results
 * Automatically extracts all wrong answers and adds them to the bank
 */
export const addMistakesFromQuiz = (
  quizId: string,
  quizTitle: string,
  results: Array<{
    question_id: string;
    question_text: string;
    selected_answer?: string;
    correct_answer?: string;
    is_correct?: boolean;
    points_earned: number;
    max_points: number;
    explanation?: string;
    feedback?: string;
  }>,
  difficulty: string,
  category?: string
): void => {
  const mistakes = getMistakes();

  results.forEach(result => {
    const isWrong = result.is_correct === false || result.points_earned === 0;

    if (isWrong && result.selected_answer) {
      addMistake({
        questionId: result.question_id,
        quizId,
        quizTitle,
        questionText: result.question_text,
        wrongAnswer: result.selected_answer,
        correctAnswer: result.correct_answer || 'See explanation',
        explanation: result.explanation,
        feedback: result.feedback,
        category,
        difficulty,
      });
    }
  });
};

/**
 * Mark a mistake as mastered
 */
export const markAsMastered = (mistakeId: string): void => {
  const mistakes = getMistakes();
  const mistake = mistakes.find(m => m.id === mistakeId);

  if (mistake) {
    mistake.mastered = true;
    mistake.lastReviewed = new Date().toISOString();
    saveMistakes(mistakes);
  }
};

/**
 * Mark a mistake as not mastered (for review)
 */
export const markForReview = (mistakeId: string): void => {
  const mistakes = getMistakes();
  const mistake = mistakes.find(m => m.id === mistakeId);

  if (mistake) {
    mistake.mastered = false;
    mistake.lastReviewed = new Date().toISOString();
    saveMistakes(mistakes);
  }
};

/**
 * Delete a mistake from the bank
 */
export const deleteMistake = (mistakeId: string): void => {
  const mistakes = getMistakes();
  const filtered = mistakes.filter(m => m.id !== mistakeId);
  saveMistakes(filtered);
};

/**
 * Clear all mastered mistakes
 */
export const clearMastered = (): void => {
  const mistakes = getMistakes();
  const filtered = mistakes.filter(m => !m.mastered);
  saveMistakes(filtered);
};

/**
 * Clear all mistakes
 */
export const clearAllMistakes = (): void => {
  saveMistakes([]);
};

/**
 * Get mistake statistics
 */
export const getMistakeStats = () => {
  const mistakes = getMistakes();

  const total = mistakes.length;
  const mastered = mistakes.filter(m => m.mastered).length;
  const remaining = total - mastered;

  // Count by category
  const byCategory: Record<string, number> = {};
  mistakes.forEach(m => {
    const cat = m.category || 'General';
    byCategory[cat] = (byCategory[cat] || 0) + 1;
  });

  // Count by difficulty
  const byDifficulty: Record<string, number> = {};
  mistakes.forEach(m => {
    byDifficulty[m.difficulty] = (byDifficulty[m.difficulty] || 0) + 1;
  });

  // Most common mistakes (questions wrong multiple times)
  const repeatMistakes = mistakes
    .filter(m => m.timesWrong > 1)
    .sort((a, b) => b.timesWrong - a.timesWrong)
    .slice(0, 5);

  return {
    total,
    mastered,
    remaining,
    byCategory,
    byDifficulty,
    repeatMistakes,
  };
};

/**
 * Filter mistakes by category, difficulty, or mastery status
 */
export const filterMistakes = (
  category?: string,
  difficulty?: string,
  mastered?: boolean
): Mistake[] => {
  const mistakes = getMistakes();

  return mistakes.filter(m => {
    if (category && m.category !== category) return false;
    if (difficulty && m.difficulty !== difficulty) return false;
    if (mastered !== undefined && m.mastered !== mastered) return false;
    return true;
  });
};

/**
 * Search mistakes by question text or answers
 */
export const searchMistakes = (query: string): Mistake[] => {
  const mistakes = getMistakes();
  const lowerQuery = query.toLowerCase();

  return mistakes.filter(m =>
    m.questionText.toLowerCase().includes(lowerQuery) ||
    m.wrongAnswer.toLowerCase().includes(lowerQuery) ||
    m.correctAnswer.toLowerCase().includes(lowerQuery) ||
    (m.category && m.category.toLowerCase().includes(lowerQuery))
  );
};

/**
 * Get mistakes that need review (not mastered, sorted by times wrong)
 */
export const getMistakesForReview = (): Mistake[] => {
  const mistakes = getMistakes();

  return mistakes
    .filter(m => !m.mastered)
    .sort((a, b) => b.timesWrong - a.timesWrong);
};

/**
 * Export mistakes as JSON (for backup)
 */
export const exportMistakes = (): string => {
  const mistakes = getMistakes();
  return JSON.stringify(mistakes, null, 2);
};

/**
 * Import mistakes from JSON
 */
export const importMistakes = (json: string): boolean => {
  try {
    const mistakes = JSON.parse(json) as Mistake[];
    saveMistakes(mistakes);
    return true;
  } catch (error) {
    console.error('Error importing mistakes:', error);
    return false;
  }
};
