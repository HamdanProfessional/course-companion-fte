/**
 * Infinite Quiz Engine - Procedurally generate unlimited practice problems
 *
 * Features:
 * - Question templates with variable placeholders
 * - Randomized generation for uniqueness
 * - Multiple difficulty levels
 * - Various topics and sub-topics
 * - Different question types
 */

export interface GeneratedQuestion {
  id: string;
  question: string;
  options: Record<string, string>;
  correctAnswer: string;
  explanation: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  topic: string;
  subtopic: string;
  type: 'multiple-choice' | 'fill-blank' | 'true-false' | 'code-completion';
}

export interface Topic {
  id: string;
  name: string;
  icon: string;
  subtopics: Subtopic[];
}

export interface Subtopic {
  id: string;
  name: string;
  templates: QuestionTemplate[];
}

interface QuestionTemplate {
  pattern: string;
  type: 'multiple-choice' | 'fill-blank' | 'true-false' | 'code-completion';
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  generate: () => GeneratedQuestion;
}

// Utility functions for randomization
const randomInt = (min: number, max: number): number => {
  return Math.floor(Math.random() * (max - min + 1)) + min;
};

const randomItem = <T,>(array: T[]): T => {
  return array[Math.floor(Math.random() * array.length)];
};

const shuffleArray = <T,>(array: T[]): T[] => {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
};

// ============================================================================
// TOPIC: JavaScript
// ============================================================================

const javascriptBasicsTemplates: QuestionTemplate[] = [
  // Variable declarations
  {
    pattern: 'variable_declaration',
    type: 'multiple-choice',
    difficulty: 'beginner',
    generate: () => {
      const keywords = ['const', 'let', 'var'];
      const correct = randomItem(keywords);
      const question = `Which keyword is used to declare a ${correct === 'const' ? 'constant' : correct === 'let' ? 'block-scoped variable' : 'function-scoped variable'} in modern JavaScript?`;

      const wrongOptions = keywords.filter(k => k !== correct);
      const options = {
        A: correct,
        B: randomItem(wrongOptions),
        C: wrongOptions.find(w => w !== randomItem(wrongOptions)) || wrongOptions[0],
        D: 'static',
      };

      return {
        id: `js-var-${Date.now()}`,
        question,
        options,
        correctAnswer: 'A',
        explanation: `${correct} is used to declare ${correct === 'const' ? 'constants that cannot be reassigned' : correct === 'let' ? 'block-scoped variables that can be reassigned' : 'function-scoped variables (legacy)'}.`,
        difficulty: 'beginner',
        topic: 'JavaScript',
        subtopic: 'Basics',
        type: 'multiple-choice',
      };
    },
  },
  // Data types
  {
    pattern: 'data_types',
    type: 'multiple-choice',
    difficulty: 'beginner',
    generate: () => {
      const types = [
        { name: 'String', example: '"Hello"' },
        { name: 'Number', example: '42' },
        { name: 'Boolean', example: 'true' },
        { name: 'Array', example: '[1, 2, 3]' },
        { name: 'Object', example: '{ key: "value" }' },
      ];
      const selected = randomItem(types);

      const question = `What data type is represented by: ${selected.example}?`;

      const wrongOptions = types.filter(t => t.name !== selected.name).map(t => t.name);
      const options = {
        A: selected.name,
        B: randomItem(wrongOptions),
        C: wrongOptions.find((_, i) => i !== wrongOptions.indexOf(randomItem(wrongOptions))) || wrongOptions[0],
        D: 'Undefined',
      };

      return {
        id: `js-type-${Date.now()}`,
        question,
        options,
        correctAnswer: 'A',
        explanation: `${selected.name} is a primitive data type in JavaScript.`,
        difficulty: 'beginner',
        topic: 'JavaScript',
        subtopic: 'Basics',
        type: 'multiple-choice',
      };
    },
  },
  // Array methods
  {
    pattern: 'array_methods',
    type: 'multiple-choice',
    difficulty: 'intermediate',
    generate: () => {
      const methods = [
        {
          name: 'map()',
          description: 'creates a new array by transforming each element',
          example: '[1, 2, 3].map(x => x * 2) // [2, 4, 6]',
        },
        {
          name: 'filter()',
          description: 'creates a new array with elements that pass a test',
          example: '[1, 2, 3].filter(x => x > 1) // [2, 3]',
        },
        {
          name: 'reduce()',
          description: 'reduces array to a single value',
          example: '[1, 2, 3].reduce((a, b) => a + b) // 6',
        },
        {
          name: 'forEach()',
          description: 'executes a function for each element',
          example: '[1, 2, 3].forEach(x => console.log(x))',
        },
      ];
      const selected = randomItem(methods);

      const question = `Which array method ${selected.description}?`;

      const wrongOptions = methods.filter(m => m.name !== selected.name).map(m => m.name);
      const options = {
        A: selected.name,
        B: randomItem(wrongOptions),
        C: wrongOptions.find((_, i) => i !== wrongOptions.indexOf(randomItem(wrongOptions))) || wrongOptions[0],
        D: 'sort()',
      };

      return {
        id: `js-array-${Date.now()}`,
        question,
        options,
        correctAnswer: 'A',
        explanation: `${selected.name} ${selected.description}. Example: ${selected.example}`,
        difficulty: 'intermediate',
        topic: 'JavaScript',
        subtopic: 'Arrays',
        type: 'multiple-choice',
      };
    },
  },
];

