'use client';

/**
 * Certificate Verification Page - Public page for verifying certificates
 * No authentication required
 */

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Award, CheckCircle, XCircle, Calendar, BookOpen, TrendingUp, Clock, Download } from 'lucide-react';
import { PageContainer } from '@/components/layout/PageContainer';
import { GlassCard } from '@/components/ui/GlassCard';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { tutorApi, CertificateVerification } from '@/lib/api-v3';
import { pageVariants } from '@/lib/animations';

export default function CertificateVerifyPage() {
  const params = useParams();
  const router = useRouter();
  const certificateId = params.id as string;

  const [verification, setVerification] = useState<CertificateVerification | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (certificateId) {
      verifyCertificate();
    }
  }, [certificateId]);

  const verifyCertificate = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const result = await tutorApi.verifyCertificate(certificateId);
      setVerification(result);
    } catch (err) {
      console.error('Failed to verify certificate:', err);
      setError('Certificate not found. Please check the certificate ID and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const downloadCertificate = () => {
    window.print();
  };

  if (isLoading) {
    return (
      <PageContainer>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cosmic-primary" />
        </div>
      </PageContainer>
    );
  }

  if (error || !verification) {
    return (
      <PageContainer>
        <motion.div
          variants={pageVariants}
          initial="initial"
          animate="animate"
          exit="exit"
          className="max-w-2xl mx-auto py-12"
        >
          <GlassCard className="p-12 text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 200 }}
              className="w-20 h-20 mx-auto mb-6 rounded-full bg-red-500/20 flex items-center justify-center"
            >
              <XCircle className="w-10 h-10 text-red-500" />
            </motion.div>

            <h1 className="text-2xl font-bold text-text-primary mb-3">
              Certificate Not Found
            </h1>

            <p className="text-text-secondary mb-8">
              {error || 'The certificate could not be verified. Please check the certificate ID.'}
            </p>

            <Button
              variant="outline"
              onClick={() => router.push('/')}
            >
              Return to Home
            </Button>
          </GlassCard>
        </motion.div>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <motion.div
        variants={pageVariants}
        initial="initial"
        animate="animate"
        exit="exit"
        className="max-w-4xl mx-auto py-12 print:py-0"
      >
        {/* Certificate Document */}
        <GlassCard className="overflow-hidden print:shadow-none print:border-2">
          {/* Header */}
          <div className="bg-gradient-to-r from-cosmic-primary to-cosmic-purple p-8 text-center">
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5 }}
              className="w-20 h-20 mx-auto mb-4 rounded-full bg-white/20 flex items-center justify-center backdrop-blur-sm"
            >
              <Award className="w-10 h-10 text-white" />
            </motion.div>

            <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">
              Certificate of Completion
            </h1>

            <p className="text-white/80">
              Course Companion FTE - AI Agent Development
            </p>
          </div>

          {/* Certificate Content */}
          <div className="p-8 md:p-12">
            {/* Verification Status */}
            <div className="flex justify-center mb-8 print:hidden">
              <Badge variant="success" className="text-sm gap-1 px-4 py-2">
                <CheckCircle className="w-4 h-4" />
                Verified Certificate
              </Badge>
            </div>

            {/* Certificate ID */}
            <div className="text-center mb-8">
              <p className="text-sm text-text-secondary uppercase tracking-wider">Certificate ID</p>
              <p className="text-2xl font-mono font-bold text-cosmic-primary mt-1">
                {verification.certificate_id}
              </p>
            </div>

            {/* Student Name */}
            <div className="text-center mb-8">
              <p className="text-sm text-text-secondary uppercase tracking-wider mb-2">Presented To</p>
              <h2 className="text-3xl font-bold text-text-primary">
                {verification.student_name}
              </h2>
            </div>

            {/* Achievement Description */}
            <div className="text-center mb-10">
              <p className="text-lg text-text-secondary leading-relaxed max-w-2xl mx-auto">
                Has successfully completed the AI Agent Development course with distinction,
                demonstrating mastery of Model Context Protocol (MCP), Agent Architecture,
                and Reusable Skill Development.
              </p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="text-center p-4 rounded-xl bg-glass-hover border border-glass-border"
              >
                <div className="w-10 h-10 mx-auto mb-2 rounded-lg bg-cosmic-primary/20 flex items-center justify-center">
                  <BookOpen className="w-5 h-5 text-cosmic-primary" />
                </div>
                <p className="text-2xl font-bold text-text-primary">
                  {verification.completion_percentage}%
                </p>
                <p className="text-xs text-text-secondary">Completion</p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="text-center p-4 rounded-xl bg-glass-hover border border-glass-border"
              >
                <div className="w-10 h-10 mx-auto mb-2 rounded-lg bg-cosmic-purple/20 flex items-center justify-center">
                  <TrendingUp className="w-5 h-5 text-cosmic-purple" />
                </div>
                <p className="text-2xl font-bold text-text-primary">
                  {verification.average_quiz_score}%
                </p>
                <p className="text-xs text-text-secondary">Avg Score</p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="text-center p-4 rounded-xl bg-glass-hover border border-glass-border"
              >
                <div className="w-10 h-10 mx-auto mb-2 rounded-lg bg-green-500/20 flex items-center justify-center">
                  <BookOpen className="w-5 h-5 text-green-500" />
                </div>
                <p className="text-2xl font-bold text-text-primary">
                  {verification.total_chapters_completed}
                </p>
                <p className="text-xs text-text-secondary">Chapters</p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="text-center p-4 rounded-xl bg-glass-hover border border-glass-border"
              >
                <div className="w-10 h-10 mx-auto mb-2 rounded-lg bg-orange-500/20 flex items-center justify-center">
                  <Clock className="w-5 h-5 text-orange-500" />
                </div>
                <p className="text-2xl font-bold text-text-primary">
                  {verification.total_streak_days}
                </p>
                <p className="text-xs text-text-secondary">Day Streak</p>
              </motion.div>
            </div>

            {/* Issue Date */}
            <div className="text-center mb-8 pt-8 border-t border-glass-border">
              <p className="text-sm text-text-secondary uppercase tracking-wider mb-1">Issued On</p>
              <p className="text-lg font-semibold text-text-primary flex items-center justify-center gap-2">
                <Calendar className="w-5 h-5" />
                {formatDate(verification.issued_at)}
              </p>
            </div>

            {/* Verification Info */}
            <div className="text-center text-xs text-text-secondary print:hidden">
              <p>Verified on {formatDate(verification.verified_at)}</p>
              <p className="mt-1">This certificate can be verified at any time using the unique ID above.</p>
            </div>

            {/* Actions */}
            <div className="flex justify-center gap-4 mt-8 print:hidden">
              <Button
                variant="primary"
                onClick={downloadCertificate}
                className="gap-2"
              >
                <Download className="w-4 h-4" />
                Download / Print
              </Button>
              <Button
                variant="outline"
                onClick={() => router.push('/')}
              >
                Back to Home
              </Button>
            </div>
          </div>

          {/* Seal */}
          <div className="absolute bottom-8 right-8 print:relative print:bottom-auto print:right-auto print:mb-8">
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-cosmic-primary to-cosmic-purple flex items-center justify-center shadow-lg">
              <Award className="w-12 h-12 text-white" />
            </div>
          </div>
        </GlassCard>

        {/* Share Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-6 text-center print:hidden"
        >
          <p className="text-text-secondary text-sm">
            Share this certificate: {typeof window !== 'undefined' ? window.location.href : ''}
          </p>
        </motion.div>
      </motion.div>
    </PageContainer>
  );
}
