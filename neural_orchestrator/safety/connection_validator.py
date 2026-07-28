"""
Connection Validator - Connection Rejection/Acceptance Based on Handshake
Validates and acceptsrejects connections based on handshake agreement process.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from .safety_config import SafetyConfig
from .handshake_protocol import HandshakeProtocol, HandshakeStatus, ValidationStatus


class ConnectionDecision(Enum):
    """Connection decision."""
    ACCEPT = "accept"
    REJECT = "reject"
    PENDING = "pending"
    DEFER = "defer"


@dataclass
class ConnectionRequest:
    """Represents a connection request."""
    request_id: str
    requester_id: str
    target_id: str
    timestamp: float
    handshake_session_id: Optional[str]
    status: ConnectionDecision
    rejection_reason: Optional[str]


class ConnectionValidator:
    """
    Validates and accepts/rejects connections based on handshake.
    Knows which connections to reject and which are good based on handshake agreement.
    """
    
    def __init__(self, config: SafetyConfig, handshake_protocol: HandshakeProtocol):
        """
        Initialize Connection Validator.
        
        Args:
            config: Safety configuration
            handshake_protocol: Handshake protocol instance
        """
        self.config = config
        self.handshake_protocol = handshake_protocol
        
        # Connection rules
        self.connection_rules = config.get_connection_rules()
        self.reject_on = self.connection_rules.get('reject_on', [])
        self.accept_on = self.connection_rules.get('accept_on', [])
        
        # Connection requests
        self.connection_requests: Dict[str, ConnectionRequest] = {}
        
        # Accepted connections (for tracking)
        self.accepted_connections: Dict[str, List[str]] = {}  # key: user_id, value: list of connected user_ids
        
        # Rejected connections (for tracking)
        self.rejected_connections: Dict[str, List[str]] = {}  # key: user_id, value: list of rejected user_ids
    
    def request_connection(
        self,
        requester_id: str,
        target_id: str,
        handshake_data: Optional[Dict] = None
    ) -> ConnectionRequest:
        """
        Request a connection with another user.
        
        Args:
            requester_id: Requester user ID
            target_id: Target user ID
            handshake_data: Optional handshake data
            
        Returns:
            ConnectionRequest object
        """
        request_id = f"conn_{requester_id}_{target_id}_{datetime.now().timestamp()}"
        
        # Initiate handshake if required
        handshake_session_id = None
        if self.config.require_handshake:
            session = self.handshake_protocol.initiate_handshake(requester_id, target_id, handshake_data)
            handshake_session_id = session.session_id
        
        # Create connection request
        request = ConnectionRequest(
            request_id=request_id,
            requester_id=requester_id,
            target_id=target_id,
            timestamp=datetime.now().timestamp(),
            handshake_session_id=handshake_session_id,
            status=ConnectionDecision.PENDING,
            rejection_reason=None
        )
        
        self.connection_requests[request_id] = request
        
        return request
    
    def validate_connection(
        self,
        request_id: str,
        target_data: Dict
    ) -> ConnectionRequest:
        """
        Validate a connection request.
        
        Args:
            request_id: Connection request ID
            target_data: Target user data
            
        Returns:
            ConnectionRequest object with decision
        """
        if request_id not in self.connection_requests:
            raise ValueError("Request not found")
        
        request = self.connection_requests[request_id]
        
        # Check handshake if required
        if self.config.require_handshake and request.handshake_session_id:
            session = self.handshake_protocol.get_handshake_status(request.handshake_session_id)
            
            if not session:
                request.status = ConnectionDecision.REJECT
                request.rejection_reason = "handshake_not_found"
                return request
            
            # Respond to handshake
            self.handshake_protocol.respond_to_handshake(
                request.handshake_session_id,
                request.target_id,
                target_data
            )
            
            # Validate cross-side data
            validation_status, validation_results = self.handshake_protocol.validate_cross_side_data(
                request.handshake_session_id,
                target_data,
                target_data  # In real implementation, would use initiator data
            )
            
            # Check validation results
            if validation_status == ValidationStatus.FAILED:
                request.status = ConnectionDecision.REJECT
                request.rejection_reason = f"validation_failed: {validation_results}"
                self._track_rejection(request)
                return request
            
            # Complete handshake
            self.handshake_protocol.complete_handshake(request.handshake_session_id)
        
        # Apply connection rules
        decision = self._apply_connection_rules(request, target_data)
        
        request.status = decision
        
        if decision == ConnectionDecision.ACCEPT:
            self._track_acceptance(request)
        elif decision == ConnectionDecision.REJECT:
            self._track_rejection(request)
        
        return request
    
    def _apply_connection_rules(self, request: ConnectionRequest, target_data: Dict) -> ConnectionDecision:
        """Apply connection rules to make decision."""
        # Check reject conditions
        for condition in self.reject_on:
            if self._check_condition(condition, request, target_data):
                request.rejection_reason = f"rejected_on_{condition}"
                return ConnectionDecision.REJECT
        
        # Check accept conditions
        for condition in self.accept_on:
            if self._check_condition(condition, request, target_data):
                return ConnectionDecision.ACCEPT
        
        # Default to defer if no conditions met
        return ConnectionDecision.DEFER
    
    def _check_condition(self, condition: str, request: ConnectionRequest, target_data: Dict) -> bool:
        """Check if a condition is met."""
        if condition == "protocol_mismatch":
            return target_data.get('protocol_version') != self.config.version
        elif condition == "validation_failed":
            if request.handshake_session_id:
                session = self.handshake_protocol.get_handshake_status(request.handshake_session_id)
                return session and session.validation_status == ValidationStatus.FAILED
            return False
        elif condition == "high_risk_detected":
            return target_data.get('risk_score', 0) > self.config.max_risk_threshold
        elif condition == "handshake_timeout":
            if request.handshake_session_id:
                return self.handshake_protocol.check_timeout(request.handshake_session_id)
            return False
        elif condition == "user_data_invalid":
            required_fields = self.config.get_user_validation_config().get('required_fields', [])
            return not all(field in target_data for field in required_fields)
        elif condition == "handshake_complete":
            if request.handshake_session_id:
                session = self.handshake_protocol.get_handshake_status(request.handshake_session_id)
                return session and session.status == HandshakeStatus.COMPLETED
            return False
        elif condition == "validation_passed":
            if request.handshake_session_id:
                session = self.handshake_protocol.get_handshake_status(request.handshake_session_id)
                return session and session.validation_status == ValidationStatus.PASSED
            return False
        elif condition == "low_risk":
            return target_data.get('risk_score', 1.0) <= self.config.max_risk_threshold
        elif condition == "protocol_compatible":
            return target_data.get('protocol_version') == self.config.version
        
        return False
    
    def _track_acceptance(self, request: ConnectionRequest):
        """Track accepted connection."""
        if request.requester_id not in self.accepted_connections:
            self.accepted_connections[request.requester_id] = []
        self.accepted_connections[request.requester_id].append(request.target_id)
        
        if request.target_id not in self.accepted_connections:
            self.accepted_connections[request.target_id] = []
        self.accepted_connections[request.target_id].append(request.requester_id)
    
    def _track_rejection(self, request: ConnectionRequest):
        """Track rejected connection."""
        if request.requester_id not in self.rejected_connections:
            self.rejected_connections[request.requester_id] = []
        self.rejected_connections[request.requester_id].append(request.target_id)
        
        if request.target_id not in self.rejected_connections:
            self.rejected_connections[request.target_id] = []
        self.rejected_connections[request.target_id].append(request.requester_id)
    
    def is_connection_accepted(self, user_id: str, other_user_id: str) -> bool:
        """
        Check if connection between users is accepted.
        
        Args:
            user_id: First user ID
            other_user_id: Second user ID
            
        Returns:
            True if connection is accepted
        """
        if user_id not in self.accepted_connections:
            return False
        
        return other_user_id in self.accepted_connections[user_id]
    
    def is_connection_rejected(self, user_id: str, other_user_id: str) -> bool:
        """
        Check if connection between users is rejected.
        
        Args:
            user_id: First user ID
            other_user_id: Second user ID
            
        Returns:
            True if connection is rejected
        """
        if user_id not in self.rejected_connections:
            return False
        
        return other_user_id in self.rejected_connections[user_id]
    
    def get_user_connections(self, user_id: str) -> List[str]:
        """
        Get all accepted connections for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of connected user IDs
        """
        return self.accepted_connections.get(user_id, [])
    
    def get_connection_request(self, request_id: str) -> Optional[ConnectionRequest]:
        """Get a connection request by ID."""
        return self.connection_requests.get(request_id)
    
    def get_connection_statistics(self) -> Dict[str, any]:
        """
        Get statistics about connections.
        
        Returns:
            Dictionary containing connection statistics
        """
        total_requests = len(self.connection_requests)
        accepted = sum(1 for r in self.connection_requests.values() if r.status == ConnectionDecision.ACCEPT)
        rejected = sum(1 for r in self.connection_requests.values() if r.status == ConnectionDecision.REJECT)
        pending = sum(1 for r in self.connection_requests.values() if r.status == ConnectionDecision.PENDING)
        
        return {
            'total_requests': total_requests,
            'accepted_connections': accepted,
            'rejected_connections': rejected,
            'pending_requests': pending,
            'acceptance_rate': accepted / total_requests if total_requests > 0 else 0,
            'total_users': len(self.accepted_connections)
        }
