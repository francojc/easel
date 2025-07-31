# ADR 005: Authentication Strategy

**Status:** Accepted  
**Date:** 2025-07-31  
**Deciders:** Jerid Francom, Development Team  
**Technical Story:** Secure and flexible authentication system for Canvas API access  

## Context and Problem Statement

Easel requires a robust authentication strategy to securely access Canvas APIs while providing excellent user experience. The system must handle Canvas API tokens securely, support future authentication methods (OAuth2), and work across different deployment scenarios (desktop, server, CI/CD).

Key requirements:

- Secure storage and transmission of Canvas API tokens
- Support for Canvas Personal Access Tokens (current primary method)
- Future extensibility for OAuth2 when Canvas supports it better
- Environment variable overrides for automation scenarios
- Token validation and refresh capabilities
- Cross-platform security (keyring integration where available)

## Decision Drivers

- **Security:** Tokens must be stored and transmitted securely
- **User Experience:** Simple setup and minimal ongoing token management
- **Automation Friendly:** Environment variable support for CI/CD
- **Future Proofing:** Architecture that can support OAuth2 and other methods
- **Canvas Compatibility:** Work within Canvas's current authentication limitations
- **Cross-platform:** Consistent behavior across Linux, macOS, and Windows

## Considered Options

- **Personal Access Tokens** with secure local storage
- **OAuth2 Authorization Code Flow** (limited Canvas support)
- **OAuth2 Client Credentials Flow** (for service accounts)
- **Canvas Developer Keys** with custom authentication flow
- **Hybrid Approach** supporting multiple authentication methods

## Decision Outcome

**Chosen option:** "Personal Access Tokens with secure local storage and hybrid architecture"

**Rationale:** Canvas Personal Access Tokens provide the most reliable authentication method currently available, while designing a hybrid architecture allows future OAuth2 integration when Canvas support improves. This balances immediate usability with future extensibility.

### Positive Consequences

- Simple user setup with Canvas's built-in token generation
- Secure local storage using system keyring where available
- Environment variable override for automation scenarios
- Architecture ready for OAuth2 when Canvas support improves
- Consistent behavior across different deployment environments

### Negative Consequences

- Manual token setup required (no automatic refresh)
- Token expiration handling is manual
- Limited to Canvas's token-based permissions model

## Pros and Cons of the Options

### Personal Access Tokens with Secure Storage

**Description:** Use Canvas Personal Access Tokens with encrypted local storage

**Pros:**

- Canvas fully supports Personal Access Tokens
- Simple user setup through Canvas UI
- No callback URL or application registration required
- Works consistently across all Canvas instances
- User controls token scope and expiration

**Cons:**

- Manual token generation and setup
- No automatic token refresh capability
- Token expiration requires manual intervention
- Limited to user's Canvas permissions

### OAuth2 Authorization Code Flow

**Description:** Full OAuth2 implementation with browser-based authorization

**Pros:**

- Industry standard authentication flow
- Automatic token refresh capability
- Better security with short-lived access tokens
- Granular permission scoping

**Cons:**

- Canvas OAuth2 support is inconsistent across instances
- Requires application registration with each Canvas instance
- Complex setup for institutions
- Callback URL requirements complicate CLI usage
- Not all Canvas instances enable OAuth2

### OAuth2 Client Credentials Flow

**Description:** Service account style authentication for server deployments

**Pros:**

- Excellent for server-side automation
- No user interaction required
- Automatic token refresh
- Service account permissions model

**Cons:**

- Not widely supported by Canvas instances
- Requires institutional Canvas admin setup
- Complex permission management
- Limited to service account use cases

### Canvas Developer Keys

**Description:** Custom authentication using Canvas Developer Keys

**Pros:**

- More control over authentication flow
- Institution-level configuration
- Can provide enhanced permissions

**Cons:**

- Requires Canvas admin involvement for setup
- Complex implementation and maintenance
- Not standardized across Canvas instances
- Overkill for most use cases

### Hybrid Authentication Architecture

**Description:** Pluggable authentication system supporting multiple methods

**Pros:**

- Future-proof architecture
- Supports different deployment scenarios
- Can evolve with Canvas API improvements
- Flexible for different institutional needs

**Cons:**

- Added complexity in initial implementation
- Potential configuration confusion for users
- Maintenance overhead for multiple auth methods

## Implementation Notes

### Authentication Interface Design

