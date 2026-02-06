'use client';

/**
 * Time Machine Page - View Your Learning Journey
 *
 * Features:
 * - See how your questions have evolved over time
 * - Track improvement in question sophistication
 * - Visual timeline of your learning progress
 * - Compare early questions vs recent questions
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingSpinner } from '@/components/ui/Loading';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import { Clock, TrendingUp, Lightbulb, Star, ArrowRight, Calendar, MessageSquare, Brain, Target, Award, ChevronDown, ChevronUp } from 'lucide-react';

interface QuestionEvolution {
  date: string;
  question: string;
  sophistication: 'beginner' | 'intermediate' | 'advanced';
  topic: string;
  context?: string;
}

interface MilestoneItem {
  date: string;
  title: string;
  description: string;
  level: number;
}

// Mock data - In production, this would come from the backend
const mockQuestionEvolution: QuestionEvolution[] = [
  {
    date: '2026-01-15',
    question: 'What is an API?',
    sophistication: 'beginner',
    topic: 'Introduction',
  },
  {
    date: '2026-01-20',
    question: 'How do I call an API in JavaScript?',
    sophistication: 'beginner',
    topic: 'API Basics',
  },
  {
    date: '2026-01-28',
    question: 'What are the differences between REST and GraphQL?',
    sophistication: 'intermediate',
    topic: 'API Design',
  },
  {
    date: '2026-02-05',
    question: 'How do I handle errors when an API call fails?',
    sophistication: 'intermediate',
    topic: 'Error Handling',
  },
  {
    date: '2026-02-10',
    question: 'Can you explain how to implement rate limiting for an API?',
    sophistication: 'advanced',
    topic: 'API Architecture',
  },
  {
    date: '2026-02-15',
    question: 'How do I design a scalable API architecture with caching, load balancing, and database optimization?',
    sophistication: 'advanced',
    topic: 'System Design',
  },
];

const mockMilestones: MilestoneItem[] = [
  {
    date: '2026-01-15',
    title: 'First Question Asked',
    description: 'You began your learning journey with foundational questions',
    level: 1,
  },
  {
    date: '2026-01-28',
    title: 'Intermediate Thinker',
    description: 'Your questions showed deeper understanding of concepts',
    level: 2,
  },
  {
    date: '2026-02-10',
    title: 'Advanced Inquirer',
    description: 'You started asking sophisticated, multi-faceted questions',
    level: 3,
  },
];

export default function TimeMachinePage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [selectedQuestion, setSelectedQuestion] = useState<QuestionEvolution | null>(null);
  const [expandedMilestones, setExpandedMilestones] = useState<number[]>([]);

  useEffect(() => {
    const userId = localStorage.getItem('user_id');
    if (!userId) {
      router.push('/login');
      return;
    }
    setIsLoading(false);
  }, [router]);

  const sophisticationConfig = {
    beginner: {
      color: 'accent-warning',
      icon: Lightbulb,
      label: 'Foundational',
    },
    intermediate: {
      color: 'accent-primary',
      icon: Brain,
      label: 'Growing',
    },
    advanced: {
      color: 'accent-success',
      icon: Star,
      label: 'Sophisticated',
    },
  };

  const getSophisticationLevel = (question: QuestionEvolution) => {
    if (question.question.length > 100) return 3;
    if (question.question.includes('how') && question.question.includes('why')) return 2;
    if (question.question.includes('what is')) return 1;
    return 2;
  };

  const toggleMilestone = (index: number) => {
    setExpandedMilestones(prev =>
      prev.includes(index)
        ? prev.filter(i => i !== index)
        : [...prev, index]
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <PageContainer>
      <PageHeader
        title="Time Machine"
        description="See how your questions and understanding have evolved over time"
      />

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
                <MessageSquare className="w-6 h-6 text-cosmic-primary" />
              </div>
            </div>
            <h3 className="text-3xl font-bold text-text-primary">{mockQuestionEvolution.length}</h3>
            <p className="text-sm text-text-secondary">Questions Asked</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-success/20 to-accent-success/10 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-accent-success" />
              </div>
            </div>
            <h3 className="text-3xl font-bold text-accent-success">Advanced</h3>
            <p className="text-sm text-text-secondary">Current Level</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-info/20 to-accent-info/10 flex items-center justify-center">
                <Calendar className="w-6 h-6 text-accent-info" />
              </div>
            </div>
            <h3 className="text-3xl font-bold text-text-primary">1 Month</h3>
            <p className="text-sm text-text-secondary">Learning Journey</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Question Evolution Timeline */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center">
                  <Clock className="w-6 h-6 text-cosmic-primary" />
                </div>
                Your Question Evolution
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockQuestionEvolution.map((item, index) => {
                  const config = sophisticationConfig[item.sophistication];
                  const Icon = config.icon;

                  return (
                    <div
                      key={index}
                      onClick={() => setSelectedQuestion(item)}
                      className={`p-4 rounded-lg border cursor-pointer transition-all hover:shadow-lg ${
                        selectedQuestion?.date === item.date
                          ? 'bg-gradient-to-r from-cosmic-primary/20 to-cosmic-purple/20 border-cosmic-primary'
                          : 'bg-bg-elevated border-border-default hover:border-cosmic-primary/50'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <Badge
                              variant={item.sophistication === 'beginner' ? 'warning' : item.sophistication === 'intermediate' ? 'primary' : 'success'}
                              className="text-xs"
                            >
                              {config.label}
                            </Badge>
                            <span className="text-xs text-text-muted">{item.date}</span>
                          </div>
                          <p className="text-text-primary font-medium">{item.question}</p>
                          <p className="text-xs text-text-muted mt-1">
                            Topic: {item.topic}
                          </p>
                        </div>
                        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-${config.color}/20 to-${config.color}/10 flex items-center justify-center flex-shrink-0">
                          <Icon className="w-5 h-5 text-${config.color}" />
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* Comparison View */}
          {selectedQuestion && (
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Deep Dive: {selectedQuestion.question}</CardTitle>
                <CardDescription>
                  Understanding your progression
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-4 rounded-lg bg-accent-info/10 border border-accent-info/30">
                    <h4 className="font-semibold text-text-primary mb-2 flex items-center gap-2">
                      <Target className="w-4 h-4 text-accent-info" />
                      Sophistication Analysis
                    </h4>
                    <p className="text-sm text-text-secondary">
                      This {selectedQuestion.sophistication} level question shows{' '}
                      {selectedQuestion.sophistication === 'beginner' && 'you\'re building foundational knowledge'}
                      {selectedQuestion.sophistication === 'intermediate' && 'growing understanding of relationships between concepts'}
                      {selectedQuestion.sophistication === 'advanced' && 'ability to think strategically about system design'}
                    </p>
                  </div>

                  <div className="p-4 rounded-lg bg-bg-elevated border border-border-default">
                    <h4 className="font-semibold text-text-primary mb-2">Growth Journey</h4>
                    <div className="relative pl-6 border-l-2 border-cosmic-primary">
                      <div className="space-y-3">
                        <div className="text-sm">
                          <span className="text-text-muted">Start:</span> Asking "what is" questions to understand basics
                        </div>
                        <div className="text-sm">
                          <span className="text-text-muted">Progress:</span> Adding "how" and "why" to explore mechanics
                        </div>
                        <div className="text-sm">
                          <span className="text-text-muted">Now:</span> Multi-faceted questions considering architecture and optimization
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-3">
                    <Button variant="primary" onClick={() => router.push('/ai-mentor')}>
                      <MessageSquare className="w-4 h-4 mr-2" />
                      Discuss This
                    </Button>
                    <Button variant="outline" onClick={() => setSelectedQuestion(null)}>
                      Close
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Milestones Sidebar */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-primary/20 to-cosmic-purple/20 flex items-center justify-center">
                  <Award className="w-6 h-6 text-cosmic-primary" />
                </div>
                Learning Milestones
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {mockMilestones.map((milestone, index) => {
                  const isExpanded = expandedMilestones.includes(index);

                  return (
                    <div
                      key={index}
                      className="border border-border-default rounded-lg overflow-hidden"
                    >
                      <button
                        onClick={() => toggleMilestone(index)}
                        className="w-full p-3 flex items-center justify-between hover:bg-bg-elevated transition-colors"
                      >
                        <div className="flex items-center gap-3 flex-1 text-left">
                          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cosmic-primary/20 to-cosmic-purple/20 flex items-center justify-center flex-shrink-0">
                            <Star className="w-4 h-4 text-cosmic-primary" />
                          </div>
                          <div>
                            <p className="text-sm font-medium text-text-primary">{milestone.title}</p>
                            <p className="text-xs text-text-muted">{milestone.date}</p>
                          </div>
                        </div>
                        {isExpanded ? <ChevronUp className="w-4 h-4 text-text-muted" /> : <ChevronDown className="w-4 h-4 text-text-muted" />}
                      </button>

                      {isExpanded && (
                        <div className="px-3 pb-3 border-t border-border-default pt-3">
                          <p className="text-sm text-text-secondary">{milestone.description}</p>
                          <div className="mt-2 flex gap-1">
                            {[...Array(milestone.level)].map((_, i) => (
                              <div
                                key={i}
                                className="w-6 h-1 rounded-full bg-cosmic-primary"
                              />
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* Insights Card */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Brain className="w-5 h-5 text-cosmic-primary" />
                Learning Insights
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="p-3 rounded-lg bg-accent-success/10 border border-accent-success/30">
                <p className="text-text-primary font-medium mb-1">Strong Growth</p>
                <p className="text-text-secondary">
                  Your questions have become {Math.round((mockQuestionEvolution.length * 100) / mockQuestionEvolution.length)}% more sophisticated
                </p>
              </div>

              <div className="p-3 rounded-lg bg-accent-primary/10 border border-accent-primary/30">
                <p className="text-text-primary font-medium mb-1">Topic Evolution</p>
                <p className="text-text-secondary">
                  Started with basics, now exploring {mockQuestionEvolution[mockQuestionEvolution.length - 1].topic}
                </p>
              </div>

              <div className="p-3 rounded-lg bg-bg-elevated border border-border-default">
                <p className="text-text-primary font-medium mb-1">Keep Growing!</p>
                <p className="text-text-secondary text-xs">
                  Continue asking deeper questions to accelerate your understanding
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Call to Action */}
      <Card className="mt-8 bg-gradient-to-r from-cosmic-primary/10 to-cosmic-purple/10 border-cosmic-primary/30">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold text-text-primary mb-2">Ready to Continue Your Journey?</h3>
              <p className="text-text-secondary">
                Use AI Mentor to explore advanced topics and deepen your understanding
              </p>
            </div>
            <div className="flex gap-3">
              <Button variant="primary" onClick={() => router.push('/ai-mentor')}>
                <MessageSquare className="w-4 h-4 mr-2" />
                Ask AI Mentor
              </Button>
              <Button variant="outline" onClick={() => router.push('/chapters')}>
                <ArrowRight className="w-4 h-4 mr-2" />
                Continue Learning
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </PageContainer>
  );
}
