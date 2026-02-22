"""REST API ingestion for IRC bot."""
import asyncio
import logging
import time
from typing import Any, Dict, Optional
from enum import Enum

import httpx

from .base import BaseIngestion, IngestionEvent, IngestionStatus

logger = logging.getLogger(__name__)


class AuthType(Enum):
    """API authentication types."""
    NONE = "none"
    API_KEY = "api_key"
    BEARER = "bearer"
    BASIC = "basic"
    OAUTH = "oauth"


class APIIngestion(BaseIngestion):
    """REST API polling ingestion."""
    
    def __init__(self, source_id: str, config: Dict[str, Any]):
        """
        Initialize API ingestion.
        
        Config options:
            - url: API endpoint URL
            - method: HTTP method (GET, POST, etc.)
            - auth_type: Authentication type
            - auth_config: Authentication configuration
            - polling_interval: Seconds between polls (default: 60)
            - headers: Custom headers
            - params: Query parameters
            - transform: JSONPath or jq expression to transform response
        """
        super().__init__(source_id, config)
        self.url = config.get('url')
        self.method = config.get('method', 'GET').upper()
        self.auth_type = AuthType(config.get('auth_type', 'none'))
        self.auth_config = config.get('auth_config', {})
        self.polling_interval = config.get('polling_interval', 60)
        self.headers = config.get('headers', {})
        self.params = config.get('params', {})
        self.transform = config.get('transform')
        self.last_data = None
        self._task = None
        self._client = None
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers based on auth type."""
        headers = self.headers.copy()
        
        if self.auth_type == AuthType.API_KEY:
            key = self.auth_config.get('key', 'X-API-Key')
            value = self.auth_config.get('value')
            if value:
                headers[key] = value
        
        elif self.auth_type == AuthType.BEARER:
            token = self.auth_config.get('token')
            if token:
                headers['Authorization'] = f"Bearer {token}"
        
        elif self.auth_type == AuthType.BASIC:
            username = self.auth_config.get('username')
            password = self.auth_config.get('password')
            if username and password:
                import base64
                credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                headers['Authorization'] = f"Basic {credentials}"
        
        return headers
    
    async def _fetch_data(self) -> Optional[Dict[str, Any]]:
        """Fetch data from API."""
        try:
            headers = self._get_auth_headers()
            
            response = await self._client.request(
                method=self.method,
                url=self.url,
                headers=headers,
                params=self.params,
                timeout=30.0
            )
            
            response.raise_for_status()
            
            # Parse response
            if response.headers.get('content-type', '').startswith('application/json'):
                data = response.json()
            else:
                data = {'content': response.text}
            
            # Apply transformation if configured
            if self.transform:
                data = self._transform_data(data)
            
            return data
        
        except Exception as e:
            logger.error(f"Error fetching API data: {e}")
            return None
    
    def _transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data using configured expression."""
        # Simple JSONPath-like access for now
        # Could be extended with jq or full JSONPath library
        try:
            parts = self.transform.split('.')
            result = data
            for part in parts:
                if '[' in part and ']' in part:
                    # Array access
                    key, idx = part.split('[')
                    idx = int(idx.rstrip(']'))
                    result = result[key][idx]
                else:
                    result = result[part]
            return {'transformed': result}
        except Exception as e:
            logger.warning(f"Transform failed: {e}, returning original data")
            return data
    
    async def _poll_loop(self):
        """Main polling loop."""
        while self.status == IngestionStatus.RUNNING:
            try:
                data = await self._fetch_data()
                
                if data is not None:
                    # Check if data changed (optional deduplication)
                    if data != self.last_data:
                        event = IngestionEvent(
                            source_type="api",
                            source_id=self.source_id,
                            data=data,
                            metadata={
                                'url': self.url,
                                'method': self.method,
                                'changed': data != self.last_data
                            },
                            timestamp=time.time()
                        )
                        
                        await self._dispatch_event(event)
                        self.last_data = data
                
                # Wait for next poll
                await asyncio.sleep(self.polling_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in poll loop: {e}")
                await asyncio.sleep(self.polling_interval)
    
    async def start(self):
        """Start API polling."""
        self.status = IngestionStatus.STARTING
        try:
            self._client = httpx.AsyncClient()
            self.status = IngestionStatus.RUNNING
            self._task = asyncio.create_task(self._poll_loop())
            logger.info(f"API polling started for {self.url}")
        except Exception as e:
            self.status = IngestionStatus.ERROR
            logger.error(f"Failed to start API polling: {e}")
            raise
    
    async def stop(self):
        """Stop API polling."""
        self.status = IngestionStatus.STOPPED
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._client:
            await self._client.aclose()
        logger.info(f"API polling stopped")
