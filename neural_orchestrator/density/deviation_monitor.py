"""
Deviation Monitor - Density Markers and Linear Decline
Monitors density markers and tracks linear decline of approximately -0.02 per year.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class DensityMarker:
    """Represents a density marker at a specific time."""
    timestamp: float
    density_value: float
    marker_type: str
    coordinates: Tuple[float, float, float]


class DeviationMonitor:
    """
    Monitors deviation using density markers and tracks linear decline.
    Uses deviation linear decline monitor of approximately -0.02 per year
    to find likely output token dilation.
    """
    
    def __init__(self, base_decline_rate: float = -0.02):
        """
        Initialize the Deviation Monitor.
        
        Args:
            base_decline_rate: Base linear decline rate per year (default -0.02)
        """
        self.base_decline_rate = base_decline_rate
        self.density_markers: List[DensityMarker] = []
        self.deviaton_history: List[float] = []
        self.token_dilation_history: List[float] = []
        
        # Baseline tracking
        self.baseline_value: float = 1.0
        self.baseline_timestamp: float = datetime.now().timestamp()
        
        # Density tracking
        self.density_threshold = 0.5
        self.current_density = 1.0
    
    def calculate_deviation(self, current_value: Optional[float] = None) -> float:
        """
        Calculate current deviation based on linear decline.
        
        Args:
            current_value: Current value to compare (uses calculated if None)
            
        Returns:
            Current deviation value
        """
        if current_value is None:
            current_value = self._calculate_current_value()
        
        # Calculate time elapsed since baseline
        current_time = datetime.now().timestamp()
        years_elapsed = (current_time - self.baseline_timestamp) / (365.25 * 24 * 3600)
        
        # Calculate expected decline
        expected_decline = self.base_decline_rate * years_elapsed
        expected_value = self.baseline_value + expected_decline
        
        # Calculate deviation
        deviation = current_value - expected_value
        
        # Store in history
        self.deviaton_history.append(deviation)
        if len(self.deviaton_history) > 1000:
            self.deviaton_history.pop(0)
        
        return deviation
    
    def _calculate_current_value(self) -> float:
        """
        Calculate current value based on density markers.
        
        Returns:
            Current calculated value
        """
        if not self.density_markers:
            return self.baseline_value
        
        # Average recent density markers
        recent_markers = self.density_markers[-10:] if len(self.density_markers) >= 10 else self.density_markers
        avg_density = np.mean([m.density_value for m in recent_markers])
        
        return avg_density
    
    def add_density_marker(
        self,
        density_value: float,
        marker_type: str = "general",
        coordinates: Optional[Tuple[float, float, float]] = None
    ) -> DensityMarker:
        """
        Add a density marker at the current time.
        
        Args:
            density_value: Density value to record
            marker_type: Type of marker
            coordinates: 3D coordinates (optional)
            
        Returns:
            DensityMarker object
        """
        if coordinates is None:
            coordinates = (0.0, 0.0, 0.0)
        
        marker = DensityMarker(
            timestamp=datetime.now().timestamp(),
            density_value=density_value,
            marker_type=marker_type,
            coordinates=coordinates
        )
        
        self.density_markers.append(marker)
        if len(self.density_markers) > 1000:
            self.density_markers.pop(0)
        
        # Update current density
        self.current_density = density_value
        
        return marker
    
    def calculate_token_dilation(self, q: int = 1) -> float:
        """
        Calculate token dilation based on deviation.
        Token dilation occurs when deviation exceeds threshold.
        
        Args:
            q: Frequency recursion parameter (5^q)
            
        Returns:
            Token dilation factor
        """
        deviation = self.calculate_deviation()
        
        # Token dilation occurs when deviation is significant
        # Using 5^q as reference
        frequency_value = 5 ** q
        
        # Calculate dilation based on deviation and frequency
        dilation_factor = 1.0 + (deviation * frequency_value) / 1000.0
        
        # Ensure positive dilation
        dilation_factor = max(0.1, dilation_factor)
        
        # Store in history
        self.token_dilation_history.append(dilation_factor)
        if len(self.token_dilation_history) > 1000:
            self.token_dilation_history.pop(0)
        
        return dilation_factor
    
    def get_density_markers_by_type(self, marker_type: str) -> List[DensityMarker]:
        """
        Get density markers of a specific type.
        
        Args:
            marker_type: Type of marker to retrieve
            
        Returns:
            List of DensityMarker objects
        """
        return [m for m in self.density_markers if m.marker_type == marker_type]
    
    def get_density_trend(self, window_size: int = 10) -> Dict[str, float]:
        """
        Get density trend over a time window.
        
        Args:
            window_size: Number of recent markers to analyze
            
        Returns:
            Dictionary containing trend information
        """
        if len(self.density_markers) < 2:
            return {
                'trend': 'insufficient_data',
                'slope': 0.0,
                'correlation': 0.0
            }
        
        recent_markers = self.density_markers[-window_size:] if len(self.density_markers) >= window_size else self.density_markers
        
        # Extract timestamps and values
        timestamps = [m.timestamp for m in recent_markers]
        values = [m.density_value for m in recent_markers]
        
        # Normalize timestamps
        min_time = min(timestamps)
        normalized_times = [(t - min_time) for t in timestamps]
        
        # Calculate linear regression
        if len(normalized_times) > 1:
            slope = np.polyfit(normalized_times, values, 1)[0]
            
            # Calculate correlation
            if len(values) > 1:
                correlation = np.corrcoef(normalized_times, values)[0, 1]
            else:
                correlation = 0.0
        else:
            slope = 0.0
            correlation = 0.0
        
        # Determine trend
        if slope > 0.001:
            trend = 'increasing'
        elif slope < -0.001:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'slope': slope,
            'correlation': correlation,
            'current_value': values[-1] if values else 0.0,
            'window_size': len(recent_markers)
        }
    
    def predict_decline(self, years_ahead: float = 1.0) -> Dict[str, float]:
        """
        Predict decline based on linear decline rate.
        
        Args:
            years_ahead: Number of years to predict ahead
            
        Returns:
            Dictionary containing prediction data
        """
        current_time = datetime.now().timestamp()
        years_elapsed = (current_time - self.baseline_timestamp) / (365.25 * 24 * 3600)
        
        # Current expected value
        current_expected = self.baseline_value + self.base_decline_rate * years_elapsed
        
        # Predicted value
        predicted_years = years_elapsed + years_ahead
        predicted_value = self.baseline_value + self.base_decline_rate * predicted_years
        
        # Predicted deviation
        current_actual = self._calculate_current_value()
        predicted_deviation = current_actual - predicted_value
        
        return {
            'years_ahead': years_ahead,
            'current_expected': current_expected,
            'predicted_value': predicted_value,
            'predicted_deviation': predicted_deviation,
            'decline_rate': self.base_decline_rate
        }
    
    def find_likely_output(self, threshold: float = 0.1) -> Dict[str, any]:
        """
        Find likely output based on deviation and token dilation.
        
        Args:
            threshold: Threshold for likely output detection
            
        Returns:
            Dictionary containing likely output information
        """
        deviation = self.calculate_deviation()
        
        # Check if deviation is significant
        is_likely = abs(deviation) > threshold
        
        # Get recent token dilation
        recent_dilation = self.token_dilation_history[-1] if self.token_dilation_history else 1.0
        
        return {
            'is_likely_output': is_likely,
            'deviation': deviation,
            'threshold': threshold,
            'token_dilation': recent_dilation,
            'confidence': min(abs(deviation) / threshold, 1.0) if threshold > 0 else 0.0
        }
    
    def reset_baseline(self, new_baseline: Optional[float] = None):
        """
        Reset baseline for deviation tracking.
        
        Args:
            new_baseline: New baseline value (uses current if None)
        """
        if new_baseline is None:
            new_baseline = self._calculate_current_value()
        
        self.baseline_value = new_baseline
        self.baseline_timestamp = datetime.now().timestamp()
    
    def get_monitoring_statistics(self) -> Dict[str, any]:
        """
        Get statistics about deviation monitoring.
        
        Returns:
            Dictionary containing monitoring statistics
        """
        if not self.deviaton_history:
            return {
                'total_markers': len(self.density_markers),
                'deviation_count': 0,
                'baseline_value': self.baseline_value
            }
        
        return {
            'total_markers': len(self.density_markers),
            'deviation_count': len(self.deviaton_history),
            'current_deviation': self.deviaton_history[-1],
            'avg_deviation': np.mean(self.deviaton_history),
            'max_deviation': max(self.deviaton_history),
            'min_deviation': min(self.deviaton_history),
            'std_deviation': np.std(self.deviaton_history),
            'baseline_value': self.baseline_value,
            'decline_rate': self.base_decline_rate,
            'current_density': self.current_density
        }
