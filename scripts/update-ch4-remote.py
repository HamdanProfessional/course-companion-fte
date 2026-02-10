import psycopg2

conn = psycopg2.connect(
    host="ep-silent-darkness-a19lc6fn-pooler.ap-southeast-1.aws.neon.tech",
    database="neondb",
    user="neondb_owner",
    password="npg_4ejWEylrw0MH",
    sslmode="require"
)
c = conn.cursor()

content = """# Building Reusable Skills: The Art of AI Capability Design

The evolution from building isolated AI features to creating sophisticated, multi-capability assistants represents one of the most important transitions in modern AI development. This transformation is powered by skills - modular, reusable units of AI capability that can be combined and orchestrated to create assistants that are far more capable than any single feature could be on its own. Understanding how to design, build, and compose skills is what separates developers who can build simple demos from those who can create production-ready AI applications.

A skill in the context of AI development is more than just a prompt or a function call. It's a complete package that encompasses the knowledge, instructions, and tools needed to perform a specific task reliably. Think of a skill as a well-trained expert consultant who you can bring into a conversation when their expertise is needed. This expert knows their domain deeply, has practiced explaining complex concepts clearly, and knows how to work collaboratively with others to achieve a larger goal. When you build skills well, you're creating these experts and teaching your AI assistant how to deploy them effectively.

## The Anatomy of a Well-Designed Skill

Every skill begins with a clearly defined purpose. Before you write a single line of code or craft a single prompt, you should be able to articulate exactly what your skill does, when it should be used, and what success looks like. This clarity of purpose is what distinguishes useful skills from generic, ineffective ones. A skill for explaining concepts, for example, has a different purpose than a skill for conducting quizzes, and both differ from a skill for tracking progress. Understanding these distinctions is the first step in building skills that actually work.

Once you've defined your skill's purpose, you need to think about its interface - how other parts of your system will interact with it. A good skill has a clean, well-defined interface that makes its capabilities clear without exposing unnecessary complexity. This includes the triggers that cause the skill to activate, the parameters it needs to do its work, and the outputs it produces. The interface is your skill's contract with the world, and designing it carefully is essential for creating skills that can be composed into larger systems.

Beneath the interface lies the skill's implementation - the prompts, logic, and tool calls that make the skill actually work. This is where the art of skill design really shines through. A well-implemented skill doesn't just perform its function; it does so reliably, handle edge cases gracefully, and provides helpful feedback when things go wrong. The difference between a fragile skill that works sometimes and a robust skill that works consistently comes down to the thought and care put into the implementation.

## The Skill Manifesto: Structuring Your AI Expertise

Every skill needs a manifesto - a document that describes its purpose, capabilities, and usage patterns. This isn't just documentation; it's the authoritative source of truth about what your skill does and how it should be used. When you're building skills for the Course Companion FTE system, for example, each skill has a dedicated markdown file that serves as its manifesto, describing everything from when the skill should be invoked to what outputs it should produce.

The skill manifesto serves multiple audiences. For developers, it's documentation that explains how to integrate and use the skill. For the AI system itself, it's often used as part of the prompt that tells the model how to invoke the skill appropriately. For users, it provides transparency about what the skill can do and what limitations it has. A well-written manifesto aligns all these perspectives, creating shared understanding that prevents miscommunication and misuse.

What goes into a good skill manifesto? Start with a clear description of the skill's purpose - what problem does it solve and why does it exist? Then move to usage patterns - when should this skill be invoked and what signals indicate it's the right time to use it? Document the skill's inputs and outputs clearly, including any optional parameters and what they control. Finally, describe any limitations or edge cases that developers and users should be aware of. This completeness is what transforms a simple description into a useful manifesto.

## Four Pillars of Educational AI Skills

In the context of building educational AI assistants, four core skill categories emerge again and again: explanation, assessment, guidance, and motivation. Each of these represents a fundamental way that AI can support learning, and understanding how to build skills in each category is essential for creating comprehensive educational experiences.

The concept explainer skill is perhaps the most fundamental - it's about taking complex ideas and making them accessible to learners at various levels. A good explanation skill doesn't just simplify content; it adapts its approach based on the learner's existing knowledge, uses analogies and examples to build intuition, and progressively increases complexity as understanding grows. Building this skill means understanding how people learn, what makes explanations effective, and how to structure information for maximum clarity.

The quiz master skill represents the assessment pillar - the ability to test understanding and provide feedback. But good assessment is about more than just asking questions and checking answers. An effective quiz skill encourages learners, celebrates effort even when answers are wrong, and uses mistakes as learning opportunities rather than failures. It understands psychology and motivation, recognizing that how feedback is delivered matters just as much as what the feedback says.

The socratic tutor skill embodies the guidance pillar - helping learners work through problems themselves rather than simply giving them answers. This is one of the more challenging skills to build effectively because it requires resisting the urge to provide direct solutions. Instead, the skill must ask carefully crafted questions that guide learners toward insights, allowing them to experience the satisfaction of discovery while ensuring they don't get stuck or frustrated.

The progress motivator skill addresses the motivation pillar - the emotional and psychological aspects of learning that are often overlooked but critically important. Learning is hard work, and maintaining motivation over time requires celebration of progress, recognition of effort, and support during setbacks. This skill tracks accomplishments, highlights growth, and helps learners see how far they've come even when the path ahead seems long.

## Design Patterns for Composable Skills

As you build more skills, you'll start to recognize patterns that make skills easier to compose and orchestrate. These design patterns emerge from experience and represent proven solutions to common problems in skill design. Understanding these patterns lets you build skills that fit together naturally, creating larger capabilities from smaller, focused components.

One fundamental pattern is the single responsibility principle - each skill should do one thing well. A skill that tries to do too much becomes difficult to use, hard to test, and prone to failure. By keeping skills focused, you make them easier to understand, easier to maintain, and easier to combine in novel ways. The four educational skills we discussed each have a clear, single purpose, and this clarity is what makes them work well together.

Another important pattern is clear interfaces with minimal coupling. Skills should communicate through well-defined inputs and outputs rather than sharing state or depending on each other's internals. This loose coupling means you can modify or replace individual skills without affecting others, making your system more maintainable and allowing for incremental improvement. When skills are tightly coupled, changes ripple through the system in unpredictable ways, creating fragility and making evolution difficult.

The declarative configuration pattern is particularly powerful for AI skills. Instead of hardcoding behavior, structure your skills so that key behaviors can be configured through external parameters. This might include difficulty levels, subject domains, or pedagogical approaches. Configuration makes your skills more flexible without requiring code changes, enabling adaptation to different contexts without redevelopment.
"""

c.execute("UPDATE chapters SET content = %s WHERE id = %s RETURNING title", (content, "56aa5028-8ddd-4e21-b00a-e935147079cc"))
r = c.fetchone()
print("Chapter 4 Updated:", r[0] if r else "Not found", "-", len(content), "chars")
conn.commit()
c.close()
conn.close()
