"""
Cortex Blocks - User Mesh Cortex Binary Blocks Storage
Stores and manages binary blocks for user experiences, images, video, actions, word data, and language.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import hashlib
import pickle


class BlockType(Enum):
    """Types of cortex blocks."""
    EXPERIENCE = "experience"
    IMAGE = "image"
    VIDEO = "video"
    ACTION = "action"
    WORD_DATA = "word_data"
    LANGUAGE = "language"
    CODE_INTERPRETATION = "code_interpretation"
    DECISION_INTERACTION = "decision_interaction"
    SPATIAL = "spatial"
    TEMPORAL = "temporal"


@dataclass
class CortexBlock:
    """Represents a cortex binary block."""
    block_id: str
    block_type: BlockType
    binary_data: bytes
    metadata: Dict[str, any]
    timestamp: float
    access_count: int
    last_accessed: float
    connections: List[str]  # Connected block IDs
    activation_level: float  # 0-1


class CortexBlocks:
    """
    Manages user mesh cortex binary blocks storage.
    Handles storage and retrieval of various data types as binary blocks.
    """
    
    def __init__(self, max_blocks: int = 10_000_000):
        """
        Initialize the Cortex Blocks storage.
        
        Args:
            max_blocks: Maximum number of blocks to store
        """
        self.max_blocks = max_blocks
        
        # Block storage
        self.blocks: Dict[str, CortexBlock] = {}
        
        # Block type indices
        self.blocks_by_type: Dict[BlockType, List[str]] = {}
        
        # Connection graph
        self.block_connections: Dict[str, List[str]] = {}
        
        # Access tracking
        self.access_frequency: Dict[str, int] = {}
        
        # Compression settings
        self.use_compression = True
        self.compression_threshold = 1024  # Compress blocks larger than 1KB
    
    def create_block(
        self,
        block_type: BlockType,
        data: Union[bytes, np.ndarray, Dict, List, str],
        metadata: Optional[Dict[str, any]] = None
    ) -> CortexBlock:
        """
        Create a new cortex block.
        
        Args:
            block_type: Type of block
            data: Data to store (will be converted to binary)
            metadata: Additional metadata
            
        Returns:
            CortexBlock object
        """
        # Convert data to binary
        binary_data = self._convert_to_binary(data)
        
        # Compress if needed
        if self.use_compression and len(binary_data) > self.compression_threshold:
            binary_data = self._compress_data(binary_data)
        
        # Generate block ID
        block_id = self._generate_block_id(block_type, binary_data)
        
        # Create block
        block = CortexBlock(
            block_id=block_id,
            block_type=block_type,
            binary_data=binary_data,
            metadata=metadata or {},
            timestamp=datetime.now().timestamp(),
            access_count=0,
            last_accessed=datetime.now().timestamp(),
            connections=[],
            activation_level=0.5
        )
        
        # Store block
        self.blocks[block_id] = block
        
        # Update type index
        if block_type not in self.blocks_by_type:
            self.blocks_by_type[block_type] = []
        self.blocks_by_type[block_type].append(block_id)
        
        # Check capacity
        if len(self.blocks) > self.max_blocks:
            self._evict_oldest_blocks()
        
        return block
    
    def _convert_to_binary(self, data: Union[bytes, np.ndarray, Dict, List, str]) -> bytes:
        """
        Convert various data types to binary format.
        
        Args:
            data: Data to convert
            
        Returns:
            Binary data
        """
        if isinstance(data, bytes):
            return data
        elif isinstance(data, np.ndarray):
            return data.tobytes()
        elif isinstance(data, (Dict, List)):
            return pickle.dumps(data)
        elif isinstance(data, str):
            return data.encode('utf-8')
        else:
            return pickle.dumps(data)
    
    def _compress_data(self, data: bytes) -> bytes:
        """
        Compress binary data.
        
        Args:
            data: Data to compress
            
        Returns:
            Compressed data
        """
        # Simple compression simulation (in real implementation, use zlib/lzma)
        return data  # Placeholder
    
    def _generate_block_id(self, block_type: BlockType, data: bytes) -> str:
        """
        Generate unique block ID.
        
        Args:
            block_type: Type of block
            data: Block data
            
        Returns:
            Unique block ID
        """
        hash_value = hashlib.sha256(data).hexdigest()[:16]
        return f"{block_type.value}_{hash_value}"
    
    def get_block(self, block_id: str) -> Optional[CortexBlock]:
        """
        Retrieve a cortex block.
        
        Args:
            block_id: Block ID to retrieve
            
        Returns:
            CortexBlock object or None
        """
        block = self.blocks.get(block_id)
        
        if block:
            # Update access tracking
            block.access_count += 1
            block.last_accessed = datetime.now().timestamp()
            self.access_frequency[block_id] = self.access_frequency.get(block_id, 0) + 1
        
        return block
    
    def retrieve_data(self, block_id: str) -> Optional[any]:
        """
        Retrieve and decode data from a block.
        
        Args:
            block_id: Block ID to retrieve from
            
        Returns:
            Decoded data or None
        """
        block = self.get_block(block_id)
        
        if not block:
            return None
        
        return self._decode_binary(block.binary_data, block.metadata)
    
    def _decode_binary(self, binary_data: bytes, metadata: Dict) -> any:
        """
        Decode binary data based on metadata.
        
        Args:
            binary_data: Binary data to decode
            metadata: Block metadata
            
        Returns:
            Decoded data
        """
        data_type = metadata.get('data_type', 'raw')
        
        if data_type == 'numpy_array':
            shape = metadata.get('shape')
            dtype = metadata.get('dtype', 'float32')
            return np.frombuffer(binary_data, dtype=dtype).reshape(shape)
        elif data_type == 'pickle':
            return pickle.loads(binary_data)
        elif data_type == 'string':
            return binary_data.decode('utf-8')
        else:
            return binary_data
    
    def connect_blocks(self, block_id1: str, block_id2: str, strength: float = 0.5):
        """
        Create a connection between two blocks.
        
        Args:
            block_id1: First block ID
            block_id2: Second block ID
            strength: Connection strength (0-1)
        """
        if block_id1 not in self.blocks or block_id2 not in self.blocks:
            return
        
        block1 = self.blocks[block_id1]
        block2 = self.blocks[block_id2]
        
        # Add connections
        if block_id2 not in block1.connections:
            block1.connections.append(block_id2)
        if block_id1 not in block2.connections:
            block2.connections.append(block_id1)
        
        # Update connection graph
        if block_id1 not in self.block_connections:
            self.block_connections[block_id1] = []
        if block_id2 not in self.block_connections:
            self.block_connections[block_id2] = []
        
        self.block_connections[block_id1].append(block_id2)
        self.block_connections[block_id2].append(block_id1)
    
    def activate_block(self, block_id: str, activation: float):
        """
        Set activation level for a block.
        
        Args:
            block_id: Block ID to activate
            activation: Activation level (0-1)
        """
        if block_id in self.blocks:
            self.blocks[block_id].activation_level = min(max(activation, 0.0), 1.0)
            
            # Propagate activation to connected blocks
            for connected_id in self.blocks[block_id].connections:
                if connected_id in self.blocks:
                    connected_block = self.blocks[connected_id]
                    connected_block.activation_level = min(
                        connected_block.activation_level + activation * 0.3,
                        1.0
                    )
    
    def get_blocks_by_type(self, block_type: BlockType) -> List[CortexBlock]:
        """
        Get all blocks of a specific type.
        
        Args:
            block_type: Type of blocks to retrieve
            
        Returns:
            List of CortexBlock objects
        """
        block_ids = self.blocks_by_type.get(block_type, [])
        return [self.blocks[bid] for bid in block_ids if bid in self.blocks]
    
    def find_similar_blocks(self, block_id: str, threshold: float = 0.8) -> List[str]:
        """
        Find blocks similar to the given block.
        
        Args:
            block_id: Reference block ID
            threshold: Similarity threshold
            
        Returns:
            List of similar block IDs
        """
        if block_id not in self.blocks:
            return []
        
        reference_block = self.blocks[block_id]
        similar_blocks = []
        
        for other_id, other_block in self.blocks.items():
            if other_id == block_id:
                continue
            
            # Calculate similarity based on type and metadata
            if reference_block.block_type == other_block.block_type:
                similarity = self._calculate_similarity(reference_block, other_block)
                if similarity >= threshold:
                    similar_blocks.append(other_id)
        
        return similar_blocks
    
    def _calculate_similarity(self, block1: CortexBlock, block2: CortexBlock) -> float:
        """
        Calculate similarity between two blocks.
        
        Args:
            block1: First block
            block2: Second block
            
        Returns:
            Similarity score (0-1)
        """
        # Simple similarity based on metadata
        metadata1_keys = set(block1.metadata.keys())
        metadata2_keys = set(block2.metadata.keys())
        
        shared_keys = metadata1_keys & metadata2_keys
        total_keys = metadata1_keys | metadata2_keys
        
        if not total_keys:
            return 0.0
        
        key_similarity = len(shared_keys) / len(total_keys)
        
        # Add activation similarity
        activation_similarity = 1.0 - abs(block1.activation_level - block2.activation_level)
        
        return (key_similarity * 0.7) + (activation_similarity * 0.3)
    
    def _evict_oldest_blocks(self, count: int = 100):
        """
        Evict oldest blocks to maintain capacity.
        
        Args:
            count: Number of blocks to evict
        """
        # Sort by last accessed time
        sorted_blocks = sorted(
            self.blocks.values(),
            key=lambda b: b.last_accessed
        )
        
        # Evict oldest blocks
        for block in sorted_blocks[:count]:
            self._remove_block(block.block_id)
    
    def _remove_block(self, block_id: str):
        """
        Remove a block from storage.
        
        Args:
            block_id: Block ID to remove
        """
        if block_id not in self.blocks:
            return
        
        block = self.blocks[block_id]
        
        # Remove from type index
        if block.block_type in self.blocks_by_type:
            self.blocks_by_type[block.block_type].remove(block_id)
        
        # Remove connections
        for connected_id in block.connections:
            if connected_id in self.blocks:
                self.blocks[connected_id].connections.remove(block_id)
        
        # Remove from connection graph
        if block_id in self.block_connections:
            del self.block_connections[block_id]
        
        # Remove block
        del self.blocks[block_id]
        if block_id in self.access_frequency:
            del self.access_frequency[block_id]
    
    def get_storage_statistics(self) -> Dict[str, any]:
        """
        Get statistics about block storage.
        
        Returns:
            Dictionary containing storage statistics
        """
        total_size = sum(len(block.binary_data) for block in self.blocks.values())
        
        type_counts = {
            bt.value: len(self.blocks_by_type.get(bt, []))
            for bt in BlockType
        }
        
        avg_activation = np.mean([b.activation_level for b in self.blocks.values()]) if self.blocks else 0.0
        
        return {
            'total_blocks': len(self.blocks),
            'max_blocks': self.max_blocks,
            'total_size_bytes': total_size,
            'avg_block_size': total_size / len(self.blocks) if self.blocks else 0,
            'blocks_by_type': type_counts,
            'avg_activation': avg_activation,
            'total_connections': sum(len(conns) for conns in self.block_connections.values()),
            'use_compression': self.use_compression
        }
    
    def clear_old_blocks(self, max_age_seconds: float = 86400):
        """
        Clear blocks older than specified age.
        
        Args:
            max_age_seconds: Maximum age in seconds (default 24 hours)
        """
        current_time = datetime.now().timestamp()
        
        blocks_to_remove = [
            block_id for block_id, block in self.blocks.items()
            if current_time - block.last_accessed > max_age_seconds
        ]
        
        for block_id in blocks_to_remove:
            self._remove_block(block_id)
