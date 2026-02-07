# Gamification Features Architecture

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐      │
│  │ TipOfTheDay  │  │ Leaderboard  │  │   Certificate     │      │
│  │  Component   │  │    Page      │  │  Verification     │      │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘      │
│         │                 │                    │                 │
│         ▼                 ▼                    ▼                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │            API Client (lib/api-v3.ts)                   │    │
│  │  • getRandomTip()    • getLeaderboard()                │    │
│  │  • optInToLeaderboard() • generateCertificate()        │    │
│  │  • verifyCertificate()                                 │    │
│  └────────────────────────┬────────────────────────────────┘    │
└───────────────────────────┼──────────────────────────────────────┘
                            │ HTTP/JSON
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐       │
│  │              API Routers                              │       │
│  ├──────────────┬──────────────┬────────────────────────┤       │
│  │   tips.py    │ leaderboard  │  certificates.py        │       │
│  │              │    .py       │                         │       │
│  │ • GET random │ • GET list  │ • POST generate         │       │
│  │ • GET list   │ • POST opt-in│ • GET list             │       │
│  │ • POST create│ • PUT settings│ • GET check-eligibility│       │
│  └──────┬───────┴──────┬───────┴────────┬───────────────┘       │
│         │              │                │                       │
│         ▼              ▼                ▼                       │
│  ┌──────────────────────────────────────────────────────┐       │
│  │              Service Layer                             │       │
│  ├──────────────┬──────────────┬────────────────────────┤       │
│  │TipService    │Leaderboard   │CertificateService       │       │
│  │              │Service       │                         │       │
│  │• get_random  │• calculate_xp│• check_eligibility      │       │
│  │• get_all     │• get_leader  │• generate_cert_id       │       │
│  │• create      │• opt_in/out  │• verify                │       │
│  └──────┬───────┴──────┬───────┴────────┬───────────────┘       │
│         │              │                │                       │
│         ▼              ▼                ▼                       │
│  ┌──────────────────────────────────────────────────────┐       │
│  │              Database (PostgreSQL)                    │       │
│  ├──────────────┬──────────────┬────────────────────────┤       │
│  │    tips      │leaderboard_  │   certificates          │       │
│  │              │opt_in        │                         │       │
│  │• id          │• id          │• id                    │       │
│  │• content     │• user_id     │• certificate_id        │       │
│  │• category    │• display_name│• user_id               │       │
│  │• active      │• is_opted_in │• student_name          │       │
│  │              │• show_*      │• completion_%          │       │
│  │              │              │• average_quiz_score    │       │
│  └──────────────┴──────────────┴────────────────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### Tip of the Day Flow

```
User loads dashboard
        │
        ▼
┌───────────────────────┐
│ TipOfTheDay component │
└───────────┬───────────┘
            │
            ▼
┌─────────────────────┐
│ GET /api/v3/tutor/  │
│     tips/random     │
└───────────┬─────────┘
            │
            ▼
┌─────────────────────┐
│   TipService        │
│   • Query all tips  │
│   • Filter by active│
│   • Random.choice() │
└───────────┬─────────┘
            │
            ▼
┌─────────────────────┐
│   Database: tips    │
│   • SELECT * FROM   │
│     tips WHERE      │
│     active=true     │
└───────────┬─────────┘
            │
            ▼
      [Return Tip]
            │
            ▼
    Display on Dashboard
```

### Leaderboard Flow

```
User joins leaderboard
        │
        ▼
┌───────────────────────┐
│ Leaderboard Page      │
│ • Enter display name  │
│ • Set privacy prefs   │
└───────────┬───────────┘
            │
            ▼
┌─────────────────────┐
│ POST /api/v3/tutor/ │
│ leaderboard/opt-in  │
└───────────┬─────────┘
            │
            ▼
┌─────────────────────┐
│ LeaderboardService  │
│ • Create opt-in     │
│ • Calculate XP      │
└───────────┬─────────┘
            │
            ▼
┌─────────────────────┐
│   XP Calculation    │
│                     │
│ xp = quiz_score     │
│    + (10 * chapters)│
│    + (5 * streak)   │
└───────────┬─────────┘
            │
            ▼
    [Save to Database]
            │
            ▼
      Return Leaderboard
            │
            ▼
    Display Top 10 + User Rank
```

### Certificate Flow

```
User requests certificate
        │
        ▼
┌───────────────────────┐
│ Profile Page          │
│ • Check eligibility   │
│ • Generate if eligible│
└───────────┬───────────┘
            │
            ▼
┌─────────────────────┐
│ POST /api/v3/tutor/ │
│ certificates/        │
│     generate         │
└───────────┬─────────┘
            │
            ▼
┌─────────────────────┐
│ CertificateService  │
│ • check_eligibility()│
│ • generate_cert_id() │
│ • save certificate   │
└───────────┬─────────┘
            │
            ▼
┌─────────────────────┐
│ Eligibility Check   │
│                     │
│ IF completion=100%  │
│ AND avg_score>=70%  │
│ THEN eligible=true  │
└───────────┬─────────┘
            │
            ▼
┌─────────────────────┐
│ Generate Unique ID  │
│                     │
│ CERT-XXXXXX         │
│ (6 random chars)    │
└───────────┬─────────┘
            │
            ▼
    [Save Certificate]
            │
            ▼
    Return Certificate + ID
            │
            ▼
    Display on Profile + Link
```

### Certificate Verification Flow (Public)

