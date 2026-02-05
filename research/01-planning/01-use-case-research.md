# Research Use Cases

**Source:** https://developers.openai.com/apps-sdk/plan/use-case
**Phase:** Planning
**Last Updated:** February 2026

---

## Overview

Every successful Apps SDK app starts with a crisp understanding of what the user is trying to accomplish. Discovery in ChatGPT is model-driven: the assistant chooses your app when your tool metadata, descriptions, and past usage align with the user's prompt and memories.

---

## Key Concepts

### Why Start With Use Cases

- **Model-driven discovery** - ChatGPT's assistant chooses your app based on metadata alignment with user prompts
- **Prompt alignment** - Success depends on mapping tasks the model should recognize
- **Outcome definition** - Clear outcomes before building tools or components

### Discovery Mechanism

```
User Prompt + Memories → Tool Metadata Match → App Selection
```

---

## Implementation Details

### 1. Gather Inputs

Begin with qualitative and quantitative research:

**User Interviews & Support Requests**
- Capture jobs-to-be-done
- Document terminology users use
- Identify data sources users rely on today

**Prompt Sampling**
- **Direct asks:** "show my Jira board"
- **Indirect intents:** "what am I blocked on for the launch?"
- Capture both explicit and implicit ways users might request your app

**System Constraints**
- Compliance requirements
- Offline data access needs
- Rate limits that will influence tool design

**Document for Each Scenario:**
- User persona
- Context when they reach for ChatGPT
- Success definition (one sentence)

---

### 2. Define Evaluation Prompts

Decision boundary tuning requires a golden set to iterate against.

**For Each Use Case:**

| Prompt Type | Quantity | Purpose |
|-------------|----------|---------|
| Direct | 5+ | Explicit references to data/product/verbs |
| Indirect | 5+ | Goal stated without tool reference |
| Negative | 5+ | Should NOT trigger your app |

**Example Prompts:**

*Direct:*
- "Show my Course Companion dashboard"
- "Quiz me on neural networks"
- "What's my progress in the Python course?"

*Indirect:*
- "I need to understand how neural networks work"
- "Test my knowledge of Python basics"
- "How am I doing with my learning?"

*Negative (shouldn't trigger):*
- "Tell me a joke"
- "Write a poem about learning"
- "What's the weather like?"

---

### 3. Scope the Minimum Lovable Feature

For each use case, decide:

**Visibility Requirements:**
- What information must be visible inline?
- What can be hidden behind expansion?
- What requires fullscreen/picture-in-picture?

**Write Access:**
- Which actions require write access?
- Should writes be gated behind confirmation?
- What needs developer mode approval?

**State Persistence:**
- What state needs to persist between turns?
- Filters, selected rows, draft content?
- Cross-session vs intra-session storage?

**Prioritization Framework:**

```
Impact × Confidence = Priority
```

- **P0:** High impact, high confidence → Ship first
- **P1:** High impact, medium confidence → Expand after
- **P2:** Lower impact or uncertain → Hold for later

---

### 4. Draft Tool Contract

For each scoped use case:

**Inputs:**
- Parameters the model can safely provide
- Keep them explicit
- Use enums when set is constrained
- Document defaults

**Outputs:**
- Structured content to return
- Add fields model can reason about:
  - IDs
  - Timestamps
  - Status
  - Relationships
- Separate from UI-only fields

**Component Intent:**
- Read-only viewer
- Editor with writebacks
- Multiturn workspace

---

## Best Practices

### Research Phase

1. **Start early** - Before writing any code
2. **Be specific** - One sentence success definitions
3. **Capture language** - How users describe their problems
4. **Document constraints** - Compliance, rate limits, data access

### Prompt Design

1. **Vary specificity** - Mix direct and indirect prompts
2. **Include edge cases** - Negative prompts prevent false positives
3. **Use real language** - Actual user quotes over idealized versions
4. **Test across personas** - Different user types may phrase differently

### Scoping

1. **Start small** - One P0 use case
2. **Validate quickly** - Ship and measure
3. **Expand deliberately** - Add based on data, not assumptions
4. **Consider compliance** - Legal review before implementation

---

## Common Pitfalls

### Mistake 1: Starting Without Use Cases

❌ **Don't:** Build tools first, figure out use cases later

✅ **Do:** Map use cases → Define tools → Build components

---

### Mistake 2: Only Direct Prompts

❌ **Don't:** Only test "Show me my dashboard"

✅ **Do:** Test "Help me get organized" (indirect) + negative prompts

---

### Mistake 3: Overly Broad Scope

❌ **Don't:** "Our app does everything"

✅ **Do:** "One P0 scenario, done perfectly"

---

## Iteration Plan

Build time into schedule for:

**Weekly:**
- Rotate through golden prompt set
- Log tool selection accuracy
- Track false positives/negatives

**Continuous:**
- Collect qualitative feedback from testers
- Capture analytics (tool calls, component interactions)
- A/B test metadata changes

**Quarterly:**
- Review use case prioritization
- Expand to P1/P2 scenarios
- Update golden prompt sets

---

## Artifacts to Create

| Artifact | Purpose | When |
|----------|---------|------|
| User personas | Who is using the app | Before anything |
| Prompt catalog | Test set for optimization | After use case research |
| Tool contract | Input/output schema | Before implementation |
| Component wireframes | UX planning | Before coding |
| Compliance checklist | Legal review | Before production |

---

## Related Resources

- **Next:** [Define Tools](./02-define-tools.md)
- **Examples:** [Pizzaz Gallery](https://github.com/openai-apps-sdk-examples/pizzaz)
- **Best Practices:** [App Submission Guidelines](../../04-guidelines/01-submission-guidelines.md)

---

## Course Companion FTE Use Cases

**Example Use Case 1: Concept Explanation**

*Direct Prompts:*
- "Explain neural networks"
- "What is backpropagation?"
- "Help me understand gradient descent"

*Indirect Prompts:*
- "I'm confused about how neural networks learn"
- "Why do we need activation functions?"

*Success Definition:* Student receives age-appropriate explanation with examples they can relate to.

---

**Example Use Case 2: Knowledge Assessment**

*Direct Prompts:*
- "Quiz me on Python basics"
- "Test my knowledge of SQL"
- "Give me a practice test"

*Indirect Prompts:*
- "I want to see if I understand this topic"
- "Check if I'm ready for the exam"

*Success Definition:* Student completes quiz with immediate feedback and encouragement.

---

**Example Use Case 3: Progress Tracking**

*Direct Prompts:*
- "Show my progress"
- "What's my learning streak?"
- "How am I doing?"

*Indirect Prompts:*
- "Am I on track to finish the course?"
- "What should I focus on next?"

*Success Definition:* Student sees clear progress metrics and receives motivational reinforcement.
