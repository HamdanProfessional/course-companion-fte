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
// TOPIC: SQL/Database
// ============================================================================

const sqlBasicsTemplates: QuestionTemplate[] = [
  // SELECT queries
  {
    pattern: 'select_queries',
    type: 'multiple-choice',
    difficulty: 'beginner',
    generate: () => {
      const questions = [
        {
          q: 'Which SQL statement is used to retrieve data from a database?',
          correct: 'SELECT',
          wrong: ['GET', 'FETCH', 'RETRIEVE'],
        },
        {
          q: 'Which clause is used to filter results in SQL?',
          correct: 'WHERE',
          wrong: ['FILTER', 'HAVING', 'THAT'],
        },
        {
          q: 'How do you select all columns from a table?',
          correct: 'SELECT *',
          wrong: ['SELECT ALL', 'SELECT @', 'GET *'],
        },
      ];

      const selected = randomItem(questions);
      const wrongOptions = shuffleArray(selected.wrong);

      return {
        id: `sql-select-${Date.now()}`,
        question: selected.q,
        options: {
          A: selected.correct,
          B: wrongOptions[0],
          C: wrongOptions[1],
          D: wrongOptions[2],
        },
        correctAnswer: 'A',
        explanation: `${selected.correct} is the correct SQL statement for this operation.`,
        difficulty: 'beginner',
        topic: 'SQL',
        subtopic: 'Queries',
        type: 'multiple-choice',
      };
    },
  },
  // JOINs
  {
    pattern: 'joins',
    type: 'multiple-choice',
    difficulty: 'intermediate',
    generate: () => {
      const joins = [
        {
          type: 'INNER JOIN',
          description: 'returns records that have matching values in both tables',
        },
        {
          type: 'LEFT JOIN',
          description: 'returns all records from the left table, and matched records from the right',
        },
        {
          type: 'RIGHT JOIN',
          description: 'returns all records from the right table, and matched records from the left',
        },
        {
          type: 'FULL OUTER JOIN',
          description: 'returns all records when there is a match in either table',
        },
      ];
      const selected = randomItem(joins);

      const question = `Which JOIN type ${selected.description}?`;

      const wrongOptions = joins.filter(j => j.type !== selected.type).map(j => j.type);
      const options = {
        A: selected.type,
        B: randomItem(wrongOptions),
        C: wrongOptions.find((_, i) => i !== wrongOptions.indexOf(randomItem(wrongOptions))) || wrongOptions[0],
        D: 'CROSS JOIN',
      };

      return {
        id: `sql-join-${Date.now()}`,
        question,
        options,
        correctAnswer: 'A',
        explanation: `${selected.type}: ${selected.description}`,
        difficulty: 'intermediate',
        topic: 'SQL',
        subtopic: 'JOINs',
        type: 'multiple-choice',
      };
    },
  },
];

// ============================================================================
// TOPIC: Git/Version Control
// ============================================================================

const gitBasicsTemplates: QuestionTemplate[] = [
  // Basic commands
  {
    pattern: 'git_commands',
    type: 'multiple-choice',
    difficulty: 'beginner',
    generate: () => {
      const commands = [
        {
          cmd: 'git init',
          description: 'initialize a new Git repository',
        },
        {
          cmd: 'git clone',
          description: 'copy a repository from a remote source',
        },
        {
          cmd: 'git add',
          description: 'stage files for commit',
        },
        {
          cmd: 'git commit',
          description: 'save changes to the repository',
        },
        {
          cmd: 'git push',
          description: 'upload local commits to remote repository',
        },
        {
          cmd: 'git pull',
          description: 'fetch and merge changes from remote repository',
        },
      ];
      const selected = randomItem(commands);

      const question = `What does the command "${selected.cmd}" do?`;

      const wrongOptions = commands.filter(c => c.cmd !== selected.cmd).map(c => c.description).slice(0, 3);
      const options = {
        A: selected.description,
        B: wrongOptions[0],
        C: wrongOptions[1],
        D: wrongOptions[2],
      };

      return {
        id: `git-cmd-${Date.now()}`,
        question,
        options,
        correctAnswer: 'A',
        explanation: `${selected.cmd}: ${selected.description}`,
        difficulty: 'beginner',
        topic: 'Git',
        subtopic: 'Commands',
        type: 'multiple-choice',
      };
    },
  },
  // Branching
  {
    pattern: 'branching',
    type: 'multiple-choice',
    difficulty: 'intermediate',
    generate: () => {
      const questions = [
        {
          q: 'What command creates a new branch?',
          correct: 'git branch <branch-name>',
          wrong: ['git new <branch-name>', 'git create <branch-name>', 'git make-branch <branch-name>'],
        },
        {
          q: 'What command switches to a different branch?',
          correct: 'git checkout <branch-name>',
          wrong: ['git switch <branch-name>', 'git go <branch-name>', 'git move <branch-name>'],
        },
        {
          q: 'What command merges branches?',
          correct: 'git merge <branch-name>',
          wrong: ['git combine <branch-name>', 'git join <branch-name>', 'git blend <branch-name>'],
        },
      ];

      const selected = randomItem(questions);
      const wrongOptions = shuffleArray(selected.wrong);

      return {
        id: `git-branch-${Date.now()}`,
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
        topic: 'Git',
        subtopic: 'Branching',
        type: 'multiple-choice',
      };
    },
  },
];

