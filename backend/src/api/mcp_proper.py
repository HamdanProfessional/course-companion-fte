"""
Proper MCP Server implementation following OpenAI Apps SDK research
Completely compliant with: https://developers.openai.com/apps-sdk/build/mcp-server

Response Structure:
- structuredContent: Concise JSON for both model and widget
- content: Human-readable narration for model
- _meta: Large/sensitive data for widget only
"""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import json
import logging
import httpx
import re
from src.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["MCP"])

# Backend API URL for tool execution
BACKEND_API_URL = "http://localhost:3505"

# Widget HTML content embedded directly
CHAPTER_LIST_WIDGET = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Course Chapters</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            line-height: 1.5;
            color: #1a1a1a;
            background: #f9fafb;
            padding: 16px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 2px solid #e5e7eb;
        }
        h2 { font-size: 18px; font-weight: 600; color: #111827; }
        .count { font-size: 12px; font-weight: 500; color: #6b7280; background: #f3f4f6; padding: 4px 8px; border-radius: 12px; }
        .chapters { display: flex; flex-direction: column; gap: 12px; }
        .chapter-card {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px;
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .chapter-card:hover {
            border-color: #3b82f6;
            box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
            transform: translateY(-1px);
        }
        .chapter-number {
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
            font-weight: 600;
            font-size: 14px;
            flex-shrink: 0;
        }
        .chapter-info { flex: 1; min-width: 0; }
        .chapter-info h3 {
            font-size: 14px;
            font-weight: 500;
            color: #111827;
            margin-bottom: 4px;
        }
        .meta { display: flex; gap: 8px; align-items: center; }
        .difficulty {
            font-size: 10px;
            font-weight: 600;
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            text-transform: uppercase;
        }
        .difficulty-BEGINNER { background: #10b981; }
        .difficulty-INTERMEDIATE { background: #f59e0b; }
        .duration { font-size: 11px; color: #6b7280; }
        .arrow { font-size: 18px; color: #9ca3af; }
        .chapter-card:hover .arrow { transform: translateX(4px); color: #3b82f6; }
    </style>
</head>
<body>
    <div id="app">
        <div class="header">
            <h2>📚 Course Chapters</h2>
            <span class="count">Loading...</span>
        </div>
        <div class="chapters"></div>
    </div>
    <script>
        const toolOutput = window.openai?.toolOutput;
        const chaptersContainer = document.querySelector('.chapters');
        const countElement = document.querySelector('.count');

        if (toolOutput && Array.isArray(toolOutput)) {
            const chapters = toolOutput;
            countElement.textContent = `${chapters.length} chapters`;

            chapters.forEach((chapter, index) => {
                const card = document.createElement('div');
                card.className = 'chapter-card';
                card.innerHTML = `
                    <div class="chapter-number">${index + 1}</div>
                    <div class="chapter-info">
                        <h3>${chapter.title}</h3>
                        <div class="meta">
                            <span class="difficulty difficulty-${chapter.difficulty_level}">${chapter.difficulty_level}</span>
                            <span class="duration">⏱️ ${chapter.estimated_time} min</span>
                        </div>
                    </div>
                    <div class="arrow">→</div>
                `;
                card.addEventListener('click', () => {
                    window.openai.callTool('get_chapter', { chapter_id: chapter.id });
                    window.openai.requestLayout('fullscreen');
                });
                chaptersContainer.appendChild(card);
            });
        }
    </script>
</body>
</html>"""

QUIZ_WIDGET = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quiz</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            line-height: 1.5;
            color: #1a1a1a;
            background: #f9fafb;
            padding: 16px;
        }
        .header { margin-bottom: 20px; }
        .title {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        h2 { font-size: 18px; font-weight: 600; color: #111827; }
        .difficulty {
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            padding: 4px 8px;
            border-radius: 12px;
        }
        .difficulty-BEGINNER { background: #d1fae5; color: #065f46; }
        .difficulty-INTERMEDIATE { background: #fef3c7; color: #92400e; }
        .difficulty-ADVANCED { background: #fee2e2; color: #991b1b; }
        .progress {
            position: relative;
            height: 8px;
            background: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
        }
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
        }
        .progress-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 11px;
            font-weight: 600;
            color: #374151;
        }
        .question-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 20px;
        }
        .question-header { margin-bottom: 16px; }
        .question-number {
            font-size: 12px;
            font-weight: 600;
            color: #6b7280;
            text-transform: uppercase;
        }
        .question-text {
            font-size: 16px;
            font-weight: 500;
            color: #111827;
            margin-bottom: 20px;
        }
        .options { display: flex; flex-direction: column; gap: 10px; }
        .option {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px 16px;
            background: #f9fafb;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .option:hover { border-color: #667eea; background: #f5f3ff; }
        .option.selected { border-color: #667eea; background: #ede9fe; }
        .option-key {
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #e5e7eb;
            border-radius: 6px;
            font-weight: 600;
            font-size: 13px;
        }
        .option.selected .option-key { background: #667eea; color: white; }
        .option-value { flex: 1; font-size: 14px; color: #374151; }
        .navigation {
            display: flex;
            gap: 10px;
            justify-content: space-between;
            margin-top: 20px;
        }
        .nav-btn, .submit-btn {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .nav-btn { background: #f3f4f6; color: #374151; }
        .nav-btn:hover:not(:disabled) { background: #e5e7eb; }
        .nav-btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .submit-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .submit-btn:hover:not(:disabled) {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        .submit-btn:disabled { opacity: 0.7; cursor: not-allowed; }
        .explanation-box {
            margin-top: 16px;
            padding: 12px;
            background: #eff6ff;
            border: 1px solid #bfdbfe;
            border-radius: 8px;
            font-size: 13px;
            color: #1e40af;
        }
        .results { text-align: center; padding: 20px; }
        .score-circle {
            width: 120px;
            height: 120px;
            margin: 0 auto 20px;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .score-circle.passed {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
        }
        .score-circle.failed {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            color: white;
        }
        .score { font-size: 36px; font-weight: 700; }
        .label { font-size: 12px; font-weight: 500; }
    </style>
</head>
<body>
    <div id="app">
        <div class="header">
            <div class="title">
                <h2 id="quiz-title">Loading quiz...</h2>
                <span id="difficulty" class="difficulty"></span>
            </div>
            <div class="progress">
                <div class="progress-bar" id="progress-bar"></div>
                <span class="progress-text" id="progress-text">1 / 1</span>
            </div>
        </div>

        <div id="quiz-container"></div>
    </div>
    <script>
        let currentQuestion = 0;
        let quiz = null;
        let selectedAnswers = {};
        let submitted = false;

        const toolOutput = window.openai?.toolOutput;
        const container = document.getElementById('quiz-container');

        if (toolOutput?.questions) {
            quiz = toolOutput;
            document.getElementById('quiz-title').textContent = quiz.title;
            document.getElementById('difficulty').textContent = quiz.difficulty;
            document.getElementById('difficulty').className = `difficulty difficulty-${quiz.difficulty}`;
            renderQuestion();
        }

        function renderQuestion() {
            if (!quiz) return;

            const question = quiz.questions[currentQuestion];
            const progress = ((currentQuestion + 1) / quiz.questions.length) * 100;

            document.getElementById('progress-bar').style.width = `${progress}%`;
            document.getElementById('progress-text').textContent = `${currentQuestion + 1} / ${quiz.questions.length}`;

            container.innerHTML = `
                <div class="question-card">
                    <div class="question-header">
                        <span class="question-number">Question ${currentQuestion + 1}</span>
                    </div>
                    <h3 class="question-text">${question.question_text}</h3>
                    <div class="options">
                        ${Object.entries(question.options).map(([key, value]) => `
                            <button class="option ${selectedAnswers[currentQuestion] === key ? 'selected' : ''}"
                                    onclick="selectAnswer('${key}')" ${submitted ? 'disabled' : ''}>
                                <span class="option-key">${key}</span>
                                <span class="option-value">${value}</span>
                            </button>
                        `).join('')}
                    </div>
                    <div class="navigation">
                        <button class="nav-btn" onclick="prevQuestion()" ${currentQuestion === 0 || submitted ? 'disabled' : ''}>← Previous</button>
                        ${currentQuestion === quiz.questions.length - 1 ? `
                            <button class="submit-btn" onclick="submitQuiz()" ${Object.keys(selectedAnswers).length < quiz.questions.length || submitted ? 'disabled' : ''}>
                                ${submitted ? 'Submitted ✓' : 'Submit Quiz'}
                            </button>
                        ` : `
                            <button class="nav-btn" onclick="nextQuestion()">Next →</button>
                        `}
                    </div>
                </div>
            `;
        }

        function selectAnswer(option) {
            if (submitted) return;
            selectedAnswers[currentQuestion] = option;
            renderQuestion();
        }

        function nextQuestion() {
            if (currentQuestion < quiz.questions.length - 1) {
                currentQuestion++;
                renderQuestion();
            }
        }

        function prevQuestion() {
            if (currentQuestion > 0) {
                currentQuestion--;
                renderQuestion();
            }
        }

        async function submitQuiz() {
            if (Object.keys(selectedAnswers).length < quiz.questions.length) return;

            submitted = true;
            const correctCount = Object.values(selectedAnswers).filter(a => a === 'A').length;
            const percentage = Math.round((correctCount / quiz.questions.length) * 100);

            container.innerHTML = `
                <div class="results">
                    <div class="score-circle ${percentage >= 70 ? 'passed' : 'failed'}">
                        <div class="score">${percentage}%</div>
                        <div class="label">${percentage >= 70 ? 'Passed!' : 'Keep practicing'}</div>
                    </div>
                    <h2>Quiz Complete!</h2>
                    <p style="color: #6b7280;">You got ${correctCount} out of ${quiz.questions.length} questions correct.</p>
                </div>
            `;

            window.openai.sendFollowUpMessage(`Quiz completed! Score: ${correctCount}/${quiz.questions.length} correct.`);
        }
    </script>
</body>
</html>"""

ACHIEVEMENTS_WIDGET = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Achievements</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            line-height: 1.5;
            color: #1a1a1a;
            background: #f9fafb;
            padding: 16px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid #e5e7eb;
        }
        h2 { font-size: 18px; font-weight: 600; color: #111827; }
        .stats {
            display: flex;
            gap: 16px;
            font-size: 12px;
            color: #6b7280;
        }
        .stat { display: flex; align-items: center; gap: 4px; }
        .achievements-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 12px;
        }
        .achievement-card {
            padding: 16px;
            background: #ffffff;
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            text-align: center;
            transition: all 0.2s ease;
            cursor: default;
        }
        .achievement-card.unlocked {
            border-color: #fbbf24;
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            box-shadow: 0 2px 8px rgba(251, 191, 36, 0.2);
        }
        .achievement-card.locked {
            opacity: 0.6;
            filter: grayscale(0.5);
        }
        .icon { font-size: 32px; margin-bottom: 8px; }
        .achievement-name {
            font-size: 11px;
            font-weight: 600;
            color: #111827;
            margin-bottom: 4px;
        }
        .achievement-description {
            font-size: 10px;
            color: #6b7280;
            line-height: 1.3;
        }
        .rarity {
            display: inline-block;
            margin-top: 6px;
            font-size: 9px;
            font-weight: 600;
            text-transform: uppercase;
            padding: 2px 6px;
            border-radius: 4px;
        }
        .rarity.common { background: #d1d5db; color: #374151; }
        .rarity.rare { background: #bfdbfe; color: #1e40af; }
        .rarity.epic { background: #c4b5fd; color: #5b21b6; }
        .rarity.legendary { background: #fde047; color: #854d0e; }
        .progress-bar {
            height: 4px;
            background: #e5e7eb;
            border-radius: 2px;
            margin-top: 8px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
        }
        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: #9ca3af;
        }
    </style>
</head>
<body>
    <div id="app">
        <div class="header">
            <h2>🏆 Achievements</h2>
            <div class="stats">
                <div class="stat">
                    <span id="unlocked-count">0</span>
                    <span>/</span>
                    <span id="total-count">0</span>
                    <span>Unlocked</span>
                </div>
            </div>
        </div>
        <div class="achievements-grid" id="achievements-grid"></div>
    </div>
    <script>
        const toolOutput = window.openai?.toolOutput;
        const grid = document.getElementById('achievements-grid');
        const unlockedCount = document.getElementById('unlocked-count');
        const totalCount = document.getElementById('total-count');

        if (toolOutput && Array.isArray(toolOutput)) {
            const achievements = toolOutput;
            const unlocked = achievements.filter(a => a.unlocked_at);

            totalCount.textContent = achievements.length;
            unlockedCount.textContent = unlocked.length;

            if (achievements.length === 0) {
                grid.innerHTML = `
                    <div class="empty-state" style="grid-column: 1/-1;">
                        <p>No achievements available</p>
                    </div>
                `;
                return;
            }

            achievements.forEach(achievement => {
                const card = document.createElement('div');
                const isUnlocked = achievement.unlocked_at !== null;
                card.className = `achievement-card ${isUnlocked ? 'unlocked' : 'locked'}`;

                card.innerHTML = `
                    <div class="icon">${achievement.icon}</div>
                    <div class="achievement-name">${achievement.name}</div>
                    <div class="achievement-description">${achievement.description}</div>
                    <span class="rarity ${achievement.rarity}">${achievement.rarity}</span>
                    ${!isUnlocked && achievement.progress > 0 ? `
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${achievement.progress}%"></div>
                        </div>
                    ` : ''}
                `;

                grid.appendChild(card);
            });
        }
    </script>
</body>
</html>"""

STREAK_CALENDAR_WIDGET = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Streak Calendar</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            line-height: 1.5;
            color: #1a1a1a;
            background: #f9fafb;
            padding: 16px;
        }
        .header { margin-bottom: 20px; }
        .title-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }
        h2 { font-size: 18px; font-weight: 600; color: #111827; }
        .month-nav {
            display: flex;
            gap: 8px;
            align-items: center;
        }
        .month-nav button {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            padding: 6px 12px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
            transition: all 0.2s;
        }
        .month-nav button:hover {
            border-color: #3b82f6;
            color: #3b82f6;
        }
        .stats-row {
            display: flex;
            gap: 16px;
            margin-bottom: 16px;
        }
        .stat-card {
            flex: 1;
            padding: 12px;
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value {
            font-size: 24px;
            font-weight: 700;
            color: #f59e0b;
        }
        .stat-label {
            font-size: 11px;
            font-weight: 500;
            color: #6b7280;
            text-transform: uppercase;
        }
        .calendar {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 16px;
        }
        .weekdays {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 4px;
            margin-bottom: 8px;
        }
        .weekday {
            text-align: center;
            font-size: 10px;
            font-weight: 600;
            color: #9ca3af;
            text-transform: uppercase;
            padding: 8px 0;
        }
        .days {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 4px;
        }
        .day {
            aspect-ratio: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
            cursor: default;
            transition: all 0.2s;
        }
        .day.inactive {
            color: #d1d5db;
        }
        .day.active {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
            box-shadow: 0 2px 4px rgba(245, 158, 11, 0.3);
        }
        .day.today {
            border: 2px solid #3b82f6;
        }
        .day.streak-day {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        }
    </style>
</head>
<body>
    <div id="app">
        <div class="header">
            <div class="title-row">
                <h2>🔥 Streak Calendar</h2>
                <div class="month-nav">
                    <button onclick="changeMonth(-1)">←</button>
                    <span id="month-label"></span>
                    <button onclick="changeMonth(1)">→</button>
                </div>
            </div>
            <div class="stats-row">
                <div class="stat-card">
                    <div class="stat-value" id="current-streak">0</div>
                    <div class="stat-label">Current Streak</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="longest-streak">0</div>
                    <div class="stat-label">Longest Streak</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="active-days">0</div>
                    <div class="stat-label">Active Days</div>
                </div>
            </div>
        </div>
        <div class="calendar">
            <div class="weekdays">
                <div class="weekday">Sun</div>
                <div class="weekday">Mon</div>
                <div class="weekday">Tue</div>
                <div class="weekday">Wed</div>
                <div class="weekday">Thu</div>
                <div class="weekday">Fri</div>
                <div class="weekday">Sat</div>
            </div>
            <div class="days" id="calendar-days"></div>
        </div>
    </div>
    <script>
        const toolOutput = window.openai?.toolOutput;
        let currentMonth = new Date().getMonth();
        let currentYear = new Date().getFullYear();

        function renderCalendar() {
            const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                              'July', 'August', 'September', 'October', 'November', 'December'];
            document.getElementById('month-label').textContent = `${monthNames[currentMonth]} ${currentYear}`;

            const firstDay = new Date(currentYear, currentMonth, 1).getDay();
            const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
            const today = new Date();

            const daysContainer = document.getElementById('calendar-days');
            daysContainer.innerHTML = '';

            // Empty cells for days before first of month
            for (let i = 0; i < firstDay; i++) {
                const emptyDay = document.createElement('div');
                emptyDay.className = 'day inactive';
                daysContainer.appendChild(emptyDay);
            }

            // Days of month
            if (toolOutput && toolOutput.days) {
                const activeDates = new Set(
                    toolOutput.days
                        .filter(d => d.active)
                        .map(d => new Date(d.date).toDateString())
                );

                for (let day = 1; day <= daysInMonth; day++) {
                    const dayEl = document.createElement('div');
                    const date = new Date(currentYear, currentMonth, day);
                    const isToday = date.toDateString() === today.toDateString();
                    const isActive = activeDates.has(date.toDateString());

                    dayEl.className = 'day';
                    dayEl.textContent = day;

                    if (isActive) {
                        dayEl.classList.add('active', 'streak-day');
                    }
                    if (isToday) {
                        dayEl.classList.add('today');
                    }

                    daysContainer.appendChild(dayEl);
                }
            }

            // Update stats
            if (toolOutput) {
                document.getElementById('current-streak').textContent = toolOutput.current_streak || 0;
                document.getElementById('longest-streak').textContent = toolOutput.longest_streak || 0;
                document.getElementById('active-days').textContent = toolOutput.total_active_days || 0;
            }
        }

        function changeMonth(delta) {
            currentMonth += delta;
            if (currentMonth > 11) {
                currentMonth = 0;
                currentYear++;
            } else if (currentMonth < 0) {
                currentMonth = 11;
                currentYear--;
            }
            renderCalendar();
        }

        renderCalendar();
    </script>
</body>
</html>"""

PROGRESS_DASHBOARD_WIDGET = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Progress Dashboard</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            line-height: 1.5;
            color: #1a1a1a;
            background: #f9fafb;
            padding: 16px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid #e5e7eb;
        }
        h2 { font-size: 18px; font-weight: 600; color: #111827; }
        .overview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        .overview-card {
            padding: 20px;
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            text-align: center;
            transition: all 0.2s;
        }
        .overview-card:hover {
            border-color: #3b82f6;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
        }
        .icon { font-size: 32px; margin-bottom: 8px; }
        .value {
            font-size: 28px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 4px;
        }
        .label {
            font-size: 12px;
            font-weight: 500;
            color: #6b7280;
            text-transform: uppercase;
        }
        .progress-section { margin-bottom: 24px; }
        .section-title {
            font-size: 14px;
            font-weight: 600;
            color: #111827;
            margin-bottom: 12px;
        }
        .progress-bar-container {
            padding: 20px;
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
        }
        .circular-progress {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 24px;
        }
        .circular-chart {
            width: 120px;
            height: 120px;
        }
        .circle-bg {
            fill: none;
            stroke: #e5e7eb;
            stroke-width: 3;
        }
        .circle {
            fill: none;
            stroke: url(#gradient);
            stroke-width: 3;
            stroke-linecap: round;
            transition: stroke-dashoffset 0.5s ease;
        }
        .percentage {
            font-size: 28px;
            font-weight: 700;
            color: #111827;
        }
        .chapters-list {
            margin-top: 16px;
        }
        .chapter-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px;
            background: #f9fafb;
            border-radius: 8px;
            margin-bottom: 8px;
        }
        .chapter-item.completed { background: #ecfdf5; }
        .checkbox {
            width: 20px;
            height: 20px;
            border: 2px solid #d1d5db;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
        }
        .chapter-item.completed .checkbox {
            background: #10b981;
            border-color: #10b981;
            color: white;
        }
        .chapter-name {
            flex: 1;
            font-size: 13px;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div id="app">
        <div class="header">
            <h2>📊 Progress Dashboard</h2>
        </div>

        <div class="overview-grid">
            <div class="overview-card">
                <div class="icon">📖</div>
                <div class="value" id="completion-pct">0%</div>
                <div class="label">Completion</div>
            </div>
            <div class="overview-card">
                <div class="icon">✅</div>
                <div class="value" id="completed-count">0</div>
                <div class="label">Chapters Done</div>
            </div>
            <div class="overview-card">
                <div class="icon">✏️</div>
                <div class="value" id="quiz-count">0</div>
                <div class="label">Quizzes Taken</div>
            </div>
            <div class="overview-card">
                <div class="icon">🔥</div>
                <div class="value" id="streak-count">0</div>
                <div class="label">Day Streak</div>
            </div>
        </div>

        <div class="progress-section">
            <div class="section-title">Course Progress</div>
            <div class="progress-bar-container">
                <svg class="circular-progress" viewBox="0 0 36 36">
                    <defs>
                        <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" style="stop-color:#667eea"/>
                            <stop offset="100%" style="stop-color:#764ba2"/>
                        </linearGradient>
                    </defs>
                    <path class="circle-bg"
                          d="M18 2.0845
                             a 15.9155 15.9155 0 0 1 0 31.831
                             a 15.9155 15.9155 0 0 1 0 -31.831"/>
                    <path class="circle" id="progress-circle"
                          stroke-dasharray="0, 100"
                          d="M18 2.0845
                             a 15.9155 15.9155 0 0 1 0 31.831
                             a 15.9155 15.9155 0 0 1 0 -31.831"/>
                </svg>
                <div class="percentage" id="percentage-display">0%</div>
            </div>
        </div>

        <div class="progress-section">
            <div class="section-title">Chapters</div>
            <div class="chapters-list" id="chapters-list"></div>
        </div>
    </div>
    <script>
        const toolOutput = window.openai?.toolOutput;

        if (toolOutput) {
            // Update overview cards
            document.getElementById('completion-pct').textContent =
                Math.round(toolOutput.completion_percentage) + '%';
            document.getElementById('completed-count').textContent =
                (toolOutput.completed_chapters || []).length;
            document.getElementById('quiz-count').textContent =
                toolOutput.total_quizzes_taken || 0;
            document.getElementById('streak-count').textContent =
                toolOutput.current_streak || 0;

            // Update circular progress
            const percentage = toolOutput.completion_percentage || 0;
            document.getElementById('progress-circle').setAttribute(
                'stroke-dasharray', `${percentage}, 100`
            );
            document.getElementById('percentage-display').textContent = Math.round(percentage) + '%';

            // Render chapters list
            const chaptersList = document.getElementById('chapters-list');
            const completedIds = new Set(toolOutput.completed_chapters || []);

            if (toolOutput.chapters && Array.isArray(toolOutput.chapters)) {
                toolOutput.chapters.forEach(chapter => {
                    const isCompleted = completedIds.has(chapter.id);
                    const item = document.createElement('div');
                    item.className = `chapter-item ${isCompleted ? 'completed' : ''}`;
                    item.innerHTML = `
                        <div class="checkbox">${isCompleted ? '✓' : ''}</div>
                        <div class="chapter-name">${chapter.title}</div>
                    `;
                    chaptersList.appendChild(item);
                });
            }
        }
    </script>
</body>
</html>"""

QUIZ_INSIGHTS_WIDGET = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quiz Insights</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            line-height: 1.5;
            color: #1a1a1a;
            background: #f9fafb;
            padding: 16px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid #e5e7eb;
        }
        h2 { font-size: 18px; font-weight: 600; color: #111827; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 12px;
            margin-bottom: 20px;
        }
        .stat-card {
            padding: 16px;
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value {
            font-size: 24px;
            font-weight: 700;
            color: #111827;
        }
        .stat-label {
            font-size: 11px;
            font-weight: 500;
            color: #6b7280;
            text-transform: uppercase;
        }
        .chart-container {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .chart-title {
            font-size: 14px;
            font-weight: 600;
            color: #111827;
            margin-bottom: 16px;
        }
        .score-bars {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .score-bar {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .quiz-name {
            flex: 1;
            font-size: 12px;
            font-weight: 500;
            color: #374151;
            min-width: 120px;
        }
        .bar-container {
            flex: 2;
            height: 24px;
            background: #f3f4f6;
            border-radius: 4px;
            overflow: hidden;
        }
        .bar-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 8px;
            font-size: 11px;
            font-weight: 600;
            color: white;
        }
        .bar-fill.passed { background: linear-gradient(90deg, #10b981 0%, #059669 100%); }
        .bar-fill.failed { background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%); }
        .history-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .history-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            background: #f9fafb;
            border-radius: 6px;
        }
        .history-info {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        .quiz-title { font-size: 13px; font-weight: 500; color: #111827; }
        .quiz-date { font-size: 11px; color: #6b7280; }
        .score-badge {
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        }
        .score-badge.passed { background: #d1fae5; color: #065f46; }
        .score-badge.failed { background: #fee2e2; color: #991b1b; }
    </style>
</head>
<body>
    <div id="app">
        <div class="header">
            <h2>📈 Quiz Insights</h2>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="total-quizzes">0</div>
                <div class="stat-label">Total Quizzes</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="avg-score">0%</div>
                <div class="stat-label">Average Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="pass-rate">0%</div>
                <div class="stat-label">Pass Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="best-score">0%</div>
                <div class="stat-label">Best Score</div>
            </div>
        </div>

        <div class="chart-container">
            <div class="chart-title">Recent Quiz Scores</div>
            <div class="score-bars" id="score-bars"></div>
        </div>

        <div class="chart-container">
            <div class="chart-title">Quiz History</div>
            <div class="history-list" id="history-list"></div>
        </div>
    </div>
    <script>
        const toolOutput = window.openai?.toolOutput;

        if (toolOutput && Array.isArray(toolOutput)) {
            const history = toolOutput;

            // Calculate stats
            const totalQuizzes = history.length;
            const avgScore = totalQuizzes > 0
                ? Math.round(history.reduce((sum, h) => sum + h.score, 0) / totalQuizzes)
                : 0;
            const passCount = history.filter(h => h.passed).length;
            const passRate = totalQuizzes > 0 ? Math.round((passCount / totalQuizzes) * 100) : 0;
            const bestScore = totalQuizzes > 0 ? Math.max(...history.map(h => h.score)) : 0;

            document.getElementById('total-quizzes').textContent = totalQuizzes;
            document.getElementById('avg-score').textContent = avgScore + '%';
            document.getElementById('pass-rate').textContent = passRate + '%';
            document.getElementById('best-score').textContent = bestScore + '%';

            // Render score bars
            const scoreBars = document.getElementById('score-bars');
            history.slice(0, 5).forEach(attempt => {
                const bar = document.createElement('div');
                bar.className = 'score-bar';
                bar.innerHTML = `
                    <div class="quiz-name">${attempt.quiz_title}</div>
                    <div class="bar-container">
                        <div class="bar-fill ${attempt.passed ? 'passed' : 'failed'}"
                             style="width: ${attempt.score}%">
                            ${attempt.score}%
                        </div>
                    </div>
                `;
                scoreBars.appendChild(bar);
            });

            // Render history list
            const historyList = document.getElementById('history-list');
            history.forEach(attempt => {
                const item = document.createElement('div');
                item.className = 'history-item';
                const date = new Date(attempt.date).toLocaleDateString();
                item.innerHTML = `
                    <div class="history-info">
                        <div class="quiz-title">${attempt.quiz_title}</div>
                        <div class="quiz-date">${date}</div>
                    </div>
                    <div class="score-badge ${attempt.passed ? 'passed' : 'failed'}">
                        ${attempt.score}%
                    </div>
                `;
                historyList.appendChild(item);
            });
        }
    </script>
</body>
</html>"""

ADAPTIVE_LEARNING_WIDGET = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Adaptive Learning</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            line-height: 1.5;
            color: #1a1a1a;
            background: #f9fafb;
            padding: 16px;
        }
        .header {
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid #e5e7eb;
        }
        .header-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        h2 { font-size: 18px; font-weight: 600; color: #111827; }
        .badge {
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            padding: 4px 8px;
            border-radius: 4px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .subtitle {
            font-size: 12px;
            color: #6b7280;
        }
        .section {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
        }
        .section-title {
            font-size: 14px;
            font-weight: 600;
            color: #111827;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .gaps-grid {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .gap-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px;
            background: #fef3c7;
            border: 1px solid #fcd34d;
            border-radius: 8px;
        }
        .gap-icon { font-size: 20px; }
        .gap-info { flex: 1; }
        .gap-topic {
            font-size: 13px;
            font-weight: 600;
            color: #92400e;
        }
        .gap-desc {
            font-size: 11px;
            color: #b45309;
        }
        .recommendations-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .recommendation-card {
            padding: 12px;
            background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%);
            border: 1px solid #c4b5fd;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .recommendation-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(139, 92, 246, 0.2);
        }
        .rec-title {
            font-size: 13px;
            font-weight: 600;
            color: #5b21b6;
            margin-bottom: 4px;
        }
        .rec-reason {
            font-size: 11px;
            color: #7c3aed;
        }
        .action-btn {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .action-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        .premium-lock {
            text-align: center;
            padding: 20px;
            background: #f9fafb;
            border-radius: 8px;
        }
        .lock-icon { font-size: 32px; margin-bottom: 8px; }
        .lock-text {
            font-size: 12px;
            color: #6b7280;
            margin-bottom: 12px;
        }
    </style>
</head>
<body>
    <div id="app">
        <div class="header">
            <div class="header-row">
                <h2>🎯 Adaptive Learning</h2>
                <span class="badge">Premium</span>
            </div>
            <div class="subtitle">Personalized recommendations based on your performance</div>
        </div>

        <div class="section">
            <div class="section-title">
                <span>⚠️</span>
                <span>Knowledge Gaps</span>
            </div>
            <div class="gaps-grid" id="gaps-grid">
                <div class="premium-lock">
                    <div class="lock-icon">🔒</div>
                    <div class="lock-text">Upgrade to Premium to see your knowledge gaps</div>
                    <button class="action-btn" onclick="upgradePremium()">Upgrade Now</button>
                </div>
            </div>
        </div>

        <div class="section">
            <div class="section-title">
                <span>💡</span>
                <span>Recommended Next Steps</span>
            </div>
            <div class="recommendations-list" id="recommendations-list">
                <div class="premium-lock">
                    <div class="lock-icon">🔒</div>
                    <div class="lock-text">Upgrade to Premium for personalized recommendations</div>
                    <button class="action-btn" onclick="upgradePremium()">Upgrade Now</button>
                </div>
            </div>
        </div>
    </div>
    <script>
        const toolOutput = window.openai?.toolOutput;

        function upgradePremium() {
            window.openai.sendFollowUpMessage('I\\'d like to upgrade to Premium to access adaptive learning features.');
        }

        if (toolOutput) {
            // Render knowledge gaps
            const gapsGrid = document.getElementById('gaps-grid');
            if (toolOutput.gaps && Array.isArray(toolOutput.gaps) && toolOutput.gaps.length > 0) {
                gapsGrid.innerHTML = '';
                toolOutput.gaps.forEach(gap => {
                    const item = document.createElement('div');
                    item.className = 'gap-item';
                    item.innerHTML = `
                        <div class="gap-icon">📚</div>
                        <div class="gap-info">
                            <div class="gap-topic">${gap.topic}</div>
                            <div class="gap-desc">${gap.description}</div>
                        </div>
                    `;
                    gapsGrid.appendChild(item);
                });
            }

            // Render recommendations
            const recList = document.getElementById('recommendations-list');
            if (toolOutput.recommendations && Array.isArray(toolOutput.recommendations) && toolOutput.recommendations.length > 0) {
                recList.innerHTML = '';
                toolOutput.recommendations.forEach(rec => {
                    const card = document.createElement('div');
                    card.className = 'recommendation-card';
                    card.innerHTML = `
                        <div class="rec-title">${rec.title}</div>
                        <div class="rec-reason">${rec.reason}</div>
                    `;
                    card.addEventListener('click', () => {
                        if (rec.action) {
                            window.openai.callTool(rec.action.tool, rec.action.params);
                        }
                    });
                    recList.appendChild(card);
                });
            }
        }
    </script>
</body>
</html>"""

AI_MENTOR_CHAT_WIDGET = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Mentor</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            line-height: 1.5;
            color: #1a1a1a;
            background: #f9fafb;
            padding: 16px;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 12px;
            border-bottom: 2px solid #e5e7eb;
            margin-bottom: 16px;
            flex-shrink: 0;
        }
        .header-left { display: flex; align-items: center; gap: 12px; }
        .avatar {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }
        h2 { font-size: 16px; font-weight: 600; color: #111827; }
        .status {
            font-size: 11px;
            color: #10b981;
            font-weight: 500;
        }
        .badge {
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            padding: 4px 8px;
            border-radius: 4px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .messages-container {
            flex: 1;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-bottom: 16px;
            padding-right: 8px;
        }
        .message {
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 12px;
            font-size: 13px;
            line-height: 1.4;
        }
        .message.user {
            align-self: flex-end;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom-right-radius: 4px;
        }
        .message.mentor {
            align-self: flex-start;
            background: #ffffff;
            border: 1px solid #e5e7eb;
            color: #1a1a1a;
            border-bottom-left-radius: 4px;
        }
        .input-container {
            display: flex;
            gap: 8px;
            flex-shrink: 0;
        }
        .input-field {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
            outline: none;
            transition: border-color 0.2s;
        }
        .input-field:focus {
            border-color: #667eea;
        }
        .send-btn {
            padding: 12px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .send-btn:hover:not(:disabled) {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        .send-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .quick-prompts {
            display: flex;
            gap: 8px;
            margin-bottom: 12px;
            flex-wrap: wrap;
        }
        .prompt-btn {
            padding: 6px 12px;
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }
        .prompt-btn:hover {
            border-color: #667eea;
            color: #667eea;
        }
        .welcome-message {
            text-align: center;
            padding: 40px 20px;
            color: #6b7280;
        }
        .welcome-icon { font-size: 48px; margin-bottom: 12px; }
        .welcome-text {
            font-size: 14px;
            margin-bottom: 8px;
        }
        .welcome-subtext {
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div id="app">
        <div class="header">
            <div class="header-left">
                <div class="avatar">🤖</div>
                <div>
                    <h2>AI Mentor</h2>
                    <div class="status">● Online</div>
                </div>
            </div>
            <span class="badge">Premium</span>
        </div>

        <div class="quick-prompts">
            <button class="prompt-btn" onclick="sendQuickPrompt('Explain this concept')">
                Explain Concept
            </button>
            <button class="prompt-btn" onclick="sendQuickPrompt('Give me a practice problem')">
                Practice Problem
            </button>
            <button class="prompt-btn" onclick="sendQuickPrompt('Create a study plan')">
                Study Plan
            </button>
        </div>

        <div class="messages-container" id="messages">
            <div class="welcome-message">
                <div class="welcome-icon">👋</div>
                <div class="welcome-text">Hi! I'm your AI Mentor</div>
                <div class="welcome-subtext">Ask me anything about your course</div>
            </div>
        </div>

        <div class="input-container">
            <input
                type="text"
                class="input-field"
                id="message-input"
                placeholder="Ask your mentor anything..."
                onkeypress="handleKeyPress(event)"
            />
            <button class="send-btn" id="send-btn" onclick="sendMessage()">Send</button>
        </div>
    </div>
    <script>
        const toolOutput = window.openai?.toolOutput;
        const messagesContainer = document.getElementById('messages');
        const inputField = document.getElementById('message-input');
        const sendBtn = document.getElementById('send-btn');

        function addMessage(text, type) {
            const message = document.createElement('div');
            message.className = `message ${type}`;
            message.textContent = text;
            messagesContainer.appendChild(message);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        function sendQuickPrompt(text) {
            inputField.value = text;
            sendMessage();
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        function sendMessage() {
            const text = inputField.value.trim();
            if (!text) return;

            // Remove welcome message
            const welcome = messagesContainer.querySelector('.welcome-message');
            if (welcome) welcome.remove();

            // Add user message
            addMessage(text, 'user');
            inputField.value = '';
            sendBtn.disabled = true;

            // Send to AI mentor via ChatGPT
            window.openai.sendFollowUpMessage(text);

            // Simulate mentor response (in real widget, would call ask_mentor tool)
            setTimeout(() => {
                addMessage('Thanks for your question! Let me help you with that...', 'mentor');
                sendBtn.disabled = false;
            }, 1000);
        }

        // If chat history provided, render it
        if (toolOutput && toolOutput.messages && Array.isArray(toolOutput.messages)) {
            const welcome = messagesContainer.querySelector('.welcome-message');
            if (welcome) welcome.remove();

            toolOutput.messages.forEach(msg => {
                addMessage(msg.text, msg.role);
            });
        }

        inputField.focus();
    </script>
</body>
</html>"""

# =============================================================================
# Helper Functions
# =============================================================================

def create_jsonrpc_response(result: any, req_id: any) -> dict:
    """Create a JSON-RPC 2.0 success response."""
    return {
        "jsonrpc": "2.0",
        "result": result,
        "id": req_id
    }

def create_jsonrpc_error(code: int, message: str, req_id: any) -> dict:
    """Create a JSON-RPC 2.0 error response."""
    return {
        "jsonrpc": "2.0",
        "error": {
            "code": code,
            "message": message
        },
        "id": req_id
    }

# =============================================================================
# Main MCP Endpoints
# =============================================================================

@router.get("/mcp")
async def mcp_info():
    """Health check endpoint for MCP server."""
    return {
        "status": "healthy",
        "service": "Course Companion FTE MCP Server",
        "version": "1.0.0",
        "protocol": "jsonrpc-2.0",
        "endpoints": {
            "mcp": "/mcp (POST for JSON-RPC)"
        }
    }

@router.post("/mcp")
async def mcp_endpoint(request: Request):
    """
    Main MCP endpoint for JSON-RPC 2.0 requests.
    Handles: initialize, tools/list, tools/call, resources/list, resources/read
    """
    try:
        data = await request.json()
        method = data.get("method")
        params = data.get("params", {})
        req_id = data.get("id")

        logger.info(f"MCP Request: {method} (id={req_id})")

        # =====================================================================
        # Initialize
        # =====================================================================
        if method == "initialize":
            return JSONResponse(content=create_jsonrpc_response({
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "Course Companion FTE",
                    "version": "1.0.0"
                },
                "capabilities": {
                    "tools": {},
                    "resources": {}
                }
            }, req_id))

        # =====================================================================
        # Tools List
        # =====================================================================
        elif method == "tools/list":
            return JSONResponse(content=create_jsonrpc_response({
                "tools": [
                    {
                        "name": "list_chapters",
                        "description": "List all available chapters in the course",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        },
                        "annotations": {
                            "readOnlyHint": True,
                            "openWorldHint": False,
                            "destructiveHint": False
                        }
                    },
                    {
                        "name": "get_chapter",
                        "description": "Get detailed chapter content including text and metadata",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "chapter_id": {
                                    "type": "string",
                                    "description": "Chapter ID"
                                }
                            },
                            "required": ["chapter_id"]
                        },
                        "annotations": {
                            "readOnlyHint": True,
                            "openWorldHint": False,
                            "destructiveHint": False
                        }
                    },
                    {
                        "name": "search_content",
                        "description": "Search course content for specific topics",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Search query"
                                }
                            },
                            "required": ["query"]
                        },
                        "annotations": {
                            "readOnlyHint": True,
                            "openWorldHint": False,
                            "destructiveHint": False
                        }
                    },
                    {
                        "name": "get_quiz",
                        "description": "Get quiz questions for a specific quiz",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "quiz_id": {
                                    "type": "string",
                                    "description": "Quiz ID"
                                }
                            },
                            "required": ["quiz_id"]
                        },
                        "annotations": {
                            "readOnlyHint": True,
                            "openWorldHint": False,
                            "destructiveHint": False
                        }
                    },
                    {
                        "name": "submit_quiz",
                        "description": "Submit quiz answers for grading",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "quiz_id": {"type": "string"},
                                "answers": {"type": "object"}
                            },
                            "required": ["quiz_id", "answers"]
                        },
                        "annotations": {
                            "readOnlyHint": False,
                            "openWorldHint": False,
                            "destructiveHint": False
                        }
                    },
                    {
                        "name": "get_progress",
                        "description": "Get user's learning progress and completion stats",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string"}
                            },
                            "required": ["user_id"]
                        },
                        "annotations": {
                            "readOnlyHint": True,
                            "openWorldHint": False,
                            "destructiveHint": False
                        }
                    },
                    {
                        "name": "update_progress",
                        "description": "Mark a chapter as complete and update progress",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string"},
                                "chapter_id": {"type": "string"}
                            },
                            "required": ["user_id", "chapter_id"]
                        },
                        "annotations": {
                            "readOnlyHint": False,
                            "openWorldHint": False,
                            "destructiveHint": False
                        }
                    },
                    # ==================== PHASE 1: CORE TOOLS (8 tools) ====================
                    {
                        "name": "get_streak",
                        "description": "Get user's current streak and longest streak",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User ID"}
                            },
                            "required": ["user_id"]
                        },
                        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "record_checkin",
                        "description": "Record daily checkin to maintain streak",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User ID"}
                            },
                            "required": ["user_id"]
                        },
                        "annotations": {"readOnlyHint": False, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "list_quizzes",
                        "description": "List all available quizzes",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        },
                        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "get_quiz_history",
                        "description": "Get user's quiz attempt history",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "quiz_id": {"type": "string", "description": "Quiz ID"},
                                "user_id": {"type": "string", "description": "User ID"},
                                "limit": {"type": "number", "description": "Max results (default 10)"}
                            },
                            "required": ["quiz_id", "user_id"]
                        },
                        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "get_next_chapter",
                        "description": "Get next chapter in sequence",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "chapter_id": {"type": "string", "description": "Current chapter ID"}
                            },
                            "required": ["chapter_id"]
                        },
                        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "get_previous_chapter",
                        "description": "Get previous chapter in sequence",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "chapter_id": {"type": "string", "description": "Current chapter ID"}
                            },
                            "required": ["chapter_id"]
                        },
                        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "check_access",
                        "description": "Check if user can access premium content",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User ID"},
                                "resource": {"type": "string", "description": "Resource to check (e.g., 'chapter-4')"}
                            },
                            "required": ["user_id", "resource"]
                        },
                        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "get_user_tier",
                        "description": "Get user's subscription tier (FREE/PREMIUM/PRO)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User ID"}
                            },
                            "required": ["user_id"]
                        },
                        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False}
                    },
                    # ==================== PHASE 2: LLM TOOLS (12 tools) ====================
                    {
                        "name": "get_knowledge_gaps",
                        "description": "Analyze user's weak topics (Premium feature)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User ID"}
                            },
                            "required": ["user_id"]
                        },
                        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "get_recommendations",
                        "description": "Get personalized chapter recommendations (Premium feature)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User ID"}
                            },
                            "required": ["user_id"]
                        },
                        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "generate_learning_path",
                        "description": "Generate custom learning path (Premium feature)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User ID"},
                                "learning_goals": {"type": "array", "items": {"type": "string"}, "description": "Learning goals"},
                                "available_time_hours": {"type": "number", "description": "Available time in hours"}
                            },
                            "required": ["user_id", "learning_goals", "available_time_hours"]
                        },
                        "annotations": {"readOnlyHint": False, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "ask_mentor",
                        "description": "Ask AI tutor a question (Premium feature)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User ID"},
                                "question": {"type": "string", "description": "Question to ask"},
                                "context": {"type": "object", "description": "Optional context (current chapter, quiz scores)"}
                            },
                            "required": ["user_id", "question"]
                        },
                        "annotations": {"readOnlyHint": False, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "get_study_guidance",
                        "description": "Get personalized study plan (Premium feature)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User ID"}
                            },
                            "required": ["user_id"]
                        },
                        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "generate_practice_problems",
                        "description": "Generate practice problems for a topic (Premium feature)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User ID"},
                                "topic": {"type": "string", "description": "Topic to practice"},
                                "difficulty": {"type": "string", "enum": ["beginner", "intermediate", "advanced"], "description": "Difficulty level"},
                                "count": {"type": "number", "description": "Number of problems (default 3)"}
                            },
                            "required": ["user_id", "topic"]
                        },
                        "annotations": {"readOnlyHint": False, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "submit_quiz_llm",
                        "description": "Submit quiz for AI grading with detailed feedback (Premium feature)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User ID"},
                                "quiz_id": {"type": "string", "description": "Quiz ID"},
                                "answers": {"type": "object", "description": "Answers to quiz questions"}
                            },
                            "required": ["user_id", "quiz_id", "answers"]
                        },
                        "annotations": {"readOnlyHint": False, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "get_quiz_insights",
                        "description": "Get quiz performance insights and trends (Premium feature)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User ID"},
                                "quiz_id": {"type": "string", "description": "Quiz ID"}
                            },
                            "required": ["user_id", "quiz_id"]
                        },
                        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "get_user_costs",
                        "description": "Get LLM usage costs for user (PRO feature)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User ID"},
                                "days": {"type": "number", "description": "Number of days (default 30)"}
                            },
                            "required": ["user_id"]
                        },
                        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "get_total_costs",
                        "description": "Get total LLM costs across all users (PRO feature)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "days": {"type": "number", "description": "Number of days (default 30)"}
                            },
                            "required": []
                        },
                        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "get_top_cost_users",
                        "description": "Get users with highest LLM costs (PRO feature)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "days": {"type": "number", "description": "Number of days (default 30)"},
                                "limit": {"type": "number", "description": "Max results (default 10)"}
                            },
                            "required": []
                        },
                        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False}
                    },
                    # ==================== PHASE 3: ENHANCED TOOLS (13 tools) ====================
                    {
                        "name": "get_chapter_summary",
                        "description": "Get AI-generated chapter summary",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "chapter_id": {"type": "string", "description": "Chapter ID"},
                                "user_id": {"type": "string", "description": "User ID (optional, for personalization)"}
                            },
                            "required": ["chapter_id"]
                        },
                        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "get_navigation_context",
                        "description": "Get previous/next chapter with completion status",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "chapter_id": {"type": "string", "description": "Current chapter ID"},
                                "user_id": {"type": "string", "description": "User ID"}
                            },
                            "required": ["chapter_id", "user_id"]
                        },
                        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "get_continue_learning",
                        "description": "Get suggested next content based on progress",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User ID"}
                            },
                            "required": ["user_id"]
                        },
                        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "get_quiz_by_chapter",
                        "description": "Get quiz for a specific chapter",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "chapter_id": {"type": "string", "description": "Chapter ID"},
                                "user_id": {"type": "string", "description": "User ID (optional)"}
                            },
                            "required": ["chapter_id"]
                        },
                        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "submit_quiz_hybrid",
                        "description": "Submit quiz with hybrid auto+LLM grading (Premium feature)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User ID"},
                                "quiz_id": {"type": "string", "description": "Quiz ID"},
                                "answers": {"type": "object", "description": "Answers to quiz questions"},
                                "grading_mode": {"type": "string", "enum": ["auto", "llm", "hybrid"], "description": "Grading mode (default: hybrid)"}
                            },
                            "required": ["user_id", "quiz_id", "answers"]
                        },
                        "annotations": {"readOnlyHint": False, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "get_quiz_attempt_history",
                        "description": "Get detailed quiz attempt history",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User ID"},
                                "quiz_id": {"type": "string", "description": "Quiz ID"},
                                "limit": {"type": "number", "description": "Max results (default 30)"}
                            },
                            "required": ["user_id", "quiz_id"]
                        },
                        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "get_progress_summary",
                        "description": "Get comprehensive progress summary with achievements",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User ID"}
                            },
                            "required": ["user_id"]
                        },
                        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "get_chapter_progress",
                        "description": "Get progress for each chapter",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User ID"}
                            },
                            "required": ["user_id"]
                        },
                        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "get_achievements",
                        "description": "Get user's achievements and badges",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User ID"}
                            },
                            "required": ["user_id"]
                        },
                        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "get_quiz_score_history",
                        "description": "Get quiz score trend over time",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User ID"},
                                "limit": {"type": "number", "description": "Max results (default 30)"}
                            },
                            "required": ["user_id"]
                        },
                        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "explain_content",
                        "description": "Get AI explanation of specific topic",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "chapter_id": {"type": "string", "description": "Chapter ID"},
                                "topic": {"type": "string", "description": "Topic to explain"},
                                "complexity_level": {"type": "string", "enum": ["beginner", "intermediate", "advanced"], "description": "Explanation depth"}
                            },
                            "required": ["chapter_id", "topic"]
                        },
                        "annotations": {"readOnlyHint": False, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "chat_with_mentor",
                        "description": "Interactive chat with AI mentor (Premium feature)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User ID"},
                                "question": {"type": "string", "description": "Question or message"},
                                "chapter_context": {"type": "string", "description": "Optional chapter context"},
                                "conversation_history": {"type": "array", "items": {"type": "object"}, "description": "Previous messages"}
                            },
                            "required": ["user_id", "question"]
                        },
                        "annotations": {"readOnlyHint": False, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "list_plans",
                        "description": "List available subscription plans",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        },
                        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "get_subscription_info",
                        "description": "Get user's subscription details",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User ID"}
                            },
                            "required": ["user_id"]
                        },
                        "annotations": {"readOnlyHint": True, "openWorldHint": False, "destructiveHint": False}
                    },
                    {
                        "name": "export_user_data",
                        "description": "Export user data (GDPR compliance)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "User ID"},
                                "include_progress": {"type": "boolean", "description": "Include progress data"},
                                "include_quiz_history": {"type": "boolean", "description": "Include quiz history"},
                                "format": {"type": "string", "enum": ["json", "csv", "pdf"], "description": "Export format"}
                            },
                            "required": ["user_id"]
                        },
                        "annotations": {"readOnlyHint": False, "openWorldHint": False, "destructiveHint": False}
                    }
                ]
            }, req_id))

        # =====================================================================
        # Resources List - Register Widget Templates
        # =====================================================================
        elif method == "resources/list":
            # Register widget HTML files as MCP resources
            return JSONResponse(content=create_jsonrpc_response({
                "resources": [
                    {
                        "uri": "ui://widget/chapter-list.html",
                        "name": "Chapter List Widget",
                        "description": "Interactive list of course chapters",
                        "mimeType": "text/html+skybridge"
                    },
                    {
                        "uri": "ui://widget/quiz.html",
                        "name": "Quiz Widget",
                        "description": "Interactive quiz with multiple choice questions",
                        "mimeType": "text/html+skybridge"
                    },
                    {
                        "uri": "ui://widget/achievements.html",
                        "name": "Achievements Widget",
                        "description": "Display user achievements and badges with gamification",
                        "mimeType": "text/html+skybridge"
                    },
                    {
                        "uri": "ui://widget/streak-calendar.html",
                        "name": "Streak Calendar Widget",
                        "description": "Visual calendar of checkin history",
                        "mimeType": "text/html+skybridge"
                    },
                    {
                        "uri": "ui://widget/progress-dashboard.html",
                        "name": "Progress Dashboard Widget",
                        "description": "Comprehensive progress overview with stats",
                        "mimeType": "text/html+skybridge"
                    },
                    {
                        "uri": "ui://widget/quiz-insights.html",
                        "name": "Quiz Insights Widget",
                        "description": "Quiz performance analytics and trends",
                        "mimeType": "text/html+skybridge"
                    },
                    {
                        "uri": "ui://widget/adaptive-learning.html",
                        "name": "Adaptive Learning Widget",
                        "description": "Personalized recommendations and knowledge gaps",
                        "mimeType": "text/html+skybridge"
                    },
                    {
                        "uri": "ui://widget/ai-mentor-chat.html",
                        "name": "AI Mentor Chat Widget",
                        "description": "Interactive Q&A interface with AI tutor",
                        "mimeType": "text/html+skybridge"
                    }
                ]
            }, req_id))

        # =====================================================================
        # Resources Read - Serve Widget HTML Content
        # =====================================================================
        elif method == "resources/read":
            uri = params.get("uri")

            if not uri:
                return JSONResponse(
                    content=create_jsonrpc_error(-32602, "Missing URI parameter", req_id),
                    status_code=400
                )

            # Return embedded widget HTML
            if uri == "ui://widget/chapter-list.html":
                html_content = CHAPTER_LIST_WIDGET
            elif uri == "ui://widget/quiz.html":
                html_content = QUIZ_WIDGET
            elif uri == "ui://widget/achievements.html":
                html_content = ACHIEVEMENTS_WIDGET
            elif uri == "ui://widget/streak-calendar.html":
                html_content = STREAK_CALENDAR_WIDGET
            elif uri == "ui://widget/progress-dashboard.html":
                html_content = PROGRESS_DASHBOARD_WIDGET
            elif uri == "ui://widget/quiz-insights.html":
                html_content = QUIZ_INSIGHTS_WIDGET
            elif uri == "ui://widget/adaptive-learning.html":
                html_content = ADAPTIVE_LEARNING_WIDGET
            elif uri == "ui://widget/ai-mentor-chat.html":
                html_content = AI_MENTOR_CHAT_WIDGET
            else:
                return JSONResponse(
                    content=create_jsonrpc_error(-32602, f"Unknown resource URI: {uri}", req_id),
                    status_code=404
                )

            return JSONResponse(content=create_jsonrpc_response({
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "text/html+skybridge",
                        "text": html_content
                    }
                ]
            }, req_id))

        # =====================================================================
        # Tools Call - Execute Tools
        # =====================================================================
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            try:
                # Call the appropriate backend API endpoint
                async with httpx.AsyncClient() as client:
                    # list_chapters
                    if tool_name == "list_chapters":
                        response = await client.get(
                            f"{BACKEND_API_URL}/api/v1/chapters",
                            timeout=10.0
                        )
                        response.raise_for_status()
                        result = response.json()

                        # Return with proper structure: structuredContent + content + _meta
                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {
                                "chapters": result
                            },
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Found {len(result)} chapters in the course"
                                }
                            ],
                            "_meta": {
                                "openai/outputTemplate": "ui://widget/chapter-list.html",
                                "openai/widgetDomain": "https://sse.testservers.online",
                                "openai/widgetCSP": {
                                    "connect_domains": ["https://chatgpt.com"],
                                    "script_domains": ["https://sse.testservers.online"],
                                    "resource_domains": ["https://*.oaistatic.com"]
                                }
                            }
                        }, req_id))

                    # get_chapter
                    elif tool_name == "get_chapter":
                        chapter_id = arguments.get("chapter_id")
                        if not chapter_id:
                            raise ValueError("chapter_id is required")

                        response = await client.get(
                            f"{BACKEND_API_URL}/api/v1/chapters/{chapter_id}",
                            timeout=10.0
                        )
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {
                                "chapter": {
                                    "id": result.get("id"),
                                    "title": result.get("title"),
                                    "order": result.get("order"),
                                    "difficulty_level": result.get("difficulty_level"),
                                    "estimated_time": result.get("estimated_time")
                                }
                            },
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Chapter: {result.get('title')} ({result.get('difficulty_level')}, ~{result.get('estimated_time')} min)"
                                }
                            ]
                        }, req_id))

                    # search_content
                    elif tool_name == "search_content":
                        query = arguments.get("query")
                        if not query:
                            raise ValueError("query is required")

                        response = await client.get(
                            f"{BACKEND_API_URL}/api/v1/search",
                            params={"q": query},
                            timeout=10.0
                        )
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {
                                "results": result
                            },
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Found {len(result)} results for '{query}'"
                                }
                            ]
                        }, req_id))

                    # get_quiz
                    elif tool_name == "get_quiz":
                        quiz_id = arguments.get("quiz_id")
                        if not quiz_id:
                            raise ValueError("quiz_id is required")

                        response = await client.get(
                            f"{BACKEND_API_URL}/api/v1/quizzes/{quiz_id}",
                            timeout=10.0
                        )
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {
                                "quiz": {
                                    "id": result.get("id"),
                                    "title": result.get("title"),
                                    "difficulty": result.get("difficulty"),
                                    "question_count": len(result.get("questions", []))
                                }
                            },
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Quiz: {result.get('title')} ({result.get('difficulty')}, {len(result.get('questions', []))} questions)"
                                }
                            ],
                            "_meta": {
                                "openai/outputTemplate": "ui://widget/quiz.html",
                                "openai/widgetDomain": "https://sse.testservers.online",
                                "openai/widgetCSP": {
                                    "connect_domains": ["https://chatgpt.com"],
                                    "script_domains": ["https://sse.testservers.online"],
                                    "resource_domains": ["https://*.oaistatic.com"]
                                }
                            }
                        }, req_id))

                    # submit_quiz
                    elif tool_name == "submit_quiz":
                        quiz_id = arguments.get("quiz_id")
                        answers = arguments.get("answers")
                        if not quiz_id or not answers:
                            raise ValueError("quiz_id and answers are required")

                        response = await client.post(
                            f"{BACKEND_API_URL}/api/v1/quizzes/{quiz_id}/submit",
                            json={"answers": answers},
                            timeout=10.0
                        )
                        response.raise_for_status()
                        result = response.json()

                        score = result.get("score", 0)
                        total = result.get("total_questions", 0)

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {
                                "score": score,
                                "total": total,
                                "percentage": round((score / total) * 100) if total > 0 else 0
                            },
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Quiz submitted: {score}/{total} correct ({round((score / total) * 100) if total > 0 else 0}%)"
                                }
                            ]
                        }, req_id))

                    # get_progress
                    elif tool_name == "get_progress":
                        user_id = arguments.get("user_id")
                        if not user_id:
                            return JSONResponse(
                                content=create_jsonrpc_error(-32602, "user_id is required", req_id),
                                status_code=400
                            )

                        # Handle ChatGPT's "current_user" placeholder
                        # This is how ChatGPT represents the logged-in user
                        if user_id == "current_user":
                            # Use default user ID from manifest
                            default_user_id = "00000000-0000-0000-0000-000000000001"

                            try:
                                response = await client.get(
                                    f"{BACKEND_API_URL}/api/v1/progress/{default_user_id}",
                                    timeout=10.0
                                )

                                if response.status_code == 200:
                                    result = response.json()
                                    completed = result.get("completed_chapters", 0)
                                    total = result.get("total_chapters", 0)

                                    return JSONResponse(content=create_jsonrpc_response({
                                        "structuredContent": {
                                            "completed": completed,
                                            "total": total,
                                            "percentage": round((completed / total) * 100) if total > 0 else 0
                                        },
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": f"Progress: {completed}/{total} chapters completed ({round((completed / total) * 100) if total > 0 else 0}%)"
                                            }
                                        ]
                                    }, req_id))
                                else:
                                    # User doesn't exist in database yet, return default
                                    return JSONResponse(content=create_jsonrpc_response({
                                        "structuredContent": {
                                            "completed": 0,
                                            "total": 4,
                                            "percentage": 0
                                        },
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": "Progress: 0/4 chapters completed (0%)"
                                            }
                                        ]
                                    }, req_id))

                            except Exception as e:
                                logger.error(f"Error fetching progress for default user: {str(e)}")
                                # Return default progress on error
                                return JSONResponse(content=create_jsonrpc_response({
                                    "structuredContent": {
                                        "completed": 0,
                                        "total": 4,
                                        "percentage": 0
                                    },
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "Progress: 0/4 chapters completed (0%)"
                                        }
                                    ]
                                }, req_id))

                        # Validate UUID format for other user_ids
                        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
                        if not uuid_pattern.match(user_id):
                            return JSONResponse(
                                content=create_jsonrpc_error(-32602, f"Invalid user_id format: {user_id} (must be UUID)", req_id),
                                status_code=400
                            )

                        response = await client.get(
                            f"{BACKEND_API_URL}/api/v1/progress/{user_id}",
                            timeout=10.0
                        )
                        response.raise_for_status()
                        result = response.json()

                        completed = result.get("completed_chapters", 0)
                        total = result.get("total_chapters", 0)

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {
                                "completed": completed,
                                "total": total,
                                "percentage": round((completed / total) * 100) if total > 0 else 0
                            },
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Progress: {completed}/{total} chapters completed ({round((completed / total) * 100) if total > 0 else 0}%)"
                                }
                            ]
                        }, req_id))

                    # update_progress
                    elif tool_name == "update_progress":
                        user_id = arguments.get("user_id")
                        chapter_id = arguments.get("chapter_id")
                        if not user_id or not chapter_id:
                            return JSONResponse(
                                content=create_jsonrpc_error(-32602, "user_id and chapter_id are required", req_id),
                                status_code=400
                            )

                        # Handle ChatGPT's "current_user" placeholder
                        if user_id == "current_user":
                            # Use default user ID from manifest
                            user_id = "00000000-0000-0000-0000-000000000001"

                        response = await client.put(
                            f"{BACKEND_API_URL}/api/v1/progress/{user_id}",
                            json={"chapter_id": chapter_id},
                            timeout=10.0
                        )
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {
                                "chapter_id": chapter_id,
                                "marked_complete": True
                            },
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Marked chapter {chapter_id} as complete"
                                }
                            ]
                        }, req_id))

                    # ==================== PHASE 1: CORE TOOLS ====================
                    # get_streak
                    elif tool_name == "get_streak":
                        user_id = arguments.get("user_id")
                        if not user_id:
                            raise ValueError("user_id is required")

                        response = await client.get(f"{BACKEND_API_URL}/api/v1/streaks/{user_id}", timeout=10.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"streak": result},
                            "content": [{"type": "text", "text": f"Current streak: {result.get('current_streak')} days, Longest: {result.get('longest_streak')} days"}]
                        }, req_id))

                    # record_checkin
                    elif tool_name == "record_checkin":
                        user_id = arguments.get("user_id")
                        if not user_id:
                            raise ValueError("user_id is required")

                        response = await client.post(f"{BACKEND_API_URL}/api/v1/streaks/{user_id}/checkin", timeout=10.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"streak": result},
                            "content": [{"type": "text", "text": f"Checkin recorded! Current streak: {result.get('current_streak')} days"}]
                        }, req_id))

                    # list_quizzes
                    elif tool_name == "list_quizzes":
                        response = await client.get(f"{BACKEND_API_URL}/api/v1/quizzes", timeout=10.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"quizzes": result},
                            "content": [{"type": "text", "text": f"Found {len(result)} quizzes"}]
                        }, req_id))

                    # get_quiz_history
                    elif tool_name == "get_quiz_history":
                        quiz_id = arguments.get("quiz_id")
                        user_id = arguments.get("user_id")
                        limit = arguments.get("limit", 10)
                        if not quiz_id or not user_id:
                            raise ValueError("quiz_id and user_id are required")

                        response = await client.get(f"{BACKEND_API_URL}/api/v1/quizzes/{quiz_id}/results", params={"user_id": user_id, "limit": limit}, timeout=10.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"history": result},
                            "content": [{"type": "text", "text": f"Found {result.get('attempts', 0) if isinstance(result, dict) else len(result)} quiz attempts"}]
                        }, req_id))

                    # get_next_chapter
                    elif tool_name == "get_next_chapter":
                        chapter_id = arguments.get("chapter_id")
                        if not chapter_id:
                            raise ValueError("chapter_id is required")

                        response = await client.get(f"{BACKEND_API_URL}/api/v1/chapters/{chapter_id}/next", timeout=10.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"chapter": result},
                            "content": [{"type": "text", "text": f"Next: {result.get('title', 'No next chapter')}"}]
                        }, req_id))

                    # get_previous_chapter
                    elif tool_name == "get_previous_chapter":
                        chapter_id = arguments.get("chapter_id")
                        if not chapter_id:
                            raise ValueError("chapter_id is required")

                        response = await client.get(f"{BACKEND_API_URL}/api/v1/chapters/{chapter_id}/previous", timeout=10.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"chapter": result},
                            "content": [{"type": "text", "text": f"Previous: {result.get('title', 'No previous chapter')}"}]
                        }, req_id))

                    # check_access
                    elif tool_name == "check_access":
                        user_id = arguments.get("user_id")
                        resource = arguments.get("resource")
                        if not user_id or not resource:
                            raise ValueError("user_id and resource are required")

                        response = await client.post(f"{BACKEND_API_URL}/api/v1/access/check", json={"user_id": user_id, "resource": resource}, timeout=10.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"access": result},
                            "content": [{"type": "text", "text": f"Access: {'Granted' if result.get('access_granted') else 'Denied'} - {result.get('tier', 'UNKNOWN')}: {result.get('reason', '')}"}]
                        }, req_id))

                    # get_user_tier
                    elif tool_name == "get_user_tier":
                        user_id = arguments.get("user_id")
                        if not user_id:
                            raise ValueError("user_id is required")

                        response = await client.get(f"{BACKEND_API_URL}/api/v1/user/{user_id}/tier", timeout=10.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"tier": result},
                            "content": [{"type": "text", "text": f"User tier: {result.get('tier', 'UNKNOWN')}"}]
                        }, req_id))

                    # ==================== PHASE 2: LLM TOOLS ====================
                    # get_knowledge_gaps
                    elif tool_name == "get_knowledge_gaps":
                        user_id = arguments.get("user_id")
                        if not user_id:
                            raise ValueError("user_id is required")

                        response = await client.get(f"{BACKEND_API_URL}/api/v1/adaptive/analysis", params={"user_id": user_id}, timeout=30.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"gaps": result},
                            "content": [{"type": "text", "text": f"Knowledge gaps analyzed: {len(result.get('weak_topics', []))} weak topics identified"}]
                        }, req_id))

                    # get_recommendations
                    elif tool_name == "get_recommendations":
                        user_id = arguments.get("user_id")
                        if not user_id:
                            raise ValueError("user_id is required")

                        response = await client.get(f"{BACKEND_API_URL}/api/v1/adaptive/recommendations", params={"user_id": user_id}, timeout=30.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"recommendations": result},
                            "content": [{"type": "text", "text": f"Recommended: {result.get('next_chapter_id', 'No recommendation')} - {result.get('reason', '')}"}]
                        }, req_id))

                    # generate_learning_path
                    elif tool_name == "generate_learning_path":
                        user_id = arguments.get("user_id")
                        learning_goals = arguments.get("learning_goals")
                        available_time_hours = arguments.get("available_time_hours")
                        if not all([user_id, learning_goals, available_time_hours is not None]):
                            raise ValueError("user_id, learning_goals, and available_time_hours are required")

                        response = await client.post(f"{BACKEND_API_URL}/api/v1/adaptive/path", json={"user_id": user_id, "learning_goals": learning_goals, "available_time_hours": available_time_hours}, timeout=30.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"path": result},
                            "content": [{"type": "text", "text": f"Learning path generated: {result.get('total_hours', 0)} hours, {len(result.get('path', []))} milestones"}]
                        }, req_id))

                    # ask_mentor
                    elif tool_name == "ask_mentor":
                        user_id = arguments.get("user_id")
                        question = arguments.get("question")
                        context = arguments.get("context", {})
                        if not user_id or not question:
                            raise ValueError("user_id and question are required")

                        response = await client.post(f"{BACKEND_API_URL}/api/v1/mentor/ask", json={"user_id": user_id, "question": question, "context": context}, timeout=30.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"answer": result},
                            "content": [{"type": "text", "text": result.get("answer", "No answer available")}]
                        }, req_id))

                    # get_study_guidance
                    elif tool_name == "get_study_guidance":
                        user_id = arguments.get("user_id")
                        if not user_id:
                            raise ValueError("user_id is required")

                        response = await client.get(f"{BACKEND_API_URL}/api/v1/mentor/guidance", params={"user_id": user_id}, timeout=30.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"guidance": result},
                            "content": [{"type": "text", "text": f"Study guidance: {result.get('learning_pace', 'N/A')}, {len(result.get('strengths', []))} strengths, {len(result.get('areas_for_improvement', []))} areas to improve"}]
                        }, req_id))

                    # generate_practice_problems
                    elif tool_name == "generate_practice_problems":
                        user_id = arguments.get("user_id")
                        topic = arguments.get("topic")
                        difficulty = arguments.get("difficulty", "intermediate")
                        count = arguments.get("count", 3)
                        if not user_id or not topic:
                            raise ValueError("user_id and topic are required")

                        response = await client.post(f"{BACKEND_API_URL}/api/v1/mentor/practice-problems", json={"user_id": user_id, "topic": topic, "difficulty": difficulty, "count": count}, timeout=30.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"problems": result},
                            "content": [{"type": "text", "text": f"Generated {len(result.get('problems', []))} practice problems for {topic}"}]
                        }, req_id))

                    # submit_quiz_llm
                    elif tool_name == "submit_quiz_llm":
                        user_id = arguments.get("user_id")
                        quiz_id = arguments.get("quiz_id")
                        answers = arguments.get("answers")
                        if not all([user_id, quiz_id, answers]):
                            raise ValueError("user_id, quiz_id, and answers are required")

                        response = await client.post(f"{BACKEND_API_URL}/api/v1/quizzes/{quiz_id}/grade-llm", json={"user_id": user_id, "answers": answers}, timeout=30.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"result": result},
                            "content": [{"type": "text", "text": f"LLM graded: {result.get('score', 0)}% - {result.get('feedback', 'No feedback')}"}]
                        }, req_id))

                    # get_quiz_insights
                    elif tool_name == "get_quiz_insights":
                        user_id = arguments.get("user_id")
                        quiz_id = arguments.get("quiz_id")
                        if not user_id or not quiz_id:
                            raise ValueError("user_id and quiz_id are required")

                        response = await client.get(f"{BACKEND_API_URL}/api/v1/quizzes/{quiz_id}/insights", params={"user_id": user_id}, timeout=30.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"insights": result},
                            "content": [{"type": "text", "text": f"Quiz insights: {result.get('average_score', 0)}% avg, {len(result.get('strengths', []))} strengths, {len(result.get('focus_areas', []))} focus areas"}]
                        }, req_id))

                    # get_user_costs
                    elif tool_name == "get_user_costs":
                        user_id = arguments.get("user_id")
                        days = arguments.get("days", 30)
                        if not user_id:
                            raise ValueError("user_id is required")

                        response = await client.get(f"{BACKEND_API_URL}/api/v1/costs/{user_id}", params={"days": days}, timeout=10.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"costs": result},
                            "content": [{"type": "text", "text": f"User LLM costs: ${result.get('total_cost_usd', 0):.4f} over {days} days"}]
                        }, req_id))

                    # get_total_costs
                    elif tool_name == "get_total_costs":
                        days = arguments.get("days", 30)

                        response = await client.get(f"{BACKEND_API_URL}/api/v1/costs/summary/total", params={"days": days}, timeout=10.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"costs": result},
                            "content": [{"type": "text", "text": f"Total LLM costs: ${result.get('total_cost_usd', 0):.2f} across {result.get('unique_users', 0)} users"}]
                        }, req_id))

                    # get_top_cost_users
                    elif tool_name == "get_top_cost_users":
                        days = arguments.get("days", 30)
                        limit = arguments.get("limit", 10)

                        response = await client.get(f"{BACKEND_API_URL}/api/v1/costs/top-users", params={"days": days, "limit": limit}, timeout=10.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"top_users": result},
                            "content": [{"type": "text", "text": f"Top {len(result.get('top_users', []))} users by LLM cost over {days} days"}]
                        }, req_id))

                    # ==================== PHASE 3: ENHANCED TOOLS ====================
                    # get_chapter_summary
                    elif tool_name == "get_chapter_summary":
                        chapter_id = arguments.get("chapter_id")
                        user_id = arguments.get("user_id")
                        if not chapter_id:
                            raise ValueError("chapter_id is required")

                        params = {"chapter_id": chapter_id}
                        if user_id:
                            params["user_id"] = user_id

                        response = await client.get(f"{BACKEND_API_URL}/api/v3/tutor/content", params=params, timeout=10.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"summary": result},
                            "content": [{"type": "text", "text": result.get("summary", "Chapter content loaded")}]
                        }, req_id))

                    # get_navigation_context
                    elif tool_name == "get_navigation_context":
                        chapter_id = arguments.get("chapter_id")
                        user_id = arguments.get("user_id")
                        if not chapter_id or not user_id:
                            raise ValueError("chapter_id and user_id are required")

                        response = await client.get(f"{BACKEND_API_URL}/api/v3/tutor/content/navigation", params={"chapter_id": chapter_id, "user_id": user_id}, timeout=10.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"navigation": result},
                            "content": [{"type": "text", "text": f"Navigation: Previous: {result.get('previous', {}).get('title', 'None')}, Next: {result.get('next', {}).get('title', 'None')}, Can continue: {result.get('can_continue', False)}"}]
                        }, req_id))

                    # get_continue_learning
                    elif tool_name == "get_continue_learning":
                        user_id = arguments.get("user_id")
                        if not user_id:
                            raise ValueError("user_id is required")

                        response = await client.get(f"{BACKEND_API_URL}/api/v3/tutor/content/continue", params={"user_id": user_id}, timeout=10.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"continue": result},
                            "content": [{"type": "text", "text": f"Continue learning: {result.get('title', 'No suggestion')} - {result.get('reason', '')}"}]
                        }, req_id))

                    # get_quiz_by_chapter
                    elif tool_name == "get_quiz_by_chapter":
                        chapter_id = arguments.get("chapter_id")
                        user_id = arguments.get("user_id")
                        if not chapter_id:
                            raise ValueError("chapter_id is required")

                        params = {"chapter_id": chapter_id}
                        if user_id:
                            params["user_id"] = user_id

                        response = await client.get(f"{BACKEND_API_URL}/api/v3/tutor/quizzes/by-chapter/{chapter_id}", params=params, timeout=10.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"quiz": result},
                            "content": [{"type": "text", "text": f"Quiz for chapter {chapter_id}: {result.get('total_questions', 0)} questions"}]
                        }, req_id))

                    # submit_quiz_hybrid
                    elif tool_name == "submit_quiz_hybrid":
                        user_id = arguments.get("user_id")
                        quiz_id = arguments.get("quiz_id")
                        answers = arguments.get("answers")
                        grading_mode = arguments.get("grading_mode", "hybrid")
                        if not all([user_id, quiz_id, answers]):
                            raise ValueError("user_id, quiz_id, and answers are required")

                        response = await client.post(f"{BACKEND_API_URL}/api/v3/tutor/quizzes/{quiz_id}/submit", json={"user_id": user_id, "answers": answers, "grading_mode": grading_mode}, timeout=30.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"result": result},
                            "content": [{"type": "text", "text": f"Quiz submitted ({grading_mode} grading): {result.get('score', 0)}% - {result.get('summary', '')}"}]
                        }, req_id))

                    # get_quiz_attempt_history
                    elif tool_name == "get_quiz_attempt_history":
                        user_id = arguments.get("user_id")
                        quiz_id = arguments.get("quiz_id")
                        limit = arguments.get("limit", 30)
                        if not user_id or not quiz_id:
                            raise ValueError("user_id and quiz_id are required")

                        response = await client.get(f"{BACKEND_API_URL}/api/v3/tutor/quizzes/{quiz_id}/history", params={"user_id": user_id, "limit": limit}, timeout=10.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"history": result},
                            "content": [{"type": "text", "text": f"Found {len(result) if isinstance(result, list) else 0} quiz attempts"}]
                        }, req_id))

                    # get_progress_summary
                    elif tool_name == "get_progress_summary":
                        user_id = arguments.get("user_id")
                        if not user_id:
                            raise ValueError("user_id is required")

                        response = await client.get(f"{BACKEND_API_URL}/api/v3/tutor/progress/summary", params={"user_id": user_id}, timeout=10.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"summary": result},
                            "content": [{"type": "text", "text": f"Progress: {result.get('completion_percentage', 0)}% complete, {result.get('completed_chapters', 0)} chapters, {result.get('current_streak', 0)} day streak, {len(result.get('achievements', []))} achievements"}]
                        }, req_id))

                    # get_chapter_progress
                    elif tool_name == "get_chapter_progress":
                        user_id = arguments.get("user_id")
                        if not user_id:
                            raise ValueError("user_id is required")

                        response = await client.get(f"{BACKEND_API_URL}/api/v3/tutor/progress/chapters", params={"user_id": user_id}, timeout=10.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"progress": result},
                            "content": [{"type": "text", "text": f"Chapter progress for {len(result) if isinstance(result, list) else 0} chapters"}]
                        }, req_id))

                    # get_achievements
                    elif tool_name == "get_achievements":
                        user_id = arguments.get("user_id")
                        if not user_id:
                            raise ValueError("user_id is required")

                        response = await client.get(f"{BACKEND_API_URL}/api/v3/tutor/progress/achievements", params={"user_id": user_id}, timeout=10.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"achievements": result},
                            "content": [{"type": "text", "text": f"Unlocked {len(result) if isinstance(result, list) else 0} achievements"}]
                        }, req_id))

                    # get_quiz_score_history
                    elif tool_name == "get_quiz_score_history":
                        user_id = arguments.get("user_id")
                        limit = arguments.get("limit", 30)
                        if not user_id:
                            raise ValueError("user_id is required")

                        response = await client.get(f"{BACKEND_API_URL}/api/v3/tutor/progress/quiz-scores", params={"user_id": user_id, "limit": limit}, timeout=10.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"history": result},
                            "content": [{"type": "text", "text": f"Quiz score history: {len(result) if isinstance(result, list) else 0} attempts"}]
                        }, req_id))

                    # explain_content
                    elif tool_name == "explain_content":
                        chapter_id = arguments.get("chapter_id")
                        topic = arguments.get("topic")
                        complexity_level = arguments.get("complexity_level", "intermediate")
                        if not chapter_id or not topic:
                            raise ValueError("chapter_id and topic are required")

                        response = await client.post(f"{BACKEND_API_URL}/api/v3/tutor/ai/explain", json={"chapter_id": chapter_id, "topic": topic, "complexity_level": complexity_level}, timeout=30.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"explanation": result},
                            "content": [{"type": "text", "text": result.get("explanation", f"Explanation of {topic}")}]
                        }, req_id))

                    # chat_with_mentor
                    elif tool_name == "chat_with_mentor":
                        user_id = arguments.get("user_id")
                        question = arguments.get("question")
                        chapter_context = arguments.get("chapter_context")
                        conversation_history = arguments.get("conversation_history", [])
                        if not user_id or not question:
                            raise ValueError("user_id and question are required")

                        response = await client.post(f"{BACKEND_API_URL}/api/v3/tutor/ai/mentor/chat", json={"user_id": user_id, "question": question, "chapter_context": chapter_context, "conversation_history": conversation_history}, timeout=30.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"chat": result},
                            "content": [{"type": "text", "text": result.get("answer", "No response from mentor")}]
                        }, req_id))

                    # list_plans
                    elif tool_name == "list_plans":
                        response = await client.get(f"{BACKEND_API_URL}/api/v3/tutor/access/plans", timeout=10.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"plans": result},
                            "content": [{"type": "text", "text": f"Available plans: {', '.join([p.get('name', 'Unknown') for p in result]) if isinstance(result, list) else ''}"}]
                        }, req_id))

                    # get_subscription_info
                    elif tool_name == "get_subscription_info":
                        user_id = arguments.get("user_id")
                        if not user_id:
                            raise ValueError("user_id is required")

                        response = await client.get(f"{BACKEND_API_URL}/api/v3/tutor/access/subscription", params={"user_id": user_id}, timeout=10.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"subscription": result},
                            "content": [{"type": "text", "text": f"Subscription: {result.get('tier_name', 'Unknown')} ({result.get('subscription_status', 'UNKNOWN')})"}]
                        }, req_id))

                    # export_user_data
                    elif tool_name == "export_user_data":
                        user_id = arguments.get("user_id")
                        include_progress = arguments.get("include_progress", True)
                        include_quiz_history = arguments.get("include_quiz_history", True)
                        format = arguments.get("format", "json")
                        if not user_id:
                            raise ValueError("user_id is required")

                        response = await client.post(f"{BACKEND_API_URL}/api/v3/tutor/access/export-data", json={"user_id": user_id, "include_progress": include_progress, "include_quiz_history": include_quiz_history, "format": format}, timeout=30.0)
                        response.raise_for_status()
                        result = response.json()

                        return JSONResponse(content=create_jsonrpc_response({
                            "structuredContent": {"export": result},
                            "content": [{"type": "text", "text": f"Data export requested: {result.get('export_id', 'Pending')} - expires {result.get('expires_at', 'N/A')}"}]
                        }, req_id))

                    else:
                        return JSONResponse(
                            content=create_jsonrpc_error(-32601, f"Unknown tool: {tool_name}", req_id),
                            status_code=404
                        )

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error calling {tool_name}: {e}")
                return JSONResponse(
                    content=create_jsonrpc_error(-32603, f"Backend error: {str(e)}", req_id),
                    status_code=500
                )
            except Exception as e:
                logger.error(f"Error executing {tool_name}: {str(e)}", exc_info=True)
                return JSONResponse(
                    content=create_jsonrpc_error(-32603, f"Error: {str(e)}", req_id),
                    status_code=500
                )

        # =====================================================================
        # Unknown Method
        # =====================================================================
        else:
            return JSONResponse(
                content=create_jsonrpc_error(-32601, f"Method not found: {method}", req_id),
                status_code=404
            )

    except json.JSONDecodeError:
        return JSONResponse(
            content=create_jsonrpc_error(-32700, "Invalid JSON", None),
            status_code=400
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return JSONResponse(
            content=create_jsonrpc_error(-32603, f"Internal error: {str(e)}", None),
            status_code=500
        )
