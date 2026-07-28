"""
Enhanced Guardrails - Enhanced Safety Guardrails with Cognitive Awareness
Enhances safety guardrails with cognitive awareness, hesitation detection, and action stalling.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from .safety_config import SafetyConfig
from .cognitive_awareness import CognitiveAwareness, AwarenessLevel
from .threat_detection import ThreatDetection, ThreatLevel


class ActionDecision(Enum):
    """Action decision types."""
    PROCEED = "proceed"
    STALL = "stall"
    CANCEL = "cancel"
    DEFER = "defer"
    REJECT = "reject"


@dataclass
class SafetyAssessment:
    """Represents a comprehensive safety assessment."""
    assessment_id: str
    action: str
    action_decision: ActionDecision
    risk_score: float
    hesitation_score: float
    cognitive_awareness_level: AwarenessLevel
    threat_level: ThreatLevel
    reasoning: str
    timestamp: float
    confidence: float


class EnhancedGuardrails:
    """
    Enhanced safety guardrails with cognitive awareness.
    Controls model decisions based on risk, threats, and cognitive assessment.
    """
    
    def __init__(self, config: SafetyConfig, cognitive_awareness: CognitiveAwareness, threat_detection: ThreatDetection):
        """
        Initialize Enhanced Guardrails.
        
        Args:
            config: Safety configuration
            cognitive_awareness: Cognitive awareness instance
            threat_detection: Threat detection instance
        """
        self.config = config
        self.cognitive_awareness = cognitive_awareness
        self.threat_detection = threat_detection
        
        # Action control settings
        self.stall_on_hesitation = config.stall_on_hesitation
        self.cancel_on_high_risk = config.cancel_on_high_risk
        self.hesitation_threshold = config.hesitation_threshold
        self.max_risk_threshold = config.max_risk_threshold
        
        # Assessment history
        self.assessments: Dict[str, SafetyAssessment] = {}
        
        # Stalled actions
        self.stalled_actions: Dict[str, Dict] = {}
    
    def assess_action(
        self,
        action: str,
        user_id: str,
        context: Dict,
        behavior_data: Optional[Dict] = None,
        target_user_id: Optional[str] = None
    ) -> SafetyAssessment:
        """
        Assess an action for safety.
        
        Args:
            action: Action to assess
            user_id: User ID performing action
            context: Current context
            behavior_data: Optional behavior data
            target_user_id: Optional target user ID
            
        Returns:
            SafetyAssessment object
        """
        assessment_id = f"safety_{action}_{user_id}_{datetime.now().timestamp()}"
        
        # Cognitive assessment
        cognitive_assessment = self.cognitive_awareness.assess_situation(user_id, context, behavior_data)
        
        # Threat assessment (if target user involved)
        threat_level = ThreatLevel.NONE
        if target_user_id:
            threat_level, _ = self.threat_detection.assess_user_threat(target_user_id, context, behavior_data)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(cognitive_assessment, threat_level)
        
        # Calculate hesitation score
        hesitation_score = self._calculate_hesitation_score(cognitive_assessment, context)
        
        # Make action decision
        action_decision = self._make_action_decision(
            risk_score,
            hesitation_score,
            cognitive_assessment.awareness_level,
            threat_level
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            action_decision,
            risk_score,
            hesitation_score,
            cognitive_assessment,
            threat_level
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(cognitive_assessment, threat_level)
        
        assessment = SafetyAssessment(
            assessment_id=assessment_id,
            action=action,
            action_decision=action_decision,
            risk_score=risk_score,
            hesitation_score=hesitation_score,
            cognitive_awareness_level=cognitive_assessment.awareness_level,
            threat_level=threat_level,
            reasoning=reasoning,
            timestamp=datetime.now().timestamp(),
            confidence=confidence
        )
        
        self.assessments[assessment_id] = assessment
        
        # Handle stalled actions
        if action_decision == ActionDecision.STALL:
            self.stalled_actions[assessment_id] = {
                'action': action,
                'user_id': user_id,
                'timestamp': datetime.now().timestamp(),
                'context': context
            }
        
        return assessment
    
    def _calculate_risk_score(
        self,
        cognitive_assessment,
        threat_level: ThreatLevel
    ) -> float:
        """Calculate overall risk score."""
        # Base risk from cognitive awareness
        awareness_risk = {
            AwarenessLevel.LOW: 0.1,
            AwarenessLevel.MEDIUM: 0.3,
            AwarenessLevel.HIGH: 0.6,
            AwarenessLevel.CRITICAL: 0.9
        }.get(cognitive_assessment.awareness_level, 0.5)
        
        # Risk from threat level
        threat_risk = {
            ThreatLevel.NONE: 0.0,
            ThreatLevel.LOW: 0.2,
            ThreatLevel.MEDIUM: 0.5,
            ThreatLevel.HIGH: 0.8,
            ThreatLevel.CRITICAL: 1.0
        }.get(threat_level, 0.0)
        
        # Weighted combination (cognitive awareness has higher weight)
        risk_score = (
            awareness_risk * self.config.cognitive_awareness_weight +
            threat_risk * (1 - self.config.cognitive_awareness_weight)
        )
        
        return risk_score
    
    def _calculate_hesitation_score(self, cognitive_assessment, context: Dict) -> float:
        """Calculate hesitation score."""
        # Hesitation based on cognitive confidence
        hesitation = 1.0 - cognitive_assessment.confidence
        
        # Adjust for context factors
        if context.get('uncertainty', 0) > 0.5:
            hesitation += 0.2
        
        if context.get('complexity', 0) > 0.8:
            hesitation += 0.1
        
        return min(hesitation, 1.0)
    
    def _make_action_decision(
        self,
        risk_score: float,
        hesitation_score: float,
        awareness_level: AwarenessLevel,
        threat_level: ThreatLevel
    ) -> ActionDecision:
        """Make action decision based on assessment."""
        # Cancel on high risk
        if self.cancel_on_high_risk and risk_score > self.max_risk_threshold:
            return ActionDecision.CANCEL
        
        # Cancel on critical threat
        if threat_level == ThreatLevel.CRITICAL:
            return ActionDecision.CANCEL
        
        # Stall on hesitation
        if self.stall_on_hesitation and hesitation_score > self.hesitation_threshold:
            return ActionDecision.STALL
        
        # Reject on high threat
        if threat_level == ThreatLevel.HIGH:
            return ActionDecision.REJECT
        
        # Proceed if low risk and no hesitation
        if risk_score < self.max_risk_threshold and hesitation_score < self.hesitation_threshold:
            return ActionDecision.PROCEED
        
        # Defer for manual review
        return ActionDecision.DEFER
    
    def _generate_reasoning(
        self,
        action_decision: ActionDecision,
        risk_score: float,
        hesitation_score: float,
        cognitive_assessment,
        threat_level: ThreatLevel
    ) -> str:
        """Generate reasoning for action decision."""
        reasoning_parts = []
        
        reasoning_parts.append(f"Risk score: {risk_score:.2f}")
        reasoning_parts.append(f"Hesitation score: {hesitation_score:.2f}")
        reasoning_parts.append(f"Awareness level: {cognitive_assessment.awareness_level.value}")
        reasoning_parts.append(f"Threat level: {threat_level.value}")
        
        if action_decision == ActionDecision.CANCEL:
            reasoning_parts.append("Action cancelled due to high risk or critical threat")
        elif action_decision == ActionDecision.STALL:
            reasoning_parts.append("Action stalled due to hesitation")
        elif action_decision == ActionDecision.REJECT:
            reasoning_parts.append("Action rejected due to threat")
        elif action_decision == ActionDecision.PROCEED:
            reasoning_parts.append("Action approved to proceed")
        else:
            reasoning_parts.append("Action deferred for manual review")
        
        return ". ".join(reasoning_parts)
    
    def _calculate_confidence(self, cognitive_assessment, threat_level: ThreatLevel) -> float:
        """Calculate confidence in assessment."""
        # Base confidence from cognitive assessment
        confidence = cognitive_assessment.confidence
        
        # Reduce confidence if threat detected
        if threat_level != ThreatLevel.NONE:
            confidence *= 0.7
        
        return confidence
    
    def release_stalled_action(self, assessment_id: str) -> bool:
        """
        Release a stalled action.
        
        Args:
            assessment_id: Assessment ID
            
        Returns:
            True if released successfully
        """
        if assessment_id not in self.stalled_actions:
            return False
        
        del self.stalled_actions[assessment_id]
        return True
    
    def get_stalled_actions(self) -> List[Dict]:
        """Get all stalled actions."""
        return list(self.stalled_actions.values())
    
    def get_assessment(self, assessment_id: str) -> Optional[SafetyAssessment]:
        """Get an assessment by ID."""
        return self.assessments.get(assessment_id)
    
    def get_user_assessments(self, user_id: str) -> List[SafetyAssessment]:
        """Get all assessments for a user."""
        return [
            assessment for assessment in self.assessments.values()
            if user_id in assessment.assessment_id
        ]
    
    def get_safety_statistics(self) -> Dict[str, any]:
        """
        Get statistics about safety assessments.
        
        Returns:
            Dictionary containing safety statistics
        """
        if not self.assessments:
            return {
                'total_assessments': 0
            }
        
        decision_counts = {}
        for assessment in self.assessments.values():
            decision = assessment.action_decision.value
            decision_counts[decision] = decision_counts.get(decision, 0) + 1
        
        avg_risk = sum(a.risk_score for a in self.assessments.values()) / len(self.assessments)
        avg_hesitation = sum(a.hesitation_score for a in self.assessments.values()) / len(self.assessments)
        
        return {
            'total_assessments': len(self.assessments),
            'decision_distribution': decision_counts,
            'average_risk_score': avg_risk,
            'average_hesitation_score': avg_hesitation,
            'stalled_actions': len(self.stalled_actions),
            'cancelled_actions': decision_counts.get('cancel', 0),
            'proceeded_actions': decision_counts.get('proceed', 0)
        }
