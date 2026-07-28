"""
Example usage of the Neural Orchestrator package.
Demonstrates the main features and components.
"""

import asyncio
from neural_orchestrator import NeuralOrchestrator


async def main():
    """Main example usage."""
    
    # Initialize the orchestrator with default parameters
    orchestrator = NeuralOrchestrator(
        base_model_size=8.3e9,  # 8.3 billion
        baseline_percentage=1e-11,  # 0.00000000001 percent
        alpha_hz_range=(8, 12),  # Alpha wave range
        beta_hz_range=(13, 30),  # Beta wave range
        load_capacity_mb=12,  # 12MB load capacity
        update_interval_seconds=1.0  # 1 second update interval
    )
    
    print("Starting Neural Orchestrator...")
    
    # Run for a few cycles
    for i in range(5):
        await orchestrator.update_cycle()
        status = orchestrator.get_status()
        print(f"Cycle {i+1}:")
        print(f"  Current Cycle: {status['current_cycle']}")
        print(f"  Dimensional Resolution: {status['dimensional_resolution']}")
        print(f"  N Value: {status['n_value']:.6f}")
        print(f"  Density Markers: {status['density_markers']}")
        print()
    
    # Load some cookies
    orchestrator.load_cookies({
        'session_id': 'example_session',
        'user_token': 'example_token'
    })
    
    # Monitor traffic flow
    orchestrator.monitor_traffic_flow({
        'source': '192.168.1.1',
        'destination': '192.168.1.2',
        'packet_count': 100
    })
    
    # Get pipeline snapshot
    pipeline = orchestrator.get_pipeline_snapshot()
    print(f"Pipeline buffer size: {len(pipeline)}")
    
    # Recover commands
    commands = orchestrator.recover_commands()
    print(f"Recovered commands: {len(commands)}")
    
    print("\nExample completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