// ============================================================================
// TOPIC: Docker
// ============================================================================

const dockerBasicsTemplates: QuestionTemplate[] = [
  // Docker concepts
  {
    pattern: 'docker_concepts',
    type: 'multiple-choice',
    difficulty: 'beginner',
    generate: () => {
      const questions = [
        {
          q: 'What is a Docker container?',
          correct: 'A lightweight, standalone package of software',
          wrong: ['A virtual machine', 'A physical server', 'A programming language'],
        },
        {
          q: 'What is a Docker image?',
          correct: 'A read-only template for creating containers',
          wrong: ['A running container', 'A Docker file', 'A network configuration'],
        },
        {
          q: 'What command builds a Docker image?',
          correct: 'docker build',
          wrong: ['docker create', 'docker make', 'docker compile'],
        },
      ];

      const selected = randomItem(questions);
      const wrongOptions = shuffleArray(selected.wrong);

      return {
        id: `docker-concept-${Date.now()}`,
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
        topic: 'Docker',
        subtopic: 'Concepts',
        type: 'multiple-choice',
      };
    },
  },
  // Docker commands
  {
    pattern: 'docker_commands',
    type: 'multiple-choice',
    difficulty: 'intermediate',
    generate: () => {
      const commands = [
        {
          cmd: 'docker run',
          description: 'create and start a new container',
        },
        {
          cmd: 'docker ps',
          description: 'list running containers',
        },
        {
          cmd: 'docker stop',
          description: 'stop a running container',
        },
        {
          cmd: 'docker rm',
          description: 'remove a container',
        },
      ];
      const selected = randomItem(commands);

      const question = `What does "docker ${selected.cmd.split(' ')[1]}" do?`;

      const wrongOptions = commands.filter(c => c.cmd !== selected.cmd).map(c => c.description).slice(0, 3);
      const options = {
        A: selected.description,
        B: wrongOptions[0],
        C: wrongOptions[1],
        D: wrongOptions[2],
      };

      return {
        id: `docker-cmd-${Date.now()}`,
        question,
        options,
        correctAnswer: 'A',
        explanation: `${selected.cmd}: ${selected.description}`,
        difficulty: 'intermediate',
        topic: 'Docker',
        subtopic: 'Commands',
        type: 'multiple-choice',
      };
    },
  },
];

// ============================================================================
// TOPIC: TypeScript
// ============================================================================

