'use client';

/**
 * AI Mentor Page - Phase 3
 *
 * Interactive AI tutor for conceptual Q&A:
 * - Ask questions about course content
 * - Get detailed explanations
 * - Receive follow-up questions
 * - Explore related topics
 */

import { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingSpinner } from '@/components/ui/Loading';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import { useV3MentorChat, useV3AIStatus } from '@/hooks/useV3';
import { useUserTier } from '@/hooks';
import type { MentorMessage } from '@/lib/api-v3';

// Suggested questions to help users get started
const SUGGESTED_QUESTIONS = [
  "How do MCP servers connect to ChatGPT?",
  "What's the difference between a skill and an agent?",
  "Explain state management in React Query",
  "How do I implement adaptive learning?",
];

export default function AIMentorPage() {
  const [messages, setMessages] = useState<MentorMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [authError, setAuthError] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Get user tier
  const { data: tier, isLoading: tierLoading } = useUserTier();
  const { data: aiStatus } = useV3AIStatus();
  const mentorChat = useV3MentorChat();

  // Check if user can access AI features (PREMIUM or PRO tier)
  // Default to allow if tier is still loading (FREE tier doesn't block anymore since we have LLM)
  const canAccessAI = (!tierLoading && tier && tier === 'FREE') ? false : true;

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    // Check if user is logged in
    const userId = localStorage.getItem('user_id');
    if (!userId) {
      setAuthError(true);
      // Auto-redirect to login after showing error
      setTimeout(() => {
        window.location.href = '/login';
      }, 2000);
      return;
    }

    const userMessage: MentorMessage = {
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setAuthError(false);

    try {
      const response = await mentorChat.mutateAsync({
        question: userMessage.content,
        conversation_history: messages,
      });

      const assistantMessage: MentorMessage = {
        role: 'assistant',
        content: response.answer,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('AI Mentor error:', error);
      const errorMessage: MentorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again or contact support if the issue persists.',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSuggestedQuestion = (question: string) => {
    setInputValue(question);
  };

  const handleClearChat = () => {
    setMessages([]);
  };

  if (!canAccessAI && aiStatus) {
    return (
      <PageContainer>
        <Card>
          <CardContent className="p-8 text-center">
            <div className="text-5xl mb-4">🤖</div>
            <h2 className="text-2xl font-bold mb-2">Premium Feature</h2>
            <p className="text-text-secondary mb-6 max-w-md mx-auto">
              Unlock AI-powered mentoring with 24/7 access to personalized tutoring and
              conceptual explanations.
            </p>
            <Button variant="primary">Upgrade to Premium</Button>
          </CardContent>
        </Card>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      {/* Page Header */}
      <PageHeader
        title="AI Mentor"
        description="Ask questions and get personalized explanations from your AI tutor"
      />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Chat Area */}
        <div className="lg:col-span-3">
          <Card className="h-[600px] flex flex-col">
            <CardHeader className="border-b border-border-default">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-3">
                  <span className="text-2xl">🤖</span>
                  AI Tutor
                </CardTitle>
                {messages.length > 0 && (
                  <Button variant="outline" size="sm" onClick={handleClearChat}>
                    Clear Chat
                  </Button>
                )}
              </div>
            </CardHeader>

            <CardContent className="flex-1 flex flex-col p-0">
              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.length === 0 ? (
                  /* Welcome State */
                  <div className="h-full flex flex-col items-center justify-center text-center">
                    <div className="text-6xl mb-4">👋</div>
                    <h3 className="text-xl font-semibold text-text-primary mb-2">
                      Welcome to AI Mentor!
                    </h3>
                    <p className="text-text-secondary max-w-md mb-6">
                      Ask me anything about the course material. I'm here to help you understand
                      concepts, answer questions, and guide your learning journey.
                    </p>
                    <div className="text-sm text-text-muted">
                      <span className="inline-block px-3 py-1 rounded-full bg-bg-elevated">
                        Powered by {aiStatus?.llm_provider?.toUpperCase() || 'AI'}
                      </span>
                    </div>
                  </div>
                ) : (
                  /* Messages */
                  <div className="space-y-4">
                    {messages.map((message, index) => (
                      <div
                        key={index}
                        className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-[80%] rounded-lg px-4 py-3 ${
                            message.role === 'user'
                              ? 'bg-accent-primary text-white'
                              : 'bg-bg-elevated text-text-primary'
                          }`}
                        >
                          <div className="flex items-start gap-2">
                            {message.role === 'assistant' && (
                              <span className="text-lg">🤖</span>
                            )}
                            <div className="flex-1">
                              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                              {message.timestamp && (
                                <p
                                  className={`text-xs mt-2 ${
                                    message.role === 'user'
                                      ? 'text-white/70'
                                      : 'text-text-muted'
                                  }`}
                                >
                                  {new Date(message.timestamp).toLocaleTimeString()}
                                </p>
                              )}
                            </div>
                            {message.role === 'user' && (
                              <span className="text-lg">👤</span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                    {isLoading && (
                      <div className="flex justify-start">
                        <div className="bg-bg-elevated rounded-lg px-4 py-3 flex items-center gap-2">
                          <LoadingSpinner size="sm" />
                          <span className="text-sm text-text-muted">Thinking...</span>
                        </div>
                      </div>
                    )}
                    <div ref={messagesEndRef} />
                  </div>
                )}
              </div>

              {/* Input Area */}
              <div className="border-t border-border-default p-4">
                {authError && (
                  <div className="mb-4 p-3 rounded-lg bg-accent-warning/10 border border-accent-warning/30">
                    <p className="text-sm text-accent-warning">
                      ⚠️ You need to be logged in to use AI Mentor. Redirecting to login...
                    </p>
                  </div>
                )}
                <div className="flex gap-3">
                  <textarea
                    value={inputValue}
                    onChange={e => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask a question about the course..."
                    className="flex-1 px-4 py-3 rounded-lg border border-border-default bg-bg-elevated text-text-primary placeholder:text-text-muted resize-none focus:outline-none focus:ring-2 focus:ring-accent-primary"
                    rows={2}
                    disabled={isLoading}
                  />
                  <Button
                    variant="primary"
                    onClick={handleSendMessage}
                    disabled={!inputValue.trim() || isLoading}
                    className="self-end"
                  >
                    Send
                  </Button>
                </div>
                <p className="text-xs text-text-muted mt-2">
                  Press Enter to send, Shift+Enter for new line
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          {/* Suggested Questions */}
          {messages.length === 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Suggested Questions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {SUGGESTED_QUESTIONS.map((question, i) => (
                  <button
                    key={i}
                    onClick={() => handleSuggestedQuestion(question)}
                    className="w-full text-left p-3 rounded-lg bg-bg-elevated hover:bg-bg-hover transition-colors text-sm"
                  >
                    {question}
                  </button>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Tips */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <span>💡</span>
                Tips
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-text-secondary">
              <p>• Be specific with your questions</p>
              <p>• Reference chapters when relevant</p>
              <p>• Ask follow-up questions</p>
              <p>• Use examples for clarity</p>
            </CardContent>
          </Card>

          {/* Status */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <span>⚡</span>
                AI Status
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-text-secondary">Provider</span>
                <Badge variant="info">{aiStatus?.llm_provider || 'AI'}</Badge>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-text-secondary">Status</span>
                <Badge variant="success">Online</Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </PageContainer>
  );
}
