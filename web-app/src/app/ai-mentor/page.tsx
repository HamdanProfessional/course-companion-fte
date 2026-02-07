'use client';

/**
 * AI Mentor Page - Phase 3
 *
 * Interactive AI tutor for conceptual Q&A:
 * - Ask questions about course content
 * - Get detailed explanations
 * - Receive follow-up questions
 * - Explore related topics
 * - Voice Mode: Two-way voice conversations
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
import { Bot, User as UserIcon, Sparkles, Lightbulb, Zap, AlertTriangle, Mic, MicOff, Volume2, VolumeX } from 'lucide-react';

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

  // Voice Mode State
  const [isVoiceMode, setIsVoiceMode] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const recognitionRef = useRef<any>(null);
  const synthesisRef = useRef<SpeechSynthesisUtterance | null>(null);

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

  // Voice Mode Functions
  const toggleVoiceMode = () => {
    if (!isVoiceMode && !voiceEnabled) {
      // Check for browser support
      if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert('Speech recognition is not supported in your browser. Please use Chrome, Edge, or Safari.');
        return;
      }
      if (!('speechSynthesis' in window)) {
        alert('Text-to-speech is not supported in your browser.');
        return;
      }
    }
    setIsVoiceMode(!isVoiceMode);
  };

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  const startListening = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert('Speech recognition is not supported in your browser.');
      return;
    }

    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;

    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    let finalTranscript = '';

    recognition.onresult = (event: any) => {
      let interimTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        } else {
          interimTranscript += transcript;
        }
      }

      setInputValue(finalTranscript || interimTranscript);
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
      if (event.error === 'not-allowed') {
        alert('Microphone permission denied. Please allow microphone access to use voice mode.');
      }
    };

    recognition.onend = () => {
      setIsListening(false);
      if (finalTranscript) {
        setInputValue(finalTranscript);
        // Auto-send after listening completes
        setTimeout(() => {
          handleSendMessage();
        }, 500);
      }
    };

    recognition.start();
    setIsListening(true);
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  const speakText = (text: string) => {
    if (!voiceEnabled || !('speechSynthesis' in window)) return;

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    synthesisRef.current = utterance;

    // Select a natural sounding voice
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(voice =>
      voice.lang.startsWith('en') && voice.name.includes('Google') || voice.name.includes('Natural')
    ) || voices.find(voice => voice.lang.startsWith('en')) || voices[0];

    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }

    utterance.rate = 0.9; // Slightly slower for better comprehension
    utterance.pitch = 1;
    utterance.volume = 1;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utterance);
  };

  const stopSpeaking = () => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  };

  const toggleSpeechEnabled = () => {
    setVoiceEnabled(!voiceEnabled);
    if (isSpeaking) {
      stopSpeaking();
    }
  };

  // Auto-speak AI responses when voice mode is enabled
  useEffect(() => {
    if (isVoiceMode && voiceEnabled && messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.role === 'assistant' && !isSpeaking) {
        speakText(lastMessage.content);
      }
    }
  }, [messages, isVoiceMode, voiceEnabled]);

  // Load voices when component mounts
  useEffect(() => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.getVoices();
      const handleVoicesChanged = () => {
        window.speechSynthesis.getVoices();
      };
      window.speechSynthesis.onvoiceschanged = handleVoicesChanged;
    }

    // Cleanup on unmount
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      window.speechSynthesis.cancel();
    };
  }, []);

  if (!canAccessAI && aiStatus) {
    return (
      <PageContainer>
        <Card>
          <CardContent className="p-8 text-center">
            <div className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-cosmic-pink/20 to-cosmic-purple/20 flex items-center justify-center">
              <Bot className="w-12 h-12 text-cosmic-purple" />
            </div>
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
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cosmic-pink/20 to-cosmic-purple/20 flex items-center justify-center">
                    <Bot className="w-6 h-6 text-cosmic-purple" />
                  </div>
                  AI Tutor
                  {isVoiceMode && (
                    <Badge variant="premium" className="ml-2">
                      Voice Mode Active
                    </Badge>
                  )}
                </CardTitle>
                <div className="flex items-center gap-2">
                  {/* Voice Mode Controls */}
                  <Button
                    variant={isVoiceMode ? 'primary' : 'outline'}
                    size="sm"
                    onClick={toggleVoiceMode}
                    className="flex items-center gap-2"
                  >
                    {isVoiceMode ? (
                      <>
                        <Mic className="w-4 h-4" />
                        Voice On
                      </>
                    ) : (
                      <>
                        <MicOff className="w-4 h-4" />
                        Voice Off
                      </>
                    )}
                  </Button>

                  {isVoiceMode && (
                    <>
                      {/* Mic Button */}
                      <Button
                        variant={isListening ? 'danger' : 'outline'}
                        size="sm"
                        onClick={toggleListening}
                        className="relative"
                        disabled={isLoading}
                      >
                        {isListening ? (
                          <>
                            <div className="absolute inset-0 bg-red-500/20 rounded-md animate-pulse" />
                            <Mic className="w-4 h-4" />
                            Stop
                          </>
                        ) : (
                          <>
                            <Mic className="w-4 h-4" />
                            Speak
                          </>
                        )}
                      </Button>

                      {/* Volume Toggle */}
                      <Button
                        variant={voiceEnabled ? 'outline' : 'ghost'}
                        size="sm"
                        onClick={toggleSpeechEnabled}
                        title={voiceEnabled ? 'Sound On' : 'Muted'}
                      >
                        {voiceEnabled ? (
                          <Volume2 className="w-4 h-4" />
                        ) : (
                          <VolumeX className="w-4 h-4" />
                        )}
                      </Button>

                      {/* Stop Speaking if active */}
                      {isSpeaking && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={stopSpeaking}
                        >
                          Stop Speaking
                        </Button>
                      )}
                    </>
                  )}

                  {messages.length > 0 && (
                    <Button variant="outline" size="sm" onClick={handleClearChat}>
                      Clear Chat
                    </Button>
                  )}
                </div>
              </div>

              {/* Voice Mode Status Bar */}
              {isVoiceMode && (
                <div className="mt-3 p-3 rounded-lg bg-gradient-to-r from-cosmic-primary/10 to-cosmic-purple/10 border border-cosmic-primary/30">
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      {isListening ? (
                        <>
                          <div className="w-2 h-2 bg-red-500 rounded-full animate-ping" />
                          <span className="text-text-primary font-medium">Listening...</span>
                        </>
                      ) : isSpeaking ? (
                        <>
                          <div className="w-2 h-2 bg-accent-primary rounded-full animate-pulse" />
                          <span className="text-text-primary font-medium">Speaking...</span>
                        </>
                      ) : (
                        <>
                          <div className="w-2 h-2 bg-accent-success rounded-full" />
                          <span className="text-text-secondary">
                            {voiceEnabled ? 'Ready to speak & listen' : 'Ready to listen only'}
                          </span>
                        </>
                      )}
                    </div>
                    <span className="text-xs text-text-muted">
                      Click Speak button or type your question
                    </span>
                  </div>
                </div>
              )}
            </CardHeader>

            <CardContent className="flex-1 flex flex-col p-0">
              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.length === 0 ? (
                  /* Welcome State */
                  <div className="h-full flex flex-col items-center justify-center text-center">
                    <div className="w-20 h-20 mb-4 rounded-2xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
                      <Sparkles className="w-12 h-12 text-cosmic-purple" />
                    </div>
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
                              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cosmic-purple/20 to-cosmic-pink/20 flex items-center justify-center flex-shrink-0 mt-1">
                                <Bot className="w-5 h-5 text-cosmic-purple" />
                              </div>
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
                              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cosmic-primary/20 to-cosmic-blue/20 flex items-center justify-center flex-shrink-0 mt-1">
                                <UserIcon className="w-5 h-5 text-cosmic-primary" />
                              </div>
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
                    <p className="text-sm text-accent-warning flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4" />
                      You need to be logged in to use AI Mentor. Redirecting to login...
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
                <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-accent-warning/20 to-accent-warning/10 flex items-center justify-center">
                  <Lightbulb className="w-4 h-4 text-accent-warning" />
                </div>
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

          {/* Voice Mode Info */}
          <Card className={isVoiceMode ? 'border-accent-primary' : ''}>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
                  <Mic className="w-4 h-4 text-cosmic-primary" />
                </div>
                Voice Mode
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              {isVoiceMode ? (
                <>
                  <div className="p-3 rounded-lg bg-accent-success/10 border border-accent-success/30">
                    <p className="text-text-primary font-medium mb-1">Active</p>
                    <p className="text-text-secondary text-xs">
                      Tap Speak to ask questions verbally. AI responses will be spoken aloud.
                    </p>
                  </div>
                  <div className="space-y-2 text-text-secondary">
                    <p className="flex items-center gap-2">
                      <Zap className="w-4 h-4 text-accent-primary" />
                      <span>Perfect for commuting or hands-free learning</span>
                    </p>
                    <p className="flex items-center gap-2">
                      <Zap className="w-4 h-4 text-accent-primary" />
                      <span>Practice oral exams and language skills</span>
                    </p>
                    <p className="text-xs text-text-muted mt-3">
                      Requires microphone permission
                    </p>
                  </div>
                </>
              ) : (
                <div className="text-center">
                  <p className="text-text-secondary mb-3">
                    Enable voice mode for hands-free conversations
                  </p>
                  <Button variant="outline" size="sm" onClick={toggleVoiceMode} className="w-full">
                    <Mic className="w-4 h-4 mr-2" />
                    Enable Voice
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Status */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Zap className="w-4 h-4" />
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
