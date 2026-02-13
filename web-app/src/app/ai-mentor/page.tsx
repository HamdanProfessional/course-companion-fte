'use client';

/**
 * AI Mentor Page - Nebula Theme with Voice Input
 *
 * Modern chat interface with cosmic/nebula styling:
 * - Dark space-themed gradients
 * - Voice input with Web Speech API
 * - Glowing effects on active elements
 * - ChatGPT-like conversation interface
 * - Recording animations
 */

import { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingSpinner } from '@/components/ui/Loading';
import { PageContainer } from '@/components/layout/PageContainer';
import {
  useV3ChatConversations,
  useV3CreateConversation,
  useV3DeleteConversation,
  useV3ConversationDetail,
  useV3MentorChatWithHistory,
  useV3UpdateConversation,
} from '@/hooks/useV3';
import { useUserTier } from '@/hooks';
import type { MentorMessage } from '@/lib/api-v3';
import {
  Bot,
  User as UserIcon,
  Plus,
  MessageSquare,
  Trash2,
  Edit2,
  Send,
  Clock,
  Mic,
  MicOff,
  X,
  Sparkles,
} from 'lucide-react';

// Types
interface ChatConversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

// Nebula/Cosmic theme colors
const NEBULA_COLORS = {
  purple: '#a855f7',
  pink: '#ec4899',
  blue: '#0ea5e9',
  cyan: '#06b6d4',
  primary: '#8b5cf6',
  bg: '#0f111a',
  secondary: '#1e2133',
};

// Suggested questions to help users get started
const SUGGESTED_QUESTIONS = [
  "How do MCP servers connect to ChatGPT?",
  "What's the difference between a skill and an agent?",
  "Explain state management in React Query",
  "How do I implement adaptive learning?",
];

// Typing animation component
const TypingIndicator = () => (
  <div className="flex items-center gap-1">
    <motion.span
      animate={{ y: [0, -4, 0] }}
      transition={{ duration: 0.4, repeat: Infinity, delay: 0 }}
      className="w-1.5 h-1.5 bg-cosmic-purple rounded-full"
    />
    <motion.span
      animate={{ y: [0, -4, 0] }}
      transition={{ duration: 0.4, repeat: Infinity, delay: 0.1 }}
      className="w-1.5 h-1.5 bg-cosmic-pink rounded-full"
    />
    <motion.span
      animate={{ y: [0, -4, 0] }}
      transition={{ duration: 0.4, repeat: Infinity, delay: 0.2 }}
      className="w-1.5 h-1.5 bg-cosmic-cyan rounded-full"
    />
  </div>
);

// Recording pulse animation
const RecordingPulse = () => (
  <div className="relative">
    <motion.div
      className="absolute inset-0 bg-cosmic-pink rounded-full"
      animate={{
        scale: [1, 1.5, 1],
        opacity: [0.5, 0, 0.5],
      }}
      transition={{
        duration: 1.5,
        repeat: Infinity,
        ease: "easeInOut",
      }}
    />
    <motion.div
      className="absolute inset-0 bg-cosmic-purple rounded-full"
      animate={{
        scale: [1, 1.3, 1],
        opacity: [0.5, 0, 0.5],
      }}
      transition={{
        duration: 1.5,
        repeat: Infinity,
        ease: "easeInOut",
        delay: 0.2,
      }}
    />
  </div>
);

