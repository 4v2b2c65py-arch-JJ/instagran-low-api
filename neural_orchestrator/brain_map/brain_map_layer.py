"""
Brain Map Layer - Central Neural Integration
Integrates all device inputs and feeds into the central brain map layer.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class BrainMapNode:
    """Represents a node in the brain map layer."""
    node_id: str
    node_type: str
    position: Tuple[float, float, float]  # 3D coordinates
    activation: float  # 0-1
    connections: List[str]  # Connected node IDs
    metadata: Dict[str, any]
    last_update: float


@dataclass
class BrainMapConnection:
    """Represents a connection between brain map nodes."""
    connection_id: str
    source_node: str
    target_node: str
    strength: float  # 0-1
    connection_type: str
    metadata: Dict[str, any]


class BrainMapLayer:
    """
    Central brain map layer that integrates all device inputs.
    Creates a neural representation of device interactions and feeds.
    """
    
    def __init__(self, layer_id: str = "main_layer", dimensions: Tuple[int, int, int] = (100, 100, 100)):
        """
        Initialize the Brain Map Layer.
        
        Args:
            layer_id: Identifier for this brain map layer
            dimensions: 3D dimensions of the brain map space
        """
        self.layer_id = layer_id
        self.dimensions = dimensions
        
        # Brain map structure
        self.nodes: Dict[str, BrainMapNode] = {}
        self.connections: Dict[str, BrainMapConnection] = {}
        
        # Input feeds from various sources
        self.input_feeds: Dict[str, List[Dict]] = {}
        
        # Activation patterns
        self.activation_patterns: List[Dict[str, float]] = {}
        
        # Learning state
        self.learning_rate = 0.1
        self.decay_rate = 0.99
        
        # Statistics
        self.total_inputs_processed = 0
        self.last_update_time = datetime.now().timestamp()
    
    def add_input_feed(self, source_type: str, feed_data: List[Dict]):
        """
        Add input feed from a source to the brain map.
        
        Args:
            source_type: Type of input source (cache, emoji, auto_corrector, click, app_interaction)
            feed_data: List of feed data dictionaries
        """
        if source_type not in self.input_feeds:
            self.input_feeds[source_type] = []
        
        self.input_feeds[source_type].extend(feed_data)
        
        # Process feed to update brain map
        self._process_input_feed(source_type, feed_data)
        
        self.total_inputs_processed += len(feed_data)
        self.last_update_time = datetime.now().timestamp()
    
    def _process_input_feed(self, source_type: str, feed_data: List[Dict]):
        """
        Process input feed to update brain map nodes and connections.
        
        Args:
            source_type: Type of input source
            feed_data: Feed data to process
        """
        for data in feed_data:
            # Create or update node based on input
            node_id = self._generate_node_id(source_type, data)
            
            if node_id not in self.nodes:
                # Create new node
                position = self._generate_node_position(source_type, data)
                node = BrainMapNode(
                    node_id=node_id,
                    node_type=source_type,
                    position=position,
                    activation=0.5,
                    connections=[],
                    metadata=data.copy(),
                    last_update=datetime.now().timestamp()
                )
                self.nodes[node_id] = node
            else:
                # Update existing node
                node = self.nodes[node_id]
                node.activation = min(node.activation + 0.1, 1.0)
                node.metadata.update(data)
                node.last_update = datetime.now().timestamp()
            
            # Create connections to related nodes
            self._create_connections(node_id, source_type, data)
    
    def _generate_node_id(self, source_type: str, data: Dict) -> str:
        """
        Generate unique node ID from source and data.
        
        Args:
            source_type: Type of input source
            data: Feed data
            
        Returns:
            Unique node ID
        """
        # Extract key identifier from data
        key_fields = ['cache_id', 'emoji', 'original_text', 'click_id', 'interaction_id']
        
        for field in key_fields:
            if field in data:
                return f"{source_type}_{data[field]}"
        
        # Fallback to timestamp-based ID
        return f"{source_type}_{datetime.now().timestamp()}"
    
    def _generate_node_position(self, source_type: str, data: Dict) -> Tuple[float, float, float]:
        """
        Generate 3D position for a node.
        
        Args:
            source_type: Type of input source
            data: Feed data
            
        Returns:
            3D coordinates (x, y, z)
        """
        # Use source type to determine base position
        source_positions = {
            'cache': (0.2, 0.2, 0.2),
            'emoji': (0.2, 0.8, 0.2),
            'auto_corrector': (0.8, 0.2, 0.2),
            'click': (0.5, 0.5, 0.5),
            'app_interaction': (0.8, 0.8, 0.8),
            'click_pattern': (0.5, 0.5, 0.8)
        }
        
        base_pos = source_positions.get(source_type, (0.5, 0.5, 0.5))
        
        # Add randomness for variation
        noise = np.random.uniform(-0.1, 0.1, 3)
        
        x = (base_pos[0] + noise[0]) * self.dimensions[0]
        y = (base_pos[1] + noise[1]) * self.dimensions[1]
        z = (base_pos[2] + noise[2]) * self.dimensions[2]
        
        return (x, y, z)
    
    def _create_connections(self, node_id: str, source_type: str, data: Dict):
        """
        Create connections between nodes based on relationships.
        
        Args:
            node_id: Source node ID
            source_type: Type of input source
            data: Feed data
        """
        # Find related nodes based on metadata
        related_nodes = []
        
        # Connect nodes with similar metadata
        for other_id, other_node in self.nodes.items():
            if other_id == node_id:
                continue
            
            # Calculate similarity
            similarity = self._calculate_similarity(data, other_node.metadata)
            
            if similarity > 0.5:
                related_nodes.append((other_id, similarity))
        
        # Create connections to related nodes
        for other_id, similarity in related_nodes:
            connection_id = f"conn_{node_id}_{other_id}"
            
            if connection_id not in self.connections:
                connection = BrainMapConnection(
                    connection_id=connection_id,
                    source_node=node_id,
                    target_node=other_id,
                    strength=similarity,
                    connection_type="similarity",
                    metadata={'similarity_score': similarity}
                )
                self.connections[connection_id] = connection
                
                # Update node connections list
                if node_id in self.nodes:
                    self.nodes[node_id].connections.append(other_id)
                if other_id in self.nodes:
                    self.nodes[other_id].connections.append(node_id)
    
    def _calculate_similarity(self, data1: Dict, data2: Dict) -> float:
        """
        Calculate similarity between two data dictionaries.
        
        Args:
            data1: First data dictionary
            data2: Second data dictionary
            
        Returns:
            Similarity score (0-1)
        """
        # Simple similarity based on shared keys
        keys1 = set(data1.keys())
        keys2 = set(data2.keys())
        
        shared_keys = keys1 & keys2
        total_keys = keys1 | keys2
        
        if not total_keys:
            return 0.0
        
        key_similarity = len(shared_keys) / len(total_keys)
        
        # Value similarity for shared keys
        value_similarities = []
        for key in shared_keys:
            val1 = data1[key]
            val2 = data2[key]
            
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # Numerical similarity
                if val1 == val2:
                    value_similarities.append(1.0)
                else:
                    value_similarities.append(0.5)
            elif isinstance(val1, str) and isinstance(val2, str):
                # String similarity
                if val1 == val2:
                    value_similarities.append(1.0)
                else:
                    value_similarities.append(0.3)
            else:
                value_similarities.append(0.5)
        
        if value_similarities:
            avg_value_similarity = np.mean(value_similarities)
        else:
            avg_value_similarity = 0.0
        
        # Combine key and value similarities
        return (key_similarity * 0.4) + (avg_value_similarity * 0.6)
    
    def activate_node(self, node_id: str, activation: float):
        """
        Manually activate a node.
        
        Args:
            node_id: Node ID to activate
            activation: Activation level (0-1)
        """
        if node_id in self.nodes:
            self.nodes[node_id].activation = min(max(activation, 0.0), 1.0)
            self.nodes[node_id].last_update = datetime.now().timestamp()
            
            # Propagate activation to connected nodes
            self._propagate_activation(node_id)
    
    def _propagate_activation(self, node_id: str):
        """
        Propagate activation to connected nodes.
        
        Args:
            node_id: Source node ID
        """
        if node_id not in self.nodes:
            return
        
        node = self.nodes[node_id]
        
        for connected_id in node.connections:
            if connected_id in self.nodes:
                # Find connection strength
                connection_id = f"conn_{node_id}_{connected_id}"
                reverse_connection_id = f"conn_{connected_id}_{node_id}"
                
                strength = 0.5
                if connection_id in self.connections:
                    strength = self.connections[connection_id].strength
                elif reverse_connection_id in self.connections:
                    strength = self.connections[reverse_connection_id].strength
                
                # Propagate activation
                connected_node = self.nodes[connected_id]
                connected_node.activation = min(
                    connected_node.activation + (node.activation * strength * self.learning_rate),
                    1.0
                )
    
    def apply_decay(self):
        """Apply decay to all node activations."""
        for node in self.nodes.values():
            node.activation *= self.decay_rate
            node.last_update = datetime.now().timestamp()
    
    def get_activation_pattern(self) -> Dict[str, float]:
        """
        Get current activation pattern across all nodes.
        
        Returns:
            Dictionary mapping node IDs to activation levels
        """
        return {node_id: node.activation for node_id, node in self.nodes.items()}
    
    def get_highly_active_nodes(self, threshold: float = 0.7) -> List[BrainMapNode]:
        """
        Get nodes with activation above threshold.
        
        Args:
            threshold: Activation threshold
            
        Returns:
            List of highly active BrainMapNode objects
        """
        return [node for node in self.nodes.values() if node.activation >= threshold]
    
    def get_node_clusters(self) -> List[List[str]]:
        """
        Identify clusters of strongly connected nodes.
        
        Returns:
            List of node clusters (each cluster is a list of node IDs)
        """
        clusters = []
        visited = set()
        
        for node_id in self.nodes:
            if node_id not in visited:
                cluster = self._find_cluster(node_id, visited)
                if len(cluster) > 1:
                    clusters.append(cluster)
        
        return clusters
    
    def _find_cluster(self, node_id: str, visited: set) -> List[str]:
        """
        Find cluster of connected nodes using DFS.
        
        Args:
            node_id: Starting node ID
            visited: Set of visited node IDs
            
        Returns:
            List of node IDs in the cluster
        """
        cluster = []
        stack = [node_id]
        
        while stack:
            current_id = stack.pop()
            
            if current_id in visited:
                continue
            
            visited.add(current_id)
            cluster.append(current_id)
            
            if current_id in self.nodes:
                for connected_id in self.nodes[current_id].connections:
                    if connected_id not in visited:
                        stack.append(connected_id)
        
        return cluster
    
    def get_brain_map_statistics(self) -> Dict[str, any]:
        """
        Get statistics about the brain map layer.
        
        Returns:
            Dictionary containing brain map statistics
        """
        activations = [node.activation for node in self.nodes.values()]
        
        return {
            'layer_id': self.layer_id,
            'total_nodes': len(self.nodes),
            'total_connections': len(self.connections),
            'avg_activation': np.mean(activations) if activations else 0.0,
            'max_activation': max(activations) if activations else0.0,
            'highly_active_nodes': len([a for a in activations if a >= 0.7]),
            'input_sources': list(self.input_feeds.keys()),
            'total_inputs_processed': self.total_inputs_processed,
            'last_update_time': self.last_update_time,
            'node_clusters': len(self.get_node_clusters())
        }
    
    def export_brain_map(self) -> Dict[str, any]:
        """
        Export brain map structure as dictionary.
        
        Returns:
            Dictionary containing brain map data
        """
        return {
            'layer_id': self.layer_id,
            'dimensions': self.dimensions,
            'nodes': {node_id: node.__dict__ for node_id, node in self.nodes.items()},
            'connections': {conn_id: conn.__dict__ for conn_id, conn in self.connections.items()},
            'statistics': self.get_brain_map_statistics(),
            'export_timestamp': datetime.now().timestamp()
        }
    
    def clear_inactive_nodes(self, threshold: float = 0.1):
        """
        Clear nodes with activation below threshold.
        
        Args:
            threshold: Activation threshold for clearing
        """
        nodes_to_remove = [
            node_id for node_id, node in self.nodes.items()
            if node.activation < threshold
        ]
        
        for node_id in nodes_to_remove:
            # Remove connections
            connections_to_remove = [
                conn_id for conn_id, conn in self.connections.items()
                if conn.source_node == node_id or conn.target_node == node_id
            ]
            
            for conn_id in connections_to_remove:
                del self.connections[conn_id]
            
            # Remove node
            del self.nodes[node_id]