const javascriptAsyncTemplates: QuestionTemplate[] = [
  // Promises
  {
    pattern: 'promises',
    type: 'multiple-choice',
    difficulty: 'intermediate',
    generate: () => {
      const states = [
        { state: 'pending', description: 'initial state, neither fulfilled nor rejected' },
        { state: 'fulfilled', description: 'operation completed successfully' },
        { state: 'rejected', description: 'operation failed' },
      ];
      const selected = randomItem(states);

      const question = `What does it mean when a Promise is in the "${selected.state}" state?`;

      const wrongOptions = states.filter(s => s.state !== selected.state).map(s => s.description);
      const options = {
        A: selected.description,
        B: randomItem(wrongOptions),
        C: wrongOptions.find((_, i) => i !== wrongOptions.indexOf(randomItem(wrongOptions))) || wrongOptions[0],
        D: 'The Promise has been cancelled',
      };

      return {
        id: `js-promise-${Date.now()}`,
        question,
        options,
        correctAnswer: 'A',
        explanation: `A Promise in ${selected.state} state means ${selected.description}.`,
        difficulty: 'intermediate',
        topic: 'JavaScript',
        subtopic: 'Async/Await',
        type: 'multiple-choice',
      };
    },
  },
  // Async/await
  {
    pattern: 'async_await',
    type: 'multiple-choice',
    difficulty: 'intermediate',
    generate: () => {
      const questions = [
        {
          q: 'What keyword is used to declare an async function?',
          correct: 'async',
          wrong: ['await', 'promise', 'defer'],
        },
        {
          q: 'What keyword pauses execution until a Promise resolves?',
          correct: 'await',
          wrong: ['async', 'yield', 'wait'],
        },
        {
          q: 'Can "await" be used outside an async function?',
          correct: 'No',
          wrong: ['Yes', 'Only in strict mode', 'Only with modules'],
        },
      ];

      const selected = randomItem(questions);
      const wrongOptions = shuffleArray(selected.wrong);

      return {
        id: `js-async-${Date.now()}`,
        question: selected.q,
        options: {
          A: selected.correct,
          B: wrongOptions[0],
          C: wrongOptions[1],
          D: wrongOptions[2] || 'undefined',
        },
        correctAnswer: 'A',
        explanation: `${selected.correct} is used for this purpose in JavaScript async programming.`,
        difficulty: 'intermediate',
        topic: 'JavaScript',
        subtopic: 'Async/Await',
        type: 'multiple-choice',
      };
    },
  },
];

// ============================================================================
// TOPIC: Python
// ============================================================================