const typescriptBasicsTemplates: QuestionTemplate[] = [
  // Types
  {
    pattern: 'typescript_types',
    type: 'multiple-choice',
    difficulty: 'beginner',
    generate: () => {
      const types = [
        { name: 'string', example: 'let name: string = "John";' },
        { name: 'number', example: 'let age: number = 25;' },
        { name: 'boolean', example: 'let isActive: boolean = true;' },
        { name: 'array', example: 'let items: number[] = [1, 2, 3];' },
        { name: 'any', example: 'let data: any = "could be anything";' },
      ];
      const selected = randomItem(types);

      const question = `Which TypeScript type is shown in: ${selected.example}`;

      const wrongOptions = types.filter(t => t.name !== selected.name).map(t => t.name).slice(0, 3);
      const options = {
        A: selected.name,
        B: wrongOptions[0],
        C: wrongOptions[1],
        D: wrongOptions[2] || 'unknown',
      };

      return {
        id: `ts-type-${Date.now()}`,
        question,
        options,
        correctAnswer: 'A',
        explanation: `${selected.name} is a basic TypeScript type.`,
        difficulty: 'beginner',
        topic: 'TypeScript',
        subtopic: 'Types',
        type: 'multiple-choice',
      };
    },
  },
  // Interfaces
  {
    pattern: 'interfaces',
    type: 'multiple-choice',
    difficulty: 'intermediate',
    generate: () => {
      const questions = [
        {
          q: 'What keyword defines an interface in TypeScript?',
          correct: 'interface',
          wrong: ['type', 'class', 'schema'],
        },
        {
          q: 'Can optional properties be defined in TypeScript interfaces?',
          correct: 'Yes, using the ? operator',
          wrong: ['No', 'Yes, using the * operator', 'Only in classes'],
        },
        {
          q: 'How do you make interface properties readonly?',
          correct: 'Use the readonly keyword',
          wrong: ['Use const', 'Use final', 'Use static'],
        },
      ];

      const selected = randomItem(questions);
      const wrongOptions = shuffleArray(selected.wrong);

      return {
        id: `ts-interface-${Date.now()}`,
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
        topic: 'TypeScript',
        subtopic: 'Interfaces',
        type: 'multiple-choice',
      };
    },
  },
];

// ============================================================================
// TOPIC: Node.js
// ============================================================================

const nodejsBasicsTemplates: QuestionTemplate[] = [
  // Core concepts
  {
    pattern: 'nodejs_concepts',
    type: 'multiple-choice',
    difficulty: 'beginner',
    generate: () => {
      const questions = [
        {
          q: 'What is Node.js built on?',
          correct: 'V8 JavaScript engine',
          wrong: ['SpiderMonkey', 'JavaScriptCore', 'Chakra'],
        },
        {
          q: 'What is npm?',
          correct: 'Node Package Manager',
          wrong: ['Node Process Manager', 'New Project Mode', 'Node Program Module'],
        },
        {
          q: 'What is the entry point file in a Node.js application?',
          correct: 'index.js (or configured in package.json)',
          wrong: ['main.js', 'app.js', 'start.js'],
        },
      ];

      const selected = randomItem(questions);
      const wrongOptions = shuffleArray(selected.wrong);

      return {
        id: `nodejs-concept-${Date.now()}`,
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
        topic: 'Node.js',
        subtopic: 'Core Concepts',
        type: 'multiple-choice',
      };
    },
  },
  // Modules
  {
    pattern: 'modules',
    type: 'multiple-choice',
    difficulty: 'intermediate',
    generate: () => {
      const questions = [
        {
          q: 'How do you export a function in Node.js?',
          correct: 'module.exports = function',
          wrong: ['export function', 'exports.default function', 'module.function'],
        },
        {
          q: 'How do you import a module in Node.js?',
          correct: 'require("./module")',
          wrong: ['import "./module"', 'include "./module"', 'using "./module"'],
        },
      ];

      const selected = randomItem(questions);
      const wrongOptions = shuffleArray(selected.wrong);

      return {
        id: `nodejs-module-${Date.now()}`,
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
        topic: 'Node.js',
        subtopic: 'Modules',
        type: 'multiple-choice',
      };
    },
  },
];

// ============================================================================
// TOPIC: Testing
// ============================================================================

