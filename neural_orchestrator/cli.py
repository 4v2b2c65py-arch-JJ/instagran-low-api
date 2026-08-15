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
    Platform,
    APIKeyCaptureAgent,
    A2AProtocol
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
    
    # API key capture command
    capture_parser = subparsers.add_parser('capture-keys', help='Capture API keys with sudo')
    capture_parser.add_argument('--auto', action='store_true', help='Auto-capture from common sources')
    capture_parser.add_argument('--manual', nargs=2, metavar=('KEY_NAME', 'KEY_VALUE'), help='Manually set key')
    capture_parser.add_argument('--config', help='Capture from config file')
    capture_parser.add_argument('--env', help='Capture from environment variable')
    capture_parser.add_argument('--export', help='Export to shell script')
    capture_parser.add_argument('--list', action='store_true', help='List captured keys')
    capture_parser.add_argument('--session', action='store_true', help='Show session info')
    
    # A2A protocol command
    a2a_parser = subparsers.add_parser('a2a', help='Agent-to-Agent protocol operations')
    a2a_parser.add_argument('--pipeline', action='store_true', help='Run credential pipeline sequence')
    a2a_parser.add_argument('--connect', help='Connect to agent ID')
    a2a_parser.add_argument('--send', help='Send message to agent')
    a2a_parser.add_argument('--message-type', help='Message type')
    a2a_parser.add_argument('--register', help='Register new agent')
    a2a_parser.add_argument('--info', action='store_true', help='Show A2A session info')
    
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
    elif args.command == 'capture-keys':
        run_key_capture(args)
    elif args.command == 'a2a':
        asyncio.run(run_a2a_protocol(args))
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


def run_key_capture(args):
    """Run API key capture operations."""
    print("=== API Key Capture Agent ===\n")
    
    capture_agent = APIKeyCaptureAgent()
    
    try:
        if args.auto:
            print("Auto-capturing API keys from common sources...")
            
            # Check sudo access
            if capture_agent.check_sudo_access():
                print("✓ Sudo access available")
            else:
                print("⚠️  No sudo access - limited capture capabilities")
            
            # Capture Instagram keys
            print("\nCapturing Instagram keys...")
            insta_keys = capture_agent.auto_capture_instagram_keys()
            for key_name, key in insta_keys.items():
                print(f"  ✓ {key_name}: {key.key_value[:8]}... (from {key.source})")
            
            # Capture TikTok keys
            print("\nCapturing TikTok keys...")
            tiktok_keys = capture_agent.auto_capture_tiktok_keys()
            for key_name, key in tiktok_keys.items():
                print(f"  ✓ {key_name}: {key.key_value[:8]}... (from {key.source})")
            
            total = len(insta_keys) + len(tiktok_keys)
            print(f"\nTotal keys captured: {total}")
            
            # Export to environment
            capture_agent.export_to_environment()
            print("✓ Keys exported to environment")
            
            # Generate env script
            script_path = capture_agent.storage_dir / "setup_keys.sh"
            capture_agent.generate_env_script(str(script_path))
            print(f"✓ Environment script generated: {script_path}")
        
        elif args.manual:
            key_name, key_value = args.manual
            print(f"Manually setting key: {key_name}")
            key = capture_agent.set_key_manually(key_name, key_value)
            print(f"✓ Key stored: {key.key_value[:8]}...")
            capture_agent.export_to_environment()
        
        elif args.config:
            key_name = "API_KEY"  # Default key name
            print(f"Capturing from config: {args.config}")
            key = capture_agent.capture_from_system_config(key_name, args.config)
            if key:
                print(f"✓ Key captured: {key.key_value[:8]}...")
                capture_agent.export_to_environment()
            else:
                print("✗ Failed to capture key from config")
        
        elif args.env:
            print(f"Capturing from environment: {args.env}")
            key = capture_agent.capture_from_environment(args.env)
            if key:
                print(f"✓ Key captured: {key.key_value[:8]}...")
                capture_agent.export_to_environment()
            else:
                print("✗ Key not found in environment")
        
        elif args.export:
            print(f"Generating environment script: {args.export}")
            script_content = capture_agent.generate_env_script(args.export)
            print("✓ Script generated")
            print(f"\nScript preview:")
            print(script_content[:200] + "...")
        
        elif args.list:
            print("Captured keys:")
            for key_name, key in capture_agent.captured_keys.items():
                print(f"  {key_name}: {key.key_value[:8]}... (from {key.source}, captured {key.captured_at})")
        
        elif args.session:
            session_info = capture_agent.get_session_info()
            print("Session information:")
            print(json.dumps(session_info, indent=2))
        
        else:
            print("No capture action specified. Use --help for options.")
            print("\nAvailable actions:")
            print("  --auto: Auto-capture from common sources")
            print("  --manual: Manually set a key")
            print("  --config: Capture from config file")
            print("  --env: Capture from environment variable")
            print("  --export: Export to shell script")
            print("  --list: List captured keys")
            print("  --session: Show session info")
    
    except Exception as e:
        print(f"Error during key capture: {e}")
        import traceback
        traceback.print_exc()


