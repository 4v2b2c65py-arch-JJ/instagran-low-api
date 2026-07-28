"""
Threat Detection - Risk/Threat Detection for Other Users
Detects risks and threats from other users before interaction.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from .safety_config import SafetyConfig


class ThreatLevel(Enum):
    """Levels of threats."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(Enum):
    """Types of threats."""
    MALICIOUS_BEHAVIOR = "malicious_behavior"
    UNUSUAL_ACTIVITY = "unusual_activity"
    DATA_MANIPULATION = "data_manipulation"
    PERMISSION_ABUSE = "permission_abuse"
    SOCIAL_ENGINEERING = "social_engineering"
    SYSTEM_COMPROMISE = "system_compromise"


@dataclass
class Threat:
    """Represents a detected threat."""
    threat_id: str
    threat_type: ThreatType
    threat_level: ThreatLevel
    source_user_id: str
    description: str
    evidence: List[str]
    confidence: float
    timestamp: float
    blocked: bool = False


class ThreatDetection:
    """
    Detects risks and threats from other users.
    Blocks interactions based on threat assessment.
    """
    
    def __init__(self, config: SafetyConfig):
        """
        Initialize Threat Detection.
        
        Args:
            config: Safety configuration
        """
        self.config = config
        
        # Threat detection config
        threat_config = config.get_threat_detection_config()
        self.enabled = threat_config.get('enabled', True)
        self.sensitivity = config.threat_detection_sensitivity
        self.check_patterns = threat_config.get('check_patterns', [])
        self.block_on_threat = threat_config.get('block_on_threat', True)
        self.alert_on_suspicious = threat_config.get('alert_on_suspicious', True)
        
        # Threat database
        self.detected_threats: Dict[str, Threat] = {}
        self.user_threat_history: Dict[str, List[str]] = {}  # key: user_id, value: list of threat_ids
        
        # Threat patterns
        self.threat_patterns = {
            'malicious_behavior': [
                {'pattern': 'rapid_requests', 'threshold': 10},
                {'pattern': 'unusual_permissions', 'threshold': 5},
                {'pattern': 'data_extraction', 'threshold': 3}
            ],
            'unusual_activity': [
                {'pattern': 'time_anomaly', 'threshold': 0.8},
                {'pattern': 'location_anomaly', 'threshold': 0.7},
                {'pattern': 'device_anomaly', 'threshold': 0.6}
            ],
            'data_manipulation': [
                {'pattern': 'data_tampering', 'threshold': 1},
                {'pattern': 'signature_mismatch', 'threshold': 1}
            ],
            'permission_abuse': [
                {'pattern': 'excessive_requests', 'threshold': 20},
                {'pattern': 'privilege_escalation', 'threshold': 1}
            ]
        }
    
    def assess_user_threat(
        self,
        user_id: str,
        user_data: Dict,
        behavior_data: Optional[Dict] = None
    ) -> Tuple[ThreatLevel, List[Threat]]:
        """
        Assess threat level of a user.
        
        Args:
            user_id: User ID to assess
            user_data: User data
            behavior_data: Optional behavior data
            
        Returns:
            Tuple of (ThreatLevel, List of Threat objects)
        """
        detected_threats = []
        
        # Check each threat pattern type
        for pattern_type in self.check_patterns:
            threats = self._check_threat_pattern(
                user_id,
                pattern_type,
                user_data,
                behavior_data
            )
            detected_threats.extend(threats)
        
        # Determine overall threat level
        threat_level = self._calculate_threat_level(detected_threats)
        
        # Block if high threat
        if self.block_on_threat and threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            for threat in detected_threats:
                threat.blocked = True
        
        return threat_level, detected_threats
    
    def _check_threat_pattern(
        self,
        user_id: str,
        pattern_type: str,
        user_data: Dict,
        behavior_data: Optional[Dict]
    ) -> List[Threat]:
        """Check for specific threat patterns."""
        threats = []
        
        if pattern_type not in self.threat_patterns:
            return threats
        
        patterns = self.threat_patterns[pattern_type]
        
        for pattern in patterns:
            if self._matches_threat_pattern(pattern, user_data, behavior_data):
                threat_id = f"threat_{pattern_type}_{user_id}_{datetime.now().timestamp()}"
                
                threat = Threat(
                    threat_id=threat_id,
                    threat_type=ThreatType(pattern_type),
                    threat_level=self._determine_pattern_severity(pattern),
                    source_user_id=user_id,
                    description=f"{pattern_type} detected: {pattern['pattern']}",
                    evidence=[pattern['pattern']],
                    confidence=self.sensitivity,
                    timestamp=datetime.now().timestamp()
                )
                
                self.detected_threats[threat_id] = threat
                
                if user_id not in self.user_threat_history:
                    self.user_threat_history[user_id] = []
                self.user_threat_history[user_id].append(threat_id)
                
                threats.append(threat)
        
        return threats
    
    def _matches_threat_pattern(
        self,
        pattern: Dict,
        user_data: Dict,
        behavior_data: Optional[Dict]
    ) -> bool:
        """Check if data matches a threat pattern."""
        pattern_name = pattern['pattern']
        threshold = pattern['threshold']
        
        # Check user data
        if pattern_name in user_data:
            value = user_data[pattern_name]
            if isinstance(value, (int, float)):
                return value >= threshold
        
        # Check behavior data
        if behavior_data and pattern_name in behavior_data:
            value = behavior_data[pattern_name]
            if isinstance(value, (int, float)):
                return value >= threshold
        
        return False
    
    def _determine_pattern_severity(self, pattern: Dict) -> ThreatLevel:
        """Determine threat level based on pattern."""
        threshold = pattern['threshold']
        
        if threshold >= 10:
            return ThreatLevel.CRITICAL
        elif threshold >= 5:
            return ThreatLevel.HIGH
        elif threshold >= 3:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    def _calculate_threat_level(self, threats: List[Threat]) -> ThreatLevel:
        """Calculate overall threat level from detected threats."""
        if not threats:
            return ThreatLevel.NONE
        
        # Count threats by level
        level_counts = {}
        for threat in threats:
            level = threat.threat_level
            level_counts[level] = level_counts.get(level, 0) + 1
        
        # Determine overall level
        if ThreatLevel.CRITICAL in level_counts:
            return ThreatLevel.CRITICAL
        elif ThreatLevel.HIGH in level_counts:
            return ThreatLevel.HIGH
        elif level_counts.get(ThreatLevel.MEDIUM, 0) >= 2:
            return ThreatLevel.HIGH
        elif ThreatLevel.MEDIUM in level_counts:
            return ThreatLevel.MEDIUM
        elif level_counts.get(ThreatLevel.LOW, 0) >= 3:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    def is_user_blocked(self, user_id: str) -> bool:
        """
        Check if a user is blocked due to threats.
        
        Args:
            user_id: User ID to check
            
        Returns:
            True if user is blocked
        """
        if user_id not in self.user_threat_history:
            return False
        
        for threat_id in self.user_threat_history[user_id]:
            threat = self.detected_threats.get(threat_id)
            if threat and threat.blocked:
                return True
        
        return False
    
    def get_user_threats(self, user_id: str) -> List[Threat]:
        """
        Get all threats for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of Threat objects
        """
        if user_id not in self.user_threat_history:
            return []
        
        return [
            self.detected_threats[threat_id]
            for threat_id in self.user_threat_history[user_id]
            if threat_id in self.detected_threats
        ]
    
    def clear_user_threats(self, user_id: str):
        """
        Clear threats for a user.
        
        Args:
            user_id: User ID
        """
        if user_id in self.user_threat_history:
            for threat_id in self.user_threat_history[user_id]:
                if threat_id in self.detected_threats:
                    del self.detected_threats[threat_id]
            del self.user_threat_history[user_id]
    
    def get_threat_statistics(self) -> Dict[str, any]:
        """
        Get statistics about detected threats.
        
        Returns:
            Dictionary containing threat statistics
        """
        total_threats = len(self.detected_threats)
        blocked_threats = sum(1 for t in self.detected_threats.values() if t.blocked)
        
        type_counts = {}
        for threat in self.detected_threats.values():
            ttype = threat.threat_type.value
            type_counts[ttype] = type_counts.get(ttype, 0) + 1
        
        level_counts = {}
        for threat in self.detected_threats.values():
            level = threat.threat_level.value
            level_counts[level] = level_counts.get(level, 0) + 1
        
        return {
            'total_threats': total_threats,
            'blocked_threats': blocked_threats,
            'blocked_users': len([uid for uid in self.user_threat_history if self.is_user_blocked(uid)]),
            'threat_type_distribution': type_counts,
            'threat_level_distribution': level_counts
        }
