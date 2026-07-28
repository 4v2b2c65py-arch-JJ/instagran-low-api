"""
Semantic Processor - Narrative Tracking and Intelligence Input
Processes semantic units, tracks narrative contributions, and manages cumulative intelligence.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re


@dataclass
class SemanticUnit:
    """Represents a semantic unit in the narrative."""
    unit_id: str
    content: str
    concepts: List[str]
    intent: str
    complexity: float
    timestamp: float
    vector_lag: float
    spatial_deviation: float


class SemanticProcessor:
    """
    Processes semantic units for narrative tracking and cumulative intelligence.
    Each semantic unit is fed by data concepts and intent based on complexity expansion.
    """
    
    def __init__(self, base_complexity: float = 0.5):
        """
        Initialize the Semantic Processor.
        
        Args:
            base_complexity: Base complexity for semantic units
        """
        self.base_complexity = base_complexity
        self.semantic_units: List[SemanticUnit] = []
        self.narrative_contributions: List[Dict] = []
        self.cumulative_intelligence: float = 0.0
        
        # Logic input tracking
        self.logic_inputs: List[float] = []
        self.current_iteration_n = 0
        
        # Semantic reconstruction
        self.reconstruction_buffer: List[Dict] = []
        
        # Vector time lag tracking
        self.vector_time_lags: Dict[str, float] = {}
    
    def generate_semantic_unit(
        self,
        content: str = "",
        concepts: Optional[List[str]] = None,
        intent: str = "processing",
        complexity: Optional[float] = None
    ) -> SemanticUnit:
        """
        Generate a semantic unit based on input parameters.
        
        Args:
            content: Content of the semantic unit
            concepts: List of concepts
            intent: Intent of the unit
            complexity: Complexity value (uses base if None)
            
        Returns:
            SemanticUnit object
        """
        if complexity is None:
            complexity = self.base_complexity
        
        # Generate concepts if not provided
        if concepts is None:
            concepts = self._extract_concepts(content)
        
        # Calculate vector time lag
        vector_lag = self._calculate_vector_time_lag(complexity)
        
        # Calculate spatial deviation
        spatial_deviation = self._calculate_spatial_deviation(complexity)
        
        # Create semantic unit
        unit = SemanticUnit(
            unit_id=f"unit_{len(self.semantic_units)}_{datetime.now().timestamp()}",
            content=content,
            concepts=concepts,
            intent=intent,
            complexity=complexity,
            timestamp=datetime.now().timestamp(),
            vector_lag=vector_lag,
            spatial_deviation=spatial_deviation
        )
        
        # Store unit
        self.semantic_units.append(unit)
        
        # Update cumulative intelligence
        self._update_cumulative_intelligence(unit)
        
        return unit
    
    def _extract_concepts(self, content: str) -> List[str]:
        """
        Extract concepts from content.
        
        Args:
            content: Content string
            
        Returns:
            List of concepts
        """
        if not content:
            return ["general"]
        
        # Simple concept extraction (words longer than 4 characters)
        words = re.findall(r'\b[a-zA-Z]{5,}\b', content.lower())
        return list(set(words)) if words else ["general"]
    
    def _calculate_vector_time_lag(self, complexity: float) -> float:
        """
        Calculate vector time lag based on complexity.
        Vector time lag represents deviation from cause in narrative order.
        
        Args:
            complexity: Complexity value
            
        Returns:
            Vector time lag value
        """
        # Lag increases with complexity
        base_lag = 0.1
        lag = base_lag * (1 + complexity)
        return lag
    
    def _calculate_spatial_deviation(self, complexity: float) -> float:
        """
        Calculate spatial deviation from cause.
        Spatial deviation represents how much the effect has deviated
        from the cause and rendered hidden beneath word data.
        
        Args:
            complexity: Complexity value
            
        Returns:
            Spatial deviation value
        """
        # Deviation increases with complexity
        base_deviation = 0.05
        deviation = base_deviation * complexity * np.random.uniform(0.8, 1.2)
        return deviation
    
    def _update_cumulative_intelligence(self, unit: SemanticUnit):
        """
        Update cumulative intelligence based on semantic unit.
        
        Args:
            unit: Semantic unit to process
        """
        # Intelligence contribution based on complexity and concepts
        contribution = unit.complexity * len(unit.concepts) * 0.1
        self.cumulative_intelligence += contribution
    
    def process_logic_input(self, i_n: float):
        """
        Process logic input I_n for narrative contribution tracking.
        
        Args:
            i_n: Logic input value for iteration n
        """
        self.logic_inputs.append(i_n)
        self.current_iteration_n = len(self.logic_inputs)
        
        # Track as narrative contribution
        self.narrative_contributions.append({
            'iteration': self.current_iteration_n,
            'logic_input': i_n,
            'timestamp': datetime.now().timestamp(),
            'cumulative_intelligence': self.cumulative_intelligence
        })
    
    def synthesize_semantic_units(self, unit_ids: List[str]) -> Dict[str, any]:
        """
        Synthesize multiple semantic units through synthesis.
        The sum through synthesis reconstructs outputs as narrative order.
        
        Args:
            unit_ids: List of semantic unit IDs to synthesize
            
        Returns:
            Dictionary containing synthesis results
        """
        units = [u for u in self.semantic_units if u.unit_id in unit_ids]
        
        if not units:
            return {
                'synthesized': False,
                'reason': 'No units found'
            }
        
        # Combine concepts
        all_concepts = []
        for unit in units:
            all_concepts.extend(unit.concepts)
        unique_concepts = list(set(all_concepts))
        
        # Calculate combined complexity
        combined_complexity = np.mean([u.complexity for u in units])
        
        # Calculate average vector lag
        avg_vector_lag = np.mean([u.vector_lag for u in units])
        
        # Calculate total spatial deviation
        total_spatial_deviation = np.sum([u.spatial_deviation for u in units])
        
        # Create synthesis result
        synthesis = {
            'synthesized': True,
            'unit_count': len(units),
            'combined_complexity': combined_complexity,
            'concepts': unique_concepts,
            'avg_vector_lag': avg_vector_lag,
            'total_spatial_deviation': total_spatial_deviation,
            'narrative_order': self._determine_narrative_order(units),
            'timestamp': datetime.now().timestamp()
        }
        
        # Store in reconstruction buffer
        self.reconstruction_buffer.append(synthesis)
        if len(self.reconstruction_buffer) > 100:
            self.reconstruction_buffer.pop(0)
        
        return synthesis
    
    def _determine_narrative_order(self, units: List[SemanticUnit]) -> List[str]:
        """
        Determine narrative order from semantic units.
        Reconstructs outputs as narrative order based on vector time lag.
        
        Args:
            units: List of semantic units
            
        Returns:
            List of unit IDs in narrative order
        """
        # Sort by vector time lag (smaller lag = closer to cause)
        sorted_units = sorted(units, key=lambda u: u.vector_lag)
        return [u.unit_id for u in sorted_units]
    
    def reconstruct_output(self, synthesis_id: Optional[int] = None) -> Dict[str, any]:
        """
        Reconstruct output from synthesis buffer.
        
        Args:
            synthesis_id: ID of synthesis to reconstruct (latest if None)
            
        Returns:
            Dictionary containing reconstructed output
        """
        if not self.reconstruction_buffer:
            return {
                'reconstructed': False,
                'reason': 'No synthesis data available'
            }
        
        if synthesis_id is None:
            synthesis = self.reconstruction_buffer[-1]
        else:
            synthesis = self.reconstruction_buffer[synthesis_id]
        
        # Reconstruct narrative
        narrative = self._reconstruct_narrative(synthesis)
        
        return {
            'reconstructed': True,
            'synthesis': synthesis,
            'narrative': narrative,
            'hidden_data': self._extract_hidden_data(synthesis),
            'timestamp': datetime.now().timestamp()
        }
    
    def _reconstruct_narrative(self, synthesis: Dict) -> str:
        """
        Reconstruct narrative from synthesis data.
        
        Args:
            synthesis: Synthesis dictionary
            
        Returns:
            Reconstructed narrative string
        """
        concepts = synthesis.get('concepts', [])
        complexity = synthesis.get('combined_complexity', 0.5)
        
        # Build narrative from concepts
        if concepts:
            narrative = f"Narrative with {len(concepts)} concepts at complexity {complexity:.2f}. "
            narrative += "Key concepts: " + ", ".join(concepts[:5])
        else:
            narrative = f"Narrative at complexity {complexity:.2f} with no specific concepts."
        
        return narrative
    def _extract_hidden_data(self, synthesis: Dict) -> Dict[str, any]:
        """
        Extract hidden data from synthesis.
        Hidden data includes pixel interaction, electron shifts, pressure from density.
        
        Args:
            synthesis: Synthesis dictionary
            
        Returns:
            Dictionary containing hidden data
        """
        spatial_deviation = synthesis.get('total_spatial_deviation', 0.0)
        vector_lag = synthesis.get('avg_vector_lag', 0.0)
        
        return {
            'pixel_interaction': spatial_deviation * 100,
            'electron_shifts': vector_lag * 50,
            'pressure_from_density': spatial_deviation * vector_lag * 10,
            'hidden_beneath_word_data': spatial_deviation > 0.1
        }
    
    def get_narrative_statistics(self) -> Dict[str, any]:
        """
        Get statistics about narrative processing.
        
        Returns:
            Dictionary containing narrative statistics
        """
        if not self.semantic_units:
            return {
                'total_units': 0,
                'cumulative_intelligence': 0.0
            }
        
        complexities = [u.complexity for u in self.semantic_units]
        concept_counts = [len(u.concepts) for u in self.semantic_units]
        
        return {
            'total_units': len(self.semantic_units),
            'cumulative_intelligence': self.cumulative_intelligence,
            'avg_complexity': np.mean(complexities),
            'max_complexity': max(complexities),
            'min_complexity': min(complexities),
            'avg_concepts_per_unit': np.mean(concept_counts),
            'total_narrative_contributions': len(self.narrative_contributions),
            'current_iteration_n': self.current_iteration_n
        }
    
    def get_intent_distribution(self) -> Dict[str, int]:
        """
        Get distribution of intents across semantic units.
        
        Returns:
            Dictionary mapping intent to count
        """
        intent_counts = {}
        for unit in self.semantic_units:
            intent = unit.intent
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
        return intent_counts
