"""
API Handler - API Interaction Handlers
Handles API interactions for autonomous agent operations.
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class APIRequest:
    """Represents an API request."""
    request_id: str
    endpoint: str
    method: str
    headers: Dict[str, str]
    data: Optional[Dict[str, any]]
    timestamp: float


@dataclass
class APIResponse:
    """Represents an API response."""
    response_id: str
    request_id: str
    status_code: int
    data: Optional[Dict[str, any]]
    error: Optional[str]
    timestamp: float
    duration_ms: float


class APIHandler:
    """
    Handles API interactions for autonomous agent operations.
    Manages HTTP requests, responses, and error handling.
    """
    
    def __init__(self, base_url: str = "", timeout: float = 30.0):
        """
        Initialize the API Handler.
        
        Args:
            base_url: Base URL for API requests
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.timeout = timeout
        
        # Request/Response tracking
        self.request_history: List[APIRequest] = []
        self.response_history: List[APIResponse] = []
        
        # Session management
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Authentication
        self.auth_token: Optional[str] = None
        self.api_key: Optional[str] = None
        
        # Rate limiting
        self.rate_limit_delay = 0.1
        self.last_request_time = 0.0
    
    async def initialize_session(self):
        """Initialize the HTTP session."""
        if self.session is None or self.session.closed:
            headers = {}
            if self.auth_token:
                headers['Authorization'] = f'Bearer {self.auth_token}'
            if self.api_key:
                headers['X-API-Key'] = self.api_key
            
            self.session = aiohttp.ClientSession(headers=headers)
    
    async def close_session(self):
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def make_request(
        self,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict[str, any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """
        Make an API request.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            data: Request data
            headers: Additional headers
            
        Returns:
            APIResponse object
        """
        await self.initialize_session()
        
        # Rate limiting
        current_time = datetime.now().timestamp()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        
        # Create request
        request = APIRequest(
            request_id=f"req_{len(self.request_history)}_{datetime.now().timestamp()}",
            endpoint=endpoint,
            method=method,
            headers=headers or {},
            data=data,
            timestamp=datetime.now().timestamp()
        )
        
        self.request_history.append(request)
        self.last_request_time = datetime.now().timestamp()
        
        # Make request
        start_time = datetime.now().timestamp()
        try:
            url = f"{self.base_url}{endpoint}" if self.base_url else endpoint
            
            async with self.session.request(
                method=method,
                url=url,
                json=data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                response_data = None
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                api_response = APIResponse(
                    response_id=f"resp_{len(self.response_history)}_{datetime.now().timestamp()}",
                    request_id=request.request_id,
                    status_code=response.status,
                    data=response_data,
                    error=None,
                    timestamp=datetime.now().timestamp(),
                    duration_ms=(datetime.now().timestamp() - start_time) * 1000
                )
                
        except Exception as e:
            api_response = APIResponse(
                response_id=f"resp_{len(self.response_history)}_{datetime.now().timestamp()}",
                request_id=request.request_id,
                status_code=0,
                data=None,
                error=str(e),
                timestamp=datetime.now().timestamp(),
                duration_ms=(datetime.now().timestamp() - start_time) * 1000
            )
        
        self.response_history.append(api_response)
        
        # Keep history manageable
        if len(self.request_history) > 1000:
            self.request_history.pop(0)
        if len(self.response_history) > 1000:
            self.response_history.pop(0)
        
        return api_response
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> APIResponse:
        """
        Make a GET request.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            APIResponse object
        """
        return await self.make_request(endpoint, method="GET", data=params)
    
    async def post(self, endpoint: str, data: Optional[Dict] = None) -> APIResponse:
        """
        Make a POST request.
        
        Args:
            endpoint: API endpoint
            data: Request data
            
        Returns:
            APIResponse object
        """
        return await self.make_request(endpoint, method="POST", data=data)
    
    async def put(self, endpoint: str, data: Optional[Dict] = None) -> APIResponse:
        """
        Make a PUT request.
        
        Args:
            endpoint: API endpoint
            data: Request data
            
        Returns:
            APIResponse object
        """
        return await self.make_request(endpoint, method="PUT", data=data)
    
    async def delete(self, endpoint: str) -> APIResponse:
        """
        Make a DELETE request.
        
        Args:
            endpoint: API endpoint
            
        Returns:
            APIResponse object
        """
        return await self.make_request(endpoint, method="DELETE")
    
    def set_auth_token(self, token: str):
        """
        Set authentication token.
        
        Args:
            token: Auth token
        """
        self.auth_token = token
        # Reinitialize session with new headers
        if self.session and not self.session.closed:
            asyncio.create_task(self.close_session())
    
    def set_api_key(self, api_key: str):
        """
        Set API key.
        
        Args:
            api_key: API key
        """
        self.api_key = api_key
        # Reinitialize session with new headers
        if self.session and not self.session.closed:
            asyncio.create_task(self.close_session())
    
    def set_rate_limit(self, delay: float):
        """
        Set rate limit delay.
        
        Args:
            delay: Delay between requests in seconds
        """
        self.rate_limit_delay = delay
    
    def get_request_statistics(self) -> Dict[str, any]:
        """
        Get statistics about API requests.
        
        Returns:
            Dictionary containing request statistics
        """
        if not self.response_history:
            return {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0
            }
        
        successful = sum(1 for r in self.response_history if r.status_code >= 200 and r.status_code < 300)
        failed = len(self.response_history) - successful
        
        durations = [r.duration_ms for r in self.response_history]
        
        return {
            'total_requests': len(self.response_history),
            'successful_requests': successful,
            'failed_requests': failed,
            'success_rate': successful / len(self.response_history),
            'avg_duration_ms': sum(durations) / len(durations),
            'min_duration_ms': min(durations),
            'max_duration_ms': max(durations)
        }
    
    def get_recent_responses(self, limit: int = 10) -> List[APIResponse]:
        """
        Get recent API responses.
        
        Args:
            limit: Maximum number of responses to return
            
        Returns:
            List of recent APIResponse objects
        """
        return self.response_history[-limit:] if self.response_history else []
    
    def clear_history(self):
        """Clear request and response history."""
        self.request_history.clear()
        self.response_history.clear()