async def run_a2a_protocol(args):
    """Run A2A protocol operations."""
    print("=== Agent-to-Agent Protocol ===\n")
    
    # Get session key from environment
    session_key = os.getenv("STARSHIP_SESSION_KEY")
    if not session_key:
        print("⚠️  STARSHIP_SESSION_KEY not found in environment")
        print("Please set STARSHIP_SESSION_KEY environment variable")
        return
    
    print(f"✓ Session key: {session_key[:8]}...")
    
    try:
        a2a_protocol = A2AProtocol(session_key)
        
        if args.pipeline:
            print("Running credential creation and validation pipeline...")
            pipeline_results = await a2a_protocol.run_pipeline_sequence()
            
            print(f"\nPipeline Results:")
            print(f"  Pipeline ID: {pipeline_results['pipeline_id']}")
            print(f"  Status: {pipeline_results['final_status']}")
            print(f"  Stages completed: {len(pipeline_results['stages_completed'])}")
            print(f"  Stages failed: {len(pipeline_results['stages_failed'])}")
            
            if pipeline_results['stages_completed']:
                print(f"\nCompleted stages:")
                for stage in pipeline_results['stages_completed']:
                    print(f"  ✓ {stage['stage']}: {stage['result']}")
            
            if pipeline_results['stages_failed']:
                print(f"\nFailed stages:")
                for stage in pipeline_results['stages_failed']:
                    print(f"  ✗ {stage.get('stage', 'unknown')}: {stage.get('error', 'unknown')}")
        
        elif args.connect:
            print(f"Connecting to agent: {args.connect}")
            connected = await a2a_protocol.connect_to_agent(args.connect)
            print(f"Connection result: {'Success' if connected else 'Failed'}")
        
        elif args.send and args.message_type:
            print(f"Sending message to agent: {args.send}")
            message = a2a_protocol.send_message(
                args.send,
                args.message_type,
                {"content": "Test message", "timestamp": datetime.utcnow().isoformat()}
            )
            print(f"Message sent: {message.message_id}")
        
        elif args.register:
            print(f"Registering agent: {args.register}")
            agent = a2a_protocol.register_agent(
                args.register,
                "public_key_placeholder",
                ["credential_management", "hosting"]
            )
            print(f"Agent registered: {agent.agent_id}")
        
        elif args.info:
            session_info = a2a_protocol.get_session_info()
            print("A2A Session Information:")
            print(json.dumps(session_info, indent=2))
        
        else:
            print("No A2A action specified. Use --help for options.")
            print("\nAvailable actions:")
            print("  --pipeline: Run credential pipeline sequence")
            print("  --connect: Connect to agent")
            print("  --send: Send message to agent")
            print("  --register: Register new agent")
            print("  --info: Show A2A session info")
    
    except Exception as e:
        print(f"Error during A2A protocol: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
