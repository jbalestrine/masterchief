"""
MasterChief Setup Wizard
Interactive web-based setup for authentication and cloud integration
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from flask import Blueprint, render_template_string, request, redirect, url_for, flash, jsonify
import requests

# Conditional imports for authentication modules
try:
    from auth_config import auth_config
    AUTH_CONFIG_AVAILABLE = True
except ImportError:
    AUTH_CONFIG_AVAILABLE = False
    auth_config = None

try:
    from azure_integration import azure_integration
    AZURE_INTEGRATION_AVAILABLE = True
except ImportError:
    AZURE_INTEGRATION_AVAILABLE = False
    azure_integration = None

try:
    from github_integration import github_integration
    GITHUB_INTEGRATION_AVAILABLE = True
except ImportError:
    GITHUB_INTEGRATION_AVAILABLE = False
    github_integration = None

try:
    from app_management import app_management
    APP_MANAGEMENT_AVAILABLE = True
except ImportError:
    APP_MANAGEMENT_AVAILABLE = False
    app_management = None

logger = logging.getLogger(__name__)

class SetupWizard:
    """Interactive setup wizard for authentication configuration"""

    def __init__(self, app):
        self.app = app
        self.blueprint = Blueprint('setup', __name__, url_prefix='/setup')
        self._register_routes()
        self.app.register_blueprint(self.blueprint)

    def _register_routes(self):
        """Register setup wizard routes"""

        @self.blueprint.route('/')
        def setup_welcome():
            """Welcome page for setup wizard"""
            return self._render_template('welcome.html', {
                'title': 'MasterChief Setup Wizard',
                'step': 1,
                'total_steps': 4
            })

        @self.blueprint.route('/providers')
        def select_providers():
            """Select which providers to configure"""
            providers = {
                'azure': {
                    'name': 'Azure Active Directory',
                    'description': 'Microsoft identity platform for enterprise authentication',
                    'configured': AUTH_CONFIG_AVAILABLE and auth_config and auth_config.is_configured('azure')
                },
                'okta': {
                    'name': 'OKTA SSO',
                    'description': 'Enterprise single sign-on solution',
                    'configured': AUTH_CONFIG_AVAILABLE and auth_config and auth_config.is_configured('okta')
                },
                'github': {
                    'name': 'GitHub OAuth',
                    'description': 'Developer platform authentication',
                    'configured': AUTH_CONFIG_AVAILABLE and auth_config and auth_config.is_configured('github')
                }
            }
            return self._render_template('providers.html', {
                'title': 'Select Authentication Providers',
                'step': 2,
                'total_steps': 4,
                'providers': providers
            })

        @self.blueprint.route('/configure/<provider>', methods=['GET', 'POST'])
        def configure_provider(provider):
            """Configure a specific provider"""
            if request.method == 'POST':
                return self._handle_provider_config(provider)

            template_data = {
                'title': f'Configure {provider.title()}',
                'step': 3,
                'total_steps': 4,
                'provider': provider,
                'config_guide': app_management.get_app_registration_guide().get(provider, {})
            }

            return self._render_template('configure_provider.html', template_data)

        @self.blueprint.route('/test', methods=['GET', 'POST'])
        def test_configuration():
            """Test the configuration"""
            if request.method == 'POST':
                return self._handle_test_config()

            return self._render_template('test_config.html', {
                'title': 'Test Configuration',
                'step': 4,
                'total_steps': 4
            })

        @self.blueprint.route('/complete')
        def setup_complete():
            """Setup completion page"""
            return self._render_template('complete.html', {
                'title': 'Setup Complete!',
                'providers': {
                    'azure': auth_config.is_configured('azure'),
                    'okta': auth_config.is_configured('okta'),
                    'github': auth_config.is_configured('github')
                }
            })

        @self.blueprint.route('/api/test/<provider>', methods=['POST'])
        def api_test_provider(provider):
            """API endpoint to test provider configuration"""
            try:
                data = request.get_json()
                result = self._test_provider_config(provider, data)
                return jsonify(result)
            except Exception as e:
                logger.error(f"Error testing {provider}: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.blueprint.route('/api/save-config', methods=['POST'])
        def api_save_config():
            """API endpoint to save configuration"""
            try:
                data = request.get_json()
                self._save_configuration(data)
                return jsonify({'success': True})
            except Exception as e:
                logger.error(f"Error saving configuration: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500

    def _handle_provider_config(self, provider):
        """Handle provider configuration form submission"""
        try:
            config_data = {}
            for key in request.form:
                if key.startswith(f'{provider}_'):
                    config_key = key.replace(f'{provider}_', '')
                    config_data[config_key] = request.form[key]

            # Save to environment
            self._update_env_config(provider, config_data)

            flash(f'{provider.title()} configuration saved successfully!', 'success')
            return redirect(url_for('setup.test_configuration'))

        except Exception as e:
            logger.error(f"Error configuring {provider}: {e}")
            flash(f'Error configuring {provider}: {str(e)}', 'error')
            return redirect(url_for('setup.configure_provider', provider=provider))

    def _handle_test_config(self):
        """Handle configuration testing"""
        try:
            # Test all configured providers
            results = {}
            for provider in ['azure', 'okta', 'github']:
                if auth_config.is_configured(provider):
                    results[provider] = self._test_provider_config(provider, {})

            # If all tests pass, redirect to complete
            all_passed = all(result.get('success', False) for result in results.values())

            if all_passed:
                flash('All configurations tested successfully!', 'success')
                return redirect(url_for('setup.setup_complete'))
            else:
                failed_providers = [p for p, r in results.items() if not r.get('success', False)]
                flash(f'Configuration test failed for: {", ".join(failed_providers)}', 'warning')
                return redirect(url_for('setup.test_configuration'))

        except Exception as e:
            logger.error(f"Error testing configuration: {e}")
            flash(f'Error testing configuration: {str(e)}', 'error')
            return redirect(url_for('setup.test_configuration'))

    def _test_provider_config(self, provider: str, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test provider configuration"""
        try:
            if provider == 'azure':
                # Test Azure configuration
                if azure_integration.is_configured():
                    subscriptions = azure_integration.list_subscriptions()
                    return {
                        'success': True,
                        'message': f'Found {len(subscriptions)} subscription(s)',
                        'details': subscriptions
                    }
                else:
                    return {'success': False, 'error': 'Azure not configured'}

            elif provider == 'github':
                # Test GitHub configuration
                if github_integration.is_configured():
                    user = github_integration.get_current_user()
                    if user:
                        return {
                            'success': True,
                            'message': f'Connected as {user.get("login", "unknown")}',
                            'details': user
                        }
                    else:
                        return {'success': False, 'error': 'Could not get user info'}
                else:
                    return {'success': False, 'error': 'GitHub not configured'}

            elif provider == 'okta':
                # Test OKTA configuration (basic validation)
                okta_config = auth_config.get_okta_config()
                if all(okta_config.values()):
                    return {
                        'success': True,
                        'message': 'OKTA configuration appears valid',
                        'details': {'domain': okta_config.get('domain')}
                    }
                else:
                    return {'success': False, 'error': 'OKTA configuration incomplete'}

            return {'success': False, 'error': f'Unknown provider: {provider}'}

        except Exception as e:
            logger.error(f"Error testing {provider}: {e}")
            return {'success': False, 'error': str(e)}

    def _update_env_config(self, provider: str, config_data: Dict[str, str]):
        """Update environment configuration"""
        env_file = os.path.join(os.getcwd(), '.env')

        # Read current .env content
        env_content = {}
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        env_content[key] = value

        # Update with new config
        for key, value in config_data.items():
            env_key = f"{provider.upper()}_{key.upper()}"
            env_content[env_key] = value

        # Write back to .env
        with open(env_file, 'w') as f:
            for key, value in env_content.items():
                f.write(f"{key}={value}\n")

        # Reload configuration
        auth_config.__init__()

    def _save_configuration(self, config_data: Dict[str, Any]):
        """Save complete configuration"""
        env_file = os.path.join(os.getcwd(), '.env')

        with open(env_file, 'w') as f:
            f.write("# MasterChief Authentication Configuration\n")
            f.write("# Generated by Setup Wizard\n\n")

            for provider, settings in config_data.items():
                f.write(f"# {provider.upper()} Configuration\n")
                for key, value in settings.items():
                    env_key = f"{provider.upper()}_{key.upper()}"
                    f.write(f"{env_key}={value}\n")
                f.write("\n")

        # Reload configuration
        auth_config.__init__()

    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render HTML template with context"""
        templates = {
            'welcome.html': """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .logo { font-size: 2em; color: #007acc; margin-bottom: 10px; }
        .subtitle { color: #666; font-size: 1.1em; }
        .progress { display: flex; justify-content: space-between; margin: 30px 0; }
        .step { flex: 1; text-align: center; padding: 10px; }
        .step.active { background: #007acc; color: white; border-radius: 5px; }
        .step.completed { background: #28a745; color: white; border-radius: 5px; }
        .btn { background: #007acc; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 1em; text-decoration: none; display: inline-block; }
        .btn:hover { background: #005aa3; }
        .features { margin: 30px 0; }
        .feature { margin: 15px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🚀 MasterChief</div>
            <h1>{{ title }}</h1>
            <div class="subtitle">DevOps Automation Platform Setup</div>
        </div>

        <div class="progress">
            {% for i in range(1, total_steps + 1) %}
            <div class="step {% if i < step %}completed{% elif i == step %}active{% endif %}">
                Step {{ i }}
            </div>
            {% endfor %}
        </div>

        <div class="features">
            <div class="feature">
                <h3>🔐 Multi-Provider Authentication</h3>
                <p>Support for Azure AD, OKTA SSO, and GitHub OAuth</p>
            </div>
            <div class="feature">
                <h3>☁️ Cloud Integration</h3>
                <p>Azure resource management and GitHub repository operations</p>
            </div>
            <div class="feature">
                <h3>🎯 Enterprise Ready</h3>
                <p>Secure, scalable, and production-ready authentication</p>
            </div>
        </div>

        <div style="text-align: center; margin-top: 40px;">
            <a href="/setup/providers" class="btn">Start Setup →</a>
        </div>
    </div>
</body>
</html>
            """,

            'providers.html': """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .progress { display: flex; justify-content: space-between; margin: 30px 0; }
        .step { flex: 1; text-align: center; padding: 10px; }
        .step.active { background: #007acc; color: white; border-radius: 5px; }
        .step.completed { background: #28a745; color: white; border-radius: 5px; }
        .provider { margin: 20px 0; padding: 20px; border: 2px solid #e9ecef; border-radius: 10px; cursor: pointer; transition: all 0.3s; }
        .provider:hover { border-color: #007acc; background: #f8f9ff; }
        .provider.selected { border-color: #007acc; background: #e7f3ff; }
        .provider-header { display: flex; align-items: center; margin-bottom: 10px; }
        .provider-icon { font-size: 2em; margin-right: 15px; }
        .provider-name { font-size: 1.2em; font-weight: bold; }
        .provider-desc { color: #666; margin: 5px 0; }
        .status { margin-left: auto; padding: 5px 10px; border-radius: 15px; font-size: 0.8em; }
        .status.configured { background: #d4edda; color: #155724; }
        .status.not-configured { background: #fff3cd; color: #856404; }
        .btn { background: #007acc; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 1em; text-decoration: none; display: inline-block; margin: 10px 5px; }
        .btn:hover { background: #005aa3; }
        .btn.secondary { background: #6c757d; }
        .btn.secondary:hover { background: #545b62; }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ title }}</h1>

        <div class="progress">
            {% for i in range(1, total_steps + 1) %}
            <div class="step {% if i < step %}completed{% elif i == step %}active{% endif %}">
                Step {{ i }}
            </div>
            {% endfor %}
        </div>

        <p>Select which authentication providers you want to configure:</p>

        {% for key, provider in providers.items() %}
        <div class="provider" onclick="toggleProvider('{{ key }}')">
            <div class="provider-header">
                <div class="provider-icon">
                    {% if key == 'azure' %}☁️{% elif key == 'okta' %}🔐{% elif key == 'github' %}🐙{% endif %}
                </div>
                <div class="provider-name">{{ provider.name }}</div>
                <div class="status {{ 'configured' if provider.configured else 'not-configured' }}">
                    {{ 'Configured' if provider.configured else 'Not Configured' }}
                </div>
            </div>
            <div class="provider-desc">{{ provider.description }}</div>
        </div>
        {% endfor %}

        <div style="text-align: center; margin-top: 40px;">
            <a href="/setup" class="btn secondary">← Back</a>
            <button onclick="proceedToConfig()" class="btn">Configure Selected →</button>
        </div>
    </div>

    <script>
        let selectedProviders = [];

        function toggleProvider(provider) {
            const element = document.querySelector(`[onclick="toggleProvider('${provider}')"]`);
            const index = selectedProviders.indexOf(provider);

            if (index > -1) {
                selectedProviders.splice(index, 1);
                element.classList.remove('selected');
            } else {
                selectedProviders.push(provider);
                element.classList.add('selected');
            }
        }

        function proceedToConfig() {
            if (selectedProviders.length === 0) {
                alert('Please select at least one provider to configure.');
                return;
            }

            // For simplicity, redirect to the first selected provider
            // In a full implementation, you'd handle multiple providers
            window.location.href = `/setup/configure/${selectedProviders[0]}`;
        }
    </script>
</body>
</html>
            """,

            'configure_provider.html': """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .progress { display: flex; justify-content: space-between; margin: 30px 0; }
        .step { flex: 1; text-align: center; padding: 10px; }
        .step.active { background: #007acc; color: white; border-radius: 5px; }
        .step.completed { background: #28a745; color: white; border-radius: 5px; }
        .form-group { margin: 20px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], input[type="password"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 1em; }
        .help-text { color: #666; font-size: 0.9em; margin-top: 5px; }
        .guide { background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }
        .guide h3 { margin-top: 0; }
        .guide ol { margin: 10px 0; }
        .guide li { margin: 5px 0; }
        .btn { background: #007acc; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 1em; text-decoration: none; display: inline-block; margin: 10px 5px; }
        .btn:hover { background: #005aa3; }
        .btn.secondary { background: #6c757d; }
        .btn.secondary:hover { background: #545b62; }
        .test-result { margin: 20px 0; padding: 15px; border-radius: 5px; }
        .test-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .test-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ title }}</h1>

        <div class="progress">
            {% for i in range(1, total_steps + 1) %}
            <div class="step {% if i < step %}completed{% elif i == step %}active{% endif %}">
                Step {{ i }}
            </div>
            {% endfor %}
        </div>

        {% if config_guide %}
        <div class="guide">
            <h3>📋 Setup Instructions for {{ provider.title() }}</h3>
            <ol>
            {% for step in config_guide.steps %}
                <li>{{ step }}</li>
            {% endfor %}
            </ol>
            {% if config_guide.portal_url %}
            <p><strong>Portal:</strong> <a href="{{ config_guide.portal_url }}" target="_blank">{{ config_guide.portal_url }}</a></p>
            {% endif %}
        </div>
        {% endif %}

        <form method="POST">
            <div class="form-group">
                <label for="client_id">Client ID:</label>
                <input type="text" id="client_id" name="{{ provider }}_client_id" required>
                <div class="help-text">The application/client ID from your {{ provider.title() }} app registration</div>
            </div>

            <div class="form-group">
                <label for="client_secret">Client Secret:</label>
                <input type="password" id="client_secret" name="{{ provider }}_client_secret" required>
                <div class="help-text">The client secret from your {{ provider.title() }} app registration</div>
            </div>

            {% if provider == 'azure' %}
            <div class="form-group">
                <label for="tenant_id">Tenant ID:</label>
                <input type="text" id="tenant_id" name="{{ provider }}_tenant_id" required>
                <div class="help-text">Your Azure AD tenant/directory ID</div>
            </div>

            <div class="form-group">
                <label for="subscription_id">Subscription ID:</label>
                <input type="text" id="subscription_id" name="{{ provider }}_subscription_id">
                <div class="help-text">Your Azure subscription ID (optional, for resource management)</div>
            </div>
            {% endif %}

            {% if provider == 'okta' %}
            <div class="form-group">
                <label for="domain">OKTA Domain:</label>
                <input type="text" id="domain" name="{{ provider }}_domain" placeholder="your-org.okta.com" required>
                <div class="help-text">Your OKTA organization domain</div>
            </div>
            {% endif %}

            <div style="text-align: center; margin-top: 40px;">
                <a href="/setup/providers" class="btn secondary">← Back</a>
                <button type="submit" class="btn">Save Configuration →</button>
            </div>
        </form>
    </div>
</body>
</html>
            """,

            'test_config.html': """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .progress { display: flex; justify-content: space-between; margin: 30px 0; }
        .step { flex: 1; text-align: center; padding: 10px; }
        .step.active { background: #007acc; color: white; border-radius: 5px; }
        .step.completed { background: #28a745; color: white; border-radius: 5px; }
        .test-section { margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        .test-header { display: flex; align-items: center; margin-bottom: 15px; }
        .test-icon { font-size: 1.5em; margin-right: 10px; }
        .test-name { font-size: 1.2em; font-weight: bold; }
        .test-status { margin-left: auto; padding: 5px 10px; border-radius: 15px; font-size: 0.8em; }
        .status-pending { background: #fff3cd; color: #856404; }
        .status-testing { background: #cce5ff; color: #004085; }
        .status-success { background: #d4edda; color: #155724; }
        .status-error { background: #f8d7da; color: #721c24; }
        .test-details { margin-top: 10px; font-size: 0.9em; color: #666; }
        .btn { background: #007acc; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 1em; text-decoration: none; display: inline-block; margin: 10px 5px; }
        .btn:hover { background: #005aa3; }
        .btn.secondary { background: #6c757d; }
        .btn.secondary:hover { background: #545b62; }
        .btn:disabled { background: #ccc; cursor: not-allowed; }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ title }}</h1>

        <div class="progress">
            {% for i in range(1, total_steps + 1) %}
            <div class="step {% if i < step %}completed{% elif i == step %}active{% endif %}">
                Step {{ i }}
            </div>
            {% endfor %}
        </div>

        <p>Let's test your authentication configuration to make sure everything works:</p>

        <div id="azure-test" class="test-section" style="display: none;">
            <div class="test-header">
                <div class="test-icon">☁️</div>
                <div class="test-name">Azure Active Directory</div>
                <div id="azure-status" class="test-status status-pending">Ready to test</div>
            </div>
            <div id="azure-details" class="test-details"></div>
        </div>

        <div id="okta-test" class="test-section" style="display: none;">
            <div class="test-header">
                <div class="test-icon">🔐</div>
                <div class="test-name">OKTA SSO</div>
                <div id="okta-status" class="test-status status-pending">Ready to test</div>
            </div>
            <div id="okta-details" class="test-details"></div>
        </div>

        <div id="github-test" class="test-section" style="display: none;">
            <div class="test-header">
                <div class="test-icon">🐙</div>
                <div class="test-name">GitHub OAuth</div>
                <div id="github-status" class="test-status status-pending">Ready to test</div>
            </div>
            <div id="github-details" class="test-details"></div>
        </div>

        <div style="text-align: center; margin-top: 40px;">
            <a href="/setup/providers" class="btn secondary">← Back</a>
            <button onclick="runTests()" class="btn" id="test-btn">Run Tests</button>
            <button onclick="completeSetup()" class="btn" id="complete-btn" style="display: none;">Complete Setup →</button>
        </div>
    </div>

    <script>
        let testResults = {};

        async function runTests() {
            const testBtn = document.getElementById('test-btn');
            testBtn.textContent = 'Testing...';
            testBtn.disabled = true;

            // Show configured providers
            {% for provider in ['azure', 'okta', 'github'] %}
            {% if auth_config.is_configured(provider) %}
            document.getElementById('{{ provider }}-test').style.display = 'block';
            {% endif %}
            {% endfor %}

            // Test each provider
            const providers = ['azure', 'okta', 'github'];
            for (const provider of providers) {
                if (document.getElementById(`${provider}-test`).style.display !== 'none') {
                    await testProvider(provider);
                }
            }

            testBtn.textContent = 'Tests Complete';
            document.getElementById('complete-btn').style.display = 'inline-block';
        }

        async function testProvider(provider) {
            const statusEl = document.getElementById(`${provider}-status`);
            const detailsEl = document.getElementById(`${provider}-details`);

            statusEl.textContent = 'Testing...';
            statusEl.className = 'test-status status-testing';

            try {
                const response = await fetch(`/setup/api/test/${provider}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({})
                });

                const result = await response.json();
                testResults[provider] = result;

                if (result.success) {
                    statusEl.textContent = 'Success';
                    statusEl.className = 'test-status status-success';
                    detailsEl.textContent = result.message;
                } else {
                    statusEl.textContent = 'Failed';
                    statusEl.className = 'test-status status-error';
                    detailsEl.textContent = result.error || 'Test failed';
                }
            } catch (error) {
                statusEl.textContent = 'Error';
                statusEl.className = 'test-status status-error';
                detailsEl.textContent = error.message;
                testResults[provider] = { success: false, error: error.message };
            }
        }

        function completeSetup() {
            // Submit test results and complete setup
            fetch('/setup/api/save-config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(testResults)
            }).then(() => {
                window.location.href = '/setup/complete';
            });
        }
    </script>
</body>
</html>
            """,

            'complete.html': """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .success-icon { text-align: center; font-size: 4em; margin: 20px 0; }
        .summary { margin: 30px 0; }
        .provider-status { display: flex; align-items: center; margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 5px; }
        .provider-icon { font-size: 1.5em; margin-right: 15px; }
        .provider-name { flex: 1; font-weight: bold; }
        .status-badge { padding: 5px 10px; border-radius: 15px; font-size: 0.8em; }
        .status-configured { background: #d4edda; color: #155724; }
        .status-not-configured { background: #f8d7da; color: #721c24; }
        .next-steps { background: #e7f3ff; padding: 20px; border-radius: 5px; margin: 30px 0; }
        .next-steps h3 { margin-top: 0; }
        .btn { background: #007acc; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 1em; text-decoration: none; display: inline-block; margin: 10px 5px; }
        .btn:hover { background: #005aa3; }
        .btn.primary { background: #28a745; }
        .btn.primary:hover { background: #218838; }
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">🎉</div>
        <h1>{{ title }}</h1>

        <div class="summary">
            <h2>Configuration Summary</h2>

            <div class="provider-status">
                <div class="provider-icon">☁️</div>
                <div class="provider-name">Azure Active Directory</div>
                <div class="status-badge {{ 'status-configured' if providers.azure else 'status-not-configured' }}">
                    {{ 'Configured' if providers.azure else 'Not Configured' }}
                </div>
            </div>

            <div class="provider-status">
                <div class="provider-icon">🔐</div>
                <div class="provider-name">OKTA SSO</div>
                <div class="status-badge {{ 'status-configured' if providers.okta else 'status-not-configured' }}">
                    {{ 'Configured' if providers.okta else 'Not Configured' }}
                </div>
            </div>

            <div class="provider-status">
                <div class="provider-icon">🐙</div>
                <div class="provider-name">GitHub OAuth</div>
                <div class="status-badge {{ 'status-configured' if providers.github else 'status-not-configured' }}">
                    {{ 'Configured' if providers.github else 'Not Configured' }}
                </div>
            </div>
        </div>

        <div class="next-steps">
            <h3>🚀 What's Next?</h3>
            <ul>
                <li><strong>Start the application:</strong> Run <code>python main.py</code></li>
                <li><strong>Access the web interface:</strong> Visit <code>http://localhost:5000/web-ide</code></li>
                <li><strong>Test authentication:</strong> Try logging in with your configured providers</li>
                <li><strong>Explore features:</strong> Use the Azure resource manager and GitHub integration</li>
            </ul>
        </div>

        <div style="text-align: center; margin-top: 40px;">
            <a href="/web-ide" class="btn primary">Launch MasterChief →</a>
            <a href="/setup" class="btn">Run Setup Again</a>
        </div>
    </div>
</body>
</html>
            """
        }

        template = templates.get(template_name, "<h1>Template not found</h1>")
        return self._render_jinja_template(template, context)

    def _render_jinja_template(self, template: str, context: Dict[str, Any]) -> str:
        """Simple Jinja-like template rendering"""
        result = template

        # Simple variable replacement
        for key, value in context.items():
            result = result.replace("{{ " + key + " }}", str(value))
            result = result.replace("{{" + key + "}}", str(value))

        # Simple if statements (basic implementation)
        import re
        if_pattern = r'{% if (.*?) %}(.*?){% endif %}'
        for match in re.finditer(if_pattern, result, re.DOTALL):
            condition = match.group(1).strip()
            content = match.group(2)

            # Simple condition evaluation
            if 'auth_config.is_configured' in condition:
                provider = condition.split("'")[1]
                should_show = auth_config.is_configured(provider)
            else:
                should_show = bool(context.get(condition.split()[0], False))

            if should_show:
                result = result.replace(match.group(0), content)
            else:
                result = result.replace(match.group(0), '')

        # Simple for loops
        for_pattern = r'{% for (.*?) in (.*?) %}(.*?){% endfor %}'
        for match in re.finditer(for_pattern, result, re.DOTALL):
            var_name = match.group(1).strip()
            list_name = match.group(2).strip()
            content = match.group(3)

            items = context.get(list_name, [])
            if isinstance(items, dict):
                items = items.items()

            replacement = ''
            for item in items:
                item_content = content
                if isinstance(item, tuple):
                    item_content = item_content.replace("{{ " + var_name + " }}", str(item[0]))
                    item_content = item_content.replace("{{" + var_name + "}}", str(item[0]))
                else:
                    item_content = item_content.replace("{{ " + var_name + " }}", str(item))
                    item_content = item_content.replace("{{" + var_name + "}}", str(item))
                replacement += item_content

            result = result.replace(match.group(0), replacement)

        return result

# Global setup wizard instance
setup_wizard = None

def init_setup_wizard(app):
    """Initialize the setup wizard for the Flask app"""
    global setup_wizard
    setup_wizard = SetupWizard(app)
    return setup_wizard