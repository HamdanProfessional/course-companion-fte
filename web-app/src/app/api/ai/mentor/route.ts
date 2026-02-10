/**
 * AI Mentor API Route
 *
 * Next.js API route that proxies requests to the backend AI Mentor endpoint.
 * Integrates with Vercel AI SDK for useChat hook compatibility.
 */

import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://92.113.147.250:3505';

// Allow streaming responses up to 30 seconds
export const maxDuration = 30;

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { messages, user_id } = body;

    // Get user ID from request body or header
    const userId = user_id || req.headers.get('x-user-id') || '82b8b862-059a-416a-9ef4-e582a4870efa';

    // Get the latest message from the messages array
    const lastMessage = messages?.[messages.length - 1];
    const question = lastMessage?.content || body.question || '';

    if (!question) {
      return NextResponse.json(
        { error: 'Question is required' },
        { status: 400 }
      );
    }

    // Build conversation history from messages array
    const history = messages?.slice(0, -1).map((msg: any) => ({
      role: msg.role,
      content: msg.content,
      timestamp: msg.createdAt || new Date().toISOString(),
    })) || [];

    // Build query params with user_id
    const params = new URLSearchParams({ user_id: userId });

    // Call the backend API directly
    const url = `${BACKEND_URL}/api/v3/tutor/ai/mentor/chat?${params}`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        conversation_history: history,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    const data = await response.json();

    // Return the response in AI SDK format
    return NextResponse.json({
      id: `msg-${Date.now()}`,
      role: 'assistant',
      content: data.answer || 'No response from mentor.',
      createdAt: new Date().toISOString(),
    });

  } catch (error) {
    console.error('AI Mentor API error:', error);
    return NextResponse.json(
      {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again or contact support if the issue persists.',
        createdAt: new Date().toISOString(),
      },
      { status: 500 }
    );
  }
}
