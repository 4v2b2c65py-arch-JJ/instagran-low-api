"""
Behavior Predictor - User Behavior Prediction Models
Predicts user behavior patterns to enable autonomous AI steering.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class BehaviorType(Enum):
    """Types of user behaviors to predict."""
    CLICK_PATTERN = "click_pattern"
    SCROLL_PATTERN = "scroll_pattern"
    TYPING_PATTERN = "typing_pattern"
    APP_NAVIGATION = "app_navigation"
    CONTENT_PREFERENCE = "content_preference"
    TIME_OF_DAY = "time_of_day"
    EMOTIONAL_STATE = "emotional_state"


@dataclass
class BehaviorPrediction:
    """Represents a behavior prediction."""
    prediction_id: str
    behavior_type: BehaviorType
    predicted_action: str
    confidence: float
    timestamp: float
    context: Dict[str, any]
    model_used: str


class BehaviorPredictor:
    """
    Predicts user behavior patterns using machine learning models.
    Enables the autonomous agent to anticipate and mimic user actions.
    """
    
    def __init__(self, model_complexity: int = 3):
        """
        Initialize the Behavior Predictor.
        
        Args:
            model_complexity: Complexity level of prediction models (1-5)
        """
        self.model_complexity = model_complexity
        
        # Behavior history
        self.behavior_history: Dict[BehaviorType, List[Dict]] = {}
        
        # Prediction models (simplified for demonstration)
        self.prediction_models: Dict[BehaviorType, any] = {}
        
        # Initialize models
        self._initialize_models()
        
        # Prediction cache
        self.prediction_cache: List[BehaviorPrediction] = []
        
        # Learning parameters
        self.learning_rate = 0.1
        self.decay_factor = 0.95
    
    def _initialize_models(self):
        """Initialize prediction models for each behavior type."""
        for behavior_type in BehaviorType:
            self.behavior_history[behavior_type] = []
            # Create simple model weights
            self.prediction_models[behavior_type] = {
                'weights': np.random.randn(10) * 0.1,
                'bias': np.random.randn() * 0.1,
                'accuracy': 0.5
            }
    
    def record_behavior(
        self,
        behavior_type: BehaviorType,
        action_data: Dict[str, any],
        context: Optional[Dict[str, any]] = None
    ):
        """
        Record observed user behavior for learning.
        
        Args:
            behavior_type: Type of behavior
            action_data: Data about the action
            context: Contextual information
        """
        behavior_entry = {
            'action_data': action_data,
            'context': context or {},
            'timestamp': datetime.now().timestamp()
        }
        
        self.behavior_history[behavior_type].append(behavior_entry)
        
        # Keep history manageable
        if len(self.behavior_history[behavior_type]) > 1000:
            self.behavior_history[behavior_type].pop(0)
        
        # Update model
        self._update_model(behavior_type, behavior_entry)
    
    def _update_model(self, behavior_type: BehaviorType, behavior_entry: Dict):
        """
        Update prediction model based on new behavior.
        
        Args:
            behavior_type: Type of behavior
            behavior_entry: Behavior entry to learn from
        """
        model = self.prediction_models[behavior_type]
        
        # Simple weight update (in real implementation, would use proper ML)
        model['weights'] = model['weights'] * (1 - self.learning_rate) + \
                          np.random.randn(len(model['weights'])) * 0.01 * self.learning_rate
        model['bias'] = model['bias'] * (1 - self.learning_rate) + \
                       np.random.randn() * 0.01 * self.learning_rate
    
    def predict_next_behavior(
        self,
        behavior_type: BehaviorType,
        context: Optional[Dict[str, any]] = None,
        time_horizon: float = 5.0
    ) -> BehaviorPrediction:
        """
        Predict the next user behavior.
        
        Args:
            behavior_type: Type of behavior to predict
            context: Current context
            time_horizon: Time horizon in seconds
            
        Returns:
            BehaviorPrediction object
        """
        model = self.prediction_models[behavior_type]
        history = self.behavior_history[behavior_type]
        
        # Calculate prediction based on history and model
        if len(history) < 3:
            # Not enough data, return default prediction
            predicted_action = self._get_default_action(behavior_type)
            confidence = 0.3
        else:
            # Use model to predict
            predicted_action = self._generate_prediction(behavior_type, history, context)
            confidence = model['accuracy']
        
        prediction = BehaviorPrediction(
            prediction_id=f"pred_{len(self.prediction_cache)}_{datetime.now().timestamp()}",
            behavior_type=behavior_type,
            predicted_action=predicted_action,
            confidence=confidence,
            timestamp=datetime.now().timestamp(),
            context=context or {},
            model_used=f"model_complexity_{self.model_complexity}"
        )
        
        self.prediction_cache.append(prediction)
        if len(self.prediction_cache) > 100:
            self.prediction_cache.pop(0)
        
        return prediction
    
    def _get_default_action(self, behavior_type: BehaviorType) -> str:
        """Get default action for behavior type."""
        defaults = {
            BehaviorType.CLICK_PATTERN: "tap_center",
            BehaviorType.SCROLL_PATTERN: "scroll_down",
            BehaviorType.TYPING_PATTERN: "continue_typing",
            BehaviorType.APP_NAVIGATION: "stay_current_screen",
            BehaviorType.CONTENT_PREFERENCE: "neutral",
            BehaviorType.TIME_OF_DAY: "normal_activity",
            BehaviorType.EMOTIONAL_STATE: "neutral"
        }
        return defaults.get(behavior_type, "unknown")
    
    def _generate_prediction(
        self,
        behavior_type: BehaviorType,
        history: List[Dict],
        context: Optional[Dict[str, any]]
    ) -> str:
        """
        Generate prediction using model.
        
        Args:
            behavior_type: Type of behavior
            history: Behavior history
            context: Current context
            
        Returns:
            Predicted action string
        """
        model = self.prediction_models[behavior_type]
        
        # Analyze recent patterns
        recent_actions = [entry['action_data'] for entry in history[-10:]]
        
        # Simple pattern matching
        if behavior_type == BehaviorType.CLICK_PATTERN:
            return self._predict_click(recent_actions, context)
        elif behavior_type == BehaviorType.SCROLL_PATTERN:
            return self._predict_scroll(recent_actions, context)
        elif behavior_type == BehaviorType.APP_NAVIGATION:
            return self._predict_navigation(recent_actions, context)
        elif behavior_type == BehaviorType.CONTENT_PREFERENCE:
            return self._predict_content_preference(recent_actions, context)
        else:
            return self._get_default_action(behavior_type)
    
    def _predict_click(self, recent_actions: List[Dict], context: Optional[Dict]) -> str:
        """Predict next click action."""
        if not recent_actions:
            return "tap_center"
        
        # Analyze click positions
        positions = [(a.get('x', 0), a.get('y', 0)) for a in recent_actions if 'x' in a]
        
        if positions:
            # Predict based on recent position trends
            avg_x = np.mean([p[0] for p in positions])
            avg_y = np.mean([p[1] for p in positions])
            
            if avg_x < 0.3:
                return "tap_left"
            elif avg_x > 0.7:
                return "tap_right"
            elif avg_y < 0.3:
                return "tap_top"
            elif avg_y > 0.7:
                return "tap_bottom"
        
        return "tap_center"
    
    def _predict_scroll(self, recent_actions: List[Dict], context: Optional[Dict]) -> str:
        """Predict next scroll action."""
        if not recent_actions:
            return "scroll_down"
        
        # Analyze scroll directions
        directions = [a.get('direction', 'down') for a in recent_actions if 'direction' in a]
        
        if directions:
            most_common = max(set(directions), key=directions.count)
            return f"scroll_{most_common}"
        
        return "scroll_down"
    
    def _predict_navigation(self, recent_actions: List[Dict], context: Optional[Dict]) -> str:
        """Predict next navigation action."""
        if not recent_actions:
            return "stay_current_screen"
        
        # Analyze screen transitions
        screens = [a.get('screen', 'current') for a in recent_actions if 'screen' in a]
        
        if len(set(screens)) > 1:
            # User is navigating, predict continuation
            return "navigate_to_next_screen"
        
        return "stay_current_screen"
    
    def _predict_content_preference(self, recent_actions: List[Dict], context: Optional[Dict]) -> str:
        """Predict content preference."""
        if not recent_actions:
            return "neutral"
        
        # Analyze content interactions
        sentiments = [a.get('sentiment', 0) for a in recent_actions if 'sentiment' in a]
        
        if sentiments:
            avg_sentiment = np.mean(sentiments)
            if avg_sentiment > 0.3:
                return "positive_preference"
            elif avg_sentiment < -0.3:
                return "negative_preference"
        
        return "neutral"
    
    def get_behavior_statistics(self) -> Dict[str, any]:
        """
        Get statistics about behavior prediction.
        
        Returns:
            Dictionary containing prediction statistics
        """
        total_behaviors = sum(len(history) for history in self.behavior_history.values())
        
        recent_predictions = self.prediction_cache[-20:] if self.prediction_cache else []
        avg_confidence = np.mean([p.confidence for p in recent_predictions]) if recent_predictions else 0.0
        
        return {
            'total_behaviors_recorded': total_behaviors,
            'behaviors_by_type': {
                bt.value: len(history) for bt, history in self.behavior_history.items()
            },
            'total_predictions': len(self.prediction_cache),
            'avg_confidence': avg_confidence,
            'model_complexity': self.model_complexity,
            'active_models': len(self.prediction_models)
        }
    
    def get_recent_predictions(self, limit: int = 10) -> List[BehaviorPrediction]:
        """
        Get recent behavior predictions.
        
        Args:
            limit: Maximum number of predictions to return
            
        Returns:
            List of recent BehaviorPrediction objects
        """
        return self.prediction_cache[-limit:] if self.prediction_cache else []
    
    def clear_old_data(self, max_age_seconds: float = 86400):
        """
        Clear old behavior data.
        
        Args:
            max_age_seconds: Maximum age in seconds (default 24 hours)
        """
        current_time = datetime.now().timestamp()
        
        for behavior_type in self.behavior_history:
            self.behavior_history[behavior_type] = [
                entry for entry in self.behavior_history[behavior_type]
                if current_time - entry['timestamp'] < max_age_seconds
            ]
        
        self.prediction_cache = [
            pred for pred in self.prediction_cache
            if current_time - pred.timestamp < max_age_seconds
        ]
