"""
MasterChief GitHub Integration Module
Provides GitHub API integration for repository and user management
"""

import logging
from typing import Dict, List, Any, Optional
try:
    from github import Github, GithubException
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False
    Github = None
    GithubException = Exception
import requests

from auth_config import auth_config

logger = logging.getLogger(__name__)

class GitHubIntegration:
    """GitHub API integration for repository and user management"""

    def __init__(self):
        self.config = auth_config.get_github_config()
        self.github = None
        self.token = self.config.get('token')

        # Initialize GitHub client
        self._init_client()

    def _init_client(self):
        """Initialize GitHub client"""
        if not GITHUB_AVAILABLE:
            logger.warning("PyGitHub package not available")
            return

        try:
            if self.token:
                self.github = Github(self.token)
            elif self.config.get('client_id') and self.config.get('client_secret'):
                # For OAuth apps, we need an access token from the session
                # This will be set when a user authenticates
                pass
            else:
                logger.warning("GitHub integration not configured")
                return

            # Test connection
            if self.github:
                user = self.github.get_user()
                logger.info(f"GitHub integration initialized for user: {user.login}")

        except GithubException as e:
            logger.error(f"Failed to initialize GitHub client: {e}")
            self.github = None
        except Exception as e:
            logger.error(f"Error initializing GitHub integration: {e}")
            self.github = None

    def set_access_token(self, token: str):
        """Set access token for authenticated user"""
        try:
            self.github = Github(token)
            user = self.github.get_user()
            logger.info(f"GitHub access token set for user: {user.login}")
        except Exception as e:
            logger.error(f"Error setting GitHub access token: {e}")
            if GITHUB_AVAILABLE:
                self.github = None

    def is_configured(self) -> bool:
        """Check if GitHub integration is properly configured"""
        return self.github is not None

    # User Operations
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user information"""
        try:
            if not self.is_configured():
                return None

            user = self.github.get_user()
            return {
                'id': user.id,
                'login': user.login,
                'name': user.name,
                'email': user.email,
                'avatar_url': user.avatar_url,
                'html_url': user.html_url,
                'public_repos': user.public_repos,
                'followers': user.followers,
                'following': user.following
            }

        except GithubException as e:
            logger.error(f"Error getting current user: {e}")
            return None
        except Exception as e:
            logger.error(f"Error in get_current_user: {e}")
            return None

    def get_user_repositories(self, username: str = None) -> List[Dict[str, Any]]:
        """Get repositories for a user"""
        try:
            if not self.is_configured():
                return []

            if username:
                user = self.github.get_user(username)
            else:
                user = self.github.get_user()

            repos = []
            for repo in user.get_repos():
                repos.append({
                    'id': repo.id,
                    'name': repo.name,
                    'full_name': repo.full_name,
                    'description': repo.description,
                    'private': repo.private,
                    'html_url': repo.html_url,
                    'clone_url': repo.clone_url,
                    'language': repo.language,
                    'stars': repo.stargazers_count,
                    'forks': repo.forks_count,
                    'updated_at': repo.updated_at.isoformat() if repo.updated_at else None
                })

            return repos

        except GithubException as e:
            logger.error(f"Error getting user repositories: {e}")
            return []
        except Exception as e:
            logger.error(f"Error in get_user_repositories: {e}")
            return []

    # Repository Operations
    def get_repository(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """Get repository information"""
        try:
            if not self.is_configured():
                return None

            repository = self.github.get_repo(f"{owner}/{repo}")
            return {
                'id': repository.id,
                'name': repository.name,
                'full_name': repository.full_name,
                'description': repository.description,
                'private': repository.private,
                'html_url': repository.html_url,
                'clone_url': repository.clone_url,
                'language': repository.language,
                'stars': repository.stargazers_count,
                'forks': repository.forks_count,
                'open_issues': repository.open_issues_count,
                'default_branch': repository.default_branch,
                'created_at': repository.created_at.isoformat() if repository.created_at else None,
                'updated_at': repository.updated_at.isoformat() if repository.updated_at else None
            }

        except GithubException as e:
            logger.error(f"Error getting repository {owner}/{repo}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error in get_repository: {e}")
            return None

    def create_repository(self, name: str, description: str = "", private: bool = False) -> Optional[Dict[str, Any]]:
        """Create a new repository"""
        try:
            if not self.is_configured():
                return None

            user = self.github.get_user()
            repo = user.create_repo(
                name=name,
                description=description,
                private=private
            )

            return {
                'id': repo.id,
                'name': repo.name,
                'full_name': repo.full_name,
                'description': repo.description,
                'private': repo.private,
                'html_url': repo.html_url,
                'clone_url': repo.clone_url
            }

        except GithubException as e:
            logger.error(f"Error creating repository {name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error in create_repository: {e}")
            return None

    def delete_repository(self, owner: str, repo: str) -> bool:
        """Delete a repository"""
        try:
            if not self.is_configured():
                return False

            repository = self.github.get_repo(f"{owner}/{repo}")
            repository.delete()
            return True

        except GithubException as e:
            logger.error(f"Error deleting repository {owner}/{repo}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error in delete_repository: {e}")
            return False

    # Repository Search
    def search_repositories(self, query: str, sort: str = "stars", order: str = "desc", limit: int = 30) -> List[Dict[str, Any]]:
        """Search repositories on GitHub"""
        try:
            if not self.is_configured():
                return []

            # Use GitHub search API
            query_string = f"{query} in:name,description,topics"
            repositories = self.github.search_repositories(query=query_string, sort=sort, order=order)

            results = []
            for repo in repositories[:limit]:
                results.append({
                    'id': repo.id,
                    'name': repo.name,
                    'full_name': repo.full_name,
                    'description': repo.description,
                    'owner': {
                        'login': repo.owner.login,
                        'avatar_url': repo.owner.avatar_url
                    },
                    'html_url': repo.html_url,
                    'language': repo.language,
                    'stars': repo.stargazers_count,
                    'forks': repo.forks_count,
                    'updated_at': repo.updated_at.isoformat() if repo.updated_at else None
                })

            return results

        except GithubException as e:
            logger.error(f"Error searching repositories with query '{query}': {e}")
            return []
        except Exception as e:
            logger.error(f"Error in search_repositories: {e}")
            return []

    # Pull Request Operations
    def get_pull_requests(self, owner: str, repo: str, state: str = "open") -> List[Dict[str, Any]]:
        """Get pull requests for a repository"""
        try:
            if not self.is_configured():
                return []

            repository = self.github.get_repo(f"{owner}/{repo}")
            pull_requests = repository.get_pulls(state=state)

            results = []
            for pr in pull_requests:
                results.append({
                    'id': pr.id,
                    'number': pr.number,
                    'title': pr.title,
                    'body': pr.body,
                    'state': pr.state,
                    'html_url': pr.html_url,
                    'user': {
                        'login': pr.user.login,
                        'avatar_url': pr.user.avatar_url
                    },
                    'created_at': pr.created_at.isoformat() if pr.created_at else None,
                    'updated_at': pr.updated_at.isoformat() if pr.updated_at else None,
                    'merged': pr.merged if hasattr(pr, 'merged') else False
                })

            return results

        except GithubException as e:
            logger.error(f"Error getting pull requests for {owner}/{repo}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error in get_pull_requests: {e}")
            return []

    def create_pull_request(self, owner: str, repo: str, title: str, head: str, base: str, body: str = "") -> Optional[Dict[str, Any]]:
        """Create a pull request"""
        try:
            if not self.is_configured():
                return None

            repository = self.github.get_repo(f"{owner}/{repo}")
            pr = repository.create_pull(
                title=title,
                body=body,
                head=head,
                base=base
            )

            return {
                'id': pr.id,
                'number': pr.number,
                'title': pr.title,
                'html_url': pr.html_url,
                'state': pr.state
            }

        except GithubException as e:
            logger.error(f"Error creating pull request in {owner}/{repo}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error in create_pull_request: {e}")
            return None

# Global GitHub integration instance
github_integration = GitHubIntegration()