export default function AIMentorPage() {
  // Chat state
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const [messages, setMessages] = useState<MentorMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [authError, setAuthError] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [editingTitle, setEditingTitle] = useState<string | null>(null);
  const [newTitle, setNewTitle] = useState('');
  const [mounted, setMounted] = useState(false);

  // Prevent hydration errors by only rendering browser-specific content after mount
  useEffect(() => {
    setMounted(true);
  }, []);

  // Voice input state
  const [isRecording, setIsRecording] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState<any>(null);
  const [voiceError, setVoiceError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // API hooks
  const { data: tier, isLoading: tierLoading } = useUserTier();
  const { data: conversations, isLoading: conversationsLoading, refetch: refetchConversations } = useV3ChatConversations();
  const { data: conversationDetail, isLoading: detailLoading } = useV3ConversationDetail(currentChatId || '');
  const createConversationMutation = useV3CreateConversation();
  const deleteConversationMutation = useV3DeleteConversation();
  const updateConversationMutation = useV3UpdateConversation();
  const mentorChatMutation = useV3MentorChatWithHistory();

  // Check if user can access AI features
  const canAccessAI = (!tierLoading && tier && tier === 'FREE') ? false : true;

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== 'undefined') {
      // Check for browser support
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

      if (SpeechRecognition) {
        const recognitionInstance = new SpeechRecognition();
        recognitionInstance.continuous = false;
        recognitionInstance.interimResults = true;
        recognitionInstance.lang = 'en-US';

        recognitionInstance.onstart = () => {
          setIsListening(true);
          setVoiceError(null);
        };

        recognitionInstance.onresult = (event: any) => {
          let interimTranscript = '';
          let finalTranscript = '';

          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              finalTranscript += transcript;
            } else {
              interimTranscript += transcript;
            }
          }

          if (finalTranscript) {
            setInputValue(prev => prev + finalTranscript);
          } else if (interimTranscript) {
            // Show interim results visually
            setInputValue(prev => {
              const baseText = prev;
              return baseText + interimTranscript;
            });
          }
        };

        recognitionInstance.onerror = (event: any) => {
          console.error('Speech recognition error:', event.error);
          setIsListening(false);
          setIsRecording(false);

          // Ignore "message port closed" errors from browser Speech API
          const errorMsg = event.error?.toString() || '';
          if (errorMsg.includes('message port closed') || errorMsg.includes('MessageChannel')) {
            console.warn('Ignoring message port closed error from Speech API');
            return;
          }

          if (event.error === 'no-speech') {
            setVoiceError('No speech detected. Please try again.');
          } else if (event.error === 'not-allowed') {
            setVoiceError('Microphone access denied. Please allow microphone access.');
          } else if (event.error === 'network') {
            setVoiceError('Network error. Please check your connection.');
          } else {
            setVoiceError(`Voice error: ${event.error}`);
          }

          setTimeout(() => setVoiceError(null), 3000);
        };

        recognitionInstance.onend = () => {
          setIsListening(false);
          setIsRecording(false);
        };

        setRecognition(recognitionInstance);
      } else {
        console.warn('Speech recognition not supported in this browser');
      }
    }

    return () => {
      if (recognition) {
        recognition.abort();
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
    // recognition is created inside this effect and should not be in dependencies
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load conversation detail when currentChatId changes
  useEffect(() => {
    if (currentChatId && conversationDetail) {
      setMessages(
        conversationDetail.messages.map(msg => ({
          role: msg.role as 'user' | 'assistant' | 'system',
          content: msg.content,
          timestamp: msg.created_at,
        }))
      );
    }
  }, [currentChatId, conversationDetail]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [inputValue]);

  // Start voice recording
  const startRecording = useCallback(() => {
    if (!recognition) {
      setVoiceError('Voice input not supported in this browser');
      setTimeout(() => setVoiceError(null), 3000);
      return;
    }

    try {
      recognition.start();
      setIsRecording(true);
      setVoiceError(null);
    } catch (error: any) {
      console.error('Error starting recognition:', error);
      // Ignore "message port closed" errors
      const errorMsg = error?.toString() || '';
      if (errorMsg.includes('message port closed') || errorMsg.includes('MessageChannel')) {
        console.warn('Ignoring message port closed error on start');
        return;
      }
      setVoiceError('Could not start microphone. Please try again.');
      setTimeout(() => setVoiceError(null), 3000);
    }
  }, [recognition]);

  // Stop voice recording
  const stopRecording = useCallback(() => {
    if (recognition && isListening) {
      recognition.stop();
      setIsRecording(false);
    }
  }, [recognition, isListening]);

  // Toggle recording
  const toggleRecording = useCallback(() => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  }, [isRecording, startRecording, stopRecording]);

  // Start a new chat
  const startNewChat = async () => {
    try {
      const result = await createConversationMutation.mutateAsync();
      setCurrentChatId(result.id);
      setMessages([]);
      setInputValue('');
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  // Load a chat from history
  const loadChat = (chatId: string) => {
    setCurrentChatId(chatId);
    if (window.innerWidth < 1024) {
      setIsSidebarOpen(false);
    }
  };

  // Delete a chat from history
  const deleteChat = async (chatId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await deleteConversationMutation.mutateAsync(chatId);
      if (currentChatId === chatId) {
        setCurrentChatId(null);
        setMessages([]);
      }
    } catch (error) {
      console.error('Failed to delete conversation:', error);
    }
  };

  // Update conversation title
  const updateTitle = async (chatId: string) => {
    if (!newTitle.trim()) {
      setEditingTitle(null);
      setNewTitle('');
      return;
    }

    try {
      await updateConversationMutation.mutateAsync({
        conversationId: chatId,
        data: { title: newTitle },
      });
      setEditingTitle(null);
      setNewTitle('');
      refetchConversations();
    } catch (error) {
      console.error('Failed to update title:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    // Check minimum question length (backend requires at least 5 characters)
    if (inputValue.trim().length < 5) {
      setVoiceError('Please enter at least 5 characters');
      setTimeout(() => setVoiceError(null), 3000);
      return;
    }

    // Check if user is logged in
    const userId = localStorage.getItem('user_id');
    if (!userId) {
      setAuthError(true);
      setTimeout(() => {
        window.location.href = '/login';
      }, 2000);
      return;
    }

    // Create conversation if none exists
    let chatId = currentChatId;
    if (!chatId) {
      try {
        const result = await createConversationMutation.mutateAsync();
        chatId = result.id;
        setCurrentChatId(chatId);
      } catch (error) {
        console.error('Failed to create conversation:', error);
        return;
      }
    }

    const userMessage: MentorMessage = {
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    const messageToSend = inputValue.trim();
    setInputValue('');
    setIsLoading(true);
    setAuthError(false);

    try {
      // Sanitize conversation history - only send required fields
      const sanitizedHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content,
      }));

      const response = await mentorChatMutation.mutateAsync({
        request: {
          question: messageToSend,
          conversation_history: sanitizedHistory,
        },
        conversationId: chatId,
      });

      const assistantMessage: MentorMessage = {
        role: 'assistant',
        content: response.answer,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, assistantMessage]);
      refetchConversations();
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
    setTimeout(() => handleSendMessage(), 100);
  };

  const handleClearChat = () => {
    setCurrentChatId(null);
    setMessages([]);
  };

  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  if (!canAccessAI) {
    return (
      <PageContainer suppressHydrationWarning>
        <div className="min-h-screen bg-cosmic-bg flex items-center justify-center p-4" suppressHydrationWarning>
          <Card className="relative overflow-hidden max-w-md w-full border-cosmic-purple/30 bg-cosmic-secondary/50 backdrop-blur-xl">
            <div className="absolute inset-0 bg-gradient-nebula opacity-10" />
            <CardContent className="relative p-12 text-center">
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-cosmic flex items-center justify-center shadow-nebula"
              >
                <Sparkles className="w-12 h-12 text-white" />
              </motion.div>
              <h2 className="text-3xl font-bold mb-3 bg-gradient-cosmic bg-clip-text text-transparent">
                Premium Feature
              </h2>
              <p className="text-cosmic-fg/70 mb-8 max-w-md mx-auto">
                Unlock AI-powered mentoring with 24/7 access to personalized tutoring and conceptual explanations.
              </p>
              <Button className="bg-gradient-cosmic hover:shadow-glow-purple text-white border-0">
                Upgrade to Premium
              </Button>
            </CardContent>
          </Card>
        </div>
      </PageContainer>
    );
  }

  return (
    <PageContainer className="p-0" suppressHydrationWarning>
      <div className="flex h-[calc(100vh-2rem)] gap-0" suppressHydrationWarning>
        {/* Sidebar - Chat History */}
        <motion.div
          initial={false}
          animate={{ width: isSidebarOpen ? '280px' : '0px' }}
          transition={{ duration: 0.2 }}
          className="relative border-r border-glass-border bg-cosmic-secondary/30 backdrop-blur-xl overflow-hidden"
        >
          <div className="w-[280px] h-full flex flex-col">
            {/* Sidebar Header */}
            <div className="p-4 border-b border-glass-border">
              <Button
                variant="outline"
                size="sm"
                onClick={startNewChat}
                className="w-full justify-start gap-2 bg-cosmic-bg/50 border-glass-border text-cosmic-fg hover:bg-glass-hover"
              >
                <Plus className="w-4 h-4" />
                New chat
              </Button>
            </div>

            {/* Chat List */}
            <div className="flex-1 overflow-y-auto p-2 space-y-1">
              {conversationsLoading ? (
                <div className="flex items-center justify-center py-8">
                  <LoadingSpinner size="sm" />
                </div>
              ) : conversations && conversations.length > 0 ? (
                conversations.map((chat) => (
                  <motion.div
                    key={chat.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className={`group relative p-3 rounded-lg cursor-pointer transition-all ${
                      currentChatId === chat.id
                        ? 'bg-gradient-stellar border border-cosmic-purple/30'
                        : 'hover:bg-glass-hover border border-transparent'
                    }`}
                    onClick={() => loadChat(chat.id)}
                  >
                    {editingTitle === chat.id ? (
                      <div className="flex items-center gap-2">
                        <input
                          type="text"
                          value={newTitle}
                          onChange={(e) => setNewTitle(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') updateTitle(chat.id);
                            if (e.key === 'Escape') {
                              setEditingTitle(null);
                              setNewTitle('');
                            }
                          }}
                          className="flex-1 px-2 py-1 text-sm bg-cosmic-bg border border-glass-border rounded focus:outline-none focus:ring-2 focus:ring-cosmic-purple text-cosmic-fg"
                          autoFocus
                        />
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            updateTitle(chat.id);
                          }}
                          className="p-1 hover:bg-glass-hover rounded"
                        >
                          <Bot className="w-4 h-4 text-cosmic-cyan" />
                        </button>
                      </div>
                    ) : (
                      <>
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-cosmic-fg truncate">
                              {chat.title}
                            </p>
                            <p className="text-xs text-cosmic-fg/50 mt-1 flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {formatDate(chat.updated_at)}
                            </p>
                          </div>
                          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                setEditingTitle(chat.id);
                                setNewTitle(chat.title);
                              }}
                              className="p-1 hover:bg-glass-hover rounded"
                              title="Rename"
                            >
                              <Edit2 className="w-3 h-3 text-cosmic-purple" />
                            </button>
                            <button
                              onClick={(e) => deleteChat(chat.id, e)}
                              className="p-1 hover:bg-red-500/20 rounded"
                              title="Delete"
                            >
                              <Trash2 className="w-3 h-3 text-red-400" />
                            </button>
                          </div>
                        </div>
                      </>
                    )}
                  </motion.div>
                ))
              ) : (
                <div className="text-center py-8 text-cosmic-fg/50 text-sm">
                  No chat history yet
                </div>
              )}
            </div>

            {/* Sidebar Footer */}
            <div className="p-4 border-t border-glass-border text-xs text-cosmic-fg/50">
              <p>AI Mentor v2.0 - Nebula Edition</p>
            </div>
          </div>
        </motion.div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col bg-cosmic-bg relative overflow-hidden">
          {/* Animated background */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <motion.div
              className="absolute top-20 left-20 w-96 h-96 bg-cosmic-purple/10 rounded-full blur-3xl"
              animate={{
                scale: [1, 1.2, 1],
                x: [0, 30, 0],
                y: [0, -30, 0],
              }}
              transition={{
                duration: 20,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            />
            <motion.div
              className="absolute bottom-20 right-20 w-96 h-96 bg-cosmic-blue/10 rounded-full blur-3xl"
              animate={{
                scale: [1, 1.3, 1],
                x: [0, -30, 0],
                y: [0, 30, 0],
              }}
              transition={{
                duration: 25,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            />
            <motion.div
              className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-cosmic-pink/10 rounded-full blur-3xl"
              animate={{
                scale: [1, 1.1, 1],
              }}
              transition={{
                duration: 15,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            />
          </div>

          {/* Chat Header */}
          <div className="relative flex items-center justify-between px-4 py-3 border-b border-glass-border bg-cosmic-secondary/30 backdrop-blur-xl">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                className="lg:hidden text-cosmic-fg hover:bg-glass-hover"
              >
                <MessageSquare className="w-5 h-5" />
              </Button>
              <div className="flex items-center gap-2">
                <motion.div
                  className="w-8 h-8 rounded-lg bg-gradient-cosmic flex items-center justify-center shadow-glow-purple"
                  animate={{
                    boxShadow: [
                      '0 0 20px rgba(139, 92, 246, 0.5)',
                      '0 0 30px rgba(14, 165, 233, 0.5)',
                      '0 0 20px rgba(139, 92, 246, 0.5)',
                    ],
                  }}
                  transition={{
                    duration: 3,
                    repeat: Infinity,
                    ease: "easeInOut",
                  }}
                >
                  <Sparkles className="w-5 h-5 text-white" />
                </motion.div>
                <div>
                  <h1 className="font-semibold text-cosmic-fg">AI Mentor</h1>
                  <p className="text-xs text-cosmic-fg/60">Always here to help</p>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {messages.length > 0 && (
                <Button variant="ghost" size="sm" onClick={handleClearChat} className="text-cosmic-fg hover:bg-glass-hover">
                  Clear chat
                </Button>
              )}
            </div>
          </div>

          {/* Messages Area */}
          <div className="relative flex-1 overflow-y-auto">
            <div className="max-w-3xl mx-auto px-4 py-6">
              {messages.length === 0 ? (
                /* Welcome State */
                <div className="h-full flex flex-col items-center justify-center text-center py-12">
                  <motion.div
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ duration: 0.5 }}
                    className="w-16 h-16 mb-6 rounded-2xl bg-gradient-cosmic flex items-center justify-center shadow-nebula"
                  >
                    <Sparkles className="w-10 h-10 text-white" />
                  </motion.div>
                  <h3 className="text-2xl font-semibold text-cosmic-fg mb-2">
                    How can I help you today?
                  </h3>
                  <p className="text-cosmic-fg/60 mb-8 max-w-md">
                    Ask me anything about the course material. I'm here to help you understand concepts and answer questions.
                  </p>

                  {/* Suggested Questions */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-2xl">
                    {SUGGESTED_QUESTIONS.map((question, i) => (
                      <motion.button
                        key={i}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.1 }}
                        onClick={() => handleSuggestedQuestion(question)}
                        className="text-left p-4 rounded-xl border border-glass-border hover:border-cosmic-purple/50 hover:bg-glass-hover transition-all group"
                      >
                        <p className="text-sm text-cosmic-fg group-hover:text-cosmic-purple transition-colors">{question}</p>
                      </motion.button>
                    ))}
                  </div>
                </div>
              ) : (
                /* Messages */
                <div className="space-y-6">
                  <AnimatePresence mode="popLayout">
                    {messages.map((message, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className={`flex gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        {message.role === 'assistant' && (
                          <div className="w-8 h-8 rounded-lg bg-gradient-cosmic flex items-center justify-center flex-shrink-0 shadow-glow-purple">
                            <Sparkles className="w-5 h-5 text-white" />
                          </div>
                        )}
                        <div className={`max-w-[80%] ${message.role === 'user' ? 'bg-gradient-to-r from-cosmic-purple to-cosmic-pink text-white' : 'text-cosmic-fg'}`}>
                          <div className={`rounded-2xl px-4 py-3 ${
                            message.role === 'user'
                              ? 'bg-gradient-to-r from-cosmic-purple to-cosmic-pink shadow-glow-purple'
                              : 'bg-glass-surface border border-glass-border backdrop-blur-xl'
                          }`}>
                            <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
                          </div>
                          {message.timestamp && (
                            <p className={`text-xs mt-1 ${message.role === 'user' ? 'text-cosmic-fg/70' : 'text-cosmic-fg/50'}`}>
                              {new Date(message.timestamp).toLocaleTimeString([], {
                                hour: '2-digit',
                                minute: '2-digit',
                              })}
                            </p>
                          )}
                        </div>
                        {message.role === 'user' && (
                          <div className="w-8 h-8 rounded-lg bg-glass-surface border border-glass-border flex items-center justify-center flex-shrink-0">
                            <UserIcon className="w-5 h-5 text-cosmic-fg" />
                          </div>
                        )}
                      </motion.div>
                    ))}
                  </AnimatePresence>

                  {/* Loading State */}
                  <AnimatePresence>
                    {isLoading && (
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                        className="flex gap-4"
                      >
                        <div className="w-8 h-8 rounded-lg bg-gradient-cosmic flex items-center justify-center flex-shrink-0 shadow-glow-purple">
                          <Sparkles className="w-5 h-5 text-white" />
                        </div>
                        <div className="bg-glass-surface border border-glass-border backdrop-blur-xl rounded-2xl px-4 py-3 flex items-center gap-2">
                          <TypingIndicator />
                          <span className="text-sm text-cosmic-fg/70">Thinking...</span>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  <div ref={messagesEndRef} />
                </div>
              )}
            </div>
          </div>

          {/* Input Area */}
          <div className="relative border-t border-glass-border bg-cosmic-secondary/30 backdrop-blur-xl">
            <div className="max-w-3xl mx-auto px-4 py-4">
              {authError && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mb-4 p-3 rounded-lg bg-orange-500/20 border border-orange-500/30 text-sm text-orange-300"
                >
                  You need to be logged in to use AI Mentor. Redirecting to login...
                </motion.div>
              )}

              {voiceError && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="mb-4 p-3 rounded-lg bg-red-500/20 border border-red-500/30 text-sm text-red-300"
                >
                  {voiceError}
                </motion.div>
              )}

              <div className="relative flex items-end gap-2 p-3 rounded-xl border border-glass-border focus-within:border-cosmic-purple/50 focus-within:ring-2 focus-within:ring-cosmic-purple/20 transition-all bg-glass-surface/50 backdrop-blur-xl">
                <textarea
                  ref={textareaRef}
                  value={inputValue}
                  onChange={(e) => {
                    setInputValue(e.target.value);
                    // Auto-resize textarea
                    if (textareaRef.current) {
                      textareaRef.current.style.height = 'auto';
                      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
                    }
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage();
                    }
                  }}
                  placeholder="Message AI Mentor..."
                  className="flex-1 bg-transparent text-cosmic-fg placeholder:text-cosmic-fg/40 resize-none focus:outline-none text-sm leading-relaxed py-2"
                  rows={1}
                  disabled={isLoading}
                  style={{ minHeight: '44px', maxHeight: '200px', overflowY: 'auto' }}
                />

                {/* Voice Input Button */}
                <div className="relative flex items-center gap-2">
                  {isRecording ? (
                    <motion.div
                      className="relative"
                      animate={{ scale: [1, 1.1, 1] }}
                      transition={{ duration: 1, repeat: Infinity }}
                    >
                      <RecordingPulse />
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={toggleRecording}
                        className="relative bg-cosmic-pink hover:bg-cosmic-pink/80 text-white p-2 rounded-full"
                      >
                        <MicOff className="w-4 h-4" />
                      </Button>
                    </motion.div>
                  ) : (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={toggleRecording}
                      disabled={isLoading}
                      className="text-cosmic-fg/60 hover:text-cosmic-purple hover:bg-glass-hover p-2 rounded-full transition-colors"
                      title={recognition ? 'Click to speak' : 'Voice input not supported'}
                    >
                      <Mic className="w-4 h-4" />
                    </Button>
                  )}

                  <Button
                    variant={inputValue.trim() ? 'primary' : 'ghost'}
                    size="sm"
                    onClick={handleSendMessage}
                    disabled={!inputValue.trim() || isLoading}
                    className="flex-shrink-0"
                  >
                    {isLoading ? (
                      <LoadingSpinner size="sm" />
                    ) : (
                      <Send className="w-4 h-4" />
                    )}
                  </Button>
                </div>
              </div>

              <div className="flex items-center justify-between mt-2">
                <p className="text-xs text-cosmic-fg/50">
                  Press Enter to send, Shift+Enter for new line
                </p>
                {isRecording && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex items-center gap-2 text-xs text-cosmic-pink"
                  >
                    <motion.span
                      animate={{ opacity: [0.5, 1, 0.5] }}
                      transition={{ duration: 1, repeat: Infinity }}
                    >
                      Recording...
                    </motion.span>
                  </motion.div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
