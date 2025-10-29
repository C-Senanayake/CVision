"""
GitHub Data Extraction Utility
Fetches user profile, repositories, and activity data from GitHub REST API v3
"""

import httpx
import re
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitHubExtractor:
    """GitHub REST API client for extracting user data"""
    
    BASE_URL = "https://api.github.com"
    API_VERSION = "2022-11-28"
    TIMEOUT = 10.0
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub API client
        
        Args:
            token: GitHub Personal Access Token (optional, but recommended for higher rate limits)
                   Without token: 60 requests/hour
                   With token: 5000 requests/hour
        """
        self.token = token
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": self.API_VERSION
        }
        
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
    
    @staticmethod
    def extract_username_from_url(github_url: str) -> Optional[str]:
        """
        Extract GitHub username from various URL formats
        
        Supported formats:
        - https://github.com/username
        - http://github.com/username
        - github.com/username
        - @username (if prepended with @)
        
        Args:
            github_url: GitHub profile URL or username
            
        Returns:
            Username string or None if invalid
        """
        if not github_url:
            return None
        
        # Remove whitespace
        github_url = github_url.strip()
        
        # Handle @username format
        if github_url.startswith("@"):
            return github_url[1:]
        
        # Extract from URL
        patterns = [
            r"(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9-]+)",
            r"^([a-zA-Z0-9-]+)$"  # Just username
        ]
        
        for pattern in patterns:
            match = re.search(pattern, github_url)
            if match:
                username = match.group(1)
                # Exclude common non-username paths
                if username.lower() not in ["login", "signup", "explore", "features", "pricing"]:
                    return username
        
        return None
    
    async def get_user_profile(self, username: str) -> Dict[str, Any]:
        """
        Fetch user profile information
        
        Endpoint: GET /users/{username}
        
        Args:
            username: GitHub username
            
        Returns:
            User profile data dictionary
        """
        url = f"{self.BASE_URL}/users/{username}"
        
        async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
            response = await client.get(url, headers=self.headers)
            
            if response.status_code == 404:
                raise ValueError(f"GitHub user '{username}' not found")
            elif response.status_code == 403:
                raise Exception("GitHub API rate limit exceeded")
            elif response.status_code != 200:
                raise Exception(f"GitHub API error: {response.status_code}")
            
            data = response.json()
            
            return {
                "username": data.get("login"),
                "name": data.get("name"),
                "avatar_url": data.get("avatar_url"),
                "bio": data.get("bio"),
                "company": data.get("company"),
                "location": data.get("location"),
                "email": data.get("email"),
                "blog": data.get("blog"),
                "twitter_username": data.get("twitter_username"),
                "public_repos": data.get("public_repos", 0),
                "public_gists": data.get("public_gists", 0),
                "followers": data.get("followers", 0),
                "following": data.get("following", 0),
                "created_at": data.get("created_at"),
                "updated_at": data.get("updated_at"),
                "hireable": data.get("hireable"),
                "profile_url": data.get("html_url")
            }
    
    async def get_user_repositories(self, username: str, max_repos: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch user's public repositories
        
        Endpoint: GET /users/{username}/repos
        
        Args:
            username: GitHub username
            max_repos: Maximum number of repositories to fetch (default 100)
            
        Returns:
            List of repository data dictionaries
        """
        url = f"{self.BASE_URL}/users/{username}/repos"
        params = {
            "per_page": min(max_repos, 100),
            "sort": "updated",
            "direction": "desc"
        }
        
        async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
            response = await client.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch repositories for {username}: {response.status_code}")
                return []
            
            repos_data = response.json()
            
            repositories = []
            for repo in repos_data:
                repositories.append({
                    "name": repo.get("name"),
                    "full_name": repo.get("full_name"),
                    "description": repo.get("description"),
                    "html_url": repo.get("html_url"),
                    "homepage": repo.get("homepage"),
                    "language": repo.get("language"),
                    "stargazers_count": repo.get("stargazers_count", 0),
                    "watchers_count": repo.get("watchers_count", 0),
                    "forks_count": repo.get("forks_count", 0),
                    "open_issues_count": repo.get("open_issues_count", 0),
                    "created_at": repo.get("created_at"),
                    "updated_at": repo.get("updated_at"),
                    "pushed_at": repo.get("pushed_at"),
                    "size": repo.get("size", 0),
                    "topics": repo.get("topics", []),
                    "is_fork": repo.get("fork", False),
                    "archived": repo.get("archived", False)
                })
            
            return repositories
    
    async def get_user_events(self, username: str, max_events: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch user's recent public activity events
        
        Endpoint: GET /users/{username}/events/public
        
        Args:
            username: GitHub username
            max_events: Maximum number of events to fetch (default 100)
            
        Returns:
            List of event data dictionaries
        """
        url = f"{self.BASE_URL}/users/{username}/events/public"
        params = {
            "per_page": min(max_events, 100)
        }
        
        async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
            response = await client.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch events for {username}: {response.status_code}")
                return []
            
            events_data = response.json()
            
            events = []
            for event in events_data:
                events.append({
                    "type": event.get("type"),
                    "created_at": event.get("created_at"),
                    "repo": event.get("repo", {}).get("name"),
                    "public": event.get("public", True)
                })
            
            return events
    
    def analyze_language_usage(self, repositories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze programming language usage from repositories
        
        Args:
            repositories: List of repository dictionaries
            
        Returns:
            Language statistics dictionary
        """
        language_count = {}
        total_repos = len(repositories)
        
        for repo in repositories:
            lang = repo.get("language")
            if lang:
                language_count[lang] = language_count.get(lang, 0) + 1
        
        # Sort by count descending
        sorted_languages = sorted(language_count.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "languages": [{"language": lang, "repo_count": count} for lang, count in sorted_languages],
            "total_languages": len(language_count),
            "primary_language": sorted_languages[0][0] if sorted_languages else None
        }
    
    def analyze_repository_statistics(self, repositories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate aggregate statistics from repositories
        
        Args:
            repositories: List of repository dictionaries
            
        Returns:
            Repository statistics dictionary
        """
        total_stars = sum(repo.get("stargazers_count", 0) for repo in repositories)
        total_forks = sum(repo.get("forks_count", 0) for repo in repositories)
        total_watchers = sum(repo.get("watchers_count", 0) for repo in repositories)
        
        # Find most popular repos
        sorted_by_stars = sorted(repositories, key=lambda x: x.get("stargazers_count", 0), reverse=True)
        top_repos = sorted_by_stars[:5]
        
        # Filter out forks
        original_repos = [repo for repo in repositories if not repo.get("is_fork", False)]
        
        # Get all unique topics
        all_topics = []
        for repo in repositories:
            all_topics.extend(repo.get("topics", []))
        unique_topics = list(set(all_topics))
        
        return {
            "total_repositories": len(repositories),
            "total_original_repos": len(original_repos),
            "total_forks": len(repositories) - len(original_repos),
            "total_stars": total_stars,
            "total_repository_forks": total_forks,
            "total_watchers": total_watchers,
            "average_stars_per_repo": round(total_stars / len(repositories), 2) if repositories else 0,
            "top_repositories": [
                {
                    "name": repo["name"],
                    "stars": repo["stargazers_count"],
                    "forks": repo["forks_count"],
                    "language": repo["language"],
                    "url": repo["html_url"]
                }
                for repo in top_repos
            ],
            "topics": unique_topics[:20]  # Limit to 20 most common topics
        }
    
    def analyze_activity(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze recent activity from events
        
        Args:
            events: List of event dictionaries
            
        Returns:
            Activity statistics dictionary
        """
        if not events:
            return {
                "total_events": 0,
                "recent_activity_days": 0,
                "event_types": {},
                "is_active": False
            }
        
        event_types = {}
        for event in events:
            event_type = event.get("type", "Unknown")
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        # Calculate activity timeframe
        if events:
            latest_event = events[0].get("created_at")
            oldest_event = events[-1].get("created_at")
            
            if latest_event and oldest_event:
                latest_dt = datetime.fromisoformat(latest_event.replace("Z", "+00:00"))
                oldest_dt = datetime.fromisoformat(oldest_event.replace("Z", "+00:00"))
                activity_days = (latest_dt - oldest_dt).days
            else:
                activity_days = 0
        else:
            activity_days = 0
        
        # Check if active in last 30 days
        if events:
            latest_event = events[0].get("created_at")
            if latest_event:
                latest_dt = datetime.fromisoformat(latest_event.replace("Z", "+00:00"))
                is_active = (datetime.now(latest_dt.tzinfo) - latest_dt).days <= 30
            else:
                is_active = False
        else:
            is_active = False
        
        return {
            "total_events": len(events),
            "recent_activity_days": activity_days,
            "event_types": event_types,
            "is_active": is_active,
            "last_activity": events[0].get("created_at") if events else None
        }
    
    async def get_complete_profile(self, username: str) -> Dict[str, Any]:
        """
        Fetch and analyze complete GitHub profile data
        
        Args:
            username: GitHub username
            
        Returns:
            Complete profile data with statistics
        """
        try:
            # Fetch all data
            profile = await self.get_user_profile(username)
            repositories = await self.get_user_repositories(username)
            events = await self.get_user_events(username)
            
            # Analyze data
            language_stats = self.analyze_language_usage(repositories)
            repo_stats = self.analyze_repository_statistics(repositories)
            activity_stats = self.analyze_activity(events)
            
            # Calculate account age
            if profile.get("created_at"):
                created_dt = datetime.fromisoformat(profile["created_at"].replace("Z", "+00:00"))
                account_age_days = (datetime.now(created_dt.tzinfo) - created_dt).days
                account_age_years = round(account_age_days / 365, 1)
            else:
                account_age_days = 0
                account_age_years = 0
            
            return {
                "profile": profile,
                "statistics": {
                    "repositories": repo_stats,
                    "languages": language_stats,
                    "activity": activity_stats,
                    "account_age_days": account_age_days,
                    "account_age_years": account_age_years
                },
                "repositories": repositories[:10],  # Top 10 repos
                "fetch_status": "success",
                "fetched_at": datetime.utcnow().isoformat()
            }
            
        except ValueError as e:
            # User not found
            logger.error(f"GitHub user not found: {username}")
            return {
                "profile": None,
                "statistics": None,
                "repositories": [],
                "fetch_status": "user_not_found",
                "error": str(e),
                "fetched_at": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            # Other errors (rate limit, network, etc.)
            logger.error(f"GitHub API error for {username}: {str(e)}")
            return {
                "profile": None,
                "statistics": None,
                "repositories": [],
                "fetch_status": "error",
                "error": str(e),
                "fetched_at": datetime.utcnow().isoformat()
            }
    
    async def check_rate_limit(self) -> Dict[str, Any]:
        """
        Check current GitHub API rate limit status
        
        Endpoint: GET /rate_limit
        
        Returns:
            Rate limit information
        """
        url = f"{self.BASE_URL}/rate_limit"
        
        async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
            response = await client.get(url, headers=self.headers)
            
            if response.status_code != 200:
                return {"error": "Failed to fetch rate limit"}
            
            data = response.json()
            core_limit = data.get("resources", {}).get("core", {})
            
            return {
                "limit": core_limit.get("limit"),
                "remaining": core_limit.get("remaining"),
                "reset": core_limit.get("reset"),
                "used": core_limit.get("used")
            }
