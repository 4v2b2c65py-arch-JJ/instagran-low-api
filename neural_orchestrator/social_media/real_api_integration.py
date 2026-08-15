"""
Real API Integration for Instagram and TikTok
Provides actual API access for profile matching and conversation testing.
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class Platform(Enum):
    """Social media platforms."""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"


class ProfileStatus(Enum):
    """Status of profile matching."""
    FOUND = "found"
    NOT_FOUND = "not_found"
    PRIVATE = "private"
    SUSPENDED = "suspended"
    ERROR = "error"


@dataclass
class UserProfile:
    """User profile from social media API."""
    platform: Platform
    username: str
    user_id: str
    profile_url: str
    display_name: str
    bio: str
    follower_count: int
    following_count: int
    is_verified: bool
    is_private: bool
    profile_picture_url: str
    status: ProfileStatus
    last_updated: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ConversationMessage:
    """Message from conversation history."""
    message_id: str
    platform: Platform
    sender_username: str
    recipient_username: str
    content: str
    timestamp: str
    is_from_me: bool
    message_type: str  # text, image, video, etc.
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ProximityMatch:
    """Proximity match between agents/users."""
    match_id: str
    user1_username: str
    user2_username: str
    proximity_score: float
    match_type: str  # "new_discovery", "established"
    common_interests: List[str]
    interaction_frequency: float
    last_interaction: str
    confidence: float


class RealAPIIntegration:
    """
    Real API integration for Instagram and TikTok.
    Provides actual profile matching and conversation testing.
    """

    def __init__(self, instagram_api_key: Optional[str] = None, tiktok_api_key: Optional[str] = None):
        self.instagram_api_key = instagram_api_key
        self.tiktok_api_key = tiktok_api_key
        self.hidden_profiles: Dict[str, UserProfile] = {}  # username -> profile
        self.conversation_history: Dict[str, List[ConversationMessage]] = {}
        self.proximity_matches: List[ProximityMatch] = []
        self.session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close_session(self) -> None:
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def search_instagram_profile(self, username: str) -> Optional[UserProfile]:
        """
        Search for Instagram profile using real API.
        
        Args:
            username: Instagram username
            
        Returns:
            UserProfile if found
        """
        if not self.instagram_api_key:
            print("Instagram API key not configured")
            return None
        
        session = await self._get_session()
        
        try:
            # Instagram Graph API endpoint
            url = f"https://graph.instagram.com/{username}?fields=id,username,biography,followers_count,follows_count,is_verified,profile_picture_url&access_token={self.instagram_api_key}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    profile = UserProfile(
                        platform=Platform.INSTAGRAM,
                        username=data.get("username", username),
                        user_id=data.get("id", ""),
                        profile_url=f"https://instagram.com/{username}",
                        display_name=data.get("username", username),
                        bio=data.get("biography", ""),
                        follower_count=data.get("followers_count", 0),
                        following_count=data.get("follows_count", 0),
                        is_verified=data.get("is_verified", False),
                        is_private=False,  # Would need additional API call
                        profile_picture_url=data.get("profile_picture_url", ""),
                        status=ProfileStatus.FOUND,
                        last_updated=datetime.utcnow().isoformat(),
                        metadata={"api_response": data}
                    )
                    
                    self.hidden_profiles[username] = profile
                    return profile
                else:
                    error_text = await response.text()
                    print(f"Instagram API error: {response.status} - {error_text}")
                    
                    return UserProfile(
                        platform=Platform.INSTAGRAM,
                        username=username,
                        user_id="",
                        profile_url=f"https://instagram.com/{username}",
                        display_name=username,
                        bio="",
                        follower_count=0,
                        following_count=0,
                        is_verified=False,
                        is_private=False,
                        profile_picture_url="",
                        status=ProfileStatus.NOT_FOUND,
                        last_updated=datetime.utcnow().isoformat()
                    )
                    
        except Exception as e:
            print(f"Error searching Instagram profile: {e}")
            return None

    async def search_tiktok_profile(self, username: str) -> Optional[UserProfile]:
        """
        Search for TikTok profile using real API.
        
        Args:
            username: TikTok username
            
        Returns:
            UserProfile if found
        """
        if not self.tiktok_api_key:
            print("TikTok API key not configured")
            return None
        
        session = await self._get_session()
        
        try:
            # TikTok API endpoint
            url = f"https://open.tiktokapis.com/v2/user/info/?fields=display_name,avatar_url,biography,follower_count,following_count,is_verified&username={username}"
            
            headers = {
                "Authorization": f"Bearer {self.tiktok_api_key}"
            }
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("data") and data["data"].get("user"):
                        user_data = data["data"]["user"]
                        
                        profile = UserProfile(
                            platform=Platform.TIKTOK,
                            username=username,
                            user_id=user_data.get("id", ""),
                            profile_url=f"https://tiktok.com/@{username}",
                            display_name=user_data.get("display_name", username),
                            bio=user_data.get("biography", ""),
                            follower_count=user_data.get("follower_count", 0),
                            following_count=user_data.get("following_count", 0),
                            is_verified=user_data.get("is_verified", False),
                            is_private=False,
                            profile_picture_url=user_data.get("avatar_url", ""),
                            status=ProfileStatus.FOUND,
                            last_updated=datetime.utcnow().isoformat(),
                            metadata={"api_response": data}
                        )
                        
                        self.hidden_profiles[username] = profile
                        return profile
                
                return UserProfile(
                    platform=Platform.TIKTOK,
                    username=username,
                    user_id="",
                    profile_url=f"https://tiktok.com/@{username}",
                    display_name=username,
                    bio="",
                    follower_count=0,
                    following_count=0,
                    is_verified=False,
                    is_private=False,
                    profile_picture_url="",
                    status=ProfileStatus.NOT_FOUND,
                    last_updated=datetime.utcnow().isoformat()
                )
                
        except Exception as e:
            print(f"Error searching TikTok profile: {e}")
            return None

    async def match_specific_users(self, usernames: List[str]) -> Dict[str, UserProfile]:
        """
        Match specific users across platforms.
        
        Args:
            usernames: List of usernames to match
            
        Returns:
            Dictionary of username -> UserProfile
        """
        results = {}
        
        for username in usernames:
            # Try Instagram first
            insta_profile = await self.search_instagram_profile(username)
            if insta_profile and insta_profile.status == ProfileStatus.FOUND:
                results[f"{username}_instagram"] = insta_profile
            
            # Try TikTok
            tiktok_profile = await self.search_tiktok_profile(username)
            if tiktok_profile and tiktok_profile.status == ProfileStatus.FOUND:
                results[f"{username}_tiktok"] = tiktok_profile
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.5)
        
        return results

    async def get_conversation_history(self, platform: Platform, username: str) -> List[ConversationMessage]:
        """
        Get conversation history for a user.
        
        Args:
            platform: Social media platform
            username: Username
            
        Returns:
            List of conversation messages
        """
        if not self.instagram_api_key and platform == Platform.INSTAGRAM:
            print("Instagram API key not configured")
            return []
        
        if not self.tiktok_api_key and platform == Platform.TIKTOK:
            print("TikTok API key not configured")
            return []
        
        session = await self._get_session()
        
        try:
            if platform == Platform.INSTAGRAM:
                # Instagram Messaging API
                url = f"https://graph.instagram.com/me/conversations?user_id={username}&fields=messages,participants&access_token={self.instagram_api_key}"
            else:
                # TikTok Messaging API
                url = f"https://open.tiktokapis.com/v2/message/list/?username={username}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    messages = []
                    # Parse messages from API response
                    # This would depend on actual API structure
                    
                    key = f"{platform.value}_{username}"
                    self.conversation_history[key] = messages
                    
                    return messages
                else:
                    print(f"Error getting conversation history: {response.status}")
                    return []
                    
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []

    async def send_message(
        self,
        platform: Platform,
        recipient_username: str,
        content: str,
        message_type: str = "text"
    ) -> bool:
        """
        Send a message to a user.
        
        Args:
            platform: Social media platform
            recipient_username: Recipient username
            content: Message content
            message_type: Type of message
            
        Returns:
            True if successful
        """
        if not self.instagram_api_key and platform == Platform.INSTAGRAM:
            print("Instagram API key not configured")
            return False
        
        if not self.tiktok_api_key and platform == Platform.TIKTOK:
            print("TikTok API key not configured")
            return False
        
        session = await self._get_session()
        
        try:
            if platform == Platform.INSTAGRAM:
                url = f"https://graph.instagram.com/me/messages?access_token={self.instagram_api_key}"
                payload = {
                    "recipient": {"id": recipient_username},
                    "message": {"text": content}
                }
            else:
                url = f"https://open.tiktokapis.com/v2/message/send/"
                headers = {"Authorization": f"Bearer {self.tiktok_api_key}"}
                payload = {
                    "to_user_id": recipient_username,
                    "content": content,
                    "content_type": message_type
                }
            
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    print(f"Message sent to {recipient_username} on {platform.value}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"Error sending message: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"Error sending message: {e}")
            return False

    def calculate_proximity(
        self,
        user1: UserProfile,
        user2: UserProfile,
        interaction_data: Optional[Dict[str, Any]] = None
    ) -> ProximityMatch:
        """
        Calculate proximity match between two users.
        
        Args:
            user1: First user profile
            user2: Second user profile
            interaction_data: Optional interaction data
            
        Returns:
            ProximityMatch
        """
        # Calculate proximity score based on various factors
        score = 0.0
        
        # Follower count similarity
        follower_diff = abs(user1.follower_count - user2.follower_count)
        follower_similarity = 1.0 - min(follower_diff / max(user1.follower_count, user2.follower_count, 1), 1.0)
        score += follower_similarity * 0.3
        
        # Verification status match
        if user1.is_verified == user2.is_verified:
            score += 0.2
        
        # Bio similarity (simple word overlap)
        bio1_words = set(user1.bio.lower().split())
        bio2_words = set(user2.bio.lower().split())
        if bio1_words and bio2_words:
            bio_similarity = len(bio1_words & bio2_words) / len(bio1_words | bio2_words)
            score += bio_similarity * 0.2
        
        # Interaction frequency
        interaction_freq = interaction_data.get("frequency", 0.0) if interaction_data else 0.0
        score += min(interaction_freq, 1.0) * 0.3
        
        # Determine match type
        match_type = "new_discovery" if score < 0.5 else "established"
        
        # Common interests (from bio keywords)
        common_interests = list(bio1_words & bio2_words)
        
        match_id = f"match_{user1.username}_{user2.username}_{int(score * 100)}"
        
        proximity_match = ProximityMatch(
            match_id=match_id,
            user1_username=user1.username,
            user2_username=user2.username,
            proximity_score=score,
            match_type=match_type,
            common_interests=common_interests,
            interaction_frequency=interaction_freq,
            last_interaction=datetime.utcnow().isoformat(),
            confidence=score
        )
        
        self.proximity_matches.append(proximity_match)
        return proximity_match

    def get_hidden_profile(self, username: str) -> Optional[UserProfile]:
        """Get hidden profile by username."""
        return self.hidden_profiles.get(username)

    def get_all_hidden_profiles(self) -> List[UserProfile]:
        """Get all hidden profiles."""
        return list(self.hidden_profiles.values())

    def get_proximity_matches(self, min_score: float = 0.0) -> List[ProximityMatch]:
        """Get proximity matches above minimum score."""
        return [m for m in self.proximity_matches if m.proximity_score >= min_score]

    def export_hidden_profiles(self) -> str:
        """Export hidden profiles for backup."""
        return json.dumps([asdict(profile) for profile in self.hidden_profiles.values()], indent=2)

    def import_hidden_profiles(self, profiles_json: str) -> bool:
        """Import hidden profiles from backup."""
        try:
            profile_dicts = json.loads(profiles_json)
            for profile_dict in profile_dicts:
                profile_dict["platform"] = Platform(profile_dict["platform"])
                profile_dict["status"] = ProfileStatus(profile_dict["status"])
                profile = UserProfile(**profile_dict)
                self.hidden_profiles[profile.username] = profile
            return True
        except Exception as e:
            print(f"Error importing profiles: {e}")
            return False

    async def cleanup(self) -> None:
        """Cleanup resources."""
        await self.close_session()
