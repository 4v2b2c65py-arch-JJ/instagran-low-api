"""
Test Suite for Real Conversation History and Response Testing
Allows testing real conversations and sending responses to verify functionality.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from neural_orchestrator.social_media.real_api_integration import (
    RealAPIIntegration,
    Platform,
    UserProfile,
    ConversationMessage,
    ProximityMatch
)


class TestStatus(Enum):
    """Status of test execution."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TestType(Enum):
    """Types of tests."""
    PROFILE_MATCH = "profile_match"
    CONVERSATION_HISTORY = "conversation_history"
    MESSAGE_SEND = "message_send"
    PROXIMITY_MATCH = "proximity_match"
    INTEGRATION = "integration"


@dataclass
class TestCase:
    """Test case for social media testing."""
    test_id: str
    test_type: TestType
    name: str
    description: str
    platform: Platform
    username: str
    parameters: Dict[str, Any]
    status: TestStatus
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class TestSession:
    """Test session for side-by-side testing."""
    session_id: str
    started_at: str
    test_cases: List[TestCase]
    user_interactions: List[Dict[str, Any]]
    complex_processes: List[Dict[str, Any]]
    status: TestStatus


class SocialMediaTestSuite:
    """
    Test suite for real social media API integration.
    Allows testing conversation history and sending responses.
    """

    def __init__(self, api_integration: RealAPIIntegration):
        self.api_integration = api_integration
        self.test_sessions: Dict[str, TestSession] = []
        self.current_session: Optional[TestSession] = None
        self.target_users = [
            "katiewynnz",
            "pavuk1_0", 
            "billieeilish",
            "cinnannoe",
            "snowie5370"
        ]

    def create_test_session(self) -> TestSession:
        """Create a new test session."""
        session_id = f"session_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        session = TestSession(
            session_id=session_id,
            started_at=datetime.utcnow().isoformat(),
            test_cases=[],
            user_interactions=[],
            complex_processes=[],
            status=TestStatus.PENDING
        )
        
        self.current_session = session
        self.test_sessions.append(session)
        
        return session

    async def run_profile_match_test(self, username: str, platform: Platform = Platform.INSTAGRAM) -> TestCase:
        """
        Test profile matching for a specific user.
        
        Args:
            username: Username to test
            platform: Platform to test on
            
        Returns:
            TestCase with results
        """
        test_id = f"test_profile_{username}_{platform.value}"
        
        test_case = TestCase(
            test_id=test_id,
            test_type=TestType.PROFILE_MATCH,
            name=f"Profile Match Test - {username}",
            description=f"Test profile matching for {username} on {platform.value}",
            platform=platform,
            username=username,
            parameters={"platform": platform.value},
            status=TestStatus.RUNNING,
            started_at=datetime.utcnow().isoformat()
        )
        
        try:
            if platform == Platform.INSTAGRAM:
                profile = await self.api_integration.search_instagram_profile(username)
            else:
                profile = await self.api_integration.search_tiktok_profile(username)
            
            test_case.result = {
                "profile_found": profile is not None and profile.status.value == "found",
                "username": profile.username if profile else username,
                "user_id": profile.user_id if profile else "",
                "follower_count": profile.follower_count if profile else 0,
                "is_verified": profile.is_verified if profile else False,
                "is_private": profile.is_private if profile else False
            }
            
            test_case.status = TestStatus.PASSED if test_case.result["profile_found"] else TestStatus.FAILED
            
        except Exception as e:
            test_case.status = TestStatus.FAILED
            test_case.error_message = str(e)
        
        test_case.completed_at = datetime.utcnow().isoformat()
        
        if self.current_session:
            self.current_session.test_cases.append(test_case)
        
        return test_case

    async def run_conversation_history_test(self, username: str, platform: Platform = Platform.INSTAGRAM) -> TestCase:
        """
        Test conversation history retrieval.
        
        Args:
            username: Username to test
            platform: Platform to test on
            
        Returns:
            TestCase with results
        """
        test_id = f"test_conversation_{username}_{platform.value}"
        
        test_case = TestCase(
            test_id=test_id,
            test_type=TestType.CONVERSATION_HISTORY,
            name=f"Conversation History Test - {username}",
            description=f"Test conversation history retrieval for {username}",
            platform=platform,
            username=username,
            parameters={"platform": platform.value},
            status=TestStatus.RUNNING,
            started_at=datetime.utcnow().isoformat()
        )
        
        try:
            messages = await self.api_integration.get_conversation_history(platform, username)
            
            test_case.result = {
                "message_count": len(messages),
                "has_messages": len(messages) > 0,
                "sample_messages": [asdict(m) for m in messages[:3]] if messages else []
            }
            
            test_case.status = TestStatus.PASSED
            
        except Exception as e:
            test_case.status = TestStatus.FAILED
            test_case.error_message = str(e)
        
        test_case.completed_at = datetime.utcnow().isoformat()
        
        if self.current_session:
            self.current_session.test_cases.append(test_case)
        
        return test_case

    async def run_message_send_test(
        self,
        username: str,
        content: str,
        platform: Platform = Platform.INSTAGRAM,
        message_type: str = "text"
    ) -> TestCase:
        """
        Test message sending functionality.
        
        Args:
            username: Recipient username
            content: Message content
            platform: Platform to send on
            message_type: Type of message
            
        Returns:
            TestCase with results
        """
        test_id = f"test_send_{username}_{platform.value}"
        
        test_case = TestCase(
            test_id=test_id,
            test_type=TestType.MESSAGE_SEND,
            name=f"Message Send Test - {username}",
            description=f"Test sending message to {username}",
            platform=platform,
            username=username,
            parameters={
                "platform": platform.value,
                "content": content,
                "message_type": message_type
            },
            status=TestStatus.RUNNING,
            started_at=datetime.utcnow().isoformat()
        )
        
        try:
            success = await self.api_integration.send_message(platform, username, content, message_type)
            
            test_case.result = {
                "send_success": success,
                "recipient": username,
                "content_preview": content[:50] + "..." if len(content) > 50 else content
            }
            
            test_case.status = TestStatus.PASSED if success else TestStatus.FAILED
            
        except Exception as e:
            test_case.status = TestStatus.FAILED
            test_case.error_message = str(e)
        
        test_case.completed_at = datetime.utcnow().isoformat()
        
        if self.current_session:
            self.current_session.test_cases.append(test_case)
        
        return test_case

    async def run_proximity_match_test(self, username1: str, username2: str) -> TestCase:
        """
        Test proximity matching between two users.
        
        Args:
            username1: First username
            username2: Second username
            
        Returns:
            TestCase with results
        """
        test_id = f"test_proximity_{username1}_{username2}"
        
        test_case = TestCase(
            test_id=test_id,
            test_type=TestType.PROXIMITY_MATCH,
            name=f"Proximity Match Test - {username1} vs {username2}",
            description=f"Test proximity matching between {username1} and {username2}",
            platform=Platform.INSTAGRAM,
            username=username1,
            parameters={"username1": username1, "username2": username2},
            status=TestStatus.RUNNING,
            started_at=datetime.utcnow().isoformat()
        )
        
        try:
            # Get profiles
            profile1 = await self.api_integration.search_instagram_profile(username1)
            profile2 = await self.api_integration.search_instagram_profile(username2)
            
            if profile1 and profile2:
                proximity = self.api_integration.calculate_proximity(profile1, profile2)
                
                test_case.result = {
                    "proximity_score": proximity.proximity_score,
                    "match_type": proximity.match_type,
                    "common_interests": proximity.common_interests,
                    "confidence": proximity.confidence
                }
                
                test_case.status = TestStatus.PASSED
            else:
                test_case.status = TestStatus.FAILED
                test_case.error_message = "Could not retrieve both profiles"
                
        except Exception as e:
            test_case.status = TestStatus.FAILED
            test_case.error_message = str(e)
        
        test_case.completed_at = datetime.utcnow().isoformat()
        
        if self.current_session:
            self.current_session.test_cases.append(test_case)
        
        return test_case

    async def run_target_user_tests(self) -> List[TestCase]:
        """
        Run tests for all target users.
        
        Returns:
            List of test results
        """
        if not self.current_session:
            self.create_test_session()
        
        results = []
        
        for username in self.target_users:
            # Test profile matching
            profile_test = await self.run_profile_match_test(username)
            results.append(profile_test)
            
            # Test conversation history
            history_test = await self.run_conversation_history_test(username)
            results.append(history_test)
            
            # Small delay between tests
            await asyncio.sleep(1)
        
        # Test proximity between some users
        if len(self.target_users) >= 2:
            proximity_test = await self.run_proximity_match_test(
                self.target_users[0],
                self.target_users[1]
            )
            results.append(proximity_test)
        
        self.current_session.status = TestStatus.PASSED
        
        return results

    def record_user_interaction(self, interaction_type: str, data: Dict[str, Any]) -> None:
        """
        Record a user interaction for side-by-side testing.
        
        Args:
            interaction_type: Type of interaction
            data: Interaction data
        """
        if self.current_session:
            self.current_session.user_interactions.append({
                "type": interaction_type,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            })

    def record_complex_process(self, process_name: str, data: Dict[str, Any]) -> None:
        """
        Record a complex process for side-by-side testing.
        
        Args:
            process_name: Name of the complex process
            data: Process data
        """
        if self.current_session:
            self.current_session.complex_processes.append({
                "name": process_name,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            })

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current test session."""
        if not self.current_session:
            return {"error": "No active session"}
        
        passed = len([t for t in self.current_session.test_cases if t.status == TestStatus.PASSED])
        failed = len([t for t in self.current_session.test_cases if t.status == TestStatus.FAILED])
        total = len(self.current_session.test_cases)
        
        return {
            "session_id": self.current_session.session_id,
            "status": self.current_session.status.value,
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "success_rate": passed / total if total > 0 else 0,
            "user_interactions": len(self.current_session.user_interactions),
            "complex_processes": len(self.current_session.complex_processes),
            "started_at": self.current_session.started_at
        }

    def get_test_results(self) -> List[Dict[str, Any]]:
        """Get detailed test results."""
        if not self.current_session:
            return []
        
        return [asdict(test) for test in self.current_session.test_cases]

    def export_session(self) -> str:
        """Export current session data."""
        if not self.current_session:
            return "{}"
        
        session_data = {
            "session": asdict(self.current_session),
            "test_cases": [asdict(test) for test in self.current_session.test_cases]
        }
        
        return json.dumps(session_data, indent=2)

    async def interactive_test_mode(self) -> None:
        """
        Interactive test mode for side-by-side testing.
        User tests interactions while system handles complex processes.
        """
        print("=== Interactive Test Mode ===")
        print("You test the interactions, I handle the complex processes")
        print("Target users:", ", ".join(self.target_users))
        print()
        
        if not self.current_session:
            self.create_test_session()
        
        while True:
            print("\nOptions:")
            print("1. Test profile match")
            print("2. Test conversation history")
            print("3. Send test message")
            print("4. Test proximity match")
            print("5. Run all target user tests")
            print("6. View session summary")
            print("7. Export session")
            print("8. Exit")
            
            choice = input("\nYour choice (1-8): ").strip()
            
            if choice == "1":
                username = input("Enter username: ").strip()
                platform = input("Platform (instagram/tiktok): ").strip().lower()
                plat = Platform.INSTAGRAM if platform == "instagram" else Platform.TIKTOK
                
                test = await self.run_profile_match_test(username, plat)
                self.record_user_interaction("profile_match_test", {"username": username, "platform": platform})
                print(f"Test result: {test.status.value}")
                if test.result:
                    print(f"Profile found: {test.result.get('profile_found')}")
                
            elif choice == "2":
                username = input("Enter username: ").strip()
                platform = input("Platform (instagram/tiktok): ").strip().lower()
                plat = Platform.INSTAGRAM if platform == "instagram" else Platform.TIKTOK
                
                test = await self.run_conversation_history_test(username, plat)
                self.record_user_interaction("conversation_history_test", {"username": username})
                print(f"Test result: {test.status.value}")
                if test.result:
                    print(f"Messages found: {test.result.get('message_count')}")
                
            elif choice == "3":
                username = input("Enter recipient username: ").strip()
                content = input("Enter message content: ").strip()
                platform = input("Platform (instagram/tiktok): ").strip().lower()
                plat = Platform.INSTAGRAM if platform == "instagram" else Platform.TIKTOK
                
                confirm = input(f"Send '{content}' to {username}? (y/n): ").strip().lower()
                if confirm == 'y':
                    test = await self.run_message_send_test(username, content, plat)
                    self.record_user_interaction("message_send_test", {"username": username, "content": content})
                    print(f"Test result: {test.status.value}")
                else:
                    print("Message send cancelled")
                
            elif choice == "4":
                username1 = input("Enter first username: ").strip()
                username2 = input("Enter second username: ").strip()
                
                test = await self.run_proximity_match_test(username1, username2)
                self.record_user_interaction("proximity_match_test", {"user1": username1, "user2": username2})
                print(f"Test result: {test.status.value}")
                if test.result:
                    print(f"Proximity score: {test.result.get('proximity_score'):.2f}")
                    print(f"Match type: {test.result.get('match_type')}")
                
            elif choice == "5":
                print("Running tests for all target users...")
                results = await self.run_target_user_tests()
                self.record_user_interaction("batch_test", {"users": self.target_users})
                print(f"Completed {len(results)} tests")
                
            elif choice == "6":
                summary = self.get_session_summary()
                print("\nSession Summary:")
                print(json.dumps(summary, indent=2))
                
            elif choice == "7":
                session_data = self.export_session()
                filename = f"test_session_{self.current_session.session_id}.json"
                with open(filename, 'w') as f:
                    f.write(session_data)
                print(f"Session exported to {filename}")
                
            elif choice == "8":
                print("Exiting interactive test mode")
                break
            
            else:
                print("Invalid choice")
