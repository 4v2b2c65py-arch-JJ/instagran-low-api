"""
Example usage of Real API Integration and Test Suite
Demonstrates specific user matching and interactive testing for target users.
"""

import asyncio
import os
from neural_orchestrator.social_media import (
    RealAPIIntegration,
    SocialMediaTestSuite,
    Platform
)


async def main():
    """Main example demonstrating real API testing."""
    
    print("=== Real API Integration and Testing Example ===\n")
    
    # Get API keys from environment (user should set these)
    instagram_api_key = os.getenv("INSTAGRAM_API_KEY")
    tiktok_api_key = os.getenv("TIKTOK_API_KEY")
    
    if not instagram_api_key and not tiktok_api_key:
        print("⚠️  No API keys found in environment variables")
        print("To test with real APIs, set:")
        print("  export INSTAGRAM_API_KEY='your_instagram_key'")
        print("  export TIKTOK_API_KEY='your_tiktok_key'")
        print("\nRunning in demonstration mode...\n")
    
    # Initialize API integration
    api_integration = RealAPIIntegration(
        instagram_api_key=instagram_api_key,
        tiktok_api_key=tiktok_api_key
    )
    
    # Initialize test suite
    test_suite = SocialMediaTestSuite(api_integration)
    
    # Target users specified by user
    target_users = [
        "katiewynnz",
        "pavuk1_0",
        "billieeilish", 
        "cinnannoe",
        "snowie5370"
    ]
    
    print(f"Target users for testing: {', '.join(target_users)}\n")
    
    # Create test session
    session = test_suite.create_test_session()
    print(f"Created test session: {session.session_id}\n")
    
    # Test 1: Profile matching for target users
    print("1. Testing Profile Matching for Target Users")
    print("-" * 50)
    
    for username in target_users:
        print(f"\nTesting profile: {username}")
        
        # Test Instagram
        insta_profile = await api_integration.search_instagram_profile(username)
        if insta_profile:
            print(f"  Instagram: {insta_profile.status.value}")
            if insta_profile.status.value == "found":
                print(f"    - User ID: {insta_profile.user_id}")
                print(f"    - Followers: {insta_profile.follower_count}")
                print(f"    - Verified: {insta_profile.is_verified}")
                print(f"    - Private: {insta_profile.is_private}")
        
        # Test TikTok
        tiktok_profile = await api_integration.search_tiktok_profile(username)
        if tiktok_profile:
            print(f"  TikTok: {tiktok_profile.status.value}")
            if tiktok_profile.status.value == "found":
                print(f"    - User ID: {tiktok_profile.user_id}")
                print(f"    - Followers: {tiktok_profile.follower_count}")
                print(f"    - Verified: {tiktok_profile.is_verified}")
        
        # Record as hidden profile
        if insta_profile and insta_profile.status.value == "found":
            test_suite.record_user_interaction("profile_discovery", {
                "username": username,
                "platform": "instagram",
                "profile_id": insta_profile.user_id
            })
        
        await asyncio.sleep(0.5)  # Rate limiting
    
    print("\n2. Testing Conversation History")
    print("-" * 50)
    
    # Test conversation history for first user
    test_user = target_users[0]
    print(f"\nTesting conversation history for: {test_user}")
    
    messages = await api_integration.get_conversation_history(Platform.INSTAGRAM, test_user)
    print(f"  Messages found: {len(messages)}")
    
    if messages:
        print(f"  Sample messages:")
        for msg in messages[:3]:
            print(f"    - {msg.sender_username}: {msg.content[:50]}...")
    
    test_suite.record_user_interaction("conversation_history_test", {
        "username": test_user,
        "message_count": len(messages)
    })
    
    print("\n3. Testing Proximity Matching")
    print("-" * 50)
    
    # Test proximity between first two users
    user1, user2 = target_users[0], target_users[1]
    print(f"\nTesting proximity between: {user1} and {user2}")
    
    profile1 = await api_integration.search_instagram_profile(user1)
    profile2 = await api_integration.search_instagram_profile(user2)
    
    if profile1 and profile2:
        proximity = api_integration.calculate_proximity(profile1, profile2)
        print(f"  Proximity score: {proximity.proximity_score:.2f}")
        print(f"  Match type: {proximity.match_type}")
        print(f"  Common interests: {', '.join(proximity.common_interests) if proximity.common_interests else 'None'}")
        print(f"  Confidence: {proximity.confidence:.2f}")
        
        test_suite.record_user_interaction("proximity_match", {
            "user1": user1,
            "user2": user2,
            "score": proximity.proximity_score,
            "match_type": proximity.match_type
        })
    
    print("\n4. Hidden Profile Management")
    print("-" * 50)
    
    # Show all hidden profiles
    hidden_profiles = api_integration.get_all_hidden_profiles()
    print(f"\nHidden profiles stored: {len(hidden_profiles)}")
    
    for profile in hidden_profiles:
        print(f"  - {profile.username} ({profile.platform.value})")
        print(f"    Status: {profile.status.value}")
    
    # Export hidden profiles
    profiles_json = api_integration.export_hidden_profiles()
    print(f"\nExported {len(profiles_json)} characters of profile data")
    
    print("\n5. Test Session Summary")
    print("-" * 50)
    
    summary = test_suite.get_session_summary()
    print(f"\nSession: {summary['session_id']}")
    print(f"Status: {summary['status']}")
    print(f"Total tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Success rate: {summary['success_rate']:.2%}")
    print(f"User interactions: {summary['user_interactions']}")
    print(f"Complex processes: {summary['complex_processes']}")
    
    print("\n6. Interactive Testing Mode")
    print("-" * 50)
    print("\nThe test suite includes an interactive mode where:")
    print("- YOU test the interactions (profile matching, message sending)")
    print("- I handle the complex processes (API integration, data analysis)")
    print("- We work side-by-side to verify functionality")
    print("\nTo start interactive mode, use:")
    print("  await test_suite.interactive_test_mode()")
    
    print("\n7. Example: Sending a Test Message")
    print("-" * 50)
    
    if instagram_api_key:
        print("\n⚠️  Message sending requires valid API credentials")
        print("Example code (uncomment to use with real API):")
        print("""
        # Send test message
        test = await test_suite.run_message_send_test(
            username="katiewynnz",
            content="Hello! This is a test message.",
            platform=Platform.INSTAGRAM
        )
        print(f"Message send result: {test.status.value}")
        """)
    else:
        print("\n⚠️  Skipping message send test (no API key)")
        print("To test message sending, set INSTAGRAM_API_KEY environment variable")
    
    # Cleanup
    await api_integration.cleanup()
    
    print("\n=== Real API Testing Complete ===")
    print("\nSummary:")
    print(f"✓ Profile matching tested for {len(target_users)} users")
    print(f"✓ Conversation history retrieval tested")
    print(f"✓ Proximity matching implemented")
    print(f"✓ Hidden profile management active")
    print(f"✓ Interactive test mode available")
    print(f"✓ Side-by-side testing framework ready")
    
    print("\nNext steps:")
    print("1. Set API keys for real testing: export INSTAGRAM_API_KEY='your_key'")
    print("2. Run interactive mode: await test_suite.interactive_test_mode()")
    print("3. Test actual message sending with valid credentials")
    print("4. Review proximity matches for new discoveries")


if __name__ == "__main__":
    asyncio.run(main())
