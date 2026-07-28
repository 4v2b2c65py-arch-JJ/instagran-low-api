"""
Safety Guardrails - Safety Guardrails for Autonomous Actions
Ensures autonomous actions remain within safe boundaries.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class SafetyLevel(Enum):
    """Safety levels for autonomous actions."""
    SAFE = "safe"
    CAUTION = "caution"
    DANGER = "danger"
    BLOCKED = "blocked"


class RiskCategory(Enum):
    """Categories of risks to monitor."""
    DATA_PRIVACY = "data_privacy"
    FINANCIAL = "financial"
    SYSTEM_INTEGRITY = "system_integrity"
    USER_CONSENT = "user_consent"
    LEGAL_COMPLIANCE = "legal_compliance"
    RESOURCE_USAGE = "resource_usage"


@dataclass
class SafetyCheck:
    """Represents a safety check result."""
    check_id: str
    action: str
    safety_level: SafetyLevel
    risk_categories: List[RiskCategory]
    confidence: float
    reasoning: str
    timestamp: float
    approved: bool


class SafetyGuardrails:
    """
    Ensures autonomous actions remain within safe boundaries.
    Validates actions against safety rules and risk thresholds.
    """
    
    def __init__(self, strict_mode: bool = False):
        """
        Initialize the Safety Guardrails.
        
        Args:
            strict_mode: If True, blocks all potentially risky actions
        """
        self.strict_mode = strict_mode
        
        # Safety rules
        self.blocked_actions = {
            'delete_account',
            'make_payment',
            'share_sensitive_data',
            'install_unverified_software',
            'modify_system_settings'
        }
        
        self.caution_actions = {
            'post_content',
            'send_message',
            'download_file',
            'change_password',
            'grant_permissions'
        }
        
        # Risk thresholds
        self.risk_thresholds = {
            RiskCategory.DATA_PRIVACY: 0.8,
            RiskCategory.FINANCIAL: 0.9,
            RiskCategory.SYSTEM_INTEGRITY: 0.7,
            RiskCategory.USER_CONSENT: 0.6,
            RiskCategory.LEGAL_COMPLIANCE: 0.9,
            RiskCategory.RESOURCE_USAGE: 0.5
        }
        
        # Safety check history
        self.safety_history: List[SafetyCheck] = []
        
        # Violation tracking
        self.violation_count = 0
        self.recent_violations: List[SafetyCheck] = []
    
    def check_action_safety(
        self,
        action: str,
        parameters: Dict[str, any],
        context: Optional[Dict[str, any]] = None
    ) -> SafetyCheck:
        """
        Check if an action is safe to execute.
        
        Args:
            action: Action to check
            parameters: Action parameters
            context: Current context
            
        Returns:
            SafetyCheck object
        """
        risk_categories = self._identify_risk_categories(action, parameters)
        safety_level = self._determine_safety_level(action, risk_categories)
        confidence = self._calculate_safety_confidence(action, parameters, context)
        reasoning = self._generate_safety_reasoning(action, risk_categories, safety_level)
        
        # Determine approval based on safety level and strict mode
        approved = self._is_action_approved(safety_level, confidence)
        
        safety_check = SafetyCheck(
            check_id=f"safety_{len(self.safety_history)}_{datetime.now().timestamp()}",
            action=action,
            safety_level=safety_level,
            risk_categories=risk_categories,
            confidence=confidence,
            reasoning=reasoning,
            timestamp=datetime.now().timestamp(),
            approved=approved
        )
        
        self.safety_history.append(safety_check)
        
        # Track violations
        if not approved:
            self.violation_count += 1
            self.recent_violations.append(safety_check)
            if len(self.recent_violations) > 100:
                self.recent_violations.pop(0)
        
        return safety_check
    
    def _identify_risk_categories(self, action: str, parameters: Dict[str, any]) -> List[RiskCategory]:
        """
        Identify risk categories for an action.
        
        Args:
            action: Action to analyze
            parameters: Action parameters
            
        Returns:
            List of RiskCategory enums
        """
        risk_categories = []
        
        # Check for data privacy risks
        if any(key in parameters for key in ['personal_data', 'user_info', 'contact_list']):
            risk_categories.append(RiskCategory.DATA_PRIVACY)
        
        # Check for financial risks
        if any(key in parameters for key in ['payment', 'purchase', 'transaction', 'credit_card']):
            risk_categories.append(RiskCategory.FINANCIAL)
        
        # Check for system integrity risks
        if action in ['delete', 'remove', 'uninstall', 'modify_system']:
            risk_categories.append(RiskCategory.SYSTEM_INTEGRITY)
        
        # Check for user consent risks
        if action in ['post', 'share', 'publish', 'send']:
            risk_categories.append(RiskCategory.USER_CONSENT)
        
        # Check for legal compliance risks
        if any(key in parameters for key in ['contract', 'agreement', 'legal', 'terms']):
            risk_categories.append(RiskCategory.LEGAL_COMPLIANCE)
        
        # Check for resource usage risks
        if action in ['download', 'upload', 'stream', 'install']:
            risk_categories.append(RiskCategory.RESOURCE_USAGE)
        
        return risk_categories
    
    def _determine_safety_level(self, action: str, risk_categories: List[RiskCategory]) -> SafetyLevel:
        """
        Determine safety level based on action and risks.
        
        Args:
            action: Action to evaluate
            risk_categories: Identified risk categories
            
        Returns:
            SafetyLevel enum
        """
        # Check blocked actions
        if action in self.blocked_actions:
            return SafetyLevel.BLOCKED
        
        # Check caution actions
        if action in self.caution_actions:
            if len(risk_categories) > 2:
                return SafetyLevel.DANGER
            return SafetyLevel.CAUTION
        
        # Evaluate based on risk categories
        high_risk_categories = [
            RiskCategory.FINANCIAL,
            RiskCategory.LEGAL_COMPLIANCE,
            RiskCategory.DATA_PRIVACY
        ]
        
        if any(cat in risk_categories for cat in high_risk_categories):
            return SafetyLevel.CAUTION
        
        return SafetyLevel.SAFE
    
    def _calculate_safety_confidence(
        self,
        action: str,
        parameters: Dict[str, any],
        context: Optional[Dict[str, any]]
    ) -> float:
        """
        Calculate confidence in safety assessment.
        
        Args:
            action: Action being checked
            parameters: Action parameters
            context: Current context
            
        Returns:
            Confidence score (0-1)
        """
        base_confidence = 0.5
        
        # Adjust based on action type
        if action in self.blocked_actions:
            base_confidence = 0.1
        elif action in self.caution_actions:
            base_confidence = 0.4
        
        # Adjust based on parameters
        if parameters.get('user_confirmed', False):
            base_confidence += 0.3
        
        if parameters.get('verified', False):
            base_confidence += 0.2
        
        # Adjust based on context
        if context and context.get('safe_mode', False):
            base_confidence += 0.1
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def _generate_safety_reasoning(
        self,
        action: str,
        risk_categories: List[RiskCategory],
        safety_level: SafetyLevel
    ) -> str:
        """
        Generate reasoning for safety decision.
        
        Args:
            action: Action being evaluated
            risk_categories: Identified risk categories
            safety_level: Determined safety level
            
        Returns:
            Reasoning string
        """
        reasoning = f"Action '{action}' assessed as {safety_level.value}. "
        
        if risk_categories:
            reasoning += f"Risk categories: {', '.join([rc.value for rc in risk_categories])}. "
        
        if safety_level == SafetyLevel.BLOCKED:
            reasoning += "Action is blocked due to safety policy."
        elif safety_level == SafetyLevel.DANGER:
            reasoning += "Action poses significant risk and requires explicit approval."
        elif safety_level == SafetyLevel.CAUTION:
            reasoning += "Action requires caution and monitoring."
        else:
            reasoning += "Action is considered safe."
        
        return reasoning
    
    def _is_action_approved(self, safety_level: SafetyLevel, confidence: float) -> bool:
        """
        Determine if action is approved based on safety level and confidence.
        
        Args:
            safety_level: Safety level of action
            confidence: Confidence in safety assessment
            
        Returns:
            True if approved, False otherwise
        """
        if self.strict_mode:
            # In strict mode, only safe actions are approved
            return safety_level == SafetyLevel.SAFE
        
        # Normal mode
        if safety_level == SafetyLevel.BLOCKED:
            return False
        elif safety_level == SafetyLevel.DANGER:
            return confidence > 0.8
        elif safety_level == SafetyLevel.CAUTION:
            return confidence > 0.5
        else:
            return True
    
    def add_blocked_action(self, action: str):
        """
        Add an action to the blocked list.
        
        Args:
            action: Action to block
        """
        self.blocked_actions.add(action)
    
    def remove_blocked_action(self, action: str):
        """
        Remove an action from the blocked list.
        
        Args:
            action: Action to unblock
        """
        self.blocked_actions.discard(action)
    
    def add_caution_action(self, action: str):
        """
        Add an action to the caution list.
        
        Args:
            action: Action to add caution for
        """
        self.caution_actions.add(action)
    
    def set_risk_threshold(self, category: RiskCategory, threshold: float):
        """
        Set risk threshold for a category.
        
        Args:
            category: Risk category
            threshold: Threshold value (0-1)
        """
        self.risk_thresholds[category] = min(max(threshold, 0.0), 1.0)
    
    def get_safety_statistics(self) -> Dict[str, any]:
        """
        Get statistics about safety checks.
        
        Returns:
            Dictionary containing safety statistics
        """
        if not self.safety_history:
            return {
                'total_checks': 0,
                'approved_count': 0,
                'blocked_count': 0
            }
        
        approved_count = sum(1 for check in self.safety_history if check.approved)
        blocked_count = len(self.safety_history) - approved_count
        
        safety_level_counts = {}
        for check in self.safety_history:
            level = check.safety_level.value
            safety_level_counts[level] = safety_level_counts.get(level, 0) + 1
        
        return {
            'total_checks': len(self.safety_history),
            'approved_count': approved_count,
            'blocked_count': blocked_count,
            'approval_rate': approved_count / len(self.safety_history),
            'safety_level_distribution': safety_level_counts,
            'total_violations': self.violation_count,
            'recent_violations': len(self.recent_violations),
            'strict_mode': self.strict_mode
        }
    
    def get_recent_violations(self, limit: int = 10) -> List[SafetyCheck]:
        """
        Get recent safety violations.
        
        Args:
            limit: Maximum number of violations to return
            
        Returns:
            List of recent SafetyCheck objects
        """
        return self.recent_violations[-limit:] if self.recent_violations else []
    
    def toggle_strict_mode(self):
        """Toggle strict mode on/off."""
        self.strict_mode = not self.strict_mode
    
    def clear_history(self):
        """Clear safety check history."""
        self.safety_history.clear()
        self.recent_violations.clear()
