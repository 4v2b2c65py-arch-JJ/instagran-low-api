"""
Calibration System - Age Calibration and Model Adjustment
Calibrates age estimates and adjusts model parameters based on observed data.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from .age_estimator import AgeEstimator, AgeEstimate


@dataclass
class CalibrationResult:
    """Represents a calibration result."""
    calibration_id: str
    original_estimate: AgeEstimate
    calibrated_estimate: AgeEstimate
    adjustment_factor: float
    confidence_change: float
    timestamp: float
    success: bool


class CalibrationSystem:
    """
    Calibrates age estimates and adjusts model parameters.
    Ensures the model can self-correct when estimates fall incorrect.
    """
    
    def __init__(self, sensitivity: float = 0.1):
        """
        Initialize the Calibration System.
        
        Args:
            sensitivity: How sensitive calibration is to new data
        """
        self.sensitivity = sensitivity
        
        # Calibration history
        self.calibration_history: List[CalibrationResult] = []
        
        # Calibration parameters
        self.min_confidence = 0.3
        self.max_confidence = 0.95
        self.confidence_increment = 0.05
        self.confidence_decrement = 0.1
        
        # Adjustment tracking
        self.adjustment_factors: List[float] = []
        
        # Model parameters to calibrate
        self.model_parameters = {
            'node_growth_rate': 522222,  # nodes per year
            'base_age': 18.0,
            'base_node_count': 9_400_000,
            'age_variance': 2.0,  # years
            'node_variance': 500000  # nodes
        }
    
    def calibrate_from_observed_data(
        self,
        age_estimator: AgeEstimator,
        observed_age: Optional[float] = None,
        observed_node_count: Optional[int] = None,
        behavior_indicators: Optional[Dict[str, float]] = None
    ) -> CalibrationResult:
        """
        Calibrate age estimate based on observed data.
        
        Args:
            age_estimator: AgeEstimator instance to calibrate
            observed_age: Observed actual age
            observed_node_count: Observed actual node count
            behavior_indicators: Behavior indicators for calibration
            
        Returns:
            CalibrationResult object
        """
        original_estimate = age_estimator.get_current_estimate()
        
        if not original_estimate:
            return CalibrationResult(
                calibration_id=f"cal_{len(self.calibration_history)}_{datetime.now().timestamp()}",
                original_estimate=original_estimate,
                calibrated_estimate=original_estimate,
                adjustment_factor=1.0,
                confidence_change=0.0,
                timestamp=datetime.now().timestamp(),
                success=False
            )
        
        # Store original values
        original_age = original_estimate.estimated_age
        original_nodes = original_estimate.estimated_node_count
        original_confidence = original_estimate.confidence
        
        # Calibrate based on available data
        if observed_age is not None:
            self._calibrate_age(age_estimator, observed_age)
        
        if observed_node_count is not None:
            self._calibrate_node_count(age_estimator, observed_node_count)
        
        if behavior_indicators:
            self._calibrate_from_behavior(age_estimator, behavior_indicators)
        
        # Get calibrated estimate
        calibrated_estimate = age_estimator.get_current_estimate()
        
        # Calculate adjustment factor
        if calibrated_estimate:
            adjustment_factor = calibrated_estimate.estimated_node_count / original_nodes
            confidence_change = calibrated_estimate.confidence - original_confidence
        else:
            adjustment_factor = 1.0
            confidence_change = 0.0
        
        # Create calibration result
        result = CalibrationResult(
            calibration_id=f"cal_{len(self.calibration_history)}_{datetime.now().timestamp()}",
            original_estimate=original_estimate,
            calibrated_estimate=calibrated_estimate,
            adjustment_factor=adjustment_factor,
            confidence_change=confidence_change,
            timestamp=datetime.now().timestamp(),
            success=True
        )
        
        self.calibration_history.append(result)
        self.adjustment_factors.append(adjustment_factor)
        
        # Keep history manageable
        if len(self.calibration_history) > 1000:
            self.calibration_history.pop(0)
        if len(self.adjustment_factors) > 1000:
            self.adjustment_factors.pop(0)
        
        return result
    
    def _calibrate_age(self, age_estimator: AgeEstimator, observed_age: float):
        """
        Calibrate age estimate based on observed age.
        
        Args:
            age_estimator: AgeEstimator instance
            observed_age: Observed actual age
        """
        current_estimate = age_estimator.get_current_estimate()
        if not current_estimate:
            return
        
        # Calculate age error
        age_error = observed_age - current_estimate.estimated_age
        
        # Adjust estimate using sensitivity
        current_estimate.estimated_age = (
            current_estimate.estimated_age * (1 - self.sensitivity) +
            observed_age * self.sensitivity
        )
        
        # Recalculate node count based on new age
        current_estimate.estimated_node_count = age_estimator._calculate_node_count(
            current_estimate.estimated_age
        )
        
        # Update confidence based on error magnitude
        error_magnitude = abs(age_error)
        if error_magnitude < 1.0:  # Good estimate
            current_estimate.confidence = min(
                current_estimate.confidence + self.confidence_increment,
                self.max_confidence
            )
        else:  # Poor estimate
            current_estimate.confidence = max(
                current_estimate.confidence - self.confidence_decrement,
                self.min_confidence
            )
    
    def _calibrate_node_count(self, age_estimator: AgeEstimator, observed_node_count: int):
        """
        Calibrate node count based on observed node count.
        
        Args:
            age_estimator: AgeEstimator instance
            observed_node_count: Observed actual node count
        """
        current_estimate = age_estimator.get_current_estimate()
        if not current_estimate:
            return
        
        # Calculate node error
        node_error = observed_node_count - current_estimate.estimated_node_count
        
        # Adjust calibration factor
        calibration_factor = observed_node_count / current_estimate.estimated_node_count
        current_estimate.calibration_factor = (
            current_estimate.calibration_factor * (1 - self.sensitivity) +
            calibration_factor * self.sensitivity
        )
        
        # Apply calibration factor
        current_estimate.estimated_node_count = int(
            current_estimate.estimated_node_count * current_estimate.calibration_factor
        )
        
        # Recalculate age based on new node count
        current_estimate.estimated_age = (
            current_estimate.estimated_node_count / self.model_parameters['node_growth_rate']
        )
    
    def _calibrate_from_behavior(self, age_estimator: AgeEstimator, behavior_indicators: Dict[str, float]):
        """
        Calibrate based on behavior indicators.
        
        Args:
            age_estimator: AgeEstimator instance
            behavior_indicators: Behavior indicators
        """
        current_estimate = age_estimator.get_current_estimate()
        if not current_estimate:
            return
        
        # Estimate age from behavior
        behavior_age = age_estimator._estimate_age_from_behavior(behavior_indicators)
        
        # Blend with current estimate
        current_estimate.estimated_age = (
            current_estimate.estimated_age * 0.7 +
            behavior_age * 0.3
        )
        
        # Recalculate node count
        current_estimate.estimated_node_count = age_estimator._calculate_node_count(
            current_estimate.estimated_age
        )
    
    def auto_calibrate_from_discrepancy(
        self,
        age_estimator: AgeEstimator,
        discrepancy_type: str,
        magnitude: float
    ):
        """
        Automatically calibrate based on observed discrepancy.
        
        Args:
            age_estimator: AgeEstimator instance
            discrepancy_type: Type of discrepancy
            magnitude: Magnitude of discrepancy (0-1)
        """
        current_estimate = age_estimator.get_current_estimate()
        if not current_estimate:
            return
        
        if discrepancy_type == 'overestimate':
            # Model is overestimating, reduce node count
            adjustment = 1.0 - (magnitude * self.sensitivity)
            current_estimate.estimated_node_count = int(
                current_estimate.estimated_node_count * adjustment
            )
            current_estimate.calibration_factor *= adjustment
            
        elif discrepancy_type == 'underestimate':
            # Model is underestimating, increase node count
            adjustment = 1.0 + (magnitude * self.sensitivity)
            current_estimate.estimated_node_count = int(
                current_estimate.estimated_node_count * adjustment
            )
            current_estimate.calibration_factor *= adjustment
        
        # Recalculate age
        current_estimate.estimated_age = (
            current_estimate.estimated_node_count / self.model_parameters['node_growth_rate']
        )
        
        # Adjust confidence
        current_estimate.confidence = max(
            current_estimate.confidence - 0.05,
            self.min_confidence
        )
    
    def adjust_model_parameters(self, parameter_updates: Dict[str, float]):
        """
        Adjust model parameters based on learning.
        
        Args:
            parameter_updates: Dictionary of parameter updates
        """
        for param, value in parameter_updates.items():
            if param in self.model_parameters:
                self.model_parameters[param] = value
    
    def get_calibration_statistics(self) -> Dict[str, any]:
        """
        Get statistics about calibration.
        
        Returns:
            Dictionary containing calibration statistics
        """
        if not self.calibration_history:
            return {
                'total_calibrations': 0
            }
        
        successful_calibrations = sum(1 for c in self.calibration_history if c.success)
        
        adjustment_factors = [c.adjustment_factor for c in self.calibration_history]
        confidence_changes = [c.confidence_change for c in self.calibration_history]
        
        return {
            'total_calibrations': len(self.calibration_history),
            'successful_calibrations': successful_calibrations,
            'success_rate': successful_calibrations / len(self.calibration_history),
            'avg_adjustment_factor': np.mean(adjustment_factors),
            'avg_confidence_change': np.mean(confidence_changes),
            'model_parameters': self.model_parameters,
            'sensitivity': self.sensitivity
        }
    
    def get_recent_calibrations(self, limit: int = 10) -> List[CalibrationResult]:
        """
        Get recent calibration results.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of recent CalibrationResult objects
        """
        return self.calibration_history[-limit:] if self.calibration_history else []
    
    def should_recalibrate(self, age_estimator: AgeEstimator) -> bool:
        """
        Determine if recalibration is needed.
        
        Args:
            age_estimator: AgeEstimator instance
            
        Returns:
            True if recalibration is needed
        """
        current_estimate = age_estimator.get_current_estimate()
        
        if not current_estimate:
            return True
        
        # Recalibrate if confidence is low
        if current_estimate.confidence < 0.5:
            return True
        
        # Recalibrate if recent calibrations show high variance
        if len(self.adjustment_factors) > 10:
            recent_factors = self.adjustment_factors[-10:]
            variance = np.var(recent_factors)
            if variance > 0.1:  # High variance indicates instability
                return True
        
        return False
    
    def set_sensitivity(self, new_sensitivity: float):
        """
        Set calibration sensitivity.
        
        Args:
            new_sensitivity: New sensitivity value (0-1)
        """
        self.sensitivity = min(max(new_sensitivity, 0.01), 1.0)
