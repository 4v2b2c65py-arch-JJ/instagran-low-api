"""
Frequency Recursion Engine - Dimensional Resolution System
Handles frequency recursion (5^q) and dimensional resolution across cognitive dimensions.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta


class FrequencyRecursionEngine:
    """
    Engine for frequency recursion and dimensional resolution calculations.
    Manages 5^q recursion across q=1 to q=9 with 3 cycles of dimensional resolution.
    """
    
    def __init__(self, q_range: Tuple[int, int] = (1, 9)):
        """
        Initialize the Frequency Recursion Engine.
        
        Args:
            q_range: Range of q values for recursion (default 1-9)
        """
        self.q_range = q_range
        self.current_q = 1
        self.current_cycle = 1  # 3 cycles total
        self.frequency_history: List[float] = []
        self.dimensional_resolution_history: List[int] = []
        
        # Cognitive dimension time tracking (24 hours)
        self.cognitive_dimension_start = datetime.now()
        
    def calculate_frequency_recursion(self, q: int) -> float:
        """
        Calculate frequency recursion value 5^q.
        
        Args:
            q: Recursion parameter
            
        Returns:
            Frequency value (5^q)
        """
        return 5 ** q
    
    def get_frequency_values(self) -> Dict[int, float]:
        """
        Get all frequency values across q range.
        
        Returns:
            Dictionary mapping q to 5^q values
        """
        return {q: self.calculate_frequency_recursion(q) for q in range(self.q_range[0], self.q_range[1] + 1)}
    
    def calculate_dimensional_resolution(self, q: int, cycle: int) -> int:
        """
        Calculate dimensional resolution across 3 cycles from q=1 to q=9.
        
        Args:
            q: Current q value (1-9)
            cycle: Current cycle (1-3)
            
        Returns:
            Dimensional resolution value
        """
        # 3 cycles of dimensional resolution
        # Cycle 1: q=1-3, Cycle 2: q=4-6, Cycle 3: q=7-9
        cycle_position = (q - 1) // 3  # 0, 1, 2
        resolution = (q * (cycle_position + 1)) + cycle
        return resolution
    
    def get_relative_time_units(self, q: int) -> Dict[str, float]:
        """
        Get relative time units for specific q value.
        
        Examples:
            - 5^1 = 5 units of relative time
            - 5^5 = 3,125 units
            - 5^9 = 1,953,125 units
            
        Args:
            q: q value for calculation
            
        Returns:
            Dictionary containing time unit information
        """
        frequency_value = self.calculate_frequency_recursion(q)
        
        # Project to 24-hour cognitive dimension
        projection_factor = frequency_value / (5 ** 9)  # Normalize to max
        projected_hours = projection_factor * 24
        
        return {
            'q': q,
            'frequency_value': frequency_value,
            'relative_time_units': frequency_value,
            'projected_hours_24h': projected_hours,
            'projection_factor': projection_factor
        }
    
    def advance_q(self) -> int:
        """
        Advance to next q value in the sequence.
        
        Returns:
            New q value
        """
        self.current_q += 1
        if self.current_q > self.q_range[1]:
            self.current_q = self.q_range[0]
            self.current_cycle += 1
            if self.current_cycle > 3:
                self.current_cycle = 1
        
        return self.current_q
    
    def get_current_state(self) -> Dict[str, any]:
        """
        Get current state of the frequency engine.
        
        Returns:
            Dictionary containing current state information
        """
        frequency_value = self.calculate_frequency_recursion(self.current_q)
        dimensional_resolution = self.calculate_dimensional_resolution(
            self.current_q, self.current_cycle
        )
        
        # Store in history
        self.frequency_history.append(frequency_value)
        self.dimensional_resolution_history.append(dimensional_resolution)
        
        # Keep history manageable
        if len(self.frequency_history) > 1000:
            self.frequency_history.pop(0)
            self.dimensional_resolution_history.pop(0)
        
        return {
            'current_q': self.current_q,
            'current_cycle': self.current_cycle,
            'frequency_value': frequency_value,
            'dimensional_resolution': dimensional_resolution,
            'relative_time_units': self.get_relative_time_units(self.current_q),
            'cognitive_dimension_elapsed': (datetime.now() - self.cognitive_dimension_start).total_seconds()
        }
    
    def calculate_token_dilation(self, q: int, base_tokens: int = 1000) -> float:
        """
        Calculate token dilation based on frequency recursion.
        Token dilation occurs across dimensional resolution cycles.
        
        Args:
            q: Current q value
            base_tokens: Base number of tokens
            
        Returns:
            Dilated token count
        """
        frequency_value = self.calculate_frequency_recursion(q)
        dilation_factor = np.log(frequency_value) / np.log(5)
        return base_tokens * dilation_factor
    
    def get_frequency_trajectory(self, steps: int = 10) -> List[Dict[str, float]]:
        """
        Get frequency trajectory for projection.
        
        Args:
            steps: Number of steps to project
            
        Returns:
            List of frequency trajectory points
        """
        trajectory = []
        temp_q = self.current_q
        
        for _ in range(steps):
            frequency_value = self.calculate_frequency_recursion(temp_q)
            dimensional_resolution = self.calculate_dimensional_resolution(temp_q, self.current_cycle)
            
            trajectory.append({
                'q': temp_q,
                'frequency_value': frequency_value,
                'dimensional_resolution': dimensional_resolution,
                'projected_hours': (frequency_value / (5 ** 9)) * 24
            })
            
            temp_q += 1
            if temp_q > self.q_range[1]:
                temp_q = self.q_range[0]
        
        return trajectory
    
    def derive_entity_frequency(self, base_frequency: float, recursion_depth: int = 5) -> float:
        """
        Derive entity using frequency recursion.
        
        Args:
            base_frequency: Base frequency value
            recursion_depth: Depth of recursion (default 5)
            
        Returns:
            Derived entity frequency
        """
        return base_frequency ** recursion_depth
    
    def calculate_frequency_density(self, alpha_hz: float, beta_hz: float) -> Dict[str, float]:
        """
        Calculate frequency density for alpha and beta wave ranges.
        
        Args:
            alpha_hz: Alpha wave frequency (8-12 Hz)
            beta_hz: Beta wave frequency (13-30 Hz)
            
        Returns:
            Dictionary containing frequency density metrics
        """
        alpha_density = alpha_hz / 12.0  # Normalize to max alpha
        beta_density = beta_hz / 30.0  # Normalize to max beta
        combined_density = (alpha_density + beta_density) / 2.0
        
        return {
            'alpha_hz': alpha_hz,
            'beta_hz': beta_hz,
            'alpha_density': alpha_density,
            'beta_density': beta_density,
            'combined_density': combined_density,
            'density_ratio': alpha_hz / beta_hz if beta_hz > 0 else 0
        }
