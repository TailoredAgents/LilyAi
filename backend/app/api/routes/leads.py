from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
import structlog
from app.integrations.s3_client import S3Client

logger = structlog.get_logger()
router = APIRouter()

class PhotoPresignRequest(BaseModel):
    tenant_id: str
    lead_id: str
    file_extension: str = 'jpg'
    expiration_seconds: int = 3600

class PhotoPresignResponse(BaseModel):
    upload_url: str
    fields: dict
    file_key: str
    file_id: str
    expires_at: str
    max_size_bytes: int

class PhotoListResponse(BaseModel):
    photos: List[dict]

@router.post("/leads/{lead_id}/photos/presign", response_model=PhotoPresignResponse)
async def presign_photo_upload(lead_id: str, request: PhotoPresignRequest):
    """
    Generate a presigned URL for photo upload
    
    This endpoint allows clients to upload photos directly to S3
    without going through the server, improving performance and reducing load.
    """
    try:
        s3_client = S3Client()
        
        presigned_data = s3_client.generate_presigned_upload_url(
            tenant_id=request.tenant_id,
            lead_id=lead_id,
            file_extension=request.file_extension,
            expiration=request.expiration_seconds
        )
        
        if not presigned_data:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Photo upload service not available"
            )
        
        return PhotoPresignResponse(**presigned_data)
        
    except Exception as e:
        logger.error(
            "Error generating presigned URL",
            error=str(e),
            lead_id=lead_id,
            tenant_id=request.tenant_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate upload URL"
        )

@router.get("/leads/{lead_id}/photos/{file_key}/download")
async def get_photo_download_url(lead_id: str, file_key: str, expiration: int = 3600):
    """Generate a presigned URL for photo download"""
    try:
        s3_client = S3Client()
        
        download_url = s3_client.generate_presigned_download_url(
            file_key=file_key,
            expiration=expiration
        )
        
        if not download_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Photo not found or service unavailable"
            )
        
        return {
            "download_url": download_url,
            "expires_in_seconds": expiration
        }
        
    except Exception as e:
        logger.error(
            "Error generating download URL",
            error=str(e),
            lead_id=lead_id,
            file_key=file_key
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate download URL"
        )

@router.get("/leads/{lead_id}/photos", response_model=PhotoListResponse)
async def list_lead_photos(lead_id: str, tenant_id: str):
    """List all photos for a lead"""
    try:
        s3_client = S3Client()
        
        photos = s3_client.list_tenant_photos(
            tenant_id=tenant_id,
            lead_id=lead_id
        )
        
        return PhotoListResponse(photos=photos)
        
    except Exception as e:
        logger.error(
            "Error listing photos",
            error=str(e),
            lead_id=lead_id,
            tenant_id=tenant_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list photos"
        )

@router.delete("/leads/{lead_id}/photos/{file_key}")
async def delete_lead_photo(lead_id: str, file_key: str):
    """Delete a photo"""
    try:
        s3_client = S3Client()
        
        success = s3_client.delete_photo(file_key)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Photo not found or delete failed"
            )
        
        return {"status": "deleted"}
        
    except Exception as e:
        logger.error(
            "Error deleting photo",
            error=str(e),
            lead_id=lead_id,
            file_key=file_key
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete photo"
        )