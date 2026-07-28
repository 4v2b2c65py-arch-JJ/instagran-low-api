"""
Device Input Collector - Feeds Brain Map Layer
Collects device inputs including cache, emoji, and auto-corrector suggestions.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class DeviceCache:
    """Represents device cache data."""
    cache_id: str
    data: Dict[str, any]
    size_bytes: int
    timestamp: float
    access_frequency: int


@dataclass
class EmojiUsage:
    """Represents emoji usage data."""
    emoji: str
    usage_count: int
    context: str
    timestamp: float
    sentiment_score: float


@dataclass
class AutoCorrectorSuggestion:
    """Represents auto-corrector suggestion data."""
    original_text: str
    corrected_text: str
    confidence: float
    context: str
    timestamp: float
    accepted: bool


class DeviceInputCollector:
    """
    Collects device inputs to feed the brain map layer.
    Gathers cache data, emoji usage, and auto-corrector suggestions.
    """
    
    def __init__(self, brain_map_layer: Optional[str] = None):
        """
        Initialize the Device Input Collector.
        
        Args:
            brain_map_layer: Target brain map layer for feeding data
        """
        self.brain_map_layer = brain_map_layer
        
        # Storage for device inputs
        self.cache_data: List[DeviceCache] = []
        self.emoji_usage: List[EmojiUsage] = []
        self.auto_corrector_suggestions: List[AutoCorrectorSuggestion] = []
        
        # Device state tracking
        self.device_id = "device_001"
        self.last_sync_timestamp = datetime.now().timestamp()
        
        # Brain map integration
        self.brain_map_feed: Dict[str, any] = {}
    
    def collect_cache_data(
        self,
        cache_key: str,
        cache_data: Dict[str, any],
        size_bytes: int = 0
    ) -> DeviceCache:
        """
        Collect device cache data.
        
        Args:
            cache_key: Cache key identifier
            cache_data: Cache data contents
            size_bytes: Size of cache in bytes
            
        Returns:
            DeviceCache object
        """
        cache = DeviceCache(
            cache_id=f"cache_{cache_key}_{datetime.now().timestamp()}",
            data=cache_data,
            size_bytes=size_bytes,
            timestamp=datetime.now().timestamp(),
            access_frequency=1
        )
        
        # Update existing cache or add new
        existing = self._find_existing_cache(cache_key)
        if existing:
            existing.access_frequency += 1
            existing.data = cache_data
            existing.timestamp = cache.timestamp
        else:
            self.cache_data.append(cache)
        
        # Feed to brain map
        self._feed_to_brain_map('cache', cache)
        
        return cache
    
    def collect_emoji_usage(
        self,
        emoji: str,
        context: str = "",
        sentiment_score: float = 0.0
    ) -> EmojiUsage:
        """
        Collect emoji usage data.
        
        Args:
            emoji: Emoji character
            context: Context of emoji usage
            sentiment_score: Sentiment score (-1 to 1)
            
        Returns:
            EmojiUsage object
        """
        # Update existing emoji or add new
        existing = self._find_existing_emoji(emoji)
        if existing:
            existing.usage_count += 1
            existing.context = context
            existing.timestamp = datetime.now().timestamp()
            existing.sentiment_score = sentiment_score
            usage = existing
        else:
            usage = EmojiUsage(
                emoji=emoji,
                usage_count=1,
                context=context,
                timestamp=datetime.now().timestamp(),
                sentiment_score=sentiment_score
            )
            self.emoji_usage.append(usage)
        
        # Feed to brain map
        self._feed_to_brain_map('emoji', usage)
        
        return usage
    
    def collect_auto_corrector_suggestion(
        self,
        original_text: str,
        corrected_text: str,
        confidence: float,
        context: str = "",
        accepted: bool = False
    ) -> AutoCorrectorSuggestion:
        """
        Collect auto-corrector suggestion data.
        
        Args:
            original_text: Original text before correction
            corrected_text: Corrected text suggestion
            confidence: Confidence score (0-1)
            context: Context of the correction
            accepted: Whether the suggestion was accepted
            
        Returns:
            AutoCorrectorSuggestion object
        """
        suggestion = AutoCorrectorSuggestion(
            original_text=original_text,
            corrected_text=corrected_text,
            confidence=confidence,
            context=context,
            timestamp=datetime.now().timestamp(),
            accepted=accepted
        )
        
        self.auto_corrector_suggestions.append(suggestion)
        
        # Feed to brain map
        self._feed_to_brain_map('auto_corrector', suggestion)
        
        return suggestion
    
    def _find_existing_cache(self, cache_key: str) -> Optional[DeviceCache]:
        """Find existing cache entry by key."""
        for cache in self.cache_data:
            if cache_key in cache.cache_id:
                return cache
        return None
    
    def _find_existing_emoji(self, emoji: str) -> Optional[EmojiUsage]:
        """Find existing emoji usage entry."""
        for usage in self.emoji_usage:
            if usage.emoji == emoji:
                return usage
        return None
    
    def _feed_to_brain_map(self, input_type: str, data: any):
        """
        Feed collected data to brain map layer.
        
        Args:
            input_type: Type of input (cache, emoji, auto_corrector)
            data: Data to feed
        """
        if input_type not in self.brain_map_feed:
            self.brain_map_feed[input_type] = []
        
        # Convert data to dictionary for brain map
        if hasattr(data, '__dict__'):
            feed_data = data.__dict__.copy()
        else:
            feed_data = {'data': data}
        
        self.brain_map_feed[input_type].append(feed_data)
        
        # Keep feed manageable
        if len(self.brain_map_feed[input_type]) > 100:
            self.brain_map_feed[input_type].pop(0)
    
    def get_brain_map_feed(self) -> Dict[str, any]:
        """
        Get current brain map feed data.
        
        Returns:
            Dictionary containing all brain map feed data
        """
        return self.brain_map_feed.copy()
    
    def get_cache_statistics(self) -> Dict[str, any]:
        """
        Get statistics about collected cache data.
        
        Returns:
            Dictionary containing cache statistics
        """
        if not self.cache_data:
            return {'total_entries': 0}
        
        sizes = [c.size_bytes for c in self.cache_data]
        frequencies = [c.access_frequency for c in self.cache_data]
        
        return {
            'total_entries': len(self.cache_data),
            'total_size_bytes': sum(sizes),
            'avg_size_bytes': np.mean(sizes),
            'max_size_bytes': max(sizes),
            'avg_access_frequency': np.mean(frequencies),
            'most_accessed': max(self.cache_data, key=lambda c: c.access_frequency).cache_id
        }
    
    def get_emoji_statistics(self) -> Dict[str, any]:
        """
        Get statistics about emoji usage.
        
        Returns:
            Dictionary containing emoji statistics
        """
        if not self.emoji_usage:
            return {'total_unique_emojis': 0}
        
        usage_counts = [e.usage_count for e in self.emoji_usage]
        sentiments = [e.sentiment_score for e in self.emoji_usage]
        
        return {
            'total_unique_emojis': len(self.emoji_usage),
            'total_usage': sum(usage_counts),
            'avg_usage_per_emoji': np.mean(usage_counts),
            'most_used_emoji': max(self.emoji_usage, key=lambda e: e.usage_count).emoji,
            'avg_sentiment': np.mean(sentiments),
            'sentiment_distribution': self._get_sentiment_distribution()
        }
    
    def _get_sentiment_distribution(self) -> Dict[str, int]:
        """Get distribution of sentiment scores."""
        distribution = {'positive': 0, 'neutral': 0, 'negative': 0}
        
        for usage in self.emoji_usage:
            if usage.sentiment_score > 0.3:
                distribution['positive'] += 1
            elif usage.sentiment_score < -0.3:
                distribution['negative'] += 1
            else:
                distribution['neutral'] += 1
        
        return distribution
    
    def get_auto_corrector_statistics(self) -> Dict[str, any]:
        """
        Get statistics about auto-corrector suggestions.
        
        Returns:
            Dictionary containing auto-corrector statistics
        """
        if not self.auto_corrector_suggestions:
            return {'total_suggestions': 0}
        
        confidences = [s.confidence for s in self.auto_corrector_suggestions]
        accepted_count = sum(1 for s in self.auto_corrector_suggestions if s.accepted)
        
        return {
            'total_suggestions': len(self.auto_corrector_suggestions),
            'accepted_count': accepted_count,
            'acceptance_rate': accepted_count / len(self.auto_corrector_suggestions),
            'avg_confidence': np.mean(confidences),
            'high_confidence_count': sum(1 for c in confidences if c > 0.8)
        }
    
    def sync_to_brain_map(self) -> Dict[str, any]:
        """
        Sync all collected data to brain map layer.
        
        Returns:
            Dictionary containing sync results
        """
        sync_data = {
            'device_id': self.device_id,
            'sync_timestamp': datetime.now().timestamp(),
            'cache_data': [c.__dict__ for c in self.cache_data],
            'emoji_usage': [e.__dict__ for e in self.emoji_usage],
            'auto_corrector_suggestions': [s.__dict__ for s in self.auto_corrector_suggestions],
            'brain_map_feed': self.brain_map_feed
        }
        
        self.last_sync_timestamp = datetime.now().timestamp()
        
        return sync_data
    
    def clear_old_data(self, max_age_seconds: float = 86400):
        """
        Clear data older than specified age.
        
        Args:
            max_age_seconds: Maximum age in seconds (default 24 hours)
        """
        current_time = datetime.now().timestamp()
        
        # Clear old cache data
        self.cache_data = [
            c for c in self.cache_data 
            if current_time - c.timestamp < max_age_seconds
        ]
        
        # Clear old emoji usage
        self.emoji_usage = [
            e for e in self.emoji_usage 
            if current_time - e.timestamp < max_age_seconds
        ]
        
        # Clear old auto-corrector suggestions
        self.auto_corrector_suggestions = [
            s for s in self.auto_corrector_suggestions 
            if current_time - s.timestamp < max_age_seconds
        ]