```
Anyone visits /certificate/verify/ID
        │
        ▼
┌───────────────────────┐
│ Verification Page     │
│ (No auth required)    │
└───────────┬───────────┘
            │
            ▼
┌─────────────────────┐
│ GET /api/v3/        │
│ certificate/verify/ │
│     {cert_id}       │
└───────────┬─────────┘
            │
            ▼
┌─────────────────────┐
│ CertificateService  │
│ • verify_certificate│
│ • update counter    │
└───────────┬─────────┘
            │
            ▼
┌─────────────────────┐
│   Database Lookup   │
│                     │
│ SELECT * FROM       │
│ certificates WHERE  │
│ certificate_id=?    │
└───────────┬─────────┘
            │
            ▼
    [Return Certificate Details]
            │
            ▼
    Display Certificate with:
    • Student name
    • Completion %
    • Average score
    • Issued date
    • Verified status
```

## Privacy Flow

```
User Privacy Settings
        │
        ▼
┌───────────────────────┐
│ Opt-In Form           │
│ • Display name (anon) │
│ • Show rank?          │
│ • Show score?         │
│ • Show streak?        │
└───────────┬───────────┘
            │
            ▼
┌─────────────────────┐
│ LeaderboardOptIn    │
│ Record in Database  │
└───────────┬─────────┘
            │
            ▼
┌─────────────────────┐
│ Leaderboard Display │
│                     │
│ IF show_rank=false  │
│ THEN hide rank      │
│                     │
│ Always use display  │
│ name (never email)  │
└─────────────────────┘
```

## Component Hierarchy

### TipOfTheDay Component
```
TipOfTheDay
├── State
│   ├── tip: TipItem | null
│   ├── isLoading: boolean
│   └── isRefreshing: boolean
├── Effects
│   └── useEffect → fetchTip on mount
└── UI
    ├── Lightbulb icon (animated when refreshing)
    ├── Category badge
    ├── Tip content
    └── "Get another tip" button
```

### Leaderboard Page
```
LeaderboardPage
├── State
│   ├── leaderboard: LeaderboardData | null
│   ├── optInStatus: LeaderboardOptInStatus | null
│   ├── showOptInForm: boolean
│   └── Form state (displayName, privacy settings)
├── Effects
│   ├── useEffect → fetchLeaderboard
│   └── useEffect → fetchOptInStatus
└── UI
    ├── User Status Card
    │   ├── Rank & XP (if opted in)
    │   └── Opt-in/opt-out buttons
    ├── Opt-In Form (conditional)
    │   ├── Display name input
    │   └── Privacy checkboxes
    └── Leaderboard Table
        └── Top 10 entries with stats
```

### Certificate Verification Page
```
CertificateVerifyPage
├── State
│   ├── verification: CertificateVerification | null
│   ├── isLoading: boolean
│   └── error: string | null
├── Effects
│   └── useEffect → verifyCertificate
└── UI
    ├── Success View
    │   ├── Certificate header
    │   ├── Student name
    │   ├── Stats grid (4 cards)
    │   ├── Issue date
    │   └── Download/Print button
    └── Error View
        └── "Certificate not found"
```

## API Route Map

```
/api/v3/
├── tutor/
│   ├── tips/
│   │   ├── GET  /              - List all tips
│   │   ├── GET  /random        - Get random tip
│   │   ├── GET  /{id}          - Get specific tip
│   │   ├── POST /              - Create tip
│   │   ├── PUT  /{id}          - Update tip
│   │   └── DELETE /{id}        - Delete tip
│   │
│   ├── leaderboard/
│   │   ├── GET  /              - Get leaderboard
│   │   ├── GET  /opt-in-status - Get opt-in status
│   │   ├── POST /opt-in        - Join leaderboard
│   │   ├── POST /opt-out       - Leave leaderboard
│   │   ├── PUT  /opt-in-settings - Update settings
│   │   ├── GET  /rank/{id}     - Get user rank
│   │   └── GET  /stats/{id}    - Get user stats
│   │
│   └── certificates/
│       ├── POST /generate           - Generate certificate
│       ├── GET  /                   - Get user certificates
│       ├── POST /check-eligibility  - Check eligibility
│       ├── GET  /{uuid}             - Get certificate
│       └── DELETE /{uuid}           - Delete certificate
│
└── certificate/
    └── verify/
        └── GET /{id}  - Public verification (NO AUTH)
```

## Database Relationships

```
┌──────────────┐
│    users     │
│              │
│ • id (PK)    │◄────────────┐
│ • email      │             │
│ • tier       │             │
└──────────────┘             │
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────────┐   ┌──────────────┐
│     tips     │    │ leaderboard_opt_in│   │certificates  │
│              │    │                  │   │              │
│ • id (PK)    │    │ • id (PK)        │   │ • id (PK)    │
│ • content    │    │ • user_id (FK)   │   │ • certificate_id│
│ • category   │    │ • display_name   │   │ • user_id (FK)│
│ • active     │    │ • is_opted_in    │   │ • student_name│
└──────────────┘    │ • show_rank      │   │ • completion_%│
                    │ • show_score     │   │ • avg_score   │
                    │ • show_streak    │   │ • issued_at   │
                    └──────────────────┘   └──────────────┘
```

---

**Legend:**
- `PK` = Primary Key
- `FK` = Foreign Key
- `→` = Data flow direction
- `├─┬─┼` = Component hierarchy
