"""
Public Certificate Verification API - No authentication required.
Zero-Backend-LLM: Public read-only endpoint for certificate verification.
"""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.services.certificate_service import CertificateService
from src.models.schemas import CertificateVerification

router = APIRouter()


@router.get("/verify/{certificate_id}", response_model=CertificateVerification)
async def verify_certificate(
    certificate_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Public endpoint to verify a certificate.

    Zero-LLM compliance: Simple database lookup and verification counter increment.

    No authentication required - anyone can verify a certificate.

    Args:
        certificate_id: Certificate ID (e.g., CERT-ABC123)

    Returns:
        Certificate verification details

    Raises:
        HTTPException 404: If certificate not found
    """
    service = CertificateService(db)

    # Clean certificate ID format (uppercase, strip spaces)
    certificate_id = certificate_id.strip().upper()

    verification = await service.verify_certificate(certificate_id)

    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found. Please check the certificate ID."
        )

    return verification
