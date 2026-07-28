"""
Handshake Protocol - Handshake Agreement Process for Cross-Validation
Implements handshake agreement process before interaction with cross-side user data validation.
"""

import hashlib
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from .safety_config import SafetyConfig


class HandshakeStatus(Enum):
    """Status of handshake process."""
    INITIATED = "initiated"
    PENDING = "pending"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    REJECTED = "rejected"


class ValidationStatus(Enum):
    """Status of cross-validation."""
    PENDING = "pending"
    VALIDATING = "validating"
    PASSED = "passed"
    FAILED = "failed"
    INCOMPATIBLE = "incompatible"


@dataclass
class HandshakeSignature:
    """Represents a handshake signature."""
    user_id: str
    protocol_version: str
    timestamp: float
    signature: str
    safety_compliance: bool


@dataclass
class UserData:
    """Represents user data for validation."""
    user_id: str
    protocol_version: str
    safety_compliance: bool
    handshake_signature: str
    validation_data: Dict[str, any]
    timestamp: float


@dataclass
class HandshakeSession:
    """Represents a handshake session."""
    session_id: str
    initiator_id: str
    responder_id: str
    status: HandshakeStatus
    validation_status: ValidationStatus
    signature: Optional[HandshakeSignature]
    user_data: Optional[UserData]
    cross_validation_data: Optional[Dict]
    created_at: float
    completed_at: Optional[float]
    retry_count: int


