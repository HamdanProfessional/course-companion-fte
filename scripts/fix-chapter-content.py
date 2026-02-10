#!/usr/bin/env python3
"""
Script to populate chapter content in the database.
Updates existing chapters with rich markdown content.
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
backend_dir = Path(__file__).parent.parent
load_dotenv(backend_dir / ".env")

# Add parent directory to path for imports
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import async_session_maker
from src.models.database import Chapter


# Chapter content to populate (using raw strings)
CHAPTERS_CONTENT = {
    1: r"""# Introduction to AI Agents

## What are AI Agents?

AI agents are software systems that can autonomously perform tasks in pursuit of goals.

> **Key Insight**: AI agents represent a paradigm shift from static, rule-based software to dynamic, adaptive systems.

## Key Characteristics

### 1. Autonomy
AI agents operate without constant human intervention.

### 2. Perception
Agents can sense and interpret their environment through various inputs.

### 3. Reasoning
Based on perceived information, agents can make decisions.

### 4. Action
Agents execute actions that affect their environment.

### 5. Learning
Many AI agents can improve their performance over time.

## Types of AI Agents

| Type | Description | Example |
|------|-------------|---------|
| **Reactive Agents** | Respond only to current state | Chess-playing AI |
| **Proactive Agents** | Can take initiative | Personal assistants |
| **Social Agents** | Can interact with others | Chatbots |
| **Hybrid Agents** | Combine multiple approaches | Autonomous vehicles |

## Real-World Applications

### Virtual Assistants
- Siri, Alexa, Google Assistant
- Understand natural language
- Perform tasks across multiple apps

### Autonomous Vehicles
- Self-driving cars
- Delivery drones
- Warehouse robots

### Game Playing
- AlphaGo (Go)
- Deep Blue (Chess)
- OpenAI Five (Dota 2)

## Summary

AI agents are transforming how we interact with technology.
""",

    2: r"""# Agent Architectures

## Overview

The architecture of an AI agent determines its capabilities and appropriate use cases.

## Reactive Architecture

The simplest form of agent architecture.

### Characteristics
- Stateless: No memory of past states
- Fast: Immediate responses
- Simple: Easy to implement

### Use Cases
- Thermostat control
- Simple game bots
- Traffic light controllers

## Deliberative Architecture

Agents maintain an internal model of the world and plan actions.

### Components
- Knowledge Base
- Reasoning Engine
- Planning Module

## Hybrid Architecture

Combines reactive and deliberative approaches.

```
Reactive Layer (Fast, reflexive)
Deliberative Layer (Slow, thoughtful)
```

## Summary

Architecture choice fundamentally shapes an agent's capabilities.
""",

    3: r"""# Multi-Agent Systems

## Introduction

Multiple AI agents working together can solve problems beyond the capability of any single agent.

## Why Multiple Agents?

- Parallel processing
- Robustness through redundancy
- Multiple viewpoints
- Near-unlimited scaling

## Coordination Mechanisms

### 1. Communication
- Message passing
- Request-response patterns
- Event broadcasting

### 2. Cooperation
Agents work toward common goals.

### 3. Competition
Agents compete for resources or rewards.

## MAS Architectures

### Centralized Architecture
- Central coordinator manages all agents
- Easier to implement
- Single point of failure

### Decentralized Architecture
- No central authority
- More robust
- Complex coordination

## Summary

Multi-agent systems enable collaboration beyond individual agent capabilities.
""",

    4: r"""# Agent Communication

## Overview

Effective communication is the foundation of multi-agent coordination.

## Communication Protocols

### Direct Communication
- Point-to-Point Messaging
- Request-Response Patterns
- Event Broadcasting

### Indirect Communication
- Shared Environment (Stigmergy)
- Blackboard Systems
- Tuple Spaces

## Agent Communication Languages (ACL)

### KQML
Knowledge Query and Manipulation Language.

### FIPA ACL
Foundation for Intelligent Physical Agents.

## Standard Protocols

### Contract Net Protocol
The most widely used multi-agent negotiation protocol.

### Auction Protocol
- English Auction
- Dutch Auction
- Vickrey Auction

## Summary

Standardized communication enables agents from different developers to work together.
""",

    5: r"""# Planning and Decision Making

## Introduction

AI agents need to plan sequences of actions to achieve their goals efficiently.

## Classical Planning

### State Space Search
Planning as searching through a space of possible states.

### Planning Algorithms
- STRIPS: Stanford Research Institute Problem Solver
- PDDL: Planning Domain Definition Language
- Partial Order Planning

## Decision Making Under Uncertainty

### Markov Decision Processes (MDP)

Components:
- States (S)
- Actions (A)
- Transition Probabilities (T)
- Rewards (R)
- Discount Factor

### Solving MDPs
- Value Iteration
- Policy Iteration
- Q-Learning

## Hierarchical Planning

Benefits:
- Manage Complexity
- Reuse Plans
- Parallel Execution
- Efficiency

