"""
Cognitive Awareness - Cognitive Awareness and Deduction
Enhances safety guardrails with cognitive awareness and deduction capabilities.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from .safety_config import SafetyConfig


class AwarenessLevel(Enum):
    """Levels of cognitive awareness."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DeductionType(Enum):
    """Types of cognitive deductions."""
    PATTERN_RECOGNITION = "pattern_recognition"
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"
    CONTEXT_AWARENESS = "context_awareness"
    THREAT_ASSESSMENT = "threat_assessment"
    RISK_EVALUATION = "risk_evaluation"


@dataclass
class CognitiveAssessment:
    """Represents a cognitive assessment."""
    assessment_id: str
    awareness_level: AwarenessLevel
    confidence: float
    deductions: List[Dict]
    patterns_detected: List[str]
    behavioral_indicators: Dict[str, float]
    context_factors: Dict[str, any]
    timestamp: float


@dataclass
class DeductionResult:
    """Represents a deduction result."""
    deduction_type: DeductionType
    conclusion: str
    confidence: float
    evidence: List[str]
    risk_score: float


class CognitiveAwareness:
    """
    Cognitive awareness and deduction system.
    Uses cognitive awareness and deduction more than experience for safety decisions.
    """
    
    def __init__(self, config: SafetyConfig):
        """
        Initialize Cognitive Awareness.
        
        Args:
            config: Safety configuration
        """
        self.config = config
        
        # Cognitive config
        cognitive_config = config.get_cognitive_awareness_config()
        self.deduction_priority = cognitive_config.get('deduction_priority', 0.7)
        self.pattern_recognition_enabled = cognitive_config.get('pattern_recognition', True)
        self.behavioral_analysis_enabled = cognitive_config.get('behavioral_analysis', True)
        self.context_awareness_enabled = cognitive_config.get('context_awareness', True)
        
        # Assessment history
        self.assessments: Dict[str, CognitiveAssessment] = {}
        
        # Pattern database
        self.pattern_database: Dict[str, List[Dict]] = {
            'malicious_patterns': [],
            'safe_patterns': [],
            'suspicious_patterns': []
        }
    
    def assess_situation(
        self,
        user_id: str,
        context: Dict,
        behavior_data: Optional[Dict] = None
    ) -> CognitiveAssessment:
        """
        Assess a situation using cognitive awareness and deduction.
        
        Args:
            user_id: User ID to assess
            context: Current context
            behavior_data: Optional behavior data
            
        Returns:
            CognitiveAssessment object
        """
        assessment_id = f"assessment_{user_id}_{datetime.now().timestamp()}"
        
        # Perform deductions
        deductions = []
        
        if self.pattern_recognition_enabled:
            pattern_deductions = self._perform_pattern_recognition(context, behavior_data)
            deductions.extend(pattern_deductions)
        
        if self.behavioral_analysis_enabled:
            behavioral_deductions = self._perform_behavioral_analysis(behavior_data)
            deductions.extend(behavioral_deductions)
        
        if self.context_awareness_enabled:
            context_deductions = self._perform_context_analysis(context)
            deductions.extend(context_deductions)
        
        # Calculate awareness level
        awareness_level = self._calculate_awareness_level(deductions)
        
        # Calculate confidence based on deduction priority
        confidence = self._calculate_confidence(deductions)
        
        # Detect patterns
        patterns_detected = self._detect_patterns(context, behavior_data)
        
        # Extract behavioral indicators
        behavioral_indicators = self._extract_behavioral_indicators(behavior_data)
        
        assessment = CognitiveAssessment(
            assessment_id=assessment_id,
            awareness_level=awareness_level,
            confidence=confidence,
            deductions=deductions,
            patterns_detected=patterns_detected,
            behavioral_indicators=behavioral_indicators,
            context_factors=context,
            timestamp=datetime.now().timestamp()
        )
        
        self.assessments[assessment_id] = assessment
        
        return assessment
    
    def _perform_pattern_recognition(
        self,
        context: Dict,
        behavior_data: Optional[Dict]
    ) -> List[Dict]:
        """Perform pattern recognition deduction."""
        deductions = []
        
        if not behavior_data:
            return deductions
        
        # Check for malicious patterns
        for pattern in self.pattern_database['malicious_patterns']:
            if self._matches_pattern(behavior_data, pattern):
                deductions.append({
                    'type': DeductionType.PATTERN_RECOGNITION,
                    'conclusion': 'Malicious pattern detected',
                    'confidence': 0.8,
                    'risk_score': 0.9
                })
        
        # Check for suspicious patterns
        for pattern in self.pattern_database['suspicious_patterns']:
            if self._matches_pattern(behavior_data, pattern):
                deductions.append({
                    'type': DeductionType.PATTERN_RECOGNITION,
                    'conclusion': 'Suspicious pattern detected',
                    'confidence': 0.6,
                    'risk_score': 0.5
                })
        
        return deductions
    
    def _perform_behavioral_analysis(self, behavior_data: Optional[Dict]) -> List[Dict]:
        """Perform behavioral analysis deduction."""
        deductions = []
        
        if not behavior_data:
            return deductions
        
        # Analyze behavior patterns
        urgency = behavior_data.get('urgency', 0.5)
        frequency = behavior_data.get('frequency', 1.0)
        complexity = behavior_data.get('complexity', 0.5)
        
        # High urgency + high frequency = suspicious
        if urgency > 0.8 and frequency > 2.0:
            deductions.append({
                'type': DeductionType.BEHAVIORAL_ANALYSIS,
                'conclusion': 'High urgency and frequency detected',
                'confidence': 0.7,
                'risk_score': 0.6
            })
        
        # Unusual complexity
        if complexity > 0.9:
            deductions.append({
                'type': DeductionType.BEHAVIORAL_ANALYSIS,
                'conclusion': 'Unusual complexity detected',
                'confidence': 0.5,
                'risk_score': 0.4
            })
        
        return deductions
    
    def _perform_context_analysis(self, context: Dict) -> List[Dict]:
        """Perform context analysis deduction."""
        deductions = []
        
        # Check for unusual context
        time_of_day = context.get('time_of_day', 12)
        location = context.get('location', 'unknown')
        device = context.get('device', 'unknown')
        
        # Unusual time (late night)
        if time_of_day < 6 or time_of_day > 22:
            deductions.append({
                'type': DeductionType.CONTEXT_AWARENESS,
                'conclusion': 'Unusual time of day',
                'confidence': 0.4,
                'risk_score': 0.3
            })
        
        # Unknown location
        if location == 'unknown':
            deductions.append({
                'type': DeductionType.CONTEXT_AWARENESS,
                'conclusion': 'Unknown location',
                'confidence': 0.5,
                'risk_score': 0.4
            })
        
        return deductions
    
    def _calculate_awareness_level(self, deductions: List[Dict]) -> AwarenessLevel:
        """Calculate overall awareness level from deductions."""
        if not deductions:
            return AwarenessLevel.LOW
        
        total_risk = sum(d.get('risk_score', 0) for d in deductions)
        avg_risk = total_risk / len(deductions)
        
        if avg_risk > 0.8:
            return AwarenessLevel.CRITICAL
        elif avg_risk > 0.6:
            return AwarenessLevel.HIGH
        elif avg_risk > 0.3:
            return AwarenessLevel.MEDIUM
        else:
            return AwarenessLevel.LOW
    
    def _calculate_confidence(self, deductions: List[Dict]) -> float:
        """Calculate confidence in assessment."""
        if not deductions:
            return 0.5
        
        # Weight by deduction priority (cognitive awareness > experience)
        confidence_sum = sum(d.get('confidence', 0.5) * self.deduction_priority for d in deductions)
        return min(confidence_sum / len(deductions), 1.0)
    
    def _detect_patterns(self, context: Dict, behavior_data: Optional[Dict]) -> List[str]:
        """Detect patterns in context and behavior."""
        patterns = []
        
        if behavior_data:
            if behavior_data.get('repetitive', False):
                patterns.append('repetitive_behavior')
            if behavior_data.get('rapid', False):
                patterns.append('rapid_actions')
            if behavior_data.get('unusual', False):
                patterns.append('unusual_pattern')
        
        return patterns
    
    def _extract_behavioral_indicators(self, behavior_data: Optional[Dict]) -> Dict[str, float]:
        """Extract behavioral indicators."""
        if not behavior_data:
            return {}
        
        return {
            'urgency': behavior_data.get('urgency', 0.5),
            'frequency': behavior_data.get('frequency', 1.0),
            'complexity': behavior_data.get('complexity', 0.5),
            'consistency': behavior_data.get('consistency', 0.5)
        }
    
    def _matches_pattern(self, data: Dict, pattern: Dict) -> bool:
        """Check if data matches a pattern."""
        for key, value in pattern.items():
            if key not in data:
                return False
            if isinstance(value, (int, float)):
                if abs(data[key] - value) > 0.1:
                    return False
            elif data[key] != value:
                return False
        return True
    
    def add_malicious_pattern(self, pattern: Dict):
        """Add a malicious pattern to the database."""
        self.pattern_database['malicious_patterns'].append(pattern)
    
    def add_suspicious_pattern(self, pattern: Dict):
        """Add a suspicious pattern to the database."""
        self.pattern_database['suspicious_patterns'].append(pattern)
    
    def get_assessment(self, assessment_id: str) -> Optional[CognitiveAssessment]:
        """Get an assessment by ID."""
        return self.assessments.get(assessment_id)
    
    def get_user_assessments(self, user_id: str) -> List[CognitiveAssessment]:
        """Get all assessments for a user."""
        return [
            assessment for assessment in self.assessments.values()
            if user_id in assessment.assessment_id
        ]
