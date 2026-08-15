"""Social media integration module."""

from .format_handlers import SocialMediaFormatHandlers
from .sha_sharing import SHASharingSystem
from .chat_conversation import ChatConversationManager
from .instagram_plugin import InstagramPluginManager, InstagramPluginType, InstagramMediaItem, InstagramUserProfile
from .real_api_integration import (
    RealAPIIntegration,
    Platform,
    ProfileStatus,
    UserProfile as SocialUserProfile,
    ConversationMessage,
    ProximityMatch
)
from .test_suite import (
    SocialMediaTestSuite,
    TestStatus,
    TestType,
    TestCase,
    TestSession
)
from .device_permissions import DevicePermissionManager
from .broadband_handler import BroadbandHandler
from .streaming_formats import StreamingFormatHandler

__all__ = [
    'SocialMediaFormatHandlers',
    'SHASharingSystem',
    'ChatConversationManager',
    'InstagramPluginManager',
    'InstagramPluginType',
    'InstagramMediaItem',
    'InstagramUserProfile',
    'RealAPIIntegration',
    'Platform',
    'ProfileStatus',
    'SocialUserProfile',
    'ConversationMessage',
    'ProximityMatch',
    'SocialMediaTestSuite',
    'TestStatus',
    'TestType',
    'TestCase',
    'TestSession',
    'DevicePermissionManager',
    'BroadbandHandler',
    'StreamingFormatHandler'
]
