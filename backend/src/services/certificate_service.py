"""
Certificate Service - Manages course completion certificates.
Zero-Backend-LLM: All certificates are generated deterministically.
Requirements: 100% course completion, 70%+ average score.
"""

import uuid
import random
import string
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import Certificate, QuizAttempt
from src.models.schemas import CertificateGenerate, Certificate, CertificateVerification, CertificateList


class CertificateService:
    """Service for managing course completion certificates."""

    # Constants for certificate generation
    CERTIFICATE_LENGTH = 6
    CERTIFICATE_PREFIX = "CERT"
    MIN_COMPLETION_PERCENTAGE = 100  # Must complete 100% of course
    MIN_AVERAGE_SCORE = 70  # Must have 70%+ average score

    def __init__(self, db: AsyncSession):
        self.db = db

    def _generate_certificate_id(self) -> str:
        """
        Generate a unique certificate ID.
        Format: CERT-XXXXXX where X is uppercase alphanumeric.

        Returns:
            Unique certificate ID
        """
        # Generate random alphanumeric characters
        chars = string.ascii_uppercase + string.digits
        suffix = ''.join(random.choice(chars) for _ in range(self.CERTIFICATE_LENGTH))
        return f"{self.CERTIFICATE_PREFIX}-{suffix}"

    async def _is_certificate_id_unique(self, certificate_id: str) -> bool:
        """
        Check if certificate ID is unique.

        Args:
            certificate_id: Certificate ID to check

        Returns:
            True if unique, False otherwise
        """
        query = select(Certificate).where(
            Certificate.certificate_id == certificate_id
        )
        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()
        return existing is None

    async def _get_average_quiz_score(self, user_id: uuid.UUID) -> float:
        """
        Get user's average quiz score.

        Args:
            user_id: User UUID

        Returns:
            Average quiz score percentage
        """
        from sqlalchemy import func

        query = select(func.avg(QuizAttempt.score)).where(
            QuizAttempt.user_id == user_id
        )
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def check_eligibility(self, user_id: uuid.UUID) -> dict:
        """
        Check if user is eligible for a certificate.

        Args:
            user_id: User UUID

        Returns:
            Dictionary with eligibility status and details
        """
        from src.models.database import Progress, Streak

        # Get progress
        progress_query = select(Progress).where(Progress.user_id == user_id)
        progress_result = await self.db.execute(progress_query)
        progress = progress_result.scalar_one_or_none()

        if not progress:
            return {
                "eligible": False,
                "reason": "No progress record found",
                "completion_percentage": 0,
                "average_score": 0,
                "min_completion_required": self.MIN_COMPLETION_PERCENTAGE,
                "min_score_required": self.MIN_AVERAGE_SCORE
            }

        # Get total chapters count
        from src.models.database import Chapter
        chapter_query = select(func.count(Chapter.id))
        chapter_result = await self.db.execute(chapter_query)
        total_chapters = chapter_result.scalar() or 1

        # Calculate completion percentage
        completed_chapters = len(progress.completed_chapters) if progress.completed_chapters else 0
        completion_percentage = int((completed_chapters / total_chapters) * 100)

        # Get average quiz score
        quiz_query = select(func.avg(QuizAttempt.score)).where(
            QuizAttempt.user_id == user_id
        )
        quiz_result = await self.db.execute(quiz_query)
        average_score = quiz_result.scalar() or 0

        # Get streak
        streak_query = select(Streak).where(Streak.user_id == user_id)
        streak_result = await self.db.execute(streak_query)
        streak = streak_result.scalar_one_or_none()
        streak_days = streak.current_streak if streak else 0

        # Check eligibility
        eligible = (
            completion_percentage >= self.MIN_COMPLETION_PERCENTAGE and
            average_score >= self.MIN_AVERAGE_SCORE
        )

        return {
            "eligible": eligible,
            "completion_percentage": completion_percentage,
            "average_score": average_score,
            "completed_chapters": completed_chapters,
            "total_streak_days": streak_days,
            "min_completion_required": self.MIN_COMPLETION_PERCENTAGE,
            "min_score_required": self.MIN_AVERAGE_SCORE,
            "reason": None if eligible else "Requirements not met"
        }

    async def generate_certificate(
        self,
        user_id: uuid.UUID,
        certificate_data: CertificateGenerate
    ) -> Optional[Certificate]:
        """
        Generate a certificate for a user.

        Args:
            user_id: User UUID
            certificate_data: Certificate generation data

        Returns:
            Generated certificate or None if not eligible
        """
        # Check eligibility first
        eligibility = await self.check_eligibility(user_id)

        if not eligibility["eligible"]:
            return None

        # Generate unique certificate ID
        max_attempts = 10
        certificate_id = None

        for _ in range(max_attempts):
            cert_id = self._generate_certificate_id()
            if await self._is_certificate_id_unique(cert_id):
                certificate_id = cert_id
                break

        if not certificate_id:
            # Fallback to timestamp-based ID
            timestamp_suffix = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            certificate_id = f"{self.CERTIFICATE_PREFIX}-{timestamp_suffix[-6:]}"

        # Create certificate
        certificate = Certificate(
            certificate_id=certificate_id,
            user_id=user_id,
            student_name=certificate_data.student_name,
            completion_percentage=eligibility["completion_percentage"],
            average_quiz_score=int(eligibility["average_score"]),
            total_chapters_completed=eligibility["completed_chapters"],
            total_streak_days=eligibility["total_streak_days"]
        )

        self.db.add(certificate)
        await self.db.commit()
        await self.db.refresh(certificate)

        return certificate

    async def get_certificate_by_id(self, certificate_id: str) -> Optional[Certificate]:
        """
        Get certificate by certificate ID.

        Args:
            certificate_id: Certificate ID (e.g., CERT-ABC123)

        Returns:
            Certificate or None if not found
        """
        query = select(Certificate).where(
            Certificate.certificate_id == certificate_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def verify_certificate(self, certificate_id: str) -> Optional[CertificateVerification]:
        """
        Verify a certificate and update verification stats.

        Args:
            certificate_id: Certificate ID

        Returns:
            Certificate verification details or None if not found
        """
        certificate = await self.get_certificate_by_id(certificate_id)

        if not certificate:
            return None

        # Update verification stats
        certificate.verified_at = datetime.utcnow()
        certificate.verification_count += 1
        await self.db.commit()

        # Create verification response
        verification = CertificateVerification(
            certificate_id=certificate.certificate_id,
            is_valid=True,
            student_name=certificate.student_name,
            completion_percentage=certificate.completion_percentage,
            average_quiz_score=certificate.average_quiz_score,
            total_chapters_completed=certificate.total_chapters_completed,
            total_streak_days=certificate.total_streak_days,
            issued_at=certificate.issued_at,
            verified_at=certificate.verified_at,
            verification_url=f"/certificate/verify/{certificate.certificate_id}"
        )

        return verification

    async def get_user_certificates(
        self,
        user_id: uuid.UUID
    ) -> CertificateList:
        """
        Get all certificates for a user.

        Args:
            user_id: User UUID

        Returns:
            List of user certificates
        """
        query = select(Certificate).where(
            Certificate.user_id == user_id
        ).order_by(Certificate.issued_at.desc())

        result = await self.db.execute(query)
        certificates = result.scalars().all()

        return CertificateList(
            certificates=list(certificates),
            total=len(certificates)
        )

    async def get_certificate_by_internal_id(self, certificate_uuid: uuid.UUID) -> Optional[Certificate]:
        """
        Get certificate by internal UUID.

        Args:
            certificate_uuid: Internal certificate UUID

        Returns:
            Certificate or None if not found
        """
        query = select(Certificate).where(Certificate.id == certificate_uuid)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def delete_certificate(self, certificate_uuid: uuid.UUID) -> bool:
        """
        Delete a certificate (admin function).

        Args:
            certificate_uuid: Internal certificate UUID

        Returns:
            True if deleted, False if not found
        """
        certificate = await self.get_certificate_by_internal_id(certificate_uuid)

        if not certificate:
            return False

        await self.db.delete(certificate)
        await self.db.commit()
        return True
