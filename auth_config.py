"""
MasterChief Authentication Configuration
Centralized configuration management for all authentication providers
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class AuthConfig:
    """Configuration class for authentication settings"""

    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Flask settings
        self.secret_key = os.getenv('SECRET_KEY', 'change-this-in-production')
        self.session_timeout = int(os.getenv('SESSION_TIMEOUT', '3600'))

        # Azure AD settings
        self.azure_client_id = os.getenv('AZURE_CLIENT_ID', '')
        self.azure_client_secret = os.getenv('AZURE_CLIENT_SECRET', '')
        self.azure_tenant_id = os.getenv('AZURE_TENANT_ID', '')
        self.azure_subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID', '')

        # OKTA settings
        self.okta_client_id = os.getenv('OKTA_CLIENT_ID', '')
        self.okta_client_secret = os.getenv('OKTA_CLIENT_SECRET', '')
        self.okta_issuer = os.getenv('OKTA_ISSUER', '')

        # GitHub settings
        self.github_client_id = os.getenv('GITHUB_CLIENT_ID', '')
        self.github_client_secret = os.getenv('GITHUB_CLIENT_SECRET', '')
        self.github_token = os.getenv('GITHUB_TOKEN', '')

        # Admin settings
        self.admin_token = os.getenv('ADMIN_TOKEN', 'admin-token-change-me')

    def validate_config(self) -> Dict[str, bool]:
        """Validate that all required configurations are present"""
        return {
            'azure': bool(self.azure_client_id and self.azure_client_secret and self.azure_tenant_id),
            'okta': bool(self.okta_client_id and self.okta_client_secret and self.okta_issuer),
            'github': bool(self.github_client_id and self.github_client_secret),
            'github_token': bool(self.github_token),
        }

    def get_azure_config(self) -> Dict[str, str]:
        """Get Azure-specific configuration"""
        return {
            'client_id': self.azure_client_id,
            'client_secret': self.azure_client_secret,
            'tenant_id': self.azure_tenant_id,
            'subscription_id': self.azure_subscription_id,
        }

    def get_okta_config(self) -> Dict[str, str]:
        """Get OKTA-specific configuration"""
        return {
            'client_id': self.okta_client_id,
            'client_secret': self.okta_client_secret,
            'issuer': self.okta_issuer,
        }

    def get_github_config(self) -> Dict[str, str]:
        """Get GitHub-specific configuration"""
        return {
            'client_id': self.github_client_id,
            'client_secret': self.github_client_secret,
            'token': self.github_token,
        }

    def is_configured(self, provider: str) -> bool:
        """Check if a specific provider is configured"""
        validation = self.validate_config()
        return validation.get(provider, False)

# Global configuration instance
auth_config = AuthConfig()