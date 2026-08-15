"""
Agent Awareness Steering
Provides awareness-based steering for agents with context understanding and decision making.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import numpy as np


class AwarenessLevel(Enum):
    """Levels of agent awareness."""
    MINIMAL = 1
    BASIC = 2
    INTERMEDIATE = 3
    ADVANCED = 4
    EXPERT = 5


class SteeringMode(Enum):
    """Steering modes for agent behavior."""
    AUTONOMOUS = "autonomous"
    ASSISTED = "assisted"
    SUPERVISED = "supervised"
    MANUAL = "manual"


class ContextType(Enum):
    """Types of context for awareness."""
    USER_BEHAVIOR = "user_behavior"
    SYSTEM_STATE = "system_state"
    ENVIRONMENT = "environment"
    SOCIAL = "social"
    TEMPORAL = "temporal"


@dataclass
class AwarenessContext:
    """Context information for agent awareness."""
    context_id: str
    context_type: ContextType
    data: Dict[str, Any]
    confidence: float
    timestamp: str
    source: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SteeringDecision:
    """Represents a steering decision made by the agent."""
    decision_id: str
    agent_id: str
    action_type: str
    parameters: Dict[str, Any]
    awareness_level: AwarenessLevel
    confidence: float
    reasoning: str
    timestamp: str
    executed: bool = False
    result: Optional[Dict[str, Any]] = None


@dataclass
class AwarenessMetric:
    """Metric for tracking agent awareness."""
    metric_id: str
    metric_name: str
    value: float
    trend: str  # "increasing", "decreasing", "stable"
    timestamp: str
    context: Optional[Dict[str, Any]] = None


class AgentAwarenessSteering:
    """
    Provides awareness-based steering for agents.
    Enables agents to understand context and make informed decisions.
    """

    def __init__(self, awareness_level: AwarenessLevel = AwarenessLevel.INTERMEDIATE):
        self.awareness_level = awareness_level
        self.steering_mode = SteeringMode.ASSISTED
        
        self.context_buffer: List[AwarenessContext] = []
        self.decision_history: List[SteeringDecision] = []
        self.awareness_metrics: List[AwarenessMetric] = []
        
        self.context_weights: Dict[ContextType, float] = {
            ContextType.USER_BEHAVIOR: 0.3,
            ContextType.SYSTEM_STATE: 0.25,
            ContextType.ENVIRONMENT: 0.2,
            ContextType.SOCIAL: 0.15,
            ContextType.TEMPORAL: 0.1
        }
        
        self.learning_rate = 0.1
        self.decision_threshold = 0.7

    def add_context(
        self,
        context_type: ContextType,
        data: Dict[str, Any],
        confidence: float = 1.0,
        source: str = "system"
    ) -> AwarenessContext:
        """
        Add context information to the awareness buffer.
        
        Args:
            context_type: Type of context
            data: Context data
            confidence: Confidence level (0-1)
            source: Source of context
            
        Returns:
            AwarenessContext: Added context
        """
        context_id = f"ctx_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{hash(str(data)) % 10000}"
        
        context = AwarenessContext(
            context_id=context_id,
            context_type=context_type,
            data=data,
            confidence=confidence,
            timestamp=datetime.utcnow().isoformat(),
            source=source
        )
        
        self.context_buffer.append(context)
        
        # Maintain buffer size
        if len(self.context_buffer) > 1000:
            self.context_buffer.pop(0)
        
        return context

    def calculate_awareness_score(self, context_types: Optional[List[ContextType]] = None) -> float:
        """
        Calculate overall awareness score based on available context.
        
        Args:
            context_types: Optional list of context types to consider
            
        Returns:
            Awareness score (0-1)
        """
        if not self.context_buffer:
            return 0.0
        
        relevant_contexts = self.context_buffer
        if context_types:
            relevant_contexts = [c for c in self.context_buffer if c.context_type in context_types]
        
        if not relevant_contexts:
            return 0.0
        
        # Calculate weighted score
        total_weight = 0.0
        weighted_score = 0.0
        
        for context in relevant_contexts:
            weight = self.context_weights.get(context.context_type, 0.2)
            confidence = context.confidence
            
            weighted_score += weight * confidence
            total_weight += weight
        
        if total_weight > 0:
            return weighted_score / total_weight
        
        return 0.0

    def make_steering_decision(
        self,
        agent_id: str,
        action_type: str,
        parameters: Dict[str, Any],
        require_awareness: bool = True
    ) -> SteeringDecision:
        """
        Make a steering decision based on current awareness.
        
        Args:
            agent_id: Agent identifier
            action_type: Type of action to take
            parameters: Action parameters
            require_awareness: Whether to require minimum awareness
            
        Returns:
            SteeringDecision: The decision made
        """
        decision_id = f"dec_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{hash(str(parameters)) % 10000}"
        
        # Calculate awareness score
        awareness_score = self.calculate_awareness_score()
        
        # Check awareness requirement
        if require_awareness and awareness_score < self.decision_threshold:
            decision = SteeringDecision(
                decision_id=decision_id,
                agent_id=agent_id,
                action_type=action_type,
                parameters=parameters,
                awareness_level=self.awareness_level,
                confidence=awareness_score,
                reasoning=f"Insufficient awareness ({awareness_score:.2f} < {self.decision_threshold})",
                timestamp=datetime.utcnow().isoformat(),
                executed=False
            )
        else:
            # Make decision based on context
            decision = self._evaluate_decision(agent_id, action_type, parameters, awareness_score)
        
        self.decision_history.append(decision)
        return decision

    def _evaluate_decision(
        self,
        agent_id: str,
        action_type: str,
        parameters: Dict[str, Any],
        awareness_score: float
    ) -> SteeringDecision:
        """Evaluate and make a decision based on context."""
        decision_id = f"dec_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{hash(str(parameters)) % 10000}"
        
        # Analyze relevant context
        relevant_context = self._get_relevant_context(action_type)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(action_type, parameters, relevant_context, awareness_score)
        
        # Calculate confidence
        confidence = min(awareness_score + self._calculate_context_confidence(relevant_context), 1.0)
        
        decision = SteeringDecision(
            decision_id=decision_id,
            agent_id=agent_id,
            action_type=action_type,
            parameters=parameters,
            awareness_level=self.awareness_level,
            confidence=confidence,
            reasoning=reasoning,
            timestamp=datetime.utcnow().isoformat(),
            executed=False
        )
        
        # Execute if in autonomous mode and confidence is high
        if self.steering_mode == SteeringMode.AUTONOMOUS and confidence >= self.decision_threshold:
            decision.executed = True
            decision.result = self._execute_decision(decision)
        
        return decision

    def _get_relevant_context(self, action_type: str) -> List[AwarenessContext]:
        """Get context relevant to the action type."""
        # Simple relevance matching - can be enhanced with ML
        relevant_contexts = []
        
        for context in reversed(self.context_buffer[-50:]):  # Last 50 contexts
            # Check if context data contains relevant keywords
            context_str = json.dumps(context.data).lower()
            action_keywords = action_type.lower().split('_')
            
            if any(keyword in context_str for keyword in action_keywords):
                relevant_contexts.append(context)
        
        return relevant_contexts

    def _calculate_context_confidence(self, contexts: List[AwarenessContext]) -> float:
        """Calculate confidence based on context quality."""
        if not contexts:
            return 0.0
        
        avg_confidence = sum(c.confidence for c in contexts) / len(contexts)
        
        # Boost confidence if we have diverse context types
        context_types = set(c.context_type for c in contexts)
        diversity_boost = min(len(context_types) * 0.05, 0.2)
        
        return avg_confidence + diversity_boost

    def _generate_reasoning(
        self,
        action_type: str,
        parameters: Dict[str, Any],
        contexts: List[AwarenessContext],
        awareness_score: float
    ) -> str:
        """Generate reasoning for the decision."""
        reasoning_parts = []
        
        reasoning_parts.append(f"Awareness score: {awareness_score:.2f}")
        reasoning_parts.append(f"Contexts analyzed: {len(contexts)}")
        
        if contexts:
            context_types = set(c.context_type.value for c in contexts)
            reasoning_parts.append(f"Context types: {', '.join(context_types)}")
        
        reasoning_parts.append(f"Steering mode: {self.steering_mode.value}")
        
        return " | ".join(reasoning_parts)

    def _execute_decision(self, decision: SteeringDecision) -> Dict[str, Any]:
        """Execute a steering decision (placeholder)."""
        return {
            "status": "executed",
            "decision_id": decision.decision_id,
            "timestamp": datetime.utcnow().isoformat(),
            "action": decision.action_type
        }

    def set_steering_mode(self, mode: SteeringMode) -> None:
        """Set the steering mode."""
        self.steering_mode = mode

    def set_awareness_level(self, level: AwarenessLevel) -> None:
        """Set the awareness level."""
        self.awareness_level = level

    def adjust_context_weights(self, weights: Dict[ContextType, float]) -> bool:
        """
        Adjust context weights for awareness calculation.
        
        Args:
            weights: New weights for context types
            
        Returns:
            True if successful
        """
        # Normalize weights
        total = sum(weights.values())
        if total == 0:
            return False
        
        normalized_weights = {k: v / total for k, v in weights.items()}
        self.context_weights.update(normalized_weights)
        return True

    def record_awareness_metric(
        self,
        metric_name: str,
        value: float,
        context: Optional[Dict[str, Any]] = None
    ) -> AwarenessMetric:
        """
        Record an awareness metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            context: Optional context
            
        Returns:
            AwarenessMetric: Recorded metric
        """
        metric_id = f"metric_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{hash(metric_name) % 1000}"
        
        # Calculate trend
        trend = "stable"
        if self.awareness_metrics:
            last_metric = next((m for m in reversed(self.awareness_metrics) if m.metric_name == metric_name), None)
            if last_metric:
                if value > last_metric.value:
                    trend = "increasing"
                elif value < last_metric.value:
                    trend = "decreasing"
        
        metric = AwarenessMetric(
            metric_id=metric_id,
            metric_name=metric_name,
            value=value,
            trend=trend,
            timestamp=datetime.utcnow().isoformat(),
            context=context
        )
        
        self.awareness_metrics.append(metric)
        
        # Maintain metrics buffer size
        if len(self.awareness_metrics) > 500:
            self.awareness_metrics.pop(0)
        
        return metric

    def get_awareness_summary(self) -> Dict[str, Any]:
        """Get summary of agent awareness."""
        awareness_score = self.calculate_awareness_score()
        
        # Recent metrics
        recent_metrics = self.awareness_metrics[-20:] if self.awareness_metrics else []
        
        # Decision success rate
        if self.decision_history:
            executed_decisions = [d for d in self.decision_history if d.executed]
            success_rate = len(executed_decisions) / len(self.decision_history)
        else:
            success_rate = 0.0
        
        return {
            "awareness_level": self.awareness_level.name,
            "steering_mode": self.steering_mode.value,
            "current_awareness_score": awareness_score,
            "context_buffer_size": len(self.context_buffer),
            "decision_count": len(self.decision_history),
            "success_rate": success_rate,
            "recent_metrics": len(recent_metrics),
            "context_weights": {k.value: v for k, v in self.context_weights.items()}
        }

    def learn_from_feedback(self, decision_id: str, feedback: float) -> None:
        """
        Learn from feedback on a decision.
        
        Args:
            decision_id: Decision identifier
            feedback: Feedback score (0-1, where 1 is positive)
        """
        decision = next((d for d in self.decision_history if d.decision_id == decision_id), None)
        if not decision:
            return
        
        # Adjust learning based on feedback
        if feedback > 0.7:
            # Positive feedback - increase confidence in similar decisions
            self.learning_rate = min(self.learning_rate * 1.1, 0.3)
        elif feedback < 0.3:
            # Negative feedback - decrease confidence
            self.learning_rate = max(self.learning_rate * 0.9, 0.05)

    def clear_old_context(self, age_hours: int = 24) -> int:
        """
        Clear context older than specified age.
        
        Args:
            age_hours: Age threshold in hours
            
        Returns:
            Number of contexts cleared
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=age_hours)
        to_remove = []
        
        for i, context in enumerate(self.context_buffer):
            context_time = datetime.fromisoformat(context.timestamp)
            if context_time < cutoff_time:
                to_remove.append(i)
        
        for i in reversed(to_remove):
            self.context_buffer.pop(i)
        
        return len(to_remove)

    def export_state(self) -> str:
        """Export current state for recovery."""
        state = {
            "awareness_level": self.awareness_level.value,
            "steering_mode": self.steering_mode.value,
            "context_buffer": [asdict(ctx) for ctx in self.context_buffer],
            "decision_history": [asdict(dec) for dec in self.decision_history],
            "awareness_metrics": [asdict(metric) for metric in self.awareness_metrics],
            "context_weights": {k.value: v for k, v in self.context_weights.items()},
            "learning_rate": self.learning_rate,
            "decision_threshold": self.decision_threshold,
            "export_timestamp": datetime.utcnow().isoformat()
        }
        return json.dumps(state, indent=2)

    def import_state(self, state_json: str) -> bool:
        """
        Import state for recovery.
        
        Args:
            state_json: JSON string of exported state
            
        Returns:
            True if import successful
        """
        try:
            state = json.loads(state_json)
            
            # Restore basic settings
            self.awareness_level = AwarenessLevel(state["awareness_level"])
            self.steering_mode = SteeringMode(state["steering_mode"])
            self.learning_rate = state["learning_rate"]
            self.decision_threshold = state["decision_threshold"]
            
            # Restore context weights
            self.context_weights = {
                ContextType(k): v for k, v in state["context_weights"].items()
            }
            
            # Restore context buffer
            for ctx_dict in state["context_buffer"]:
                ctx_dict["context_type"] = ContextType(ctx_dict["context_type"])
                self.context_buffer.append(AwarenessContext(**ctx_dict))
            
            # Restore decision history
            for dec_dict in state["decision_history"]:
                dec_dict["awareness_level"] = AwarenessLevel(dec_dict["awareness_level"])
                self.decision_history.append(SteeringDecision(**dec_dict))
            
            # Restore metrics
            for metric_dict in state["awareness_metrics"]:
                self.awareness_metrics.append(AwarenessMetric(**metric_dict))
            
            return True
        except Exception as e:
            print(f"Error importing state: {e}")
            return False
