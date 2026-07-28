"""
Decision Engine - Decision-Making Engine
Makes autonomous decisions based on predictions, context, and goals.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class DecisionType(Enum):
    """Types of decisions the engine can make."""
    ACTION_DECISION = "action_decision"
    NAVIGATION_DECISION = "navigation_decision"
    CONTENT_DECISION = "content_decision"
    TIMING_DECISION = "timing_decision"
    API_DECISION = "api_decision"
    SAFETY_DECISION = "safety_decision"


class Priority(Enum):
    """Priority levels for decisions."""
    CRITICAL = 3
    HIGH = 2
    MEDIUM = 1
    LOW = 0


@dataclass
class Decision:
    """Represents a decision made by the engine."""
    decision_id: str
    decision_type: DecisionType
    action: str
    parameters: Dict[str, any]
    confidence: float
    priority: Priority
    reasoning: str
    timestamp: float
    executed: bool = False


class DecisionEngine:
    """
    Makes autonomous decisions based on predictions, context, and goals.
    Combines behavior predictions with current state to determine optimal actions.
    """
    
    def __init__(self, risk_tolerance: float = 0.5):
        """
        Initialize the Decision Engine.
        
        Args:
            risk_tolerance: Risk tolerance level (0-1), higher = more risk-taking
        """
        self.risk_tolerance = risk_tolerance
        
        # Decision history
        self.decision_history: List[Decision] = []
        
        # Current goals
        self.current_goals: List[str] = []
        
        # Decision weights
        self.decision_weights = {
            'prediction_confidence': 0.4,
            'context_relevance': 0.3,
            'goal_alignment': 0.2,
            'safety_score': 0.1
        }
        
        # State tracking
        self.current_state: Dict[str, any] = {}
        self.previous_decisions: List[Decision] = []
    
    def set_goals(self, goals: List[str]):
        """
        Set current autonomous goals.
        
        Args:
            goals: List of goal descriptions
        """
        self.current_goals = goals
    
    def update_state(self, state: Dict[str, any]):
        """
        Update current state information.
        
        Args:
            state: Current state dictionary
        """
        self.current_state = state
    
    def make_decision(
        self,
        prediction: Dict[str, any],
        context: Dict[str, any],
        available_actions: List[Dict[str, any]]
    ) -> Decision:
        """
        Make a decision based on prediction, context, and available actions.
        
        Args:
            prediction: Behavior prediction
            context: Current context
            available_actions: List of available actions
            
        Returns:
            Decision object
        """
        # Score each available action
        scored_actions = []
        for action in available_actions:
            score = self._score_action(action, prediction, context)
            scored_actions.append((action, score))
        
        # Select best action
        if scored_actions:
            best_action, best_score = max(scored_actions, key=lambda x: x[1])
        else:
            best_action = {'action': 'wait', 'parameters': {}}
            best_score = 0.5
        
        # Determine priority
        priority = self._determine_priority(best_action, best_score)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(best_action, prediction, context, best_score)
        
        decision = Decision(
            decision_id=f"dec_{len(self.decision_history)}_{datetime.now().timestamp()}",
            decision_type=self._map_action_to_decision_type(best_action['action']),
            action=best_action['action'],
            parameters=best_action.get('parameters', {}),
            confidence=best_score,
            priority=priority,
            reasoning=reasoning,
            timestamp=datetime.now().timestamp()
        )
        
        self.decision_history.append(decision)
        self.previous_decisions.append(decision)
        
        # Keep history manageable
        if len(self.previous_decisions) > 50:
            self.previous_decisions.pop(0)
        
        return decision
    
    def _score_action(
        self,
        action: Dict[str, any],
        prediction: Dict[str, any],
        context: Dict[str, any]
    ) -> float:
        """
        Score an action based on multiple factors.
        
        Args:
            action: Action to score
            prediction: Behavior prediction
            context: Current context
            
        Returns:
            Action score (0-1)
        """
        scores = {}
        
        # Prediction confidence
        prediction_confidence = prediction.get('confidence', 0.5)
        scores['prediction_confidence'] = prediction_confidence
        
        # Context relevance
        context_relevance = self._calculate_context_relevance(action, context)
        scores['context_relevance'] = context_relevance
        
        # Goal alignment
        goal_alignment = self._calculate_goal_alignment(action)
        scores['goal_alignment'] = goal_alignment
        
        # Safety score
        safety_score = self._calculate_safety_score(action)
        scores['safety_score'] = safety_score
        
        # Weighted score
        weighted_score = sum(
            scores[key] * self.decision_weights[key]
            for key in scores
        )
        
        return weighted_score
    
    def _calculate_context_relevance(self, action: Dict[str, any], context: Dict[str, any]) -> float:
        """
        Calculate how relevant an action is to current context.
        
        Args:
            action: Action to evaluate
            context: Current context
            
        Returns:
            Context relevance score (0-1)
        """
        action_type = action.get('action', '')
        
        # Simple context matching
        if 'screen' in context:
            current_screen = context['screen']
            if action_type == 'navigate' and current_screen != 'target':
                return 0.8
            elif action_type == 'click' and current_screen == 'target':
                return 0.9
        
        if 'time_of_day' in context:
            hour = context['time_of_day']
            if 9 <= hour <= 17:  # Business hours
                if action_type in ['work', 'productivity']:
                    return 0.8
            else:  # Personal time
                if action_type in ['entertainment', 'social']:
                    return 0.8
        
        return 0.5  # Default relevance
    
    def _calculate_goal_alignment(self, action: Dict[str, any]) -> float:
        """
        Calculate how well action aligns with current goals.
        
        Args:
            action: Action to evaluate
            
        Returns:
            Goal alignment score (0-1)
        """
        if not self.current_goals:
            return 0.5
        
        action_type = action.get('action', '')
        
        # Simple goal matching
        for goal in self.current_goals:
            if 'productivity' in goal.lower() and action_type in ['work', 'task']:
                return 0.9
            elif 'social' in goal.lower() and action_type in ['message', 'share']:
                return 0.9
            elif 'learning' in goal.lower() and action_type in ['read', 'study']:
                return 0.9
        
        return 0.5  # Default alignment
    
    def _calculate_safety_score(self, action: Dict[str, any]) -> float:
        """
        Calculate safety score for an action.
        
        Args:
            action: Action to evaluate
            
        Returns:
            Safety score (0-1)
        """
        action_type = action.get('action', '')
        
        # Risk assessment
        risky_actions = ['delete', 'remove', 'uninstall', 'payment']
        safe_actions = ['view', 'read', 'scroll', 'wait']
        
        if action_type in risky_actions:
            return 1.0 - self.risk_tolerance  # Lower score for risky actions
        elif action_type in safe_actions:
            return 1.0  # High score for safe actions
        else:
            return 0.7  # Medium score for neutral actions
    
    def _determine_priority(self, action: Dict[str, any], score: float) -> Priority:
        """
        Determine priority level for decision.
        
        Args:
            action: Action being decided
            score: Action score
            
        Returns:
            Priority level
        """
        action_type = action.get('action', '')
        
        # Critical actions
        if action_type in ['emergency', 'safety', 'critical']:
            return Priority.CRITICAL
        
        # High priority based on score
        if score > 0.8:
            return Priority.HIGH
        elif score > 0.5:
            return Priority.MEDIUM
        else:
            return Priority.LOW
    
    def _generate_reasoning(
        self,
        action: Dict[str, any],
        prediction: Dict[str, any],
        context: Dict[str, any],
        score: float
    ) -> str:
        """
        Generate reasoning for the decision.
        
        Args:
            action: Selected action
            prediction: Behavior prediction
            context: Current context
            score: Action score
            
        Returns:
            Reasoning string
        """
        action_type = action.get('action', 'unknown')
        predicted_action = prediction.get('predicted_action', 'unknown')
        confidence = prediction.get('confidence', 0.0)
        
        reasoning = f"Selected {action_type} based on "
        reasoning += f"predicted behavior ({predicted_action}, {confidence:.2f} confidence). "
        reasoning += f"Decision score: {score:.2f}. "
        
        if self.current_goals:
            reasoning += f"Aligns with goals: {', '.join(self.current_goals[:2])}."
        
        return reasoning
    
    def _map_action_to_decision_type(self, action: str) -> DecisionType:
        """
        Map action string to decision type.
        
        Args:
            action: Action string
            
        Returns:
            DecisionType enum
        """
        if action in ['click', 'tap', 'swipe']:
            return DecisionType.ACTION_DECISION
        elif action in ['navigate', 'go_to']:
            return DecisionType.NAVIGATION_DECISION
        elif action in ['read', 'view', 'watch']:
            return DecisionType.CONTENT_DECISION
        elif action in ['wait', 'schedule']:
            return DecisionType.TIMING_DECISION
        elif action in ['api_call', 'request']:
            return DecisionType.API_DECISION
        else:
            return DecisionType.SAFETY_DECISION
    
    def get_decision_statistics(self) -> Dict[str, any]:
        """
        Get statistics about decisions made.
        
        Returns:
            Dictionary containing decision statistics
        """
        if not self.decision_history:
            return {
                'total_decisions': 0,
                'executed_decisions': 0
            }
        
        executed_count = sum(1 for d in self.decision_history if d.executed)
        
        confidence_scores = [d.confidence for d in self.decision_history]
        
        priority_counts = {}
        for decision in self.decision_history:
            priority = decision.priority.name
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        return {
            'total_decisions': len(self.decision_history),
            'executed_decisions': executed_count,
            'execution_rate': executed_count / len(self.decision_history),
            'avg_confidence': np.mean(confidence_scores),
            'priority_distribution': priority_counts,
            'current_goals': self.current_goals,
            'risk_tolerance': self.risk_tolerance
        }
    
    def get_recent_decisions(self, limit: int = 10) -> List[Decision]:
        """
        Get recent decisions.
        
        Args:
            limit: Maximum number of decisions to return
            
        Returns:
            List of recent Decision objects
        """
        return self.decision_history[-limit:] if self.decision_history else []
    
    def adjust_risk_tolerance(self, new_tolerance: float):
        """
        Adjust risk tolerance level.
        
        Args:
            new_tolerance: New risk tolerance (0-1)
        """
        self.risk_tolerance = min(max(new_tolerance, 0.0), 1.0)
    
    def clear_history(self):
        """Clear decision history."""
        self.decision_history.clear()
        self.previous_decisions.clear()
