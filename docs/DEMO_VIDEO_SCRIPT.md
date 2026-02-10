# Course Companion FTE - Demo Video Script

**Hackathon IV Submission**
**Target Duration:** 5 minutes
**Production Date:** February 2026

---

## Video Structure Overview

| Segment | Duration | Content |
|---------|----------|---------|
| 1. Introduction | 30 seconds | Team intro, project overview |
| 2. Architecture | 60 seconds | Zero-LLM + Hybrid explanation |
| 3. Web App Demo | 90 seconds | Full user journey walkthrough |
| 4. ChatGPT App Demo | 90 seconds | Conversational learning session |
| 5. Phase 2 Features | 30 seconds | Premium AI features demo |
| **Total** | **5:00** | |

---

## Segment 1: Introduction (0:00 - 0:30)

**Visual:** Course Companion FTE logo + Team names

**Script:**
> "Welcome to our submission for Agent Factory Hackathon IV. I'm [Name], and together with [Team Members], we built Course Companion FTE — a Digital Full-Time Equivalent educational tutor that works 168 hours per week at 99% cost reduction compared to human tutors."

**Screen:** Title slide with:
- Project name: Course Companion FTE
- Team members
- Architecture: Zero-Backend-LLM + Hybrid

---

## Segment 2: Architecture Overview (0:30 - 1:30)

**Visual:** Architecture diagram from docs/ARCHITECTURE.md

**Script:**
> "Our implementation follows the Agent Factory Architecture with a key innovation: we start with Zero-Backend-LLM by default. This means all core features — content delivery, quizzes, progress tracking — are deterministic with zero LLM costs."
>
> "Hybrid intelligence is added selectively only for premium features like AI-graded assessments and our AI mentor. This keeps our per-user cost at just $0.002-0.004 per month while still delivering powerful AI tutoring."

**Screen to show:**
```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  STUDENT     │────▶│  CHATGPT     │────▶│  BACKEND     │
│              │     │  APP         │     │  (Zero-LLM)  │
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                    All LLM work here
                    (Zero cost to dev!)
```

---

## Segment 3: Web App Demo (1:30 - 3:00)

**URL:** http://92.113.147.250:3225

### 3a. Dashboard Tour (1:30 - 2:00)

**Actions:**
1. Show login page
2. Login with demo account
3. Show dashboard with stats cards

**Script:**
> "Let's start with our web application. After logging in, students see their personalized dashboard showing course progress, current streak, and quick access to continue learning."

### 3b. Chapter Navigation (2:00 - 2:30)

**Actions:**
1. Click to Chapters page
2. Show chapter list with completion status
3. Open Chapter 1 (Introduction to AI Agents)
4. Scroll through content
5. Show table of contents sidebar

**Script:**
> "Students browse through course chapters with our beautiful reading interface. Each chapter includes a table of contents, reading progress bar, and a manual 'Mark as Complete' button — giving learners control over their progress."

### 3c. Quiz Experience (2:30 - 3:00)

**Actions:**
1. Click "Take Quiz" button
2. Show quiz interface with one question at a time
3. Answer a few questions
4. Show results page with score

**Script:**
> "Our quiz system features one-question-at-a-time display for better focus. Students receive immediate feedback on their answers with detailed explanations. When they pass, they can continue to the next chapter."

---

## Segment 4: ChatGPT App Demo (3:00 - 4:30)

**Note:** Screen record the ChatGPT interface

### 4a. Content Explanation (3:00 - 3:30)

**User inputs:** "Explain what MCP is in simple terms"

**Script:**
> "Students can also learn directly inside ChatGPT. Watch how our Course Companion skill explains technical concepts at the learner's level with analogies and examples — all powered by ChatGPT's intelligence, using our backend only for content."

**Expected response:** Concept-explainer skill provides clear, simple explanation

### 4b. Interactive Quiz (3:30 - 4:00)

**User inputs:** "Test me on Chapter 1 concepts"

**Script:**
> "The quiz-master skill guides students through practice questions with encouragement and detailed feedback. It maintains motivation even when answers are incorrect."

### 4c. Progress Check (4:00 - 4:30)

**User inputs:** "How am I doing with my progress?"

**Script:**
> "Our progress-motivator celebrates achievements and maintains momentum. It tracks streaks, completion rates, and unlocks achievements to keep students engaged."

---

## Segment 5: Phase 2 Premium Features (4:30 - 5:00)

**URL:** http://92.113.147.250:3225/ai-mentor

