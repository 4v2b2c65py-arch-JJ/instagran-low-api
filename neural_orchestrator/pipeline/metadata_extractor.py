"""
Web Metadata Extractor - Pipeline Buffer and Axiom Pattern Tracing
Extracts web metadata from instance nodes, observes axiom patterns, and traces them in pipeline buffer flows.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json


@dataclass
class WebMetadata:
    """Represents web metadata for an instance node."""
    node_id: str
    url: Optional[str]
    title: Optional[str]
    description: Optional[str]
    keywords: List[str]
    axiom_patterns: List[str]
    timestamp: float
    hash: str


@dataclass
class PipelineEntry:
    """Represents an entry in the pipeline buffer."""
    entry_id: str
    metadata: WebMetadata
    command: Optional[Dict]
    flow_state: Dict[str, any]
    timestamp: float
    processed: bool


class WebMetadataExtractor:
    """
    Extracts web metadata from instance nodes and observes axiom patterns.
    Traces patterns in pipeline buffer flows and recovers commands.
    """
    
    def __init__(self, buffer_size: int = 1000):
        """
        Initialize the Web Metadata Extractor.
        
        Args:
            buffer_size: Maximum size of pipeline buffer
        """
        self.buffer_size = buffer_size
        self.pipeline_buffer: List[PipelineEntry] = []
        self.metadata_registry: Dict[str, WebMetadata] = {}
        self.axiom_pattern_registry: Dict[str, List[str]] = {}
        
        # Flow tracking
        self.flow_states: Dict[str, Dict] = {}
        self.active_flows: List[str] = []
    
    def extract_metadata(
        self,
        node_id: str,
        url: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        keywords: Optional[List[str]] = None
    ) -> WebMetadata:
        """
        Extract web metadata from an instance node.
        
        Args:
            node_id: Node identifier
            url: URL of the node
            title: Title of the node
            description: Description of the node
            keywords: List of keywords
            
        Returns:
            WebMetadata object
        """
        if keywords is None:
            keywords = []
        
        # Observe axiom patterns
        axiom_patterns = self._observe_axiom_patterns(node_id, title, description, keywords)
        
        # Create metadata
        metadata = WebMetadata(
            node_id=node_id,
            url=url,
            title=title,
            description=description,
            keywords=keywords,
            axiom_patterns=axiom_patterns,
            timestamp=datetime.now().timestamp(),
            hash=self._generate_metadata_hash(node_id, url, title)
        )
        
        # Register metadata
        self.metadata_registry[node_id] = metadata
        
        # Register axiom patterns
        for pattern in axiom_patterns:
            if pattern not in self.axiom_pattern_registry:
                self.axiom_pattern_registry[pattern] = []
            self.axiom_pattern_registry[pattern].append(node_id)
        
        return metadata
    
    def _observe_axiom_patterns(
        self,
        node_id: str,
        title: Optional[str],
        description: Optional[str],
        keywords: List[str]
    ) -> List[str]:
        """
        Observe axiom patterns from node data.
        
        Args:
            node_id: Node identifier
            title: Node title
            description: Node description
            keywords: List of keywords
            
        Returns:
            List of observed axiom patterns
        """
        patterns = []
        
        # Extract patterns from title
        if title:
            patterns.extend(self._extract_text_patterns(title))
        
        # Extract patterns from description
        if description:
            patterns.extend(self._extract_text_patterns(description))
        
        # Extract patterns from keywords
        for keyword in keywords:
            patterns.append(f"keyword:{keyword.lower()}")
        
        # Extract patterns from node_id
        patterns.extend(self._extract_node_id_patterns(node_id))
        
        # Remove duplicates
        patterns = list(set(patterns))
        
        return patterns
    
    def _extract_text_patterns(self, text: str) -> List[str]:
        """
        Extract patterns from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of patterns
        """
        patterns = []
        
        # Word patterns (words > 3 characters)
        words = text.split()
        for word in words:
            if len(word) > 3:
                patterns.append(f"word:{word.lower()}")
        
        # Length patterns
        patterns.append(f"length:{len(text)}")
        
        # Character patterns
        if any(c.isdigit() for c in text):
            patterns.append("contains:digit")
        if any(c.isupper() for c in text):
            patterns.append("contains:uppercase")
        
        return patterns
    
    def _extract_node_id_patterns(self, node_id: str) -> List[str]:
        """
        Extract patterns from node ID.
        
        Args:
            node_id: Node identifier
            
        Returns:
            List of patterns
        """
        patterns = []
        
        # Separator patterns
        if '_' in node_id:
            patterns.append("separator:underscore")
        if '-' in node_id:
            patterns.append("separator:hyphen")
        if '/' in node_id:
            patterns.append("separator:slash")
        
        # Length pattern
        patterns.append(f"id_length:{len(node_id)}")
        
        return patterns
    
    def _generate_metadata_hash(self, node_id: str, url: Optional[str], title: Optional[str]) -> str:
        """
        Generate hash for metadata.
        
        Args:
            node_id: Node identifier
            url: URL
            title: Title
            
        Returns:
            Hash string
        """
        data = f"{node_id}_{url}_{title}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def trace_in_pipeline_buffer(
        self,
        metadata: WebMetadata,
        command: Optional[Dict] = None,
        flow_state: Optional[Dict] = None
    ) -> PipelineEntry:
        """
        Trace metadata in pipeline buffer flow.
        
        Args:
            metadata: Web metadata to trace
            command: Optional command to include
            flow_state: Flow state information
            
        Returns:
            PipelineEntry object
        """
        if flow_state is None:
            flow_state = {}
        
        # Create pipeline entry
        entry = PipelineEntry(
            entry_id=f"entry_{len(self.pipeline_buffer)}_{datetime.now().timestamp()}",
            metadata=metadata,
            command=command,
            flow_state=flow_state,
            timestamp=datetime.now().timestamp(),
            processed=False
        )
        
        # Add to buffer
        self.pipeline_buffer.append(entry)
        
        # Manage buffer size
        if len(self.pipeline_buffer) > self.buffer_size:
            self.pipeline_buffer.pop(0)
        
        # Update flow state
        self.flow_states[entry.entry_id] = flow_state
        if entry.entry_id not in self.active_flows:
            self.active_flows.append(entry.entry_id)
        
        return entry
    
    def recover_commands(self, node_id: Optional[str] = None) -> List[Dict]:
        """
        Recover commands from pipeline buffer.
        
        Args:
            node_id: Optional node ID to filter by
            
        Returns:
            List of recovered commands
        """
        commands = []
        
        for entry in self.pipeline_buffer:
            if entry.command is not None:
                if node_id is None or entry.metadata.node_id == node_id:
                    commands.append({
                        'entry_id': entry.entry_id,
                        'command': entry.command,
                        'node_id': entry.metadata.node_id,
                        'timestamp': entry.timestamp
                    })
        
        return commands
    
    def get_axiom_pattern_nodes(self, pattern: str) -> List[str]:
        """
        Get nodes that match a specific axiom pattern.
        
        Args:
            pattern: Axiom pattern to search for
            
        Returns:
            List of node IDs matching the pattern
        """
        return self.axiom_pattern_registry.get(pattern, [])
    
    def get_flow_state(self, entry_id: str) -> Optional[Dict]:
        """
        Get flow state for a pipeline entry.
        
        Args:
            entry_id: Pipeline entry ID
            
        Returns:
            Flow state dictionary or None
        """
        return self.flow_states.get(entry_id)
    
    def update_flow_state(self, entry_id: str, new_state: Dict):
        """
        Update flow state for a pipeline entry.
        
        Args:
            entry_id: Pipeline entry ID
            new_state: New flow state
        """
        self.flow_states[entry_id] = new_state
        
        # Update entry in buffer
        for entry in self.pipeline_buffer:
            if entry.entry_id == entry_id:
                entry.flow_state = new_state
                break
    
    def mark_processed(self, entry_id: str):
        """
        Mark a pipeline entry as processed.
        
        Args:
            entry_id: Pipeline entry ID
        """
        for entry in self.pipeline_buffer:
            if entry.entry_id == entry_id:
                entry.processed = True
                break
        
        # Remove from active flows
        if entry_id in self.active_flows:
            self.active_flows.remove(entry_id)
    
    def get_pipeline_snapshot(self, include_processed: bool = False) -> List[Dict]:
        """
        Get snapshot of pipeline buffer.
        
        Args:
            include_processed: Whether to include processed entries
            
        Returns:
            List of pipeline entry dictionaries
        """
        snapshot = []
        
        for entry in self.pipeline_buffer:
            if include_processed or not entry.processed:
                snapshot.append({
                    'entry_id': entry.entry_id,
                    'node_id': entry.metadata.node_id,
                    'command': entry.command,
                    'flow_state': entry.flow_state,
                    'timestamp': entry.timestamp,
                    'processed': entry.processed
                })
        
        return snapshot
    
    def get_pattern_statistics(self) -> Dict[str, any]:
        """
        Get statistics about axiom patterns.
        
        Returns:
            Dictionary containing pattern statistics
        """
        pattern_counts = {pattern: len(nodes) for pattern, nodes in self.axiom_pattern_registry.items()}
        
        return {
            'total_patterns': len(self.axiom_pattern_registry),
            'pattern_counts': pattern_counts,
            'most_common_patterns': sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            'total_metadata_entries': len(self.metadata_registry)
        }
    
    def get_buffer_statistics(self) -> Dict[str, any]:
        """
        Get statistics about pipeline buffer.
        
        Returns:
            Dictionary containing buffer statistics
        """
        processed_count = sum(1 for entry in self.pipeline_buffer if entry.processed)
        unprocessed_count = len(self.pipeline_buffer) - processed_count
        
        return {
            'buffer_size': len(self.pipeline_buffer),
            'max_buffer_size': self.buffer_size,
            'processed_entries': processed_count,
            'unprocessed_entries': unprocessed_count,
            'active_flows': len(self.active_flows),
            'total_commands': sum(1 for entry in self.pipeline_buffer if entry.command is not None)
        }
    
    def clear_processed_entries(self):
        """Clear processed entries from the pipeline buffer."""
        self.pipeline_buffer = [entry for entry in self.pipeline_buffer if not entry.processed]
        
        # Clean up flow states
        active_ids = {entry.entry_id for entry in self.pipeline_buffer}
        self.flow_states = {k: v for k, v in self.flow_states.items() if k in active_ids}
        self.active_flows = [flow_id for flow_id in self.active_flows if flow_id in active_ids]