class HandshakeProtocol:
    """
    Implements handshake agreement process for cross-validation.
    Validates cross-side user data before interaction occurs.
    """
    
    def __init__(self, config: SafetyConfig):
        """
        Initialize the Handshake Protocol.
        
        Args:
            config: Safety configuration
        """
        self.config = config
        
        # Active handshake sessions
        self.sessions: Dict[str, HandshakeSession] = {}
        
        # Completed handshakes (for tracking)
        self.completed_handshakes: Dict[str, List[str]] = {}  # key: user_id, value: list of session_ids
        
        # Protocol compatibility cache
        self.compatibility_cache: Dict[str, bool] = {}
    
    def initiate_handshake(
        self,
        initiator_id: str,
        responder_id: str,
        initiator_data: Optional[Dict] = None
    ) -> HandshakeSession:
        """
        Initiate a handshake with another user.
        
        Args:
            initiator_id: Initiator user ID
            responder_id: Responder user ID
            initiator_data: Optional initiator data
            
        Returns:
            HandshakeSession object
        """
        session_id = f"handshake_{initiator_id}_{responder_id}_{datetime.now().timestamp()}"
        
        # Create initiator signature
        signature = self._create_signature(initiator_id)
        
        session = HandshakeSession(
            session_id=session_id,
            initiator_id=initiator_id,
            responder_id=responder_id,
            status=HandshakeStatus.INITIATED,
            validation_status=ValidationStatus.PENDING,
            signature=signature,
            user_data=None,
            cross_validation_data=None,
            created_at=datetime.now().timestamp(),
            completed_at=None,
            retry_count=0
        )
        
        self.sessions[session_id] = session
        session.status = HandshakeStatus.PENDING
        
        return session
    
    def respond_to_handshake(
        self,
        session_id: str,
        responder_id: str,
        responder_data: Dict
    ) -> HandshakeSession:
        """
        Respond to a handshake request.
        
        Args:
            session_id: Handshake session ID
            responder_id: Responder user ID
            responder_data: Responder data
            
        Returns:
            HandshakeSession object
        """
        if session_id not in self.sessions:
            raise ValueError("Session not found")
        
        session = self.sessions[session_id]
        
        # Validate responder matches
        if session.responder_id != responder_id:
            session.status = HandshakeStatus.REJECTED
            return session
        
        # Create responder user data
        user_data = UserData(
            user_id=responder_id,
            protocol_version=responder_data.get('protocol_version', '1.0'),
            safety_compliance=responder_data.get('safety_compliance', False),
            handshake_signature=responder_data.get('handshake_signature', ''),
            validation_data=responder_data.get('validation_data', {}),
            timestamp=datetime.now().timestamp()
        )
        
        session.user_data = user_data
        session.status = HandshakeStatus.VALIDATING
        session.validation_status = ValidationStatus.VALIDATING
        
        return session
    
    def validate_cross_side_data(
        self,
        session_id: str,
        initiator_data: Dict,
        responder_data: Dict
    ) -> Tuple[ValidationStatus, Dict]:
        """
        Validate cross-side user data.
        
        Args:
            session_id: Handshake session ID
            initiator_data: Initiator data
            responder_data: Responder data
            
        Returns:
            Tuple of (ValidationStatus, validation_results)
        """
        if session_id not in self.sessions:
            return ValidationStatus.FAILED, {}
        
        session = self.sessions[session_id]
        
        validation_results = {
            'protocol_compatible': False,
            'safety_compliant': False,
            'signatures_valid': False,
            'data_integrity': False,
            'overall': False
        }
        
        # Check protocol compatibility
        protocol_compatible = self._check_protocol_compatibility(
            initiator_data.get('protocol_version'),
            responder_data.get('protocol_version')
        )
        validation_results['protocol_compatible'] = protocol_compatible
        
        # Check safety compliance
        safety_compliant = (
            initiator_data.get('safety_compliance', False) and
            responder_data.get('safety_compliance', False)
        )
        validation_results['safety_compliant'] = safety_compliant
        
        # Validate signatures
        signatures_valid = self._validate_signatures(
            initiator_data.get('handshake_signature'),
            responder_data.get('handshake_signature')
        )
        validation_results['signatures_valid'] = signatures_valid
        
        # Check data integrity
        data_integrity = self._check_data_integrity(
            initiator_data.get('validation_data', {}),
            responder_data.get('validation_data', {})
        )
        validation_results['data_integrity'] = data_integrity
        
        # Overall validation
        overall = all(validation_results.values())
        validation_results['overall'] = overall
        
        session.cross_validation_data = validation_results
        
        if overall:
            session.validation_status = ValidationStatus.PASSED
            session.status = HandshakeStatus.COMPLETED
            session.completed_at = datetime.now().timestamp()
        else:
            session.validation_status = ValidationStatus.FAILED
            session.status = HandshakeStatus.FAILED
        
        return session.validation_status, validation_results
    
    def complete_handshake(self, session_id: str) -> bool:
        """
        Complete a handshake after successful validation.
        
        Args:
            session_id: Handshake session ID
            
        Returns:
            True if completed successfully
        """
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        
        if session.validation_status != ValidationStatus.PASSED:
            return False
        
        session.status = HandshakeStatus.COMPLETED
        session.completed_at = datetime.now().timestamp()
        
        # Track completed handshakes
        if session.initiator_id not in self.completed_handshakes:
            self.completed_handshakes[session.initiator_id] = []
        self.completed_handshakes[session.initiator_id].append(session_id)
        
        if session.responder_id not in self.completed_handshakes:
            self.completed_handshakes[session.responder_id] = []
        self.completed_handshakes[session.responder_id].append(session_id)
        
        return True
    
    def reject_handshake(self, session_id: str, reason: str) -> bool:
        """
        Reject a handshake.
        
        Args:
            session_id: Handshake session ID
            reason: Rejection reason
            
        Returns:
            True if rejected successfully
        """
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        session.status = HandshakeStatus.REJECTED
        session.cross_validation_data = {'rejection_reason': reason}
        
        return True
    
    def retry_handshake(self, session_id: str) -> Optional[HandshakeSession]:
        """
        Retry a failed handshake.
        
        Args:
            session_id: Handshake session ID
            
        Returns:
            New HandshakeSession or None if max retries exceeded
        """
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        if session.retry_count >= self.config.max_retries:
            return None
        
        session.retry_count += 1
        session.status = HandshakeStatus.PENDING
        session.validation_status = ValidationStatus.PENDING
        
        return session
    
    def check_timeout(self, session_id: str) -> bool:
        """
        Check if a handshake has timed out.
        
        Args:
            session_id: Handshake session ID
            
        Returns:
            True if timed out
        """
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        
        elapsed = datetime.now().timestamp() - session.created_at
        
        if elapsed > self.config.handshake_timeout:
            session.status = HandshakeStatus.TIMEOUT
            return True
        
        return False
    
    def _create_signature(self, user_id: str) -> HandshakeSignature:
        """Create a handshake signature for a user."""
        timestamp = datetime.now().timestamp()
        data = f"{user_id}:{timestamp}:{self.config.version}"
        signature = hashlib.sha256(data.encode()).hexdigest()
        
        return HandshakeSignature(
            user_id=user_id,
            protocol_version=self.config.version,
            timestamp=timestamp,
            signature=signature,
            safety_compliance=True
        )
    
    def _check_protocol_compatibility(self, version1: str, version2: str) -> bool:
        """Check if protocol versions are compatible."""
        # Simple version check (major version must match)
        try:
            major1 = int(version1.split('.')[0])
            major2 = int(version2.split('.')[0])
            return major1 == major2
        except:
            return False
    
    def _validate_signatures(self, sig1: str, sig2: str) -> bool:
        """Validate handshake signatures."""
        # In real implementation, verify cryptographic signatures
        return bool(sig1) and bool(sig2) and len(sig1) == 64 and len(sig2) == 64
    
    def _check_data_integrity(self, data1: Dict, data2: Dict) -> bool:
        """Check data integrity."""
        # Check required fields
        required_fields = self.config.get_user_validation_config().get('required_fields', [])
        
        for field in required_fields:
            if field not in data1 or field not in data2:
                return False
        
        return True
    
    def get_handshake_status(self, session_id: str) -> Optional[HandshakeSession]:
        """Get handshake session status."""
        return self.sessions.get(session_id)
    
    def get_user_handshakes(self, user_id: str) -> List[HandshakeSession]:
        """Get all handshakes for a user."""
        user_sessions = []
        
        for session in self.sessions.values():
            if session.initiator_id == user_id or session.responder_id == user_id:
                user_sessions.append(session)
        
        return user_sessions
    
    def has_completed_handshake(self, user_id: str, other_user_id: str) -> bool:
        """Check if users have a completed handshake."""
        if user_id not in self.completed_handshakes:
            return False
        
        for session_id in self.completed_handshakes[user_id]:
            session = self.sessions.get(session_id)
            if session and (
                (session.initiator_id == user_id and session.responder_id == other_user_id) or
                (session.initiator_id == other_user_id and session.responder_id == user_id)
            ):
                return session.status == HandshakeStatus.COMPLETED
        
        return False
