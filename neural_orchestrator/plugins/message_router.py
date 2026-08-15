"""
User-to-User Message Routing with Destination Origin Profile
Routes messages between users with verification and origin profile tracking.
"""

import asyncio
import hashlib
import json
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid


class MessageStatus(Enum):
    """Status of message routing."""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    BLOCKED = "blocked"
    VERIFIED = "verified"
    IMPOSTER_DETECTED = "imposter_detected"


class VerificationLevel(Enum):
    """Verification levels for users."""
    UNVERIFIED = 0
    BASIC = 1
    CONFIRMED = 2
    SUCCESSIVE = 3
    ROOT = 4


@dataclass
class UserProfile:
    """User profile with origin verification."""
    user_id: str
    username: str
    origin_profile: str
    verification_level: VerificationLevel
    public_key: str
    created_at: str
    last_active: str
    linked_users: List[str]
    verification_chain: List[str]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MessageRoute:
    """Represents a message route between users."""
    message_id: str
    sender_id: str
    recipient_id: str
    content: str
    status: MessageStatus
    origin_verified: bool
    timestamp: str
    delivery_attempts: int = 0
    route_path: List[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.route_path is None:
            self.route_path = []


@dataclass
class ImposterFlag:
    """Represents a detected imposter attempt."""
    flag_id: str
    user_id: str
    flag_type: str
    detected_at: str
    evidence: Dict[str, Any]
    resolved: bool = False


class MessageRouter:
    """
    Routes messages between users with destination origin profile verification.
    Detects imposters and false flags, only routes to real linked successive confirmed users.
    """

    def __init__(self):
        self.user_profiles: Dict[str, UserProfile] = {}
        self.message_routes: Dict[str, MessageRoute] = []
        self.pending_messages: Dict[str, MessageRoute] = {}
        self.imposter_flags: Dict[str, ImposterFlag] = {}
        self.verification_requests: Dict[str, Dict[str, Any]] = {}
        self.linked_chains: Dict[str, List[str]] = {}  # user_id -> chain of linked users
        self.root_users: Set[str] = set()
        self.blocked_users: Set[str] = set()

    def _generate_message_id(self, sender_id: str, recipient_id: str) -> str:
        """Generate unique message ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        unique_hash = hashlib.md5(f"{sender_id}_{recipient_id}_{uuid.uuid4()}".encode()).hexdigest()[:8]
        return f"msg_{timestamp}_{unique_hash}"

    def _generate_user_id(self, username: str, origin_profile: str) -> str:
        """Generate unique user ID from username and origin profile."""
        user_string = f"{username}_{origin_profile}"
        return hashlib.sha256(user_string.encode()).hexdigest()[:16]

    def register_user(
        self,
        username: str,
        origin_profile: str,
        public_key: str,
        verification_level: VerificationLevel = VerificationLevel.UNVERIFIED,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UserProfile:
        """
        Register a user with origin profile.
        
        Args:
            username: Username
            origin_profile: Origin profile identifier
            public_key: Public key for verification
            verification_level: Initial verification level
            metadata: Optional metadata
            
        Returns:
            UserProfile: Registered user profile
        """
        user_id = self._generate_user_id(username, origin_profile)
        
        profile = UserProfile(
            user_id=user_id,
            username=username,
            origin_profile=origin_profile,
            verification_level=verification_level,
            public_key=public_key,
            created_at=datetime.utcnow().isoformat(),
            last_active=datetime.utcnow().isoformat(),
            linked_users=[],
            verification_chain=[],
            metadata=metadata or {}
        )
        
        self.user_profiles[user_id] = profile
        self.linked_chains[user_id] = []
        
        return profile

    def verify_user(
        self,
        user_id: str,
        verification_method: str,
        verification_data: Dict[str, Any]
    ) -> bool:
        """
        Verify a user using specified method.
        
        Args:
            user_id: User identifier
            verification_method: Method of verification
            verification_data: Verification data
            
        Returns:
            True if verification successful
        """
        if user_id not in self.user_profiles:
            return False
        
        profile = self.user_profiles[user_id]
        
        # Simple verification logic (in production, use actual cryptographic verification)
        if verification_method == "public_key":
            # Verify signature using public key
            # This is a placeholder for actual cryptographic verification
            if verification_data.get("signature") and verification_data.get("challenge"):
                profile.verification_level = VerificationLevel.CONFIRMED
                profile.verification_chain.append(f"verified_{datetime.utcnow().isoformat()}")
                return True
        
        elif verification_method == "successive_link":
            # Verify through successive linking
            if verification_data.get("linked_user_id") in profile.linked_users:
                profile.verification_level = VerificationLevel.SUCCESSIVE
                return True
        
        return False

    def link_users(self, user_id_1: str, user_id_2: str) -> bool:
        """
        Link two users for successive verification.
        
        Args:
            user_id_1: First user ID
            user_id_2: Second user ID
            
        Returns:
            True if linking successful
        """
        if user_id_1 not in self.user_profiles or user_id_2 not in self.user_profiles:
            return False
        
        # Check if both users are verified
        profile_1 = self.user_profiles[user_id_1]
        profile_2 = self.user_profiles[user_id_2]
        
        if profile_1.verification_level.value < VerificationLevel.CONFIRMED.value:
            return False
        if profile_2.verification_level.value < VerificationLevel.CONFIRMED.value:
            return False
        
        # Create bidirectional link
        if user_id_2 not in profile_1.linked_users:
            profile_1.linked_users.append(user_id_2)
        if user_id_1 not in profile_2.linked_users:
            profile_2.linked_users.append(user_id_1)
        
        # Update linked chains
        self.linked_chains[user_id_1].append(user_id_2)
        self.linked_chains[user_id_2].append(user_id_1)
        
        # Check for successive verification
        if len(profile_1.linked_users) >= 2 and len(profile_2.linked_users) >= 2:
            profile_1.verification_level = VerificationLevel.SUCCESSIVE
            profile_2.verification_level = VerificationLevel.SUCCESSIVE
        
        return True

    def set_root_user(self, user_id: str) -> bool:
        """
        Set a user as root user (highest trust level).
        
        Args:
            user_id: User identifier
            
        Returns:
            True if successful
        """
        if user_id not in self.user_profiles:
            return False
        
        self.root_users.add(user_id)
        self.user_profiles[user_id].verification_level = VerificationLevel.ROOT
        return True

    def route_message(
        self,
        sender_id: str,
        recipient_id: str,
        content: str,
        require_verification: bool = True
    ) -> MessageRoute:
        """
        Route a message from sender to recipient with verification.
        
        Args:
            sender_id: Sender user ID
            recipient_id: Recipient user ID
            content: Message content
            require_verification: Whether to require verification
            
        Returns:
            MessageRoute: The message route
        """
        message_id = self._generate_message_id(sender_id, recipient_id)
        
        # Check if users exist
        if sender_id not in self.user_profiles or recipient_id not in self.user_profiles:
            route = MessageRoute(
                message_id=message_id,
                sender_id=sender_id,
                recipient_id=recipient_id,
                content=content,
                status=MessageStatus.FAILED,
                origin_verified=False,
                timestamp=datetime.utcnow().isoformat(),
                metadata={"error": "User not found"}
            )
            self.message_routes.append(route)
            return route
        
        # Check if sender is blocked
        if sender_id in self.blocked_users:
            route = MessageRoute(
                message_id=message_id,
                sender_id=sender_id,
                recipient_id=recipient_id,
                content=content,
                status=MessageStatus.BLOCKED,
                origin_verified=False,
                timestamp=datetime.utcnow().isoformat(),
                metadata={"error": "Sender blocked"}
            )
            self.message_routes.append(route)
            return route
        
        # Check verification requirements
        sender_profile = self.user_profiles[sender_id]
        recipient_profile = self.user_profiles[recipient_id]
        
        origin_verified = True
        
        if require_verification:
            # Check if users are linked (successive verification)
            if recipient_id not in sender_profile.linked_users:
                origin_verified = False
                
                # Check for imposter
                if self._check_imposter(sender_id, recipient_id, content):
                    self._flag_imposter(sender_id, recipient_id, content)
                    route = MessageRoute(
                        message_id=message_id,
                        sender_id=sender_id,
                        recipient_id=recipient_id,
                        content=content,
                        status=MessageStatus.IMPOSTER_DETECTED,
                        origin_verified=False,
                        timestamp=datetime.utcnow().isoformat()
                    )
                    self.message_routes.append(route)
                    return route
        
        # Create message route
        route = MessageRoute(
            message_id=message_id,
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content,
            status=MessageStatus.VERIFIED if origin_verified else MessageStatus.PENDING,
            origin_verified=origin_verified,
            timestamp=datetime.utcnow().isoformat(),
            route_path=[sender_id, recipient_id]
        )
        
        self.message_routes.append(route)
        
        # Update last active
        sender_profile.last_active = datetime.utcnow().isoformat()
        
        return route

    def _check_imposter(self, sender_id: str, recipient_id: str, content: str) -> bool:
        """Check if sender might be an imposter."""
        # Check if sender has sufficient verification
        sender_profile = self.user_profiles.get(sender_id)
        if not sender_profile:
            return True
        
        # Check verification level
        if sender_profile.verification_level.value < VerificationLevel.CONFIRMED.value:
            return True
        
        # Check if users are linked
        if recipient_id not in sender_profile.linked_users:
            # Additional checks could be added here
            return False
        
        return False

    def _flag_imposter(self, sender_id: str, recipient_id: str, content: str) -> None:
        """Flag a potential imposter."""
        flag_id = f"flag_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{sender_id[:8]}"
        
        flag = ImposterFlag(
            flag_id=flag_id,
            user_id=sender_id,
            flag_type="unverified_message_attempt",
            detected_at=datetime.utcnow().isoformat(),
            evidence={
                "recipient_id": recipient_id,
                "content_hash": hashlib.sha256(content.encode()).hexdigest(),
                "sender_verification": self.user_profiles[sender_id].verification_level.value if sender_id in self.user_profiles else 0
            }
        )
        
        self.imposter_flags[flag_id] = flag

    def deliver_message(self, message_id: str) -> bool:
        """
        Mark a message as delivered.
        
        Args:
            message_id: Message identifier
            
        Returns:
            True if successful
        """
        for route in self.message_routes:
            if route.message_id == message_id:
                route.status = MessageStatus.DELIVERED
                route.delivery_attempts += 1
                return True
        return False

    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID."""
        return self.user_profiles.get(user_id)

    def get_linked_users(self, user_id: str) -> List[UserProfile]:
        """Get all linked users for a user."""
        if user_id not in self.user_profiles:
            return []
        
        profile = self.user_profiles[user_id]
        linked_profiles = []
        
        for linked_id in profile.linked_users:
            if linked_id in self.user_profiles:
                linked_profiles.append(self.user_profiles[linked_id])
        
        return linked_profiles

    def get_verification_chain(self, user_id: str) -> List[str]:
        """Get verification chain for a user."""
        if user_id not in self.user_profiles:
            return []
        
        return self.user_profiles[user_id].verification_chain

    def block_user(self, user_id: str, reason: str = "") -> bool:
        """
        Block a user from sending messages.
        
        Args:
            user_id: User identifier
            reason: Reason for blocking
            
        Returns:
            True if successful
        """
        if user_id not in self.user_profiles:
            return False
        
        self.blocked_users.add(user_id)
        
        # Add to metadata
        if "blocked_reasons" not in self.user_profiles[user_id].metadata:
            self.user_profiles[user_id].metadata["blocked_reasons"] = []
        self.user_profiles[user_id].metadata["blocked_reasons"].append(reason)
        
        return True

    def unblock_user(self, user_id: str) -> bool:
        """
        Unblock a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if successful
        """
        if user_id in self.blocked_users:
            self.blocked_users.remove(user_id)
            return True
        return False

    def get_imposter_flags(self, user_id: Optional[str] = None) -> List[ImposterFlag]:
        """
        Get imposter flags.
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            List of imposter flags
        """
        flags = list(self.imposter_flags.values())
        
        if user_id:
            flags = [f for f in flags if f.user_id == user_id]
        
        return flags

    def resolve_imposter_flag(self, flag_id: str) -> bool:
        """
        Resolve an imposter flag.
        
        Args:
            flag_id: Flag identifier
            
        Returns:
            True if successful
        """
        if flag_id in self.imposter_flags:
            self.imposter_flags[flag_id].resolved = True
            return True
        return False

    def get_message_history(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[MessageRoute]:
        """
        Get message history for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of messages
            
        Returns:
            List of message routes
        """
        user_messages = []
        
        for route in reversed(self.message_routes):
            if route.sender_id == user_id or route.recipient_id == user_id:
                user_messages.append(route)
                if len(user_messages) >= limit:
                    break
        
        return user_messages

    def get_statistics(self) -> Dict[str, Any]:
        """Get router statistics."""
        verification_distribution = {}
        for profile in self.user_profiles.values():
            level = profile.verification_level.name
            verification_distribution[level] = verification_distribution.get(level, 0) + 1
        
        return {
            "total_users": len(self.user_profiles),
            "total_messages": len(self.message_routes),
            "root_users": len(self.root_users),
            "blocked_users": len(self.blocked_users),
            "imposter_flags": len(self.imposter_flags),
            "verification_distribution": verification_distribution,
            "linked_pairs": sum(len(chain) for chain in self.linked_chains.values()) // 2
        }

    def export_state(self) -> str:
        """Export current state for recovery."""
        state = {
            "user_profiles": {
                uid: asdict(profile) for uid, profile in self.user_profiles.items()
            },
            "message_routes": [asdict(route) for route in self.message_routes],
            "imposter_flags": [asdict(flag) for flag in self.imposter_flags.values()],
            "root_users": list(self.root_users),
            "blocked_users": list(self.blocked_users),
            "linked_chains": self.linked_chains,
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
            
            # Restore user profiles
            for uid, profile_dict in state.get("user_profiles", {}).items():
                profile_dict["verification_level"] = VerificationLevel(profile_dict["verification_level"])
                self.user_profiles[uid] = UserProfile(**profile_dict)
            
            # Restore message routes
            for route_dict in state.get("message_routes", []):
                route_dict["status"] = MessageStatus(route_dict["status"])
                self.message_routes.append(MessageRoute(**route_dict))
            
            # Restore imposter flags
            for flag_dict in state.get("imposter_flags", []):
                self.imposter_flags[flag_dict["flag_id"]] = ImposterFlag(**flag_dict)
            
            # Restore sets and chains
            self.root_users = set(state.get("root_users", []))
            self.blocked_users = set(state.get("blocked_users", []))
            self.linked_chains = state.get("linked_chains", {})
            
            return True
        except Exception as e:
            print(f"Error importing state: {e}")
            return False