const testingBasicsTemplates: QuestionTemplate[] = [
  // Testing concepts
  {
    pattern: 'testing_concepts',
    type: 'multiple-choice',
    difficulty: 'beginner',
    generate: () => {
      const testingTypes = [
        {
          type: 'Unit Testing',
          description: 'testing individual units of code in isolation',
        },
        {
          type: 'Integration Testing',
          description: 'testing how different parts work together',
        },
        {
          type: 'End-to-End Testing',
          description: 'testing the entire application flow',
        },
      ];
      const selected = randomItem(testingTypes);

      const question = `What is ${selected.type}?`;

      const wrongOptions = testingTypes.filter(t => t.type !== selected.type).map(t => t.description);
      const options = {
        A: selected.description,
        B: wrongOptions[0],
        C: wrongOptions[1],
        D: 'testing without errors',
      };

      return {
        id: `test-concept-${Date.now()}`,
        question,
        options,
        correctAnswer: 'A',
        explanation: `${selected.type}: ${selected.description}`,
        difficulty: 'beginner',
        topic: 'Testing',
        subtopic: 'Concepts',
        type: 'multiple-choice',
      };
    },
  },
  // Jest/Testing frameworks
  {
    pattern: 'jest',
    type: 'multiple-choice',
    difficulty: 'intermediate',
    generate: () => {
      const questions = [
        {
          q: 'What does describe() do in Jest?',
          correct: 'Groups related tests',
          wrong: ['Runs a test', 'Tests async code', 'Mocks functions'],
        },
        {
          q: 'What assertion does Jest use?',
          correct: 'expect()',
          wrong: ['assert()', 'should()', 'check()'],
        },
        {
          q: 'How do you test for equality in Jest?',
          correct: 'expect(value).toBe(expected)',
          wrong: ['assert(value === expected)', 'check(value, expected)', 'verify(value).is(expected)'],
        },
      ];

      const selected = randomItem(questions);
      const wrongOptions = shuffleArray(selected.wrong);

      return {
        id: `test-jest-${Date.now()}`,
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
        topic: 'Testing',
        subtopic: 'Jest',
        type: 'multiple-choice',
      };
    },
  },
];

// ============================================================================
// TOPIC: Data Structures
// ============================================================================

const dataStructuresTemplates: QuestionTemplate[] = [
  // Arrays vs Linked Lists
  {
    pattern: 'arrays_vs_linkedlists',
    type: 'multiple-choice',
    difficulty: 'beginner',
    generate: () => {
      const questions = [
        {
          q: 'What is the main advantage of arrays over linked lists?',
          correct: 'O(1) random access by index',
          wrong: ['Dynamic size', 'Easy insertion/deletion', 'Less memory'],
        },
        {
          q: 'What is the main advantage of linked lists over arrays?',
          correct: 'Efficient insertion/deletion',
          wrong: ['Random access', 'Less memory', 'Better cache locality'],
        },
        {
          q: 'What data type uses nodes with pointers?',
          correct: 'Linked List',
          wrong: ['Array', 'Stack', 'Queue'],
        },
      ];

      const selected = randomItem(questions);
      const wrongOptions = shuffleArray(selected.wrong);

      return {
        id: `ds-basic-${Date.now()}`,
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
        topic: 'Data Structures',
        subtopic: 'Basics',
        type: 'multiple-choice',
      };
    },
  },
  // Stacks and Queues
  {
    pattern: 'stacks_queues',
    type: 'multiple-choice',
    difficulty: 'intermediate',
    generate: () => {
      const structures = [
        {
          name: 'Stack',
          principle: 'LIFO (Last In, First Out)',
          example: 'Browser history back button',
        },
        {
          name: 'Queue',
          principle: 'FIFO (First In, First Out)',
          example: 'Print job spooler',
        },
      ];
      const selected = randomItem(structures);

      const question = `Which data structure follows ${selected.principle}?`;

      const wrongOptions = structures.filter(s => s.name !== selected.name).map(s => s.principle);
      const options = {
        A: selected.name,
        B: wrongOptions[0],
        C: wrongOptions[1],
        D: 'LILO (Last In, Last Out)',
      };

      return {
        id: `ds-stackqueue-${Date.now()}`,
        question,
        options,
        correctAnswer: 'A',
        explanation: `${selected.name} follows ${selected.principle}. Example: ${selected.example}`,
        difficulty: 'intermediate',
        topic: 'Data Structures',
        subtopic: 'Stacks/Queues',
        type: 'multiple-choice',
      };
    },
  },
];

// ============================================================================
// TOPIC: Algorithms
// ============================================================================