**Actions:**
1. Show AI Mentor page
2. Show subscription page
3. Show difference between free and premium

**Script:**
> "For premium subscribers, we offer AI-powered features including our AI mentor for personalized tutoring conversations, LLM-graded assessments with detailed feedback, and adaptive learning paths. These features are cleanly isolated and cost-tracked."

**Closing:**
> "Course Companion FTE — scaling education to thousands with 99% cost reduction. Thank you!"

---

## Production Notes

### Screen Recording Setup

**Tools:**
- OBS Studio (free) or Loom
- Resolution: 1920x1080 minimum
- Frame rate: 30fps
- Audio: Clear microphone narration

### Pre-Demo Checklist

- [ ] Backend running on port 3505
- [ ] Frontend running on port 3225
- [ ] Demo user account created
- [ ] Course content populated (all 4 chapters)
- [ ] At least one quiz with questions
- [ ] ChatGPT App installed and configured

### Demo Account Credentials

**Test Account:**
- Email: demo@test.com
- Password: Demo123!
- Tier: PRO (for premium features)

### Screen Flow Plan

1. **Open with:** Architecture diagram (30s)
2. **Switch to:** Web browser - Frontend (90s)
3. **Switch to:** ChatGPT interface (90s)
4. **Switch to:** Premium features (30s)
5. **Close with:** Team slide + URLs

### URLs to Display

**End Screen:**
```
Course Companion FTE
Agent Factory Hackathon IV

Frontend:  http://92.113.147.250:3225
Backend:   http://92.113.147.250:3505
GitHub:    [Your Repo URL]

Architecture: Zero-Backend-LLM + Hybrid
Cost per User: $0.002-0.004/month
```

---

## Audio Script - Full Recording

```
[0:00-0:30]
"Welcome to Course Companion FTE, our submission for Agent Factory Hackathon IV.
I'm [Your Name], and together with my team, we've built a Digital Full-Time
Equivalent educational tutor that works 168 hours a week at just 0.2% the cost
of human tutoring."

[0:30-1:00]
"Our key innovation is the Zero-Backend-LLM architecture. All core features—
content delivery, quizzes, progress tracking—are completely deterministic with
zero LLM inference costs. ChatGPT handles all the explanation and tutoring work."

[1:00-1:30]
"Hybrid intelligence comes in only for premium features like AI-graded assessments
and our AI mentor. This keeps per-user costs at less than half a cent per month
while still delivering powerful AI tutoring where it matters most."

[1:30-2:00]
"Let me show you the web application. After logging in, students see their
personalized dashboard with course progress, current streak, and quick access
to continue learning."

[2:00-2:30]
"Students browse chapters with our beautiful reading interface featuring a table
of contents, reading progress bar, and manual 'Mark as Complete' button that
gives learners control over their progress."

[2:30-3:00]
"Our quiz system uses one-question-at-a-time display for better focus. Students
get immediate feedback with detailed explanations. Passing quizzes unlocks new
chapters automatically."

[3:00-3:30]
"Students can also learn directly in ChatGPT. Watch how our Course Companion
explains technical concepts at the learner's level with analogies and examples."

[3:30-4:00]
"The quiz-master skill guides students through practice questions with
encouragement and detailed feedback, maintaining motivation even when answers
are incorrect."

[4:00-4:30]
"Our progress-motivator celebrates achievements and maintains momentum by
tracking streaks, completion rates, and unlocking achievements."

[4:30-5:00]
"For premium subscribers, we offer AI-powered features including our AI mentor
for personalized tutoring conversations and LLM-graded assessments. These are
cleanly isolated and cost-tracked. Course Companion FTE—scaling education to
thousands with 99% cost reduction. Thank you!"
```

---

## Tips for Great Demo

1. **Practice runs** - Do at least 3 full rehearsals
2. **Smooth transitions** - Plan your screen switches
3. **Highlight key features** - Don't rush through UI
4. **Speak clearly** - Good audio is essential
5. **Show, don't tell** - Let the UI speak for itself
6. **Keep timing** - 5 minutes max, don't go over

---

## Editing Checklist

- [ ] Intro team slide with logo
- [ ] Architecture diagram overlay
- [ ] Web app screen recording (smooth)
- [ ] ChatGPT screen recording (clear)
- [ ] Premium features demonstration
- [ ] End slide with URLs and contact
- [ ] Background music (optional, subtle)
- [ ] Captions/subtitles (recommended)
- [ ] Export in 1080p MP4 format

---

**Script Version:** 1.0
**Duration:** 5 minutes
**Production:** February 2026
