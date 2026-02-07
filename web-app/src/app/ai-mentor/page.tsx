'use client';

/**
 * AI Mentor Page - Phase 3 (Redesigned)
 *
 * Interactive AI tutor for conceptual Q&A with a modern, stunning interface:
 * - Gradient animated hero section with stats
 * - Glassmorphism design for chat container
 * - Enhanced visual hierarchy and animations
 * - Voice Mode: Two-way voice conversations
 */

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingSpinner } from '@/components/ui/Loading';
import { PageContainer } from '@/components/layout/PageContainer';
import { useV3MentorChat, useV3AIStatus } from '@/hooks/useV3';
import { useUserTier } from '@/hooks';
import type { MentorMessage } from '@/lib/api-v3';
import {
  Bot,
  User as UserIcon,
  Sparkles,
  Lightbulb,
  Zap,
  AlertTriangle,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  MessageCircle,
  TrendingUp,
  Clock,
  Star,
  ThumbsUp,
  Paperclip,
  Send,
  X,
} from 'lucide-react';

// Suggested questions to help users get started
const SUGGESTED_QUESTIONS = [
  { question: "How do MCP servers connect to ChatGPT?", icon: "🔗" },
  { question: "What's the difference between a skill and an agent?", icon: "🤖" },
  { question: "Explain state management in React Query", icon: "⚛️" },
  { question: "How do I implement adaptive learning?", icon: "🧠" },
];

// Typing animation component with bouncing dots
const TypingIndicator = () => (
  <div className="flex items-center gap-1">
    <motion.span
      animate={{ y: [0, -8, 0] }}
      transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
      className="w-2 h-2 bg-cosmic-purple rounded-full"
    />
    <motion.span
      animate={{ y: [0, -8, 0] }}
      transition={{ duration: 0.6, repeat: Infinity, delay: 0.1 }}
      className="w-2 h-2 bg-cosmic-pink rounded-full"
    />
    <motion.span
      animate={{ y: [0, -8, 0] }}
      transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
      className="w-2 h-2 bg-cosmic-blue rounded-full"
    />
  </div>
);