```python
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass
import httpx

@dataclass
class AuthCredentials:
    """Container for authentication credentials"""
    token: str
    token_type: str = "Bearer"
    expires_at: Optional[datetime] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None

class AuthenticationProvider(ABC):
    """Abstract base class for authentication providers"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for this auth method"""
        pass
    
    @abstractmethod
    async def authenticate(self, **kwargs) -> AuthCredentials:
        """Perform authentication and return credentials"""
        pass
    
    @abstractmethod
    async def refresh_credentials(self, credentials: AuthCredentials) -> AuthCredentials:
        """Refresh expired credentials if possible"""
        pass
    
    @abstractmethod
    def is_credentials_valid(self, credentials: AuthCredentials) -> bool:
        """Check if credentials are still valid"""
        pass
    
    def apply_auth(self, request: httpx.Request, credentials: AuthCredentials) -> None:
        """Apply authentication to HTTP request"""
        request.headers["Authorization"] = f"{credentials.token_type} {credentials.token}"

class AuthenticationManager:
    """Manages authentication providers and credentials"""
    
    def __init__(self):
        self._providers: Dict[str, AuthenticationProvider] = {}
        self._current_provider: Optional[str] = None
        self._credentials: Optional[AuthCredentials] = None
    
    def register_provider(self, provider: AuthenticationProvider) -> None:
        """Register an authentication provider"""
        self._providers[provider.name] = provider
    
    def set_provider(self, provider_name: str) -> None:
        """Set the active authentication provider"""
        if provider_name not in self._providers:
            raise ValueError(f"Unknown auth provider: {provider_name}")
        self._current_provider = provider_name
    
    async def authenticate(self, **kwargs) -> AuthCredentials:
        """Authenticate using the current provider"""
        if not self._current_provider:
            raise ValueError("No authentication provider selected")
        
        provider = self._providers[self._current_provider]
        self._credentials = await provider.authenticate(**kwargs)
        return self._credentials
    
    def apply_auth(self, request: httpx.Request) -> None:
        """Apply authentication to HTTP request"""
        if not self._credentials or not self._current_provider:
            raise ValueError("No valid credentials available")
        
        provider = self._providers[self._current_provider]
        
        # Refresh credentials if needed
        if not provider.is_credentials_valid(self._credentials):
            asyncio.create_task(self._refresh_credentials())
        
        provider.apply_auth(request, self._credentials)
```

### Personal Access Token Provider

```python
import os
from datetime import datetime, timedelta
from typing import Optional
import httpx

class PersonalAccessTokenProvider(AuthenticationProvider):
    """Canvas Personal Access Token authentication"""
    
    @property
    def name(self) -> str:
        return "personal_access_token"
    
    async def authenticate(self, token: str, canvas_url: str, **kwargs) -> AuthCredentials:
        """Authenticate using Personal Access Token"""
        
        # Validate token by making a test API call
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{canvas_url}/api/v1/users/self",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 401:
                raise AuthenticationError("Invalid Canvas API token")
            elif response.status_code != 200:
                raise AuthenticationError(f"Token validation failed: {response.status_code}")
        
        # Personal access tokens don't have automatic expiration info
        # We'll assume they're long-lived unless Canvas tells us otherwise
        return AuthCredentials(
            token=token,
            token_type="Bearer",
            expires_at=None  # Unknown expiration
        )
    
    async def refresh_credentials(self, credentials: AuthCredentials) -> AuthCredentials:
        """Personal access tokens cannot be refreshed automatically"""
        raise AuthenticationError("Personal access tokens cannot be refreshed automatically. "
                                "Please generate a new token in Canvas.")
    
    def is_credentials_valid(self, credentials: AuthCredentials) -> bool:
        """Check if credentials are still valid"""
        if not credentials.token:
            return False
        
        # Personal access tokens don't provide expiration info
        # We'll assume they're valid unless we get a 401
        return True

class EnvironmentTokenProvider(PersonalAccessTokenProvider):
    """Get Personal Access Token from environment variables"""
    
    @property
    def name(self) -> str:
        return "environment_token"
    
    async def authenticate(self, canvas_url: str, **kwargs) -> AuthCredentials:
        """Get token from environment variable"""
        token = os.environ.get("CANVAS_API_TOKEN")
        if not token:
            raise AuthenticationError("CANVAS_API_TOKEN environment variable not set")
        
        return await super().authenticate(token=token, canvas_url=canvas_url, **kwargs)
```

### Future OAuth2 Provider

