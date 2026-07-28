"""
User Knowledge Base - Main User Knowledge Base System
Integrates all knowledge base components for comprehensive user modeling.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, date
from .age_estimator import AgeEstimator, AgeEstimate
from .cortex_blocks import CortexBlocks, CortexBlock, BlockType
from .node_manager import NodeManager, NodeEntry, NodeType, NodeStatus
from .data_type_handlers import DataTypeHandlers, DataType, ProcessedData
from .calibration_system import CalibrationSystem, CalibrationResult
from ..social_media.format_handlers import SocialMediaFormatHandlers
from ..social_media.sha_sharing import SHASharingSystem
from ..social_media.chat_conversation import ChatConversationManager
from ..social_media.device_permissions import DevicePermissionManager
from ..social_media.broadband_handler import BroadbandHandler
from ..social_media.streaming_formats import StreamingFormatHandler


@dataclass
class KnowledgeBaseSnapshot:
    """Represents a snapshot of the knowledge base state."""
    timestamp: float
    age_estimate: Optional[AgeEstimate]
    total_nodes: int
    total_blocks: int
    node_utilization: float
    block_utilization: float
    calibration_history: List[CalibrationResult]


class UserKnowledgeBase:
    """
    Main user knowledge base system.
    Integrates age estimation, cortex blocks, node management, data handling, and calibration.
    """
    
    def __init__(self, date_of_birth: Optional[date] = None):
        """
        Initialize the User Knowledge Base.
        
        Args:
            date_of_birth: User's date of birth (optional)
        """
        # Initialize components
        self.age_estimator = AgeEstimator()
        self.cortex_blocks = CortexBlocks(max_blocks=10_000_000)
        self.node_manager = NodeManager(target_node_count=9_400_000)
        self.data_handlers = DataTypeHandlers()
        self.calibration_system = CalibrationSystem()
        
        # Initialize social media components
        self.format_handlers = SocialMediaFormatHandlers()
        self.sha_sharing = SHASharingSystem()
        self.chat_manager = ChatConversationManager()
        self.permission_manager = DevicePermissionManager()
        self.broadband_handler = BroadbandHandler()
        self.streaming_handler = StreamingFormatHandler()
        
        # Initialize age estimate if DOB provided
        if date_of_birth:
            self.age_estimator.estimate_from_dob(date_of_birth)
        
        # Tracking
        self.snapshots: List[KnowledgeBaseSnapshot] = []
        self.tracking_interval = 3600  # 1 hour
        self.last_snapshot_time = 0.0
        
        # Readjustment tracking
        self.readjustment_history: List[Dict] = []
        self.performance_metrics: Dict[str, float] = {}
    
    def initialize_from_dob(self, date_of_birth: date):
        """
        Initialize knowledge base from date of birth.
        
        Args:
            date_of_birth: User's date of birth
        """
        estimate = self.age_estimator.estimate_from_dob(date_of_birth)
        
        # Adjust node manager target based on estimate
        self.node_manager.adjust_target_count(estimate.estimated_node_count)
        
        # Adjust cortex blocks capacity
        self.cortex_blocks.max_blocks = estimate.estimated_node_count
        
        print(f"Initialized knowledge base for age {estimate.estimated_age:.1f} years "
              f"with {estimate.estimated_node_count} nodes")
    
    def add_experience(
        self,
        experience_data: Union[Dict, str, bytes],
        experience_type: str = "generic",
        metadata: Optional[Dict] = None
    ) -> Tuple[NodeEntry, CortexBlock]:
        """
        Add an experience to the knowledge base.
        
        Args:
            experience_data: Experience data
            experience_type: Type of experience
            metadata: Additional metadata
            
        Returns:
            Tuple of (NodeEntry, CortexBlock)
        """
        # Process data
        data_type = self._map_experience_to_data_type(experience_type)
        processed = self.data_handlers.process_data(data_type, experience_data, metadata)
        
        # Create cortex block
        block = self.cortex_blocks.create_block(
            block_type=BlockType.EXPERIENCE,
            data=processed.processed_data,
            metadata={
                **processed.metadata,
                'data_type': data_type.value,
                'features': processed.features
            }
        )
        
        # Create node
        node = self.node_manager.create_node(
            node_type=NodeType.EXPERIENCE,
            data={
                'experience_type': experience_type,
                'processed_data': processed.processed_data,
                'features': processed.features
            },
            metadata=metadata or {}
        )
        
        # Connect block and node
        self._connect_block_and_node(block.block_id, node.node_id)
        
        # Track for readjustment
        self._track_addition('experience', node, block)
        
        return node, block
    
    def add_image(
        self,
        image_data: Union[np.ndarray, bytes],
        metadata: Optional[Dict] = None
    ) -> Tuple[NodeEntry, CortexBlock]:
        """
        Add image data to knowledge base.
        
        Args:
            image_data: Image data
            metadata: Additional metadata
            
        Returns:
            Tuple of (NodeEntry, CortexBlock)
        """
        processed = self.data_handlers.process_data(DataType.IMAGE, image_data, metadata)
        
        block = self.cortex_blocks.create_block(
            block_type=BlockType.IMAGE,
            data=processed.processed_data,
            metadata={
                **processed.metadata,
                'data_type': DataType.IMAGE.value,
                'features': processed.features
            }
        )
        
        node = self.node_manager.create_node(
            node_type=NodeType.KNOWLEDGE,
            data={
                'type': 'image',
                'features': processed.features
            },
            metadata=metadata or {}
        )
        
        self._connect_block_and_node(block.block_id, node.node_id)
        self._track_addition('image', node, block)
        
        return node, block
    
    def add_video(
        self,
        video_data: Union[Dict, bytes],
        metadata: Optional[Dict] = None
    ) -> Tuple[NodeEntry, CortexBlock]:
        """
        Add video data to knowledge base.
        
        Args:
            video_data: Video data
            metadata: Additional metadata
            
        Returns:
            Tuple of (NodeEntry, CortexBlock)
        """
        processed = self.data_handlers.process_data(DataType.VIDEO, video_data, metadata)
        
        block = self.cortex_blocks.create_block(
            block_type=BlockType.VIDEO,
            data=processed.processed_data,
            metadata={
                **processed.metadata,
                'data_type': DataType.VIDEO.value,
                'features': processed.features
            }
        )
        
        node = self.node_manager.create_node(
            node_type=NodeType.KNOWLEDGE,
            data={
                'type': 'video',
                'features': processed.features
            },
            metadata=metadata or {}
        )
        
        self._connect_block_and_node(block.block_id, node.node_id)
        self._track_addition('video', node, block)
        
        return node, block
    
    def add_word_data(
        self,
        word_data: Union[str, Dict],
        metadata: Optional[Dict] = None
    ) -> Tuple[NodeEntry, CortexBlock]:
        """
        Add word/linguistic data to knowledge base.
        
        Args:
            word_data: Word data
            metadata: Additional metadata
            
        Returns:
            Tuple of (NodeEntry, CortexBlock)
        """
        processed = self.data_handlers.process_data(DataType.WORD_DATA, word_data, metadata)
        
        block = self.cortex_blocks.create_block(
            block_type=BlockType.WORD_DATA,
            data=processed.processed_data,
            metadata={
                **processed.metadata,
                'data_type': DataType.WORD_DATA.value,
                'features': processed.features
            }
        )
        
        node = self.node_manager.create_node(
            node_type=NodeType.KNOWLEDGE,
            data={
                'type': 'word',
                'features': processed.features
            },
            metadata=metadata or {}
        )
        
        self._connect_block_and_node(block.block_id, node.node_id)
        self._track_addition('word', node, block)
        
        return node, block
    
    def add_language_data(
        self,
        language_data: Union[str, Dict],
        metadata: Optional[Dict] = None
    ) -> Tuple[NodeEntry, CortexBlock]:
        """
        Add language data to knowledge base.
        
        Args:
            language_data: Language data
            metadata: Additional metadata
            
        Returns:
            Tuple of (NodeEntry, CortexBlock)
        """
        processed = self.data_handlers.process_data(DataType.LANGUAGE, language_data, metadata)
        
        block = self.cortex_blocks.create_block(
            block_type=BlockType.LANGUAGE,
            data=processed.processed_data,
            metadata={
                **processed.metadata,
                'data_type': DataType.LANGUAGE.value,
                'features': processed.features
            }
        )
        
        node = self.node_manager.create_node(
            node_type=NodeType.KNOWLEDGE,
            data={
                'type': 'language',
                'features': processed.features
            },
            metadata=metadata or {}
        )
        
        self._connect_block_and_node(block.block_id, node.node_id)
        self._track_addition('language', node, block)
        
        return node, block
    
    def add_action(
        self,
        action_data: Union[str, Dict],
        metadata: Optional[Dict] = None
    ) -> Tuple[NodeEntry, CortexBlock]:
        """
        Add action data to knowledge base.
        
        Args:
            action_data: Action data
            metadata: Additional metadata
            
        Returns:
            Tuple of (NodeEntry, CortexBlock)
        """
        processed = self.data_handlers.process_data(DataType.ACTION, action_data, metadata)
        
        block = self.cortex_blocks.create_block(
            block_type=BlockType.ACTION,
            data=processed.processed_data,
            metadata={
                **processed.metadata,
                'data_type': DataType.ACTION.value,
                'features': processed.features
            }
        )
        
        node = self.node_manager.create_node(
            node_type=NodeType.SKILL,
            data={
                'type': 'action',
                'features': processed.features
            },
            metadata=metadata or {}
        )
        
        self._connect_block_and_node(block.block_id, node.node_id)
        self._track_addition('action', node, block)
        
        return node, block
    
    def add_code_interpretation(
        self,
        code_data: Union[str, Dict],
        metadata: Optional[Dict] = None
    ) -> Tuple[NodeEntry, CortexBlock]:
        """
        Add code interpretation data to knowledge base.
        
        Args:
            code_data: Code data
            metadata: Additional metadata
            
        Returns:
            Tuple of (NodeEntry, CortexBlock)
        """
        processed = self.data_handlers.process_data(DataType.CODE_INTERPRETATION, code_data, metadata)
        
        block = self.cortex_blocks.create_block(
            block_type=BlockType.CODE_INTERPRETATION,
            data=processed.processed_data,
            metadata={
                **processed.metadata,
                'data_type': DataType.CODE_INTERPRETATION.value,
                'features': processed.features
            }
        )
        
        node = self.node_manager.create_node(
            node_type=NodeType.SKILL,
            data={
                'type': 'code',
                'features': processed.features
            },
            metadata=metadata or {}
        )
        
        self._connect_block_and_node(block.block_id, node.node_id)
        self._track_addition('code', node, block)
        
        return node, block
    
    def add_decision_interaction(
        self,
        decision_data: Union[str, Dict],
        metadata: Optional[Dict] = None
    ) -> Tuple[NodeEntry, CortexBlock]:
        """
        Add decision interaction data to knowledge base.
        
        Args:
            decision_data: Decision data
            metadata: Additional metadata
            
        Returns:
            Tuple of (NodeEntry, CortexBlock)
        """
        processed = self.data_handlers.process_data(DataType.DECISION_INTERACTION, decision_data, metadata)
        
        block = self.cortex_blocks.create_block(
            block_type=BlockType.DECISION_INTERACTION,
            data=processed.processed_data,
            metadata={
                **processed.metadata,
                'data_type': DataType.DECISION_INTERACTION.value,
                'features': processed.features
            }
        )
        
        node = self.node_manager.create_node(
            node_type=NodeType.DECISION,
            data={
                'type': 'decision',
                'features': processed.features
            },
            metadata=metadata or {}
        )
        
        self._connect_block_and_node(block.block_id, node.node_id)
        self._track_addition('decision', node, block)
        
        return node, block
    
    def _map_experience_to_data_type(self, experience_type: str) -> DataType:
        """Map experience type to data type."""
        mapping = {
            'image': DataType.IMAGE,
            'video': DataType.VIDEO,
            'action': DataType.ACTION,
            'word': DataType.WORD_DATA,
            'language': DataType.LANGUAGE,
            'code': DataType.CODE_INTERPRETATION,
            'decision': DataType.DECISION_INTERACTION
        }
        return mapping.get(experience_type.lower(), DataType.TEXT)
    
    def _connect_block_and_node(self, block_id: str, node_id: str):
        """Connect a cortex block to a node."""
        # Store reference in metadata
        if block_id in self.cortex_blocks.blocks:
            self.cortex_blocks.blocks[block_id].metadata['linked_node'] = node_id
        if node_id in self.node_manager.nodes:
            self.node_manager.nodes[node_id].metadata['linked_block'] = block_id
    
    def _track_addition(self, data_type: str, node: NodeEntry, block: CortexBlock):
        """Track data addition for readjustment."""
        self.readjustment_history.append({
            'timestamp': datetime.now().timestamp(),
            'data_type': data_type,
            'node_id': node.node_id,
            'block_id': block.block_id,
            'node_weight': node.weight,
            'block_size': len(block.binary_data)
        })
        
        if len(self.readjustment_history) > 10000:
            self.readjustment_history.pop(0)
    
    def calibrate_from_observation(
        self,
        observed_age: Optional[float] = None,
        observed_node_count: Optional[int] = None,
        behavior_indicators: Optional[Dict[str, float]] = None
    ) -> CalibrationResult:
        """
        Calibrate knowledge base from observed data.
        
        Args:
            observed_age: Observed actual age
            observed_node_count: Observed actual node count
            behavior_indicators: Behavior indicators
            
        Returns:
            CalibrationResult object
        """
        result = self.calibration_system.calibrate_from_observed_data(
            self.age_estimator,
            observed_age,
            observed_node_count,
            behavior_indicators
        )
        
        # Update node manager target if node count changed
        if result.calibrated_estimate:
            self.node_manager.adjust_target_count(
                result.calibrated_estimate.estimated_node_count
            )
            self.cortex_blocks.max_blocks = result.calibrated_estimate.estimated_node_count
        
        return result
    
    def auto_readjust(self):
        """Automatically readjust based on tracking data."""
        current_estimate = self.age_estimator.get_current_estimate()
        
        if not current_estimate:
            return
        
        # Check if calibration is needed
        if self.calibration_system.should_recalibrate(self.age_estimator):
            # Analyze recent additions
            recent_additions = [
                entry for entry in self.readjustment_history
                if datetime.now().timestamp() - entry['timestamp'] < 3600
            ]
            
            if recent_additions:
                # Calculate growth rate
                growth_rate = len(recent_additions) / 3600  # additions per second
                
                # Adjust model parameters
                self.calibration_system.adjust_model_parameters({
                    'node_growth_rate': growth_rate * 86400  # per day
                })
                
                # Recalibrate
                self.calibrate_from_observation()
    
    def take_snapshot(self) -> KnowledgeBaseSnapshot:
        """
        Take a snapshot of current knowledge base state.
        
        Returns:
            KnowledgeBaseSnapshot object
        """
        snapshot = KnowledgeBaseSnapshot(
            timestamp=datetime.now().timestamp(),
            age_estimate=self.age_estimator.get_current_estimate(),
            total_nodes=len(self.node_manager.nodes),
            total_blocks=len(self.cortex_blocks.blocks),
            node_utilization=len(self.node_manager.nodes) / self.node_manager.target_node_count,
            block_utilization=len(self.cortex_blocks.blocks) / self.cortex_blocks.max_blocks,
            calibration_history=self.calibration_system.get_recent_calibrations(10)
        )
        
        self.snapshots.append(snapshot)
        self.last_snapshot_time = snapshot.timestamp
        
        if len(self.snapshots) > 100:
            self.snapshots.pop(0)
        
        return snapshot
    
    def get_comprehensive_status(self) -> Dict[str, any]:
        """
        Get comprehensive status of knowledge base.
        
        Returns:
            Dictionary containing all status information
        """
        return {
            'age_estimation': self.age_estimator.get_estimation_statistics(),
            'node_management': self.node_manager.get_node_statistics(),
            'cortex_blocks': self.cortex_blocks.get_storage_statistics(),
            'data_processing': self.data_handlers.get_processing_statistics(),
            'calibration': self.calibration_system.get_calibration_statistics(),
            'tracking': {
                'total_additions': len(self.readjustment_history),
                'snapshots_count': len(self.snapshots),
                'last_snapshot_time': self.last_snapshot_time
            },
            'performance': self.performance_metrics
        }
    
    def find_related_knowledge(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Find knowledge related to a query.
        
        Args:
            query: Query string
            limit: Maximum results
            
        Returns:
            List of related knowledge items
        """
        # Simple keyword matching (in real implementation, use semantic search)
        results = []
        
        for node_id, node in self.node_manager.nodes.items():
            if node.status != NodeStatus.ACTIVE:
                continue
            
            # Check if query matches node data
            node_data_str = str(node.data).lower()
            if query.lower() in node_data_str:
                results.append({
                    'node_id': node_id,
                    'node_type': node.node_type.value,
                    'data': node.data,
                    'activation': node.activation,
                    'weight': node.weight
                })
            
            if len(results) >= limit:
                break
        
        return results
    
    def activate_knowledge(self, node_id: str, activation: float):
        """
        Activate specific knowledge node.
        
        Args:
            node_id: Node ID to activate
            activation: Activation level (0-1)
        """
        self.node_manager.activate_node(node_id, activation)
        
        # Also activate linked block
        node = self.node_manager.get_node(node_id)
        if node and 'linked_block' in node.metadata:
            block_id = node.metadata['linked_block']
            self.cortex_blocks.activate_block(block_id, activation)
    
    def get_knowledge_growth_trend(self) -> List[Tuple[float, int]]:
        """
        Get knowledge growth trend over time.
        
        Returns:
            List of (timestamp, node_count) tuples
        """
        return [
            (snapshot.timestamp, snapshot.total_nodes)
            for snapshot in self.snapshots
        ]
