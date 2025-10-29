"""
GitHub Data Schemas
Pydantic models for GitHub profile and enrichment data
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime


class GitHubRepository(BaseModel):
    """GitHub repository information"""
    name: str
    full_name: str
    description: Optional[str] = None
    html_url: str
    homepage: Optional[str] = None
    language: Optional[str] = None
    stargazers_count: int = 0
    watchers_count: int = 0
    forks_count: int = 0
    open_issues_count: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    pushed_at: Optional[str] = None
    size: int = 0
    topics: List[str] = Field(default_factory=list)
    is_fork: bool = False
    archived: bool = False


class GitHubProfile(BaseModel):
    """GitHub user profile information"""
    username: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    email: Optional[str] = None
    blog: Optional[str] = None
    twitter_username: Optional[str] = None
    public_repos: int = 0
    public_gists: int = 0
    followers: int = 0
    following: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    hireable: Optional[bool] = None
    profile_url: str


class LanguageStats(BaseModel):
    """Programming language usage statistics"""
    language: str
    repo_count: int


class LanguageAnalysis(BaseModel):
    """Complete language analysis"""
    languages: List[LanguageStats] = Field(default_factory=list)
    total_languages: int = 0
    primary_language: Optional[str] = None


class TopRepository(BaseModel):
    """Top repository summary"""
    name: str
    stars: int
    forks: int
    language: Optional[str] = None
    url: str


class RepositoryStatistics(BaseModel):
    """Aggregate repository statistics"""
    total_repositories: int = 0
    total_original_repos: int = 0
    total_forks: int = 0
    total_stars: int = 0
    total_repository_forks: int = 0
    total_watchers: int = 0
    average_stars_per_repo: float = 0.0
    top_repositories: List[TopRepository] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)


class ActivityStatistics(BaseModel):
    """User activity statistics"""
    total_events: int = 0
    recent_activity_days: int = 0
    event_types: Dict[str, int] = Field(default_factory=dict)
    is_active: bool = False
    last_activity: Optional[str] = None


class GitHubStatistics(BaseModel):
    """Complete GitHub statistics"""
    repositories: RepositoryStatistics
    languages: LanguageAnalysis
    activity: ActivityStatistics
    account_age_days: int = 0
    account_age_years: float = 0.0


class GitHubData(BaseModel):
    """Complete GitHub enrichment data"""
    profile: Optional[GitHubProfile] = None
    statistics: Optional[GitHubStatistics] = None
    repositories: List[GitHubRepository] = Field(default_factory=list)
    fetch_status: str  # success, user_not_found, error
    error: Optional[str] = None
    fetched_at: str


class GitHubEnrichmentRequest(BaseModel):
    """Request schema for GitHub enrichment"""
    cv_id: str = Field(..., description="MongoDB ObjectId of the CV document")
    force_refresh: bool = Field(default=False, description="Force refresh even if data exists")


class GitHubEnrichmentResponse(BaseModel):
    """Response schema for GitHub enrichment"""
    cv_id: str
    status: str  # success, user_not_found, no_github_url, error
    message: str
    github_data: Optional[GitHubData] = None
    enriched_at: str


class GitHubURLValidationRequest(BaseModel):
    """Request to validate and extract GitHub username from URL"""
    github_url: str


class GitHubURLValidationResponse(BaseModel):
    """Response for GitHub URL validation"""
    is_valid: bool
    username: Optional[str] = None
    error: Optional[str] = None


class GitHubScoreInput(BaseModel):
    """GitHub data formatted for scoring system"""
    has_github: bool = False
    profile_exists: bool = False
    username: Optional[str] = None
    account_age_years: float = 0.0
    total_repositories: int = 0
    total_original_repos: int = 0
    total_stars: int = 0
    total_forks: int = 0
    followers: int = 0
    primary_language: Optional[str] = None
    languages_count: int = 0
    is_active: bool = False
    top_repos: List[Dict[str, Any]] = Field(default_factory=list)
    contribution_activity: str = "none"  # none, low, medium, high