```python
from urllib.parse import urlencode, parse_qs, urlparse
import secrets
import base64
import hashlib

class OAuth2Provider(AuthenticationProvider):
    """OAuth2 Authorization Code Flow provider (future implementation)"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
    
    @property
    def name(self) -> str:
        return "oauth2"
    
    async def authenticate(self, canvas_url: str, **kwargs) -> AuthCredentials:
        """Perform OAuth2 authorization code flow"""
        
        # Generate PKCE parameters
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip('=')
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip('=')
        
        state = secrets.token_urlsafe(32)
        
        # Build authorization URL
        auth_params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'read write',
            'state': state,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'
        }
        
        auth_url = f"{canvas_url}/login/oauth2/auth?" + urlencode(auth_params)
        
        click.echo(f"Please visit: {auth_url}")
        click.echo("After authorizing, copy the full redirect URL:")
        
        redirect_response = click.prompt("Redirect URL")
        
        # Parse authorization code from redirect
        parsed_url = urlparse(redirect_response)
        query_params = parse_qs(parsed_url.query)
        
        if 'error' in query_params:
            raise AuthenticationError(f"OAuth2 error: {query_params['error'][0]}")
        
        auth_code = query_params.get('code', [None])[0]
        returned_state = query_params.get('state', [None])[0]
        
        if not auth_code:
            raise AuthenticationError("No authorization code received")
        
        if returned_state != state:
            raise AuthenticationError("Invalid state parameter")
        
        # Exchange authorization code for access token
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'code': auth_code,
            'code_verifier': code_verifier
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{canvas_url}/login/oauth2/token",
                data=token_data
            )
            
            if response.status_code != 200:
                raise AuthenticationError(f"Token exchange failed: {response.status_code}")
            
            token_response = response.json()
        
        # Calculate expiration time
        expires_in = token_response.get('expires_in', 3600)
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        
        return AuthCredentials(
            token=token_response['access_token'],
            token_type=token_response.get('token_type', 'Bearer'),
            expires_at=expires_at,
            refresh_token=token_response.get('refresh_token'),
            scope=token_response.get('scope')
        )
    
    async def refresh_credentials(self, credentials: AuthCredentials) -> AuthCredentials:
        """Refresh OAuth2 access token"""
        if not credentials.refresh_token:
            raise AuthenticationError("No refresh token available")
        
        # Implementation would refresh the token using the refresh token
        # This is a simplified version
        raise NotImplementedError("OAuth2 token refresh not yet implemented")
```

### Secure Credential Storage Integration

```python
from easel.config import CredentialManager

class AuthenticatedAPIClient:
    """API client with authentication integration"""
    
    def __init__(self, canvas_url: str, auth_manager: AuthenticationManager):
        self.canvas_url = canvas_url
        self.auth_manager = auth_manager
        self.credential_manager = CredentialManager(get_config_dir())
        
        # Configure httpx client
        self.client = httpx.AsyncClient(
            base_url=f"{canvas_url}/api/v1",
            timeout=httpx.Timeout(30.0)
        )
        
        # Add authentication middleware
        self.client.event_hooks['request'] = [self._apply_auth]
    
    async def _apply_auth(self, request: httpx.Request) -> None:
        """Apply authentication to outgoing requests"""
        try:
            self.auth_manager.apply_auth(request)
        except ValueError:
            # No credentials available, try to load from storage
            await self._load_stored_credentials()
            self.auth_manager.apply_auth(request)
    
    async def _load_stored_credentials(self) -> None:
        """Load stored credentials and authenticate"""
        # Try to get stored token
        stored_token = self.credential_manager.get_token("default")
        if stored_token:
            # Use personal access token provider
            provider = PersonalAccessTokenProvider()
            self.auth_manager.register_provider(provider)
            self.auth_manager.set_provider(provider.name)
            await self.auth_manager.authenticate(
                token=stored_token,
                canvas_url=self.canvas_url
            )
        else:
            raise AuthenticationError("No stored credentials found. Run 'easel init' to configure.")
```

### CLI Integration

```python
@click.command()
@click.option('--auth-method', 
              type=click.Choice(['personal_token', 'environment', 'oauth2']),
              default='personal_token',
              help='Authentication method to use')
def configure_auth(auth_method: str):
    """Configure authentication for Easel"""
    
    auth_manager = AuthenticationManager()
    
    if auth_method == 'personal_token':
        token = click.prompt("Canvas API Token", hide_input=True)
        canvas_url = click.prompt("Canvas URL")
        
        provider = PersonalAccessTokenProvider()
        auth_manager.register_provider(provider)
        auth_manager.set_provider(provider.name)
        
        # Test authentication
        credentials = asyncio.run(auth_manager.authenticate(
            token=token,
            canvas_url=canvas_url
        ))
        
        # Store credentials securely
        credential_manager = CredentialManager(get_config_dir())
        credential_manager.store_token("default", token)
        
        click.echo("✅ Authentication configured successfully!")
    
    elif auth_method == 'environment':
        click.echo("Set the CANVAS_API_TOKEN environment variable with your Canvas API token.")
        click.echo("Example: export CANVAS_API_TOKEN=your_token_here")
    
    elif auth_method == 'oauth2':
        click.echo("⚠️  OAuth2 support is experimental and requires Canvas admin configuration.")
        # OAuth2 setup would go here
```

## Links

- [Canvas API Authentication](https://canvas.instructure.com/doc/api/file.oauth.html)
- [Canvas Personal Access Tokens](https://canvas.instructure.com/doc/api/file.oauth.html#manual-token-generation)
- [OAuth 2.0 RFC](https://tools.ietf.org/html/rfc6749)
- [PKCE RFC](https://tools.ietf.org/html/rfc7636)
- [Python Keyring Documentation](https://pypi.org/project/keyring/)