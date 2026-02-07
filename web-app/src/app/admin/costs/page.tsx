'use client';

/**
 * Cost Tracking Dashboard - Phase 3
 *
 * Admin dashboard for monitoring LLM usage costs.
 * Pro tier feature for understanding AI operational costs.
 */

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingSpinner } from '@/components/ui/Loading';
import { PageContainer, PageHeader } from '@/components/layout/PageContainer';
import { useV3LLMCosts, useV3AIStatus, useV3SubscriptionInfo } from '@/hooks/useV3';
import { BarChart3, Lightbulb } from 'lucide-react';

const TIME_PERIODS = [
  { value: '7d', label: 'Last 7 days' },
  { value: '30d', label: 'Last 30 days' },
  { value: '90d', label: 'Last 90 days' },
  { value: 'all', label: 'All time' },
];

export default function CostsDashboardPage() {
  const [period, setPeriod] = useState('all');
  const { data: costs, isLoading } = useV3LLMCosts();
  const { data: aiStatus } = useV3AIStatus();
  const { data: subscription } = useV3SubscriptionInfo();

  // Check if user is Pro
  const isPro = subscription?.current_tier === 'PRO';

  if (!isPro) {
    return (
      <PageContainer>
        <Card>
          <CardContent className="p-8 text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-gradient-to-br from-accent-info/20 to-accent-info/10 flex items-center justify-center">
              <BarChart3 className="w-10 h-10 text-accent-info" />
            </div>
            <h2 className="text-2xl font-bold mb-2">Pro Feature</h2>
            <p className="text-text-secondary mb-6 max-w-md mx-auto">
              The cost tracking dashboard is available to Pro subscribers who need detailed
              insights into AI usage and operational costs.
            </p>
            <Button variant="primary">Upgrade to Pro</Button>
          </CardContent>
        </Card>
      </PageContainer>
    );
  }

  if (isLoading) {
    return (
      <PageContainer>
        <div className="flex items-center justify-center min-h-[50vh]">
          <LoadingSpinner size="lg" />
        </div>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <PageHeader
        title="Cost Tracking Dashboard"
        description="Monitor LLM usage and operational costs"
      />

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="text-sm text-text-muted mb-2">Total Requests</div>
            <div className="text-3xl font-bold text-text-primary">
              {costs?.total_requests || 0}
            </div>
            <div className="text-xs text-text-muted mt-1">{period}</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="text-sm text-text-muted mb-2">Total Cost</div>
            <div className="text-3xl font-bold text-accent-primary">
              ${(costs?.total_cost_usd || 0).toFixed(4)}
            </div>
            <div className="text-xs text-text-muted mt-1">USD</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="text-sm text-text-muted mb-2">Avg Cost/Request</div>
            <div className="text-3xl font-bold text-accent-secondary">
              ${(costs?.average_cost_per_request || 0).toFixed(6)}
            </div>
            <div className="text-xs text-text-muted mt-1">Per API call</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="text-sm text-text-muted mb-2">LLM Provider</div>
            <div className="text-3xl font-bold text-text-primary uppercase">
              {aiStatus?.llm_provider || 'N/A'}
            </div>
            <div className="text-xs text-text-muted mt-1">{aiStatus?.model || ''}</div>
          </CardContent>
        </Card>
      </div>

      {/* Cost Breakdown */}
      {costs?.cost_breakdown && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Cost Breakdown by Feature</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(costs.cost_breakdown).map(([feature, data]: [string, any]) => (
                <div key={feature} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-text-primary capitalize">
                      {feature.replace(/_/g, ' ')}
                    </span>
                    <span className="text-sm text-text-secondary">
                      {data.requests || 0} requests
                    </span>
                  </div>
                  <div className="relative h-4 bg-bg-elevated rounded-full overflow-hidden">
                    <div
                      className="absolute h-full bg-accent-primary rounded-full transition-all"
                      style={{
                        width: `${((data.cost || 0) / (costs.total_cost_usd || 1)) * 100}%`,
                      }}
                    />
                  </div>
                  <div className="flex items-center justify-between text-xs text-text-muted">
                    <span>${(data.cost || 0).toFixed(6)}</span>
                    <span>
                      {((data.cost || 0) / (costs.total_cost_usd || 1) * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Cost Optimization Tips */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-warning/20 to-accent-warning/10 flex items-center justify-center">
              <Lightbulb className="w-6 h-6 text-accent-warning" />
            </div>
            Cost Optimization Tips
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-lg bg-bg-elevated">
              <h4 className="font-semibold text-text-primary mb-2">Use Hybrid Grading</h4>
              <p className="text-sm text-text-secondary">
                Combine rule-based grading for multiple choice with LLM grading only for
                open-ended answers to reduce costs by 60-70%.
              </p>
            </div>
            <div className="p-4 rounded-lg bg-bg-elevated">
              <h4 className="font-semibold text-text-primary mb-2">Cache Explanations</h4>
              <p className="text-sm text-text-secondary">
                Generate AI explanations once and cache them for repeated questions
                instead of regenerating for each user.
              </p>
            </div>
            <div className="p-4 rounded-lg bg-bg-elevated">
              <h4 className="font-semibold text-text-primary mb-2">Batch Requests</h4>
              <p className="text-sm text-text-secondary">
                Process multiple quiz submissions in a single LLM request when possible
                to reduce API overhead.
              </p>
            </div>
            <div className="p-4 rounded-lg bg-bg-elevated">
              <h4 className="font-semibold text-text-primary mb-2">Set Token Limits</h4>
              <p className="text-sm text-text-secondary">
                Configure appropriate max_tokens for each request type to avoid
                paying for unnecessary output length.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Pricing Info */}
      <Card>
        <CardHeader>
          <CardTitle>Current Pricing</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-text-secondary space-y-2">
            <p>
              <strong>Model:</strong> {aiStatus?.model || 'N/A'}
            </p>
            <p>
              <strong>Provider:</strong> {aiStatus?.llm_provider || 'N/A'}
            </p>
            <p className="text-text-muted mt-4">
              Note: Actual costs may vary based on prompt length, response length, and
              current provider pricing. Check the provider's pricing page for most
              up-to-date information.
            </p>
          </div>
        </CardContent>
      </Card>
    </PageContainer>
  );
}
