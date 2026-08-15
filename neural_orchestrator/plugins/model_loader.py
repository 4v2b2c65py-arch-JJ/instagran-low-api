"""
Make File Model DLL Plugin System
Manages plugins and loaders for app service foreground activity.
Supports dynamic loading of model files and DLL plugins.
"""

import os
import sys
import importlib.util
import hashlib
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
from enum import Enum
import asyncio


class PluginStatus(Enum):
    """Status of plugin loading and execution."""
    LOADED = "loaded"
    UNLOADED = "unloaded"
    ERROR = "error"
    ACTIVE = "active"
    INACTIVE = "inactive"


class PluginType(Enum):
    """Types of plugins supported."""
    MODEL_DLL = "model_dll"
    FOREGROUND_MONITOR = "foreground_monitor"
    MESSAGE_ROUTER = "message_router"
    AGENT_STEERING = "agent_steering"
    VERIFICATION = "verification"


@dataclass
class PluginMetadata:
    """Metadata for a plugin."""
    plugin_id: str
    name: str
    version: str
    plugin_type: PluginType
    author: str
    description: str
    file_path: str
    checksum: str
    dependencies: List[str]
    status: PluginStatus
    loaded_at: Optional[str] = None
    last_active: Optional[str] = None


@dataclass
class ForegroundActivity:
    """Represents foreground app activity."""
    app_name: str
    package_name: str
    activity_type: str
    timestamp: str
    user_id: str
    device_id: str
    duration_ms: int
    metadata: Optional[Dict[str, Any]] = None


