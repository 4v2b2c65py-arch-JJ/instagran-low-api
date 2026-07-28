"""
Node Manager - Node Entry Management (1-9.4M+ nodes)
Manages node entries for user knowledge base with scalable storage.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import uuid


class NodeStatus(Enum):
    """Status of a node."""
    ACTIVE = "active"
    DORMANT = "dormant"
    ARCHIVED = "archived"
    DELETED = "deleted"


class NodeType(Enum):
    """Types of nodes in the knowledge base."""
    EXPERIENCE = "experience"
    KNOWLEDGE = "knowledge"
    SKILL = "skill"
    MEMORY = "memory"
    PREFERENCE = "preference"
    RELATIONSHIP = "relationship"
    CONTEXT = "context"
    DECISION = "decision"


@dataclass
class NodeEntry:
    """Represents a node entry in the knowledge base."""
    node_id: str
    node_type: NodeType
    status: NodeStatus
    data: Dict[str, any]
    connections: List[str]
    weight: float
    activation: float
    created_at: float
    last_accessed: float
    access_count: int
    metadata: Dict[str, any]


class NodeManager:
    """
    Manages node entries for user knowledge base.
    Handles scalable storage from 1 to 9.4M+ nodes based on user age.
    """
    
    def __init__(self, target_node_count: int = 9_400_000):
        """
        Initialize the Node Manager.
        
        Args:
            target_node_count: Target number of nodes (default 9.4M for 18-year-old)
        """
        self.target_node_count = target_node_count
        
        # Node storage (using dictionary for O(1) access)
        self.nodes: Dict[str, NodeEntry] = {}
        
        # Node type indices
        self.nodes_by_type: Dict[NodeType, List[str]] = {}
        
        # Spatial indexing for efficient queries
        self.spatial_index: Dict[Tuple[int, int, int], List[str]] = {}
        
        # Connection graph
        self.adjacency_list: Dict[str, List[str]] = {}
        
        # Performance tracking
        self.node_creation_count = 0
        self.node_deletion_count = 0
        self.last_compaction_time = 0.0
    
    def create_node(
        self,
        node_type: NodeType,
        data: Dict[str, any],
        weight: float = 1.0,
        metadata: Optional[Dict[str, any]] = None
    ) -> NodeEntry:
        """
        Create a new node entry.
        
        Args:
            node_type: Type of node
            data: Node data
            weight: Node weight for importance
            metadata: Additional metadata
            
        Returns:
            NodeEntry object
        """
        # Generate unique node ID
        node_id = str(uuid.uuid4())
        
        # Calculate spatial position
        spatial_pos = self._calculate_spatial_position(node_type, data)
        
        # Create node
        node = NodeEntry(
            node_id=node_id,
            node_type=node_type,
            status=NodeStatus.ACTIVE,
            data=data,
            connections=[],
            weight=weight,
            activation=0.5,
            created_at=datetime.now().timestamp(),
            last_accessed=datetime.now().timestamp(),
            access_count=0,
            metadata=metadata or {}
        )
        
        # Store node
        self.nodes[node_id] = node
        
        # Update type index
        if node_type not in self.nodes_by_type:
            self.nodes_by_type[node_type] = []
        self.nodes_by_type[node_type].append(node_id)
        
        # Update spatial index
        if spatial_pos not in self.spatial_index:
            self.spatial_index[spatial_pos] = []
        self.spatial_index[spatial_pos].append(node_id)
        
        # Initialize adjacency list
        self.adjacency_list[node_id] = []
        
        self.node_creation_count += 1
        
        # Check if we need to compact
        if len(self.nodes) > self.target_node_count * 1.1:  # 10% buffer
            self._compact_nodes()
        
        return node
    
    def _calculate_spatial_position(self, node_type: NodeType, data: Dict) -> Tuple[int, int, int]:
        """
        Calculate spatial position for a node.
        
        Args:
            node_type: Type of node
            data: Node data
            
        Returns:
            3D spatial coordinates (grid position)
        """
        # Use hash of data for consistent positioning
        data_str = str(data) + node_type.value
        hash_val = hash(data_str)
        
        # Map to 3D grid (100x100x100 grid = 1M positions)
        grid_size = 100
        x = abs(hash_val) % grid_size
        y = abs(hash_val // grid_size) % grid_size
        z = abs(hash_val // (grid_size * grid_size)) % grid_size
        
        return (x, y, z)
    
    def get_node(self, node_id: str) -> Optional[NodeEntry]:
        """
        Retrieve a node entry.
        
        Args:
            node_id: Node ID to retrieve
            
        Returns:
            NodeEntry object or None
        """
        node = self.nodes.get(node_id)
        
        if node and node.status == NodeStatus.ACTIVE:
            # Update access tracking
            node.last_accessed = datetime.now().timestamp()
            node.access_count += 1
            node.activation = min(node.activation + 0.1, 1.0)
        
        return node
    
    def connect_nodes(self, node_id1: str, node_id2: str, strength: float = 0.5):
        """
        Create a connection between two nodes.
        
        Args:
            node_id1: First node ID
            node_id2: Second node ID
            strength: Connection strength (0-1)
        """
        if node_id1 not in self.nodes or node_id2 not in self.nodes:
            return
        
        node1 = self.nodes[node_id1]
        node2 = self.nodes[node_id2]
        
        # Add to connections
        if node_id2 not in node1.connections:
            node1.connections.append(node_id2)
        if node_id1 not in node2.connections:
            node2.connections.append(node_id1)
        
        # Update adjacency list
        self.adjacency_list[node_id1].append(node_id2)
        self.adjacency_list[node_id2].append(node_id1)
    
    def disconnect_nodes(self, node_id1: str, node_id2: str):
        """
        Remove connection between two nodes.
        
        Args:
            node_id1: First node ID
            node_id2: Second node ID
        """
        if node_id1 in self.nodes and node_id2 in self.nodes[node_id1].connections:
            self.nodes[node_id1].connections.remove(node_id2)
        if node_id2 in self.nodes and node_id1 in self.nodes[node_id2].connections:
            self.nodes[node_id2].connections.remove(node_id1)
        
        # Update adjacency list
        if node_id1 in self.adjacency_list and node_id2 in self.adjacency_list[node_id1]:
            self.adjacency_list[node_id1].remove(node_id2)
        if node_id2 in self.adjacency_list and node_id1 in self.adjacency_list[node_id2]:
            self.adjacency_list[node_id2].remove(node_id1)
    
    def activate_node(self, node_id: str, activation: float):
        """
        Set activation level for a node.
        
        Args:
            node_id: Node ID to activate
            activation: Activation level (0-1)
        """
        if node_id in self.nodes:
            self.nodes[node_id].activation = min(max(activation, 0.0), 1.0)
            
            # Propagate activation to connected nodes
            for connected_id in self.nodes[node_id].connections:
                if connected_id in self.nodes:
                    connected_node = self.nodes[connected_id]
                    connected_node.activation = min(
                        connected_node.activation + activation * 0.2,
                        1.0
                    )
    
    def get_nodes_by_type(self, node_type: NodeType) -> List[NodeEntry]:
        """
        Get all nodes of a specific type.
        
        Args:
            node_type: Type of nodes to retrieve
            
        Returns:
            List of NodeEntry objects
        """
        node_ids = self.nodes_by_type.get(node_type, [])
        return [self.nodes[nid] for nid in node_ids if nid in self.nodes]
    
    def get_connected_nodes(self, node_id: str) -> List[NodeEntry]:
        """
        Get all nodes connected to a given node.
        
        Args:
            node_id: Node ID
            
        Returns:
            List of connected NodeEntry objects
        """
        if node_id not in self.nodes:
            return []
        
        connected_ids = self.nodes[node_id].connections
        return [self.nodes[cid] for cid in connected_ids if cid in self.nodes]
    
    def find_nearby_nodes(self, node_id: str, radius: int = 5) -> List[NodeEntry]:
        """
        Find nodes within spatial radius of a given node.
        
        Args:
            node_id: Reference node ID
            radius: Spatial radius in grid units
            
        Returns:
            List of nearby NodeEntry objects
        """
        if node_id not in self.nodes:
            return []
        
        # Get spatial position of reference node
        ref_node = self.nodes[node_id]
        ref_pos = self._calculate_spatial_position(ref_node.node_type, ref_node.data)
        
        # Find nodes within radius
        nearby_nodes = []
        for other_id, other_node in self.nodes.items():
            if other_id == node_id:
                continue
            
            other_pos = self._calculate_spatial_position(other_node.node_type, other_node.data)
            
            # Calculate Manhattan distance
            distance = (
                abs(ref_pos[0] - other_pos[0]) +
                abs(ref_pos[1] - other_pos[1]) +
                abs(ref_pos[2] - other_pos[2])
            )
            
            if distance <= radius:
                nearby_nodes.append(other_node)
        
        return nearby_nodes
    
    def update_node_data(self, node_id: str, new_data: Dict[str, any]):
        """
        Update data for an existing node.
        
        Args:
            node_id: Node ID to update
            new_data: New data to merge
        """
        if node_id in self.nodes:
            self.nodes[node_id].data.update(new_data)
            self.nodes[node_id].last_accessed = datetime.now().timestamp()
    
    def archive_node(self, node_id: str):
        """
        Archive a node (mark as dormant).
        
        Args:
            node_id: Node ID to archive
        """
        if node_id in self.nodes:
            self.nodes[node_id].status = NodeStatus.DORMANT
            self.nodes[node_id].activation = 0.0
    
    def delete_node(self, node_id: str):
        """
        Delete a node from the knowledge base.
        
        Args:
            node_id: Node ID to delete
        """
        if node_id not in self.nodes:
            return
        
        node = self.nodes[node_id]
        
        # Remove connections
        for connected_id in node.connections:
            if connected_id in self.nodes:
                self.nodes[connected_id].connections.remove(node_id)
        
        # Remove from type index
        if node.node_type in self.nodes_by_type:
            self.nodes_by_type[node.node_type].remove(node_id)
        
        # Remove from adjacency list
        if node_id in self.adjacency_list:
            del self.adjacency_list[node_id]
        
        # Remove node
        del self.nodes[node_id]
        self.node_deletion_count += 1
    
    def _compact_nodes(self):
        """Compact nodes by archiving least recently used nodes."""
        # Sort by last accessed time
        sorted_nodes = sorted(
            self.nodes.values(),
            key=lambda n: n.last_accessed
        )
        
        # Archive 10% of oldest nodes
        archive_count = int(len(sorted_nodes) * 0.1)
        for node in sorted_nodes[:archive_count]:
            if node.status == NodeStatus.ACTIVE:
                self.archive_node(node.node_id)
        
        self.last_compaction_time = datetime.now().timestamp()
    
    def adjust_target_count(self, new_target: int):
        """
        Adjust target node count based on calibration.
        
        Args:
            new_target: New target node count
        """
        self.target_node_count = new_target
        
        # If we're over the new target, compact
        if len(self.nodes) > new_target:
            self._compact_nodes()
    
    def get_node_statistics(self) -> Dict[str, any]:
        """
        Get statistics about node management.
        
        Returns:
            Dictionary containing node statistics
        """
        active_nodes = [n for n in self.nodes.values() if n.status == NodeStatus.ACTIVE]
        dormant_nodes = [n for n in self.nodes.values() if n.status == NodeStatus.DORMANT]
        
        type_counts = {
            nt.value: len(self.nodes_by_type.get(nt, []))
            for nt in NodeType
        }
        
        avg_activation = np.mean([n.activation for n in active_nodes]) if active_nodes else 0.0
        avg_weight = np.mean([n.weight for n in active_nodes]) if active_nodes else 0.0
        
        return {
            'total_nodes': len(self.nodes),
            'active_nodes': len(active_nodes),
            'dormant_nodes': len(dormant_nodes),
            'target_node_count': self.target_node_count,
            'node_utilization': len(self.nodes) / self.target_node_count if self.target_node_count > 0 else 0,
            'nodes_by_type': type_counts,
            'avg_activation': avg_activation,
            'avg_weight': avg_weight,
            'total_connections': sum(len(conns) for conns in self.adjacency_list.values()),
            'node_creation_count': self.node_creation_count,
            'node_deletion_count': self.node_deletion_count,
            'last_compaction_time': self.last_compaction_time
        }
    
    def find_path(self, start_node_id: str, end_node_id: str) -> Optional[List[str]]:
        """
        Find shortest path between two nodes using BFS.
        
        Args:
            start_node_id: Starting node ID
            end_node_id: Ending node ID
            
        Returns:
            List of node IDs forming the path, or None if no path exists
        """
        if start_node_id not in self.nodes or end_node_id not in self.nodes:
            return None
        
        # BFS
        from collections import deque
        queue = deque([(start_node_id, [start_node_id])])
        visited = {start_node_id}
        
        while queue:
            current_node, path = queue.popleft()
            
            if current_node == end_node_id:
                return path
            
            for neighbor in self.adjacency_list.get(current_node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