const pythonBasicsTemplates: QuestionTemplate[] = [
  // Variables and types
  {
    pattern: 'python_types',
    type: 'multiple-choice',
    difficulty: 'beginner',
    generate: () => {
      const types = [
        { name: 'int', example: '42', description: 'integer numbers' },
        { name: 'float', example: '3.14', description: 'decimal numbers' },
        { name: 'str', example: '"Hello"', description: 'strings/ text' },
        { name: 'bool', example: 'True', description: 'boolean values' },
        { name: 'list', example: '[1, 2, 3]', description: 'ordered collections' },
      ];
      const selected = randomItem(types);

      const question = `What Python data type is represented by: ${selected.example}?`;

      const wrongOptions = types.filter(t => t.name !== selected.name).map(t => t.name);
      const options = {
        A: selected.name,
        B: randomItem(wrongOptions),
        C: wrongOptions.find((_, i) => i !== wrongOptions.indexOf(randomItem(wrongOptions))) || wrongOptions[0],
        D: 'dict',
      };

      return {
        id: `py-type-${Date.now()}`,
        question,
        options,
        correctAnswer: 'A',
        explanation: `${selected.name} represents ${selected.description} in Python.`,
        difficulty: 'beginner',
        topic: 'Python',
        subtopic: 'Basics',
        type: 'multiple-choice',
      };
    },
  },
  // List comprehensions
  {
    pattern: 'list_comprehension',
    type: 'multiple-choice',
    difficulty: 'intermediate',
    generate: () => {
      const num = randomInt(1, 10);
      const multiplier = randomInt(2, 5);

      const question = `What is the output of: [x * ${multiplier} for x in range(${num})]?`;

      const correctAnswer = Array.from({ length: num }, (_, i) => i * multiplier).join(', ');

      const wrongAnswers = [
        Array.from({ length: num }, (_, i) => (i + 1) * multiplier).join(', '),
        Array.from({ length: num }, (_, i) => i + multiplier).join(', '),
        `range(${num})`,
      ];

      const options = {
        A: `[${correctAnswer}]`,
        B: `[${wrongAnswers[0]}]`,
        C: `[${wrongAnswers[1]}]`,
        D: wrongAnswers[2],
      };

      return {
        id: `py-listcomp-${Date.now()}`,
        question,
        options,
        correctAnswer: 'A',
        explanation: `List comprehension generates [0*${multiplier}, 1*${multiplier}, ..., ${num-1}*${multiplier}] = [${correctAnswer}]`,
        difficulty: 'intermediate',
        topic: 'Python',
        subtopic: 'Lists',
        type: 'multiple-choice',
      };
    },
  },
];

// ============================================================================
// TOPIC: React
// ============================================================================

const reactBasicsTemplates: QuestionTemplate[] = [
  // JSX
  {
    pattern: 'jsx',
    type: 'multiple-choice',
    difficulty: 'beginner',
    generate: () => {
      const questions = [
        {
          q: 'What does JSX stand for?',
          correct: 'JavaScript XML',
          wrong: ['Java Syntax Extension', 'JSON Extended', 'JavaScript Extension'],
        },
        {
          q: 'Can you use JavaScript expressions inside JSX?',
          correct: 'Yes, using curly braces {}',
          wrong: ['No', 'Yes, using parentheses ()', 'Yes, using square brackets []'],
        },
        {
          q: 'What must you return from a React component?',
          correct: 'A single element or fragment',
          wrong: ['Always a div', 'An array', 'A string'],
        },
      ];

      const selected = randomItem(questions);
      const wrongOptions = shuffleArray(selected.wrong);

      return {
        id: `react-jsx-${Date.now()}`,
        question: selected.q,
        options: {
          A: selected.correct,
          B: wrongOptions[0],
          C: wrongOptions[1],
          D: wrongOptions[2],
        },
        correctAnswer: 'A',
        explanation: selected.correct,
        difficulty: 'beginner',
        topic: 'React',
        subtopic: 'JSX',
        type: 'multiple-choice',
      };
    },
  },
  // Props
  {
    pattern: 'props',
    type: 'multiple-choice',
    difficulty: 'intermediate',
    generate: () => {
      const questions = [
        {
          q: 'How do you pass data to a React component?',
          correct: 'Using props',
          wrong: ['Using state', 'Using context', 'Using refs'],
        },
        {
          q: 'Are props read-only?',
          correct: 'Yes, props are immutable',
          wrong: ['No, they can be modified', 'Only in class components', 'Only with the spread operator'],
        },
      ];

      const selected = randomItem(questions);
      const wrongOptions = shuffleArray(selected.wrong);

      return {
        id: `react-props-${Date.now()}`,
        question: selected.q,
        options: {
          A: selected.correct,
          B: wrongOptions[0],
          C: wrongOptions[1],
          D: wrongOptions[2],
        },
        correctAnswer: 'A',
        explanation: selected.correct,
        difficulty: 'intermediate',
        topic: 'React',
        subtopic: 'Props',
        type: 'multiple-choice',
      };
    },
  },
];

