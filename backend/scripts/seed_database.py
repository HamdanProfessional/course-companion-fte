"""
Database seeding script for Course Companion FTE.
Creates test users, chapters, quizzes, questions, progress, streaks, and quiz attempts.
Zero-LLM compliance: All data is deterministic, no LLM generation.
"""

import asyncio
import uuid
import os
from datetime import datetime, timedelta, date
from pathlib import Path
import sys
from dotenv import load_dotenv

# Load environment variables from backend/.env
backend_dir = Path(__file__).parent.parent
load_dotenv(backend_dir / ".env")

# Add parent directory to path for imports
sys.path.insert(0, str(backend_dir))

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_maker, engine
from src.models.database import (
    User,
    Chapter,
    Quiz,
    Question,
    Progress,
    Streak,
    QuizAttempt,
)


# ============================================================================
# DATA DEFINITIONS
# ============================================================================

# Users to create
USERS_DATA = [
    {
        "id": uuid.UUID("82b8b862-059a-416a-9ef4-e582a4870efa"),
        "email": "demo@example.com",
        "password": "password123",
        "tier": "FREE",
        "days_ago": 30,
    },
    {
        "id": uuid.uuid4(),
        "email": "premium@example.com",
        "password": "password123",
        "tier": "PREMIUM",
        "days_ago": 60,
    },
    {
        "id": uuid.uuid4(),
        "email": "pro@example.com",
        "password": "password123",
        "tier": "PRO",
        "days_ago": 90,
    },
]

