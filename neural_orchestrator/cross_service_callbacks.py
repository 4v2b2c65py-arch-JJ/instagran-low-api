"""
Cross-Service Callback Mechanisms
Provides easy parcel recovery methods and cross-service communication
without connection loss for Linux userland deployment.
"""

import asyncio
import json
import uuid
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
import hashlib


class CallbackStatus(Enum):
    """Status of callback operations."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class ParcelPriority(Enum):
    """Priority levels for parcel delivery."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class CallbackParcel:
    """Represents a parcel for cross-service callback."""
    parcel_id: str
    source_service: str
    target_service: str
    payload: Dict[str, Any]
    priority: ParcelPriority
    status: CallbackStatus
    created_at: str
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 30
    callback_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class CallbackResponse:
    """Represents a callback response."""
    parcel_id: str
    success: bool
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


class CrossServiceCallbackManager:
    """
    Manages cross-service callbacks with automatic retry and parcel recovery.
    Ensures no connection loss during Linux userland deployment.
    """

    def __init__(self, max_parcels: int = 1000):
        self.max_parcels = max_parcels
        self.pending_parcels: Dict[str, CallbackParcel] = {}
        self.completed_parcels: Dict[str, CallbackResponse] = {}
        self.service_endpoints: Dict[str, str] = {}
        self.callback_handlers: Dict[str, Callable] = {}
        self.recovery_queue: List[str] = []
        self.session_token: str = self._generate_session_token()

    def _generate_session_token(self) -> str:
        """Generate unique session token for this instance."""
        return hashlib.sha256(
            f"{datetime.utcnow().isoformat()}_{uuid.uuid4()}".encode()
        ).hexdigest()[:32]

    def register_service_endpoint(self, service_name: str, endpoint_url: str) -> None:
        """
        Register a service endpoint for callbacks.
        
        Args:
            service_name: Name of the service
            endpoint_url: URL endpoint for the service
        """
        self.service_endpoints[service_name] = endpoint_url

    def register_callback_handler(self, service_name: str, handler: Callable) -> None:
        """
        Register a callback handler for a service.
        
        Args:
            service_name: Name of the service
            handler: Async callback handler function
        """
        self.callback_handlers[service_name] = handler

    def create_parcel(
        self,
        source_service: str,
        target_service: str,
        payload: Dict[str, Any],
        priority: ParcelPriority = ParcelPriority.NORMAL,
        callback_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CallbackParcel:
        """
        Create a callback parcel for cross-service communication.
        
        Args:
            source_service: Source service name
            target_service: Target service name
            payload: Data payload
            priority: Priority level
            callback_url: Optional callback URL
            metadata: Optional metadata
            
        Returns:
            CallbackParcel: Created parcel
        """
        parcel_id = self._generate_parcel_id(source_service, target_service)
        
        parcel = CallbackParcel(
            parcel_id=parcel_id,
            source_service=source_service,
            target_service=target_service,
            payload=payload,
            priority=priority,
            status=CallbackStatus.PENDING,
            created_at=datetime.utcnow().isoformat(),
            callback_url=callback_url,
            metadata=metadata or {}
        )
        
        self._add_to_pending(parcel)
        return parcel

    def _generate_parcel_id(self, source: str, target: str) -> str:
        """Generate unique parcel ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        unique_hash = hashlib.md5(f"{source}_{target}_{uuid.uuid4()}".encode()).hexdigest()[:8]
        return f"{timestamp}_{source}_{target}_{unique_hash}"

    def _add_to_pending(self, parcel: CallbackParcel) -> None:
        """Add parcel to pending queue with size management."""
        if len(self.pending_parcels) >= self.max_parcels:
            # Remove oldest low-priority parcels
            to_remove = [
                pid for pid, p in self.pending_parcels.items()
                if p.priority == ParcelPriority.LOW
            ]
            for pid in to_remove[:10]:  # Remove up to 10 old parcels
                del self.pending_parcels[pid]
        
        self.pending_parcels[parcel.parcel_id] = parcel

    async def send_parcel(self, parcel_id: str) -> CallbackResponse:
        """
        Send a parcel to the target service.
        
        Args:
            parcel_id: Parcel identifier
            
        Returns:
            CallbackResponse: Response from the service
        """
        parcel = self.pending_parcels.get(parcel_id)
        if not parcel:
            return CallbackResponse(
                parcel_id=parcel_id,
                success=False,
                error_message="Parcel not found"
            )
        
        parcel.status = CallbackStatus.IN_PROGRESS
        
        try:
            # Check if local handler exists
            if parcel.target_service in self.callback_handlers:
                response = await self._execute_local_handler(parcel)
            else:
                response = await self._execute_http_callback(parcel)
            
            if response.success:
                parcel.status = CallbackStatus.COMPLETED
                self.completed_parcels[parcel_id] = response
                del self.pending_parcels[parcel_id]
            else:
                await self._handle_failed_parcel(parcel, response.error_message)
            
            return response
            
        except Exception as e:
            error_msg = f"Callback execution error: {str(e)}"
            await self._handle_failed_parcel(parcel, error_msg)
            return CallbackResponse(
                parcel_id=parcel_id,
                success=False,
                error_message=error_msg
            )

    async def _execute_local_handler(self, parcel: CallbackParcel) -> CallbackResponse:
        """Execute local callback handler."""
        handler = self.callback_handlers[parcel.target_service]
        try:
            result = await handler(parcel.payload)
            return CallbackResponse(
                parcel_id=parcel.parcel_id,
                success=True,
                response_data=result if isinstance(result, dict) else {"result": result}
            )
        except Exception as e:
            return CallbackResponse(
                parcel_id=parcel.parcel_id,
                success=False,
                error_message=str(e)
            )

    async def _execute_http_callback(self, parcel: CallbackParcel) -> CallbackResponse:
        """Execute HTTP callback to remote service."""
        endpoint = self.service_endpoints.get(parcel.target_service)
        if not endpoint:
            return CallbackResponse(
                parcel_id=parcel.parcel_id,
                success=False,
                error_message=f"No endpoint registered for {parcel.target_service}"
            )
        
        callback_url = parcel.callback_url or endpoint
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    callback_url,
                    json={
                        "parcel_id": parcel.parcel_id,
                        "source": parcel.source_service,
                        "payload": parcel.payload,
                        "metadata": parcel.metadata,
                        "session_token": self.session_token
                    },
                    timeout=aiohttp.ClientTimeout(total=parcel.timeout_seconds)
                ) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        return CallbackResponse(
                            parcel_id=parcel.parcel_id,
                            success=True,
                            response_data=response_data
                        )
                    else:
                        error_text = await response.text()
                        return CallbackResponse(
                            parcel_id=parcel.parcel_id,
                            success=False,
                            error_message=f"HTTP {response.status}: {error_text}"
                        )
        except asyncio.TimeoutError:
            return CallbackResponse(
                parcel_id=parcel.parcel_id,
                success=False,
                error_message="Request timeout"
            )
        except Exception as e:
            return CallbackResponse(
                parcel_id=parcel.parcel_id,
                success=False,
                error_message=str(e)
            )

    async def _handle_failed_parcel(self, parcel: CallbackParcel, error_message: str) -> None:
        """Handle failed parcel with retry logic."""
        parcel.retry_count += 1
        
        if parcel.retry_count < parcel.max_retries:
            parcel.status = CallbackStatus.RETRYING
            # Add to recovery queue
            if parcel.parcel_id not in self.recovery_queue:
                self.recovery_queue.append(parcel.parcel_id)
        else:
            parcel.status = CallbackStatus.FAILED
            self.completed_parcels[parcel.parcel_id] = CallbackResponse(
                parcel_id=parcel.parcel_id,
                success=False,
                error_message=f"Max retries exceeded: {error_message}"
            )
            del self.pending_parcels[parcel.parcel_id]

    async def process_recovery_queue(self) -> int:
        """
        Process parcels in the recovery queue.
        
        Returns:
            Number of parcels processed
        """
        processed = 0
        while self.recovery_queue:
            parcel_id = self.recovery_queue.pop(0)
            parcel = self.pending_parcels.get(parcel_id)
            
            if parcel and parcel.status == CallbackStatus.RETRYING:
                response = await self.send_parcel(parcel_id)
                processed += 1
        
        return processed

    async def send_batch_parcels(self, parcel_ids: List[str]) -> List[CallbackResponse]:
        """
        Send multiple parcels in batch.
        
        Args:
            parcel_ids: List of parcel identifiers
            
        Returns:
            List of callback responses
        """
        tasks = [self.send_parcel(pid) for pid in parcel_ids]
        return await asyncio.gather(*tasks)

    def get_parcel_status(self, parcel_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a parcel."""
        if parcel_id in self.pending_parcels:
            parcel = self.pending_parcels[parcel_id]
            return {
                "status": parcel.status.value,
                "retry_count": parcel.retry_count,
                "created_at": parcel.created_at,
                "priority": parcel.priority.value
            }
        elif parcel_id in self.completed_parcels:
            response = self.completed_parcels[parcel_id]
            return {
                "status": "completed",
                "success": response.success,
                "timestamp": response.timestamp,
                "error": response.error_message
            }
        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get callback manager statistics."""
        priority_counts = {}
        for parcel in self.pending_parcels.values():
            priority_name = parcel.priority.name
            priority_counts[priority_name] = priority_counts.get(priority_name, 0) + 1
        
        return {
            "session_token": self.session_token,
            "pending_parcels": len(self.pending_parcels),
            "completed_parcels": len(self.completed_parcels),
            "recovery_queue_size": len(self.recovery_queue),
            "registered_services": len(self.service_endpoints),
            "registered_handlers": len(self.callback_handlers),
            "priority_distribution": priority_counts
        }

    def export_state(self) -> str:
        """Export current state for recovery."""
        state = {
            "session_token": self.session_token,
            "pending_parcels": [asdict(p) for p in self.pending_parcels.values()],
            "completed_parcels": [asdict(r) for r in self.completed_parcels.values()],
            "service_endpoints": self.service_endpoints,
            "recovery_queue": self.recovery_queue,
            "export_timestamp": datetime.utcnow().isoformat()
        }
        return json.dumps(state, indent=2)

    def import_state(self, state_json: str) -> bool:
        """
        Import state for recovery.
        
        Args:
            state_json: JSON string of exported state
            
        Returns:
            True if import successful
        """
        try:
            state = json.loads(state_json)
            self.session_token = state.get("session_token", self._generate_session_token())
            self.service_endpoints = state.get("service_endpoints", {})
            self.recovery_queue = state.get("recovery_queue", [])
            
            # Restore parcels
            for parcel_data in state.get("pending_parcels", []):
                parcel = CallbackParcel(**parcel_data)
                parcel.status = CallbackStatus(parcel_data["status"])
                parcel.priority = ParcelPriority(parcel_data["priority"])
                self.pending_parcels[parcel.parcel_id] = parcel
            
            for response_data in state.get("completed_parcels", []):
                response = CallbackResponse(**response_data)
                self.completed_parcels[response.parcel_id] = response
            
            return True
        except Exception as e:
            print(f"State import failed: {e}")
            return False

    def clear_old_completed(self, age_hours: int = 24) -> int:
        """
        Clear completed parcels older than specified age.
        
        Args:
            age_hours: Age threshold in hours
            
        Returns:
            Number of parcels cleared
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=age_hours)
        to_remove = []
        
        for parcel_id, response in self.completed_parcels.items():
            response_time = datetime.fromisoformat(response.timestamp)
            if response_time < cutoff_time:
                to_remove.append(parcel_id)
        
        for parcel_id in to_remove:
            del self.completed_parcels[parcel_id]
        
        return len(to_remove)