// ============================================================================
// TOPIC: API Development
// ============================================================================

const apiBasicsTemplates: QuestionTemplate[] = [
  // HTTP methods
  {
    pattern: 'http_methods',
    type: 'multiple-choice',
    difficulty: 'beginner',
    generate: () => {
      const methods = [
        {
          name: 'GET',
          description: 'retrieve data from a server',
          safe: true,
        },
        {
          name: 'POST',
          description: 'create new data on a server',
          safe: false,
        },
        {
          name: 'PUT',
          description: 'update existing data (full replacement)',
          safe: false,
        },
        {
          name: 'DELETE',
          description: 'remove data from a server',
          safe: false,
        },
      ];
      const selected = randomItem(methods);

      const question = `Which HTTP method is used to ${selected.description}?`;

      const wrongOptions = methods.filter(m => m.name !== selected.name).map(m => m.name);
      const options = {
        A: selected.name,
        B: randomItem(wrongOptions),
        C: wrongOptions.find((_, i) => i !== wrongOptions.indexOf(randomItem(wrongOptions))) || wrongOptions[0],
        D: wrongOptions.find((_, i) => i !== wrongOptions.indexOf(randomItem(wrongOptions)) && wrongOptions[i] !== options.C) || wrongOptions[0],
      };

      return {
        id: `api-http-${Date.now()}`,
        question,
        options,
        correctAnswer: 'A',
        explanation: `${selected.name} is used to ${selected.description}. It is ${selected.safe ? 'safe' : 'not safe'} (doesn't/does modify data).`,
        difficulty: 'beginner',
        topic: 'API Development',
        subtopic: 'HTTP Methods',
        type: 'multiple-choice',
      };
    },
  },
  // Status codes
  {
    pattern: 'status_codes',
    type: 'multiple-choice',
    difficulty: 'intermediate',
    generate: () => {
      const codes = [
        { code: '200', description: 'OK - Request succeeded', category: 'Success' },
        { code: '201', description: 'Created - Resource created', category: 'Success' },
        { code: '400', description: 'Bad Request - Invalid input', category: 'Client Error' },
        { code: '401', description: 'Unauthorized - Authentication required', category: 'Client Error' },
        { code: '403', description: 'Forbidden - Insufficient permissions', category: 'Client Error' },
        { code: '404', description: 'Not Found - Resource doesn\'t exist', category: 'Client Error' },
        { code: '500', description: 'Internal Server Error', category: 'Server Error' },
      ];
      const selected = randomItem(codes);

      const question = `What does HTTP status code ${selected.code} mean?`;

      const wrongOptions = codes.filter(c => c.code !== selected.code).map(c => c.description).slice(0, 3);
      const options = {
        A: selected.description,
        B: wrongOptions[0],
        C: wrongOptions[1],
        D: wrongOptions[2] || 'Unknown error',
      };

      return {
        id: `api-status-${Date.now()}`,
        question,
        options,
        correctAnswer: 'A',
        explanation: `HTTP ${selected.code}: ${selected.description} (${selected.category})`,
        difficulty: 'intermediate',
        topic: 'API Development',
        subtopic: 'Status Codes',
        type: 'multiple-choice',
      };
    },
  },
];

