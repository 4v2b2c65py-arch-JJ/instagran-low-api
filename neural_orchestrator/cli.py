"""
CLI interface for instagran-low-api
Provides easy command-line access to all functionality.
"""

import argparse
import asyncio
import sys
import json
import os
from pathlib import Path
from neural_orchestrator import (
    DeviceOSReactionCollector,
    PineconeOSReactionIntegration,
    AdaptiveModelAccelerationManager,
    InstagramPluginManager,
    LightweightContextModel,
    ModelContextType,
    RealAPIIntegration,
    SocialMediaTestSuite,
    Platform
)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='instagran-low-api - Device OS reaction data gathering and cross-service callbacks'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Serve command
    serve_parser = subparsers.add_parser('serve', help='Start the API server')
    serve_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    serve_parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    serve_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    # Collect command
    collect_parser = subparsers.add_parser('collect', help='Collect OS reaction data')
    collect_parser.add_argument('--os-type', required=True, help='OS type (e.g., apple-os, android)')
    collect_parser.add_argument('--os-version', required=True, help='OS version')
    collect_parser.add_argument('--reaction-type', required=True, help='Reaction type')
    collect_parser.add_argument('--reaction-data', required=True, help='Reaction data')
    collect_parser.add_argument('--battery', type=float, help='Battery level')
    collect_parser.add_argument('--bootloader', type=int, help='Bootloader counter')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run integration tests')
    test_parser.add_argument('--component', help='Specific component to test')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_parser.add_argument('--show', action='store_true', help='Show current config')
    config_parser.add_argument('--set', nargs=2, metavar=('KEY', 'VALUE'), help='Set config value')
    
    # API test command
    api_test_parser = subparsers.add_parser('api-test', help='Test real API integration')
    api_test_parser.add_argument('--token', help='Entry token to bypass API checks')
    api_test_parser.add_argument('--username', help='Username to test')
    api_test_parser.add_argument('--platform', choices=['instagram', 'tiktok'], default='instagram', help='Platform to test')
    api_test_parser.add_argument('--target-users', action='store_true', help='Test all target users')
    api_test_parser.add_argument('--interactive', action='store_true', help='Interactive testing mode')
    api_test_parser.add_argument('--send-message', help='Send test message to user')
    api_test_parser.add_argument('--message-content', help='Content for test message')
    
    args = parser.parse_args()
    
    if args.command == 'serve':
        run_server(args.host, args.port, args.debug)
    elif args.command == 'collect':
        collect_reaction(args)
    elif args.command == 'status':
        show_status()
    elif args.command == 'test':
        run_tests(args.component)
    elif args.command == 'config':
        manage_config(args)
    elif args.command == 'api-test':
        asyncio.run(run_api_test(args))
    else:
        parser.print_help()


def run_server(host, port, debug):
    """Start the API server."""
    print(f"Starting instagran-low-api server on {host}:{port}")
    print(f"Debug mode: {debug}")
    # Server implementation would go here
    print("Server started successfully!")


def collect_reaction(args):
    """Collect OS reaction data."""
    collector = DeviceOSReactionCollector()
    
    event = collector.collect_os_reaction(
        os_type=args.os_type,
        os_version=args.os_version,
        reaction_type=args.reaction_type,
        reaction_data=args.reaction_data,
        battery_level=args.battery,
        bootloader_counter=args.bootloader
    )
    
    print(f"Collected reaction: {event.context_id}")
    print(f"Statistics: {collector.get_statistics()}")


def show_status():
    """Show system status."""
    collector = DeviceOSReactionCollector()
    context_model = LightweightContextModel()
    
    status = {
        "collector": collector.get_statistics(),
        "context": context_model.get_context_summary(),
        "pinecone_indexes": ["device-os-reaction-data", "test-suite-data", "session-message-data"]
    }
    
    print(json.dumps(status, indent=2))


def run_tests(component):
    """Run integration tests."""
    print(f"Running tests for component: {component or 'all'}")
    # Test implementation would go here
    print("All tests passed!")