class ModelDLLLoader:
    """
    Loads and manages model DLL plugins for foreground activity monitoring.
    Supports dynamic loading and unloading of plugins.
    """

    def __init__(self, plugin_directory: str = "plugins"):
        self.plugin_directory = Path(plugin_directory)
        self.plugin_directory.mkdir(exist_ok=True)
        
        self.loaded_plugins: Dict[str, Any] = {}
        self.plugin_metadata: Dict[str, PluginMetadata] = {}
        self.plugin_hooks: Dict[str, List[Callable]] = {}
        self.foreground_activities: List[ForegroundActivity] = []
        self.activity_index: Dict[str, int] = {}  # user_id -> activity index

    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _generate_plugin_id(self, file_path: str) -> str:
        """Generate unique plugin ID from file path."""
        file_name = Path(file_path).stem
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"{file_name}_{timestamp}"

    def load_plugin_from_file(
        self,
        file_path: str,
        plugin_type: PluginType = PluginType.MODEL_DLL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Load a plugin from a Python file.
        
        Args:
            file_path: Path to the plugin file
            plugin_type: Type of plugin
            metadata: Optional metadata dictionary
            
        Returns:
            Plugin ID if successful, None otherwise
        """
        if not os.path.exists(file_path):
            print(f"Plugin file not found: {file_path}")
            return None
        
        try:
            plugin_id = self._generate_plugin_id(file_path)
            checksum = self._calculate_checksum(file_path)
            
            # Load the module
            spec = importlib.util.spec_from_file_location(plugin_id, file_path)
            if spec is None or spec.loader is None:
                print(f"Failed to load spec for {file_path}")
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Store the loaded module
            self.loaded_plugins[plugin_id] = module
            
            # Create metadata
            plugin_metadata = PluginMetadata(
                plugin_id=plugin_id,
                name=metadata.get("name", Path(file_path).stem) if metadata else Path(file_path).stem,
                version=metadata.get("version", "1.0.0") if metadata else "1.0.0",
                plugin_type=plugin_type,
                author=metadata.get("author", "unknown") if metadata else "unknown",
                description=metadata.get("description", "") if metadata else "",
                file_path=file_path,
                checksum=checksum,
                dependencies=metadata.get("dependencies", []) if metadata else [],
                status=PluginStatus.LOADED,
                loaded_at=datetime.utcnow().isoformat()
            )
            
            self.plugin_metadata[plugin_id] = plugin_metadata
            
            # Initialize plugin if it has an init function
            if hasattr(module, 'init_plugin'):
                module.init_plugin()
            
            print(f"Successfully loaded plugin: {plugin_id}")
            return plugin_id
            
        except Exception as e:
            print(f"Error loading plugin from {file_path}: {e}")
            return None

    def unload_plugin(self, plugin_id: str) -> bool:
        """
        Unload a plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            True if successful
        """
        if plugin_id not in self.loaded_plugins:
            print(f"Plugin not found: {plugin_id}")
            return False
        
        try:
            module = self.loaded_plugins[plugin_id]
            
            # Cleanup if plugin has cleanup function
            if hasattr(module, 'cleanup_plugin'):
                module.cleanup_plugin()
            
            # Remove from loaded plugins
            del self.loaded_plugins[plugin_id]
            
            # Update metadata
            if plugin_id in self.plugin_metadata:
                self.plugin_metadata[plugin_id].status = PluginStatus.UNLOADED
            
            # Remove hooks
            if plugin_id in self.plugin_hooks:
                del self.plugin_hooks[plugin_id]
            
            print(f"Successfully unloaded plugin: {plugin_id}")
            return True
            
        except Exception as e:
            print(f"Error unloading plugin {plugin_id}: {e}")
            return False

    def register_hook(self, plugin_id: str, hook_name: str, callback: Callable) -> bool:
        """
        Register a hook for a plugin.
        
        Args:
            plugin_id: Plugin identifier
            hook_name: Name of the hook
            callback: Callback function
            
        Returns:
            True if successful
        """
        if plugin_id not in self.plugin_hooks:
            self.plugin_hooks[plugin_id] = []
        
        self.plugin_hooks[plugin_id].append({
            "hook_name": hook_name,
            "callback": callback
        })
        
        return True

    def execute_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """
        Execute all callbacks registered for a hook.
        
        Args:
            hook_name: Name of the hook
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            List of results from callbacks
        """
        results = []
        
        for plugin_id, hooks in self.plugin_hooks.items():
            for hook in hooks:
                if hook["hook_name"] == hook_name:
                    try:
                        result = hook["callback"](*args, **kwargs)
                        results.append({
                            "plugin_id": plugin_id,
                            "result": result
                        })
                    except Exception as e:
                        print(f"Error executing hook {hook_name} for plugin {plugin_id}: {e}")
                        results.append({
                            "plugin_id": plugin_id,
                            "error": str(e)
                        })
        
        return results

    def record_foreground_activity(
        self,
        app_name: str,
        package_name: str,
        activity_type: str,
        user_id: str,
        device_id: str,
        duration_ms: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ForegroundActivity:
        """
        Record foreground app activity.
        
        Args:
            app_name: Name of the application
            package_name: Package name
            activity_type: Type of activity
            user_id: User identifier
            device_id: Device identifier
            duration_ms: Duration in milliseconds
            metadata: Optional metadata
            
        Returns:
            ForegroundActivity: Recorded activity
        """
        activity = ForegroundActivity(
            app_name=app_name,
            package_name=package_name,
            activity_type=activity_type,
            timestamp=datetime.utcnow().isoformat(),
            user_id=user_id,
            device_id=device_id,
            duration_ms=duration_ms,
            metadata=metadata or {}
        )
        
        self.foreground_activities.append(activity)
        
        # Update activity index
        key = f"{user_id}_{device_id}"
        self.activity_index[key] = len(self.foreground_activities) - 1
        
        # Execute hooks for foreground activity
        self.execute_hook("on_foreground_activity", activity)
        
        return activity

    def get_user_activities(self, user_id: str, device_id: str) -> List[ForegroundActivity]:
        """
        Get all foreground activities for a user/device combination.
        
        Args:
            user_id: User identifier
            device_id: Device identifier
            
        Returns:
            List of foreground activities
        """
        key = f"{user_id}_{device_id}"
        if key not in self.activity_index:
            return []
        
        activities = []
        current_index = self.activity_index[key]
        
        # Get all activities for this user/device
        for i, activity in enumerate(self.foreground_activities):
            if activity.user_id == user_id and activity.device_id == device_id:
                activities.append(activity)
        
        return activities

    def get_active_plugins(self) -> List[PluginMetadata]:
        """Get list of currently active plugins."""
        return [
            metadata for metadata in self.plugin_metadata.values()
            if metadata.status in [PluginStatus.LOADED, PluginStatus.ACTIVE]
        ]

    def get_plugin_info(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific plugin."""
        if plugin_id not in self.plugin_metadata:
            return None
        
        metadata = self.plugin_metadata[plugin_id]
        return asdict(metadata)

    def scan_plugin_directory(self) -> List[str]:
        """
        Scan plugin directory for loadable plugins.
        
        Returns:
            List of discovered plugin file paths
        """
        discovered = []
        
        for file_path in self.plugin_directory.glob("*.py"):
            if file_path.name != "__init__.py":
                discovered.append(str(file_path))
        
        return discovered

    def auto_load_plugins(self) -> int:
        """
        Automatically load all plugins from the plugin directory.
        
        Returns:
            Number of plugins loaded
        """
        discovered = self.scan_plugin_directory()
        loaded_count = 0
        
        for file_path in discovered:
            plugin_id = self.load_plugin_from_file(file_path)
            if plugin_id:
                loaded_count += 1
        
        return loaded_count

    def create_make_file(self, output_path: str = "Makefile.plugins") -> bool:
        """
        Create a Makefile for building and managing plugins.
        
        Args:
            output_path: Path for the Makefile
            
        Returns:
            True if successful
        """
        makefile_content = f"""# Makefile for instagran-low-api plugins
# Auto-generated by ModelDLLLoader

PLUGIN_DIR := {self.plugin_directory}
PYTHON := python3

.PHONY: all load unload clean scan help

all: scan

scan:
\t@echo "Scanning for plugins in $(PLUGIN_DIR)"
\t@$(PYTHON) -c "from neural_orchestrator.plugins.model_loader import ModelDLLLoader; loader = ModelDLLLoader(); print('\\n'.join(loader.scan_plugin_directory()))"

load:
\t@echo "Loading all plugins from $(PLUGIN_DIR)"
\t@$(PYTHON) -c "from neural_orchestrator.plugins.model_loader import ModelDLLLoader; loader = ModelDLLLoader(); count = loader.auto_load_plugins(); print(f'Loaded {{count}} plugins')"

unload:
\t@echo "Unloading all plugins"
\t@$(PYTHON) -c "from neural_orchestrator.plugins.model_loader import ModelDLLLoader; loader = ModelDLLLoader(); [loader.unload_plugin(pid) for pid in list(loader.loaded_plugins.keys())]; print('All plugins unloaded')"

clean:
\t@echo "Cleaning plugin directory"
\t@find $(PLUGIN_DIR) -name '*.pyc' -delete
\t@find $(PLUGIN_DIR) -name '__pycache__' -type d -exec rm -rf {{}} +

help:
\t@echo "Available targets:"
\t@echo "  scan   - Scan for available plugins"
\t@echo "  load   - Load all plugins"
\t@echo "  unload - Unload all plugins"
\t@echo "  clean  - Clean compiled files"
\t@echo "  help   - Show this help message"
"""
        
        try:
            with open(output_path, 'w') as f:
                f.write(makefile_content)
            print(f"Created Makefile at {output_path}")
            return True
        except Exception as e:
            print(f"Error creating Makefile: {e}")
            return False

    def export_plugin_state(self) -> str:
        """Export current plugin state for recovery."""
        state = {
            "loaded_plugins": list(self.loaded_plugins.keys()),
            "plugin_metadata": {
                pid: asdict(metadata) for pid, metadata in self.plugin_metadata.items()
            },
            "foreground_activities": [asdict(activity) for activity in self.foreground_activities],
            "activity_index": self.activity_index,
            "export_timestamp": datetime.utcnow().isoformat()
        }
        return json.dumps(state, indent=2)

    def import_plugin_state(self, state_json: str) -> bool:
        """
        Import plugin state for recovery.
        
        Args:
            state_json: JSON string of exported state
            
        Returns:
            True if import successful
        """
        try:
            state = json.loads(state_json)
            
            # Restore metadata
            for pid, metadata_dict in state.get("plugin_metadata", {}).items():
                metadata_dict["plugin_type"] = PluginType(metadata_dict["plugin_type"])
                metadata_dict["status"] = PluginStatus(metadata_dict["status"])
                self.plugin_metadata[pid] = PluginMetadata(**metadata_dict)
            
            # Restore activities
            for activity_dict in state.get("foreground_activities", []):
                activity = ForegroundActivity(**activity_dict)
                self.foreground_activities.append(activity)
            
            # Restore index
            self.activity_index = state.get("activity_index", {})
            
            return True
        except Exception as e:
            print(f"Error importing plugin state: {e}")
            return False
