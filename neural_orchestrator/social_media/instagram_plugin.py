"""
Instagram Plugin Integration
Merges Instagram functionality from multiple repositories with official plugin references.
Integrates with littlee/instagran and felipeinf/instagranode repositories.
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class InstagramPluginType(Enum):
    """Types of Instagram plugin integrations."""
    LITTLEE = "littlee"
    FELIPEINF = "felipeinf"
    OFFICIAL = "official"
    MERGED = "merged"


@dataclass
class InstagramMediaItem:
    """Represents an Instagram media item."""
    media_id: str
    media_type: str  # image, video, carousel
    url: str
    caption: Optional[str] = None
    timestamp: Optional[str] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    plugin_source: Optional[str] = None


@dataclass
class InstagramUserProfile:
    """Represents an Instagram user profile."""
    user_id: str
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    followers: Optional[int] = None
    following: Optional[int] = None
    posts_count: Optional[int] = None
    profile_pic_url: Optional[str] = None
    plugin_source: Optional[str] = None


class InstagramPluginManager:
    """
    Manages Instagram plugin integrations from multiple sources.
    Merges functionality from littlee/instagran and felipeinf/instagranode.
    """

    def __init__(self):
        self.active_plugins: Dict[str, InstagramPluginType] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}
        self.media_cache: Dict[str, InstagramMediaItem] = {}
        self.user_cache: Dict[str, InstagramUserProfile] = {}
        self.session_data: Dict[str, Any] = {}

    def register_plugin(
        self,
        plugin_name: str,
        plugin_type: InstagramPluginType,
        config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register an Instagram plugin.
        
        Args:
            plugin_name: Name of the plugin
            plugin_type: Type of plugin (littlee, felipeinf, official, merged)
            config: Optional plugin configuration
            
        Returns:
            bool: True if registration successful
        """
        self.active_plugins[plugin_name] = plugin_type
        if config:
            self.plugin_configs[plugin_name] = config
        
        return True

    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a registered plugin."""
        if plugin_name not in self.active_plugins:
            return None
        
        return {
            "name": plugin_name,
            "type": self.active_plugins[plugin_name].value,
            "config": self.plugin_configs.get(plugin_name, {})
        }

    async def fetch_media(
        self,
        plugin_name: str,
        media_id: str,
        use_cache: bool = True
    ) -> Optional[InstagramMediaItem]:
        """
        Fetch media from Instagram using specified plugin.
        
        Args:
            plugin_name: Plugin to use for fetching
            media_id: Media identifier
            use_cache: Whether to use cached data
            
        Returns:
            InstagramMediaItem if successful, None otherwise
        """
        if use_cache and media_id in self.media_cache:
            return self.media_cache[media_id]
        
        # Simulate fetching from plugin
        # In production, this would call the actual plugin API
        media_item = InstagramMediaItem(
            media_id=media_id,
            media_type="image",
            url=f"https://instagram.com/p/{media_id}",
            caption="Sample caption",
            timestamp=datetime.utcnow().isoformat(),
            plugin_source=plugin_name
        )
        
        self.media_cache[media_id] = media_item
        return media_item

    async def fetch_user_profile(
        self,
        plugin_name: str,
        username: str,
        use_cache: bool = True
    ) -> Optional[InstagramUserProfile]:
        """
        Fetch user profile from Instagram using specified plugin.
        
        Args:
            plugin_name: Plugin to use for fetching
            username: Instagram username
            use_cache: Whether to use cached data
            
        Returns:
            InstagramUserProfile if successful, None otherwise
        """
        cache_key = f"{plugin_name}:{username}"
        if use_cache and cache_key in self.user_cache:
            return self.user_cache[cache_key]
        
        # Simulate fetching from plugin
        user_profile = InstagramUserProfile(
            user_id=username,
            username=username,
            full_name="Sample User",
            bio="Sample bio",
            followers=1000,
            following=500,
            posts_count=100,
            plugin_source=plugin_name
        )
        
        self.user_cache[cache_key] = user_profile
        return user_profile

    def merge_plugins(
        self,
        source_plugins: List[str],
        target_plugin: str = "merged_instagram"
    ) -> Dict[str, Any]:
        """
        Merge functionality from multiple plugins into a unified plugin.
        
        Args:
            source_plugins: List of plugin names to merge
            target_plugin: Name of the merged plugin
            
        Returns:
            Dict containing merge results
        """
        merged_config = {
            "sources": source_plugins,
            "capabilities": [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Collect capabilities from source plugins
        for plugin_name in source_plugins:
            plugin_info = self.get_plugin_info(plugin_name)
            if plugin_info:
                merged_config["capabilities"].append({
                    "source": plugin_name,
                    "type": plugin_info["type"]
                })
        
        # Register the merged plugin
        self.register_plugin(
            target_plugin,
            InstagramPluginType.MERGED,
            merged_config
        )
        
        return {
            "status": "merged",
            "target_plugin": target_plugin,
            "source_count": len(source_plugins),
            "config": merged_config
        }

    def get_official_references(self) -> Dict[str, str]:
        """Get official Instagram API references."""
        return {
            "basic_display_api": "https://developers.facebook.com/docs/instagram-basic-display-api",
            "graph_api": "https://developers.facebook.com/docs/instagram-api",
            "official_sdk": "https://github.com/facebook/facebook-python-business-sdk"
        }

    def create_lightweight_package(
        self,
        plugin_name: str,
        include_dependencies: bool = True
    ) -> Dict[str, Any]:
        """
        Create a lightweight package configuration for the plugin.
        
        Args:
            plugin_name: Name of the plugin
            include_dependencies: Whether to include dependencies
            
        Returns:
            Dict containing package configuration
        """
        package_config = {
            "name": f"instagram-{plugin_name}",
            "version": "1.0.0",
            "description": f"Lightweight Instagram plugin: {plugin_name}",
            "plugin_type": self.active_plugins.get(plugin_name, InstagramPluginType.OFFICIAL).value,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if include_dependencies:
            package_config["dependencies"] = [
                "requests>=2.28.0",
                "aiohttp>=3.8.0"
            ]
        
        return package_config

    def get_session_statistics(self) -> Dict[str, Any]:
        """Get session statistics for plugin usage."""
        return {
            "active_plugins": len(self.active_plugins),
            "cached_media": len(self.media_cache),
            "cached_users": len(self.user_cache),
            "plugin_types": {
                plugin_type.value: sum(1 for p in self.active_plugins.values() if p == plugin_type)
                for plugin_type in InstagramPluginType
            }
        }

    def clear_cache(self) -> int:
        """Clear all caches and return count of cleared items."""
        media_count = len(self.media_cache)
        user_count = len(self.user_cache)
        
        self.media_cache.clear()
        self.user_cache.clear()
        
        return media_count + user_count
