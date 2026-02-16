"""
MasterChief Authentication Module
Handles user authentication, session management, and OAuth flows
"""

from flask import Flask, request, redirect, url_for, session, jsonify, g, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
from authlib.integrations.base_client import OAuthError
import requests
from datetime import datetime, timedelta
import jwt
from urllib.parse import urlencode
import logging

from auth_config import auth_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class User(UserMixin):
    """User model for Flask-Login"""

    def __init__(self, user_id, username=None, email=None, provider=None, profile_data=None):
        self.id = user_id
        self.username = username
        self.email = email
        self.provider = provider
        self.profile_data = profile_data or {}

    @staticmethod
    def get(user_id):
        """Get user by ID (mock implementation)"""
        # In a real app, this would query a database
        return User(user_id)

class AuthModule:
    """Main authentication module"""

    def __init__(self, app: Flask):
        self.app = app
        self.oauth = OAuth(app)
        self.login_manager = LoginManager()
        self.login_manager.init_app(app)
        self.login_manager.login_view = 'login'

        # Configure OAuth providers
        self._configure_oauth_providers()

        # Register routes
        self._register_routes()

        # User session store (in production, use a database)
        self.user_sessions = {}

    def _configure_oauth_providers(self):
        """Configure OAuth providers"""

        # Azure AD
        if auth_config.is_configured('azure'):
            self.oauth.register(
                name='azure',
                client_id=auth_config.azure_client_id,
                client_secret=auth_config.azure_client_secret,
                server_metadata_url=f'https://login.microsoftonline.com/{auth_config.azure_tenant_id}/v2.0/.well-known/openid_connect_configuration',
                client_kwargs={
                    'scope': 'openid email profile https://graph.microsoft.com/User.Read'
                }
            )

        # OKTA
        if auth_config.is_configured('okta'):
            self.oauth.register(
                name='okta',
                client_id=auth_config.okta_client_id,
                client_secret=auth_config.okta_client_secret,
                server_metadata_url=f'{auth_config.okta_issuer}/.well-known/openid_configuration',
                client_kwargs={
                    'scope': 'openid email profile'
                }
            )

        # GitHub
        if auth_config.is_configured('github'):
            self.oauth.register(
                name='github',
                client_id=auth_config.github_client_id,
                client_secret=auth_config.github_client_secret,
                access_token_url='https://github.com/login/oauth/access_token',
                authorize_url='https://github.com/login/oauth/authorize',
                api_base_url='https://api.github.com/',
                client_kwargs={'scope': 'user:email read:user'},
            )

    def _register_routes(self):
        """Register authentication routes"""

        @self.app.route('/auth/status')
        def auth_status():
            """Get current authentication status"""
            if current_user.is_authenticated:
                return jsonify({
                    'authenticated': True,
                    'user': {
                        'id': current_user.id,
                        'username': current_user.username,
                        'email': current_user.email,
                        'provider': current_user.provider
                    }
                })
            return jsonify({'authenticated': False})

        @self.app.route('/auth/azure/login')
        def azure_login():
            """Initiate Azure AD login"""
            if not auth_config.is_configured('azure'):
                return jsonify({'error': 'Azure AD not configured'}), 500

            redirect_uri = url_for('azure_callback', _external=True)
            return self.oauth.azure.authorize_redirect(redirect_uri)

        @self.app.route('/auth/azure/callback')
        def azure_callback():
            """Handle Azure AD callback"""
            try:
                token = self.oauth.azure.authorize_access_token()
                user_info = self.oauth.azure.get('https://graph.microsoft.com/v1.0/me').json()

                user = User(
                    user_id=user_info.get('id'),
                    username=user_info.get('displayName'),
                    email=user_info.get('mail') or user_info.get('userPrincipalName'),
                    provider='azure',
                    profile_data=user_info
                )

                login_user(user)
                session['provider'] = 'azure'
                session['token'] = token

                return redirect('/web-ide')

            except OAuthError as e:
                logger.error(f"Azure OAuth error: {e}")
                return jsonify({'error': 'Authentication failed'}), 400

        @self.app.route('/auth/okta/login')
        def okta_login():
            """Initiate OKTA login"""
            if not auth_config.is_configured('okta'):
                return jsonify({'error': 'OKTA not configured'}), 500

            redirect_uri = url_for('okta_callback', _external=True)
            return self.oauth.okta.authorize_redirect(redirect_uri)

        @self.app.route('/auth/okta/callback')
        def okta_callback():
            """Handle OKTA callback"""
            try:
                token = self.oauth.okta.authorize_access_token()
                user_info = token.get('userinfo', {})

                user = User(
                    user_id=user_info.get('sub'),
                    username=user_info.get('name'),
                    email=user_info.get('email'),
                    provider='okta',
                    profile_data=user_info
                )

                login_user(user)
                session['provider'] = 'okta'
                session['token'] = token

                return redirect('/web-ide')

            except OAuthError as e:
                logger.error(f"OKTA OAuth error: {e}")
                return jsonify({'error': 'Authentication failed'}), 400

        @self.app.route('/auth/github/login')
        def github_login():
            """Initiate GitHub login"""
            if not auth_config.is_configured('github'):
                return jsonify({'error': 'GitHub not configured'}), 500

            redirect_uri = url_for('github_callback', _external=True)
            return self.oauth.github.authorize_redirect(redirect_uri)

        @self.app.route('/auth/github/callback')
        def github_callback():
            """Handle GitHub callback"""
            try:
                token = self.oauth.github.authorize_access_token()
                resp = self.oauth.github.get('user')
                user_info = resp.json()

                # Get user email if not provided
                if not user_info.get('email'):
                    email_resp = self.oauth.github.get('user/emails')
                    emails = email_resp.json()
                    primary_email = next((email for email in emails if email.get('primary')), None)
                    if primary_email:
                        user_info['email'] = primary_email['email']

                user = User(
                    user_id=str(user_info.get('id')),
                    username=user_info.get('login'),
                    email=user_info.get('email'),
                    provider='github',
                    profile_data=user_info
                )

                login_user(user)
                session['provider'] = 'github'
                session['token'] = token

                return redirect('/web-ide')

            except OAuthError as e:
                logger.error(f"GitHub OAuth error: {e}")
                return jsonify({'error': 'Authentication failed'}), 400

        @self.app.route('/auth/logout', methods=['POST'])
        def logout():
            """Logout user"""
            logout_user()
            session.clear()
            return jsonify({'message': 'Logged out successfully'})

    @staticmethod
    def init_app(app: Flask):
        """Initialize authentication for Flask app"""
        auth_module = AuthModule(app)

        @app.before_request
        def load_user():
            """Load current user before each request"""
            g.user = current_user

        # Register user loader
        @auth_module.login_manager.user_loader
        def load_user(user_id):
            """Load user by ID"""
            return User.get(user_id)

        return auth_module


def init_auth(app: Flask):
    """Initialize authentication module"""
    return AuthModule.init_app(app)