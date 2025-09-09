import boto3
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import structlog
from botocore.exceptions import ClientError, NoCredentialsError

from app.core.config import settings

logger = structlog.get_logger()

class S3Client:
    """S3 integration client for photo uploads and presigned URLs"""
    
    def __init__(self):
        self.client = None
        self.bucket_name = settings.S3_BUCKET_NAME
        
        if (settings.AWS_ACCESS_KEY_ID and 
            settings.AWS_SECRET_ACCESS_KEY and 
            settings.S3_BUCKET_NAME):
            try:
                self.client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION
                )
                logger.info("S3 client initialized", bucket=self.bucket_name)
            except Exception as e:
                logger.error("Failed to initialize S3 client", error=str(e))
        else:
            logger.warning("S3 credentials not configured - photo upload disabled")
    
    def generate_presigned_upload_url(
        self,
        tenant_id: str,
        lead_id: str,
        file_extension: str = 'jpg',
        expiration: int = 3600,
        max_size: int = 10 * 1024 * 1024  # 10MB
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a presigned URL for photo upload
        
        Args:
            tenant_id: Tenant ID for organizing uploads
            lead_id: Lead ID for associating photos
            file_extension: File extension (jpg, png, etc.)
            expiration: URL expiration time in seconds
            max_size: Maximum file size in bytes
        
        Returns:
            Dictionary with upload URL and metadata, or None if failed
        """
        if not self.client:
            logger.error("S3 client not available")
            return None
        
        try:
            # Generate unique file key
            file_id = str(uuid.uuid4())
            file_key = f"photos/{tenant_id}/{lead_id}/{file_id}.{file_extension}"
            
            # Generate presigned POST URL with conditions
            conditions = [
                {"bucket": self.bucket_name},
                {"key": file_key},
                ["content-length-range", 0, max_size],
                ["starts-with", "$Content-Type", "image/"]
            ]
            
            fields = {
                "key": file_key,
                "Content-Type": f"image/{file_extension}"
            }
            
            response = self.client.generate_presigned_post(
                Bucket=self.bucket_name,
                Key=file_key,
                Fields=fields,
                Conditions=conditions,
                ExpiresIn=expiration
            )
            
            logger.info(
                "Generated presigned upload URL",
                tenant_id=tenant_id,
                lead_id=lead_id,
                file_key=file_key,
                expiration=expiration
            )
            
            return {
                "upload_url": response["url"],
                "fields": response["fields"],
                "file_key": file_key,
                "file_id": file_id,
                "expires_at": (datetime.utcnow() + timedelta(seconds=expiration)).isoformat(),
                "max_size_bytes": max_size
            }
            
        except Exception as e:
            logger.error(
                "Failed to generate presigned upload URL",
                error=str(e),
                tenant_id=tenant_id,
                lead_id=lead_id
            )
            return None
    
    def generate_presigned_download_url(
        self,
        file_key: str,
        expiration: int = 3600
    ) -> Optional[str]:
        """
        Generate a presigned URL for photo download
        
        Args:
            file_key: S3 object key
            expiration: URL expiration time in seconds
        
        Returns:
            Presigned download URL or None if failed
        """
        if not self.client:
            logger.error("S3 client not available")
            return None
        
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_key},
                ExpiresIn=expiration
            )
            
            logger.info(
                "Generated presigned download URL",
                file_key=file_key,
                expiration=expiration
            )
            
            return url
            
        except Exception as e:
            logger.error(
                "Failed to generate presigned download URL",
                error=str(e),
                file_key=file_key
            )
            return None
    
    def delete_photo(self, file_key: str) -> bool:
        """
        Delete a photo from S3
        
        Args:
            file_key: S3 object key
        
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.error("S3 client not available")
            return False
        
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=file_key)
            
            logger.info("Deleted photo from S3", file_key=file_key)
            return True
            
        except Exception as e:
            logger.error(
                "Failed to delete photo from S3",
                error=str(e),
                file_key=file_key
            )
            return False
    
    def check_photo_exists(self, file_key: str) -> bool:
        """
        Check if a photo exists in S3
        
        Args:
            file_key: S3 object key
        
        Returns:
            True if photo exists, False otherwise
        """
        if not self.client:
            logger.error("S3 client not available")
            return False
        
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=file_key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                logger.error(
                    "Error checking photo existence",
                    error=str(e),
                    file_key=file_key
                )
                return False
    
    def get_photo_metadata(self, file_key: str) -> Optional[Dict[str, Any]]:
        """
        Get photo metadata from S3
        
        Args:
            file_key: S3 object key
        
        Returns:
            Photo metadata dictionary or None if failed
        """
        if not self.client:
            logger.error("S3 client not available")
            return None
        
        try:
            response = self.client.head_object(Bucket=self.bucket_name, Key=file_key)
            
            return {
                "file_key": file_key,
                "size_bytes": response.get('ContentLength'),
                "content_type": response.get('ContentType'),
                "last_modified": response.get('LastModified'),
                "etag": response.get('ETag', '').strip('"'),
                "metadata": response.get('Metadata', {})
            }
            
        except Exception as e:
            logger.error(
                "Failed to get photo metadata",
                error=str(e),
                file_key=file_key
            )
            return None
    
    def list_tenant_photos(
        self,
        tenant_id: str,
        lead_id: Optional[str] = None,
        max_keys: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List photos for a tenant/lead
        
        Args:
            tenant_id: Tenant ID
            lead_id: Optional lead ID to filter by
            max_keys: Maximum number of keys to return
        
        Returns:
            List of photo metadata dictionaries
        """
        if not self.client:
            logger.error("S3 client not available")
            return []
        
        try:
            if lead_id:
                prefix = f"photos/{tenant_id}/{lead_id}/"
            else:
                prefix = f"photos/{tenant_id}/"
            
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            photos = []
            for obj in response.get('Contents', []):
                photos.append({
                    "file_key": obj['Key'],
                    "size_bytes": obj['Size'],
                    "last_modified": obj['LastModified'],
                    "etag": obj['ETag'].strip('"')
                })
            
            logger.info(
                "Listed tenant photos",
                tenant_id=tenant_id,
                lead_id=lead_id,
                count=len(photos)
            )
            
            return photos
            
        except Exception as e:
            logger.error(
                "Failed to list tenant photos",
                error=str(e),
                tenant_id=tenant_id,
                lead_id=lead_id
            )
            return []