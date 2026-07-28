"""
Device Feedback Loop - Brain Map Integration
Creates feedback loops from device inputs to brain map layer for adaptive learning.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
from datetime import datetime
import asyncio


@dataclass
class FeedbackSignal:
    """Represents a feedback signal from device to brain map."""
    signal_id: str
    source_type: str  # cache, emoji, auto_corrector, click, app_interaction
    signal_data: Dict[str, any]
    strength: float  # 0-1
    timestamp: float
    processed: bool = False


@dataclass
class BrainMapResponse:
    """Represents response from brain map layer."""
    response_id: str
    feedback_signal_id: str
    action: str
    parameters: Dict[str, any]
    confidence: float
    timestamp: float


class DeviceFeedbackLoop:
    """
    Creates feedback loops from device inputs to brain map layer.
    Processes device inputs and generates adaptive responses.
    """
    
    def __init__(self, brain_map_layer: Optional[str] = None, loop_interval: float = 0.5):
        """
        Initialize the Device Feedback Loop.
        
        Args:
            brain_map_layer: Target brain map layer
            loop_interval: Feedback loop processing interval in seconds
        """
        self.brain_map_layer = brain_map_layer
        self.loop_interval = loop_interval
        
        # Feedback signals
        self.feedback_signals: List[FeedbackSignal] = []
        self.brain_map_responses: List[BrainMapResponse] = []
        
        # Loop state
        self.is_running = False
        self.processing_callback: Optional[Callable] = None
        
        # Adaptive learning parameters
        self.learning_rate = 0.1
        self.decay_factor = 0.95
        
        # Signal strength tracking
        self.signal_strengths: Dict[str, float] = {}
        
        # Brain map integration
        self.brain_map_state: Dict[str, any] = {}
    
    async def start_feedback_loop(self):
        """Start the feedback loop processing."""
        self.is_running = True
        print("Device Feedback Loop started")
        
        while self.is_running:
            await self.process_feedback_cycle()
            await asyncio.sleep(self.loop_interval)
    
    async def stop_feedback_loop(self):
        """Stop the feedback loop processing."""
        self.is_running = False
        print("Device Feedback Loop stopped")
    
    async def process_feedback_cycle(self):
        """Process a single feedback cycle."""
        # Get unprocessed signals
        unprocessed = [s for s in self.feedback_signals if not s.processed]
        
        for signal in unprocessed:
            # Process signal through brain map
            response = self._process_signal(signal)
            
            # Store response
            self.brain_map_responses.append(response)
            
            # Mark signal as processed
            signal.processed = True
            
            # Update brain map state
            self._update_brain_map_state(signal, response)
            
            # Call callback if provided
            if self.processing_callback:
                await self.processing_callback(signal, response)
        
        # Apply decay to signal strengths
        self._apply_decay()
    
    def add_feedback_signal(
        self,
        source_type: str,
        signal_data: Dict[str, any],
        strength: float = 0.5
    ) -> FeedbackSignal:
        """
        Add a feedback signal to the loop.
        
        Args:
            source_type: Type of signal source
            signal_data: Signal data
            strength: Signal strength (0-1)
            
        Returns:
            FeedbackSignal object
        """
        signal = FeedbackSignal(
            signal_id=f"signal_{len(self.feedback_signals)}_{datetime.now().timestamp()}",
            source_type=source_type,
            signal_data=signal_data,
            strength=strength,
            timestamp=datetime.now().timestamp()
        )
        
        self.feedback_signals.append(signal)
        
        # Update signal strength tracking
        if source_type not in self.signal_strengths:
            self.signal_strengths[source_type] = 0.0
        self.signal_strengths[source_type] = (
            self.signal_strengths[source_type] * (1 - self.learning_rate) +
            strength * self.learning_rate
        )
        
        return signal
    
    def _process_signal(self, signal: FeedbackSignal) -> BrainMapResponse:
        """
        Process a feedback signal through brain map.
        
        Args:
            signal: Feedback signal to process
            
        Returns:
            BrainMapResponse object
        """
        # Determine action based on signal type and data
        action = self._determine_action(signal)
        
        # Calculate confidence based on signal strength and brain map state
        confidence = self._calculate_confidence(signal)
        
        # Generate parameters for the action
        parameters = self._generate_parameters(signal, action)
        
        response = BrainMapResponse(
            response_id=f"response_{len(self.brain_map_responses)}_{datetime.now().timestamp()}",
            feedback_signal_id=signal.signal_id,
            action=action,
            parameters=parameters,
            confidence=confidence,
            timestamp=datetime.now().timestamp()
        )
        
        return response
    
    def _determine_action(self, signal: FeedbackSignal) -> str:
        """
        Determine action based on signal type and data.
        
        Args:
            signal: Feedback signal
            
        Returns:
            Action string
        """
        source_type = signal.source_type
        data = signal.signal_data
        
        # Action mapping based on source type
        action_map = {
            'cache': 'update_cache_priority',
            'emoji': 'adjust_sentiment_model',
            'auto_corrector': 'update_correction_model',
            'click': 'analyze_interaction_pattern',
            'app_interaction': 'optimize_user_experience'
        }
        
        base_action = action_map.get(source_type, 'general_processing')
        
        # Refine action based on data
        if source_type == 'cache' and data.get('size_bytes', 0) > 1000000:
            return 'optimize_large_cache'
        elif source_type == 'emoji' and data.get('sentiment_score', 0) > 0.5:
            return 'reinforce_positive_patterns'
        elif source_type == 'auto_corrector' and data.get('accepted', False):
            return 'strengthen_correction'
        elif source_type == 'click' and data.get('rapid_click', False):
            return 'detect_user_frustration'
        
        return base_action
    
    def _calculate_confidence(self, signal: FeedbackSignal) -> float:
        """
        Calculate confidence for response.
        
        Args:
            signal: Feedback signal
            
        Returns:
            Confidence score (0-1)
        """
        base_confidence = signal.strength
        
        # Adjust based on signal strength history
        source_strength = self.signal_strengths.get(signal.source_type, 0.5)
        
        # Combine with brain map state
        state_factor = len(self.brain_map_state) / (len(self.brain_map_state) + 10)
        
        confidence = (base_confidence * 0.6) + (source_strength * 0.3) + (state_factor * 0.1)
        
        return min(max(confidence, 0.0), 1.0)
    
    def _generate_parameters(self, signal: FeedbackSignal, action: str) -> Dict[str, any]:
        """
        Generate parameters for the action.
        
        Args:
            signal: Feedback signal
            action: Determined action
            
        Returns:
            Parameters dictionary
        """
        parameters = {
            'action': action,
            'source_type': signal.source_type,
            'signal_strength': signal.strength,
            'timestamp': signal.timestamp
        }
        
        # Add specific parameters based on action
        if action == 'update_cache_priority':
            parameters['priority'] = signal.signal_data.get('access_frequency', 1)
            parameters['size'] = signal.signal_data.get('size_bytes', 0)
        elif action == 'adjust_sentiment_model':
            parameters['sentiment'] = signal.signal_data.get('sentiment_score', 0.0)
            parameters['emoji'] = signal.signal_data.get('emoji', '')
        elif action == 'update_correction_model':
            parameters['confidence'] = signal.signal_data.get('confidence', 0.0)
            parameters['accepted'] = signal.signal_data.get('accepted', False)
        
        return parameters
    
    def _update_brain_map_state(self, signal: FeedbackSignal, response: BrainMapResponse):
        """
        Update brain map state based on signal and response.
        
        Args:
            signal: Feedback signal
            response: Brain map response
        """
        state_key = f"{signal.source_type}_{response.action}"
        
        if state_key not in self.brain_map_state:
            self.brain_map_state[state_key] = {
                'count': 0,
                'avg_confidence': 0.0,
                'last_update': datetime.now().timestamp()
            }
        
        state = self.brain_map_state[state_key]
        state['count'] += 1
        state['avg_confidence'] = (
            state['avg_confidence'] * (state['count'] - 1) + response.confidence
        ) / state['count']
        state['last_update'] = datetime.now().timestamp()
    
    def _apply_decay(self):
        """Apply decay factor to signal strengths."""
        for source_type in self.signal_strengths:
            self.signal_strengths[source_type] *= self.decay_factor
    
    def set_processing_callback(self, callback: Callable):
        """
        Set callback for processing feedback signals.
        
        Args:
            callback: Async callback function
        """
        self.processing_callback = callback
    
    def get_feedback_statistics(self) -> Dict[str, any]:
        """
        Get statistics about feedback loop.
        
        Returns:
            Dictionary containing feedback statistics
        """
        processed_count = sum(1 for s in self.feedback_signals if s.processed)
        unprocessed_count = len(self.feedback_signals) - processed_count
        
        response_confidences = [r.confidence for r in self.brain_map_responses]
        
        return {
            'total_signals': len(self.feedback_signals),
            'processed_signals': processed_count,
            'unprocessed_signals': unprocessed_count,
            'total_responses': len(self.brain_map_responses),
            'avg_response_confidence': np.mean(response_confidences) if response_confidences else 0.0,
            'signal_strengths': self.signal_strengths.copy(),
            'brain_map_state_size': len(self.brain_map_state),
            'is_running': self.is_running
        }
    
    def get_brain_map_state(self) -> Dict[str, any]:
        """
        Get current brain map state.
        
        Returns:
            Dictionary containing brain map state
        """
        return self.brain_map_state.copy()
    
    def clear_old_signals(self, max_age_seconds: float = 3600):
        """
        Clear old feedback signals.
        
        Args:
            max_age_seconds: Maximum age in seconds (default 1 hour)
        """
        current_time = datetime.now().timestamp()
        
        self.feedback_signals = [
            s for s in self.feedback_signals
            if current_time - s.timestamp < max_age_seconds
        ]
        
        self.brain_map_responses = [
            r for r in self.brain_map_responses
            if current_time - r.timestamp < max_age_seconds
        ]
    
    def get_recent_responses(self, limit: int = 10) -> List[BrainMapResponse]:
        """
        Get recent brain map responses.
        
        Args:
            limit: Maximum number of responses to return
            
        Returns:
            List of recent BrainMapResponse objects
        """
        return self.brain_map_responses[-limit:] if self.brain_map_responses else []
