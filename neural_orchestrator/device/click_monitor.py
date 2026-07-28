"""
Click Monitor - In-App Interaction Tracking
Monitors device clicks on specific in-app interactions like social platform style.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ClickType(Enum):
    """Types of clicks to monitor."""
    TAP = "tap"
    DOUBLE_TAP = "double_tap"
    LONG_PRESS = "long_press"
    SWIPE = "swipe"
    SCROLL = "scroll"
    PINCH = "pinch"
    BUTTON_PRESS = "button_press"
    LINK_CLICK = "link_click"
    IMAGE_CLICK = "image_click"
    TEXT_SELECT = "text_select"


@dataclass
class ClickEvent:
    """Represents a click event."""
    click_id: str
    click_type: ClickType
    x_coordinate: float
    y_coordinate: float
    element_id: Optional[str]
    element_type: str
    timestamp: float
    pressure: float  # Touch pressure (0-1)
    duration_ms: float
    app_context: str


@dataclass
class ClickPattern:
    """Represents a detected click pattern."""
    pattern_id: str
    pattern_type: str  # rapid_click, repetitive, spatial_cluster, etc.
    clicks: List[ClickEvent]
    confidence: float
    timestamp: float
    metadata: Dict[str, any]


class ClickMonitor:
    """
    Monitors device clicks on specific in-app interactions.
    Tracks click patterns and feeds data to brain map layer.
    """
    
    def __init__(self, brain_map_layer: Optional[str] = None):
        """
        Initialize the Click Monitor.
        
        Args:
            brain_map_layer: Target brain map layer for feeding data
        """
        self.brain_map_layer = brain_map_layer
        
        # Click storage
        self.click_events: List[ClickEvent] = []
        self.click_patterns: List[ClickPattern] = []
        
        # Element tracking
        self.element_clicks: Dict[str, List[ClickEvent]] = {}
        
        # Spatial clustering
        self.spatial_clusters: Dict[str, List[ClickEvent]] = {}
        
        # Temporal patterns
        self.temporal_windows: List[List[ClickEvent]] = []
        
        # Brain map feed
        self.brain_map_feed: Dict[str, any] = {}
        
        # Configuration
        self.rapid_click_threshold = 5  # clicks per second
        self.spatial_cluster_radius = 50  # pixels
        self.temporal_window_size = 5.0  # seconds
    
    def record_click(
        self,
        click_type: ClickType,
        x_coordinate: float,
        y_coordinate: float,
        element_id: Optional[str] = None,
        element_type: str = "unknown",
        pressure: float = 0.5,
        duration_ms: float = 100.0,
        app_context: str = "generic"
    ) -> ClickEvent:
        """
        Record a click event.
        
        Args:
            click_type: Type of click
            x_coordinate: X coordinate
            y_coordinate: Y coordinate
            element_id: Element identifier
            element_type: Type of element
            pressure: Touch pressure (0-1)
            duration_ms: Duration in milliseconds
            app_context: Application context
            
        Returns:
            ClickEvent object
        """
        click = ClickEvent(
            click_id=f"click_{len(self.click_events)}_{datetime.now().timestamp()}",
            click_type=click_type,
            x_coordinate=x_coordinate,
            y_coordinate=y_coordinate,
            element_id=element_id,
            element_type=element_type,
            timestamp=datetime.now().timestamp(),
            pressure=pressure,
            duration_ms=duration_ms,
            app_context=app_context
        )
        
        self.click_events.append(click)
        
        # Track element clicks
        if element_id:
            if element_id not in self.element_clicks:
                self.element_clicks[element_id] = []
            self.element_clicks[element_id].append(click)
        
        # Update temporal windows
        self._update_temporal_windows(click)
        
        # Detect patterns
        self._detect_patterns(click)
        
        # Feed to brain map
        self._feed_to_brain_map('click', click)
        
        return click
    
    def _update_temporal_windows(self, click: ClickEvent):
        """
        Update temporal windows with new click.
        
        Args:
            click: Click event to add
        """
        current_time = click.timestamp
        
        # Add to current window or create new
        if not self.temporal_windows:
            self.temporal_windows.append([click])
        else:
            latest_window = self.temporal_windows[-1]
            window_start = latest_window[0].timestamp
            
            if current_time - window_start < self.temporal_window_size:
                latest_window.append(click)
            else:
                self.temporal_windows.append([click])
        
        # Keep only recent windows
        if len(self.temporal_windows) > 100:
            self.temporal_windows.pop(0)
    
    def _detect_patterns(self, click: ClickEvent):
        """
        Detect click patterns based on recent clicks.
        
        Args:
            click: Most recent click event
        """
        # Check for rapid clicks
        self._detect_rapid_clicks(click)
        
        # Check for spatial clusters
        self._detect_spatial_clusters(click)
        
        # Check for repetitive element clicks
        self._detect_repetitive_clicks(click)
    
    def _detect_rapid_clicks(self, click: ClickEvent):
        """
        Detect rapid click patterns.
        
        Args:
            click: Most recent click event
        """
        if not self.temporal_windows:
            return
        
        recent_window = self.temporal_windows[-1]
        clicks_per_second = len(recent_window) / self.temporal_window_size
        
        if clicks_per_second >= self.rapid_click_threshold:
            pattern = ClickPattern(
                pattern_id=f"rapid_click_{len(self.click_patterns)}_{datetime.now().timestamp()}",
                pattern_type="rapid_click",
                clicks=recent_window.copy(),
                confidence=min(clicks_per_second / (self.rapid_click_threshold * 2), 1.0),
                timestamp=datetime.now().timestamp(),
                metadata={
                    'clicks_per_second': clicks_per_second,
                    'app_context': click.app_context
                }
            )
            
            self.click_patterns.append(pattern)
            self._feed_to_brain_map('click_pattern', pattern)
    
    def _detect_spatial_clusters(self, click: ClickEvent):
        """
        Detect spatial clustering of clicks.
        
        Args:
            click: Most recent click event
        """
        recent_clicks = [c for c in self.click_events[-50:] if c.app_context == click.app_context]
        
        # Find clicks within radius
        nearby_clicks = []
        for c in recent_clicks:
            distance = np.sqrt(
                (c.x_coordinate - click.x_coordinate) ** 2 +
                (c.y_coordinate - click.y_coordinate) ** 2
            )
            if distance <= self.spatial_cluster_radius:
                nearby_clicks.append(c)
        
        if len(nearby_clicks) >= 3:
            cluster_id = f"cluster_{click.x_coordinate:.0f}_{click.y_coordinate:.0f}"
            
            if cluster_id not in self.spatial_clusters:
                self.spatial_clusters[cluster_id] = []
            
            self.spatial_clusters[cluster_id].extend(nearby_clicks)
            
            # Create pattern if cluster is significant
            if len(self.spatial_clusters[cluster_id]) >= 5:
                pattern = ClickPattern(
                    pattern_id=f"spatial_cluster_{len(self.click_patterns)}_{datetime.now().timestamp()}",
                    pattern_type="spatial_cluster",
                    clicks=self.spatial_clusters[cluster_id].copy(),
                    confidence=min(len(self.spatial_clusters[cluster_id]) / 10.0, 1.0),
                    timestamp=datetime.now().timestamp(),
                    metadata={
                        'center_x': click.x_coordinate,
                        'center_y': click.y_coordinate,
                        'cluster_size': len(self.spatial_clusters[cluster_id]),
                        'app_context': click.app_context
                    }
                )
                
                self.click_patterns.append(pattern)
                self._feed_to_brain_map('click_pattern', pattern)
    
    def _detect_repetitive_clicks(self, click: ClickEvent):
        """
        Detect repetitive clicks on same element.
        
        Args:
            click: Most recent click event
        """
        if not click.element_id:
            return
        
        element_clicks = self.element_clicks.get(click.element_id, [])
        
        if len(element_clicks) >= 5:
            # Check if clicks are recent
            recent_element_clicks = [c for c in element_clicks if click.timestamp - c.timestamp < 10.0]
            
            if len(recent_element_clicks) >= 5:
                pattern = ClickPattern(
                    pattern_id=f"repetitive_{len(self.click_patterns)}_{datetime.now().timestamp()}",
                    pattern_type="repetitive_click",
                    clicks=recent_element_clicks.copy(),
                    confidence=min(len(recent_element_clicks) / 10.0, 1.0),
                    timestamp=datetime.now().timestamp(),
                    metadata={
                        'element_id': click.element_id,
                        'element_type': click.element_type,
                        'click_count': len(recent_element_clicks),
                        'app_context': click.app_context
                    }
                )
                
                self.click_patterns.append(pattern)
                self._feed_to_brain_map('click_pattern', pattern)
    
    def _feed_to_brain_map(self, feed_type: str, data: any):
        """
        Feed data to brain map layer.
        
        Args:
            feed_type: Type of data feed
            data: Data to feed
        """
        if feed_type not in self.brain_map_feed:
            self.brain_map_feed[feed_type] = []
        
        if hasattr(data, '__dict__'):
            feed_data = data.__dict__.copy()
            # Convert enum to string
            if 'click_type' in feed_data:
                feed_data['click_type'] = feed_data['click_type'].value
        else:
            feed_data = {'data': data}
        
        self.brain_map_feed[feed_type].append(feed_data)
        
        if len(self.brain_map_feed[feed_type]) > 100:
            self.brain_map_feed[feed_type].pop(0)
    
    def get_click_statistics(self) -> Dict[str, any]:
        """
        Get statistics about recorded clicks.
        
        Returns:
            Dictionary containing click statistics
        """
        if not self.click_events:
            return {'total_clicks': 0}
        
        # Click type distribution
        click_types = {}
        for click in self.click_events:
            click_type = click.click_type.value
            click_types[click_type] = click_types.get(click_type, 0) + 1
        
        # Pressure statistics
        pressures = [c.pressure for c in self.click_events]
        
        # Duration statistics
        durations = [c.duration_ms for c in self.click_events]
        
        # App context distribution
        app_contexts = {}
        for click in self.click_events:
            app_contexts[click.app_context] = app_contexts.get(click.app_context, 0) + 1
        
        return {
            'total_clicks': len(self.click_events),
            'click_type_distribution': click_types,
            'avg_pressure': np.mean(pressures),
            'avg_duration_ms': np.mean(durations),
            'app_context_distribution': app_contexts,
            'unique_elements_clicked': len(self.element_clicks),
            'total_patterns_detected': len(self.click_patterns)
        }
    
    def get_element_heatmap(self, app_context: Optional[str] = None) -> Dict[str, int]:
        """
        Get click heatmap for elements.
        
        Args:
            app_context: Filter by app context (optional)
            
        Returns:
            Dictionary mapping element IDs to click counts
        """
        heatmap = {}
        
        for element_id, clicks in self.element_clicks.items():
            if app_context is None or any(c.app_context == app_context for c in clicks):
                heatmap[element_id] = len(clicks)
        
        return heatmap
    
    def get_spatial_heatmap(self, app_context: Optional[str] = None, grid_size: int = 20) -> np.ndarray:
        """
        Get spatial heatmap of clicks.
        
        Args:
            app_context: Filter by app context (optional)
            grid_size: Size of the grid (grid_size x grid_size)
            
        Returns:
            2D numpy array representing click density
        """
        heatmap = np.zeros((grid_size, grid_size))
        
        clicks_to_process = self.click_events
        if app_context:
            clicks_to_process = [c for c in self.click_events if c.app_context == app_context]
        
        # Normalize coordinates to grid
        max_x = max(c.x_coordinate for c in clicks_to_process) if clicks_to_process else 1.0
        max_y = max(c.y_coordinate for c in clicks_to_process) if clicks_to_process else 1.0
        
        for click in clicks_to_process:
            grid_x = int((click.x_coordinate / max_x) * (grid_size - 1))
            grid_y = int((click.y_coordinate / max_y) * (grid_size - 1))
            
            if 0 <= grid_x < grid_size and 0 <= grid_y < grid_size:
                heatmap[grid_y, grid_x] += 1
        
        return heatmap
    
    def get_click_patterns(self, pattern_type: Optional[str] = None) -> List[ClickPattern]:
        """
        Get detected click patterns.
        
        Args:
            pattern_type: Filter by pattern type (optional)
            
        Returns:
            List of ClickPattern objects
        """
        if pattern_type:
            return [p for p in self.click_patterns if p.pattern_type == pattern_type]
        return self.click_patterns.copy()
    
    def analyze_user_intent(self) -> Dict[str, any]:
        """
        Analyze user intent based on click patterns.
        
        Returns:
            Dictionary containing intent analysis
        """
        if not self.click_events:
            return {'status': 'insufficient_data'}
        
        # Determine primary intent based on click patterns
        pattern_types = [p.pattern_type for p in self.click_patterns]
        
        if not pattern_types:
            return {
                'primary_intent': 'exploration',
                'confidence': 0.5,
                'reasoning': 'no_clear_patterns_detected'
            }
        
        # Count pattern types
        pattern_counts = {}
        for pt in pattern_types:
            pattern_counts[pt] = pattern_counts.get(pt, 0) + 1
        
        # Determine primary intent
        most_common_pattern = max(pattern_counts, key=pattern_counts.get)
        
        inten_mapping = {
            'rapid_click': 'frustration',
            'spatial_cluster': 'targeted_interaction',
            'repetitive_click': 'persistence'
        }
        
        primary_intent = inten_mapping.get(most_common_pattern, 'unknown')
        confidence = pattern_counts[most_common_pattern] / len(pattern_types)
        
        return {
            'Primary_intent': primary_intent,
            'confidence': confidence,
            'pattern_distribution': pattern_counts,
            'total_patterns': len(self.click_patterns),
            'recent_click_rate': len(self.temporal_windows[-1]) / self.temporal_window_size if self.temporal_windows else 0
        }
    
    def get_brain_map_feed(self) -> Dict[str, any]:
        """
        Get current brain map feed data.
        
        Returns:
            Dictionary containing brain map feed data
        """
        return self.brain_map_feed.copy()
    
    def clear_old_data(self, max_age_seconds: float = 3600):
        """
        Clear old click data.
        
        Args:
            max_age_seconds: Maximum age in seconds (default 1 hour)
        """
        current_time = datetime.now().timestamp()
        
        self.click_events = [
            c for c in self.click_events
            if current_time - c.timestamp < max_age_seconds
        ]
        
        self.click_patterns = [
            p for p in self.click_patterns
            if current_time - p.timestamp < max_age_seconds
        ]
        
        # Rebuild element clicks
        self.element_clicks = {}
        for click in self.click_events:
            if click.element_id:
                if click.element_id not in self.element_clicks:
                    self.element_clicks[click.element_id] = []
                self.element_clicks[click.element_id].append(click)
        
        # Rebuild temporal windows
        self.temporal_windows = []
        for click in self.click_events:
            self._update_temporal_windows(click)
