"""
Chat Conversation Manager - Direct Chat Conversation Support
Manages direct chat conversations with message history and media support.
"""

import hashlib
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class MessageStatus(Enum):
    """Status of a message."""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class MessageType(Enum):
    """Types of messages."""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    STICKER = "sticker"
    FILE = "file"
    LOCATION = "location"
    CONTACT = "contact"


@dataclass
class ChatMessage:
    """Represents a chat message."""
    message_id: str
    conversation_id: str
    sender_id: str
    recipient_id: str
    message_type: MessageType
    content: Union[str, bytes, Dict]
    metadata: Dict[str, any]
    sha256: str
    status: MessageStatus
    timestamp: float
    read_at: Optional[float]
    delivered_at: Optional[float]


@dataclass
class Conversation:
    """Represents a chat conversation."""
    conversation_id: str
    participants: List[str]
    created_at: float
    last_activity: float
    message_count: int
    unread_count: int
    metadata: Dict[str, any]


class ChatConversationManager:
    """
    Manages direct chat conversations.
    Supports text, images, videos, audio, stickers, and file sharing.
    """
    
    def __init__(self):
        """Initialize the Chat Conversation Manager."""
        # Conversations storage
        self.conversations: Dict[str, Conversation] = {}
        
        # Messages storage
        self.messages: Dict[str, ChatMessage] = {}  # key: message_id
        self.messages_by_conversation: Dict[str, List[str]] = {}  # key: conversation_id
        
        # User conversations
        self.user_conversations: Dict[str, List[str]] = {}  # key: user_id
        
        # Message tracking
        self.message_counter = 0
    
    def create_conversation(
        self,
        participant_ids: List[str],
        metadata: Optional[Dict] = None
    ) -> Conversation:
        """
        Create a new conversation.
        
        Args:
            participant_ids: List of participant user IDs
            metadata: Additional metadata
            
        Returns:
            Conversation object
        """
        # Generate conversation ID
        participant_ids_sorted = sorted(participant_ids)
        conversation_id = f"conv_{'_'.join(participant_ids_sorted)}"
        
        # Check if conversation already exists
        if conversation_id in self.conversations:
            return self.conversations[conversation_id]
        
        # Create conversation
        conversation = Conversation(
            conversation_id=conversation_id,
            participants=participant_ids,
            created_at=datetime.now().timestamp(),
            last_activity=datetime.now().timestamp(),
            message_count=0,
            unread_count=0,
            metadata=metadata or {}
        )
        
        # Store conversation
        self.conversations[conversation_id] = conversation
        self.messages_by_conversation[conversation_id] = []
        
        # Track user conversations
        for user_id in participant_ids:
            if user_id not in self.user_conversations:
                self.user_conversations[user_id] = []
            self.user_conversations[user_id].append(conversation_id)
        
        return conversation
    
    def send_message(
        self,
        conversation_id: str,
        sender_id: str,
        recipient_id: str,
        message_type: MessageType,
        content: Union[str, bytes, Dict],
        metadata: Optional[Dict] = None
    ) -> ChatMessage:
        """
        Send a message in a conversation.
        
        Args:
            conversation_id: Conversation ID
            sender_id: Sender user ID
            recipient_id: Recipient user ID
            message_type: Type of message
            content: Message content
            metadata: Additional metadata
            
        Returns:
            ChatMessage object
        """
        # Calculate SHA256
        sha256 = self._calculate_sha256(content)
        
        # Generate message ID
        self.message_counter += 1
        message_id = f"msg_{self.message_counter}_{datetime.now().timestamp()}"
        
        # Create message
        message = ChatMessage(
            message_id=message_id,
            conversation_id=conversation_id,
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_type=message_type,
            content=content,
            metadata=metadata or {},
            sha256=sha256,
            status=MessageStatus.SENT,
            timestamp=datetime.now().timestamp(),
            read_at=None,
            delivered_at=None
        )
        
        # Store message
        self.messages[message_id] = message
        self.messages_by_conversation[conversation_id].append(message_id)
        
        # Update conversation
        if conversation_id in self.conversations:
            conversation = self.conversations[conversation_id]
            conversation.last_activity = datetime.now().timestamp()
            conversation.message_count += 1
            conversation.unread_count += 1
        
        return message
    
    def mark_as_delivered(self, message_id: str) -> bool:
        """
        Mark a message as delivered.
        
        Args:
            message_id: Message ID
            
        Returns:
            True if marked successfully
        """
        if message_id not in self.messages:
            return False
        
        message = self.messages[message_id]
        message.status = MessageStatus.DELIVERED
        message.delivered_at = datetime.now().timestamp()
        
        return True
    
    def mark_as_read(self, message_id: str, user_id: str) -> bool:
        """
        Mark a message as read.
        
        Args:
            message_id: Message ID
            user_id: User ID marking as read
            
        Returns:
            True if marked successfully
        """
        if message_id not in self.messages:
            return False
        
        message = self.messages[message_id]
        
        # Only recipient can mark as read
        if message.recipient_id != user_id:
            return False
        
        message.status = MessageStatus.READ
        message.read_at = datetime.now().timestamp()
        
        # Update conversation unread count
        if message.conversation_id in self.conversations:
            conversation = self.conversations[message.conversation_id]
            conversation.unread_count = max(0, conversation.unread_count - 1)
        
        return True
    
    def get_conversation_messages(
        self,
        conversation_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[ChatMessage]:
        """
        Get messages from a conversation.
        
        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages
            offset: Offset for pagination
            
        Returns:
            List of ChatMessage objects
        """
        message_ids = self.messages_by_conversation.get(conversation_id, [])
        
        if offset > 0:
            message_ids = message_ids[offset:]
        
        if limit:
            message_ids = message_ids[:limit]
        
        return [self.messages[mid] for mid in message_ids if mid in self.messages]
    
    def get_user_conversations(self, user_id: str) -> List[Conversation]:
        """
        Get all conversations for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of Conversation objects
        """
        conversation_ids = self.user_conversations.get(user_id, [])
        return [self.conversations[cid] for cid in conversation_ids if cid in self.conversations]
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get a specific conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation object or None
        """
        return self.conversations.get(conversation_id)
    
    def get_message(self, message_id: str) -> Optional[ChatMessage]:
        """
        Get a specific message.
        
        Args:
            message_id: Message ID
            
        Returns:
            ChatMessage object or None
        """
        return self.messages.get(message_id)
    
    def get_messages_by_sha(self, sha256: str) -> List[ChatMessage]:
        """
        Get messages by SHA256 hash.
        
        Args:
            sha256: SHA256 hash
            
        Returns:
            List of ChatMessage objects
        """
        return [msg for msg in self.messages.values() if msg.sha256 == sha256]
    
    def search_messages(
        self,
        user_id: str,
        query: str,
        conversation_id: Optional[str] = None
    ) -> List[ChatMessage]:
        """
        Search messages by content.
        
        Args:
            user_id: User ID
            query: Search query
            conversation_id: Optional conversation ID to limit search
            
        Returns:
            List of matching ChatMessage objects
        """
        # Get relevant messages
        if conversation_id:
            messages = self.get_conversation_messages(conversation_id)
        else:
            # Get all messages from user's conversations
            conversation_ids = self.user_conversations.get(user_id, [])
            messages = []
            for cid in conversation_ids:
                messages.extend(self.get_conversation_messages(cid))
        
        # Filter by query
        query_lower = query.lower()
        matching_messages = []
        
        for message in messages:
            # Search in text content
            if isinstance(message.content, str) and query_lower in message.content.lower():
                matching_messages.append(message)
            # Search in metadata
            elif any(query_lower in str(v).lower() for v in message.metadata.values()):
                matching_messages.append(message)
        
        return matching_messages
    
    def delete_message(self, message_id: str, user_id: str) -> bool:
        """
        Delete a message.
        
        Args:
            message_id: Message ID
            user_id: User ID requesting deletion (must be sender)
            
        Returns:
            True if deleted successfully
        """
        if message_id not in self.messages:
            return False
        
        message = self.messages[message_id]
        
        # Only sender can delete
        if message.sender_id != user_id:
            return False
        
        # Remove from messages
        del self.messages[message_id]
        
        # Remove from conversation
        if message.conversation_id in self.messages_by_conversation:
            self.messages_by_conversation[message.conversation_id].remove(message_id)
        
        # Update conversation
        if message.conversation_id in self.conversations:
            conversation = self.conversations[message.conversation_id]
            conversation.message_count = max(0, conversation.message_count - 1)
        
        return True
    
    def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """
        Delete a conversation for a user.
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID requesting deletion
            
        Returns:
            True if deleted successfully
        """
        if conversation_id not in self.conversations:
            return False
        
        conversation = self.conversations[conversation_id]
        
        # Remove from user's conversations
        if user_id in self.user_conversations:
            if conversation_id in self.user_conversations[user_id]:
                self.user_conversations[user_id].remove(conversation_id)
        
        # If no participants left, fully delete conversation
        remaining_users = [uid for uid in conversation.participants if uid != user_id]
        if not remaining_users:
            # Delete all messages
            for message_id in self.messages_by_conversation.get(conversation_id, []):
                if message_id in self.messages:
                    del self.messages[message_id]
            
            # Delete conversation
            del self.conversations[conversation_id]
            del self.messages_by_conversation[conversation_id]
        
        return True
    
    def get_conversation_statistics(self, conversation_id: str) -> Dict[str, any]:
        """
        Get statistics about a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Dictionary containing conversation statistics
        """
        if conversation_id not in self.conversations:
            return {}
        
        conversation = self.conversations[conversation_id]
        messages = self.get_conversation_messages(conversation_id)
        
        message_type_counts = {}
        for msg in messages:
            msg_type = msg.message_type.value
            message_type_counts[msg_type] = message_type_counts.get(msg_type, 0) + 1
        
        return {
            'conversation_id': conversation_id,
            'participants': conversation.participants,
            'message_count': conversation.message_count,
            'unread_count': conversation.unread_count,
            'created_at': conversation.created_at,
            'last_activity': conversation.last_activity,
            'message_type_distribution': message_type_counts,
            'duration_hours': (datetime.now().timestamp() - conversation.created_at) / 3600
        }
    
    def get_user_statistics(self, user_id: str) -> Dict[str, any]:
        """
        Get statistics for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary containing user statistics
        """
        conversations = self.get_user_conversations(user_id)
        
        total_messages = 0
        total_unread = 0
        message_type_counts = {}
        
        for conv in conversations:
            total_messages += conv.message_count
            total_unread += conv.unread_count
            
            messages = self.get_conversation_messages(conv.conversation_id)
            for msg in messages:
                if msg.sender_id == user_id:
                    msg_type = msg.message_type.value
                    message_type_counts[msg_type] = message_type_counts.get(msg_type, 0) + 1
        
        return {
            'user_id': user_id,
            'total_conversations': len(conversations),
            'total_messages_sent': total_messages,
            'total_unread_messages': total_unread,
            'message_type_distribution': message_type_counts
        }
    
    def _calculate_sha256(self, content: Union[str, bytes, Dict]) -> str:
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
