# 🔐 Authentication & Cloud Integration Setup Guide

This guide provides comprehensive instructions for setting up authentication and cloud integration features in MasterChief.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Azure AD Setup](#azure-ad-setup)
- [OKTA SSO Setup](#okta-sso-setup)
- [GitHub OAuth Setup](#github-oauth-setup)
- [Environment Configuration](#environment-configuration)
- [Application Setup](#application-setup)
- [Testing Authentication](#testing-authentication)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before setting up authentication, ensure you have:

- Python 3.8+ installed
- MasterChief application installed
- Administrative access to Azure, OKTA, and GitHub accounts
- Basic understanding of OAuth 2.0 flows

## Azure AD Setup

### 1. Register Azure AD Application

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** > **App registrations**
3. Click **New registration**
4. Configure:
   - **Name**: `MasterChief DevOps Platform`
   - **Supported account types**: `Accounts in this organizational directory only`
   - **Redirect URI**: `http://localhost:5000/auth/azure/callback` (for development)
5. Click **Register**

### 2. Configure API Permissions

1. In your app registration, go to **API permissions**
2. Click **Add a permission**
3. Select **Microsoft Graph**
4. Add these delegated permissions:
   - `User.Read` (Sign in and read user profile)
   - `Directory.Read.All` (Read directory data)
   - `Application.ReadWrite.All` (Read and write all applications)

### 3. Create Client Secret

1. Go to **Certificates & secrets**
2. Click **New client secret**
3. Configure:
   - **Description**: `MasterChief Client Secret`
   - **Expires**: `24 months`
4. **Copy the secret value immediately** (it won't be shown again)

### 4. Get Required Values

From your Azure AD app registration, collect:
- **Application (client) ID**: Found on the Overview page
- **Directory (tenant) ID**: Found on the Overview page
- **Client Secret**: The value you copied in step 3

## OKTA SSO Setup

### 1. Create OKTA Application

1. Log in to your [OKTA Admin Console](https://your-domain.okta.com/admin)
2. Go to **Applications** > **Applications**
3. Click **Create App Integration**
4. Select **OIDC - OpenID Connect** and **Web Application**
5. Configure:
   - **App integration name**: `MasterChief DevOps Platform`
   - **Sign-in redirect URIs**: `http://localhost:5000/auth/okta/callback`
   - **Sign-out redirect URIs**: `http://localhost:5000/`
   - **Assignments**: Assign to appropriate users/groups

### 2. Configure Claims

1. In your OKTA app, go to **Security** > **API** > **Authorization Servers**
2. Select your default authorization server
3. Go to **Claims** tab
4. Add custom claims as needed (optional)

### 3. Get Required Values

From your OKTA application:
- **Client ID**: Found in the General tab
- **Client Secret**: Found in the General tab
- **OKTA Domain**: Your OKTA domain (e.g., `your-domain.okta.com`)

## GitHub OAuth Setup

### 1. Create GitHub OAuth App

1. Go to [GitHub Settings](https://github.com/settings/developers)
2. Click **OAuth Apps** (or **Developer settings** > **OAuth Apps**)
3. Click **New OAuth App**
4. Configure:
   - **Application name**: `MasterChief DevOps Platform`
   - **Homepage URL**: `http://localhost:5000`
   - **Authorization callback URL**: `http://localhost:5000/auth/github/callback`
   - **Description**: `DevOps automation platform with GitHub integration`

### 2. Get Required Values

From your GitHub OAuth app:
- **Client ID**: Found on the app settings page
- **Client Secret**: Click **Generate a new client secret** and copy it

## Environment Configuration

### 1. Copy Environment Template

```bash
cp .env.example .env
```

### 2. Configure Azure Settings

Edit `.env` and add your Azure credentials:

```bash
# Azure AD Configuration
AZURE_CLIENT_ID=your-azure-client-id
AZURE_CLIENT_SECRET=your-azure-client-secret
AZURE_TENANT_ID=your-azure-tenant-id

# Azure SDK Configuration
AZURE_SUBSCRIPTION_ID=your-default-subscription-id
```

### 3. Configure OKTA Settings

Add OKTA configuration to `.env`:

```bash
# OKTA SSO Configuration
OKTA_DOMAIN=your-domain.okta.com
OKTA_CLIENT_ID=your-okta-client-id
OKTA_CLIENT_SECRET=your-okta-client-secret
OKTA_ISSUER=https://your-domain.okta.com/oauth2/default
```

### 4. Configure GitHub Settings

Add GitHub configuration to `.env`:

```bash
# GitHub OAuth Configuration
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

### 5. Additional Settings

Configure additional authentication settings:

```bash
# Flask Secret Key (generate a random string)
SECRET_KEY=your-random-secret-key-here

# Session Configuration
SESSION_TYPE=filesystem
SESSION_PERMANENT=True
PERMANENT_SESSION_LIFETIME=3600

# OAuth Settings
OAUTHLIB_INSECURE_TRANSPORT=1  # Remove in production
```

## Application Setup

### 1. Install Dependencies

```bash
# Install updated requirements
pip install -r requirements.txt
```

### 2. Run Setup Script

```bash
# Linux/Mac
./setup_auth.sh

# Windows
setup_auth.bat
```

### 3. Verify Configuration

The setup script will:
- Validate environment variables
- Test Azure SDK connectivity (if configured)
- Verify GitHub API access (if configured)
- Check OKTA configuration (if configured)

## Testing Authentication

### 1. Start the Application

```bash
python main.py
```

### 2. Access Web Interface

Open `http://localhost:5000/web-ide` in your browser.

### 3. Test Authentication Flows

1. **Azure AD Login**:
   - Click the Azure login button
   - Sign in with Azure AD credentials
   - Verify successful authentication

2. **OKTA SSO Login**:
   - Click the OKTA login button
   - Sign in with OKTA credentials
   - Verify successful authentication

3. **GitHub OAuth Login**:
   - Click the GitHub login button
   - Authorize the application
   - Verify successful authentication

### 4. Test API Endpoints

```bash
# Check authentication status
curl http://localhost:5000/auth/status

# Test Azure API (if authenticated)
curl -H "Cookie: session=<your-session-cookie>" \
  http://localhost:5000/api/azure/subscriptions

# Test GitHub API (if authenticated)
curl -H "Cookie: session=<your-session-cookie>" \
  http://localhost:5000/api/github/user
```

## Troubleshooting

### Common Issues

#### Azure AD Authentication Fails

**Symptoms**: "Invalid client" or "unauthorized_client" errors

**Solutions**:
1. Verify `AZURE_CLIENT_ID` and `AZURE_TENANT_ID` are correct
2. Ensure the redirect URI matches: `http://localhost:5000/auth/azure/callback`
3. Check that the client secret is valid and not expired
4. Verify API permissions are granted

#### OKTA SSO Issues

**Symptoms**: "Invalid token" or redirect errors

**Solutions**:
1. Confirm `OKTA_DOMAIN` is correct (without https://)
2. Verify `OKTA_CLIENT_ID` and `OKTA_CLIENT_SECRET`
3. Check redirect URI configuration in OKTA
4. Ensure the OKTA application is assigned to your user

#### GitHub OAuth Problems

**Symptoms**: "Bad credentials" or authorization failures

**Solutions**:
1. Verify `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET`
2. Check that the authorization callback URL is correct
3. Ensure the OAuth app is not suspended
4. Confirm you have the necessary GitHub permissions

#### Environment Variable Issues

**Symptoms**: "Missing required environment variable" errors

**Solutions**:
1. Check that `.env` file exists in the project root
2. Verify variable names match exactly (case-sensitive)
3. Ensure no extra spaces or quotes around values
4. Restart the application after changing `.env`

#### Session/Cookie Problems

**Symptoms**: Authentication works but APIs return unauthorized

**Solutions**:
1. Check browser developer tools for session cookies
2. Verify `SECRET_KEY` is set and consistent
3. Ensure `SESSION_TYPE` is properly configured
4. Check that the session isn't expired

### Debug Mode

Enable debug logging to troubleshoot issues:

```bash
# Set debug environment variable
export DEBUG_AUTH=1

# Run with debug output
python main.py
```

### Logs and Monitoring

Check application logs for detailed error information:

```bash
# View recent logs
tail -f masterchief.log

# Check for authentication-related errors
grep -i "auth" masterchief.log
```

### Getting Help

If you encounter issues not covered here:

1. Check the [GitHub Issues](https://github.com/jbalestrine/masterchief/issues) for similar problems
2. Review the [API Documentation](#) for endpoint details
3. Enable debug mode and collect logs before reporting issues

## Security Considerations

### Production Deployment

For production environments:

1. **HTTPS Only**: Always use HTTPS in production
2. **Secure Secrets**: Use Azure Key Vault or similar for secrets
3. **Environment Variables**: Never commit secrets to version control
4. **Session Security**: Configure secure session settings
5. **CORS**: Configure appropriate CORS policies
6. **Rate Limiting**: Implement rate limiting for API endpoints

### Best Practices

- Rotate client secrets regularly
- Use least-privilege access for service accounts
- Monitor authentication logs for suspicious activity
- Implement proper logout functionality
- Validate all input parameters
- Use secure random generators for secrets

## Next Steps

After successful authentication setup:

1. [Explore Azure Integration](docs/azure-integration.md) - Learn about Azure resource management
2. [GitHub API Guide](docs/github-integration.md) - Understand GitHub repository operations
3. [App Management](docs/app-management.md) - Manage OAuth applications
4. [API Reference](docs/api-reference.md) - Complete API documentation

---

For additional support, visit the [MasterChief Documentation](docs/README.md) or create an issue on GitHub.</content>
<parameter name="filePath">c:\Users\Echo\masterchief\AUTHENTICATION_SETUP.md