# Chapters content
CHAPTERS_DATA = [
    {
        "order": 1,
        "title": "Introduction to AI Agents",
        "difficulty": "beginner",
        "estimated_time": 30,
        "content": """# Introduction to AI Agents

## What are AI Agents?

AI agents are software systems that can autonomously perform tasks in pursuit of goals. Unlike traditional programs that follow explicit instructions, AI agents can perceive their environment, reason about it, and take actions to achieve objectives.

## Key Characteristics

- **Autonomy**: Operate without constant human intervention
- **Perception**: Can sense and interpret their environment
- **Reasoning**: Can make decisions based on available information
- **Action**: Can execute actions to affect their environment
- **Learning**: Can improve performance over time

## Types of AI Agents

1. **Reactive Agents**: Respond only to current state
2. **Proactive Agents**: Can take initiative
3. **Social Agents**: Can interact with other agents or humans
4. **Hybrid Agents**: Combine multiple approaches

## Applications

AI agents are used in:
- Virtual assistants (Siri, Alexa)
- Autonomous vehicles
- Game playing agents
- Trading systems
- Customer service chatbots

## Summary

AI agents represent a shift from static software to dynamic, goal-oriented systems that can adapt and learn.
"""
    },
    {
        "order": 2,
        "title": "Agent Architectures",
        "difficulty": "beginner",
        "estimated_time": 45,
        "content": """# Agent Architectures

## Overview

Different AI agent architectures provide varying levels of sophistication and capability.

## Reactive Architecture

The simplest form - agents respond only to the current state, ignoring history.

**Pros:**
- Simple to implement
- Fast response time
- Low computational cost

**Cons:**
- Limited intelligence
- No learning from experience
- Cannot handle complex scenarios

## Deliberative Architecture

Agents maintain an internal model of the world and plan actions.

**Components:**
- Knowledge base
- Reasoning engine
- Planning module

**Example:** Chess-playing agents that think several moves ahead

## Hybrid Architecture

Combines reactive and deliberative approaches for both speed and intelligence.

**Benefits:**
- Fast reflexive responses
- Considered planning for complex decisions
- Best of both worlds

## Learning Agents

Can improve performance through experience.

**Types:**
- Reinforcement learning
- Supervised learning
- Unsupervised learning

## Summary

Architecture choice depends on the problem domain and performance requirements.
"""
    },
    {
        "order": 3,
        "title": "Multi-Agent Systems",
        "difficulty": "intermediate",
        "estimated_time": 60,
        "content": """# Multi-Agent Systems

## Introduction

Multiple AI agents working together can solve problems beyond the capability of any single agent.

## Coordination Mechanisms

1. **Communication**: Agents exchange information
2. **Cooperation**: Agents work toward common goals
3. **Competition**: Agents compete for resources
4. **Negotiation**: Agents reach agreements

## Architectures

### Centralized
- Coordinator agent manages others
- Easier to implement
- Single point of failure

### Decentralized
- No central authority
- More robust
- Complex coordination

### Hierarchical
- Mix of centralized and decentralized
- Balances control and autonomy

## Applications

- Traffic management systems
- Supply chain optimization
- Robot swarms
- Distributed sensor networks

## Challenges

- Communication overhead
- Coordination complexity
- Scalability issues
- Conflict resolution

## Summary

Multi-agent systems enable collaboration but require careful design of interaction protocols.
"""
    },
    {
        "order": 4,
        "title": "Agent Communication",
        "difficulty": "intermediate",
        "estimated_time": 50,
        "content": """# Agent Communication

## Overview

Effective communication is essential for multi-agent coordination and collaboration.

## Communication Protocols

### Direct Communication
- Point-to-point messaging
- Request-response patterns
- Event broadcasting

### Indirect Communication
- Shared environment (stigmergy)
- Blackboard systems
- Tuple spaces

## Languages and Ontologies

### Agent Communication Languages (ACL)
- KQML (Knowledge Query and Manipulation Language)
- FIPA ACL (Foundation for Intelligent Physical Agents)
- Coordinated speech acts

### Ontologies
- Shared vocabulary
- Semantic understanding
- Knowledge representation

## Protocols

### Contract Net Protocol
1. Announcement
2. Bidding
3. Awarding
4. Execution

### Auction Protocol
- English auction
- Dutch auction
- Vickrey auction

## Challenges

- Semantic interoperability
- Timing and synchronization
- Trust and reliability
- Scalability

## Summary

Standardized communication enables agents from different developers to work together effectively.
"""
    },
    {
        "order": 5,
        "title": "Planning and Decision Making",
        "difficulty": "intermediate",
        "estimated_time": 70,
        "content": """# Planning and Decision Making

## Introduction

AI agents need to plan sequences of actions to achieve their goals efficiently.

## Classical Planning

### State Space Search
- Forward search
- Backward search
- Bidirectional search

### Planning Algorithms
- STRIPS
- PDDL (Planning Domain Definition Language)
- Partial Order Planning

## Decision Making Under Uncertainty

### Markov Decision Processes (MDP)
- States
- Actions
- Transition probabilities
- Rewards

### Solving MDPs
- Value iteration
- Policy iteration
- Q-learning

## Hierarchical Planning

### Reasons for Hierarchy
- Manage complexity
- Reuse plans
- Parallel execution

### Approaches
- Abstract Hierarchies
- Task decomposition
- Subgoal identification

## Real-World Planning

### Constraints
- Time limits
- Resource constraints
- Partial observability

### Techniques
- Anytime algorithms
- Approximate planning
- Reactive planning layers

## Summary

Effective planning balances computational cost with solution quality.
"""
    },
    {
        "order": 6,
        "title": "Machine Learning for Agents",
        "difficulty": "intermediate",
        "estimated_time": 65,
        "content": """# Machine Learning for Agents

## Overview

Machine learning enables agents to improve their performance through experience.

## Learning Types

### Supervised Learning
- Labeled training data
- Classification and regression
- Common algorithms: Decision trees, neural networks

### Reinforcement Learning
- Learn through trial and error
- Reward maximization
- Q-learning, SARSA, Deep Q-Networks

### Imitation Learning
- Learn from demonstrations
- Inverse reinforcement learning
- Behavioral cloning

## Agent Applications

### Adaptive Behavior
- Learn user preferences
- Adjust to changing environments
- Optimize resource usage

### Personalization
- Recommendation systems
- Customized interfaces
- Tailored responses

## Challenges

- Sample efficiency
- Generalization
- Stability
- Safety

## Advanced Topics

### Meta-Learning
- Learning to learn
- Few-shot learning
- Transfer learning

### Multi-Agent Learning
- Cooperative learning
- Competitive learning
- Emergent behaviors

## Summary

Machine learning transforms static agents into adaptive systems that improve over time.
"""
    },
    {
        "order": 7,
        "title": "Agent Perception and Sensing",
        "difficulty": "advanced",
        "estimated_time": 60,
        "content": """# Agent Perception and Sensing

## Introduction

Perception is how agents acquire and interpret information about their environment.

## Sensing Modalities

### Visual Perception
- Image processing
- Object detection
- Scene understanding

### Auditory Perception
- Speech recognition
- Sound localization
- Audio analysis

### Textual Perception
- Natural language processing
- Sentiment analysis
- Information extraction

## Perception Architectures

### Modular Perception
- Separate modules for each modality
- Specialized processing
- Integration at decision level

### Unified Perception
- Shared representation
- Cross-modal learning
- Sensor fusion

## Challenges

### Noise and Uncertainty
- Sensor errors
- Ambiguous data
- Incomplete information

### Computational Cost
- Real-time processing
- Resource constraints
- Scalability

## Techniques

### Filtering
- Kalman filters
- Particle filters
- Bayesian inference

### Attention Mechanisms
- Selective attention
- Saliency detection
- Focus of attention

## Summary

Robust perception is fundamental for reliable agent operation in real-world environments.
"""
    },
    {
        "order": 8,
        "title": "Autonomous Navigation",
        "difficulty": "advanced",
        "estimated_time": 75,
        "content": """# Autonomous Navigation

## Overview

Autonomous navigation is a key application of AI agents in robotics and vehicles.

## Components

### Localization
- Where am I?
- GPS
- SLAM (Simultaneous Localization and Mapping)
- Particle filters

### Mapping
- What's around me?
- Occupancy grids
- Topological maps
- Semantic maps

### Path Planning
- How do I get there?
- A* algorithm
- RRT (Rapidly-exploring Random Trees)
- Dijkstra's algorithm

### Obstacle Avoidance
- Dynamic obstacle detection
- Potential fields
- Velocity obstacles
- Safe navigation

## Navigation Architectures

### Deliberative
- Global planning
- Optimal paths
- Computationally expensive

### Reactive
- Local planning
- Fast response
- Suboptimal paths

### Hybrid
- Global planner with local avoidance
- Best of both approaches
- Industry standard

## Applications

- Self-driving cars
- Autonomous drones
- Mobile robots
- Warehouse automation

## Challenges

- Dynamic environments
- Human-robot interaction
- Safety guarantees
- Real-time constraints

## Summary

Autonomous navigation integrates perception, planning, and control in complex, dynamic environments.
"""
    },
    {
        "order": 9,
        "title": "Human-Agent Interaction",
        "difficulty": "advanced",
        "estimated_time": 55,
        "content": """# Human-Agent Interaction

## Overview

As agents become more capable, interacting with humans effectively becomes critical.

## Interaction Modes

### Natural Language
- Conversational interfaces
- Intent understanding
- Context management
- Personality and tone

### GUI and Visual
- Dashboards and visualizations
- Direct manipulation
- Gesture recognition
- Facial expression recognition

### Haptic and Physical
- Touch interfaces
- Force feedback
- Physical collaboration
- Shared workspaces

## Trust and Transparency

### Explainability
- Why did you do that?
- Decision visualization
- Feature importance
- Counterfactual explanations

### Predictability
- Consistent behavior
- Clear communication
- Reliable performance

## Ethical Considerations

### Privacy
- Data collection
- Storage and use
- User consent

### Autonomy
- Human oversight
- Override capabilities
- Fail-safe mechanisms

### Accountability
- Responsibility for actions
- Error handling
- Liability

## Design Principles

1. **User-Centered**: Design for human needs
2. **Transparent**: Make decisions understandable
3. **Controllable**: Give users control
4. **Reliable**: Be dependable
5. **Adaptive**: Learn user preferences

## Summary

Effective human-agent interaction requires technical excellence combined with human-centric design.
"""
    },
    {
        "order": 10,
        "title": "Advanced Topics and Future Directions",
        "difficulty": "advanced",
        "estimated_time": 80,
        "content": """# Advanced Topics and Future Directions

## Overview

This chapter explores cutting-edge developments and future possibilities for AI agents.

## Emerging Architectures

### Large Language Model Agents
- LLMs as reasoning engines
- Tool-using agents
- Multi-step reasoning
- Few-shot learning

### Swarm Intelligence
- Collective behavior
- Emergent intelligence
- Decentralized control
- Scalability

### Embodied AI
- Physical robots
- Sensorimotor learning
- Grounded language
- World models

## Advanced Capabilities

### Meta-Cognition
- Self-awareness
- Introspection
- Reflection
- Self-improvement

### Creativity
- Generative agents
- Novel solutions
- Innovation
- Art and design

### Social Intelligence
- Theory of mind
- Empathy
- Social norms
- Collaboration

## Challenges

### Safety
- Alignment
- Robustness
- Verification
- Control

### Ethics
- Fairness
- Bias mitigation
- Transparency
- Accountability

### Scalability
- Multi-agent coordination
- Distributed systems
- Network effects
- Resource management

## Future Vision

The future of AI agents includes:
- **General-purpose agents** that can handle diverse tasks
- **Collaborative ecosystems** of specialized agents
- **Lifelong learning** from continuous interaction
- **Ethical frameworks** built-in from the start
- **Human-AI symbiosis** augmenting human capabilities

## Summary

AI agents are rapidly evolving, with exciting possibilities and significant responsibilities ahead.
"""
    }
]

