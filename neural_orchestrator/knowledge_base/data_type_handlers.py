"""
Data Type Handlers - Specialized Handlers for Different Data Types
Handles images, video, actions, word data, language, code interpretation, and decision interactions.
"""

import numpy as np
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import base64
import json


class DataType(Enum):
    """Types of data to handle."""
    IMAGE = "image"
    VIDEO = "video"
    ACTION = "action"
    WORD_DATA = "word_data"
    LANGUAGE = "language"
    CODE_INTERPRETATION = "code_interpretation"
    DECISION_INTERACTION = "decision_interaction"
    AUDIO = "audio"
    TEXT = "text"


@dataclass
class ProcessedData:
    """Represents processed data ready for storage."""
    data_type: DataType
    processed_data: Any
    metadata: Dict[str, any]
    features: Dict[str, float]
    timestamp: float
    size_bytes: int


class DataTypeHandlers:
    """
    Specialized handlers for different data types.
    Processes and prepares data for storage in cortex blocks and nodes.
    """
    
    def __init__(self):
        """Initialize the Data Type Handlers."""
        self.processing_history: List[ProcessedData] = []
        self.feature_extractors = {
            DataType.IMAGE: self._extract_image_features,
            DataType.VIDEO: self._extract_video_features,
            DataType.ACTION: self._extract_action_features,
            DataType.WORD_DATA: self._extract_word_features,
            DataType.LANGUAGE: self._extract_language_features,
            DataType.CODE_INTERPRETATION: self._extract_code_features,
            DataType.DECISION_INTERACTION: self._extract_decision_features,
            DataType.AUDIO: self._extract_audio_features,
            DataType.TEXT: self._extract_text_features
        }
    
    def process_data(
        self,
        data_type: DataType,
        raw_data: Any,
        metadata: Optional[Dict[str, any]] = None
    ) -> ProcessedData:
        """
        Process data based on its type.
        
        Args:
            data_type: Type of data
            raw_data: Raw data to process
            metadata: Additional metadata
            
        Returns:
            ProcessedData object
        """
        # Get appropriate processor
        processor = self._get_processor(data_type)
        
        # Process the data
        processed_data = processor(raw_data)
        
        # Extract features
        feature_extractor = self.feature_extractors.get(data_type)
        features = feature_extractor(processed_data) if feature_extractor else {}
        
        # Calculate size
        size_bytes = self._calculate_size(processed_data)
        
        processed = ProcessedData(
            data_type=data_type,
            processed_data=processed_data,
            metadata=metadata or {},
            features=features,
            timestamp=datetime.now().timestamp(),
            size_bytes=size_bytes
        )
        
        self.processing_history.append(processed)
        if len(self.processing_history) > 1000:
            self.processing_history.pop(0)
        
        return processed
    
    def _get_processor(self, data_type: DataType):
        """Get the appropriate processor for data type."""
        processors = {
            DataType.IMAGE: self._process_image,
            DataType.VIDEO: self._process_video,
            DataType.ACTION: self._process_action,
            DataType.WORD_DATA: self._process_word_data,
            DataType.LANGUAGE: self._process_language,
            DataType.CODE_INTERPRETATION: self._process_code,
            DataType.DECISION_INTERACTION: self._process_decision,
            DataType.AUDIO: self._process_audio,
            DataType.TEXT: self._process_text
        }
        return processors.get(data_type, self._process_generic)
    
    def _process_image(self, raw_data: Any) -> np.ndarray:
        """Process image data."""
        if isinstance(raw_data, np.ndarray):
            return raw_data
        elif isinstance(raw_data, bytes):
            # Decode from bytes (simplified)
            return np.frombuffer(raw_data, dtype=np.uint8)
        else:
            # Convert to numpy array
            return np.array(raw_data)
    
    def _process_video(self, raw_data: Any) -> Dict[str, any]:
        """Process video data."""
        if isinstance(raw_data, dict):
            return raw_data
        else:
            return {
                'frames': raw_data,
                'frame_count': len(raw_data) if hasattr(raw_data, '__len__') else 0,
                'duration': 0.0
            }
    
    def _process_action(self, raw_data: Any) -> Dict[str, any]:
        """Process action data."""
        if isinstance(raw_data, dict):
            return raw_data
        else:
            return {
                'action_type': str(raw_data),
                'parameters': {},
                'timestamp': datetime.now().timestamp()
            }
    
    def _process_word_data(self, raw_data: Any) -> Dict[str, any]:
        """Process word/linguistic data."""
        if isinstance(raw_data, str):
            return {
                'word': raw_data,
                'length': len(raw_data),
                'language': 'unknown'
            }
        elif isinstance(raw_data, dict):
            return raw_data
        else:
            return {
                'word': str(raw_data),
                'length': len(str(raw_data)),
                'language': 'unknown'
            }
    
    def _process_language(self, raw_data: Any) -> Dict[str, any]:
        """Process language data."""
        if isinstance(raw_data, str):
            return {
                'text': raw_data,
                'language': 'unknown',
                'complexity': len(raw_data.split())
            }
        elif isinstance(raw_data, dict):
            return raw_data
        else:
            return {
                'text': str(raw_data),
                'language': 'unknown',
                'complexity': len(str(raw_data).split())
            }
    
    def _process_code(self, raw_data: Any) -> Dict[str, any]:
        """Process code interpretation data."""
        if isinstance(raw_data, str):
            return {
                'code': raw_data,
                'language': self._detect_language(raw_data),
                'complexity': len(raw_data.split('\n'))
            }
        elif isinstance(raw_data, dict):
            return raw_data
        else:
            return {
                'code': str(raw_data),
                'language': 'unknown',
                'complexity': len(str(raw_data).split('\n'))
            }
    
    def _process_decision(self, raw_data: Any) -> Dict[str, any]:
        """Process decision interaction data."""
        if isinstance(raw_data, dict):
            return raw_data
        else:
            return {
                'decision': str(raw_data),
                'confidence': 0.5,
                'context': {}
            }
    
    def _process_audio(self, raw_data: Any) -> np.ndarray:
        """Process audio data."""
        if isinstance(raw_data, np.ndarray):
            return raw_data
        elif isinstance(raw_data, bytes):
            return np.frombuffer(raw_data, dtype=np.float32)
        else:
            return np.array(raw_data)
    
    def _process_text(self, raw_data: Any) -> str:
        """Process text data."""
        return str(raw_data)
    
    def _process_generic(self, raw_data: Any) -> Any:
        """Generic processor for unknown types."""
        return raw_data
    
    def _extract_image_features(self, data: np.ndarray) -> Dict[str, float]:
        """Extract features from image data."""
        if not isinstance(data, np.ndarray):
            return {}
        
        return {
            'mean_intensity': float(np.mean(data)),
            'std_intensity': float(np.std(data)),
            'contrast': float(np.max(data) - np.min(data)),
            'brightness': float(np.mean(data)),
            'size': float(data.size)
        }
    
    def _extract_video_features(self, data: Dict) -> Dict[str, float]:
        """Extract features from video data."""
        return {
            'frame_count': float(data.get('frame_count', 0)),
            'duration': float(data.get('duration', 0.0)),
            'frame_rate': float(data.get('frame_count', 0) / max(data.get('duration', 1.0), 1.0))
        }
    
    def _extract_action_features(self, data: Dict) -> Dict[str, float]:
        """Extract features from action data."""
        action_type = data.get('action_type', 'unknown')
        
        return {
            'complexity': float(len(data.get('parameters', {}))),
            'urgency': data.get('urgency', 0.5),
            'confidence': data.get('confidence', 0.5)
        }
    
    def _extract_word_features(self, data: Dict) -> Dict[str, float]:
        """Extract features from word data."""
        word = data.get('word', '')
        
        return {
            'length': float(len(word)),
            'complexity': float(len(set(word))),
            'frequency': data.get('frequency', 0.0)
        }
    
    def _extract_language_features(self, data: Dict) -> Dict[str, float]:
        """Extract features from language data."""
        text = data.get('text', '')
        
        return {
            'length': float(len(text)),
            'word_count': float(len(text.split())),
            'sentence_count': float(text.count('.')),
            'complexity': data.get('complexity', 0.0)
        }
    
    def _extract_code_features(self, data: Dict) -> Dict[str, float]:
        """Extract features from code data."""
        code = data.get('code', '')
        
        return {
            'length': float(len(code)),
            'line_count': float(len(code.split('\n'))),
            'complexity': data.get('complexity', 0.0),
            'indentation_level': float(code.count('\t') + code.count('    '))
        }
    
    def _extract_decision_features(self, data: Dict) -> Dict[str, float]:
        """Extract features from decision data."""
        return {
            'confidence': data.get('confidence', 0.5),
            'urgency': data.get('urgency', 0.5),
            'impact': data.get('impact', 0.5)
        }
    
    def _extract_audio_features(self, data: np.ndarray) -> Dict[str, float]:
        """Extract features from audio data."""
        if not isinstance(data, np.ndarray):
            return {}
        
        return {
            'mean_amplitude': float(np.mean(np.abs(data))),
            'max_amplitude': float(np.max(np.abs(data))),
            'duration': float(len(data)),
            'energy': float(np.sum(data ** 2))
        }
    
    def _extract_text_features(self, data: str) -> Dict[str, float]:
        """Extract features from text data."""
        return {
            'length': float(len(data)),
            'word_count': float(len(data.split())),
            'character_diversity': float(len(set(data))),
            'sentence_count': float(data.count('.') + data.count('!') + data.count('?'))
        }
    
    def _detect_language(self, code: str) -> str:
        """Detect programming language from code."""
        code_lower = code.lower()
        
        if 'def ' in code or 'import ' in code:
            return 'python'
        elif 'function' in code or 'var ' in code or '{' in code:
            return 'javascript'
        elif 'public class' in code or 'private' in code:
            return 'java'
        elif 'fn ' in code or 'let ' in code:
            return 'rust'
        else:
            return 'unknown'
    
    def _calculate_size(self, data: Any) -> int:
        """Calculate size in bytes."""
        if isinstance(data, np.ndarray):
            return data.nbytes
        elif isinstance(data, (str, bytes)):
            return len(data)
        elif isinstance(data, dict):
            return len(json.dumps(data).encode())
        elif isinstance(data, (list, tuple)):
            return len(str(data).encode())
        else:
            return len(str(data).encode())
    
    def batch_process(self, data_items: List[Tuple[DataType, Any, Dict]]) -> List[ProcessedData]:
        """
        Process multiple data items in batch.
        
        Args:
            data_items: List of (data_type, raw_data, metadata) tuples
            
        Returns:
            List of ProcessedData objects
        """
        return [
            self.process_data(data_type, raw_data, metadata)
            for data_type, raw_data, metadata in data_items
        ]
    
    def get_processing_statistics(self) -> Dict[str, any]:
        """
        Get statistics about data processing.
        
        Returns:
            Dictionary containing processing statistics
        """
        if not self.processing_history:
            return {
                'total_processed': 0
            }
        
        type_counts = {}
        total_size = 0
        
        for processed in self.processing_history:
            dtype = processed.data_type.value
            type_counts[dtype] = type_counts.get(dtype, 0) + 1
            total_size += processed.size_bytes
        
        return {
            'total_processed': len(self.processing_history),
            'by_type': type_counts,
            'total_size_bytes': total_size,
            'avg_size_bytes': total_size / len(self.processing_history),
            'unique_types': len(type_counts)
        }
