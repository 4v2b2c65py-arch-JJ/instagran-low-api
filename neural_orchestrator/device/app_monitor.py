"""
App Interaction Plugin - Social Platform Monitoring
Monitors app interactions for social platforms and feeds data to brain map layer.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class SocialPlatform(Enum):
    """Supported social platforms."""
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"
    REDDIT = "reddit"
    SNAPCHAT = "snapchat"
    YOUTUBE = "youtube"
    GENERIC = "generic"


@dataclass
class AppInteraction:
    """Represents an app interaction event."""
    interaction_id: str
    platform: SocialPlatform
    interaction_type: str  # like, comment, share, view, scroll, post, etc.
    content_data: Dict[str, any]
    timestamp: float
    duration_seconds: float
    user_engagement_score: float


@dataclass
class SocialMetrics:
    """Represents social platform metrics."""
    platform: SocialPlatform
    total_interactions: int
    avg_engagement_score: float
    most_common_interaction: str
    time_spent_minutes: float
    sentiment_trend: float


class AppInteractionPlugin:
    """
    Plugin for monitoring app interactions on social platforms.
    Tracks user behavior and feeds data to brain map layer.
    """
    
    def __init__(self, brain_map_layer: Optional[str] = None):
        """
        Initialize the App Interaction Plugin.
        
        Args:
            brain_map_layer: Target brain map layer for feeding data
        """
        self.brain_map_layer = brain_map_layer
        
        # Interaction storage
        self.interactions: List[AppInteraction] = []
        self.platform_metrics: Dict[SocialPlatform, SocialMetrics] = {}
        
        # Platform-specific tracking
        self.platform_sessions: Dict[SocialPlatform, List[Dict]] = {}
        
        # Engagement patterns
        self.engagement_patterns: Dict[str, List[float]] = {}
        
        # Brain map feed
        self.brain_map_feed: Dict[str, any] = {}
    
    def track_interaction(
        self,
        platform: SocialPlatform,
        interaction_type: str,
        content_data: Dict[str, any],
        duration_seconds: float = 0.0,
        user_engagement_score: float = 0.5
    ) -> AppInteraction:
        """
        Track an app interaction event.
        
        Args:
            platform: Social platform
            interaction_type: Type of interaction (like, comment, share, etc.)
            content_data: Content-related data
            duration_seconds: Duration of interaction
            user_engagement_score: User engagement score (0-1)
            
        Returns:
            AppInteraction object
        """
        interaction = AppInteraction(
            interaction_id=f"interaction_{len(self.interactions)}_{datetime.now().timestamp()}",
            platform=platform,
            interaction_type=interaction_type,
            content_data=content_data,
            timestamp=datetime.now().timestamp(),
            duration_seconds=duration_seconds,
            user_engagement_score=user_engagement_score
        )
        
        self.interactions.append(interaction)
        
        # Update platform metrics
        self._update_platform_metrics(platform, interaction)
        
        # Track engagement patterns
        self._track_engagement_pattern(platform, interaction_type, user_engagement_score)
        
        # Feed to brain map
        self._feed_to_brain_map('app_interaction', interaction)
        
        return interaction
    
    def _update_platform_metrics(self, platform: SocialPlatform, interaction: AppInteraction):
        """
        Update metrics for a specific platform.
        
        Args:
            platform: Social platform
            interaction: App interaction
        """
        platform_interactions = [i for i in self.interactions if i.platform == platform]
        
        if not platform_interactions:
            return
        
        total_interactions = len(platform_interactions)
        avg_engagement = np.mean([i.user_engagement_score for i in platform_interactions])
        
        # Find most common interaction type
        interaction_types = [i.interaction_type for i in platform_interactions]
        most_common = max(set(interaction_types), key=interaction_types.count) if interaction_types else "unknown"
        
        # Calculate total time spent
        total_time = sum([i.duration_seconds for i in platform_interactions]) / 60.0  # Convert to minutes
        
        # Calculate sentiment trend (based on engagement)
        recent_engagement = [i.user_engagement_score for i in platform_interactions[-10:]]
        sentiment_trend = np.mean(recent_engagement) - 0.5 if recent_engagement else 0.0
        
        metrics = SocialMetrics(
            platform=platform,
            total_interactions=total_interactions,
            avg_engagement_score=avg_engagement,
            most_common_interaction=most_common,
            time_spent_minutes=total_time,
            sentiment_trend=sentiment_trend
        )
        
        self.platform_metrics[platform] = metrics
    
    def _track_engagement_pattern(self, platform: SocialPlatform, interaction_type: str, engagement_score: float):
        """
        Track engagement patterns for analysis.
        
        Args:
            platform: Social platform
            interaction_type: Type of interaction
            engagement_score: Engagement score
        """
        pattern_key = f"{platform.value}_{interaction_type}"
        
        if pattern_key not in self.engagement_patterns:
            self.engagement_patterns[pattern_key] = []
        
        self.engagement_patterns[pattern_key].append(engagement_score)
        
        # Keep pattern history manageable
        if len(self.engagement_patterns[pattern_key]) > 100:
            self.engagement_patterns[pattern_key].pop(0)
    
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
            if 'platform' in feed_data:
                feed_data['platform'] = feed_data['platform'].value
        else:
            feed_data = {'data': data}
        
        self.brain_map_feed[feed_type].append(feed_data)
        
        if len(self.brain_map_feed[feed_type]) > 100:
            self.brain_map_feed[feed_type].pop(0)
    
    def start_platform_session(self, platform: SocialPlatform) -> str:
        """
        Start a session for a specific platform.
        
        Args:
            platform: Social platform
            
        Returns:
            Session ID
        """
        session_id = f"session_{platform.value}_{datetime.now().timestamp()}"
        
        if platform not in self.platform_sessions:
            self.platform_sessions[platform] = []
        
        self.platform_sessions[platform].append({
            'session_id': session_id,
            'start_time': datetime.now().timestamp(),
            'end_time': None,
            'interactions': []
        })
        
        return session_id
    
    def end_platform_session(self, platform: SocialPlatform, session_id: str):
        """
        End a platform session.
        
        Args:
            platform: Social platform
            session_id: Session ID to end
        """
        if platform in self.platform_sessions:
            for session in self.platform_sessions[platform]:
                if session['session_id'] == session_id:
                    session['end_time'] = datetime.now().timestamp()
                    break
    
    def get_platform_metrics(self, platform: SocialPlatform) -> Optional[SocialMetrics]:
        """
        Get metrics for a specific platform.
        
        Args:
            platform: Social platform
            
        Returns:
            SocialMetrics object or None
        """
        return self.platform_metrics.get(platform)
    
    def get_all_platform_metrics(self) -> Dict[str, SocialMetrics]:
        """
        Get metrics for all platforms.
        
        Returns:
            Dictionary mapping platform names to metrics
        """
        return {p.value: m for p, m in self.platform_metrics.items()}
    
    def get_engagement_pattern(self, platform: SocialPlatform, interaction_type: str) -> Dict[str, float]:
        """
        Get engagement pattern for specific platform and interaction type.
        
        Args:
            platform: Social platform
            interaction_type: Type of interaction
            
        Returns:
            Dictionary containing pattern statistics
        """
        pattern_key = f"{platform.value}_{interaction_type}"
        scores = self.engagement_patterns.get(pattern_key, [])
        
        if not scores:
            return {
                'count': 0,
                'avg_score': 0.0,
                'trend': 0.0
            }
        
        return {
            'count': len(scores),
            'avg_score': np.mean(scores),
            'min_score': min(scores),
            'max_score': max(scores),
            'std_score': np.std(scores),
            'trend': scores[-1] - scores[0] if len(scores) > 1 else 0.0
        }
    
    def analyze_user_behavior(self) -> Dict[str, any]:
        """
        Analyze overall user behavior across platforms.
        
        Returns:
            Dictionary containing behavior analysis
        """
        if not self.interactions:
            return {'status': 'no_data'}
        
        # Calculate overall engagement
        engagement_scores = [i.user_engagement_score for i in self.interactions]
        avg_engagement = np.mean(engagement_scores)
        
        # Calculate time distribution
        platform_times = {}
        for platform, metrics in self.platform_metrics.items():
            platform_times[platform.value] = metrics.time_spent_minutes
        
        # Find favorite platform
        favorite_platform = max(
            self.platform_metrics.items(),
            key=lambda x: x[1].total_interactions
        )[0].value if self.platform_metrics else "unknown"
        
        # Calculate interaction diversity
        interaction_types = set(i.interaction_type for i in self.interactions)
        diversity_score = len(interaction_types) / 10.0  # Normalize
        
        return {
            'total_interactions': len(self.interactions),
            'avg_engagement_score': avg_engagement,
            'favorite_platform': favorite_platform,
            'platform_time_distribution': platform_times,
            'interaction_diversity': min(diversity_score, 1.0),
            'most_active_platform': max(platform_times, key=platform_times.get) if platform_times else "unknown",
            'total_time_spent_minutes': sum(platform_times.values())
        }
    
    def detect_anomalies(self, threshold: float = 2.0) -> List[Dict]:
        """
        Detect anomalous interaction patterns.
        
        Args:
            threshold: Standard deviation threshold for anomaly detection
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Check for unusual engagement scores
        engagement_scores = [i.user_engagement_score for i in self.interactions]
        if len(engagement_scores) > 10:
            mean_score = np.mean(engagement_scores)
            std_score = np.std(engagement_scores)
            
            for interaction in self.interactions:
                score = interaction.user_engagement_score
                if abs(score - mean_score) > threshold * std_score:
                    anomalies.append({
                        'type': 'unusual_engagement',
                        'interaction_id': interaction.interaction_id,
                        'platform': interaction.platform.value,
                        'score': score,
                        'deviation': abs(score - mean_score) / std_score
                    })
        
        # Check for rapid interaction bursts
        if len(self.interactions) > 20:
            recent_interactions = self.interactions[-20:]
            timestamps = [i.timestamp for i in recent_interactions]
            time_diffs = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
            
            if time_diffs and np.mean(time_diffs) < 1.0:  # Less than 1 second between interactions
                anomalies.append({
                    'type': 'rapid_interaction_burst',
                    'platform': recent_interactions[0].platform.value,
                    'avg_time_between': np.mean(time_diffs),
                    'interaction_count': len(recent_interactions)
                })
        
        return anomalies
    
    def get_brain_map_feed(self) -> Dict[str, any]:
        """
        Get current brain map feed data.
        
        Returns:
            Dictionary containing brain map feed data
        """
        return self.brain_map_feed.copy()
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get overall plugin statistics.
        
        Returns:
            Dictionary containing plugin statistics
        """
        return {
            'total_interactions': len(self.interactions),
            'platforms_tracked': len(self.platform_metrics),
            'engagement_patterns_tracked': len(self.engagement_patterns),
            'active_sessions': sum(len(sessions) for sessions in self.platform_sessions.values()),
            'brain_map_feed_size': sum(len(feed) for feed in self.brain_map_feed.values())
        }
    
    def clear_old_data(self, max_age_seconds: float = 604800):  # 7 days default
        """
        Clear old interaction data.
        
        Args:
            max_age_seconds: Maximum age in seconds
        """
        current_time = datetime.now().timestamp()
        
        self.interactions = [
            i for i in self.interactions
            if current_time - i.timestamp < max_age_seconds
        ]
        
        # Recalculate platform metrics
        for platform in list(self.platform_metrics.keys()):
            platform_interactions = [i for i in self.interactions if i.platform == platform]
            if platform_interactions:
                self._update_platform_metrics(platform, platform_interactions[-1])
            else:
                del self.platform_metrics[platform]
