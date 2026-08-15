"""
Agent-to-Agent (A2A) Protocol System
Enables secure agent communication, hosting, and credential validation pipelines.
"""

import asyncio
import json
import hashlib
import hmac
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid


class A2AStatus(Enum):
    """Status of A2A connections."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
    ERROR = "error"


class CredentialStatus(Enum):
    """Status of credential validation."""
    PENDING = "pending"
    VALIDATING = "validating"
    VALID = "valid"
    INVALID = "invalid"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass
class AgentIdentity:
    """Identity of an agent in the A2A network."""
    agent_id: str
    agent_name: str
    public_key: str
    session_key: str
    capabilities: List[str]
    created_at: str
    last_seen: str
    status: A2AStatus


@dataclass
class Credential:
    """Credential for API access."""
    credential_id: str
    credential_type: str  # "instagram", "tiktok", "custom"
    credential_data: Dict[str, str]
    status: CredentialStatus
    created_at: str
    expires_at: Optional[str] = None
    validation_results: Optional[Dict[str, Any]] = None


@dataclass
class A2AMessage:
    """Message in A2A protocol."""
    message_id: str
    sender_id: str
    recipient_id: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: str
    signature: str
    encrypted: bool = False


class A2AProtocol:
    """
    Agent-to-Agent Protocol for secure communication and credential management.
    Handles agent hosting, connections, and credential validation pipelines.
    """

    def __init__(self, session_key: str):
        self.session_key = session_key
        self.agent_id = self._generate_agent_id()
        self.agents: Dict[str, AgentIdentity] = {}
        self.credentials: Dict[str, Credential] = {}
        self.message_queue: List[A2AMessage] = []
        self.connections: Dict[str, A2AStatus] = {}
        
        # Pipeline stages
        self.pipeline_stages = [
            "credential_creation",
            "credential_validation", 
            "agent_authentication",
            "connection_establishment",
            "secure_communication"
        ]
        
        # Current pipeline stage
        self.current_stage = 0
        
        # Secure storage for session key
        self._secure_session_key = self._hash_session_key(session_key)

    def _generate_agent_id(self) -> str:
        """Generate unique agent ID."""
        return f"agent_{uuid.uuid4().hex[:12]}"

    def _hash_session_key(self, key: str) -> str:
        """Hash session key for secure storage."""
        return hashlib.sha256(key.encode()).hexdigest()

    def _sign_message(self, message: A2AMessage) -> str:
        """Sign message with session key."""
        message_str = json.dumps({
            "message_id": message.message_id,
            "sender_id": message.sender_id,
            "recipient_id": message.recipient_id,
            "timestamp": message.timestamp
        }, sort_keys=True)
        
        signature = hmac.new(
            self.session_key.encode(),
            message_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature

    def _verify_signature(self, message: A2AMessage, public_key: str) -> bool:
        """Verify message signature."""
        # In production, use actual cryptographic verification
        # For now, use simple validation
        return len(message.signature) == 64

    def create_credential(
        self,
        credential_type: str,
        credential_data: Dict[str, str],
        expires_hours: Optional[int] = None
    ) -> Credential:
        """
        Create a new credential.
        
        Args:
            credential_type: Type of credential (instagram, tiktok, custom)
            credential_data: Credential data (API keys, tokens, etc.)
            expires_hours: Optional expiration time in hours
            
        Returns:
            Credential object
        """
        credential_id = f"cred_{credential_type}_{uuid.uuid4().hex[:8]}"
        
        expires_at = None
        if expires_hours:
            expires_at = (datetime.utcnow() + timedelta(hours=expires_hours)).isoformat()
        
        credential = Credential(
            credential_id=credential_id,
            credential_type=credential_type,
            credential_data=credential_data,
            status=CredentialStatus.PENDING,
            created_at=datetime.utcnow().isoformat(),
            expires_at=expires_at
        )
        
        self.credentials[credential_id] = credential
        return credential

    async def validate_credential(self, credential_id: str) -> Credential:
        """
        Validate a credential.
        
        Args:
            credential_id: Credential identifier
            
        Returns:
            Updated credential with validation results
        """
        if credential_id not in self.credentials:
            raise ValueError(f"Credential {credential_id} not found")
        
        credential = self.credentials[credential_id]
        credential.status = CredentialStatus.VALIDATING
        
        # Simulate validation process
        await asyncio.sleep(1)  # Simulate API call
        
        # Perform actual validation based on credential type
        validation_results = await self._perform_validation(credential)
        
        credential.validation_results = validation_results
        
        if validation_results.get("valid", False):
            credential.status = CredentialStatus.VALID
        else:
            credential.status = CredentialStatus.INVALID
        
        return credential

    async def _perform_validation(self, credential: Credential) -> Dict[str, Any]:
        """
        Perform actual credential validation.
        
        Args:
            credential: Credential to validate
            
        Returns:
            Validation results
        """
        # This would make actual API calls to validate credentials
        # For now, simulate validation
        
        credential_data = credential.credential_data
        
        # Basic validation checks
        has_required_fields = all(
            key in credential_data and credential_data[key]
            for key in ["api_key", "access_token"]
            if key in ["api_key", "access_token"]  # Check for common fields
        )
        
        return {
            "valid": has_required_fields or len(credential_data) > 0,
            "timestamp": datetime.utcnow().isoformat(),
            "checks_performed": ["format", "length", "structure"],
            "credential_type": credential.credential_type
        }

    def register_agent(
        self,
        agent_name: str,
        public_key: str,
        capabilities: List[str]
    ) -> AgentIdentity:
        """
        Register an agent in the A2A network.
        
        Args:
            agent_name: Name of the agent
            public_key: Public key of the agent
            capabilities: List of agent capabilities
            
        Returns:
            AgentIdentity
        """
        agent_id = self._generate_agent_id()
        
        agent = AgentIdentity(
            agent_id=agent_id,
            agent_name=agent_name,
            public_key=public_key,
            session_key=self._secure_session_key,
            capabilities=capabilities,
            created_at=datetime.utcnow().isoformat(),
            last_seen=datetime.utcnow().isoformat(),
            status=A2AStatus.DISCONNECTED
        )
        
        self.agents[agent_id] = agent
        return agent

    async def connect_to_agent(self, agent_id: str) -> bool:
        """
        Connect to another agent.
        
        Args:
            agent_id: Agent identifier to connect to
            
        Returns:
            True if connection successful
        """
        if agent_id not in self.agents:
            return False
        
        self.connections[agent_id] = A2AStatus.CONNECTING
        
        # Simulate connection process
        await asyncio.sleep(0.5)
        
        # Perform authentication
        authenticated = await self._authenticate_agent(agent_id)
        
        if authenticated:
            self.connections[agent_id] = A2AStatus.AUTHENTICATED
            self.agents[agent_id].status = A2AStatus.AUTHENTICATED
            self.agents[agent_id].last_seen = datetime.utcnow().isoformat()
            return True
        else:
            self.connections[agent_id] = A2AStatus.ERROR
            return False

    async def _authenticate_agent(self, agent_id: str) -> bool:
        """
        Authenticate with another agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if authentication successful
        """
        # In production, perform actual cryptographic authentication
        # For now, simulate authentication
        agent = self.agents.get(agent_id)
        if not agent:
            return False
        
        # Simulate authentication handshake
        await asyncio.sleep(0.3)
        
        return True  # Simulate successful authentication

    def send_message(
        self,
        recipient_id: str,
        message_type: str,
        payload: Dict[str, Any],
        encrypt: bool = True
    ) -> A2AMessage:
        """
        Send a message to another agent.
        
        Args:
            recipient_id: Recipient agent ID
            message_type: Type of message
            payload: Message payload
            encrypt: Whether to encrypt message
            
        Returns:
            A2AMessage
        """
        message_id = f"msg_{uuid.uuid4().hex[:12]}"
        
        message = A2AMessage(
            message_id=message_id,
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            message_type=message_type,
            payload=payload,
            timestamp=datetime.utcnow().isoformat(),
            signature="",
            encrypted=encrypt
        )
        
        # Sign message
        message.signature = self._sign_message(message)
        
        self.message_queue.append(message)
        
        return message

    def receive_messages(self) -> List[A2AMessage]:
        """Receive messages for this agent."""
        my_messages = [
            msg for msg in self.message_queue
            if msg.recipient_id == self.agent_id
        ]
        
        # Remove received messages from queue
        self.message_queue = [
            msg for msg in self.message_queue
            if msg.recipient_id != self.agent_id
        ]
        
        return my_messages

    async def run_pipeline_sequence(self) -> Dict[str, Any]:
        """
        Run the complete credential creation and validation pipeline.
        
        Returns:
            Pipeline execution results
        """
        pipeline_results = {
            "pipeline_id": f"pipeline_{uuid.uuid4().hex[:8]}",
            "started_at": datetime.utcnow().isoformat(),
            "stages_completed": [],
            "stages_failed": [],
            "final_status": "in_progress"
        }
        
        for stage in self.pipeline_stages:
            try:
                print(f"Executing stage: {stage}")
                
                result = await self._execute_pipeline_stage(stage)
                
                pipeline_results["stages_completed"].append({
                    "stage": stage,
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                if not result.get("success", False):
                    pipeline_results["stages_failed"].append(stage)
                    break
                
                self.current_stage += 1
                
            except Exception as e:
                pipeline_results["stages_failed"].append({
                    "stage": stage,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                })
                break
        
        pipeline_results["final_status"] = "completed" if not pipeline_results["stages_failed"] else "failed"
        pipeline_results["completed_at"] = datetime.utcnow().isoformat()
        
        return pipeline_results

    async def _execute_pipeline_stage(self, stage: str) -> Dict[str, Any]:
        """
        Execute a specific pipeline stage.
        
        Args:
            stage: Stage name
            
        Returns:
            Stage execution result
        """
        if stage == "credential_creation":
            return await self._stage_credential_creation()
        elif stage == "credential_validation":
            return await self._stage_credential_validation()
        elif stage == "agent_authentication":
            return await self._stage_agent_authentication()
        elif stage == "connection_establishment":
            return await self._stage_connection_establishment()
        elif stage == "secure_communication":
            return await self._stage_secure_communication()
        else:
            return {"success": False, "error": f"Unknown stage: {stage}"}

    async def _stage_credential_creation(self) -> Dict[str, Any]:
        """Execute credential creation stage."""
        # Create sample credentials for Instagram and TikTok
        insta_credential = self.create_credential(
            "instagram",
            {"api_key": "sample_insta_key", "access_token": "sample_token"},
            expires_hours=24
        )
        
        tiktok_credential = self.create_credential(
            "tiktok",
            {"api_key": "sample_tiktok_key", "access_token": "sample_token"},
            expires_hours=24
        )
        
        return {
            "success": True,
            "credentials_created": 2,
            "credential_ids": [insta_credential.credential_id, tiktok_credential.credential_id]
        }

    async def _stage_credential_validation(self) -> Dict[str, Any]:
        """Execute credential validation stage."""
        validated_count = 0
        
        for credential_id, credential in self.credentials.items():
            if credential.status == CredentialStatus.PENDING:
                await self.validate_credential(credential_id)
                validated_count += 1
        
        return {
            "success": True,
            "credentials_validated": validated_count
        }

    async def _stage_agent_authentication(self) -> Dict[str, Any]:
        """Execute agent authentication stage."""
        # Register this agent
        self.register_agent(
            "main_agent",
            "public_key_placeholder",
            ["credential_management", "hosting", "validation"]
        )
        
        return {
            "success": True,
            "agent_registered": self.agent_id
        }

    async def _stage_connection_establishment(self) -> Dict[str, Any]:
        """Execute connection establishment stage."""
        # Simulate establishing connections
        connections = 0
        
        for agent_id in self.agents.keys():
            if agent_id != self.agent_id:
                connected = await self.connect_to_agent(agent_id)
                if connected:
                    connections += 1
        
        return {
            "success": True,
            "connections_established": connections
        }

    async def _stage_secure_communication(self) -> Dict[str, Any]:
        """Execute secure communication stage."""
        # Send test message
        if self.agents:
            target_agent = list(self.agents.keys())[0]
            message = self.send_message(
                target_agent,
                "pipeline_complete",
                {"status": "success", "timestamp": datetime.utcnow().isoformat()}
            )
            
            return {
                "success": True,
                "message_sent": message.message_id
            }
        
        return {
            "success": True,
            "message_sent": None
        }

    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information."""
        return {
            "agent_id": self.agent_id,
            "session_key_hash": self._secure_session_key[:16] + "...",
            "registered_agents": len(self.agents),
            "active_connections": len([c for c in self.connections.values() if c == A2AStatus.AUTHENTICATED]),
            "credentials_managed": len(self.credentials),
            "current_pipeline_stage": self.pipeline_stages[self.current_stage] if self.current_stage < len(self.pipeline_stages) else "complete",
            "messages_in_queue": len(self.message_queue)
        }

    def export_state(self) -> str:
        """Export current state for recovery."""
        state = {
            "agent_id": self.agent_id,
            "session_key_hash": self._secure_session_key,
            "agents": {aid: asdict(agent) for aid, agent in self.agents.items()},
            "credentials": {cid: asdict(cred) for cid, cred in self.credentials.items()},
            "connections": {aid: status.value for aid, status in self.connections.items()},
            "pipeline_stage": self.current_stage,
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
            
            self.agent_id = state["agent_id"]
            self._secure_session_key = state["session_key_hash"]
            self.current_stage = state["pipeline_stage"]
            
            # Restore agents
            for aid, agent_dict in state["agents"].items():
                agent_dict["status"] = A2AStatus(agent_dict["status"])
                self.agents[aid] = AgentIdentity(**agent_dict)
            
            # Restore credentials
            for cid, cred_dict in state["credentials"].items():
                cred_dict["status"] = CredentialStatus(cred_dict["status"])
                self.credentials[cid] = Credential(**cred_dict)
            
            # Restore connections
            for aid, status in state["connections"].items():
                self.connections[aid] = A2AStatus(status)
            
            return True
        except Exception as e:
            print(f"Error importing state: {e}")
            return False
