"""
Device OS Reaction Data Collector
Gathers device OS reaction data and stores in Pinecone for analysis and pattern detection.
Integrates with Pinecone MCP for vector storage and retrieval of OS reaction patterns.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import hashlib


@dataclass
class OSReactionEvent:
    """Represents a device OS reaction event."""
    device_id: str
    os_type: str
    os_version: str
    reaction_type: str
    reaction_data: str
    timestamp: str
    battery_level: Optional[float] = None
    bootloader_counter: Optional[int] = None
    instance_id: Optional[str] = None
    location_context: Optional[str] = None
    user_present: bool = False
    agent_connection: bool = False


class DeviceOSReactionCollector:
    """
    Collects and manages device OS reaction data using Pinecone for vector storage.
    Enables pattern detection across OS reactions and device states.
    """

    def __init__(self, pinecone_index_name: str = "device-os-reaction-data"):
        self.index_name = pinecone_index_name
        self.reaction_buffer: List[OSReactionEvent] = []
        self.session_context: Dict[str, Any] = {}
        self.instance_mapping: Dict[str, str] = {}  # device_id -> instance_id
        self.bootloader_states: Dict[str, int] = {}  # device_id -> counter value

    def generate_device_id(self, device_info: Dict[str, Any]) -> str:
        """Generate consistent device ID from device information."""
        device_string = json.dumps(device_info, sort_keys=True)
        return hashlib.sha256(device_string.encode()).hexdigest()[:16]

    def collect_os_reaction(
        self,
        os_type: str,
        os_version: str,
        reaction_type: str,
        reaction_data: str,
        device_info: Optional[Dict[str, Any]] = None,
        battery_level: Optional[float] = None,
        bootloader_counter: Optional[int] = None,
        user_present: bool = False,
        agent_connection: bool = False
    ) -> OSReactionEvent:
        """
        Collect an OS reaction event from a device.
        
        Args:
            os_type: Type of OS (e.g., "apple-os", "android", "linux")
            os_version: Version of the OS
            reaction_type: Type of reaction (e.g., "boot", "shutdown", "app_launch")
            reaction_data: Detailed reaction data as text
            device_info: Device information for ID generation
            battery_level: Current battery level (0-100)
            bootloader_counter: Current bootloader counter value
            user_present: Whether user is present
            agent_connection: Whether agent connection is active
            
        Returns:
            OSReactionEvent: The collected reaction event
        """
        if device_info is None:
            device_info = {"type": "unknown"}
        
        device_id = self.generate_device_id(device_info)
        instance_id = self.instance_mapping.get(device_id, "primary")
        
        event = OSReactionEvent(
            device_id=device_id,
            os_type=os_type,
            os_version=os_version,
            reaction_type=reaction_type,
            reaction_data=reaction_data,
            timestamp=datetime.utcnow().isoformat(),
            battery_level=battery_level,
            bootloader_counter=bootloader_counter,
            instance_id=instance_id,
            user_present=user_present,
            agent_connection=agent_connection
        )
        
        self.reaction_buffer.append(event)
        
        # Track bootloader state for flip detection
        if bootloader_counter is not None:
            self._track_bootloader_state(device_id, bootloader_counter)
        
        return event

    def _track_bootloader_state(self, device_id: str, counter: int) -> bool:
        """
        Track bootloader counter state and detect flips.
        
        Args:
            device_id: Device identifier
            counter: Current bootloader counter value
            
        Returns:
            bool: True if a flip was detected
        """
        previous_counter = self.bootloader_states.get(device_id)
        self.bootloader_states[device_id] = counter
        
        if previous_counter is not None and previous_counter != counter:
            # Bootloader counter flip detected
            self._handle_bootloader_flip(device_id, previous_counter, counter)
            return True
        return False

    def _handle_bootloader_flip(self, device_id: str, old_counter: int, new_counter: int):
        """Handle bootloader counter flip between instances."""
        # Switch instance mapping
        current_instance = self.instance_mapping.get(device_id, "primary")
        new_instance = "secondary" if current_instance == "primary" else "primary"
        self.instance_mapping[device_id] = new_instance
        
        # Log the flip event
        flip_event = {
            "device_id": device_id,
            "old_counter": old_counter,
            "new_counter": new_counter,
            "old_instance": current_instance,
            "new_instance": new_instance,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Store in session context
        if "bootloader_flips" not in self.session_context:
            self.session_context["bootloader_flips"] = []
        self.session_context["bootloader_flips"].append(flip_event)

    def calculate_battery_delta(
        self,
        device_id: str,
        current_battery: float,
        other_instance_battery: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate battery state difference between dual instances.
        
        Args:
            device_id: Device identifier
            current_battery: Current battery level (0-100)
            other_instance_battery: Battery level from other instance
            
        Returns:
            Dict containing battery delta information
        """
        result = {
            "device_id": device_id,
            "current_battery": current_battery,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if other_instance_battery is not None:
            delta = abs(current_battery - other_instance_battery)
            result["other_instance_battery"] = other_instance_battery
            result["battery_delta"] = delta
            result["sync_status"] = "synced" if delta < 5.0 else "diverged"
            result["estimated_charge_rate"] = self._estimate_charge_rate(device_id, delta)
        
        return result

    def _estimate_charge_rate(self, device_id: str, delta: float) -> Optional[float]:
        """Estimate charge rate based on battery delta history."""
        # Simple estimation - in production, use historical data
        if delta > 10:
            return -delta / 60.0  # Discharge rate per minute
        elif delta < -10:
            return abs(delta) / 60.0  # Charge rate per minute
        return None

    def get_buffered_reactions(self) -> List[OSReactionEvent]:
        """Get all buffered reaction events."""
        return self.reaction_buffer.copy()

    def clear_buffer(self) -> int:
        """Clear the reaction buffer and return count of cleared events."""
        count = len(self.reaction_buffer)
        self.reaction_buffer.clear()
        return count

    def get_session_context(self) -> Dict[str, Any]:
        """Get current session context including bootloader flips."""
        return self.session_context.copy()

    def get_instance_mapping(self) -> Dict[str, str]:
        """Get current device to instance mapping."""
        return self.instance_mapping.copy()

    def prepare_for_pinecone(self) -> List[Dict[str, Any]]:
        """
        Prepare buffered reactions for Pinecone upsert.
        
        Returns:
            List of records compatible with Pinecone upsert
        """
        records = []
        for event in self.reaction_buffer:
            record = {
                "id": f"{event.device_id}_{int(time.time())}_{hash(event.reaction_data) % 10000}",
                "reaction_data": event.reaction_data,
                "device_id": event.device_id,
                "os_type": event.os_type,
                "os_version": event.os_version,
                "reaction_type": event.reaction_type,
                "timestamp": event.timestamp,
                "battery_level": event.battery_level,
                "bootloader_counter": event.bootloader_counter,
                "instance_id": event.instance_id,
                "user_present": event.user_present,
                "agent_connection": event.agent_connection
            }
            records.append(record)
        return records

    async def process_incoming_message(
        self,
        message_content: str,
        device_id: str,
        model_processed: bool = False
    ) -> Dict[str, Any]:
        """
        Process incoming message and merge with session data.
        
        Args:
            message_content: Content of the incoming message
            device_id: Device identifier
            model_processed: Whether the message was processed by a model
            
        Returns:
            Dict containing merged session data
        """
        session_data = {
            "message_id": hashlib.sha256(message_content.encode()).hexdigest()[:16],
            "device_id": device_id,
            "content": message_content,
            "timestamp": datetime.utcnow().isoformat(),
            "model_processed": model_processed,
            "instance_id": self.instance_mapping.get(device_id, "primary")
        }
        
        # Merge with existing session context
        if "messages" not in self.session_context:
            self.session_context["messages"] = []
        self.session_context["messages"].append(session_data)
        
        return session_data

    def distinguish_url_source(self, url: str) -> Dict[str, Any]:
        """
        Distinguish URL sources, particularly for status.garudalinux.org integration.
        
        Args:
            url: URL to analyze
            
        Returns:
            Dict containing URL classification and metadata
        """
        result = {
            "original_url": url,
            "is_garuda_status": "status.garudalinux.org" in url,
            "url_type": "unknown",
            "domain": self._extract_domain(url),
            "classification": self._classify_url(url)
        }
        
        if result["is_garuda_status"]:
            result["url_type"] = "status_page"
            result["os_layer_access"] = True
            result["bootloader_monitoring"] = True
        
        return result

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return url

    def _classify_url(self, url: str) -> str:
        """Classify URL by type."""
        if "status" in url.lower():
            return "status_monitoring"
        elif "api" in url.lower():
            return "api_endpoint"
        elif "github" in url.lower():
            return "repository"
        return "general"

    def get_statistics(self) -> Dict[str, Any]:
        """Get collector statistics."""
        return {
            "buffered_events": len(self.reaction_buffer),
            "tracked_devices": len(self.instance_mapping),
            "bootloader_flips": len(self.session_context.get("bootloader_flips", [])),
            "total_messages": len(self.session_context.get("messages", [])),
            "active_instances": len(set(self.instance_mapping.values()))
        }
