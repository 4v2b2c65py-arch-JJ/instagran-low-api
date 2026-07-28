"""
SHA Sharing System - SHA-based Information Sharing
Uses SHA hashes to send and store information across points in time to other users.
"""

import hashlib
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ShareStatus(Enum):
    """Status of shared information."""
    PENDING = "pending"
    SHARED = "shared"
    RECEIVED = "received"
    EXPIRED = "expired"
    REVOKED = "revoked"


class SharePermission(Enum):
    """Permission levels for shared information."""
    PUBLIC = "public"
    CONTACTS_ONLY = "contacts_only"
    SPECIFIC_USERS = "specific_users"
    PRIVATE = "private"


@dataclass
class SharedItem:
    """Represents a shared information item."""
    share_id: str
    sha256: str
    sender_id: str
    recipient_ids: List[str]
    content_type: str
    content: Union[bytes, str, Dict]
    metadata: Dict[str, any]
    status: ShareStatus
    permission: SharePermission
    created_at: float
    expires_at: Optional[float]
    access_count: int
    last_accessed: Optional[float]


@dataclass
class ShareTransaction:
    """Represents a share transaction across time."""
    transaction_id: str
    share_id: str
    from_user: str
    to_user: str
    timestamp: float
    points_in_time: List[float]
    success: bool


