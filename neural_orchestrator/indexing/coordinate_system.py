"""
Coordinate System - Node Extraction and Indexing
Extracts coordinates from complex IDs using B-tree indexing and Godot-style node addressing.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import hashlib
import bisect


@dataclass
class NodeCoordinate:
    """Represents a node coordinate in the indexing system."""
    node_id: str
    primary_key: int
    virtual_address: str
    x: float
    y: float
    z: float
    metadata: Dict[str, Any]


class BTreeNode:
    """B-tree node for indexing."""
    
    def __init__(self, degree: int = 3):
        self.degree = degree
        self.keys: List[int] = []
        self.children: List['BTreeNode'] = []
        self.values: List[NodeCoordinate] = []
        self.is_leaf = True
    
    def is_full(self) -> bool:
        return len(self.keys) >= 2 * self.degree - 1


class BTree:
    """B-tree implementation for node indexing."""
    
    def __init__(self, degree: int = 3):
        self.root = BTreeNode(degree)
        self.degree = degree
    
    def insert(self, key: int, value: NodeCoordinate):
        """Insert a key-value pair into the B-tree."""
        root = self.root
        
        if root.is_full():
            new_root = BTreeNode(self.degree)
            new_root.children.append(root)
            self._split_child(new_root, 0)
            self.root = new_root
            self._insert_non_full(new_root, key, value)
        else:
            self._insert_non_full(root, key, value)
    
    def _insert_non_full(self, node: BTreeNode, key: int, value: NodeCoordinate):
        """Insert into a non-full node."""
        i = len(node.keys) - 1
        
        if node.is_leaf:
            # Insert key and value
            node.keys.append(0)
            node.values.append(None)
            
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                node.values[i + 1] = node.values[i]
                i -= 1
            
            node.keys[i + 1] = key
            node.values[i + 1] = value
        else:
            # Find child to insert into
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            
            if node.children[i].is_full():
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            
            self._insert_non_full(node.children[i], key, value)
    
    def _split_child(self, parent: BTreeNode, index: int):
        """Split a full child node."""
        degree = self.degree
        child = parent.children[index]
        new_node = BTreeNode(degree)
        
        # Move keys and values to new node
        mid_index = degree - 1
        new_node.keys = child.keys[degree:]
        new_node.values = child.values[degree:]
        child.keys = child.keys[:mid_index]
        child.values = child.values[:mid_index]
        
        # Move children if not leaf
        if not child.is_leaf:
            new_node.children = child.children[degree:]
            child.children = child.children[:degree]
            new_node.is_leaf = False
        
        # Insert mid key into parent
        parent.keys.insert(index, child.keys[mid_index])
        parent.values.insert(index, child.values[mid_index])
        parent.children.insert(index + 1, new_node)
        
        # Remove mid from child
        child.keys.pop()
        child.values.pop()
    
    def search(self, key: int) -> Optional[NodeCoordinate]:
        """Search for a key in the B-tree."""
        return self._search(self.root, key)
    
    def _search(self, node: BTreeNode, key: int) -> Optional[NodeCoordinate]:
        """Recursive search helper."""
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        
        if i < len(node.keys) and key == node.keys[i]:
            return node.values[i]
        
        if node.is_leaf:
            return None
        
        return self._search(node.children[i], key)
    
    def range_search(self, min_key: int, max_key: int) -> List[NodeCoordinate]:
        """Search for keys in a range."""
        results = []
        self._range_search(self.root, min_key, max_key, results)
        return results
    
    def _range_search(self, node: BTreeNode, min_key: int, max_key: int, results: List):
        """Recursive range search helper."""
        i = 0
        while i < len(node.keys) and node.keys[i] < min_key:
            i += 1
        
        while i < len(node.keys) and node.keys[i] <= max_key:
            if not node.is_leaf:
                self._range_search(node.children[i], min_key, max_key, results)
            results.append(node.values[i])
            i += 1
        
        if not node.is_leaf and i < len(node.children):
            self._range_search(node.children[i], min_key, max_key, results)


class CoordinateExtractor:
    """
    Extracts coordinates from complex node IDs using B-tree indexing
    and Godot-style node addressing with virtual address matching.
    """
    
    def __init__(self, btree_degree: int = 3):
        """
        Initialize the Coordinate Extractor.
        
        Args:
            btree_degree: Degree for B-tree indexing
        """
        self.btree = BTree(btree_degree)
        self.node_registry: Dict[str, NodeCoordinate] = {}
        self.godot_node_paths: Dict[str, str] = {}
        self.overhash_maps: Dict[str, List[str]] = {}
        
        # Coordinate space parameters
        self.coordinate_space_size = 1000.0
    
    def extract_coordinates(self, node_id: str) -> NodeCoordinate:
        """
        Extract coordinates from a complex node ID.
        
        Args:
            node_id: Complex node identifier
            
        Returns:
            NodeCoordinate object with extracted information
        """
        # Generate primary key from node ID
        primary_key = self._generate_primary_key(node_id)
        
        # Generate virtual address (Godot-style)
        virtual_address = self._generate_virtual_address(node_id)
        
        # Extract integer range
        int_range = self._extract_integer_range(node_id)
        
        # Generate 3D coordinates
        x, y, z = self._generate_3d_coordinates(node_id, int_range)
        
        # Create node coordinate
        coordinate = NodeCoordinate(
            node_id=node_id,
            primary_key=primary_key,
            virtual_address=virtual_address,
            x=x,
            y=y,
            z=z,
            metadata={
                'int_range': int_range,
                'hash': hashlib.md5(node_id.encode()).hexdigest()
            }
        )
        
        # Insert into B-tree
        self.btree.insert(primary_key, coordinate)
        
        # Register node
        self.node_registry[node_id] = coordinate
        
        return coordinate
    
    def _generate_primary_key(self, node_id: str) -> int:
        """
        Generate primary key from node ID.
        
        Args:
            node_id: Node identifier
            
        Returns:
            Integer primary key
        """
        # Use hash to generate primary key
        hash_value = hashlib.sha256(node_id.encode()).hexdigest()
        return int(hash_value[:16], 16)
    
    def _generate_virtual_address(self, node_id: str) -> str:
        """
        Generate virtual address in Godot-style node path format.
        
        Args:
            node_id: Node identifier
            
        Returns:
            Virtual address string (e.g., "/root/node1/child2")
        """
        # Parse node ID to create path
        parts = node_id.replace('_', '/').split('/')
        
        # Add root and create path
        path_parts = ['root'] + parts
        virtual_address = '/' + '/'.join(path_parts)
        
        # Store Godot-style path
        self.godot_node_paths[node_id] = virtual_address
        
        return virtual_address
    
    def _extract_integer_range(self, node_id: str) -> Tuple[int, int]:
        """
        Extract integer range from node ID.
        
        Args:
            node_id: Node identifier
            
        Returns:
            Tuple of (min, max) integer range
        """
        # Extract numbers from node ID
        numbers = []
        for char in node_id:
            if char.isdigit():
                numbers.append(int(char))
        
        if numbers:
            min_val = min(numbers)
            max_val = max(numbers)
            return (min_val, max_val)
        else:
            # Generate from hash if no numbers
            hash_val = hash(node_id)
            return (abs(hash_val) % 100, abs(hash_val) % 1000)
    
    def _generate_3d_coordinates(self, node_id: str, int_range: Tuple[int, int]) -> Tuple[float, float, float]:
        """
        Generate 3D coordinates from node ID and integer range.
        
        Args:
            node_id: Node identifier
            int_range: Integer range tuple
            
        Returns:
            Tuple of (x, y, z) coordinates
        """
        # Use hash for coordinate generation
        hash_val = hashlib.md5(node_id.encode()).hexdigest()
        
        # Convert to coordinates
        x = (int(hash_val[:8], 16) % 1000) / 1000.0 * self.coordinate_space_size
        y = (int(hash_val[8:16], 16) % 1000) / 1000.0 * self.coordinate_space_size
        z = (int(hash_val[16:24], 16) % 1000) / 1000.0 * self.coordinate_space_size
        
        # Apply integer range influence
        min_val, max_val = int_range
        x = x * (min_val / 100.0 + 0.5)
        y = y * (max_val / 1000.0 + 0.5)
        
        return (x, y, z)
    
    def get_node_by_primary_key(self, primary_key: int) -> Optional[NodeCoordinate]:
        """
        Get node by primary key using B-tree search.
        
        Args:
            primary_key: Primary key to search for
            
        Returns:
            NodeCoordinate if found, None otherwise
        """
        return self.btree.search(primary_key)
    
    def get_nodes_in_range(self, min_key: int, max_key: int) -> List[NodeCoordinate]:
        """
        Get nodes within a primary key range.
        
        Args:
            min_key: Minimum primary key
            max_key: Maximum primary key
            
        Returns:
            List of NodeCoordinate objects
        """
        return self.btree.range_search(min_key, max_key)
    
    def get_godot_node_path(self, node_id: str) -> Optional[str]:
        """
        Get Godot-style node path for a node ID.
        
        Args:
            node_id: Node identifier
            
        Returns:
            Virtual address string or None
        """
        return self.godot_node_paths.get(node_id)
    
    def find_nearby_nodes(self, node_id: str, radius: float = 100.0) -> List[NodeCoordinate]:
        """
        Find nodes within a spatial radius of a given node.
        
        Args:
            node_id: Reference node ID
            radius: Search radius
            
        Returns:
            List of nearby NodeCoordinate objects
        """
        if node_id not in self.node_registry:
            return []
        
        ref_coord = self.node_registry[node_id]
        nearby = []
        
        for coord in self.node_registry.values():
            if coord.node_id == node_id:
                continue
            
            # Calculate distance
            distance = np.sqrt(
                (coord.x - ref_coord.x) ** 2 +
                (coord.y - ref_coord.y) ** 2 +
                (coord.z - ref_coord.z) ** 2
            )
            
            if distance <= radius:
                nearby.append(coord)
        
        return nearby
    
    def create_overhash_map(self, node_id: str, related_nodes: List[str]):
        """
        Create overhash map for a node, linking to related nodes.
        
        Args:
            node_id: Primary node ID
            related_nodes: List of related node IDs
        """
        self.overhash_maps[node_id] = related_nodes
    
    def get_overhash_map(self, node_id: str) -> List[str]:
        """
        Get överhash map for a node.
        
        Args:
            node_id: Node identifier
            
        Returns:
            List of related node IDs
        """
        return self.overhash_maps.get(node_id, [])
    
    def get_coordinate_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the coordinate system.
        
        Returns:
            Dictionary containing coordinate system statistics
        """
        if not self.node_registry:
            return {
                'total_nodes': 0,
                'coordinate_space_size': self.coordinate_space_size
            }
        
        coords = list(self.node_registry.values())
        x_coords = [c.x for c in coords]
        y_coords = [c.y for c in coords]
        z_coords = [c.z for c in coords]
        
        return {
            'total_nodes': len(coords),
            'coordinate_space_size': self.coordinate_space_size,
            'x_range': (min(x_coords), max(x_coords)),
            'y_range': (min(y_coords), max(y_coords)),
            'z_range': (min(z_coords), max(z_coords)),
            'centroid': (
                np.mean(x_coords),
                np.mean(y_coords),
                np.mean(z_coords)
            )
        }
