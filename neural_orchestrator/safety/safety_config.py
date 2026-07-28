"""
Safety Config - JSON-based Safety Protocol Configuration
Loads and manages safety protocol configuration from JSON.
"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class SafetyConfig:
    """Safety protocol configuration loaded from JSON."""
    version: str
    enabled: bool
    mode: str
    max_risk_threshold: float
    threat_detection_sensitivity: float
    hesitation_threshold: float
    cognitive_awareness_weight: float
    experience_weight: float
    stall_on_hesitation: bool
    cancel_on_high_risk: bool
    require_handshake: bool
    allow_autonomous_rejection: bool
    handshake_enabled: bool
    handshake_timeout: int
    max_retries: int
    require_cross_validation: bool
    validate_user_data: bool
    
    def __init__(self, config_path: str = "safety_protocol.json"):
        """
        Load safety configuration from JSON file.
        
        Args:
            config_path: Path to safety_protocol.json file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self._parse_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            # Try to load from current directory
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            
            # Try to load from parent directory
            parent_path = os.path.join('..', self.config_path)
            if os.path.exists(parent_path):
                with open(parent_path, 'r') as f:
                    return json.load(f)
            
            # Return default config if file not found
            return self._get_default_config()
        except Exception as e:
            print(f"Error loading safety config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default safety configuration."""
        return {
            "safety_protocol": {
                "version": "1.0",
                "enabled": True,
                "mode": "strict",
                "risk_assessment": {
                    "max_risk_threshold": 0.3,
                    "threat_detection_sensitivity": 0.8,
                    "hesitation_threshold": 0.5,
                    "cognitive_awareness_weight": 0.6,
                    "experience_weight": 0.4
                },
                "action_control": {
                    "stall_on_hesitation": True,
                    "cancel_on_high_risk": True,
                    "require_handshake": True,
                    "allow_autonomous_rejection": True
                },
                "handshake_protocol": {
                    "enabled": True,
                    "timeout_seconds": 30,
                    "max_retries": 3,
                    "require_cross_validation": True,
                    "validate_user_data": True,
                    "check_protocol_compatibility": True
                }
            }
        }
    
    def _parse_config(self):
        """Parse configuration into attributes."""
        protocol = self.config.get("safety_protocol", {})
        
        self.version = protocol.get("version", "1.0")
        self.enabled = protocol.get("enabled", True)
        self.mode = protocol.get("mode", "strict")
        
        risk_assessment = protocol.get("risk_assessment", {})
        self.max_risk_threshold = risk_assessment.get("max_risk_threshold", 0.3)
        self.threat_detection_sensitivity = risk_assessment.get("threat_detection_sensitivity", 0.8)
        self.hesitation_threshold = risk_assessment.get("hesitation_threshold", 0.5)
        self.cognitive_awareness_weight = risk_assessment.get("cognitive_awareness_weight", 0.6)
        self.experience_weight = risk_assessment.get("experience_weight", 0.4)
        
        action_control = protocol.get("action_control", {})
        self.stall_on_hesitation = action_control.get("stall_on_hesitation", True)
        self.cancel_on_high_risk = action_control.get("cancel_on_high_risk", True)
        self.require_handshake = action_control.get("require_handshake", True)
        self.allow_autonomous_rejection = action_control.get("allow_autonomous_rejection", True)
        
        handshake = protocol.get("handshake_protocol", {})
        self.handshake_enabled = handshake.get("enabled", True)
        self.handshake_timeout = handshake.get("timeout_seconds", 30)
        self.max_retries = handshake.get("max_retries", 3)
        self.require_cross_validation = handshake.get("require_cross_validation", True)
        self.validate_user_data = handshake.get("validate_user_data", True)
    
    def reload(self):
        """Reload configuration from file."""
        self.config = self._load_config()
        self._parse_config()
    
    def get_connection_rules(self) -> Dict[str, list]:
        """Get connection rejection/acceptance rules."""
        protocol = self.config.get("safety_protocol", {})
        connection_rules = protocol.get("connection_rules", {})
        return connection_rules
    
    def get_threat_detection_config(self) -> Dict[str, Any]:
        """Get threat detection configuration."""
        protocol = self.config.get("safety_protocol", {})
        return protocol.get("threat_detection", {})
    
    def get_cognitive_awareness_config(self) -> Dict[str, Any]:
        """Get cognitive awareness configuration."""
        protocol = self.config.get("safety_protocol", {})
        return protocol.get("cognitive_awareness", {})
    
    def get_user_validation_config(self) -> Dict[str, Any]:
        """Get user validation configuration."""
        protocol = self.config.get("safety_protocol", {})
        return protocol.get("user_validation", {})
    
    def get_emergency_protocols(self) -> Dict[str, list]:
        """Get emergency protocol triggers."""
        protocol = self.config.get("safety_protocol", {})
        return protocol.get("emergency_protocols", {})
