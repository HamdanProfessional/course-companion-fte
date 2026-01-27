"""
Cloudflare R2 storage client (S3-compatible).
Zero-LLM compliance: Static content storage only, no LLM services.
"""

import boto3
from botocore.client import Config
from typing import Optional

from src.core.config import settings


class R2Client:
    """
    Cloudflare R2 client for storing and retrieving course content.
    Uses S3-compatible API via boto3.
    """

    def __init__(
        self,
        account_id: Optional[str] = None,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        bucket_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
    ):
        """
        Initialize R2 client.

        Args:
            account_id: Cloudflare R2 account ID
            access_key_id: R2 access key ID
            secret_access_key: R2 secret access key
            bucket_name: R2 bucket name
            endpoint_url: R2 endpoint URL
        """
        self.account_id = account_id or settings.r2_account_id
        self.access_key_id = access_key_id or settings.r2_access_key_id
        self.secret_access_key = secret_access_key or settings.r2_secret_access_key
        self.bucket_name = bucket_name or settings.r2_bucket_name
        self.endpoint_url = endpoint_url or settings.r2_endpoint_url

        # Initialize S3 client with R2 configuration
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            config=Config(signature_version="s3v4"),
            region_name="auto",
        )

    def get_object(self, key: str) -> Optional[str]:
        """
        Retrieve content from R2.

        Args:
            key: Object key in R2 bucket

        Returns:
            Content as string, or None if not found
        """
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return response["Body"].read().decode("utf-8")
        except self.s3_client.exceptions.NoSuchKey:
            return None
        except Exception as e:
            print(f"Error retrieving from R2: {e}")
            return None

    def put_object(self, key: str, content: str, content_type: str = "text/markdown") -> bool:
        """
        Store content in R2.

        Args:
            key: Object key in R2 bucket
            content: Content to store
            content_type: MIME type

        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=content.encode("utf-8"),
                ContentType=content_type
            )
            return True
        except Exception as e:
            print(f"Error storing to R2: {e}")
            return False

    def delete_object(self, key: str) -> bool:
        """
        Delete content from R2.

        Args:
            key: Object key in R2 bucket

        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception as e:
            print(f"Error deleting from R2: {e}")
            return False

    def list_objects(self, prefix: str = "") -> list:
        """
        List objects in R2 bucket with optional prefix filter.

        Args:
            prefix: Key prefix to filter

        Returns:
            List of object keys
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            return [obj["Key"] for obj in response.get("Contents", [])]
        except Exception as e:
            print(f"Error listing R2 objects: {e}")
            return []


# Global R2 client instance
r2_client = R2Client()
