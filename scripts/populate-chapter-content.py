#!/usr/bin/env python3
"""
Script to populate chapter content in the database.
Updates existing chapters with rich markdown content.
"""

import asyncio
import uuid
import os
import sys
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


# Chapter content to populate
CHAPTERS_CONTENT = {
    1: """# Introduction to AI Agents

## What are AI Agents?

AI agents are software systems that can autonomously perform tasks in pursuit of goals. Unlike traditional programs that follow explicit instructions, AI agents can perceive their environment, reason about it, and take actions to achieve objectives.

> **Key Insight**: AI agents represent a paradigm shift from static, rule-based software to dynamic, adaptive systems that can learn and evolve.

## Key Characteristics

### 1. Autonomy
AI agents operate without constant human intervention. Once given a goal, they can work independently to achieve it.

### 2. Perception
Agents can sense and interpret their environment through various inputs:
- **Visual**: Image processing, object detection
- **Auditory**: Speech recognition, sound analysis
- **Textual**: Natural language processing
- **Sensor Data**: Temperature, location, movement

### 3. Reasoning
Based on perceived information, agents can make decisions about what actions to take.

### 4. Action
Agents execute actions that affect their environment or change their internal state.

### 5. Learning
Many AI agents can improve their performance over time through experience.

## Types of AI Agents

| Type | Description | Example |
|------|-------------|---------|
| **Reactive Agents** | Respond only to current state | Chess-playing AI |
| **Proactive Agents** | Can take initiative and plan ahead | Personal assistants |
| **Social Agents** | Can interact with other agents/humans | Chatbots, negotiation agents |
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

### Trading Systems
- High-frequency trading
- Portfolio management
- Risk assessment

### Customer Service
- 24/7 support chatbots
- Ticket routing
- Automated responses

## How AI Agents Work

```
┌─────────────────────────────────────────────────┐
│              AGENT LOOP                         │
├─────────────────────────────────────────────────┤
│                                                 │
│  1. PERCEIVE → Sense environment                │
│  2. REASON   → Decide on action                │
│  3. ACT      → Execute action                  │
│  4. LEARN    → Update from experience          │
│           ↖______________↙                      │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Summary

AI agents are transforming how we interact with technology. From simple reactive systems to complex multi-agent societies, they represent the future of intelligent automation.

**Key Takeaways:**
- Agents are autonomous, goal-oriented systems
- They perceive, reason, act, and learn
- Applications range from virtual assistants to autonomous vehicles
- The field combines AI, robotics, and cognitive science
""",

    2: """# Agent Architectures

## Overview

The architecture of an AI agent determines its capabilities, limitations, and appropriate use cases. Different architectures provide varying levels of sophistication and intelligence.

## Reactive Architecture

The simplest form of agent architecture - reactive agents respond only to the current state, ignoring history.

### Characteristics
- **Stateless**: No memory of past states
- **Fast**: Immediate responses
- **Simple**: Easy to implement and debug
- **Limited**: Cannot learn or plan

### How It Works
```
Current State → Decision Rules → Action
```

### Use Cases
- Thermostat control
- Simple game bots
- Traffic light controllers
- Refle x responses in robotics

### Pros & Cons

| Advantages | Disadvantages |
|------------|---------------|
| Simple implementation | No learning from experience |
| Fast response time | Limited intelligence |
| Low computational cost | Cannot handle complex scenarios |
| Predictable behavior | No planning capability |

## Deliberative Architecture

Deliberative agents maintain an internal model of the world and plan actions before executing them.

### Components

#### 1. Knowledge Base
Stores facts about the world:
- Static information (maps, rules)
- Dynamic information (current state)
- Learned information (patterns)

#### 2. Reasoning Engine
Processes information to make decisions:
- Logical inference
- Planning algorithms
- Goal decomposition

#### 3. Planning Module
Creates sequences of actions:
- **STRIPS**: Classical planning
- **PDDL**: Planning Domain Definition Language
- **Hierarchical planning**: Multi-level planning

### Example: Chess Agent
```
1. Perceive board state
2. Generate possible moves
3. Simulate future positions (minimax)
4. Select best move
5. Execute action
```

## Hybrid Architecture

Combines reactive and deliberative approaches for both speed and intelligence.

### Architecture Design
```
┌────────────────────────────────────┐
│        DELIBERATIVE LAYER          │
│    (Slow, thoughtful planning)     │
└──────────────┬─────────────────────┘
               │
               ↓
┌────────────────────────────────────┐
│         REACTIVE LAYER             │
│   (Fast, reflexive responses)      │
└────────────────────────────────────┘
```

### Benefits
- **Fast reflexes** for immediate situations
- **Considered planning** for complex decisions
- **Best of both worlds** architecture
- **Industry standard** for robotics

### Real-World Example: Autonomous Vehicles

```
Situation: Child runs into street

Reactive Layer: IMMEDIATE BRAKE (0.1 seconds)
Deliberative Layer: Plan new route around obstruction (2 seconds)
```

## Learning Agents

Can improve performance through experience using machine learning.

### Types of Learning

#### Supervised Learning
- **Input**: Labeled training data
- **Output**: Classification or prediction
- **Algorithms**: Neural networks, decision trees
- **Example**: Face recognition

#### Reinforcement Learning
- **Input**: Reward/penalty signals
- **Output**: Optimal policy
- **Algorithms**: Q-learning, SARSA, DQN
- **Example**: Game playing AI

#### Imitation Learning
- **Input**: Expert demonstrations
- **Output**: Mimicked behavior
- **Algorithms**: Behavioral cloning
- **Example**: Robot learning from human

#### Unsupervised Learning
- **Input**: Unlabeled data
- **Output**: Patterns and clusters
- **Algorithms**: K-means, PCA
- **Example**: Customer segmentation

## Architecture Comparison

| Architecture | Intelligence | Speed | Complexity | Learning |
|--------------|--------------|-------|------------|----------|
| Reactive | Low | Very Fast | Low | No |
| Deliberative | High | Slow | High | Optional |
| Hybrid | High | Medium | High | Optional |
| Learning | Very High | Medium | Very High | Yes |

## Choosing the Right Architecture

### Use Reactive When:
- Response time is critical
- Environment is simple
- No need for planning
- Resources are limited

### Use Deliberative When:
- Complex decision-making needed
- Time for planning is available
- Future consequences matter
- Optimal solutions required

### Use Hybrid When:
- Both speed and intelligence needed
- Real-time constraints exist
- Dynamic environments
- Safety is critical

### Use Learning When:
- Environment changes over time
- Optimal behavior unknown
- Large amounts of data available
- Performance improvement desired

## Summary

Architecture choice fundamentally shapes an agent's capabilities. The right architecture balances computational cost, response time, and intelligent behavior.

**Key Points:**
- Reactive: Fast but simple
- Deliberative: Smart but slow
- Hybrid: Best of both
- Learning: Adapts over time
- Choice depends on problem domain
""",

    3: """# Multi-Agent Systems

## Introduction

Multiple AI agents working together can solve problems beyond the capability of any single agent. This is the essence of **Multi-Agent Systems (MAS)**.

> **Definition**: A multi-agent system is a computerized system composed of multiple interacting intelligent agents.

## Why Multiple Agents?

### Advantages Over Single Agents

| Single Agent | Multi-Agent System |
|--------------|-------------------|
| Limited processing power | Parallel processing |
| Single point of failure | Robustness through redundancy |
| Limited perspective | Multiple viewpoints |
| Scalability limits | Near-unlimited scaling |
| Brittleness | Graceful degradation |

## Coordination Mechanisms

### 1. Communication
Agents exchange information directly or indirectly.

**Direct Communication:**
- Message passing
- Request-response patterns
- Event broadcasting

**Indirect Communication:**
- Shared environment (stigmergy)
- Blackboard systems
- Tuple spaces

### 2. Cooperation
Agents work toward common goals.

```
Example: Search and Rescue Team
├── Agent 1: Scan area A
├── Agent 2: Scan area B
├── Agent 3: Scan area C
└── Agent 4: Coordinate findings
```

### 3. Competition
Agents compete for resources or rewards.

```
Example: Auction Market
├── Buyer Agent 1: Bid $50
├── Buyer Agent 2: Bid $55
├── Buyer Agent 3: Bid $60
└── Seller Agent: Accept highest bid
```

### 4. Negotiation
Agents reach agreements through communication.

```
Negotiation Process:
1. Agent A proposes: "I'll do X if you do Y"
2. Agent B counters: "I'll do Y if you also do Z"
3. Agent A accepts/agrees/declines
4. Agreement or continue negotiating
```

## MAS Architectures

### Centralized Architecture

```
        ┌──────────────┐
        │  Coordinator │
        │    Agent     │
        └──────┬───────┘
               │
      ┌────────┼────────┐
      ↓        ↓        ↓
   Agent A  Agent B  Agent C
```

**Characteristics:**
- Central coordinator manages all agents
- Decision-making is hierarchical
- Easier to implement and debug
- Single point of failure
- Communication bottleneck at coordinator

**Use Cases:**
- Factory automation
- Traffic management
- Simple coordination problems

### Decentralized Architecture

```
   Agent A ←↔→ Agent B
      ↑ ↖     ↙ ↑
      |    \    |
      ↓   ↙ ↖   ↓
   Agent C ←↔→ Agent D
```

**Characteristics:**
- No central authority
- Peer-to-peer communication
- More robust and fault-tolerant
- Complex coordination protocols
- Emergent behavior possible

**Use Cases:**
- Robot swarms
- Distributed sensor networks
- Peer-to-peer systems

### Hierarchical Architecture

```
         Level 3: Strategic Agent
                  ↓
         Level 2: Tactical Agents
                  ↓
         Level 1: Operational Agents
```

**Characteristics:**
- Mix of centralized and decentralized
- Balances control and autonomy
- Scales well
- Common in nature (armies, corporations)

**Use Cases:**
- Military operations
- Corporate organizations
- Complex robotics systems

## Real-World Applications

### 1. Traffic Management

```
Intersection Management:
- Each intersection = 1 agent
- Neighboring intersections communicate
- Optimize traffic flow locally
- Emergent global optimization
```

### 2. Supply Chain Optimization

```
Supply Chain Agents:
- Supplier agents: Manage inventory
- Logistics agents: Route optimization
- Manufacturer agents: Production planning
- Retailer agents: Demand forecasting
```

### 3. Robot Swarms

```
Swarm Robotics Applications:
- Search and rescue
- Agricultural monitoring
- Construction
- Environmental cleanup
```

### 4. Distributed Sensor Networks

```
Sensor Network:
- Each sensor node = agent
- Collaborative data processing
- Energy-aware coordination
- Fault detection and recovery
```

## Challenges in Multi-Agent Systems

### 1. Communication Overhead
- Message explosion in large systems
- Bandwidth limitations
- Network latency

### 2. Coordination Complexity
- Aligning agent goals
- Preventing conflicts
- Ensuring coherence

### 3. Scalability Issues
- Performance degradation with size
- Resource contention
- Decision bottlenecks

### 4. Conflict Resolution
- Competing goals
- Resource allocation
- Priority management

### 5. Emergent Behavior
- Unpredictable system behavior
- Difficult to verify correctness
- Hard to debug

## Design Principles for MAS

1. **Locality**: Agents should interact primarily with neighbors
2. **Decentralization**: Avoid central control when possible
3. **Asynchrony**: Don't assume synchronized timing
4. **Robustness**: Design for agent failure
5. **Scalability**: Plan for growth

## Summary

Multi-agent systems enable collaboration beyond individual agent capabilities through coordination and communication.

**Key Takeaways:**
- Multiple agents can solve problems single agents cannot
- Communication, cooperation, competition, and negotiation are key mechanisms
- Architecture choice (centralized, decentralized, hierarchical) impacts system properties
- Real applications range from traffic control to robot swarms
- Challenges include coordination complexity, scalability, and emergent behavior
""",

    4: """# Agent Communication

## Overview

Effective communication is the foundation of multi-agent coordination and collaboration. Without communication, agents are isolated entities unable to work together toward common goals.

> "The ability to communicate effectively with others is the hallmark of intelligent systems."

## Communication Protocols

### Direct Communication

#### Point-to-Point Messaging
```
Agent A → Message → Agent B
```

**Characteristics:**
- Direct sender-receiver relationship
- Guaranteed delivery (with acknowledgments)
- Private communication
- Common in client-server architectures

#### Request-Response Patterns
```
Agent A ──Request──→ Agent B
        ←─Response──
```

**Example:**
```python
# Agent A sends request
request = {
    "type": "query",
    "content": "What is the weather?"
}

# Agent B responds
response = {
    "type": "answer",
    "content": "Sunny, 25°C"
}
```

#### Event Broadcasting
```
           ┌──→ Agent B
Agent A ──┼──→ Agent C
           └──→ Agent D
```

**Use Cases:**
- Announcements
- Alerts
- Pub-sub systems

### Indirect Communication

#### Shared Environment (Stigmergy)
Agents communicate by modifying and sensing the environment.

```
Agent A → Modifies Environment
Agent B → Senses Environment
Agent B → Infers Agent A's action
```

**Example - Ant Foraging:**
1. Ant finds food
2. Ant deposits pheromone trail
3. Other ants sense pheromone
4. Other ants follow trail
5. Trail reinforces as more ants use it

**Applications:**
- Robot coordination
- Web crawlers
- Resource allocation

#### Blackboard Systems
```
         ┌─────────────┐
Agent A →│             │
Agent B →│ Blackboard  │
Agent C →│             │
         └─────────────┘
```

**Characteristics:**
- Shared data structure
- Agents read/write independently
- Asynchronous collaboration
- Common in AI systems

#### Tuple Spaces
```
Space = { ("task1", data), ("result2", value), ... }

Agent A: write("task", data)
Agent B: read("task", ?)  # Blocks until available
Agent C: take("task", ?)  # Removes after reading
```

**Origins:** Linda coordination language

## Agent Communication Languages (ACL)

### KQML
**Knowledge Query and Manipulation Language**

**Example:**
```lisp
(ask-one
  :sender agent-a
  :receiver agent-b
  :content "What is the capital of France?"
  :reply-with answer-1
)
```

**Performatives (speech acts):**
- `ask-if`: Query yes/no
- `ask-one`: Query for one answer
- `tell`: Informative statement
- `achieve`: Request action
- `subscribe`: Continuous updates

### FIPA ACL
**Foundation for Intelligent Physical Agents**

**Message Structure:**
```
{act, sender, receiver, content, language, ontology, protocol}
```

**Example:**
```fipa
inform
  :sender agent1
  :receiver agent2
  :content "Temperature is 25 degrees"
  :language SL
  :ontology weather-ontology
```

### Coordinated Speech Acts
Based on speech act theory from linguistics.

**Basic Speech Acts:**
- **Assertives**: Stating facts ("It is raining")
- **Directives**: Requesting action ("Close the door")
- **Commissives**: Making promises ("I will help")
- **Expressives**: Expressing attitude ("Thank you")
- **Declarations**: Changing reality ("I pronounce you married")

## Ontologies

### What is an Ontology?

> "An ontology is a formal specification of a conceptualization."

**Components:**
1. **Classes**: Categories of things
2. **Properties**: Characteristics of things
3. **Relationships**: How things relate
4. **Axioms**: Rules and constraints
5. **Individuals**: Specific instances

### Example: E-Commerce Ontology

```
Classes:
  - Product, Customer, Order

Properties:
  - Product has price
  - Customer has address
  - Order has status

Relationships:
  - Customer places Order
  - Order contains Product

Axioms:
  - Order must have at least one Product
  - Customer must be 18+ to purchase
```

### Why Ontologies Matter

| Without Ontology | With Ontology |
|------------------|---------------|
| "Buy X" ambiguous | "Purchase(Product X)" clear |
| Different meanings | Shared semantics |
| Integration hard | Integration easy |
| Limited reuse | High reuse |

## Standard Protocols

### Contract Net Protocol

The most widely used multi-agent negotiation protocol.

```
1. Announcement: Manager announces task
   ┌─────────────────────────┐
   │ "Need task X done by T" │
   └─────────────────────────┘
              ↓
2. Bidding: Contractors bid
   ┌─────────────────────────┐
   │ Agent A: "Can do, cost C1"│
   │ Agent B: "Can do, cost C2"│
   └─────────────────────────┘
              ↓
3. Awarding: Manager selects winner
   ┌─────────────────────────┐
   │ "Agent A awarded task X"│
   └─────────────────────────┘
              ↓
4. Execution: Agent A performs task
   ┌─────────────────────────┐
   │ "Task X complete, result R"│
   └─────────────────────────┘
```

### Auction Protocol

#### English Auction
```
Start: $10
Agent A: $15
Agent B: $20
Agent A: $25
...
Agent B: $100  (no more bids)
Winner: Agent B at $100
```

#### Dutch Auction
```
Start: $100
$95 (no bids)
$90 (no bids)
...
$60 (Agent A bids)
Winner: Agent A at $60
```

#### Vickrey Auction
```
All agents submit sealed bids
Agent A: $50
Agent B: $70
Agent C: $90

Winner: Agent C (highest bid)
Price: Agent C pays $70 (second highest)
```

## Challenges in Agent Communication

### 1. Semantic Interoperability
- Different meanings for same terms
- Context-dependent interpretations
- Solution: Shared ontologies

### 2. Timing and Synchronization
- Asynchronous communication
- Message delays
- Solution: Timeouts, acknowledgments

### 3. Trust and Reliability
- False information
- Malicious agents
- Solution: Reputation systems, cryptography

### 4. Scalability
- Message explosion
- Bandwidth limitations
- Solution: Hierarchical communication

## Summary

Standardized communication enables agents from different developers to work together effectively.

**Key Points:**
- Direct vs. indirect communication
- Agent Communication Languages (KQML, FIPA)
- Ontologies provide shared vocabulary
- Standard protocols (Contract Net, Auctions)
- Challenges: semantics, timing, trust, scalability
- Effective communication is essential for MAS
""",

    5: """# Planning and Decision Making

## Introduction

AI agents need to plan sequences of actions to achieve their goals efficiently. Planning is a fundamental capability that separates sophisticated agents from simple reactive systems.

> "Planning is thinking before doing." - The essence of deliberative AI

## Classical Planning

### State Space Search

Planning can be viewed as searching through a space of possible states to find a path from the initial state to a goal state.

```
Initial State → [Action 1] → State 1 → [Action 2] → ... → Goal State
```

### Search Strategies

#### Forward Search
- Start from initial state
- Apply actions until goal reached
- Explores state space forward
- Most common approach

#### Backward Search
- Start from goal state
- Work backwards to initial state
- Useful when few goal states
- Can be more efficient

#### Bidirectional Search
- Search from both directions
- Meet in the middle
- Can be exponentially faster
- Requires efficient state matching

### Planning Algorithms

#### STRIPS
**Stanford Research Institute Problem Solver**

**State Representation:**
- **Predicates**: Facts about the world
- **Operators**: Actions with preconditions and effects
- **Initial State**: Starting configuration
- **Goal State**: Desired configuration

**Example: Blocks World**
```python
# State: predicates
on(A, B), ontable(B), clear(A), hand(empty)

# Operator: pickup(X)
precondition: clear(X), ontable(X), hand(empty)
effect: holding(X), ¬ontable(X), ¬hand(empty)

# Goal: on(A, B)
```

#### PDDL
**Planning Domain Definition Language**

```lisp
(define (domain blocks-world)
  (:requirements :strips :typing)
  (:types block)
  (:predicates (on ?x -block ?y -block)
               (ontable ?x -block)
               (clear ?x -block)
               (hand-empty)
               (holding ?x -block))

  (:action pickup
    :parameters (?x -block)
    :precondition (and (ontable ?x) (clear ?x) (hand-empty))
    :effect (and (holding ?x) (not (ontable ?x))
                 (not (hand-empty)))))

(define (problem simple)
  (:domain blocks-world)
  (:init (ontable A) (ontable B) (clear A)
         (clear B) (hand-empty))
  (:goal (on A B)))
```

#### Partial Order Planning
- Not all actions need to be ordered
- Creates partial plans
- Refines iteratively
- Handles complex constraints

## Decision Making Under Uncertainty

### Markov Decision Processes (MDP)

When the world is uncertain, MDPs provide a formal framework for decision-making.

#### Components

1. **States (S)**: Possible configurations of the world
2. **Actions (A)**: Available actions in each state
3. **Transition Probabilities (T)**: P(s'|s,a) - probability of reaching s' from s with action a
4. **Rewards (R)**: R(s,a) - immediate reward for action a in state s
5. **Discount Factor (γ)**: Importance of future rewards

#### MDP Example: Grid World

```
┌─────┬─────┬─────┐
│  0  │ -1  │  0  │
├─────┼─────┼─────┤
│  0  │ XXX │  0  │  ← Goal (+10)
├─────┼─────┼─────┤
│ +10 │  0  │ -10 │  ← Trap (-10)
└─────┴─────┴─────┘
```

**Agent's Problem:**
- States: Grid positions
- Actions: Up, Down, Left, Right
- Transitions: 80% intended, 20% random slip
- Rewards: +10 at goal, -10 at trap, -1 per step
- Goal: Maximize cumulative reward

### Solving MDPs

#### Value Iteration
```python
# Initialize V(s) = 0 for all states
V = {s: 0 for s in states}

# Iterate until convergence
while not converged:
    for s in states:
        V_new[s] = max_a [R(s,a) + γ * Σ_s' P(s'|s,a) * V(s']]
    if max |V_new[s] - V[s]| < threshold:
        converged = True
    V = V_new

# Extract policy
policy[s] = argmax_a [R(s,a) + γ * Σ_s' P(s'|s,a) * V(s')]
```

#### Policy Iteration
```python
# Initialize random policy
policy = {s: random_action() for s in states}

# Repeat until stable
while True:
    # Policy Evaluation
    V = evaluate_policy(policy)

    # Policy Improvement
    new_policy = improve_policy(V)

    if new_policy == policy:
        break
    policy = new_policy
```

#### Q-Learning (Model-Free)
```python
# Initialize Q-table
Q = {(s,a): 0 for s in states for a in actions}

# For each episode
for episode in range(num_episodes):
    state = initial_state()
    while not terminal:
        # Choose action (ε-greedy)
        if random() < ε:
            action = random_action()
        else:
            action = argmax_a Q[state, a]

        # Take action, observe reward and next state
        next_state, reward = step(state, action)

        # Update Q-value
        Q[state, action] += α * [reward + γ * max_a' Q[next_state, a'] - Q[state, action]]

        state = next_state
```

## Hierarchical Planning

### Reasons for Hierarchy

```
Without Hierarchy:
"Navigate from New York to Los Angeles"
→ 3,000,000 individual actions needed

With Hierarchy:
1. Fly from New York to Los Angeles
   1.1 Go to airport
   1.2 Check in
   1.3 Board plane
   1.4 Fly
   1.5 Deplane
   1.6 Leave airport
```

### Benefits

| Benefit | Description |
|---------|-------------|
| **Manage Complexity** | Break large problems into smaller ones |
| **Reuse Plans** | Abstract plans can apply to many situations |
| **Parallel Execution** | Independent subtasks can run simultaneously |
| **Efficiency** | Avoid replanning at fine granularity |

### Approaches

#### Abstract Hierarchies
- Multiple levels of abstraction
- Plans at different time scales
- Example: Hierarchical Task Networks (HTN)

#### Task Decomposition
```
Goal: Clean House
├── Clean Kitchen
│   ├── Wash Dishes
│   ├── Wipe Counters
│   └── Sweep Floor
├── Clean Bathroom
│   ├── Scrub Toilet
│   └── Wipe Mirror
└── Clean Living Room
    ├── Dust Furniture
    └── Vacuum Carpet
```

#### Subgoal Identification
- Identify key intermediate states
- Plan to each subgoal
- Combine subplans

## Real-World Planning

### Constraints

| Constraint | Impact on Planning |
|------------|-------------------|
| **Time Limits** | Must find solution quickly |
| **Resource Constraints** | Limited compute, memory, energy |
| **Partial Observability** | Don't know full state |
| **Dynamic Environment** | World changes while planning |

### Techniques

#### Anytime Algorithms
- Provide solutions at any time
- Quality improves with more time
- Useful when deadlines exist

```python
def anytime_planner(time_limit):
    solution = initial_solution()
    start_time = now()

    while now() - start_time < time_limit:
        solution = improve_solution(solution)
        if time_critical():
            return solution

    return best_solution_found()
```

#### Approximate Planning
- Trade optimality for speed
- Use heuristics and approximations
- Often good enough in practice

#### Reactive Planning Layers
```
High Level: Deliberative planning (slow)
Mid Level: Tactical decisions (medium)
Low Level: Reactive behaviors (fast)
```

## Planning in Practice

### Autonomous Vehicles
- **Route Planning**: High-level pathfinding
- **Behavior Planning**: Lane changes, merging
- **Motion Planning**: Trajectory generation
- **Control**: Steering, acceleration

### Game AI
- **Strategic Planning**: Long-term goals
- **Tactical Planning**: Short-term objectives
- **Unit Micro**: Individual unit control
- **Building Production**: Resource allocation

### Robotics
- **Task Planning**: What to do
- **Motion Planning**: How to move
- **Path Planning**: Where to go
- **Grasp Planning**: How to manipulate

## Summary

Effective planning balances computational cost with solution quality, using techniques from classical planning to modern reinforcement learning.

**Key Takeaways:**
- Planning finds action sequences to achieve goals
- Classical planning assumes deterministic world
- MDPs handle uncertainty probabilistically
- Hierarchical planning manages complexity
- Real-world planning must handle constraints
- Balance between optimality and computation time
""",

    6: """# Machine Learning for Agents

## Overview

Machine learning is the key that transforms static, rule-based agents into adaptive systems that improve with experience. This chapter explores how ML enables agents to learn from data and interactions.

> "An agent that can learn is not limited by what its programmer knows."

## Learning Types

### Supervised Learning

Learning from labeled examples.

**Characteristics:**
- Training data with input-output pairs
- Goal: Learn mapping from inputs to outputs
- Common tasks: Classification, regression

**Example: Spam Filter**
```python
# Training Data
emails = [
    ("Buy now!!!", "spam"),
    ("Meeting tomorrow", "not spam"),
    ("Free money!!!", "spam"),
    ("Project update", "not spam"),
    # ... thousands more examples
]

# Learn pattern
model = train(emails)

# Predict
model.predict("Limited time offer") → "spam"
```

**Common Algorithms:**
- **Decision Trees**: Learn if-then rules
- **Neural Networks**: Learn complex nonlinear patterns
- **Support Vector Machines**: Find optimal decision boundaries
- **Random Forests**: Ensemble of decision trees

### Reinforcement Learning

Learning through trial and error by maximizing reward.

**The RL Loop:**
```
Agent → Action → Environment → Reward + State → Agent → ...
```

**Key Components:**
- **State**: Current situation
- **Action**: What the agent can do
- **Reward**: Feedback signal (good/bad)
- **Policy**: Strategy for choosing actions

**Example: Teaching a Robot to Walk**
```python
for episode in range(1000):
    state = reset_robot()
    done = False

    while not done:
        action = choose_action(state)
        next_state, reward = step(action)

        # Reward: forward movement good, falling bad
        if moved_forward:
            reward = +1
        if fell:
            reward = -100
            done = True

        # Learn from experience
        update_policy(state, action, reward, next_state)
        state = next_state
```

**Key Algorithms:**

| Algorithm | Description | Use Case |
|-----------|-------------|----------|
| Q-Learning | Value-based method | Simple environments |
| SARSA | On-policy variant | Safe exploration needed |
| DQN | Deep Q-Networks | High-dimensional states |
| PPO | Proximal Policy Opt. | Continuous control |
| A3C | Asynchronous actor-critic | Parallel training |

### Imitation Learning

Learning by mimicking expert behavior.

**Approaches:**

1. **Behavioral Cloning**
   - Collect expert demonstrations
   - Train supervised model to imitate
   - Simple but sensitive to expert quality

```python
# Expert demonstrations
demos = [
    (state1, expert_action1),
    (state2, expert_action2),
    ...
]

# Train to imitate
model = train(demos)

# Use learned policy
action = model.predict(state)
```

2. **Inverse Reinforcement Learning**
   - Infer reward function from expert behavior
   - Agent optimizes inferred reward
   - More robust than behavioral cloning

```python
# Expert shows behavior
expert_demos = observe_expert()

# Infer what expert wants (reward function)
reward_function = infer_reward(expert_demos)

# Optimize for inferred reward
policy = optimize(reward_function)
```

### Unsupervised Learning

Finding patterns in unlabeled data.

**Applications:**
- **Clustering**: Group similar items
- **Dimensionality Reduction**: Simplify data
- **Anomaly Detection**: Find unusual patterns
- **Association Rules**: Discover relationships

## Agent Applications of ML

### Adaptive Behavior

**Learning User Preferences:**
```python
# Content Recommendation Agent
user_history = [
    "AI article",
    "Python tutorial",
    "ML research paper",
    # ...
]

# Cluster topics
interests = cluster(user_history)
# → ["Machine Learning", "Programming", "AI"]

# Recommend similar content
recommendations = find_similar(interests)
```

**Adjusting to Environments:**
```python
# Smart Thermostat Agent
for day in range(30):
    # Learn usage patterns
    patterns = analyze(temperature_history)

    # Adjust schedule
    optimize_schedule(patterns)

    # Learn what user prefers
    learn_preferences(user_feedback)
```

### Personalization

**Recommendation Systems:**
```python
# Netflix-style recommender
# 1. Learn user preferences from watching history
user_profile = encode(watching_history)

# 2. Find similar users
similar_users = find_neighbors(user_profile)

# 3. Recommend what they liked
recommendations = get_watched_by(similar_users)
```

**Customized Interfaces:**
```python
# Adaptive UI Agent
for interaction in user_interactions:
    # Track which features are used
    feature_usage[interaction.feature] += 1

    # Reorganize interface based on usage
    if feature_usage["search"] > feature_usage["browse"]:
        move_search_to_prominent_position()

    # Learn preferred settings
    personalize_settings(interaction)
```

## Challenges in ML for Agents

### Sample Efficiency

**Problem:** Learning from limited data.

**Solutions:**
- **Transfer Learning**: Use knowledge from related tasks
- **Data Augmentation**: Create synthetic training examples
- **Few-Shot Learning**: Learn from very few examples

```python
# Transfer Learning Example
# 1. Pre-train on large dataset
base_model = train(ImageNet)

# 2. Fine-tune for specific task
final_model = fine_tune(base_model, custom_data, few_examples)
```

### Generalization

**Problem:** Performing well on new, unseen situations.

**Solutions:**
- **Diverse Training Data**: Cover many scenarios
- **Regularization**: Prevent overfitting
- **Ensemble Methods**: Combine multiple models

### Stability

**Problem:** Learning process may be unstable or diverge.

**Solutions:**
- **Learning Rate Scheduling**: Adjust learning rate over time
- **Gradient Clipping**: Prevent large updates
- **Batch Normalization**: Stabilize training

### Safety

**Problem:** Agent might learn dangerous behaviors.

**Solutions:**
- **Constrained Learning**: Limit action space
- **Reward Shaping**: Design safe reward functions
- **Human Oversight**: Keep humans in the loop
- **Sim-to-Real**: Train in simulation first

## Advanced Topics

### Meta-Learning

"Learning to learn" - agents that learn how to learn.

```
Traditional ML:
Learn Task A → Use knowledge for Task A
Learn Task B → Use knowledge for Task B (from scratch)

Meta-Learning:
Learn how to learn → Quickly learn any new task
```

**Few-Shot Learning:**
```python
# Meta-learner learns to learn from few examples
meta_learner = train_meta([task1, task2, ..., task100])

# Now can learn new tasks from few examples
new_task = get_new_task(5_examples)  # Only 5 examples!
learned_model = meta_learner.adapt(new_task)
```

### Transfer Learning

Apply knowledge from one domain to another.

```
Domain A (source) → Learn → Knowledge
                                          ↓
Domain B (target) ← Adapt ← Knowledge
```

**Example:**
1. Learn to drive in simulation
2. Transfer knowledge to real car
3. Fine-tune with real-world data

### Multi-Agent Learning

Multiple agents learning together.

**Cooperative Learning:**
- Agents share knowledge
- Learn to coordinate
- Example: Team sports AI

**Competitive Learning:**
- Agents compete against each other
- Improve through competition
- Example: Game AI, adversarial training

**Emergent Behaviors:**
```
Simple rules + learning → Complex emergent behavior

Example:
- Each agent learns to follow neighbors
- Emergent: Flocking behavior
```

## Learning in Production

### Continuous Learning

Agents keep learning after deployment.

```python
while True:
    # Interact with environment
    action = agent.act(state)
    next_state, reward = env.step(action)

    # Learn from experience
    agent.learn(state, action, reward, next_state)

    # Periodically update model
    if should_update():
        deploy_new_model(agent.model)

    state = next_state
```

### Online vs. Batch Learning

| Aspect | Online Learning | Batch Learning |
|--------|----------------|----------------|
| When to learn | Continuously | Periodically |
| Data usage | Single samples | Large batches |
| Adaptability | High | Low |
| Stability | Challenging | Easier |
| Use case | Changing envs | Static envs |

## Summary

Machine learning transforms static agents into adaptive systems that improve over time through experience.

**Key Takeaways:**
- Supervised learning: From labeled examples
- Reinforcement learning: From trial and error
- Imitation learning: From demonstrations
- Unsupervised learning: From patterns in data
- Applications: Personalization, adaptation, optimization
- Challenges: Sample efficiency, generalization, stability, safety
- Advanced: Meta-learning, transfer learning, multi-agent
- ML enables agents to go beyond their programming
""",

    7: """# Agent Perception and Sensing

## Introduction

Perception is the process by which AI agents acquire and interpret information about their environment. It's the foundation upon which all other agent capabilities are built.

> "Without perception, an agent is blind to the world. With perception, it can understand and interact."

## Sensing Modalities

### Visual Perception

Processing visual information from cameras and images.

**Tasks:**
- **Object Detection**: Finding and locating objects
  - Example: Autonomous vehicle detecting pedestrians
- **Scene Understanding**: Interpreting the overall scene
  - Example: Robot understanding it's in a kitchen
- **Face Recognition**: Identifying people
  - Example: Security system recognizing authorized users
- **Optical Character Recognition**: Reading text
  - Example: Document scanner digitizing books

**How It Works:**
```
Image Input → Preprocessing → Feature Extraction → Classification → Output
   ↓             ↓                ↓                    ↓             ↓
Raw pixels   Resize/normalize   Edges/shapes      Object class   "Cat"
```

**Example Pipeline:**
```python
import cv2
import numpy as np
from tensorflow.keras.applications import ResNet50

# Load pre-trained model
model = ResNet50(weights='imagenet')

# Process image
def detect_objects(image_path):
    # Load and preprocess
    image = cv2.imread(image_path)
    image = cv2.resize(image, (224, 224))
    image = np.expand_dims(image, axis=0)
    image = preprocess_input(image)

    # Predict
    predictions = model.predict(image)

    return decode_predictions(predictions)
```

### Auditory Perception

Processing sound and speech information.

**Tasks:**
- **Speech Recognition**: Converting speech to text
  - Example: Voice command system
- **Speaker Identification**: Recognizing who is speaking
  - Example: Authentication by voice
- **Sound Classification**: Identifying sounds
  - Example: Detecting glass breaking for security
- **Emotion Detection**: Recognizing emotion in voice
  - Example: Customer service sentiment analysis

**Audio Processing Pipeline:**
```
Audio Input → Feature Extraction → Pattern Recognition → Output
   ↓             ↓                    ↓                   ↓
Raw sound   MFCCs, spectrograms   Acoustic model    Transcript
```

### Textual Perception

Processing written language.

**Tasks:**
- **Sentiment Analysis**: Detecting emotional tone
  - Example: Analyzing customer reviews
- **Named Entity Recognition**: Finding people, places, organizations
  - Example: Information extraction from documents
- **Topic Modeling**: Discovering main themes
  - Example: Organizing news articles
- **Question Answering**: Understanding questions and finding answers
  - Example: Chatbot comprehension

**NLP Pipeline:**
```
Text → Tokenization → Embedding → Context Model → Understanding
 ↓       ↓              ↓            ↓                  ↓
"Hello" ["Hello"] [0.2,0.8,...] LSTM/Transformer Intent
```

## Perception Architectures

### Modular Perception

Separate modules for each sensing modality.

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│   Vision │  │   Audio  │  │   Text   │
│  Module  │  │  Module  │  │  Module  │
└─────┬─────┘  └─────┬─────┘  └─────┬─────┘
      │              │              │
      └──────────────┼──────────────┘
                     ↓
              Decision Layer
```

**Advantages:**
- Specialized processing for each modality
- Easy to add/remove modalities
- Clear separation of concerns

**Disadvantages:**
- No sharing of learned features
- Redundant processing possible
- Harder to integrate information

### Unified Perception

Shared representation across modalities.

```
┌──────────────────────────────────┐
│        Unified Encoder           │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐   │
│  │Vis│ │Aud│ │Txt│ │Oth│   │
│  └────┘ └────┘ └────┘ └────┘   │
│             ↓                   │
│      Shared Latent Space        │
└──────────────────────────────────┘
```

**Advantages:**
- Cross-modal learning
- Sensor fusion
- More robust overall

**Disadvantages:**
- More complex to implement
- Requires large multi-modal datasets
- Less interpretable

## Challenges in Perception

### Noise and Uncertainty

**Sources of Noise:**
- **Sensor Errors**: Hardware imperfections
  - Example: Camera pixel noise, microphone static
- **Ambiguous Data**: Multiple interpretations
  - Example: Is that a shadow or an object?
- **Incomplete Information**: Partial observations
  - Example: Occluded objects

**Solutions:**

1. **Filtering**
```python
# Kalman Filter for tracking
from filterpy.kalman import KalmanFilter

kf = KalmanFilter(dim_x=4, dim_z=2)  # State: [x, y, vx, vy]

# Predict next position
kf.predict()

# Update with noisy measurement
kf.update(measurement)

# Get filtered estimate
estimated_position = kf.x[:2]  # [x, y]
```

2. **Probabilistic Reasoning**
```python
# Bayesian inference for uncertain perception
P(object|image) ∝ P(image|object) × P(object)

# Update belief with new evidence
belief = initial_belief
for evidence in observations:
    belief = update(belief, evidence)

# Most likely object
detected_object = argmax P(object|all_evidence)
```

3. **Ensemble Methods**
```python
# Combine multiple perception models
vision_prediction = vision_model.predict(image)
audio_prediction = audio_model.predict(sound)

# Weighted combination
combined = 0.7 * vision_prediction + 0.3 * audio_prediction
```

### Computational Cost

**Challenge:** Real-time processing requires efficient algorithms.

**Solutions:**

1. **Hardware Acceleration**
   - GPUs for parallel processing
   - TPUs for ML workloads
   - FPGAs for custom algorithms

2. **Algorithm Optimization**
   - Model compression
   - Quantization (reduced precision)
   - Pruning (removing unimportant weights)

3. **Edge Computing**
   - Process locally on device
   - Reduce cloud dependency
   - Lower latency

3. **Selective Attention**
```python
# Focus computation on important regions
def efficient_perception(image):
    # Find salient regions
    salient_regions = detect_saliency(image)

    # Process only important regions
    for region in salient_regions:
        detail = process_detailed(region)

    # Quick processing for rest
    overview = process_coarse(image)

    return combine(detail, overview)
```

## Advanced Perception Techniques

### Attention Mechanisms

**Selective Attention:** Focus on important information.

```python
# Visual attention
attention_map = compute_attention(image)
attended_image = image * attention_map  # Focus on attended regions

# Self-attention for sequences
attention(Q, K, V) = softmax(QK^T / √d_k) V
```

**Saliency Detection:** Find attention-grabbing regions.

```python
def detect_saliency(image):
    # Compute color contrast
    color_saliency = compute_color_uniqueness(image)

    # Compute orientation uniqueness
    orientation_saliency = compute_orientation(image)

    # Combine
    saliency_map = color_saliency + orientation_saliency

    return normalize(saliency_map)
```

### Sensor Fusion

Combine information from multiple sensors.

```
Camera: "Object at (x=5, y=10)"
Lidar: "Object at (x=5.2, y=9.8)"
Radar: "Object moving at 10 m/s"

Fused: "Object at (x=5.1, y=9.9) moving at 10 m/s"
         (more accurate than any single sensor)
```

**Kalman Filter for Sensor Fusion:**
```python
# State: [position, velocity]
# Sensors: Camera (position), Radar (velocity)

kf = KalmanFilter(dim_x=4, dim_z=2)

# Camera update
kf.update([camera_x, camera_y])

# Radar update
kf.update([radar_vx, radar_vy])

# Fused estimate
position = kf.x[:2]
velocity = kf.x[2:]
```

## Perception in Practice

### Autonomous Vehicles

**Perception Stack:**
```
Lidar → 3D Point Clouds
Camera → Object Detection
Radar → Velocity Measurement
    ↓
Sensor Fusion → Unified World Model
    ↓
Tracking → Object Trajectories
```

### Robotics

**Perception Pipeline:**
```
Depth Camera → 3D Geometry
Gripper Sensor → Force Feedback
Vision → Object Recognition
    ↓
World Model → Complete Scene Understanding
```

### Smart Assistants

**Multi-modal Perception:**
```
Voice: "What's the weather?"
Face: Looking at device
Context: Living room, evening
    ↓
Intent: Check weather for home location
```

## Summary

Robust perception is fundamental for reliable agent operation in real-world environments.

**Key Takeaways:**
- Modalities: Visual, Auditory, Textual
- Architectures: Modular vs. Unified
- Challenges: Noise, uncertainty, computational cost
- Techniques: Filtering, attention, sensor fusion
- Advanced: Deep learning, multi-modal fusion
- Foundation for all other agent capabilities
- Quality of perception limits overall agent performance
""",

    8: """# Autonomous Navigation

## Overview

Autonomous navigation is one of the most exciting and practical applications of AI agents. It enables robots and vehicles to move through environments independently, combining perception, planning, and control.

> "A truly autonomous agent can go where it needs to, without human guidance."

## Components of Autonomous Navigation

### 1. Localization

**Question:** "Where am I?"

**Techniques:**

| Method | Description | Use Case |
|--------|-------------|----------|
| **GPS** | Satellite positioning | Outdoor navigation |
| **SLAM** | Simultaneous Localization and Mapping | Unknown environments |
| **Particle Filters** | Probabilistic localization | Noisy sensors |
| **Landmark Detection** | Recognize known features | Structured environments |

**SLAM (Simultaneous Localization and Mapping):**

```
Unknown Environment
    ↓
Agent moves and observes
    ↓
Build map while determining own position
    ↓
Complete map + trajectory
```

**Particle Filter Example:**
```python
# Particle filter for localization
particles = [
    (x1, y1, θ1, weight1),
    (x2, y2, θ2, weight2),
    ...  # Many particles
]

# Motion update (predict)
for particle in particles:
    particle.move(control_input)

# Sensor update (correct)
for particle in particles:
    weight = particle.match_observation(observation)
    particle.weight = weight

# Resample
particles = resample(particles)  # Keep likely particles

# Estimate position
estimated_position = weighted_average(particles)
```

### 2. Mapping

**Question:** "What's around me?"

**Map Types:**

| Type | Representation | Use Case |
|------|----------------|----------|
| **Occupancy Grid** | 2D grid of occupied/free space | Simple indoor navigation |
| **Topological** | Graph of locations/connections | Large-scale navigation |
| **Semantic Map** | Map with object labels | Interactive agents |
| **3D Map** | Point cloud or mesh | 3D environments |

**Occupancy Grid:**
```
  0 1 2 3 4 5
0 . . . . . .
1 . . X X . .
2 . . . . X .
3 . . . . . .
4 . S . . . .

. = Free space
X = Obstacle
S = Start position
```

### 3. Path Planning

**Question:** "How do I get there?"

**Algorithms:**

#### A* Algorithm
Heuristic search for optimal paths.

```python
import heapq

def a_star(start, goal, obstacles):
    open_set = [(0, start)]  # (f_score, position)
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        current = heapq.heappop(open_set)[1]

        if current == goal:
            return reconstruct_path(came_from, current)

        for neighbor in get_neighbors(current):
            if neighbor in obstacles:
                continue

            tentative_g = g_score[current] + distance(current, neighbor)

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return None  # No path found

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan distance
```

#### RRT (Rapidly-exploring Random Trees)
Probabilistic path planning for complex spaces.

```python
import random

def rrt(start, goal, obstacles, max_iterations=10000):
    tree = {start: None}
    path = None

    for _ in range(max_iterations):
        # Sample random point
        if random.random() < 0.1:  # 10% bias toward goal
            sample = goal
        else:
            sample = (random.randint(0, width), random.randint(0, height))

        # Find nearest node in tree
        nearest = min(tree.keys(), key=lambda n: distance(n, sample))

        # Extend toward sample
        new_node = extend(nearest, sample, step_size)

        # Check if collision-free
        if is_collision_free(nearest, new_node, obstacles):
            tree[new_node] = nearest

            # Check if reached goal
            if distance(new_node, goal) < threshold:
                tree[goal] = new_node
                path = reconstruct_path(tree, goal)
                break

    return path
```

#### Dijkstra's Algorithm
Classic shortest path algorithm.

```python
import heapq

def dijkstra(start, goal, graph):
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    previous = {}
    pq = [(0, start)]

    while pq:
        current_dist, current = heapq.heappop(pq)

        if current_dist > distances[current]:
            continue

        if current == goal:
            break

        for neighbor, weight in graph[current].items():
            distance = current_dist + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current
                heapq.heappush(pq, (distance, neighbor))

    return reconstruct_path(previous, goal)
```

### 4. Obstacle Avoidance

**Question:** "How do I avoid obstacles?"

**Techniques:**

#### Potential Fields
Virtual forces for navigation.

```python
def potential_field_navigation(current, goal, obstacles):
    # Attractive force toward goal
    f_attractive = attractive_force(current, goal)

    # Repulsive force from obstacles
    f_repulsive = Vector(0, 0)
    for obstacle in obstacles:
        f_repulsive += repulsive_force(current, obstacle)

    # Total force
    f_total = f_attractive + f_repulsive

    # Move in direction of force
    next_position = current + normalize(f_total) * step_size

    return next_position

def attractive_force(current, goal):
    direction = goal - current
    return normalize(direction) * K_ATTRACTIVE * distance(current, goal)

def repulsive_force(current, obstacle):
    direction = current - obstacle
    dist = distance(current, obstacle)
    if dist < INFLUENCE_RADIUS:
        return normalize(direction) * K_REPULSIVE * (1/dist - 1/INFLUENCE_RADIUS)
    return Vector(0, 0)
```

#### Velocity Obstacles
Dynamic obstacle avoidance.

```python
def velocity_obstacle(robot_velocity, obstacle_velocity, obstacle_position):
    # Compute velocity obstacle
    VO = compute_VO(obstacle_position, obstacle_velocity, ROBOT_RADIUS)

    # Select velocity outside VO
    if robot_velocity in VO:
        # Find alternative velocity
        new_velocity = find_safe_velocity(VO)
        return new_velocity

    return robot_velocity
```

## Navigation Architectures

### Deliberative Navigation

Global planning with optimal paths.

```
┌─────────────────────────┐
│   Global Planner        │
│  - Complete map          │
│  - Optimal paths         │
│  - A*, Dijkstra          │
└───────────┬─────────────┘
            ↓
    Execute optimal path
```

**Pros:**
- Guaranteed optimal (if complete)
- Handles complex planning

**Cons:**
- Computationally expensive
- Requires complete map
- Slow to replan

### Reactive Navigation

Local planning with fast responses.

```
┌─────────────────────────┐
│   Local Controller      │
│  - Immediate environment │
│  - Fast response        │
│  - Potential fields     │
└─────────────────────────┘
```

**Pros:**
- Fast response
- Handles dynamic environments
- Simple to implement

**Cons:**
- May get stuck in local optima
- Suboptimal paths
- No global planning

### Hybrid Navigation (Best of Both)

```
┌─────────────────────────────────────┐
│        Global Planner               │
│    (Slow, optimal planning)         │
└──────────────┬──────────────────────┘
               ↓
         Global Plan
               ↓
┌─────────────────────────────────────┐
│      Local Planner/Controller       │
│   (Fast, local obstacle avoidance)  │
└─────────────────────────────────────┘
```

**Workflow:**
1. Global planner computes optimal path
2. Local planner executes while avoiding obstacles
3. If blocked, request replanning from global planner

**Example Architecture:**
```python
class HybridNavigator:
    def __init__(self):
        self.global_planner = AStarPlanner()
        self.local_planner = PotentialFieldController()

    def navigate(self, start, goal, map_data):
        # Plan globally
        global_path = self.global_planner.plan(start, goal, map_data)

        # Execute with local avoidance
        current = start
        for waypoint in global_path:
            while not reached(current, waypoint):
                # Local control toward waypoint
                next_pos = self.local_planner.compute_control(
                    current, waypoint, current_obstacles
                )
                current = move_to(next_pos)

        return current
```

## Real-World Applications

### Self-Driving Cars

**Perception → Planning → Control Pipeline:**
```
Sensors (Lidar, Camera, Radar)
    ↓
Perception (Object detection, tracking)
    ↓
Prediction (Object behavior prediction)
    ↓
Planning (Route, behavior, motion)
    ↓
Control (Steering, acceleration, braking)
```

### Autonomous Drones

**3D Navigation Challenges:**
- Full 3D space (not just 2D)
- Aerodynamics constraints
- Battery limitations
- Wind disturbances

**Navigation Stack:**
```python
class DroneNavigator:
    def plan_mission(self, start, goal, no_fly_zones):
        # Consider battery
        max_distance = estimate_battery_range()

        # 3D path planning
        path = rrt_3d(start, goal, no_fly_zones, max_distance)

        # Add charging stops if needed
        if path_length(path) > max_distance:
            path = add_charging_stops(path, charging_stations)

        return path
```

### Warehouse Robots

**Challenges:**
- Dynamic environment (other robots, humans)
- Limited space
- Precision required
- Multi-robot coordination

**Multi-Robot Coordination:**
```python
# Centralized coordination
coordination_system = CentralCoordinator()

for robot in robots:
    # Request path
    path = robot.request_path(goal)

    # Check for conflicts
    conflicts = coordination_system.check_conflicts(path)

    # Resolve conflicts
    if conflicts:
        path = coordination_system.resolve_conflicts(path, conflicts)

    # Assign time slots
    schedule = coordination_system.schedule(robot, path)
```

## Challenges

### Dynamic Environments

**Problem:** Environment changes while navigating.

**Solutions:**
- Continuous perception and replanning
- Predictive planning (anticipate changes)
- Reactive layer for immediate response

### Real-Time Constraints

**Problem:** Must make decisions quickly.

**Solutions:**
- Hierarchical planning (coarse to fine)
- Anytime algorithms (improve solution until deadline)
- Parallel processing

### Safety Guarantees

**Problem:** Must ensure safe operation.

**Solutions:**
- Formal verification of planning algorithms
- Safety barriers (always maintain safe state)
- Failsafe mechanisms (emergency stop)
- Extensive testing and simulation

### Human-Robot Interaction

**Problem:** Navigate around humans safely and naturally.

**Solutions:**
- Predict human motion
- Respect social norms (pass on right, maintain distance)
- Clear communication of intent (signals, lights)
- Voice interaction for instructions

## Summary

Autonomous navigation integrates perception, planning, and control in complex, dynamic environments.

**Key Takeaways:**
- Components: Localization, Mapping, Path Planning, Obstacle Avoidance
- Algorithms: A*, RRT, Dijkstra, Potential Fields
- Architectures: Deliberative, Reactive, Hybrid
- Applications: Self-driving cars, drones, warehouse robots
- Challenges: Dynamic environments, real-time, safety, human interaction
- Navigation is a key application of AI agents in the physical world
""",

    9: """# Human-Agent Interaction

## Overview

As AI agents become more capable and ubiquitous, effective interaction with humans becomes critical. The success of an agent often depends on how well it can communicate with and understand humans.

> "The best agent is one that humans can use naturally and trust implicitly."

## Interaction Modes

### Natural Language Interaction

The most intuitive form of human-agent communication.

**Components:**

1. **Intent Understanding**
```python
# Example: Understanding user requests
"Book a flight to Paris"
    ↓
Intent: BOOK_FLIGHT
Destination: Paris
```

2. **Context Management**
```python
# Maintaining conversation context
conversation = [
    {"user": "What's the weather?"},
    {"agent": "It's sunny and 25°C"},
    {"user": "How about tomorrow?"}  # Refers to weather
]

# Agent maintains context across turns
context = {
    "topic": "weather",
    "location": "current location",
    "timeframe": "tomorrow"
}
```

3. **Personality and Tone**
```python
# Agent personality configuration
personality = {
    "friendliness": "high",
    "formality": "low",
    "humor": "occasional",
    "empathy": "present"
}

# Responses tailored to personality
user: "I'm having a bad day"
formal_response: "I understand you are distressed."
friendly_response: "Oh no, I'm sorry to hear that. Want to talk about it?"
```

**Challenges in NLI:**
- Ambiguity in natural language
- Context dependence
- Sarcasm and idioms
- Multilingual support

### Graphical User Interface

Visual interaction through screens and displays.

**Components:**

1. **Dashboards and Visualizations**
```
┌─────────────────────────────────────┐
│  SYSTEM STATUS                      │
│  ┌──────┐  ┌──────┐  ┌──────┐     │
│  │ CPU  │  │ MEM  │  │ DISK │     │
│  │  45% │  │  62% │  │  71% │     │
│  └──────┘  └──────┘  └──────┘     │
│                                     │
│  [Configure]  [Logs]  [Alerts]     │
└─────────────────────────────────────┘
```

2. **Direct Manipulation**
```python
# Drag-and-drop interface
class DirectManipulationInterface:
    def on_drag_start(self, item):
        self.dragging = item
        self.original_position = item.position

    def on_drag_move(self, position):
        self.dragging.position = position

    def on_drag_drop(self, position):
        if is_valid_drop_target(position):
            execute_action(self.dragging, position)
        else:
            return_to_original_position()
```

3. **Gesture Recognition**
```python
# Recognizing hand gestures
import cv2
import mediapipe

hands = mediapipe.solutions.hands.Hands()

def recognize_gesture(frame):
    # Detect hand landmarks
    results = hands.process(frame)

    if results.multi_hand_landmarks:
        landmarks = results.multi_hand_landmarks[0]

        # Classify gesture
        if is_pointing(landmarks):
            return "POINTING"
        elif is_thumbs_up(landmarks):
            return "THUMBS_UP"
        elif is_wave(landmarks):
            return "WAVE"

    return "NO_GESTURE"
```

### Haptic and Physical Interaction

Touch and physical feedback mechanisms.

**Types:**

1. **Touch Interfaces**
   - Touchscreens
   - Touchpads
   - Gesture surfaces

2. **Force Feedback**
   - Haptic gloves
   - Force feedback joysticks
   - Vibration feedback

3. **Physical Collaboration**
```python
# Human-robot collaborative assembly
class CollaborativeRobot:
    def assist_human(self, task):
        while not task.complete:
            # Sense human position
            human_pos = track_human()

            # Plan complementary action
            robot_action = plan_complementary_action(
                human_pos, task
            )

            # Execute with force monitoring
            execute_with_force_limit(robot_action, max_force=10N)

            # Adjust based on human feedback
            if human_discomfort():
                adjust_action()
```

## Trust and Transparency

### Explainability

Making agent decisions understandable to humans.

**Why It Matters:**
- Build trust
- Enable debugging
- Satisfy regulations
- Improve collaboration

**Approaches:**

1. **Decision Visualization**
```
┌─────────────────────────────────────┐
│  WHY DID I RECOMMEND THIS?          │
│                                     │
│  ✓ Matches your interests (85%)     │
│  ✓ High rated by similar users (92%)│
│  ✓ Currently on sale                │
│  ✗ Longer than your usual reads     │
│                                     │
│  CONFIDENCE: 87%                    │
└─────────────────────────────────────┘
```

2. **Feature Importance**
```python
# Explaining a prediction
import shap

def explain_prediction(model, instance):
    # Compute SHAP values
    explainer = shap.Explainer(model)
    shap_values = explainer(instance)

    # Show feature importance
    explanation = {
        "price": shap_values[0],  # Most important
        "location": shap_values[1],
        "size": shap_values[2],
        # ...
    }

    return explanation

# Example output
"The house is recommended because:"
"- Price is below market average (+0.3)"
"- Location is highly desirable (+0.2)"
"- Size matches your preferences (+0.1)"
```

3. **Counterfactual Explanations**
```python
def counterfactual_explanation(instance, model, desired_outcome):
    """What would need to change to get desired outcome?"""

    current_prediction = model.predict(instance)

    if current_prediction == desired_outcome:
        return "No changes needed"

    # Find minimal changes
    changes = find_minimal_changes(
        instance, model, desired_outcome
    )

    return f"To get {desired_outcome}, you would need to: {changes}"

# Example
loan_request = {...}
explanation = counterfactual_explanation(
    loan_request, model, "approved"
)
# Output: "To get approved, increase income by $5,000
#          or reduce debt by $2,000"
```

### Predictability

Agents should behave consistently and understandably.

**Principles:**

1. **Consistent Behavior**
```python
class PredictableAgent:
    def __init__(self):
        self.behavior_policy = clearly_documented_policy()

    def act(self, state):
        # Use consistent, documented policy
        action = self.behavior_policy.select_action(state)

        # Log decision for transparency
        self.log_decision(state, action)

        return action
```

2. **Clear Communication**
```python
# Communicate intentions clearly
def communicate_intentions(agent, human):
    intentions = agent.plan_next_actions()

    message = {
        "intentions": intentions,
        "reasoning": agent.get_reasoning(),
        "confidence": agent.get_confidence(),
        "alternatives": agent.get_alternatives()
    }

    send_to_human(message, interface="natural_language")
```

3. **Reliable Performance**
```python
# Performance monitoring
class ReliabilityMonitor:
    def __init__(self, agent):
        self.agent = agent
        self.success_rate = []
        self.error_history = []

    def track_performance(self, task, result):
        self.success_rate.append(result.success)

        if result.failed:
            self.error_history.append({
                "task": task,
                "error": result.error,
                "context": result.context
            })

        # Alert if performance degrades
        if recent_success_rate() < threshold:
            alert_human("Performance degraded")
```

## Ethical Considerations

### Privacy

**Concerns:**
- What data is collected?
- How is it stored?
- Who has access?
- How long is it kept?

**Best Practices:**
```python
# Privacy-preserving design
class PrivacyPreservingAgent:
    def __init__(self):
        self.data_retention_policy = {
            "usage_data": "30_days",
            "personal_data": "until_deletion",
            "conversation_logs": "never_store"
        }

    def collect_data(self, data):
        # Minimize collection
        minimal_data = extract_only_essentials(data)

        # Anonymize if possible
        if can_anonymize(minimal_data):
            minimal_data = anonymize(minimal_data)

        # Encrypt storage
        store_encrypted(minimal_data)

        # Set expiration
        set_expiration(minimal_data, self.retention_policy)
```

### Autonomy

**Concerns:**
- How much control does the agent have?
- Can humans override decisions?
- What are fail-safes?

**Human Oversight:**
```python
class HumanOverridableAgent:
    def __init__(self):
        self.requires_approval_for = [
            "high_risk_actions",
            "irreversible_actions",
            "expensive_actions"
        ]

    def execute_action(self, action):
        if action.type in self.requires_approval_for:
            # Request human approval
            approved = request_human_approval(action)

            if not approved:
                return "Action cancelled by human"

        # Execute with human stop capability
        return self.execute_with_stop capability(action)
```

### Accountability

**Concerns:**
- Who is responsible for agent actions?
- How are errors handled?
- What are liabilities?

**Accountability Framework:**
```python
class AccountableAgent:
    def __init__(self):
        self.action_log = []
        self.decision_log = []
        self.human_supervisor = None

    def act(self, state):
        # Log all decisions
        decision = self.make_decision(state)
        self.decision_log.append({
            "state": state,
            "decision": decision,
            "reasoning": self.get_reasoning(),
            "timestamp": now()
        })

        # Log all actions
        action = self.execute(decision)
        self.action_log.append({
            "action": action,
            "outcome": action.outcome,
            "timestamp": now()
        })

        # Alert supervisor for important actions
        if action.importance > threshold:
            notify_supervisor(self.human_supervisor, action)

        return action
```

## Design Principles

### 1. User-Centered Design

Focus on human needs and capabilities.

```python
# Adaptive interface based on user expertise
class AdaptiveInterface:
    def __init__(self, user):
        self.user_expertise = assess_expertise(user)

    def present(self, information):
        if self.user_expertise == "novice":
            return self.simplified_interface(information)
        elif self.user_expertise == "expert":
            return self.detailed_interface(information)
        else:
            return self.standard_interface(information)
```

### 2. Transparency

Make operations visible and understandable.

```python
# Transparent decision-making
class TransparentAgent:
    def explain_decision(self, decision):
        explanation = {
            "what": decision.action,
            "why": decision.reasoning,
            "alternatives": decision.alternatives_considered,
            "confidence": decision.confidence,
            "risks": decision.identified_risks
        }

        return explanation
```

### 3. Controllability

Give users control over the agent.

```python
# User control over agent behavior
class ControllableAgent:
    def __init__(self):
        self.user_preferences = get_user_preferences()
        self.override_capabilities = True

    def act(self, state):
        # Check for user override
        if self.user_has_override():
            return self.user_override_action()

        # Respect user preferences
        allowed_actions = filter_by_preferences(
            all_actions, self.user_preferences
        )

        # Select from allowed actions
        return self.select_action(allowed_actions)
```

### 4. Reliability

Be dependable and consistent.

```python
# Reliability through redundancy
class ReliableAgent:
    def __init__(self):
        self.primary_method = RobustMethod()
        self.backup_methods = [Backup1(), Backup2()]

    def execute(self, task):
        try:
            return self.primary_method.execute(task)
        except Exception as e:
            log_error(e)
            for backup in self.backup_methods:
                try:
                    return backup.execute(task)
                except Exception:
                    continue
            return self.graceful_degradation(task)
```

### 5. Adaptability

Learn and adjust to users.

```python
# Learning user preferences
class AdaptiveAgent:
    def __init__(self):
        self.user_model = UserModel()

    def interact(self, user, interaction):
        # Learn from interaction
        self.user_model.update(interaction)

        # Adapt behavior
        self.adapt_to_user_model(self.user_model)

        # Provide personalized response
        return self.personalized_response(user)
```

## Summary

Effective human-agent interaction requires technical excellence combined with human-centric design, ethical considerations, and continuous attention to trust and transparency.

**Key Takeaways:**
- Interaction modes: Natural language, GUI, haptic/physical
- Trust through explainability and predictability
- Ethics: Privacy, autonomy, accountability
- Design principles: User-centered, transparent, controllable, reliable, adaptable
- The best agent is one that humans trust and can use effectively
- Human-agent interaction is as important as the agent's core capabilities
""",

    10: """# Advanced Topics and Future Directions

## Overview

We've covered the fundamentals of AI agents. Now let's explore cutting-edge developments and future possibilities that are pushing the boundaries of what agents can do.

> "The future of AI agents is limited only by our imagination and our ability to engineer it responsibly."

## Emerging Architectures

### Large Language Model Agents

Using LLMs as the reasoning engine for agents.

**Architecture:**
```
User Request
    ↓
LLM (Reasoning Engine)
    ↓
Tool Selection
    ↓
Tool Execution (Calculator, API, Database, etc.)
    ↓
Result Processing
    ↓
LLM (Format Response)
    ↓
Response to User
```

**Example: Code Agent**
```python
class LLMAgent:
    def __init__(self, llm):
        self.llm = llm
        self.tools = {
            "execute_code": execute_code,
            "search_web": search_web,
            "read_file": read_file,
            "write_file": write_file
        }

    def process(self, user_request):
        # LLM decides which tools to use
        prompt = f"""
        User request: {user_request}
        Available tools: {list(self.tools.keys())}

        Plan which tools to use and in what order.
        """

        plan = self.llm.generate(prompt)

        # Execute tools
        results = []
        for step in plan.steps:
            tool = self.tools[step.tool]
            result = tool(step.parameters)
            results.append(result)

        # LLM formats final response
        response = self.llm.format_response(plan, results)

        return response
```

**Capabilities:**
- Multi-step reasoning
- Tool use and composition
- Few-shot learning from examples
- Natural language understanding and generation

### Swarm Intelligence

Collective behavior emerging from simple agent rules.

**Principles:**
1. **Decentralization**: No central control
2. **Local Interaction**: Agents interact with neighbors
3. **Simple Rules**: Individual behavior is simple
4. **Emergent Intelligence**: Group behavior is complex

**Example: Ant Colony Optimization**
```python
class Ant:
    def __init__(self):
        self.path = []
        self.pheromone_deposited = 0

    def explore(self, graph, pheromones):
        # Probabilistic path selection
        next_node = select_next_node(
            self.current_location,
            graph,
            pheromones  # Follow pheromone trails
        )

        self.path.append(next_node)

        # Deposit pheromone on path
        pheromones[self.path] += self.pheromone_deposited

# Pheromone evaporation
pheromones *= 0.99  # Evaporate over time

# Emergent behavior: Shortest paths have most pheromone
```

**Applications:**
- Drone swarms for search and rescue
- Traffic optimization
- Distributed computing
- Crowd simulation

### Embodied AI

AI in physical bodies interacting with the real world.

**Components:**

1. **Physical Body**
   - Robot, drone, or other physical form
   - Sensors (cameras, microphones, touch)
   - Actuators (motors, speakers)

2. **Sensorimotor Learning**
```python
class EmbodiedAgent:
    def __init__(self):
        self.body = RobotBody()
        self.brain = NeuralNetwork()

    def learn_sensorimotor(self):
        for episode in range(num_episodes):
            # Try action
            action = self.brain.decide_action(self.sensor_state)

            # Execute in physical world
            result = self.body.execute(action)

            # Learn from sensory feedback
            self.brain.learn(
                self.sensor_state,
                action,
                result.sensory_feedback
            )
```

3. **Grounded Language**
```python
# Language connected to physical experience
class GroundedLanguageModel:
    def __init__(self):
        self.word_to_experience = {}

    def learn_word(self, word, experience):
        # Connect word to physical experience
        self.word_to_experience[word] = experience

    def understand(self, word):
        # Understanding through experience
        return self.word_to_experience[word]
```

**Challenges:**
- Sim-to-real transfer
- Sample inefficiency
- Safety in physical world
- Hardware limitations

## Advanced Capabilities

### Meta-Cognition

Agents that think about their own thinking.

**Components:**

1. **Self-Awareness**
```python
class MetaCognitiveAgent:
    def __init__(self):
        self.beliefs = BeliefSystem()
        self.capabilities = CapabilityAssessment()

    def reflect_on_self(self):
        self_assessment = {
            "what_I_know": self.beliefs.get_all(),
            "what_I_can_do": self.capabilities.get_all(),
            "my_limitations": self.capabilities.get_limitations()
        }

        return self_assessment
```

2. **Introspection**
```python
def introspect_on_decision(agent, decision):
    introspection = {
        "why": decision.reasoning,
        "alternatives_considered": decision.alternatives,
        "confidence": decision.confidence,
        "biases": detect_biases(agent, decision)
    }

    return introspection
```

3. **Self-Improvement**
```python
class SelfImprovingAgent:
    def improve(self):
        # Analyze own performance
        performance = self.analyze_performance()

        # Identify weaknesses
        weaknesses = performance.find_weaknesses()

        # Target improvement efforts
        for weakness in weaknesses:
            self.learn_to_address(weakness)
```

### Creativity

Agents generating novel and useful ideas.

**Approaches:**

1. **Generative Models**
```python
# Generative AI for creative tasks
from transformers import GPT2LMHeadModel

model = GPT2LMHeadModel.from_pretrained("gpt2-medium")

def generate_creative_content(prompt):
    # Generate text
    content = model.generate(
        prompt,
        max_length=500,
        temperature=0.8,  # Control creativity
        top_p=0.9
    )

    return content
```

2. **Combinatorial Creativity**
```python
def combine_concepts(concept_a, concept_b):
    # Generate novel combinations
    combination = generate_combinations(
        concept_a.features,
        concept_b.features
    )

    # Evaluate interestingness
    interesting_combinations = filter(
        is_interesting,
        combination
    )

    return interesting_combinations
```

3. **Exploration vs. Exploitation**
```python
class CreativeAgent:
    def create(self, task):
        # Balance exploring new ideas with using known good ideas
        if random.random() < self.exploration_rate:
            return self.explore_new_idea(task)
        else:
            return self.exploit_known_idea(task)
```

### Social Intelligence

Understanding and interacting with other agents and humans.

**Components:**

1. **Theory of Mind**
```python
class TheoryOfMindAgent:
    def model_other_agent(self, other_agent):
        # Model other agent's beliefs
        other_beliefs = infer_beliefs(other_agent.behavior)

        # Model other agent's desires
        other_desires = infer_desires(other_agent.goals)

        # Predict other agent's behavior
        predicted_behavior = predict_behavior(
            other_beliefs,
            other_desires
        )

        return predicted_behavior
```

2. **Empathy**
```python
class EmpathicAgent:
    def respond_empathetically(self, user_emotion):
        # Recognize emotion
        emotion = recognize_emotion(user_emotion)

        # Generate empathetic response
        response = generate_response(
            emotion=emotion,
            empathetic=True,
            tone=appropriate_for(emotion)
        )

        return response
```

3. **Collaboration**
```python
# Collaborative problem-solving
class CollaborativeAgent:
    def collaborate(self, other_agents, task):
        # Divide task
        subtasks = divide_task(task, len(other_agents) + 1)

        # Assign subtasks
        assignments = assign_subtasks(
            subtasks,
            [self] + other_agents
        )

        # Coordinate execution
        results = []
        for agent, subtask in assignments.items():
            result = agent.execute(subtask)
            results.append(result)

        # Combine results
        return combine_results(results)
```

## Challenges

### Safety

**Alignment Problem**
```python
# Ensuring agent goals align with human values
class AlignedAgent:
    def __init__(self):
        # Learn human values
        self.human_values = learn_human_values()

        # Constrain actions to align with values
        self.value_constraints = ValueConstraints(self.human_values)

    def act(self, state):
        # Select action
        action = self.plan_action(state)

        # Check alignment
        if not self.value_constraints.check(action):
            # Find alternative aligned action
            action = self.value_constraints.find_alternative(action)

        return action
```

**Robustness**
- Handle adversarial inputs
- Graceful failure modes
- Verified behavior

**Verification**
```python
# Formal verification of agent behavior
def verify_agent(agent, specification):
    # Model check agent against specification
    model_check_result = model_check(
        agent.transition_system,
        specification.properties
    )

    return model_check_result
```

### Ethics

**Fairness**
```python
# Ensure fair treatment across groups
class FairAgent:
    def __init__(self):
        self.fairness_constraints = FairnessConstraints()

    def make_decision(self, inputs):
        # Make initial decision
        decision = self.model.decide(inputs)

        # Check for unfair bias
        if self.fairness_constraints.is_biased(
            decision, inputs
        ):
            # Adjust for fairness
            decision = self.fairness_constraints.adjust(
                decision
            )

        return decision
```

**Transparency**
```python
# Transparent decision-making
def explain_agent_decision(agent, decision):
    explanation = {
        "decision": decision,
        "reasoning": agent.get_reasoning_trace(decision),
        "confidence": agent.get_confidence(decision),
        "alternatives": agent.considered_alternatives(decision)
    }

    return explanation
```

**Accountability**
```python
# Audit trail for agent actions
class AccountableAgent:
    def __init__(self):
        self.audit_log = AuditLog()

    def act(self, state):
        decision = self.decide(state)
        action = self.execute(decision)

        # Log for accountability
        self.audit_log.log({
            "timestamp": now(),
            "state": state,
            "decision": decision,
            "action": action,
            "outcome": action.outcome
        })

        return action
```

### Scalability

**Multi-Agent Coordination**
```python
# Scaling to many agents
class ScalableMAS:
    def __init__(self, num_agents):
        self.agents = [Agent() for _ in range(num_agents)]
        self.hierarchy = self.build_hierarchy()

    def coordinate(self, task):
        # Hierarchical coordination
        if task.is_global():
            # Global coordinator
            return self.global_coordinate(task)
        else:
            # Local coordination
            return self.local_coordinate(task)
```

**Network Effects**
- Communication overhead grows with number of agents
- Emergent behaviors
- Coordination complexity

**Resource Management**
```python
# Efficient resource use
class ResourceAwareAgent:
    def __init__(self):
        self.budget = ResourceBudget()

    def act(self, state):
        # Plan within resource constraints
        plan = self.plan_with_constraints(
            state,
            self.budget
        )

        return plan
```

## Future Vision

### What's Coming?

1. **General-Purpose Agents**
   - Agents that can handle diverse tasks
   - Transfer learning across domains
   - Few-shot adaptation to new tasks

2. **Collaborative Ecosystems**
   - Specialized agents working together
   - Agent marketplaces and economies
   - Dynamic team formation

3. **Lifelong Learning**
   - Continuous learning from experience
   - Forgetting and consolidation
   - Personalized knowledge

4. **Ethical by Design**
   - Built-in ethical frameworks
   - Transparency and explainability
   - Human oversight and control

5. **Human-AI Symbiosis**
   - Augmenting human capabilities
   - Seamless collaboration
   - Mutual understanding

### A Look Ahead

```
2025: Specialized agents dominate
2027: General-purpose agents emerge
2030: Multi-agent ecosystems common
2035: Human-AI symbiosis achieved
2040: AI agents integral to society
```

### The Big Questions

1. **How do we ensure agents remain aligned with human values as they become more capable?**
2. **What rights and responsibilities should agents have?**
3. **How do we manage the transition to widespread agent adoption?**
4. **What does human-AI collaboration look like at its best?**
5. **How do we ensure benefits are distributed equitably?**

## Summary

AI agents are rapidly evolving, with exciting possibilities and significant responsibilities ahead. The future holds general-purpose agents, collaborative ecosystems, lifelong learning, ethical by design, and human-AI symbiosis.

**Final Takeaways:**
- Emerging: LLM agents, swarm intelligence, embodied AI
- Advanced: Meta-cognition, creativity, social intelligence
- Challenges: Safety, ethics, scalability
- Future: General agents, ecosystems, symbiosis
- Agents will transform every aspect of society
- Responsible development is crucial
- The best is yet to come

> "The question is not whether AI agents will transform our world, but how we will shape that transformation for the benefit of all humanity."

---

**Congratulations on completing this course on AI Agents! You now have a solid foundation to understand, build, and work with AI agents. The future is exciting, and you're ready to be part of it.**
"""
}


async def populate_chapter_content():
    """Populate all chapters with rich content."""
    print("=" * 70)
    print("Populating Chapter Content")
    print("=" * 70)

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
                    print(f"✓ Updated Chapter {chapter.order}: {chapter.title}")
                else:
                    print(f"⚠ No content found for Chapter {chapter.order}")

            await session.commit()

            print("\n" + "=" * 70)
            print("Chapter content populated successfully!")
            print("=" * 70)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(populate_chapter_content())
