"""
Device Permission Manager - Device Permission Management
Manages device permissions for image storage, broadband, and other device features.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class PermissionType(Enum):
    """Types of device permissions."""
    IMAGE_STORAGE = "image_storage"
    VIDEO_STORAGE = "video_storage"
    AUDIO_RECORDING = "audio_recording"
    CAMERA_ACCESS = "camera_access"
    MICROPHONE_ACCESS = "microphone_access"
    BROADBAND_ACCESS = "broadband_access"
    LOCATION_ACCESS = "location_access"
    CONTACTS_ACCESS = "contacts_access"
    NOTIFICATIONS = "notifications"
    FILE_ACCESS = "file_access"


class PermissionStatus(Enum):
    """Status of a permission."""
    GRANTED = "granted"
    DENIED = "denied"
    PENDING = "pending"
    REVOKED = "revoked"
    NEVER_ASK = "never_ask"


@dataclass
class Permission:
    """Represents a device permission."""
    permission_id: str
    permission_type: PermissionType
    status: PermissionStatus
    granted_at: Optional[float]
    revoked_at: Optional[float]
    expires_at: Optional[float]
    metadata: Dict[str, any]


@dataclass
class PermissionRequest:
    """Represents a permission request."""
    request_id: str
    permission_type: PermissionType
    requester: str
    reason: str
    timestamp: float
    status: PermissionStatus
    responded_at: Optional[float]


class DevicePermissionManager:
    """
    Manages device permissions for various features.
    Handles image storage, broadband access, and other device permissions.
    """
    
    def __init__(self):
        """Initialize the Device Permission Manager."""
        # Permission storage
        self.permissions: Dict[str, Permission] = {}  # key: permission_id
        
        # Permission requests
        self.permission_requests: Dict[str, PermissionRequest] = {}
        
        # User permissions
        self.user_permissions: Dict[str, Set[str]] = {}  # key: user_id, value: set of permission_ids
        
        # Permission groups
        self.permission_groups: Dict[str, List[PermissionType]] = {
            'media': [PermissionType.IMAGE_STORAGE, PermissionType.VIDEO_STORAGE, PermissionType.AUDIO_RECORDING],
            'camera': [PermissionType.CAMERA_ACCESS, PermissionType.MICROPHONE_ACCESS],
            'social': [PermissionType.CONTACTS_ACCESS, PermissionType.LOCATION_ACCESS],
            'network': [PermissionType.BROADBAND_ACCESS],
            'system': [PermissionType.NOTIFICATIONS, PermissionType.FILE_ACCESS]
        }
    
    def request_permission(
        self,
        user_id: str,
        permission_type: PermissionType,
        reason: str,
        expires_in_seconds: Optional[float] = None
    ) -> PermissionRequest:
        """
        Request a permission from the user.
        
        Args:
            user_id: User ID requesting permission
            permission_type: Type of permission
            reason: Reason for permission request
            expires_in_seconds: Optional expiration time
            
        Returns:
            PermissionRequest object
        """
        # Check if already granted
        existing_permission = self.get_user_permission(user_id, permission_type)
        if existing_permission and existing_permission.status == PermissionStatus.GRANTED:
            # Check if expired
            if existing_permission.expires_at and datetime.now().timestamp() > existing_permission.expires_at:
                self.revoke_permission(existing_permission.permission_id, user_id)
            else:
                # Already granted and valid
                return PermissionRequest(
                    request_id=f"req_existing_{datetime.now().timestamp()}",
                    permission_type=permission_type,
                    requester=user_id,
                    reason=reason,
                    timestamp=datetime.now().timestamp(),
                    status=PermissionStatus.GRANTED,
                    responded_at=datetime.now().timestamp()
                )
        
        # Create permission request
        request_id = f"req_{permission_type.value}_{user_id}_{datetime.now().timestamp()}"
        
        request = PermissionRequest(
            request_id=request_id,
            permission_type=permission_type,
            requester=user_id,
            reason=reason,
            timestamp=datetime.now().timestamp(),
            status=PermissionStatus.PENDING,
            responded_at=None
        )
        
        self.permission_requests[request_id] = request
        
        return request
    
    def grant_permission(
        self,
        request_id: str,
        user_id: str,
        expires_in_seconds: Optional[float] = None
    ) -> Optional[Permission]:
        """
        Grant a permission request.
        
        Args:
            request_id: Permission request ID
            user_id: User ID granting permission
            expires_in_seconds: Optional expiration time
            
        Returns:
            Permission object or None
        """
        if request_id not in self.permission_requests:
            return None
        
        request = self.permission_requests[request_id]
        
        # Calculate expiration
        expires_at = None
        if expires_in_seconds:
            expires_at = datetime.now().timestamp() + expires_in_seconds
        
        # Create permission
        permission_id = f"perm_{request.permission_type.value}_{user_id}_{datetime.now().timestamp()}"
        
        permission = Permission(
            permission_id=permission_id,
            permission_type=request.permission_type,
            status=PermissionStatus.GRANTED,
            granted_at=datetime.now().timestamp(),
            revoked_at=None,
            expires_at=expires_at,
            metadata={'request_id': request_id, 'reason': request.reason}
        )
        
        # Store permission
        self.permissions[permission_id] = permission
        
        # Track user permissions
        if user_id not in self.user_permissions:
            self.user_permissions[user_id] = set()
        self.user_permissions[user_id].add(permission_id)
        
        # Update request status
        request.status = PermissionStatus.GRANTED
        request.responded_at = datetime.now().timestamp()
        
        return permission
    
    def deny_permission(self, request_id: str, never_ask: bool = False) -> bool:
        """
        Deny a permission request.
        
        Args:
            request_id: Permission request ID
            never_ask: Whether to never ask again
            
        Returns:
            True if denied successfully
        """
        if request_id not in self.permission_requests:
            return False
        
        request = self.permission_requests[request_id]
        
        request.status = PermissionStatus.NEVER_ASK if never_ask else PermissionStatus.DENIED
        request.responded_at = datetime.now().timestamp()
        
        return True
    
    def revoke_permission(self, permission_id: str, user_id: str) -> bool:
        """
        Revoke a granted permission.
        
        Args:
            permission_id: Permission ID to revoke
            user_id: User ID revoking permission
            
        Returns:
            True if revoked successfully
        """
        if permission_id not in self.permissions:
            return False
        
        permission = self.permissions[permission_id]
        
        # Only user can revoke their own permissions
        if permission_id not in self.user_permissions.get(user_id, set()):
            return False
        
        permission.status = PermissionStatus.REVOKED
        permission.revoked_at = datetime.now().timestamp()
        
        # Remove from user permissions
        self.user_permissions[user_id].discard(permission_id)
        
        return True
    
    def get_user_permission(
        self,
        user_id: str,
        permission_type: PermissionType
    ) -> Optional[Permission]:
        """
        Get a specific permission for a user.
        
        Args:
            user_id: User ID
            permission_type: Permission type
            
        Returns:
            Permission object or None
        """
        if user_id not in self.user_permissions:
            return None
        
        for permission_id in self.user_permissions[user_id]:
            if permission_id in self.permissions:
                permission = self.permissions[permission_id]
                if permission.permission_type == permission_type:
                    # Check if expired
                    if permission.expires_at and datetime.now().timestamp() > permission.expires_at:
                        permission.status = PermissionStatus.REVOKED
                        return None
                    if permission.status == PermissionStatus.GRANTED:
                        return permission
        
        return None
    
    def get_user_permissions(self, user_id: str) -> List[Permission]:
        """
        Get all permissions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of Permission objects
        """
        if user_id not in self.user_permissions:
            return []
        
        permissions = []
        current_time = datetime.now().timestamp()
        
        for permission_id in self.user_permissions[user_id]:
            if permission_id in self.permissions:
                permission = self.permissions[permission_id]
                
                # Check expiration
                if permission.expires_at and current_time > permission.expires_at:
                    permission.status = PermissionStatus.REVOKED
                    continue
                
                if permission.status == PermissionStatus.GRANTED:
                    permissions.append(permission)
        
        return permissions
    
    def check_permission(
        self,
        user_id: str,
        permission_type: PermissionType
    ) -> bool:
        """
        Check if a user has a specific permission.
        
        Args:
            user_id: User ID
            permission_type: Permission type
            
        Returns:
            True if permission is granted
        """
        permission = self.get_user_permission(user_id, permission_type)
        return permission is not None and permission.status == PermissionStatus.GRANTED
    
    def grant_permission_group(
        self,
        user_id: str,
        group_name: str,
        expires_in_seconds: Optional[float] = None
    ) -> List[Permission]:
        """
        Grant all permissions in a group.
        
        Args:
            user_id: User ID
            group_name: Name of permission group
            expires_in_seconds: Optional expiration time
            
        Returns:
            List of granted Permission objects
        """
        if group_name not in self.permission_groups:
            return []
        
        granted_permissions = []
        
        for permission_type in self.permission_groups[group_name]:
            # Request and grant
            request = self.request_permission(user_id, permission_type, f"Group grant: {group_name}")
            permission = self.grant_permission(request.request_id, user_id, expires_in_seconds)
            if permission:
                granted_permissions.append(permission)
        
        return granted_permissions
    
    def get_permission_statistics(self, user_id: Optional[str] = None) -> Dict[str, any]:
        """
        Get statistics about permissions.
        
        Args:
            user_id: Optional user ID to limit statistics
            
        Returns:
            Dictionary containing permission statistics
        """
        if user_id:
            user_permissions = self.get_user_permissions(user_id)
            permission_ids = self.user_permissions.get(user_id, set())
        else:
            user_permissions = list(self.permissions.values())
            permission_ids = set(self.permissions.keys())
        
        status_counts = {}
        type_counts = {}
        
        for permission in user_permissions:
            status = permission.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            
            perm_type = permission.permission_type.value
            type_counts[perm_type] = type_counts.get(perm_type, 0) + 1
        
        return {
            'total_permissions': len(permission_ids),
            'status_distribution': status_counts,
            'type_distribution': type_counts,
            'pending_requests': len([r for r in self.permission_requests.values() if r.status == PermissionStatus.PENDING])
        }
    
    def cleanup_expired_permissions(self):
        """Clean up expired permissions."""
        current_time = datetime.now().timestamp()
        
        expired_permission_ids = [
            perm_id for perm_id, perm in self.permissions.items()
            if perm.expires_at and current_time > perm.expires_at
        ]
        
        for perm_id in expired_permission_ids:
            self.permissions[perm_id].status = PermissionStatus.REVOKED
            
            # Remove from user permissions
            for user_id, perm_set in self.user_permissions.items():
                perm_set.discard(perm_id)
    
    def get_pending_requests(self, user_id: Optional[str] = None) -> List[PermissionRequest]:
        """
        Get pending permission requests.
        
        Args:
            user_id: Optional user ID to filter requests
            
        Returns:
            List of PermissionRequest objects
        """
        pending_requests = [
            req for req in self.permission_requests.values()
            if req.status == PermissionStatus.PENDING
        ]
        
        if user_id:
            pending_requests = [req for req in pending_requests if req.requester == user_id]
        
        return pending_requests
