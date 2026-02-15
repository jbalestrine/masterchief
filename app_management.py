"""
MasterChief App Management Module
Unified interface for managing Azure AD and GitHub OAuth applications
"""

import logging
from typing import Dict, List, Any, Optional
import requests
from urllib.parse import urlencode

from auth_config import auth_config
from azure_integration import azure_integration
from github_integration import github_integration

logger = logging.getLogger(__name__)

class AppManagement:
    """Unified app registration management for Azure AD and GitHub OAuth apps"""

    def __init__(self):
        self.azure_config = auth_config.get_azure_config()
        self.github_config = auth_config.get_github_config()

    # Azure AD Application Management
    def list_azure_applications(self) -> List[Dict[str, Any]]:
        """List Azure AD applications (mock implementation)"""
        # Note: This would require Microsoft Graph API permissions
        # For now, return a placeholder
        try:
            if not auth_config.is_configured('azure'):
                return []

            # In a real implementation, this would use Microsoft Graph API
            # For now, return the current app if configured
            apps = []
            if self.azure_config.get('client_id'):
                apps.append({
                    'id': 'current-app',
                    'display_name': 'MasterChief DevOps Platform',
                    'app_id': self.azure_config['client_id'],
                    'created_date_time': '2024-01-01T00:00:00Z',
                    'sign_in_audience': 'AzureADMyOrg',
                    'web': {
                        'redirect_uris': ['http://localhost:5000/auth/azure/callback']
                    }
                })

            return apps

        except Exception as e:
            logger.error(f"Error listing Azure AD applications: {e}")
            return []

    def create_azure_application(self, name: str, redirect_uris: List[str] = None) -> Optional[Dict[str, Any]]:
        """Create Azure AD application (mock implementation)"""
        # Note: This would require Microsoft Graph API permissions
        # In a real implementation, this would create an app via Microsoft Graph API
        logger.info(f"Azure AD app creation requested: {name}")
        logger.warning("Azure AD app creation not implemented - requires Microsoft Graph API permissions")

        return {
            'id': 'mock-app-id',
            'display_name': name,
            'app_id': 'mock-client-id',
            'created': True,
            'note': 'Mock implementation - actual creation requires Microsoft Graph API'
        }

    def update_azure_application(self, app_id: str, updates: Dict[str, Any]) -> bool:
        """Update Azure AD application (mock implementation)"""
        logger.info(f"Azure AD app update requested for {app_id}")
        logger.warning("Azure AD app updates not implemented - requires Microsoft Graph API permissions")
        return True

    def delete_azure_application(self, app_id: str) -> bool:
        """Delete Azure AD application (mock implementation)"""
        logger.info(f"Azure AD app deletion requested for {app_id}")
        logger.warning("Azure AD app deletion not implemented - requires Microsoft Graph API permissions")
        return True

    # GitHub OAuth App Management
    def list_github_applications(self) -> List[Dict[str, Any]]:
        """List GitHub OAuth applications (mock implementation)"""
        # Note: GitHub doesn't provide API to list OAuth apps
        # This would need to be managed manually or through GitHub's web interface
        try:
            if not auth_config.is_configured('github'):
                return []

            # Return the current app if configured
            apps = []
            if self.github_config.get('client_id'):
                apps.append({
                    'id': 'current-app',
                    'name': 'MasterChief DevOps Platform',
                    'client_id': self.github_config['client_id'],
                    'url': 'http://localhost:5000',
                    'callback_urls': ['http://localhost:5000/auth/github/callback'],
                    'created_at': '2024-01-01T00:00:00Z'
                })

            return apps

        except Exception as e:
            logger.error(f"Error listing GitHub OAuth applications: {e}")
            return []

    def create_github_application(self, name: str, homepage_url: str = "", callback_urls: List[str] = None) -> Optional[Dict[str, Any]]:
        """Create GitHub OAuth application (mock implementation)"""
        # Note: GitHub OAuth apps must be created through the web interface
        # There's no API for creating OAuth apps programmatically
        logger.info(f"GitHub OAuth app creation requested: {name}")
        logger.warning("GitHub OAuth app creation must be done through GitHub's web interface")

        return {
            'id': 'mock-app-id',
            'name': name,
            'client_id': 'mock-client-id',
            'client_secret': 'mock-client-secret',
            'created': False,
            'note': 'GitHub OAuth apps must be created manually at https://github.com/settings/developers'
        }

    def update_github_application(self, app_id: str, updates: Dict[str, Any]) -> bool:
        """Update GitHub OAuth application (mock implementation)"""
        logger.info(f"GitHub OAuth app update requested for {app_id}")
        logger.warning("GitHub OAuth app updates must be done through GitHub's web interface")
        return True

    def delete_github_application(self, app_id: str) -> bool:
        """Delete GitHub OAuth application (mock implementation)"""
        logger.info(f"GitHub OAuth app deletion requested for {app_id}")
        logger.warning("GitHub OAuth app deletion must be done through GitHub's web interface")
        return True

    # Unified App Management
    def list_all_applications(self) -> Dict[str, List[Dict[str, Any]]]:
        """List all applications from all providers"""
        return {
            'azure': self.list_azure_applications(),
            'github': self.list_github_applications()
        }

    def get_app_registration_guide(self) -> Dict[str, Dict[str, Any]]:
        """Get registration guides for all providers"""
        return {
            'azure': {
                'title': 'Azure AD Application Registration',
                'steps': [
                    'Go to Azure Portal > Azure Active Directory > App registrations',
                    'Click "New registration"',
                    'Enter app name: "MasterChief DevOps Platform"',
                    'Select account type: "Single tenant"',
                    'Add redirect URI: "http://localhost:5000/auth/azure/callback"',
                    'Register the application',
                    'Note the Application (client) ID and Directory (tenant) ID',
                    'Go to Certificates & secrets > New client secret',
                    'Copy the client secret value'
                ],
                'required_permissions': [
                    'User.Read',
                    'Directory.Read.All',
                    'Application.ReadWrite.All'
                ],
                'portal_url': 'https://portal.azure.com'
            },
            'github': {
                'title': 'GitHub OAuth App Registration',
                'steps': [
                    'Go to GitHub Settings > Developer settings > OAuth Apps',
                    'Click "New OAuth App"',
                    'Enter app name: "MasterChief DevOps Platform"',
                    'Homepage URL: "http://localhost:5000"',
                    'Authorization callback URL: "http://localhost:5000/auth/github/callback"',
                    'Register the application',
                    'Note the Client ID',
                    'Click "Generate a new client secret"',
                    'Copy the Client Secret'
                ],
                'permissions': [
                    'Read user email addresses',
                    'Read user profile information'
                ],
                'portal_url': 'https://github.com/settings/developers'
            },
            'okta': {
                'title': 'OKTA Application Setup',
                'steps': [
                    'Log in to your OKTA Admin Console',
                    'Go to Applications > Applications',
                    'Click "Create App Integration"',
                    'Select "OIDC - OpenID Connect" and "Web Application"',
                    'Enter app name: "MasterChief DevOps Platform"',
                    'Sign-in redirect URIs: "http://localhost:5000/auth/okta/callback"',
                    'Sign-out redirect URIs: "http://localhost:5000/"',
                    'Save the application',
                    'Note the Client ID and Client Secret',
                    'Get your OKTA domain from the admin console URL'
                ],
                'portal_url': 'https://your-domain.okta.com/admin'
            }
        }

    def validate_app_configuration(self, provider: str, config: Dict[str, str]) -> Dict[str, Any]:
        """Validate app configuration for a provider"""
        results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }

        if provider == 'azure':
            required = ['client_id', 'client_secret', 'tenant_id']
            for field in required:
                if not config.get(field):
                    results['valid'] = False
                    results['errors'].append(f"Missing required field: {field}")

        elif provider == 'github':
            required = ['client_id', 'client_secret']
            for field in required:
                if not config.get(field):
                    results['valid'] = False
                    results['errors'].append(f"Missing required field: {field}")

        elif provider == 'okta':
            required = ['client_id', 'client_secret', 'domain']
            for field in required:
                if not config.get(field):
                    results['valid'] = False
                    results['errors'].append(f"Missing required field: {field}")

        return results

# Global app management instance
app_management = AppManagement()