const algorithmsTemplates: QuestionTemplate[] = [
  // Sorting algorithms
  {
    pattern: 'sorting',
    type: 'multiple-choice',
    difficulty: 'intermediate',
    generate: () => {
      const algorithms = [
        {
          name: 'Bubble Sort',
          complexity: 'O(n²)',
          description: 'repeatedly swaps adjacent elements',
        },
        {
          name: 'Quick Sort',
          complexity: 'O(n log n) average',
          description: 'uses divide and conquer with pivot',
        },
        {
          name: 'Merge Sort',
          complexity: 'O(n log n)',
          description: 'divides array and merges sorted halves',
        },
      ];
      const selected = randomItem(algorithms);

      const question = `Which sorting algorithm has time complexity of ${selected.complexity} and ${selected.description}?`;

      const wrongOptions = algorithms.filter(a => a.name !== selected.name).map(a => a.name);
      const options = {
        A: selected.name,
        B: randomItem(wrongOptions),
        C: wrongOptions.find((_, i) => i !== wrongOptions.indexOf(randomItem(wrongOptions))) || wrongOptions[0],
        D: 'Selection Sort',
      };

      return {
        id: `algo-sort-${Date.now()}`,
        question,
        options,
        correctAnswer: 'A',
        explanation: `${selected.name}: ${selected.complexity}, ${selected.description}`,
        difficulty: 'intermediate',
        topic: 'Algorithms',
        subtopic: 'Sorting',
        type: 'multiple-choice',
      };
    },
  },
  // Searching algorithms
  {
    pattern: 'searching',
    type: 'multiple-choice',
    difficulty: 'beginner',
    generate: () => {
      const num = randomInt(50, 100);

      const question = `In a sorted array of ${num} elements, what is the maximum number of comparisons needed for binary search?`;

      const comparisons = Math.ceil(Math.log2(num)) + 1;
      const wrongOptions = [
        num.toString(),
        Math.ceil(num / 2).toString(),
        Math.ceil(Math.sqrt(num)).toString(),
      ];

      return {
        id: `algo-search-${Date.now()}`,
        question,
        options: {
          A: `${comparisons}`,
          B: wrongOptions[0],
          C: wrongOptions[1],
          D: wrongOptions[2],
        },
        correctAnswer: 'A',
        explanation: `Binary search has O(log n) complexity. For ${num} elements: ⌈log₂(${num})⌉ + 1 = ${comparisons} comparisons maximum.`,
        difficulty: 'beginner',
        topic: 'Algorithms',
        subtopic: 'Searching',
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
    icon: 'python',
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
    icon: 'react',
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
    icon: 'api',
    subtopics: [
      {
        id: 'api-basics',
        name: 'HTTP Methods',
        templates: apiBasicsTemplates,
      },
    ],
  },
  {
    id: 'sql',
    name: 'SQL',
    icon: 'sql',
    subtopics: [
      {
        id: 'sql-queries',
        name: 'Queries',
        templates: sqlBasicsTemplates,
      },
    ],
  },
  {
    id: 'git',
    name: 'Git',
    icon: 'git',
    subtopics: [
      {
        id: 'git-commands',
        name: 'Commands',
        templates: gitBasicsTemplates,
      },
    ],
  },
  {
    id: 'docker',
    name: 'Docker',
    icon: 'docker',
    subtopics: [
      {
        id: 'docker-concepts',
        name: 'Concepts',
        templates: dockerBasicsTemplates,
      },
    ],
  },
  {
    id: 'typescript',
    name: 'TypeScript',
    icon: 'typescript',
    subtopics: [
      {
        id: 'ts-types',
        name: 'Types',
        templates: typescriptBasicsTemplates,
      },
    ],
  },
  {
    id: 'nodejs',
    name: 'Node.js',
    icon: 'nodejs',
    subtopics: [
      {
        id: 'nodejs-concepts',
        name: 'Core Concepts',
        templates: nodejsBasicsTemplates,
      },
    ],
  },
  {
    id: 'testing',
    name: 'Testing',
    icon: 'testing',
    subtopics: [
      {
        id: 'test-concepts',
        name: 'Concepts',
        templates: testingBasicsTemplates,
      },
    ],
  },
  {
    id: 'data-structures',
    name: 'Data Structures',
    icon: 'data-structures',
    subtopics: [
      {
        id: 'ds-basics',
        name: 'Basics',
        templates: dataStructuresTemplates,
      },
    ],
  },
  {
    id: 'algorithms',
    name: 'Algorithms',
    icon: 'algorithms',
    subtopics: [
      {
        id: 'algo-sorting',
        name: 'Sorting & Searching',
        templates: algorithmsTemplates,
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
