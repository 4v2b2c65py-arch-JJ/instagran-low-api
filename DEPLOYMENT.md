# Deployment Guide

## Quick Start (Linux Userland)

### Installation

```bash
# Clone the repository
git clone https://github.com/4v2b2c65py-arch-JJ/instagran-low-api.git
cd instagran-low-api

# Run the installation script
./install.sh
```

The installation script automatically:
- Creates a Python virtual environment
- Installs all dependencies
- Sets up configuration directories
- Installs the package in development mode

### Manual Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install package
pip install -e .

# Install with Pinecone support
pip install -e ".[pinecone]"
```

## Usage

### CLI Commands

```bash
# Activate the environment
source venv/bin/activate

# Show system status
instagran-api status

# Collect OS reaction data
instagran-api collect --os-type apple-os --os-version 14.0 --reaction-type boot --reaction-data "Device booted successfully"

# Start the API server
instagran-api serve --host 0.0.0.0 --port 8080

# Run tests
instagran-api test

# Manage configuration
instagran-api config --show
instagran-api config --set api_key your_key
```

### Python API

```python
from neural_orchestrator import (
    DeviceOSReactionCollector,
    CrossServiceCallbackManager,
    PineconeOSReactionIntegration
)

# Initialize components
collector = DeviceOSReactionCollector()
callback_manager = CrossServiceCallbackManager()
pinecone = PineconeOSReactionIntegration()

# Collect OS reaction
event = collector.collect_os_reaction(
    os_type="apple-os",
    os_version="14.0",
    reaction_type="boot",
    reaction_data="Device booted successfully"
)

# Create cross-service callback
parcel = callback_manager.create_parcel(
    source_service="device_monitor",
    target_service="analytics",
    payload={"event": event.reaction_data},
    priority=ParcelPriority.HIGH
)

# Send parcel
response = await callback_manager.send_parcel(parcel.parcel_id)
```

## Cross-Service Callbacks

The package includes a robust cross-service callback system with automatic retry and parcel recovery:

### Features

- **Automatic Retry**: Failed parcels are automatically retried up to 3 times
- **Priority Queue**: Support for LOW, NORMAL, HIGH, and CRITICAL priority levels
- **State Recovery**: Export/import functionality for state recovery
- **Session Management**: Unique session tokens for tracking
- **Local Handlers**: Support for both HTTP callbacks and local function handlers

### Example

```python
# Register service endpoints
callback_manager.register_service_endpoint(
    "analytics", 
    "https://api.example.com/callback"
)

# Register local handler
async def my_handler(payload):
    return {"processed": True}

callback_manager.register_callback_handler("local_service", my_handler)

# Create and send parcel
parcel = callback_manager.create_parcel(
    source_service="device_monitor",
    target_service="analytics",
    payload={"data": "example"}
)
response = await callback_manager.send_parcel(parcel.parcel_id)

# Recovery
await callback_manager.process_recovery_queue()

# State management
state = callback_manager.export_state()
callback_manager.import_state(state)
```

## Pinecone Integration

The package includes pre-configured Pinecone indexes:

- `device-os-reaction-data` - OS reaction patterns
- `test-suite-data` - Test suite data
- `session-message-data` - Session messages

### Configuration

```python
# Initialize Pinecone integration
pinecone = PineconeOSReactionIntegration()

# Upsert data
records = collector.prepare_for_pinecone()
result = await pinecone.upsert_os_reactions(records)

# Search data
results = await pinecone.search_os_reactions(
    query="device boot successful",
    top_k=10
)
```

## Configuration

Configuration is stored in `~/.instagran-low-api/config.json`:

```json
{
  "api_key": "your_api_key",
  "pinecone_api_key": "your_pinecone_key",
  "log_level": "INFO",
  "max_parcels": 1000
}
```

## Deployment Options

### Development Mode

```bash
source venv/bin/activate
instagran-api serve --debug
```

### Production Mode

```bash
# Using gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 neural_orchestrator.cli:app

# Using systemd
sudo cp systemd/instagran-api.service /etc/systemd/system/
sudo systemctl enable instagran-api
sudo systemctl start instagran-api
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -e ".[pinecone]"

CMD ["instagran-api", "serve", "--host", "0.0.0.0", "--port", "8080"]
```

## Troubleshooting

### Virtual Environment Issues

```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### Permission Issues

```bash
# Make install script executable
chmod +x install.sh
```

### Dependency Conflicts

```bash
# Upgrade pip first
pip install --upgrade pip
# Then reinstall
pip install -e . --force-reinstall
```

## Support

For issues and questions:
- GitHub: https://github.com/4v2b2c65py-arch-JJ/instagran-low-api/issues
- Documentation: https://github.com/4v2b2c65py-arch-JJ/instagran-low-api#readme