class SHASharingSystem:
    """
    SHA-based information sharing system.
    Uses SHA hashes to send and store information across points in time.
    """
    
    def __init__(self):
        """Initialize the SHA Sharing System."""
        # Shared items storage
        self.shared_items: Dict[str, SharedItem] = {}  # key: share_id
        self.items_by_sha: Dict[str, List[str]] = {}  # key: sha256, value: list of share_ids
        
        # Transaction tracking
        self.transactions: Dict[str, ShareTransaction] = {}
        
        # User shares
        self.user_shares: Dict[str, List[str]] = {}  # key: user_id, value: list of share_ids
        self.user_received: Dict[str, List[str]] = {}  # key: user_id, value: list of share_ids
        
        # Time points tracking
        self.time_points: Dict[str, List[float]] = {}  # key: share_id, value: list of timestamps
        
        # Default expiration (24 hours)
        self.default_expiration_seconds = 86400
    
    def share_information(
        self,
        sender_id: str,
        recipient_ids: List[str],
        content: Union[bytes, str, Dict],
        content_type: str,
        permission: SharePermission = SharePermission.CONTACTS_ONLY,
        metadata: Optional[Dict] = None,
        expires_in_seconds: Optional[float] = None
    ) -> SharedItem:
        """
        Share information using SHA-based system.
        
        Args:
            sender_id: Sender user ID
            recipient_ids: List of recipient user IDs
            content: Content to share
            content_type: Type of content (image, video, text, etc.)
            permission: Share permission level
            metadata: Additional metadata
            expires_in_seconds: Expiration time in seconds
            
        Returns:
            SharedItem object
        """
        # Calculate SHA256
        sha256 = self._calculate_sha256(content)
        
        # Generate share ID
        share_id = f"share_{sha256[:8]}_{datetime.now().timestamp()}"
        
        # Calculate expiration
        expires_at = None
        if expires_in_seconds:
            expires_at = datetime.now().timestamp() + expires_in_seconds
        else:
            expires_at = datetime.now().timestamp() + self.default_expiration_seconds
        
        # Create shared item
        shared_item = SharedItem(
            share_id=share_id,
            sha256=sha256,
            sender_id=sender_id,
            recipient_ids=recipient_ids,
            content_type=content_type,
            content=content,
            metadata=metadata or {},
            status=ShareStatus.PENDING,
            permission=permission,
            created_at=datetime.now().timestamp(),
            expires_at=expires_at,
            access_count=0,
            last_accessed=None
        )
        
        # Store shared item
        self.shared_items[share_id] = shared_item
        
        # Index by SHA
        if sha256 not in self.items_by_sha:
            self.items_by_sha[sha256] = []
        self.items_by_sha[sha256].append(share_id)
        
        # Track user shares
        if sender_id not in self.user_shares:
            self.user_shares[sender_id] = []
        self.user_shares[sender_id].append(share_id)
        
        # Track recipients
        for recipient_id in recipient_ids:
            if recipient_id not in self.user_received:
                self.user_received[recipient_id] = []
            self.user_received[recipient_id].append(share_id)
        
        # Initialize time points
        self.time_points[share_id] = [datetime.now().timestamp()]
        
        # Create transactions for each recipient
        for recipient_id in recipient_ids:
            transaction_id = f"txn_{share_id}_{recipient_id}"
            transaction = ShareTransaction(
                transaction_id=transaction_id,
                share_id=share_id,
                from_user=sender_id,
                to_user=recipient_id,
                timestamp=datetime.now().timestamp(),
                points_in_time=[datetime.now().timestamp()],
                success=True
            )
            self.transactions[transaction_id] = transaction
        
        # Update status
        shared_item.status = ShareStatus.SHARED
        
        return shared_item
    
    def receive_information(
        self,
        user_id: str,
        share_id: str
    ) -> Optional[SharedItem]:
        """
        Receive shared information.
        
        Args:
            user_id: Recipient user ID
            share_id: Share ID to receive
            
        Returns:
            SharedItem or None if not found or not authorized
        """
        if share_id not in self.shared_items:
            return None
        
        shared_item = self.shared_items[share_id]
        
        # Check if user is authorized recipient
        if user_id not in shared_item.recipient_ids:
            return None
        
        # Check if expired
        if shared_item.expires_at and datetime.now().timestamp() > shared_item.expires_at:
            shared_item.status = ShareStatus.EXPIRED
            return None
        
        # Check permission
        if shared_item.permission == SharePermission.PRIVATE:
            return None
        
        # Update access tracking
        shared_item.access_count += 1
        shared_item.last_accessed = datetime.now().timestamp()
        shared_item.status = ShareStatus.RECEIVED
        
        # Add time point
        self.time_points[share_id].append(datetime.now().timestamp())
        
        return shared_item
    
    def get_by_sha(self, sha256: str, user_id: str) -> List[SharedItem]:
        """
        Get shared items by SHA hash.
        
        Args:
            sha256: SHA256 hash
            user_id: Requesting user ID
            
        Returns:
            List of SharedItem objects
        """
        share_ids = self.items_by_sha.get(sha256, [])
        
        accessible_items = []
        for share_id in share_ids:
            if share_id in self.shared_items:
                item = self.shared_items[share_id]
                
                # Check if user is authorized
                if user_id in item.recipient_ids or item.sender_id == user_id:
                    accessible_items.append(item)
        
        return accessible_items
    
    def revoke_share(self, share_id: str, user_id: str) -> bool:
        """
        Revoke a shared item.
        
        Args:
            share_id: Share ID to revoke
            user_id: User requesting revocation (must be sender)
            
        Returns:
            True if revoked successfully
        """
        if share_id not in self.shared_items:
            return False
        
        shared_item = self.shared_items[share_id]
        
        # Only sender can revoke
        if shared_item.sender_id != user_id:
            return False
        
        shared_item.status = ShareStatus.REVOKED
        return True
    
    def get_user_shares(self, user_id: str) -> List[SharedItem]:
        """
        Get all shares sent by a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of SharedItem objects
        """
        share_ids = self.user_shares.get(user_id, [])
        return [self.shared_items[sid] for sid in share_ids if sid in self.shared_items]
    
    def get_user_received(self, user_id: str) -> List[SharedItem]:
        """
        Get all shares received by a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of SharedItem objects
        """
        share_ids = self.user_received.get(user_id, [])
        return [self.shared_items[sid] for sid in share_ids if sid in self.shared_items]
    
    def get_time_points(self, share_id: str) -> List[float]:
        """
        Get time points for a share.
        
        Args:
            share_id: Share ID
            
        Returns:
            List of timestamps
        """
        return self.time_points.get(share_id, [])
    
    def add_time_point(self, share_id: str, timestamp: Optional[float] = None):
        """
        Add a time point to a share.
        
        Args:
            share_id: Share ID
            timestamp: Timestamp (default: current time)
        """
        if share_id not in self.time_points:
            self.time_points[share_id] = []
        
        if timestamp is None:
            timestamp = datetime.now().timestamp()
        
        self.time_points[share_id].append(timestamp)
    
    def get_share_statistics(self) -> Dict[str, any]:
        """
        Get statistics about sharing.
        
        Returns:
            Dictionary containing sharing statistics
        """
        total_shares = len(self.shared_items)
        active_shares = sum(1 for item in self.shared_items.values() if item.status == ShareStatus.SHARED)
        expired_shares = sum(1 for item in self.shared_items.values() if item.status == ShareStatus.EXPIRED)
        revoked_shares = sum(1 for item in self.shared_items.values() if item.status == ShareStatus.REVOKED)
        
        content_type_counts = {}
        for item in self.shared_items.values():
            content_type_counts[item.content_type] = content_type_counts.get(item.content_type, 0) + 1
        
        return {
            'total_shares': total_shares,
            'active_shares': active_shares,
            'expired_shares': expired_shares,
            'revoked_shares': revoked_shares,
            'total_transactions': len(self.transactions),
            'content_type_distribution': content_type_counts,
            'unique_users': len(set(self.user_shares.keys()) | set(self.user_received.keys()))
        }
    
    def cleanup_expired(self):
        """Clean up expired shares."""
        current_time = datetime.now().timestamp()
        
        expired_share_ids = [
            share_id for share_id, item in self.shared_items.items()
            if item.expires_at and current_time > item.expires_at
        ]
        
        for share_id in expired_share_ids:
            self.shared_items[share_id].status = ShareStatus.EXPIRED
    
    def _calculate_sha256(self, content: Union[bytes, str, Dict]) -> str:
        """
        Calculate SHA256 hash of content.
        
        Args:
            content: Content to hash
            
        Returns:
            SHA256 hash string
        """
        if isinstance(content, str):
            data = content.encode()
        elif isinstance(content, dict):
            import json
            data = json.dumps(content).encode()
        else:
            data = content
        
        return hashlib.sha256(data).hexdigest()
