"""
Certificates API Router - Course completion certificates.
Zero-Backend-LLM: Certificates generated deterministically.
Requirements: 100% course completion, 70%+ average score.
"""

from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.services.certificate_service import CertificateService
from src.models.schemas import (
    CertificateGenerate, Certificate, CertificateVerification, CertificateList
)
from src.api.dependencies import get_current_user, get_optional_user
from src.models.database import User

router = APIRouter()


@router.post("/generate", response_model=Certificate, status_code=status.HTTP_201_CREATED)
async def generate_certificate(
    certificate_data: CertificateGenerate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a course completion certificate.

    Zero-LLM compliance: Certificate generated deterministically based on requirements.

    Requirements:
        - 100% course completion
        - 70%+ average quiz score

    Certificate ID Format: CERT-XXXXXX (random alphanumeric)

    Args:
        certificate_data: Student name for certificate

    Returns:
        Generated certificate

    Raises:
        HTTPException 400: If user not eligible

    **Authentication**: Required - Users must be logged in to generate certificates.
    """
    service = CertificateService(db)

    # Check eligibility first
    eligibility = await service.check_eligibility(current_user.id)

    if not eligibility["eligible"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "User not eligible for certificate",
                "reason": eligibility.get("reason"),
                "current_completion": eligibility["completion_percentage"],
                "required_completion": eligibility["min_completion_required"],
                "current_score": eligibility["average_score"],
                "required_score": eligibility["min_score_required"]
            }
        )

    # Generate certificate
    certificate = await service.generate_certificate(current_user.id, certificate_data)

    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate certificate"
        )

    return certificate


@router.get("/", response_model=CertificateList)
async def get_user_certificates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all certificates for a user.

    Zero-LLM compliance: Simple database query.

    Returns:
        List of user's certificates

    **Authentication**: Required - Users must be logged in to view their certificates.
    """
    service = CertificateService(db)
    certificates = await service.get_user_certificates(current_user.id)
    return certificates


# IMPORTANT: /check-eligibility must come before /{certificate_uuid}
# Otherwise FastAPI will try to parse "check-eligibility" as a UUID
@router.post("/check-eligibility")
async def check_certificate_eligibility(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check if user is eligible for a certificate.

    Zero-LLM compliance: Returns eligibility based on deterministic rules.

    Requirements:
        - 100% course completion
        - 70%+ average quiz score

    Returns:
        Eligibility status with details

    **Authentication**: Required - Users must be logged in to check eligibility.
    """
    service = CertificateService(db)
    eligibility = await service.check_eligibility(current_user.id)
    return eligibility


@router.get("/{certificate_uuid}", response_model=Certificate)
async def get_certificate(
    certificate_uuid: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get certificate by internal UUID.

    Zero-LLM compliance: Simple database lookup.

    Args:
        certificate_uuid: Internal certificate UUID

    Returns:
        Certificate details

    Raises:
        HTTPException 404: If certificate not found
    """
    service = CertificateService(db)
    certificate = await service.get_certificate_by_internal_id(certificate_uuid)

    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found"
        )

    return certificate


@router.delete("/{certificate_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_certificate(
    certificate_uuid: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a certificate (admin only).

    Zero-LLM compliance: Simple database deletion.

    Args:
        certificate_uuid: Internal certificate UUID

    Returns:
        No content on success

    Raises:
        HTTPException 404: If certificate not found
    """
    service = CertificateService(db)
    deleted = await service.delete_certificate(certificate_uuid)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found"
        )

    return None
