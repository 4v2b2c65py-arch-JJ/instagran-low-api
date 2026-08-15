"""
Lightweight Context Model
Provides a lightweight context model for device OS reaction data and session management.
Integrates with Pinecone for vector storage and retrieval of context patterns.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class ContextType(Enum):
    """Types of context data."""
    OS_REACTION = "os_reaction"
    SESSION_MESSAGE = "session_message"
    DEVICE_STATE = "device_state"
    USER_BEHAVIOR = "user_behavior"
    AGENT_ACTION = "agent_action"


@dataclass
class ContextItem:
    """Represents a context item."""
    context_id: str
    context_type: ContextType
    content: str
    timestamp: str
    device_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    embedding_vector: Optional[List[float]] = None


class LightweightContextModel:
    """
    Lightweight context model for managing device OS reactions and session data.
    Provides efficient context storage, retrieval, and pattern detection.
    """

    def __init__(self, max_context_items: int = 1000):
        self.max_context_items = max_context_items
        self.context_buffer: List[ContextItem] = []
        self.context_index: Dict[str, int] = {}  # context_id -> index
        self.session_contexts: Dict[str, List[ContextItem]] = {}  # session_id -> contexts
        self.device_contexts: Dict[str, List[ContextItem]] = {}  # device_id -> contexts
        self.pattern_cache: Dict[str, List[ContextItem]] = {}  # pattern -> matching contexts

    def add_context(
        self,
        context_type: ContextType,
        content: str,
        device_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ContextItem:
        """
        Add a context item to the model.
        
        Args:
            context_type: Type of context
            content: Context content
            device_id: Optional device identifier
            session_id: Optional session identifier
            metadata: Optional metadata
            
        Returns:
            ContextItem: The added context item
        """
        context_id = self._generate_context_id(context_type, content)
        
        context_item = ContextItem(
            context_id=context_id,
            context_type=context_type,
            content=content,
            timestamp=datetime.utcnow().isoformat(),
            device_id=device_id,
            session_id=session_id,
            metadata=metadata or {}
        )
        
        # Add to buffer
        self._add_to_buffer(context_item)
        
        # Add to session context
        if session_id:
            if session_id not in self.session_contexts:
                self.session_contexts[session_id] = []
            self.session_contexts[session_id].append(context_item)
        
        # Add to device context
        if device_id:
            if device_id not in self.device_contexts:
                self.device_contexts[device_id] = []
            self.device_contexts[device_id].append(context_item)
        
        return context_item

    def _generate_context_id(self, context_type: ContextType, content: str) -> str:
        """Generate unique context ID."""
        import hashlib
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:12]
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"{context_type.value}_{timestamp}_{content_hash}"

    def _add_to_buffer(self, context_item: ContextItem):
        """Add context item to buffer with size management."""
        if len(self.context_buffer) >= self.max_context_items:
            # Remove oldest item
            oldest = self.context_buffer.pop(0)
            del self.context_index[oldest.context_id]
        
        self.context_buffer.append(context_item)
        self.context_index[context_item.context_id] = len(self.context_buffer) - 1

    def get_context(self, context_id: str) -> Optional[ContextItem]:
        """Get context item by ID."""
        index = self.context_index.get(context_id)
        if index is not None:
            return self.context_buffer[index]
        return None

    def get_session_context(self, session_id: str) -> List[ContextItem]:
        """Get all context items for a session."""
        return self.session_contexts.get(session_id, []).copy()

    def get_device_context(self, device_id: str) -> List[ContextItem]:
        """Get all context items for a device."""
        return self.device_contexts.get(device_id, []).copy()

    def search_context(
        self,
        query: str,
        context_type: Optional[ContextType] = None,
        limit: int = 10
    ) -> List[ContextItem]:
        """
        Search context items by query text.
        
        Args:
            query: Search query
            context_type: Optional context type filter
            limit: Maximum number of results
            
        Returns:
            List of matching context items
        """
        results = []
        query_lower = query.lower()
        
        for context in reversed(self.context_buffer):  # Search newest first
            if context_type and context.context_type != context_type:
                continue
            
            if query_lower in context.content.lower():
                results.append(context)
                if len(results) >= limit:
                    break
        
        return results

    def detect_patterns(
        self,
        context_type: Optional[ContextType] = None,
        time_window_seconds: int = 3600
    ) -> Dict[str, Any]:
        """
        Detect patterns in context data.
        
        Args:
            context_type: Optional context type filter
            time_window_seconds: Time window for pattern detection
            
        Returns:
            Dict containing detected patterns
        """
        patterns = {
            "timestamp": datetime.utcnow().isoformat(),
            "time_window": time_window_seconds,
            "patterns_found": []
        }
        
        # Filter contexts by time window and type
        cutoff_time = datetime.utcnow().timestamp() - time_window_seconds
        recent_contexts = [
            c for c in self.context_buffer
            if datetime.fromisoformat(c.timestamp).timestamp() > cutoff_time
            and (context_type is None or c.context_type == context_type)
        ]
        
        # Detect frequency patterns
        type_counts = {}
        for context in recent_contexts:
            type_name = context.context_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        if type_counts:
            patterns["patterns_found"].append({
                "type": "frequency",
                "data": type_counts
            })
        
        # Detect device patterns
        device_counts = {}
        for context in recent_contexts:
            if context.device_id:
                device_counts[context.device_id] = device_counts.get(context.device_id, 0) + 1
        
        if device_counts:
            patterns["patterns_found"].append({
                "type": "device_activity",
                "data": device_counts
            })
        
        return patterns

    def merge_contexts(
        self,
        context_ids: List[str],
        merged_context_type: ContextType = ContextType.SESSION_MESSAGE
    ) -> ContextItem:
        """
        Merge multiple context items into a single context.
        
        Args:
            context_ids: List of context IDs to merge
            merged_context_type: Type for the merged context
            
        Returns:
            ContextItem: The merged context item
        """
        contexts = [self.get_context(cid) for cid in context_ids if self.get_context(cid)]
        
        if not contexts:
            raise ValueError("No valid contexts to merge")
        
        # Merge content
        merged_content = " | ".join([c.content for c in contexts])
        
        # Merge metadata
        merged_metadata = {}
        for context in contexts:
            if context.metadata:
                merged_metadata.update(context.metadata)
        
        # Create merged context
        merged_context = self.add_context(
            context_type=merged_context_type,
            content=merged_content,
            device_id=contexts[0].device_id,
            session_id=contexts[0].session_id,
            metadata={
                **merged_metadata,
                "merged_from": [c.context_id for c in contexts],
                "merge_timestamp": datetime.utcnow().isoformat()
            }
        )
        
        return merged_context

    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of context model state."""
        return {
            "total_contexts": len(self.context_buffer),
            "max_capacity": self.max_context_items,
            "utilization": len(self.context_buffer) / self.max_context_items,
            "session_count": len(self.session_contexts),
            "device_count": len(self.device_contexts),
            "type_distribution": self._get_type_distribution(),
            "timestamp": datetime.utcnow().isoformat()
        }

    def _get_type_distribution(self) -> Dict[str, int]:
        """Get distribution of context types."""
        distribution = {}
        for context in self.context_buffer:
            type_name = context.context_type.value
            distribution[type_name] = distribution.get(type_name, 0) + 1
        return distribution

    def clear_old_contexts(self, age_seconds: int = 86400) -> int:
        """
        Clear contexts older than specified age.
        
        Args:
            age_seconds: Age threshold in seconds
            
        Returns:
            Number of contexts cleared
        """
        cutoff_time = datetime.utcnow().timestamp() - age_seconds
        to_remove = []
        
        for i, context in enumerate(self.context_buffer):
            if datetime.fromisoformat(context.timestamp).timestamp() < cutoff_time:
                to_remove.append(i)
        
        # Remove in reverse order to maintain indices
        for i in reversed(to_remove):
            removed = self.context_buffer.pop(i)
            del self.context_index[removed.context_id]
            
            # Remove from session contexts
            if removed.session_id and removed.session_id in self.session_contexts:
                self.session_contexts[removed.session_id] = [
                    c for c in self.session_contexts[removed.session_id]
                    if c.context_id != removed.context_id
                ]
            
            # Remove from device contexts
            if removed.device_id and removed.device_id in self.device_contexts:
                self.device_contexts[removed.device_id] = [
                    c for c in self.device_contexts[removed.device_id]
                    if c.context_id != removed.context_id
                ]
        
        return len(to_remove)

    def export_contexts(
        self,
        context_type: Optional[ContextType] = None,
        format: str = "json"
    ) -> str:
        """
        Export contexts to specified format.
        
        Args:
            context_type: Optional context type filter
            format: Export format (json)
            
        Returns:
            Exported data as string
        """
        contexts = self.context_buffer
        if context_type:
            contexts = [c for c in contexts if c.context_type == context_type]
        
        if format == "json":
            export_data = [asdict(c) for c in contexts]
            # Convert enum to string
            for item in export_data:
                if item.get("context_type"):
                    item["context_type"] = item["context_type"].value
            return json.dumps(export_data, indent=2)
        
        raise ValueError(f"Unsupported format: {format}")

    def import_contexts(self, data: str, format: str = "json") -> int:
        """
        Import contexts from specified format.
        
        Args:
            data: Data to import
            format: Import format (json)
            
 Returns:
            Number of contexts imported
        """
        if format == "json":
            import_data = json.loads(data)
            count = 0
            
            for item in import_data:
                # Convert string back to enum
                if isinstance(item.get("context_type"), str):
                    item["context_type"] = ContextType(item["context_type"])
                
                context_item = ContextItem(**item)
                self._add_to_buffer(context_item)
                
                # Rebuild session and device contexts
                if context_item.session_id:
                    if context_item.session_id not in self.session_contexts:
                        self.session_contexts[context_item.session_id] = []
                    self.session_contexts[context_item.session_id].append(context_item)
                
                if context_item.device_id:
                    if context_item.device_id not in self.device_contexts:
                        self.device_contexts[context_item.device_id] = []
                    self.device_contexts[context_item.device_id].append(context_item)
                
                count += 1
            
            return count
        
        raise ValueError(f"Unsupported format: {format}")
