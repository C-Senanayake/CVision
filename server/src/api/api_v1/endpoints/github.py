"""
GitHub Enrichment Endpoints
API endpoints for GitHub data extraction and enrichment
"""

from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from typing import Optional

from schemas.github import (
    GitHubEnrichmentResponse,
    GitHubURLValidationRequest,
    GitHubURLValidationResponse,
    GitHubData
)
from models.cv import CV
from utils.github_extractor import GitHubExtractor
from config.config import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/enrich/{cv_id}", response_model=GitHubEnrichmentResponse)
async def enrich_github_data(
    cv_id: str,
    force_refresh: bool = False
):
    """
    Enrich CV with GitHub profile data
    
    Process:
    1. Fetch CV from database
    2. Extract GitHub URL from resumeContent
    3. Fetch GitHub data using REST API
    4. Store enriched data in CV document
    5. Return enrichment status
    
    Args:
        cv_id: MongoDB ObjectId of CV document
        force_refresh: Force refresh even if GitHub data exists
        
    Returns:
        Enrichment response with GitHub data
    """
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(cv_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid CV ID format"
            )
        
        # Fetch CV from database
        cv_data = CV.get_cv_by_id(cv_id)
        if not cv_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"CV with ID {cv_id} not found"
            )
        
        # Check if already enriched (unless force refresh)
        if not force_refresh and cv_data.get("githubData"):
            return GitHubEnrichmentResponse(
                cv_id=cv_id,
                status="already_enriched",
                message="GitHub data already exists. Use force_refresh=true to update.",
                github_data=GitHubData(**cv_data["githubData"]),
                enriched_at=cv_data["githubData"].get("fetched_at", datetime.utcnow().isoformat())
            )
        
        # Extract GitHub URL from CV
        resume_content = cv_data.get("resumeContent", {})
        personal_info = resume_content.get("personal_info", {})
        github_url = personal_info.get("github", "")
        
        if not github_url:
            return GitHubEnrichmentResponse(
                cv_id=cv_id,
                status="no_github_url",
                message="No GitHub URL found in CV",
                github_data=None,
                enriched_at=datetime.utcnow().isoformat()
            )
        
        # Extract username from URL
        extractor = GitHubExtractor(token=settings.GITHUB_API_TOKEN)
        username = GitHubExtractor.extract_username_from_url(github_url)
        
        if not username:
            return GitHubEnrichmentResponse(
                cv_id=cv_id,
                status="invalid_github_url",
                message=f"Could not extract username from GitHub URL: {github_url}",
                github_data=None,
                enriched_at=datetime.utcnow().isoformat()
            )
        
        logger.info(f"Fetching GitHub data for username: {username}")
        
        # Fetch complete GitHub profile
        github_data = await extractor.get_complete_profile(username)
        
        # Store in database
        CV.update_github_data(cv_id, github_data)
        
        # Prepare response
        if github_data["fetch_status"] == "success":
            response_status = "success"
            message = f"Successfully enriched CV with GitHub data for user {username}"
        elif github_data["fetch_status"] == "user_not_found":
            response_status = "user_not_found"
            message = f"GitHub user '{username}' not found"
        else:
            response_status = "error"
            message = f"Error fetching GitHub data: {github_data.get('error', 'Unknown error')}"
        
        return GitHubEnrichmentResponse(
            cv_id=cv_id,
            status=response_status,
            message=message,
            github_data=GitHubData(**github_data) if github_data else None,
            enriched_at=github_data.get("fetched_at", datetime.utcnow().isoformat())
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enriching GitHub data for CV {cv_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enrich GitHub data: {str(e)}"
        )


@router.post("/validate_url", response_model=GitHubURLValidationResponse)
async def validate_github_url(request: GitHubURLValidationRequest):
    """
    Validate GitHub URL and extract username
    
    Args:
        request: GitHub URL validation request
        
    Returns:
        Validation response with username if valid
    """
    try:
        username = GitHubExtractor.extract_username_from_url(request.github_url)
        
        if username:
            return GitHubURLValidationResponse(
                is_valid=True,
                username=username,
                error=None
            )
        else:
            return GitHubURLValidationResponse(
                is_valid=False,
                username=None,
                error="Invalid GitHub URL format"
            )
    except Exception as e:
        return GitHubURLValidationResponse(
            is_valid=False,
            username=None,
            error=str(e)
        )


@router.get("/status/{cv_id}")
async def get_github_enrichment_status(cv_id: str):
    """
    Check GitHub enrichment status for a CV
    
    Args:
        cv_id: MongoDB ObjectId of CV document
        
    Returns:
        Enrichment status information
    """
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(cv_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid CV ID format"
            )
        
        # Fetch CV
        cv_data = CV.get_cv_by_id(cv_id)
        if not cv_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"CV with ID {cv_id} not found"
            )
        
        github_data = cv_data.get("githubData")
        
        if github_data:
            return {
                "cv_id": cv_id,
                "is_enriched": True,
                "fetch_status": github_data.get("fetch_status"),
                "fetched_at": github_data.get("fetched_at"),
                "username": github_data.get("profile", {}).get("username") if github_data.get("profile") else None,
                "has_error": github_data.get("fetch_status") == "error",
                "error_message": github_data.get("error")
            }
        else:
            # Check if GitHub URL exists in CV
            resume_content = cv_data.get("resumeContent", {})
            personal_info = resume_content.get("personal_info", {})
            github_url = personal_info.get("github", "")
            
            return {
                "cv_id": cv_id,
                "is_enriched": False,
                "has_github_url": bool(github_url),
                "github_url": github_url,
                "fetch_status": None,
                "fetched_at": None,
                "username": None
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking GitHub status for CV {cv_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check GitHub enrichment status: {str(e)}"
        )


@router.get("/rate_limit")
async def check_github_rate_limit():
    """
    Check current GitHub API rate limit status
    
    Returns:
        Rate limit information
    """
    try:
        extractor = GitHubExtractor(token=settings.GITHUB_API_TOKEN)
        rate_limit = await extractor.check_rate_limit()
        
        return {
            "rate_limit": rate_limit.get("limit"),
            "remaining": rate_limit.get("remaining"),
            "used": rate_limit.get("used"),
            "reset_at": rate_limit.get("reset"),
            "has_token": bool(settings.GITHUB_API_TOKEN)
        }
    except Exception as e:
        logger.error(f"Error checking rate limit: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check rate limit: {str(e)}"
        )