// ============================================================================
// TOPICS CONFIGURATION
// ============================================================================

export const topics: Topic[] = [
  {
    id: 'javascript',
    name: 'JavaScript',
    icon: 'JS',
    subtopics: [
      {
        id: 'js-basics',
        name: 'Basics',
        templates: javascriptBasicsTemplates,
      },
      {
        id: 'js-async',
        name: 'Async/Await',
        templates: javascriptAsyncTemplates,
      },
    ],
  },
  {
    id: 'python',
    name: 'Python',
    icon: '🐍',
    subtopics: [
      {
        id: 'py-basics',
        name: 'Basics',
        templates: pythonBasicsTemplates,
      },
    ],
  },
  {
    id: 'react',
    name: 'React',
    icon: '⚛️',
    subtopics: [
      {
        id: 'react-basics',
        name: 'Basics',
        templates: reactBasicsTemplates,
      },
    ],
  },
  {
    id: 'api',
    name: 'API Development',
    icon: '🔌',
    subtopics: [
      {
        id: 'api-basics',
        name: 'HTTP Methods',
        templates: apiBasicsTemplates,
      },
    ],
  },
];

// ============================================================================
// GENERATION FUNCTIONS
// ============================================================================

/**
 * Generate a single question from a specific subtopic
 */
export const generateQuestion = (
  topicId: string,
  subtopicId: string,
  difficulty?: 'beginner' | 'intermediate' | 'advanced'
): GeneratedQuestion | null => {
  const topic = topics.find(t => t.id === topicId);
  if (!topic) return null;

  const subtopic = topic.subtopics.find(s => s.id === subtopicId);
  if (!subtopic || subtopic.templates.length === 0) return null;

  // Filter templates by difficulty if specified
  let availableTemplates = subtopic.templates;
  if (difficulty) {
    availableTemplates = subtopic.templates.filter(t => t.difficulty === difficulty);
    if (availableTemplates.length === 0) {
      // Fallback to any difficulty if specific level not available
      availableTemplates = subtopic.templates;
    }
  }

  // Select a random template
  const template = randomItem(availableTemplates);

  // Generate the question
  return template.generate();
};

/**
 * Generate multiple questions
 */
export const generateQuestions = (
  topicId: string,
  subtopicId: string,
  count: number,
  difficulty?: 'beginner' | 'intermediate' | 'advanced'
): GeneratedQuestion[] => {
  const questions: GeneratedQuestion[] = [];
  const generatedIds = new Set<string>();

  let attempts = 0;
  const maxAttempts = count * 10; // Prevent infinite loop

  while (questions.length < count && attempts < maxAttempts) {
    const question = generateQuestion(topicId, subtopicId, difficulty);

    if (question && !generatedIds.has(question.id)) {
      questions.push(question);
      generatedIds.add(question.id);
    }

    attempts++;
  }

  return questions;
};

/**
 * Generate a quiz with mixed difficulties
 */
export const generateMixedQuiz = (
  topicId: string,
  subtopicId: string,
  count: number
): GeneratedQuestion[] => {
  const questions: GeneratedQuestion[] = [];
  const difficulties: Array<'beginner' | 'intermediate' | 'advanced'> = ['beginner', 'intermediate', 'advanced'];

  // Distribute questions across difficulty levels
  const perDifficulty = Math.ceil(count / difficulties.length);

  difficulties.forEach(diff => {
    const diffQuestions = generateQuestions(topicId, subtopicId, perDifficulty, diff);
    questions.push(...diffQuestions);
  });

  // Trim to exact count and shuffle
  return shuffleArray(questions.slice(0, count));
};

/**
 * Get all available topics
 */
export const getTopics = (): Topic[] => {
  return topics;
};

/**
 * Get a specific topic by ID
 */
export const getTopic = (topicId: string): Topic | undefined => {
  return topics.find(t => t.id === topicId);
};

/**
 * Get subtopics for a topic
 */
export const getSubtopics = (topicId: string): Subtopic[] => {
  const topic = getTopic(topicId);
  return topic?.subtopics || [];
};
