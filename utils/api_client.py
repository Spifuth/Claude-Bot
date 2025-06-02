"""
Homelab API Client
Handles all API communication with homelab services
"""

import aiohttp
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class HomelabClient:
    """Client for interacting with homelab API"""
    
    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        
    @property
    def headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Fenrir-Discord-Bot/1.0'
        }
    
    async def request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to homelab API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.request(
                    method=method.upper(),
                    url=url,
                    headers=self.headers,
                    json=data
                ) as response:
                    
                    # Log request for debugging
                    logger.debug(f"{method.upper()} {url} -> {response.status}")
                    
                    if response.content_type == 'application/json':
                        result = await response.json()
                    else:
                        result = {"message": await response.text()}
                    
                    # Add status code to result
                    result['_status_code'] = response.status
                    
                    return result
                    
        except aiohttp.ClientTimeout:
            logger.error(f"Timeout requesting {url}")
            return {"error": "Request timed out", "_status_code": 408}
        except aiohttp.ClientError as e:
            logger.error(f"Client error requesting {url}: {e}")
            return {"error": f"Connection error: {str(e)}", "_status_code": 500}
        except Exception as e:
            logger.error(f"Unexpected error requesting {url}: {e}")
            return {"error": f"Unexpected error: {str(e)}", "_status_code": 500}
    
    # Convenience methods for common operations
    async def get_status(self) -> Dict[str, Any]:
        """Get overall homelab status"""
        return await self.request('api/status')
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return await self.request('api/system')
    
    async def get_containers(self) -> Dict[str, Any]:
        """Get Docker containers"""
        return await self.request('api/docker/containers')
    
    async def restart_service(self, service_name: str) -> Dict[str, Any]:
        """Restart a service"""
        return await self.request(f'api/services/{service_name}/restart', method='POST')
    
    async def restart_compose_stack(self, stack_name: str) -> Dict[str, Any]:
        """Restart a Docker Compose stack"""
        return await self.request(f'api/docker/compose/{stack_name}/restart', method='POST')
    
    def is_configured(self) -> bool:
        """Check if the client is properly configured"""
        return bool(self.base_url and self.api_key)