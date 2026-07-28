"""
Age Estimator - User Age Estimation and Node Count Calculation
Estimates user age and calculates corresponding node count for knowledge base.
"""

from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
from datetime import datetime, date
import numpy as np


@dataclass
class AgeEstimate:
    """Represents an age estimate."""
    estimated_age: float
    confidence: float
    date_of_birth: Optional[date]
    estimated_node_count: int
    calibration_factor: float
    timestamp: float


class AgeEstimator:
    """
    Estimates user age and calculates corresponding node count.
    Uses date of birth to estimate time of age and calibrates estimates.
    """
    
    # Base node count per year (9.4M nodes for 18 years = ~522,222 nodes/year)
    BASE_NODES_PER_YEAR = 522222
    
    # Node count range
    MIN_NODE_COUNT = 1
    MAX_NODE_COUNT = 10_000_000  # 10 million max
    
    def __init__(self, calibration_sensitivity: float = 0.1):
        """
        Initialize the Age Estimator.
        
        Args:
            calibration_sensitivity: How sensitive the calibration is to new data
        """
        self.calibration_sensitivity = calibration_sensitivity
        
        # Current estimate
        self.current_estimate: Optional[AgeEstimate] = None
        
        # Calibration history
        self.calibration_history: List[Dict] = []
        
        # Estimation parameters
        self.base_age = 18.0  # Reference age (18 years = 9.4M nodes)
        self.base_node_count = 9_400_000  # Reference node count
        
        # Learning from user behavior
        self.behavior_indicators: Dict[str, float] = {}
    
    def estimate_from_dob(self, date_of_birth: date) -> AgeEstimate:
        """
        Estimate age and node count from date of birth.
        
        Args:
            date_of_birth: User's date of birth
            
        Returns:
            AgeEstimate object
        """
        today = date.today()
        estimated_age = (today - date_of_birth).days / 365.25
        
        # Calculate node count based on age
        estimated_node_count = self._calculate_node_count(estimated_age)
        
        # Initial confidence based on data quality
        confidence = 0.7  # Base confidence from DOB
        
        estimate = AgeEstimate(
            estimated_age=estimated_age,
            confidence=confidence,
            date_of_birth=date_of_birth,
            estimated_node_count=estimated_node_count,
            calibration_factor=1.0,
            timestamp=datetime.now().timestamp()
        )
        
        self.current_estimate = estimate
        return estimate
    
    def estimate_from_behavior(self, behavior_indicators: Dict[str, float]) -> AgeEstimate:
        """
        Estimate age from behavior indicators if DOB is unavailable.
        
        Args:
            behavior_indicators: Dictionary of behavior metrics
            
        Returns:
            AgeEstimate object
        """
        self.behavior_indicators.update(behavior_indicators)
        
        # Estimate age based on behavior patterns
        estimated_age = self._estimate_age_from_behavior(behavior_indicators)
        
        # Calculate node count
        estimated_node_count = self._calculate_node_count(estimated_age)
        
        # Lower confidence for behavior-based estimation
        confidence = 0.5
        
        estimate = AgeEstimate(
            estimated_age=estimated_age,
            confidence=confidence,
            date_of_birth=None,
            estimated_node_count=estimated_node_count,
            calibration_factor=1.0,
            timestamp=datetime.now().timestamp()
        )
        
        self.current_estimate = estimate
        return estimate
    
    def _estimate_age_from_behavior(self, indicators: Dict[str, float]) -> float:
        """
        Estimate age from behavior indicators.
        
        Args:
            indicators: Behavior metrics
            
        Returns:
            Estimated age in years
        """
        # Simple heuristic based on vocabulary complexity, decision patterns, etc.
        vocabulary_score = indicators.get('vocabulary_complexity', 0.5)
        decision_complexity = indicators.get('decision_complexity', 0.5)
        experience_diversity = indicators.get('experience_diversity', 0.5)
        
        # Combine indicators
        combined_score = (vocabulary_score + decision_complexity + experience_diversity) / 3.0
        
        # Map to age range (5-80 years)
        estimated_age = 5 + combined_score * 75
        
        return estimated_age
    
    def _calculate_node_count(self, age: float) -> int:
        """
        Calculate node count based on age.
        
        Args:
            age: Age in years
            
        Returns:
            Estimated node count
        """
        # Linear scaling from base age
        node_count = int(self.base_node_count * (age / self.base_age))
        
        # Apply non-linear scaling for very young or very old
        if age < 10:
            node_count = int(node_count * 0.7)  # Fewer nodes for young users
        elif age > 60:
            node_count = int(node_count * 1.3)  # More nodes for older users
        
        # Clamp to valid range
        node_count = max(self.MIN_NODE_COUNT, min(node_count, self.MAX_NODE_COUNT))
        
        return node_count
    
    def calibrate_estimate(self, actual_node_count: int, actual_age: Optional[float] = None):
        """
        Calibrate the estimate based on actual data.
        
        Args:
            actual_node_count: Actual observed node count
            actual_age: Actual age if known
        """
        if not self.current_estimate:
            return
        
        # Calculate calibration factor
        if actual_age:
            # Calibrate based on actual age
            age_error = abs(actual_age - self.current_estimate.estimated_age)
            self.current_estimate.estimated_age = (
                self.current_estimate.estimated_age * (1 - self.calibration_sensitivity) +
                actual_age * self.calibration_sensitivity
            )
        
        # Calibrate node count
        node_error = abs(actual_node_count - self.current_estimate.estimated_node_count)
        calibration_factor = actual_node_count / self.current_estimate.estimated_node_count
        
        self.current_estimate.calibration_factor = (
            self.current_estimate.calibration_factor * (1 - self.calibration_sensitivity) +
            calibration_factor * self.calibration_sensitivity
        )
        
        # Recalculate node count
        self.current_estimate.estimated_node_count = int(
            self.current_estimate.estimated_node_count * self.current_estimate.calibration_factor
        )
        
        # Update confidence
        self.current_estimate.confidence = min(
            self.current_estimate.confidence + 0.05,
            0.95
        )
        
        # Record calibration
        self.calibration_history.append({
            'timestamp': datetime.now().timestamp(),
            'actual_node_count': actual_node_count,
            'actual_age': actual_age,
            'calibration_factor': calibration_factor,
            'previous_estimate': self.current_estimate.estimated_node_count
        })
    
    def adjust_estimate_for_discrepancy(self, discrepancy_type: str, magnitude: float):
        """
        Adjust estimate based on observed discrepancy.
        
        Args:
            discrepancy_type: Type of discrepancy ('overestimate', 'underestimate')
            magnitude: Magnitude of discrepancy (0-1)
        """
        if not self.current_estimate:
            return
        
        if discrepancy_type == 'overestimate':
            # Reduce estimate
            adjustment = 1.0 - (magnitude * self.calibration_sensitivity)
            self.current_estimate.estimated_node_count = int(
                self.current_estimate.estimated_node_count * adjustment
            )
        elif discrepancy_type == 'underestimate':
            # Increase estimate
            adjustment = 1.0 + (magnitude * self.calibration_sensitivity)
            self.current_estimate.estimated_node_count = int(
                self.current_estimate.estimated_node_count * adjustment
            )
        
        # Reduce confidence on discrepancy
        self.current_estimate.confidence = max(
            self.current_estimate.confidence - 0.1,
            0.3
        )
    
    def get_current_estimate(self) -> Optional[AgeEstimate]:
        """
        Get current age estimate.
        
        Returns:
            Current AgeEstimate or None
        """
        return self.current_estimate
    
    def get_node_count_range(self) -> Tuple[int, int]:
        """
        Get expected node count range based on current estimate.
        
        Returns:
            Tuple of (min_nodes, max_nodes)
        """
        if not self.current_estimate:
            return (self.MIN_NODE_COUNT, self.MAX_NODE_COUNT)
        
        # Calculate range based on confidence
        uncertainty = 1.0 - self.current_estimate.confidence
        range_factor = uncertainty * 0.3  # 30% range at lowest confidence
        
        base_count = self.current_estimate.estimated_node_count
        min_count = int(base_count * (1.0 - range_factor))
        max_count = int(base_count * (1.0 + range_factor))
        
        return (min_count, max_count)
    
    def get_estimation_statistics(self) -> Dict[str, any]:
        """
        Get statistics about age estimation.
        
        Returns:
            Dictionary containing estimation statistics
        """
        if not self.current_estimate:
            return {
                'has_estimate': False
            }
        
        return {
            'has_estimate': True,
            'estimated_age': self.current_estimate.estimated_age,
            'estimated_node_count': self.current_estimate.estimated_node_count,
            'confidence': self.current_estimate.confidence,
            'calibration_factor': self.current_estimate.calibration_factor,
            'calibration_count': len(self.calibration_history),
            'node_count_range': self.get_node_count_range(),
            'has_dob': self.current_estimate.date_of_birth is not None
        }