## Summary

Effective planning balances computational cost with solution quality.
""",

    6: r"""# Machine Learning for Agents

## Overview

Machine learning transforms static agents into adaptive systems.

## Learning Types

### Supervised Learning
Learning from labeled examples.

### Reinforcement Learning
Learning through trial and error.

### Imitation Learning
Learning by mimicking expert behavior.

### Unsupervised Learning
Finding patterns in unlabeled data.

## Agent Applications of ML

### Adaptive Behavior
- Learning User Preferences
- Adjusting to Environments

### Personalization
- Recommendation Systems
- Customized Interfaces

## Challenges in ML for Agents

- Sample Efficiency
- Generalization
- Stability
- Safety

## Summary

Machine learning enables agents to go beyond their programming.
""",

    7: r"""# Autonomous Navigation

## Overview

Autonomous navigation enables robots and vehicles to move through environments independently.

## Components of Autonomous Navigation

### 1. Localization
- GPS
- SLAM
- Particle Filters

### 2. Mapping
- Occupancy Grid
- Topological Maps
- Semantic Maps

### 3. Path Planning
- A* Algorithm
- RRT (Rapidly-exploring Random Trees)
- Dijkstra's Algorithm

### 4. Obstacle Avoidance
- Potential Fields
- Velocity Obstacles

## Navigation Architectures

### Deliberative Navigation
Global planning with optimal paths.

### Reactive Navigation
Local planning with fast responses.

### Hybrid Navigation
Best of both worlds.

## Summary

Autonomous navigation integrates perception, planning, and control.
""",

    8: r"""# Human-Agent Interaction

## Overview

Effective interaction with humans is critical for agent success.

## Interaction Modes

### Natural Language Interaction
- Intent Understanding
- Context Management
- Personality and Tone

### Graphical User Interface
- Dashboards and Visualizations
- Direct Manipulation
- Gesture Recognition

### Haptic and Physical Interaction
- Touch Interfaces
- Force Feedback
- Physical Collaboration

## Trust and Transparency

### Explainability
Making agent decisions understandable.

### Predictability
Agents should behave consistently.

## Ethical Considerations

### Privacy
What data is collected and how it's used.

### Autonomy
How much control does the agent have.

### Accountability
Who is responsible for agent actions.

## Summary

Effective human-agent interaction requires technical excellence combined with human-centric design.
""",

    9: r"""# Advanced Topics

## Overview

Exploring cutting-edge developments in AI agents.

## Emerging Architectures

### Large Language Model Agents
Using LLMs as the reasoning engine.

### Swarm Intelligence
Collective behavior from simple rules.

### Embodied AI
AI in physical bodies.

## Advanced Capabilities

### Meta-Cognition
Agents that think about their own thinking.

### Creativity
Generating novel and useful ideas.

### Social Intelligence
Understanding and interacting with others.

## Challenges

### Safety
Alignment, robustness, verification.

### Ethics
Fairness, transparency, accountability.

### Scalability
Multi-agent coordination, network effects.

## Summary

The future of AI agents is limited only by our imagination and responsible engineering.
""",

    10: r"""# Future Directions

## Overview

The future holds exciting possibilities for AI agents.

## What's Coming?

1. General-Purpose Agents
2. Collaborative Ecosystems
3. Lifelong Learning
4. Ethical by Design
5. Human-AI Symbiosis

## A Look Ahead

```
2025: Specialized agents dominate
2027: General-purpose agents emerge
2030: Multi-agent ecosystems common
2035: Human-AI symbiosis achieved
2040: AI agents integral to society
```

## The Big Questions

1. How do we ensure agents remain aligned with human values?
2. What rights and responsibilities should agents have?
3. How do we manage the transition to widespread agent adoption?
4. What does human-AI collaboration look like at its best?
5. How do we ensure benefits are distributed equitably?

## Summary

AI agents will transform every aspect of society. Responsible development is crucial.

> "The question is not whether AI agents will transform our world, but how we will shape that transformation for the benefit of all humanity."
"""
}


async def populate_chapter_content():
    """Populate all chapters with rich content."""
    print("=" * 60)
    print("Populating Chapter Content")
    print("=" * 60)

    async with async_session_maker() as session:
        try:
            # Get all chapters
            result = await session.execute(select(Chapter).order_by(Chapter.order))
            chapters = result.scalars().all()

            print(f"\nFound {len(chapters)} chapters in database.\n")

            # Update each chapter with content
            for chapter in chapters:
                if chapter.order in CHAPTERS_CONTENT:
                    chapter.content = CHAPTERS_CONTENT[chapter.order]
                    print(f"Updated Chapter {chapter.order}: {chapter.title}")
                else:
                    print(f"No content found for Chapter {chapter.order}")

            await session.commit()

            print("\n" + "=" * 60)
            print("Chapter content populated successfully!")
            print("=" * 60)

        except Exception as e:
            print(f"\nError: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(populate_chapter_content())
