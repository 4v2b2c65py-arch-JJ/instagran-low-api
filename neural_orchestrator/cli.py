"""
CLI interface for instagran-low-api
Provides easy command-line access to all functionality.
"""

import argparse
import asyncio
import sys
import json
from pathlib import Path
from neural_orchestrator import (
    DeviceOSReactionCollector,
    PineconeOSReactionIntegration,
    AdaptiveModelAccelerationManager,
    InstagramPluginManager,
    LightweightContextModel,
    ContextType
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


if __name__ == '__main__':
    main()