// Animated gradient background component
const AnimatedGradientBackground = () => (
  <div className="absolute inset-0 overflow-hidden rounded-t-3xl">
    <motion.div
      className="absolute inset-0 bg-gradient-to-br from-cosmic-purple via-cosmic-pink to-cosmic-blue opacity-30"
      animate={{
        backgroundPosition: ['0% 0%', '100% 100%', '0% 0%'],
      }}
      transition={{
        duration: 15,
        repeat: Infinity,
        ease: 'linear',
      }}
      style={{
        backgroundSize: '200% 200%',
      }}
    />
    {/* Floating orbs */}
    <motion.div
      className="absolute top-10 left-20 w-32 h-32 bg-cosmic-purple/40 rounded-full blur-3xl"
      animate={{
        x: [0, 50, 0],
        y: [0, 30, 0],
        scale: [1, 1.2, 1],
      }}
      transition={{
        duration: 8,
        repeat: Infinity,
        ease: 'easeInOut',
      }}
    />
    <motion.div
      className="absolute bottom-10 right-20 w-40 h-40 bg-cosmic-pink/40 rounded-full blur-3xl"
      animate={{
        x: [0, -50, 0],
        y: [0, -30, 0],
        scale: [1, 1.3, 1],
      }}
      transition={{
        duration: 10,
        repeat: Infinity,
        ease: 'easeInOut',
        delay: 1,
      }}
    />
    <motion.div
      className="absolute top-1/2 left-1/2 w-48 h-48 bg-cosmic-blue/30 rounded-full blur-3xl"
      animate={{
        x: [0, 30, -30, 0],
        y: [0, -40, 40, 0],
        scale: [1, 1.1, 1],
      }}
      transition={{
        duration: 12,
        repeat: Infinity,
        ease: 'easeInOut',
        delay: 2,
      }}
    />
  </div>
);

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

  // Message reactions state
  const [reactions, setReactions] = useState<Record<number, boolean>>({});

  // Get user tier
  const { data: tier, isLoading: tierLoading } = useUserTier();
  const { data: aiStatus } = useV3AIStatus();
  const mentorChat = useV3MentorChat();

  // Check if user can access AI features (PREMIUM or PRO tier)
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
    setReactions({});
  };

  const handleReaction = (messageIndex: number) => {
    setReactions(prev => ({
      ...prev,
      [messageIndex]: !prev[messageIndex],
    }));
  };

  // Voice Mode Functions
  const toggleVoiceMode = () => {
    if (!isVoiceMode && !voiceEnabled) {
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

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    synthesisRef.current = utterance;

    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(voice =>
      voice.lang.startsWith('en') && (voice.name.includes('Google') || voice.name.includes('Natural'))
    ) || voices.find(voice => voice.lang.startsWith('en')) || voices[0];

    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }

    utterance.rate = 0.9;
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
        <Card className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-cosmic-purple/10 via-cosmic-pink/10 to-cosmic-blue/10" />
          <CardContent className="relative p-12 text-center">
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ duration: 0.6, type: 'spring' }}
              className="w-24 h-24 mx-auto mb-6 rounded-3xl bg-gradient-to-br from-cosmic-purple to-cosmic-pink flex items-center justify-center shadow-glow-purple"
            >
              <Bot className="w-14 h-14 text-white" />
            </motion.div>
            <h2 className="text-3xl font-bold mb-3 bg-gradient-to-r from-cosmic-purple to-cosmic-pink bg-clip-text text-transparent">
              Premium Feature
            </h2>
            <p className="text-text-secondary mb-8 max-w-md mx-auto text-lg">
              Unlock AI-powered mentoring with 24/7 access to personalized tutoring and conceptual explanations.
            </p>
            <Button variant="primary" size="lg" className="shadow-glow-purple">
              Upgrade to Premium
            </Button>
          </CardContent>
        </Card>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative mb-8 rounded-3xl overflow-hidden"
      >
        <AnimatedGradientBackground />
        <div className="relative z-10 p-8 md:p-12">
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="flex-1 text-center md:text-left">
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.2 }}
                className="inline-block mb-4"
              >
                <div className="relative">
                  <motion.div
                    animate={{
                      scale: [1, 1.1, 1],
                      rotate: [0, 5, -5, 0],
                    }}
                    transition={{
                      duration: 3,
                      repeat: Infinity,
                      ease: 'easeInOut',
                    }}
                    className="w-20 h-20 rounded-2xl bg-gradient-to-br from-cosmic-purple to-cosmic-pink flex items-center justify-center shadow-glow-purple"
                  >
                    <Bot className="w-12 h-12 text-white" />
                  </motion.div>
                  <motion.div
                    className="absolute inset-0 rounded-2xl bg-gradient-to-br from-cosmic-purple to-cosmic-pink"
                    animate={{
                      scale: [1, 1.5, 1.8],
                      opacity: [0.5, 0.2, 0],
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      ease: 'easeOut',
                    }}
                  />
                </div>
              </motion.div>
              <h1 className="text-4xl md:text-5xl font-bold mb-3 text-white">
                AI Mentor
              </h1>
              <p className="text-xl text-white/80 mb-6 max-w-2xl">
                Your intelligent learning companion. Ask questions, get explanations, and master concepts with personalized AI tutoring.
              </p>
              <div className="flex flex-wrap gap-3 justify-center md:justify-start">
                <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/10 backdrop-blur-sm border border-white/20">
                  <MessageCircle className="w-5 h-5 text-cosmic-cyan" />
                  <span className="text-white font-semibold">24/7 Available</span>
                </div>
                <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/10 backdrop-blur-sm border border-white/20">
                  <Zap className="w-5 h-5 text-yellow-400" />
                  <span className="text-white font-semibold">Instant Answers</span>
                </div>
                <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/10 backdrop-blur-sm border border-white/20">
                  <Mic className="w-5 h-5 text-cosmic-pink" />
                  <span className="text-white font-semibold">Voice Mode</span>
                </div>
              </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-3 gap-4">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="text-center"
              >
                <div className="w-16 h-16 mx-auto mb-2 rounded-2xl bg-gradient-to-br from-cosmic-purple/30 to-cosmic-purple/10 backdrop-blur-sm border border-cosmic-purple/30 flex items-center justify-center">
                  <MessageCircle className="w-8 h-8 text-cosmic-purple" />
                </div>
                <div className="text-2xl font-bold text-white">{messages.length}</div>
                <div className="text-sm text-white/60">Questions</div>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="text-center"
              >
                <div className="w-16 h-16 mx-auto mb-2 rounded-2xl bg-gradient-to-br from-cosmic-pink/30 to-cosmic-pink/10 backdrop-blur-sm border border-cosmic-pink/30 flex items-center justify-center">
                  <Clock className="w-8 h-8 text-cosmic-pink" />
                </div>
                <div className="text-2xl font-bold text-white">{aiStatus ? 'Active' : 'Ready'}</div>
                <div className="text-sm text-white/60">Status</div>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="text-center"
              >
                <div className="w-16 h-16 mx-auto mb-2 rounded-2xl bg-gradient-to-br from-cosmic-blue/30 to-cosmic-blue/10 backdrop-blur-sm border border-cosmic-blue/30 flex items-center justify-center">
                  <Star className="w-8 h-8 text-cosmic-blue" />
                </div>
                <div className="text-2xl font-bold text-white">{(aiStatus?.llm_provider || 'AI').toUpperCase()}</div>
                <div className="text-sm text-white/60">Powered By</div>
              </motion.div>
            </div>
          </div>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Chat Area */}
        <div className="lg:col-span-3">
          <Card className="relative overflow-hidden backdrop-blur-xl bg-glass-surface/80 border-glass-border">
            {/* Animated gradient border */}
            <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-cosmic-purple via-cosmic-pink to-cosmic-blue opacity-0 hover:opacity-100 transition-opacity duration-500 pointer-events-none" style={{ padding: '1px' }}>
              <div className="absolute inset-0 rounded-2xl bg-cosmic-bg" />
            </div>

            <div className="relative z-10 h-[700px] flex flex-col">
              {/* Chat Header */}
              <CardHeader className="border-b border-glass-border backdrop-blur-xl">
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-3">
                    <motion.div
                      animate={{
                        scale: [1, 1.1, 1],
                        rotate: [0, 10, -10, 0],
                      }}
                      transition={{
                        duration: 4,
                        repeat: Infinity,
                        ease: 'easeInOut',
                      }}
                      className="w-12 h-12 rounded-xl bg-gradient-to-br from-cosmic-purple to-cosmic-pink flex items-center justify-center shadow-glow-purple"
                    >
                      <Bot className="w-7 h-7 text-white" />
                    </motion.div>
                    <div>
                      <div className="text-xl font-bold bg-gradient-to-r from-cosmic-purple to-cosmic-pink bg-clip-text text-transparent">
                        AI Mentor
                      </div>
                      <div className="flex items-center gap-2 mt-1">
                        <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                        <span className="text-sm text-text-secondary">Online</span>
                      </div>
                    </div>
                  </CardTitle>

                  <div className="flex items-center gap-2">
                    {isVoiceMode && (
                      <Badge variant="premium" className="shadow-glow-purple">
                        <Mic className="w-3 h-3 mr-1" />
                        Voice Mode
                      </Badge>
                    )}
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
                        <Button
                          variant={isListening ? 'danger' : 'outline'}
                          size="sm"
                          onClick={toggleListening}
                          disabled={isLoading}
                          className="relative"
                        >
                          {isListening && (
                            <motion.div
                              className="absolute inset-0 bg-red-500/20 rounded-lg"
                              animate={{ scale: [1, 1.2, 1] }}
                              transition={{ duration: 1, repeat: Infinity }}
                            />
                          )}
                          <Mic className="w-4 h-4" />
                          {isListening ? 'Stop' : 'Speak'}
                        </Button>

                        <Button
                          variant={voiceEnabled ? 'outline' : 'ghost'}
                          size="sm"
                          onClick={toggleSpeechEnabled}
                        >
                          {voiceEnabled ? (
                            <Volume2 className="w-4 h-4" />
                          ) : (
                            <VolumeX className="w-4 h-4" />
                          )}
                        </Button>
                      </>
                    )}

                    {messages.length > 0 && (
                      <Button variant="outline" size="sm" onClick={handleClearChat}>
                        Clear
                      </Button>
                    )}
                  </div>
                </div>

                {/* Voice Mode Status Bar */}
                <AnimatePresence>
                  {isVoiceMode && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="mt-4 overflow-hidden"
                    >
                      <div className="p-4 rounded-xl bg-gradient-to-r from-cosmic-purple/10 via-cosmic-pink/10 to-cosmic-blue/10 border border-cosmic-purple/30 backdrop-blur-sm">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            {isListening ? (
                              <>
                                <motion.div
                                  className="w-3 h-3 bg-red-500 rounded-full"
                                  animate={{ scale: [1, 1.5, 1] }}
                                  transition={{ duration: 0.8, repeat: Infinity }}
                                />
                                <span className="text-text-primary font-medium">Listening...</span>
                                <div className="flex gap-1">
                                  {[0, 1, 2, 3, 4].map((i) => (
                                    <motion.div
                                      key={i}
                                      className="w-1 h-6 bg-gradient-to-t from-cosmic-purple to-cosmic-pink rounded-full"
                                      animate={{
                                        height: [24, 40, 24],
                                      }}
                                      transition={{
                                        duration: 0.5,
                                        repeat: Infinity,
                                        delay: i * 0.1,
                                      }}
                                    />
                                  ))}
                                </div>
                              </>
                            ) : isSpeaking ? (
                              <>
                                <motion.div
                                  className="w-3 h-3 bg-cosmic-purple rounded-full"
                                  animate={{ scale: [1, 1.5, 1] }}
                                  transition={{ duration: 0.8, repeat: Infinity }}
                                />
                                <span className="text-text-primary font-medium">Speaking...</span>
                                <div className="flex gap-1">
                                  {[0, 1, 2, 3, 4].map((i) => (
                                    <motion.div
                                      key={i}
                                      className="w-1 h-6 bg-gradient-to-t from-cosmic-blue to-cosmic-cyan rounded-full"
                                      animate={{
                                        height: [24, 40, 24],
                                      }}
                                      transition={{
                                        duration: 0.5,
                                        repeat: Infinity,
                                        delay: i * 0.1,
                                      }}
                                    />
                                  ))}
                                </div>
                              </>
                            ) : (
                              <>
                                <div className="w-3 h-3 bg-green-400 rounded-full" />
                                <span className="text-text-secondary">
                                  {voiceEnabled ? 'Ready to speak & listen' : 'Ready to listen only'}
                                </span>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </CardHeader>

              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4 scroll-smooth">
                {messages.length === 0 ? (
                  /* Welcome State */
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5 }}
                    className="h-full flex flex-col items-center justify-center text-center"
                  >
                    <motion.div
                      initial={{ y: 20, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      transition={{ delay: 0.2 }}
                      className="relative mb-6"
                    >
                      <motion.div
                        animate={{
                          scale: [1, 1.1, 1],
                          rotate: [0, 5, -5, 0],
                        }}
                        transition={{
                          duration: 4,
                          repeat: Infinity,
                          ease: 'easeInOut',
                        }}
                        className="w-24 h-24 rounded-3xl bg-gradient-to-br from-cosmic-purple via-cosmic-pink to-cosmic-blue flex items-center justify-center shadow-nebula"
                      >
                        <Sparkles className="w-14 h-14 text-white" />
                      </motion.div>
                      <motion.div
                        className="absolute inset-0 rounded-3xl"
                        animate={{
                          scale: [1, 1.3, 1.5],
                          opacity: [0.4, 0.2, 0],
                        }}
                        transition={{
                          duration: 2,
                          repeat: Infinity,
                          ease: 'easeOut',
                        }}
                        style={{
                          background: 'linear-gradient(135deg, #8b5cf6 0%, #ec4899 50%, #0ea5e9 100%)',
                          filter: 'blur(20px)',
                        }}
                      />
                    </motion.div>
                    <motion.h3
                      initial={{ y: 20, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      transition={{ delay: 0.3 }}
                      className="text-2xl font-bold text-text-primary mb-3"
                    >
                      Welcome to AI Mentor!
                    </motion.h3>
                    <motion.p
                      initial={{ y: 20, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      transition={{ delay: 0.4 }}
                      className="text-text-secondary max-w-md mb-8 text-lg"
                    >
                      Ask me anything about the course material. I'm here to help you understand concepts, answer questions, and guide your learning journey.
                    </motion.p>

                    {/* Suggested Questions */}
                    <motion.div
                      initial={{ y: 20, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      transition={{ delay: 0.5 }}
                      className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-3xl mx-auto"
                    >
                      {SUGGESTED_QUESTIONS.map((sq, i) => (
                        <motion.button
                          key={i}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: 0.6 + i * 0.1 }}
                          onClick={() => handleSuggestedQuestion(sq.question)}
                          className="group flex items-center gap-3 p-4 rounded-xl bg-glass-surface border border-glass-border hover:border-cosmic-purple hover:shadow-glow-purple transition-all duration-300 text-left"
                        >
                          <span className="text-2xl">{sq.icon}</span>
                          <span className="text-sm text-text-primary group-hover:text-cosmic-purple transition-colors">
                            {sq.question}
                          </span>
                        </motion.button>
                      ))}
                    </motion.div>
                  </motion.div>
                ) : (
                  /* Messages */
                  <div className="space-y-4">
                    <AnimatePresence mode="popLayout">
                      {messages.map((message, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, y: 20, scale: 0.95 }}
                          animate={{ opacity: 1, y: 0, scale: 1 }}
                          exit={{ opacity: 0, scale: 0.9 }}
                          transition={{ duration: 0.3 }}
                          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                          <div
                            className={`max-w-[80%] rounded-2xl ${
                              message.role === 'user'
                                ? 'bg-gradient-to-br from-cosmic-purple to-cosmic-pink text-white shadow-glow-purple'
                                : 'bg-glass-surface border border-glass-border text-text-primary'
                            }`}
                          >
                            <div className="p-4">
                              <div className="flex items-start gap-3">
                                {message.role === 'assistant' && (
                                  <motion.div
                                    whileHover={{ scale: 1.1, rotate: 5 }}
                                    className="w-10 h-10 rounded-xl bg-gradient-to-br from-cosmic-purple to-cosmic-pink flex items-center justify-center flex-shrink-0 shadow-glow-purple"
                                  >
                                    <Bot className="w-6 h-6 text-white" />
                                  </motion.div>
                                )}
                                <div className="flex-1">
                                  <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
                                  <div className="flex items-center gap-3 mt-3">
                                    {message.timestamp && (
                                      <p
                                        className={`text-xs ${
                                          message.role === 'user'
                                            ? 'text-white/70'
                                            : 'text-text-muted'
                                        }`}
                                      >
                                        {new Date(message.timestamp).toLocaleTimeString([], {
                                          hour: '2-digit',
                                          minute: '2-digit',
                                        })}
                                      </p>
                                    )}
                                    {message.role === 'assistant' && (
                                      <motion.button
                                        whileHover={{ scale: 1.1 }}
                                        whileTap={{ scale: 0.9 }}
                                        onClick={() => handleReaction(index)}
                                        className={`flex items-center gap-1 px-2 py-1 rounded-lg transition-colors ${
                                          reactions[index]
                                            ? 'bg-cosmic-purple/20 text-cosmic-purple'
                                            : 'hover:bg-bg-elevated text-text-muted'
                                        }`}
                                      >
                                        <ThumbsUp className="w-3 h-3" />
                                      </motion.button>
                                    )}
                                  </div>
                                </div>
                                {message.role === 'user' && (
                                  <motion.div
                                    whileHover={{ scale: 1.1, rotate: -5 }}
                                    className="w-10 h-10 rounded-xl bg-gradient-to-br from-cosmic-blue to-cosmic-cyan flex items-center justify-center flex-shrink-0 shadow-glow-blue"
                                  >
                                    <UserIcon className="w-6 h-6 text-white" />
                                  </motion.div>
                                )}
                              </div>
                            </div>
                          </div>
                        </motion.div>
                      ))}
                    </AnimatePresence>

                    {/* Loading State */}
                    <AnimatePresence>
                      {isLoading && (
                        <motion.div
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -20 }}
                          className="flex justify-start"
                        >
                          <div className="bg-glass-surface border border-glass-border rounded-2xl px-6 py-4 flex items-center gap-3">
                            <TypingIndicator />
                            <span className="text-sm text-text-muted">Thinking...</span>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>

                    <div ref={messagesEndRef} />
                  </div>
                )}
              </div>

              {/* Input Area */}
              <div className="border-t border-glass-border p-4 backdrop-blur-xl">
                {authError && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-4 p-4 rounded-xl bg-accent-warning/10 border border-accent-warning/30 flex items-center gap-3"
                  >
                    <AlertTriangle className="w-5 h-5 text-accent-warning flex-shrink-0" />
                    <p className="text-sm text-accent-warning">
                      You need to be logged in to use AI Mentor. Redirecting to login...
                    </p>
                  </motion.div>
                )}

                <div className="relative">
                  <div className="flex items-end gap-3 p-3 rounded-2xl bg-glass-surface border border-glass-border shadow-lg">
                    {/* Attachment button */}
                    <motion.button
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      className="p-2 rounded-xl hover:bg-bg-elevated transition-colors text-text-muted hover:text-cosmic-purple"
                      title="Attach files (coming soon)"
                    >
                      <Paperclip className="w-5 h-5" />
                    </motion.button>

                    {/* Text input */}
                    <textarea
                      value={inputValue}
                      onChange={e => setInputValue(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Ask me anything about the course..."
                      className="flex-1 bg-transparent text-text-primary placeholder:text-text-muted resize-none focus:outline-none"
                      rows={1}
                      disabled={isLoading}
                      style={{ minHeight: '44px', maxHeight: '120px' }}
                    />

                    {/* Character counter */}
                    <span className="text-xs text-text-muted self-end mb-1">
                      {inputValue.length} / 500
                    </span>

                    {/* Send button */}
                    <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                      <Button
                        variant="primary"
                        onClick={handleSendMessage}
                        disabled={!inputValue.trim() || isLoading}
                        className="shadow-glow-purple"
                      >
                        {isLoading ? (
                          <LoadingSpinner size="sm" />
                        ) : (
                          <Send className="w-4 h-4" />
                        )}
                      </Button>
                    </motion.div>
                  </div>

                  {/* Helper text */}
                  <p className="text-xs text-text-muted mt-2 text-center">
                    Press Enter to send, Shift+Enter for new line
                  </p>
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          {/* Quick Tips */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="backdrop-blur-xl bg-glass-surface/80 border-glass-border overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-cosmic-purple/10 to-cosmic-pink/10" />
              <CardHeader className="relative z-10">
                <CardTitle className="text-base flex items-center gap-2">
                  <motion.div
                    animate={{ rotate: [0, 10, -10, 0] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-warning/30 to-accent-warning/10 flex items-center justify-center"
                  >
                    <Lightbulb className="w-4 h-4 text-accent-warning" />
                  </motion.div>
                  <span className="bg-gradient-to-r from-cosmic-purple to-cosmic-pink bg-clip-text text-transparent font-bold">
                    Quick Tips
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent className="relative z-10 space-y-3">
                {[
                  { tip: "Be specific with your questions", icon: "🎯" },
                  { tip: "Reference chapters when relevant", icon: "📚" },
                  { tip: "Ask follow-up questions", icon: "🔄" },
                  { tip: "Use examples for clarity", icon: "💡" },
                ].map((item, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 + i * 0.1 }}
                    className="flex items-start gap-3 p-3 rounded-xl bg-glass-surface border border-glass-border hover:border-cosmic-purple hover:shadow-glow-purple transition-all duration-300 group"
                  >
                    <span className="text-xl group-hover:scale-110 transition-transform">{item.icon}</span>
                    <span className="text-sm text-text-secondary">{item.tip}</span>
                  </motion.div>
                ))}
              </CardContent>
            </Card>
          </motion.div>

          {/* Voice Mode Card */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className={`backdrop-blur-xl bg-glass-surface/80 border-glass-border overflow-hidden ${
              isVoiceMode ? 'border-cosmic-purple shadow-glow-purple' : ''
            }`}>
              {isVoiceMode && (
                <div className="absolute inset-0 bg-gradient-to-br from-cosmic-purple/20 to-cosmic-pink/20" />
              )}
              <CardHeader className="relative z-10">
                <CardTitle className="text-base flex items-center gap-2">
                  <motion.div
                    animate={isVoiceMode ? {
                      scale: [1, 1.2, 1],
                      rotate: [0, 180],
                    } : {}}
                    transition={{
                      duration: 2,
                      repeat: isVoiceMode ? Infinity : 0,
                    }}
                    className="w-8 h-8 rounded-lg bg-gradient-to-br from-cosmic-primary/30 to-cosmic-purple/30 flex items-center justify-center"
                  >
                    <Mic className="w-4 h-4 text-cosmic-primary" />
                  </motion.div>
                  <span className="bg-gradient-to-r from-cosmic-primary to-cosmic-purple bg-clip-text text-transparent font-bold">
                    Voice Mode
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent className="relative z-10 space-y-4">
                {isVoiceMode ? (
                  <>
                    <motion.div
                      initial={{ scale: 0.9, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      className="p-4 rounded-xl bg-gradient-to-r from-accent-success/20 to-accent-success/10 border border-accent-success/30"
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <motion.div
                          className="w-2 h-2 bg-green-400 rounded-full"
                          animate={{ scale: [1, 1.5, 1] }}
                          transition={{ duration: 1, repeat: Infinity }}
                        />
                        <span className="text-text-primary font-semibold">Active</span>
                      </div>
                      <p className="text-text-secondary text-xs">
                        Tap Speak to ask questions verbally. AI responses will be spoken aloud.
                      </p>
                    </motion.div>
                    <div className="space-y-3 text-sm">
                      <motion.div
                        initial={{ opacity: 0, x: 10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.1 }}
                        className="flex items-center gap-3 p-2 rounded-lg hover:bg-bg-elevated transition-colors"
                      >
                        <Zap className="w-4 h-4 text-cosmic-purple" />
                        <span className="text-text-secondary">Perfect for commuting</span>
                      </motion.div>
                      <motion.div
                        initial={{ opacity: 0, x: 10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.2 }}
                        className="flex items-center gap-3 p-2 rounded-lg hover:bg-bg-elevated transition-colors"
                      >
                        <Zap className="w-4 h-4 text-cosmic-pink" />
                        <span className="text-text-secondary">Practice oral skills</span>
                      </motion.div>
                    </div>
                    <p className="text-xs text-text-muted text-center">
                      Requires microphone permission
                    </p>
                  </>
                ) : (
                  <div className="text-center">
                    <p className="text-text-secondary mb-4 text-sm">
                      Enable voice mode for hands-free conversations
                    </p>
                    <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={toggleVoiceMode}
                        className="w-full shadow-glow-purple"
                      >
                        <Mic className="w-4 h-4 mr-2" />
                        Enable Voice
                      </Button>
                    </motion.div>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* AI Status */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card className="backdrop-blur-xl bg-glass-surface/80 border-glass-border overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-cosmic-blue/10 to-cosmic-cyan/10" />
              <CardHeader className="relative z-10">
                <CardTitle className="text-base flex items-center gap-2">
                  <motion.div
                    animate={{ rotate: [0, 360] }}
                    transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
                    className="w-8 h-8 rounded-lg bg-gradient-to-br from-cosmic-blue/30 to-cosmic-cyan/30 flex items-center justify-center"
                  >
                    <Zap className="w-4 h-4 text-cosmic-blue" />
                  </motion.div>
                  <span className="bg-gradient-to-r from-cosmic-blue to-cosmic-cyan bg-clip-text text-transparent font-bold">
                    AI Status
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent className="relative z-10 space-y-3">
                <div className="flex justify-between items-center p-3 rounded-xl bg-glass-surface border border-glass-border">
                  <span className="text-sm text-text-secondary">Provider</span>
                  <Badge variant="info" glow>{(aiStatus?.llm_provider || 'AI').toUpperCase()}</Badge>
                </div>
                <div className="flex justify-between items-center p-3 rounded-xl bg-glass-surface border border-glass-border">
                  <span className="text-sm text-text-secondary">Status</span>
                  <div className="flex items-center gap-2">
                    <motion.div
                      className="w-2 h-2 bg-green-400 rounded-full"
                      animate={{ scale: [1, 1.3, 1] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    />
                    <Badge variant="success" glow>Online</Badge>
                  </div>
                </div>
                <div className="flex justify-between items-center p-3 rounded-xl bg-glass-surface border border-glass-border">
                  <span className="text-sm text-text-secondary">Model</span>
                  <Badge variant="premium" glow>GPT-4</Badge>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </PageContainer>
  );
}