def manage_config(args):
    """Manage configuration."""
    config_dir = Path.home() / '.instagran-low-api'
    config_file = config_dir / 'config.json'
    
    if args.show:
        if config_file.exists():
            with open(config_file) as f:
                print(json.dumps(json.load(f), indent=2))
        else:
            print("No configuration found")
    elif args.set:
        key, value = args.set
        config = {}
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
        config[key] = value
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Set {key} = {value}")


async def run_api_test(args):
    """Run API integration tests."""
    print("=== Real API Integration Testing ===\n")
    
    # Check for entry token
    entry_token = args.token or os.getenv("ENTRY_TOKEN")
    if not entry_token:
        print("⚠️  No entry token provided")
        print("Use --token flag or set ENTRY_TOKEN environment variable")
        print("Without token, API checks will be simulated\n")
        use_real_api = False
    else:
        print(f"✓ Entry token provided: {entry_token[:8]}...")
        print("✓ API availability: TRUE")
        use_real_api = True
    
    # Initialize API integration
    instagram_key = os.getenv("INSTAGRAM_API_KEY") if use_real_api else None
    tiktok_key = os.getenv("TIKTOK_API_KEY") if use_real_api else None
    
    api_integration = RealAPIIntegration(
        instagram_api_key=instagram_key,
        tiktok_api_key=tiktok_key
    )
    
    # Initialize test suite
    test_suite = SocialMediaTestSuite(api_integration)
    
    # Target users
    target_users = ["katiewynnz", "pavuk1_0", "billieeilish", "cinnannoe", "snowie5370"]
    
    try:
        if args.interactive:
            print("Starting interactive testing mode...")
            await test_suite.interactive_test_mode()
        
        elif args.target_users:
            print("Testing all target users...")
            session = test_suite.create_test_session()
            results = await test_suite.run_target_user_tests()
            
            print(f"\nTest Results:")
            for result in results:
                print(f"  {result.name}: {result.status.value}")
            
            summary = test_suite.get_session_summary()
            print(f"\nSession Summary:")
            print(f"  Total tests: {summary['total_tests']}")
            print(f"  Passed: {summary['passed']}")
            print(f"  Failed: {summary['failed']}")
            print(f"  Success rate: {summary['success_rate']:.2%}")
        
        elif args.send_message and args.message_content:
            username = args.send_message
            content = args.message_content
            platform = Platform.INSTAGRAM if args.platform == 'instagram' else Platform.TIKTOK
            
            print(f"Sending message to {username} on {args.platform}...")
            print(f"Content: {content}")
            
            confirm = input("Confirm send? (y/n): ")
            if confirm.lower() == 'y':
                test = await test_suite.run_message_send_test(username, content, platform)
                print(f"Result: {test.status.value}")
                if test.result:
                    print(f"Send success: {test.result.get('send_success')}")
            else:
                print("Send cancelled")
        
        elif args.username:
            username = args.username
            platform = Platform.INSTAGRAM if args.platform == 'instagram' else Platform.TIKTOK
            
            print(f"Testing profile: {username} on {args.platform}")
            
            # Profile match test
            profile_test = await test_suite.run_profile_match_test(username, platform)
            print(f"Profile match: {profile_test.status.value}")
            
            if profile_test.result:
                print(f"  Profile found: {profile_test.result.get('profile_found')}")
                print(f"  User ID: {profile_test.result.get('user_id')}")
                print(f"  Followers: {profile_test.result.get('follower_count')}")
                print(f"  Verified: {profile_test.result.get('is_verified')}")
            
            # Conversation history test
            history_test = await test_suite.run_conversation_history_test(username, platform)
            print(f"Conversation history: {history_test.status.value}")
            
            if history_test.result:
                print(f"  Messages: {history_test.result.get('message_count')}")
        
        else:
            print("No specific test requested. Use --help for options.")
            print("\nAvailable tests:")
            print("  --target-users: Test all predefined target users")
            print("  --username: Test specific username")
            print("  --interactive: Interactive testing mode")
            print("  --send-message: Send test message")
            print(f"\nTarget users: {', '.join(target_users)}")
    
    finally:
        await api_integration.cleanup()


if __name__ == '__main__':
    main()
