#!/usr/bin/env python3
import asyncio
from sqlalchemy import update
from src.core.database import async_session_maker
from src.models.database import Chapter

CHAPTER_2 = """# Understanding MCP (Model Context Protocol)

## Overview

The Model Context Protocol (MCP) is an open standard that enables AI models to securely connect to external data sources and tools. It provides a unified interface for AI agents to access diverse systems, from file systems to databases to web APIs.

## What is MCP?

MCP bridges the gap between AI models and the real world by providing standardized interfaces, security boundaries, type safety, and extensibility.

Standardized interfaces allow any AI model to connect to any data source without custom integration code. Security boundaries give you fine-grained control over what data the AI can access. Type safety means predictable interactions through JSON Schema validation. Extensibility makes it easy to add new capabilities.

## Key Concepts

### Servers

MCP servers expose resources and tools to AI clients. A server can represent anything: a file system, a database, an API, or even a custom application. Think of servers as the bridge between your data and the AI agent.

Servers host data and tools for AI agents, provide type-safe interfaces through schemas, handle authentication and authorization, and manage access control and permissions.

Server types include File System Servers for reading and writing files, Database Servers for querying databases, API Servers for connecting to external services, Memory Servers for storing conversation context, and Tool Servers for executing specific functions.

### Resources

Resources are data sources that AI can read. They represent the data layer of MCP - the information your agent needs to do its job. Resources include files containing text, code, documents, or images, database records providing structured data, API responses delivering real-time data, memory storing conversation context, and configurations holding settings.

Resources have URIs that uniquely identify them. When an agent wants to access a resource, it requests the resource by URI. The server validates the request, checks permissions, and returns the resource data.

### Tools

Tools are actions that AI can execute. While resources are for reading data, tools are for taking action. Common tool types include File Operations for reading, writing, and searching files, Code Execution for running programs, API Calls for invoking web services, Database Queries for performing SQL operations, and Data Processing for transforming and analyzing data.

Tools have input schemas that define what parameters they accept. When an agent calls a tool, it must provide valid arguments according to this schema.

### Prompts

Prompts are reusable instruction templates that standardize how your agent handles certain tasks. Instead of repeating the same instructions in every conversation, you define prompt templates once and reuse them across all interactions.

Prompt templates provide consistency across agent interactions, reduce token usage, make maintenance easier, and improve agent behavior through tested, validated prompts.

## What is Next?

Understanding MCP is fundamental to building AI agents. In the next chapter, you will create your first agent from scratch, putting this knowledge into practice.
"""

async def update():
    async with async_session_maker() as session:
        result = await session.execute(
            update(Chapter).where(Chapter.order == 2).values(content=CHAPTER_2)
        )
        await session.commit()
        print(f"Chapter 2 updated: {result.rowcount} row(s)")

if __name__ == "__main__":
    asyncio.run(update())
