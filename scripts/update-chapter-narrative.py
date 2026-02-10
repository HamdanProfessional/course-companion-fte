#!/usr/bin/env python3
"""
Update Chapters 2 and 4 with narrative, book-style content.

This script updates the database with flowing prose content for:
- Chapter 2: Understanding MCP
- Chapter 4: Building Reusable Skills

The content is written in a narrative, storytelling style rather than bullet points.
"""

import uuid

from sqlalchemy import (
    Column,
    String,
    Integer,
    Text,
    ForeignKey,
    JSON,
    Index,
    select, update,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base


# =============================================================================
# DATABASE CONNECTION - Using psycopg2 directly
# =============================================================================

import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection string
DB_HOST = "ep-silenced-water-a1b9fb1f.us-east-1.aws.neon.tech"
DB_NAME = "neondb"
DB_USER = "neondb_owner"
DB_PASSWORD = "WF65QULoapY"

# Connection parameters with SSL
conn_params = {
    "host": DB_HOST,
    "database": DB_NAME,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "sslmode": "require",
    "connect_timeout": 10
}

# =============================================================================
# CHAPTER 2: UNDERSTANDING MCP - NARRATIVE CONTENT
# =============================================================================

CHAPTER_2_CONTENT = """# Understanding MCP: The Bridge Between AI and Your Data

The journey into building intelligent assistants begins with understanding how AI models interact with the world around them. As powerful as Large Language Models like GPT-4 and Claude have become, they exist in a confined space - limited to their training data and whatever information you provide in a conversation. This is where the Model Context Protocol (MCP) enters the story, serving as a crucial bridge that connects AI assistants to the vast ecosystem of tools, databases, and services that power modern applications.

Imagine for a moment that an AI assistant is like a brilliant researcher locked in a library. This researcher has read nearly every book in existence and can synthesize information in remarkable ways, but they cannot step outside the library's doors. They cannot check current stock prices, query your company's internal database, or interact with live APIs. They can tell you about the weather in abstract terms, but they cannot tell you whether it's currently raining in your specific location. MCP is the doorway that lets this researcher step out of the library and engage with the real world.

## The Foundation: Why We Need Context Protocols

The story of MCP begins with a fundamental problem in AI development: the context window limitation. Every AI model has a finite amount of information it can process in a single conversation. When you're building applications that need to work with large datasets, codebases, or real-time information, this limitation becomes a significant bottleneck. You cannot simply copy-paste an entire database into every conversation, nor can you expect users to continually provide the same contextual information over and over again.

Before protocols like MCP existed, developers had to build custom integrations for every AI application. If you wanted an AI assistant that could query your database, you had to build a specific API endpoint, handle authentication, manage rate limiting, and create a custom prompt format to instruct the AI on how to use that endpoint. If you then wanted to add file system access, you'd repeat the entire process. Each integration was a bespoke solution, making AI applications difficult to build, maintain, and scale.

MCP emerged from the recognition that this problem needed a standardized solution. Instead of every developer building their own custom bridges between AI and data, what if there was a universal protocol - a common language that both AI assistants and data sources could understand? This is the core insight behind MCP: it provides a standardized way for AI models to request information and for servers to provide it, regardless of what that information is or where it lives.

## How MCP Works: The Client-Server Architecture

At its heart, MCP operates on a simple but powerful client-server architecture. The AI assistant acts as the client, making requests for information or actions. MCP servers act as the providers, exposing specific capabilities that the AI can utilize. These servers can run anywhere - on your local machine, in the cloud, or even within edge computing environments. They can connect to databases, file systems, APIs, or any other data source you can imagine.

What makes MCP particularly elegant is its unified interface. From the AI assistant's perspective, it doesn't matter whether it's talking to a PostgreSQL database, a GraphQL API, or the local file system. The protocol abstracts these differences away, presenting a consistent set of tools and resources that the AI can use. This abstraction is what makes MCP so powerful for building AI applications: you can swap out backend implementations without changing how your AI assistant interacts with them.

The communication flow in MCP follows a predictable pattern. When a user asks the AI assistant something that requires external data, the assistant formulates a request through the MCP protocol. This request travels to the appropriate MCP server, which processes it and returns the requested information. The AI assistant then incorporates this information into its response, all of which happens transparently to the user. What the user experiences is a seamless conversation where the AI seems to have access to all sorts of relevant information.

## Resources and Tools: The Building Blocks of MCP

MCP exposes two primary types of capabilities: resources and tools. Understanding the distinction between them is key to effectively using the protocol.

Resources are exactly what they sound like - sources of information that the AI can read from. A resource might be a collection of files from a directory, the results of a database query, or the current state of a system resource. Resources are primarily about data retrieval, giving the AI assistant access to information it needs to answer questions or perform tasks. When you think of resources, think of read operations - getting data into the AI's context so it can work with it.

Tools, on the other hand, are callable functions that can perform actions. While resources let the AI read information, tools let the AI do things. A tool might execute a SQL query, write a file, make an API call, or perform any other action that changes state or computes new information. Tools extend the AI's capabilities beyond just answering questions - they enable the AI to take action on behalf of the user, making it a true assistant rather than just a conversational interface.

The beauty of this division is that it maps naturally to how we think about software systems. We have data (resources) and we have operations (tools). MCP provides a standardized way to expose both to AI assistants, making it possible to build rich, interactive applications that combine the reasoning capabilities of LLMs with the full power of traditional software systems.

## The Anthropic Ecosystem: Where MCP Lives

MCP was developed by Anthropic as part of their broader vision for AI assistants that can safely and effectively interact with external systems. Within the Anthropic ecosystem, MCP serves as the backbone for how Claude and other AI assistants connect to the world of data and services beyond their training. This isn't just a theoretical protocol - it's actively being used to power real AI applications.

What makes MCP particularly interesting is that it's designed to be model-agnostic. While Anthropic developed it for use with Claude, the protocol itself doesn't depend on any specific AI model. You could just as easily use it with OpenAI's GPT models, open-source models, or any future AI system. This forward-thinking design means that investments you make in building MCP servers today will continue to pay off as AI technology continues to evolve.

For developers working with Claude, MCP integrates seamlessly with the Anthropic API and the Claude desktop application. This integration means you can build AI assistants that leverage MCP without having to build the entire infrastructure yourself. You simply create your MCP servers, register them with the Claude ecosystem, and suddenly your AI assistant has access to whatever capabilities you've exposed.

## Practical Implementation: Building Your First MCP Server

Understanding MCP conceptually is important, but the real learning happens when you start building. The process of creating an MCP server begins with defining what capabilities you want to expose. Are you building a server that provides access to a database? One that interacts with external APIs? Or perhaps a server that makes file system operations available to your AI assistant?

Once you've defined your server's purpose, the implementation follows a standard pattern. You'll define resources that expose your data, tools that provide actions on that data, and the logic that connects these to your actual backend systems. The MCP SDKs handle the protocol details - you simply implement the interfaces and register your capabilities. The framework takes care of serialization, error handling, and all the other infrastructure concerns that typically make building integrations difficult.

What makes this process particularly pleasant is that MCP servers can be developed in any language. While Python is a popular choice due to its rich ecosystem, you could just as easily build an MCP server in TypeScript, Go, Rust, or any language that can handle HTTP or WebSocket connections. This flexibility means you can use the right tool for the job rather than being forced into a specific technology stack.

## Security and Governance: Protecting Your Systems

As you might imagine, giving AI assistants the ability to interact with your systems comes with security considerations. MCP was designed with these concerns from the start, incorporating several layers of protection to ensure that AI assistants can only access what they should be allowed to access.

The first line of defense is authentication. MCP servers can require authentication tokens, API keys, or any other credential mechanism you prefer. This means you control exactly who can connect to your servers and what they can do once connected. You might have different authentication requirements for different servers - perhaps your public-facing content server requires no authentication, while your database manipulation server requires multi-factor authentication.

Beyond authentication, MCP provides fine-grained permission controls. You can specify exactly which resources and tools each authenticated client has access to, ensuring that even if credentials are compromised, the blast radius is limited. You might give a particular AI assistant read-only access to certain resources while completely blocking access to others. This principle of least privilege is built into the protocol's design.

Auditing is another critical security feature. Every request made through MCP can be logged, creating a comprehensive audit trail of exactly what your AI assistants are doing. This is invaluable not just for security monitoring, but also for understanding how your systems are being used and identifying opportunities for optimization.

## Looking Ahead: The Future of MCP

As we look toward the future of AI development, protocols like MCP will become increasingly important. The pattern they represent - AI models as reasoning engines that orchestrate calls to specialized systems - is rapidly becoming the dominant paradigm for building AI applications. Understanding MCP today positions you to take advantage of this evolution as it continues to unfold.

We're already seeing MCP servers being created for an incredible variety of use cases. Database connectivity servers, file system servers, API integration servers, and even specialized servers for things like code analysis, documentation generation, and system monitoring. The ecosystem is growing rapidly, with new servers and capabilities being added all the time. This momentum suggests that MCP is becoming a de facto standard for AI-database integration, much like SQL became the standard for database queries.

For developers, this represents an opportunity. By building expertise in MCP today, you're positioning yourself at the forefront of AI application development. The skills you learn building MCP servers - understanding how to structure data for AI consumption, how to design effective tools, how to think about AI-systems integration - these will be valuable regardless of how the underlying technology evolves.

## Conclusion: MCP as a Foundation for AI Innovation

Understanding MCP is more than just learning a protocol - it's about embracing a new way of thinking about AI applications. Instead of building monolithic systems that try to cram every capability into the AI model itself, we're moving toward an architecture where AI models serve as intelligent orchestrators, coordinating calls to specialized systems that each excel at what they do. This architecture is more scalable, more maintainable, and ultimately more powerful than trying to build everything into a single system.

MCP provides the foundation for this architecture. It gives us a standardized way to connect AI assistants to the world of data and services, enabling a new generation of applications that combine the reasoning capabilities of LLMs with the full power of modern software systems. Whether you're building an AI tutor, a code assistant, a data analyst, or something entirely new, MCP gives you the tools you need to make your AI assistant truly useful.

As you continue your journey through this course, you'll build on this foundation, creating your own MCP servers and learning how to integrate them into sophisticated AI applications. The concepts you've learned here - resources, tools, client-server architecture, security - these will be your constant companions. Master them now, and you'll be well-equipped to build the next generation of AI-powered software.
"""


# =============================================================================
# CHAPTER 4: BUILDING REUSABLE SKILLS - NARRATIVE CONTENT
# =============================================================================

CHAPTER_4_CONTENT = """# Building Reusable Skills: The Art of AI Capability Design

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

## Testing and Iteration: Making Skills Reliable

Building skills is an iterative process. Your first version will rarely be your best version, and embracing this reality is essential for creating high-quality capabilities. A disciplined approach to testing and iteration is what transforms initial prototypes into production-ready skills that can be trusted in real applications.

Testing AI skills requires a different mindset than testing traditional software. You're not just checking for correct outputs - you're evaluating quality, appropriateness, and effectiveness. This often means manual testing and review, observing how the skill performs across a variety of scenarios and edge cases. You'll want to test with different types of content, different user scenarios, and different combinations of inputs to ensure robustness.

Iterating based on testing feedback is where real improvement happens. Each round of testing should generate specific, actionable insights about how to improve the skill. Maybe the explanation isn't adapting enough to different knowledge levels. Perhaps the quiz feedback is too discouraging. Or the guidance questions are too leading. These observations drive refinements to prompts, parameters, and logic, gradually improving the skill's effectiveness.

Documentation emerges naturally from this iterative process. As you discover edge cases and refine behaviors, document what you've learned. This documentation becomes invaluable for future maintenance and for other developers who need to understand or extend your skills. A well-documented skill is one that can be maintained, improved, and trusted over time.

## Orchestration: Bringing Skills Together

Individual skills are powerful, but the real magic happens when you orchestrate them together, creating assistants that can handle complex, multi-step interactions. Orchestration is the art of determining which skills to invoke when, in what order, and how to pass information between them to achieve a larger goal.

The simplest orchestration pattern is sequential invocation - one skill completes its work, and then the next skill begins. This works well for straightforward workflows where each step has a clear prerequisite. A student might first have a concept explained, then take a quiz to test understanding, and finally receive motivation based on their performance. Each skill activates in turn, building on what came before.

More sophisticated orchestration involves conditional logic and branching. The path through skills might depend on the student's performance, their stated preferences, or other contextual factors. A student who struggles with a quiz might receive additional explanation before attempting another assessment. This adaptive orchestration creates personalized experiences that respond to individual needs rather than following a one-size-fits-all script.

The most advanced orchestration patterns involve parallel processing and composition, where multiple skills might contribute simultaneously to a complex response. The AI assistant might combine explanation, examples, and assessment all in a single interaction, drawing on multiple skills to provide comprehensive support. Mastering these orchestration patterns is what enables truly sophisticated AI applications.

## Scale and Evolution: Growing Your Skill Library

As you build more skills, you'll face challenges of scale and organization. A handful of skills is easy to manage, but as your library grows into the dozens or hundreds, you'll need systems for organization, discovery, and maintenance. Planning for this growth from the beginning prevents pain down the road.

Organization starts with a clear structure. Skills should be organized in a predictable directory structure, with consistent naming conventions and clear relationships. Related skills might be grouped together, with shared utilities and common patterns extracted into reusable components. This organization makes the skill library navigable and helps new developers understand the architecture.

Discovery is about finding the right skill for the job. As your skill library grows, you'll need good search and discovery mechanisms. This might include tagging skills with metadata, maintaining a catalog with descriptions and usage examples, or even building an AI-powered skill recommender that can suggest which skills to use for a given task. Good discovery mechanisms prevent reinvention and promote reuse.

Maintenance is the ongoing work of keeping skills relevant and effective. As AI models evolve, as your understanding of user needs deepens, and as the context around your application changes, skills will need updates. Having clear processes for maintenance - regular reviews, update procedures, deprecation policies - keeps your skill library healthy and prevents it from becoming a legacy burden.

## The Future of Skill Development

The patterns and practices we've discussed represent the current state of skill development, but this field continues to evolve rapidly. As AI capabilities improve and as we learn more about what works in production, new patterns and best practices will emerge. Staying engaged with the community, experimenting with new approaches, and sharing what you learn will keep you at the forefront of this evolving discipline.

We're already seeing the emergence of skill marketplaces and frameworks that make it easier to share and compose skills across projects and organizations. The future likely holds more sophisticated tools for skill development, better testing and validation frameworks, and richer orchestration capabilities. The skills you build today will continue to benefit from these advances, creating a compounding return on your investment in learning this craft.

What remains constant, even as technology evolves, are the fundamental principles we've discussed: clarity of purpose, clean interfaces, thorough testing, and thoughtful orchestration. These principles transcend specific implementations and will guide you in building effective skills regardless of how the underlying technology changes.

## Conclusion: Skills as Building Blocks for AI Innovation

Building reusable skills is more than a development practice - it's a mindset that shapes how you think about AI applications. Instead of building monolithic systems that try to do everything, you're creating modular components that can be combined in endless ways. This modularity is what enables innovation, as developers can remix and recombine skills to create new capabilities without starting from scratch.

As you continue your journey in AI development, the skills you build and the patterns you master will become your toolkit for creating sophisticated applications. Whether you're building educational tutors, coding assistants, data analysts, or something entirely new, the ability to design, implement, and orchestrate skills will be fundamental to your success.

The four educational skills we've explored - explanation, assessment, guidance, and motivation - are just the beginning. As you identify new needs and discover new patterns, you'll expand your skill library, creating ever more capable AI assistants. This is the future of AI development: not building monolithic systems, but composing elegant solutions from well-designed, thoroughly-tested skills. Master this craft, and you'll be prepared to build whatever comes next.
"""


# =============================================================================
# UPDATE FUNCTION
# =============================================================================

def update_chapters():
    """Update Chapter 2 and Chapter 4 with narrative content."""

    print("=" * 60)
    print("Chapter Content Update Script")
    print("=" * 60)
    print("\nUpdating chapters with narrative, book-style content...\n")

    # Chapter IDs
    chapter_2_id = "4d595b4d-ac38-4a35-9699-265009f430e9"
    chapter_4_id = "56aa5028-8ddd-4e21-b00a-e935147079cc"

    conn = None
    try:
        # Connect to database
        print("Connecting to database...")
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()

        # Update Chapter 2
        print("Updating Chapter 2: Understanding MCP...")
        cursor.execute(
            """
            UPDATE chapters
            SET content = %s
            WHERE id = %s
            RETURNING title
            """,
            (CHAPTER_2_CONTENT, chapter_2_id)
        )
        result = cursor.fetchone()
        if result:
            print(f"  Updated: {result[0]}")
        else:
            print(f"  WARNING: Chapter 2 not found with ID: {chapter_2_id}")

        # Update Chapter 4
        print("Updating Chapter 4: Building Reusable Skills...")
        cursor.execute(
            """
            UPDATE chapters
            SET content = %s
            WHERE id = %s
            RETURNING title
            """,
            (CHAPTER_4_CONTENT, chapter_4_id)
        )
        result = cursor.fetchone()
        if result:
            print(f"  Updated: {result[0]}")
        else:
            print(f"  WARNING: Chapter 4 not found with ID: {chapter_4_id}")

        # Commit the changes
        conn.commit()
        print("\nSuccessfully updated both chapters with narrative content!")

        # Verify the updates
        print("\n" + "-" * 40)
        print("Verification")
        print("-" * 40)

        for ch_id, ch_name in [(chapter_2_id, "Chapter 2"), (chapter_4_id, "Chapter 4")]:
            cursor.execute(
                """
                SELECT title, content
                FROM chapters
                WHERE id = %s
                """,
                (ch_id,)
            )
            result = cursor.fetchone()
            if result:
                title, content = result
                word_count = len(content.split()) if content else 0
                char_count = len(content) if content else 0
                paragraph_count = len([p for p in (content or "").split("\n\n") if p.strip()])
                print(f"\n{ch_name}: {title}")
                print(f"  - Words: {word_count:,}")
                print(f"  - Characters: {char_count:,}")
                print(f"  - Paragraphs: {paragraph_count}")
            else:
                print(f"\n{ch_name}: NOT FOUND")

        cursor.close()

    except psycopg2.Error as e:
        print(f"\nDatabase error: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            print("\nDatabase connection closed.")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    update_chapters()