# Quiz questions for each chapter
QUIZ_DATA = {
    1: {  # Introduction to AI Agents
        "title": "Introduction to AI Agents Quiz",
        "questions": [
            {
                "order": 1,
                "question_text": "What is the defining characteristic that distinguishes AI agents from traditional programs?",
                "options": {"A": "They are written in Python", "B": "They can autonomously pursue goals", "C": "They have a user interface", "D": "They run faster"},
                "correct_answer": "B",
                "explanation": "AI agents can autonomously perceive their environment, reason about it, and take actions to achieve objectives."
            },
            {
                "order": 2,
                "question_text": "Which of the following is NOT a key characteristic of AI agents?",
                "options": {"A": "Autonomy", "B": "Perception", "C": "Hard-coded rules only", "D": "Learning capability"},
                "correct_answer": "C",
                "explanation": "AI agents are not limited to hard-coded rules; they can adapt and learn from their environment."
            },
            {
                "order": 3,
                "question_text": "What type of AI agent responds only to the current state without considering history?",
                "options": {"A": "Proactive Agent", "B": "Reactive Agent", "C": "Social Agent", "D": "Learning Agent"},
                "correct_answer": "B",
                "explanation": "Reactive agents respond only to the current state, while proactive agents can take initiative based on past information."
            },
            {
                "order": 4,
                "question_text": "Which application is NOT mentioned as a common use case for AI agents?",
                "options": {"A": "Virtual assistants", "B": "Autonomous vehicles", "C": "Weather prediction systems", "D": "Customer service chatbots"},
                "correct_answer": "C",
                "explanation": "Weather prediction systems typically use numerical models rather than autonomous AI agents."
            },
            {
                "order": 5,
                "question_text": "What represents the shift from static software to dynamic systems in AI agents?",
                "options": {"A": "Better hardware", "B": "More memory", "C": "Goal-oriented systems that can adapt", "D": "Faster processors"},
                "correct_answer": "C",
                "explanation": "AI agents represent a shift toward goal-oriented systems that can adapt and learn from their environment."
            }
        ]
    },
    2: {  # Agent Architectures
        "title": "Agent Architectures Quiz",
        "questions": [
            {
                "order": 1,
                "question_text": "What is a disadvantage of the reactive architecture?",
                "options": {"A": "Slow response time", "B": "No learning from experience", "C": "High computational cost", "D": "Complex implementation"},
                "correct_answer": "B",
                "explanation": "Reactive agents respond only to current state and cannot learn from past experiences."
            },
            {
                "order": 2,
                "question_text": "Which component is NOT part of a deliberative architecture?",
                "options": {"A": "Knowledge base", "B": "Reasoning engine", "C": "Planning module", "D": "Reflex module"},
                "correct_answer": "D",
                "explanation": "Deliberative architectures have knowledge bases, reasoning engines, and planning modules, but not reflex modules which are for reactive systems."
            },
            {
                "order": 3,
                "question_text": "What is the main advantage of a hybrid agent architecture?",
                "options": {"A": "Easier to implement", "B": "Combines speed and intelligence", "C": "Uses less memory", "D": "No planning needed"},
                "correct_answer": "B",
                "explanation": "Hybrid architectures combine reactive and deliberative approaches to provide both fast responses and intelligent planning."
            },
            {
                "order": 4,
                "question_text": "Which learning type involves learning through trial and error with reward maximization?",
                "options": {"A": "Supervised learning", "B": "Unsupervised learning", "C": "Reinforcement learning", "D": "Transfer learning"},
                "correct_answer": "C",
                "explanation": "Reinforcement learning is characterized by learning through trial and error with reward maximization."
            },
            {
                "order": 5,
                "question_text": "Chess-playing agents that think several moves ahead are an example of which architecture?",
                "options": {"A": "Reactive", "B": "Deliberative", "C": "Social", "D": "Learning-only"},
                "correct_answer": "B",
                "explanation": "Chess agents use deliberative architecture to plan multiple moves ahead using internal models."
            }
        ]
    },
    3: {  # Multi-Agent Systems
        "title": "Multi-Agent Systems Quiz",
        "questions": [
            {
                "order": 1,
                "question_text": "What is a key disadvantage of centralized multi-agent architecture?",
                "options": {"A": "Harder to implement", "B": "Single point of failure", "C": "Slower communication", "D": "More expensive"},
                "correct_answer": "B",
                "explanation": "Centralized architectures have a coordinator agent, creating a single point of failure."
            },
            {
                "order": 2,
                "question_text": "Which coordination mechanism involves agents reaching agreements?",
                "options": {"A": "Communication", "B": "Cooperation", "C": "Competition", "D": "Negotiation"},
                "correct_answer": "D",
                "explanation": "Negotiation is the mechanism where agents reach agreements through communication."
            },
            {
                "order": 3,
                "question_text": "What is stigmergy in multi-agent systems?",
                "options": {"A": "Direct messaging", "B": "Communication through shared environment", "C": "Central coordinator", "D": "Voting system"},
                "correct_answer": "B",
                "explanation": "Stigmergy is a form of indirect communication where agents communicate through modifying a shared environment."
            },
            {
                "order": 4,
                "question_text": "Which application is NOT mentioned for multi-agent systems?",
                "options": {"A": "Traffic management", "B": "Supply chain optimization", "C": "Video game AI", "D": "Robot swarms"},
                "correct_answer": "C",
                "explanation": "While video games use AI, the chapter focuses on traffic management, supply chains, and robot swarms as key applications."
            },
            {
                "order": 5,
                "question_text": "What does hierarchical architecture balance?",
                "options": {"A": "Speed and memory", "B": "Control and autonomy", "C": "Cost and quality", "D": "Size and complexity"},
                "correct_answer": "B",
                "explanation": "Hierarchical architecture provides a mix of centralized control and decentralized autonomy."
            }
        ]
    },
    4: {  # Agent Communication
        "title": "Agent Communication Quiz",
        "questions": [
            {
                "order": 1,
                "question_text": "What does KQML stand for?",
                "options": {"A": "Knowledge Query and Manipulation Language", "B": "Key Quality Markup Language", "C": "Knowledge Quantum Machine Learning", "D": "Key Query Management Logic"},
                "correct_answer": "A",
                "explanation": "KQML stands for Knowledge Query and Manipulation Language, an Agent Communication Language."
            },
            {
                "order": 2,
                "question_text": "Which is NOT a phase of the Contract Net Protocol?",
                "options": {"A": "Announcement", "B": "Bidding", "C": "Negotiation", "D": "Execution"},
                "correct_answer": "C",
                "explanation": "The Contract Net Protocol has Announcement, Bidding, Awarding, and Execution phases. Negotiation is a separate protocol."
            },
            {
                "order": 3,
                "question_text": "What is the primary purpose of ontologies in agent communication?",
                "options": {"A": "Speed up communication", "B": "Provide shared vocabulary and semantic understanding", "C": "Encrypt messages", "D": "Reduce bandwidth"},
                "correct_answer": "B",
                "explanation": "Ontologies provide shared vocabulary and semantic understanding for effective communication between agents."
            },
            {
                "order": 4,
                "question_text": "Which auction type starts with a high price and lowers it until someone accepts?",
                "options": {"A": "English auction", "B": "Dutch auction", "C": "Vickrey auction", "D": "Sealed-bid auction"},
                "correct_answer": "B",
                "explanation": "Dutch auctions start with a high price and lower it until a bidder accepts."
            },
            {
                "order": 5,
                "question_text": "What is a blackboard system in agent communication?",
                "options": {"A": "Direct messaging system", "B": "Shared data structure for indirect communication", "C": "Central coordinator", "D": "Logging system"},
                "correct_answer": "B",
                "explanation": "Blackboard systems provide a shared data structure for indirect communication between agents."
            }
        ]
    },
    5: {  # Planning and Decision Making
        "title": "Planning and Decision Making Quiz",
        "questions": [
            {
                "order": 1,
                "question_text": "What does PDDL stand for in classical planning?",
                "options": {"A": "Planning Domain Definition Language", "B": "Program Design and Description Language", "C": "Process Data Definition Logic", "D": "Parallel Decision Description Language"},
                "correct_answer": "A",
                "explanation": "PDDL stands for Planning Domain Definition Language, used for expressing planning problems."
            },
            {
                "order": 2,
                "question_text": "Which is NOT a component of a Markov Decision Process (MDP)?",
                "options": {"A": "States", "B": "Actions", "C": "Goals", "D": "Transition probabilities"},
                "correct_answer": "C",
                "explanation": "MDPs consist of States, Actions, Transition probabilities, and Rewards. Goals are not a formal component."
            },
            {
                "order": 3,
                "question_text": "What algorithm explores both forward from start and backward from goal simultaneously?",
                "options": {"A": "Forward search", "B": "Backward search", "C": "Bidirectional search", "D": "Depth-first search"},
                "correct_answer": "C",
                "explanation": "Bidirectional search explores from both start and goal simultaneously, meeting in the middle."
            },
            {
                "order": 4,
                "question_text": "What is a key benefit of hierarchical planning?",
                "options": {"A": "Guarantees optimal solutions", "B": "Easier to implement", "C": "Enables plan reuse and manages complexity", "D": "Faster execution"},
                "correct_answer": "C",
                "explanation": "Hierarchical planning manages complexity and enables plan reuse through abstraction."
            },
            {
                "order": 5,
                "question_text": "When would an agent use anytime algorithms?",
                "options": {"A": "When time limits exist", "B": "When solutions must be optimal", "C": "When no uncertainty exists", "D": "When offline processing"},
                "correct_answer": "A",
                "explanation": "Anytime algorithms can provide solutions at any time, improving with more computation, making them ideal for time-constrained scenarios."
            }
        ]
    },
    6: {  # Machine Learning for Agents
        "title": "Machine Learning for Agents Quiz",
        "questions": [
            {
                "order": 1,
                "question_text": "What learning type uses labeled training data for classification and regression?",
                "options": {"A": "Unsupervised learning", "B": "Supervised learning", "C": "Reinforcement learning", "D": "Meta-learning"},
                "correct_answer": "B",
                "explanation": "Supervised learning uses labeled training data to learn patterns for classification and regression tasks."
            },
            {
                "order": 2,
                "question_text": "Which algorithm is NOT mentioned for reinforcement learning?",
                "options": {"A": "Q-learning", "B": "SARSA", "C": "Linear Regression", "D": "Deep Q-Networks"},
                "correct_answer": "C",
                "explanation": "Linear Regression is a supervised learning algorithm, not a reinforcement learning algorithm."
            },
            {
                "order": 3,
                "question_text": "What is behavioral cloning in imitation learning?",
                "options": {"A": "Creating agent copies", "B": "Learning from demonstrations by mimicking behavior", "C": "Cloning data structures", "D": "Copying code"},
                "correct_answer": "B",
                "explanation": "Behavioral cloning learns by mimicking behaviors demonstrated by an expert."
            },
            {
                "order": 4,
                "question_text": "What is a challenge mentioned for machine learning in agents?",
                "options": {"A": "Too much data", "B": "Sample efficiency", "C": "Fast learning", "D": "Simple problems"},
                "correct_answer": "B",
                "explanation": "Sample efficiency - learning from limited data - is a key challenge in machine learning for agents."
            },
            {
                "order": 5,
                "question_text": "What is meta-learning?",
                "options": {"A": "Learning about metadata", "B": "Learning to learn", "C": "Learning with metadata", "D": "Meta-analysis of learning"},
                "correct_answer": "B",
                "explanation": "Meta-learning is 'learning to learn' - developing the ability to learn new tasks quickly."
            }
        ]
    },
    7: {  # Agent Perception and Sensing
        "title": "Agent Perception and Sensing Quiz",
        "questions": [
            {
                "order": 1,
                "question_text": "What is NOT a sensing modality mentioned in the chapter?",
                "options": {"A": "Visual perception", "B": "Auditory perception", "C": "Olfactory perception", "D": "Textual perception"},
                "correct_answer": "C",
                "explanation": "The chapter covers Visual, Auditory, and Textual perception but not olfactory (smell) perception."
            },
            {
                "order": 2,
                "question_text": "What is the main advantage of unified perception architecture?",
                "options": {"A": "Specialized processing", "B": "Shared representation and cross-modal learning", "C": "Simpler implementation", "D": "Lower cost"},
                "correct_answer": "B",
                "explanation": "Unified perception uses shared representation enabling cross-modal learning and sensor fusion."
            },
            {
                "order": 3,
                "question_text": "Which filter is mentioned for dealing with noise and uncertainty in perception?",
                "options": {"A": "Low-pass filter", "B": "Kalman filter", "C": "High-pass filter", "D": "Band-pass filter"},
                "correct_answer": "B",
                "explanation": "Kalman filters and particle filters are mentioned for dealing with noise and uncertainty."
            },
            {
                "order": 4,
                "question_text": "What is saliency detection in attention mechanisms?",
                "options": {"A": "Detecting errors", "B": "Identifying important regions", "C": "Finding boundaries", "D": "Tracking motion"},
                "correct_answer": "B",
                "explanation": "Saliency detection identifies visually important or attention-grabbing regions in perceptual input."
            },
            {
                "order": 5,
                "question_text": "What is a key challenge for real-time perception?",
                "options": {"A": "Too much accuracy", "B": "Computational cost", "C": "Perfect sensors", "D": "Simple environments"},
                "correct_answer": "B",
                "explanation": "Computational cost and resource constraints are key challenges for real-time perception processing."
            }
        ]
    },
    8: {  # Autonomous Navigation
        "title": "Autonomous Navigation Quiz",
        "questions": [
            {
                "order": 1,
                "question_text": "What does SLAM stand for in autonomous navigation?",
                "options": {"A": "Simultaneous Localization and Mapping", "B": "System Location and Mapping", "C": "Synchronous Location and Movement", "D": "Simultaneous Learning and Mapping"},
                "correct_answer": "A",
                "explanation": "SLAM stands for Simultaneous Localization and Mapping, a key technique for determining position while building a map."
            },
            {
                "order": 2,
                "question_text": "Which path planning algorithm uses heuristics to find optimal paths?",
                "options": {"A": "Dijkstra's algorithm", "B": "A* algorithm", "C": "RRT", "D": "BFS"},
                "correct_answer": "B",
                "explanation": "A* algorithm uses heuristics to efficiently find optimal paths, unlike Dijkstra which explores uniformly."
            },
            {
                "order": 3,
                "question_text": "What is a disadvantage of deliberative navigation?",
                "options": {"A": "Suboptimal paths", "B": "Computationally expensive", "C": "Cannot handle dynamic environments", "D": "Too slow for real-time"},
                "correct_answer": "B",
                "explanation": "Deliberative navigation is computationally expensive due to global planning for optimal paths."
            },
            {
                "order": 4,
                "question_text": "Which is NOT mentioned as an application of autonomous navigation?",
                "options": {"A": "Self-driving cars", "B": "Autonomous drones", "C": "Warehouse automation", "D": "Weather forecasting"},
                "correct_answer": "D",
                "explanation": "Weather forecasting is not an application of autonomous navigation; the chapter focuses on vehicles, robots, and automation."
            },
            {
                "order": 5,
                "question_text": "What technique uses virtual repulsive forces for obstacle avoidance?",
                "options": {"A": "Velocity obstacles", "B": "Potential fields", "C": "RRT", "D": "A*"},
                "correct_answer": "B",
                "explanation": "Potential fields create virtual attractive and repulsive forces for obstacle avoidance and path planning."
            }
        ]
    },
    9: {  # Human-Agent Interaction
        "title": "Human-Agent Interaction Quiz",
        "questions": [
            {
                "order": 1,
                "question_text": "Which is NOT an interaction mode mentioned in the chapter?",
                "options": {"A": "Natural language", "B": "Telepathic interface", "C": "GUI and visual", "D": "Haptic and physical"},
                "correct_answer": "B",
                "explanation": "The chapter covers Natural Language, GUI/Visual, and Haptic/Physical interfaces but not telepathic interfaces."
            },
            {
                "order": 2,
                "question_text": "What is counterfactual explanation in AI transparency?",
                "options": {"A": "Explaining what did happen", "B": "Explaining what would have happened under different conditions", "C": "Explaining historical facts", "D": "Explaining nothing"},
                "correct_answer": "B",
                "explanation": "Counterfactual explanations show what would have happened under different conditions, helping users understand decisions."
            },
            {
                "order": 3,
                "question_text": "Which design principle states 'Make decisions understandable'?",
                "options": {"A": "User-Centered", "B": "Transparent", "C": "Controllable", "D": "Reliable"},
                "correct_answer": "B",
                "explanation": "The Transparent principle emphasizes making agent decisions understandable to users."
            },
            {
                "order": 4,
                "question_text": "What is NOT an ethical consideration mentioned?",
                "options": {"A": "Privacy", "B": "Autonomy", "C": "Profitability", "D": "Accountability"},
                "correct_answer": "C",
                "explanation": "Profitability is not an ethical consideration; Privacy, Autonomy, and Accountability are the key ethical concerns mentioned."
            },
            {
                "order": 5,
                "question_text": "What is the purpose of fail-safe mechanisms in human-agent interaction?",
                "options": {"A": "Make the agent faster", "B": "Provide human override and safety", "C": "Improve accuracy", "D": "Reduce cost"},
                "correct_answer": "B",
                "explanation": "Fail-safe mechanisms provide human override capabilities and ensure safety in human-agent interaction."
            }
        ]
    },
    10: {  # Advanced Topics
        "title": "Advanced Topics and Future Directions Quiz",
        "questions": [
            {
                "order": 1,
                "question_text": "What is embodied AI?",
                "options": {"A": "AI in virtual reality", "B": "Physical robots with sensorimotor learning", "C": "AI with emotions", "D": "Cloud-based AI"},
                "correct_answer": "B",
                "explanation": "Embodied AI involves physical robots that learn through sensorimotor interaction with the physical world."
            },
            {
                "order": 2,
                "question_text": "What is theory of mind in social intelligence?",
                "options": {"A": "Reading minds", "B": "Understanding others have mental states", "C": "Controlling thoughts", "D": "Memory systems"},
                "correct_answer": "B",
                "explanation": "Theory of mind is the ability to understand that others have beliefs, desires, and intentions different from one's own."
            },
            {
                "order": 3,
                "question_text": "What is NOT mentioned as a safety challenge for advanced AI agents?",
                "options": {"A": "Alignment", "B": "Robustness", "C": "Speed", "D": "Verification"},
                "correct_answer": "C",
                "explanation": "Speed is not a safety challenge; Alignment, Robustness, Verification, and Control are the key safety concerns."
            },
            {
                "order": 4,
                "question_text": "What is swarm intelligence?",
                "options": {"A": "Individual smart agents", "B": "Collective behavior and emergent intelligence", "C": "Bee simulation", "D": "Network protocols"},
                "correct_answer": "B",
                "explanation": "Swarm intelligence refers to collective behavior and emergent intelligence from decentralized, self-organized systems."
            },
            {
                "order": 5,
                "question_text": "What does human-AI symbiosis mean?",
                "options": {"A": "Humans controlling AI", "B": "AI replacing humans", "C": "AI augmenting human capabilities", "D": "Humans and AI competing"},
                "correct_answer": "C",
                "explanation": "Human-AI symbiosis refers to AI systems that augment and enhance human capabilities through collaboration."
            }
        ]
    }
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


async def clear_database(session: AsyncSession) -> None:
    """Clear all existing data from the database."""
    print("Clearing existing data...")
    await session.execute(QuizAttempt.__table__.delete())
    await session.execute(Streak.__table__.delete())
    await session.execute(Progress.__table__.delete())
    await session.execute(Question.__table__.delete())
    await session.execute(Quiz.__table__.delete())
    await session.execute(Chapter.__table__.delete())
    await session.execute(User.__table__.delete())
    await session.commit()
    print("Database cleared.")


async def create_users(session: AsyncSession) -> list[User]:
    """Create test users."""
    print("\nCreating users...")
    users = []

    for user_data in USERS_DATA:
        user = User(
            id=user_data["id"],
            email=user_data["email"],
            hashed_password=hash_password(user_data["password"]),
            tier=user_data["tier"],
            created_at=datetime.utcnow() - timedelta(days=user_data["days_ago"]),
            last_login=datetime.utcnow() - timedelta(days=1)  # Active users
        )
        session.add(user)
        users.append(user)
        print(f"  - Created user: {user.email} ({user.tier})")

    await session.commit()
    return users


async def create_chapters(session: AsyncSession) -> list[Chapter]:
    """Create chapters with proper navigation links."""
    print("\nCreating chapters...")
    chapters = []

    # Create all chapters first
    for chapter_data in CHAPTERS_DATA:
        chapter = Chapter(
            id=uuid.uuid4(),
            title=chapter_data["title"],
            content=chapter_data["content"],
            order=chapter_data["order"],
            difficulty_level=chapter_data["difficulty"],
            estimated_time=chapter_data["estimated_time"]
        )
        session.add(chapter)
        chapters.append(chapter)

    await session.commit()

    # Refresh to get IDs and set navigation links
    for chapter in chapters:
        await session.refresh(chapter)

    # Set next and previous chapter links
    for i, chapter in enumerate(chapters):
        if i > 0:
            chapter.previous_chapter_id = chapters[i - 1].id
        if i < len(chapters) - 1:
            chapter.next_chapter_id = chapters[i + 1].id
        print(f"  - Created chapter {chapter.order}: {chapter.title}")

    await session.commit()
    return chapters


async def create_quizzes_and_questions(
    session: AsyncSession,
    chapters: list[Chapter]
) -> tuple[list[Quiz], dict[int, list[Question]]]:
    """Create quizzes and questions for each chapter."""
    print("\nCreating quizzes and questions...")
    quizzes = []
    questions_by_chapter = {}

    for chapter in chapters:
        quiz_data = QUIZ_DATA.get(chapter.order)
        if not quiz_data:
            continue

        # Create quiz
        quiz = Quiz(
            id=uuid.uuid4(),
            chapter_id=chapter.id,
            title=quiz_data["title"],
            difficulty=chapter.difficulty_level.upper(),
            created_at=datetime.utcnow() - timedelta(days=30)
        )
        session.add(quiz)
        quizzes.append(quiz)

        # Create questions
        questions = []
        for q_data in quiz_data["questions"]:
            question = Question(
                id=uuid.uuid4(),
                quiz_id=quiz.id,
                question_text=q_data["question_text"],
                options=q_data["options"],
                correct_answer=q_data["correct_answer"],
                explanation=q_data.get("explanation"),
                order=q_data["order"]
            )
            session.add(question)
            questions.append(question)

        questions_by_chapter[chapter.order] = questions
        print(f"  - Created quiz for Chapter {chapter.order}: {quiz.title} ({len(questions)} questions)")

    await session.commit()
    return quizzes, questions_by_chapter


async def create_progress_and_streaks(
    session: AsyncSession,
    users: list[User],
    chapters: list[Chapter]
) -> None:
    """Create progress records and streaks for users."""
    print("\nCreating progress and streaks...")

    # Demo user: 2 chapters completed (20%)
    demo_user = users[0]
    demo_progress = Progress(
        id=uuid.uuid4(),
        user_id=demo_user.id,
        completed_chapters=[str(chapters[0].id), str(chapters[1].id)],
        current_chapter_id=chapters[1].id,
        last_activity=datetime.utcnow() - timedelta(hours=2)
    )
    demo_streak = Streak(
        id=uuid.uuid4(),
        user_id=demo_user.id,
        current_streak=5,
        longest_streak=5,
        last_checkin=date.today()
    )
    session.add(demo_progress)
    session.add(demo_streak)
    print(f"  - Demo user: {len(demo_progress.completed_chapters)} chapters, 5 day streak")

    # Premium user: 4 chapters completed (40%)
    premium_user = users[1]
    premium_progress = Progress(
        id=uuid.uuid4(),
        user_id=premium_user.id,
        completed_chapters=[str(chapters[i].id) for i in range(4)],
        current_chapter_id=chapters[3].id,
        last_activity=datetime.utcnow() - timedelta(hours=6)
    )
    premium_streak = Streak(
        id=uuid.uuid4(),
        user_id=premium_user.id,
        current_streak=15,
        longest_streak=15,
        last_checkin=date.today()
    )
    session.add(premium_progress)
    session.add(premium_streak)
    print(f"  - Premium user: {len(premium_progress.completed_chapters)} chapters, 15 day streak")

    # Pro user: All 10 chapters completed (100%)
    pro_user = users[2]
    pro_progress = Progress(
        id=uuid.uuid4(),
        user_id=pro_user.id,
        completed_chapters=[str(ch.id) for ch in chapters],
        current_chapter_id=chapters[-1].id,
        last_activity=datetime.utcnow() - timedelta(hours=12)
    )
    pro_streak = Streak(
        id=uuid.uuid4(),
        user_id=pro_user.id,
        current_streak=30,
        longest_streak=30,
        last_checkin=date.today()
    )
    session.add(pro_progress)
    session.add(pro_streak)
    print(f"  - Pro user: {len(pro_progress.completed_chapters)} chapters, 30 day streak")

    await session.commit()


async def create_quiz_attempts(
    session: AsyncSession,
    users: list[User],
    chapters: list[Chapter],
    quizzes: list[Quiz],
    questions_by_chapter: dict[int, list[Question]]
) -> None:
    """Create quiz attempts for demo user."""
    print("\nCreating quiz attempts...")

    demo_user = users[0]

    # Build a mapping of chapter_id -> quiz
    quiz_by_chapter = {quiz.chapter_id: quiz for quiz in quizzes}

    # Create attempts for chapters 1 and 2 (both passed with good scores)
    for chapter_order in [1, 2]:
        # Get the chapter and its quiz
        chapter = chapters[chapter_order - 1]  # Zero-indexed
        quiz = quiz_by_chapter.get(chapter.id)
        questions = questions_by_chapter[chapter_order]

        # Create answers (mostly correct for good score)
        answers = {}
        score = 0
        for question in questions:
            # 80% correct for demo user
            if question.order <= 4:
                answers[str(question.id)] = question.correct_answer
                score += 20
            else:
                # Last question wrong
                wrong_answer = "A" if question.correct_answer != "A" else "B"
                answers[str(question.id)] = wrong_answer

        quiz_attempt = QuizAttempt(
            id=uuid.uuid4(),
            user_id=demo_user.id,
            quiz_id=quiz.id,
            score=score,
            answers=answers,
            completed_at=datetime.utcnow() - timedelta(days=chapter_order)
        )
        session.add(quiz_attempt)
        print(f"  - Quiz attempt for Chapter {chapter_order}: {score}%")

    await session.commit()


async def check_tables_exist(session: AsyncSession) -> bool:
    """Check if database tables exist."""
    from sqlalchemy import text
    try:
        result = await session.execute(text("SELECT 1 FROM users LIMIT 1"))
        return True
    except Exception:
        return False


async def seed_database():
    """Main function to seed the database with test data."""
    print("=" * 70)
    print("Course Companion FTE - Database Seeding Script")
    print("=" * 70)

    # Check if tables exist
    async with async_session_maker() as check_session:
        tables_exist = await check_tables_exist(check_session)

    if not tables_exist:
        print("\n" + "=" * 70)
        print("WARNING: Database tables do not exist!")
        print("=" * 70)
        print("\nPlease create database tables first by running:")
        print("  alembic upgrade head")
        print("\nOr for development, you can run:")
        print("  python -c 'from src.core.database import init_db; import asyncio; asyncio.run(init_db())'")
        print("\nAborting seeding.")
        return

    # Get confirmation before clearing
    print("\nWARNING: This will clear all existing data from the database!")
    response = input("Do you want to continue? (yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print("\nSeeding cancelled.")
        return

    async with async_session_maker() as session:
        try:
            # Clear existing data
            await clear_database(session)

            # Create data in order
            users = await create_users(session)
            chapters = await create_chapters(session)
            quizzes, questions_by_chapter = await create_quizzes_and_questions(session, chapters)
            await create_progress_and_streaks(session, users, chapters)
            await create_quiz_attempts(session, users, chapters, quizzes, questions_by_chapter)

            # Summary
            print("\n" + "=" * 70)
            print("DATABASE SEEDING COMPLETED SUCCESSFULLY")
            print("=" * 70)
            print(f"\nSummary:")
            print(f"  - Users created: {len(users)}")
            print(f"  - Chapters created: {len(chapters)}")
            print(f"  - Quizzes created: {len(quizzes)}")
            print(f"  - Total questions: {sum(len(qs) for qs in questions_by_chapter.values())}")
            print(f"\nTest Accounts:")
            print(f"  - demo@example.com / password123 (FREE)")
            print(f"  - premium@example.com / password123 (PREMIUM)")
            print(f"  - pro@example.com / password123 (PRO)")
            print("=" * 70 + "\n")

        except Exception as e:
            print(f"\nERROR: Seeding failed: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_database())
