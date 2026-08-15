"""
API Key Capture Agent
Automatically captures and manages API keys with sudo privileges.
Saves to environment variables and maintains git-ignored secure storage.
"""

import os
import subprocess
import json
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import hashlib


@dataclass
class APIKey:
    """Represents a captured API key."""
    key_name: str
    key_value: str
    source: str
    captured_at: str
    expires_at: Optional[str] = None
    metadata: Optional[Dict] = None


class APIKeyCaptureAgent:
    """
    Captures and manages API keys with elevated privileges.
    Provides automatic environment variable setup and secure storage.
    """

    def __init__(self, storage_dir: str = "~/.instagran-low-api/secure"):
        self.storage_dir = Path(storage_dir).expanduser()
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.keys_file = self.storage_dir / "api_keys.json"
        self.env_file = self.storage_dir / ".env"
        self.session_file = self.storage_dir / "session.json"
        
        self.captured_keys: Dict[str, APIKey] = {}
        self.session_id = self._generate_session_id()
        
        # Load existing keys
        self._load_keys()

    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        return hashlib.sha256(
            f"{datetime.utcnow().isoformat()}_{os.getpid()}".encode()
        ).hexdigest()[:16]

    def _load_keys(self) -> None:
        """Load existing keys from storage."""
        if self.keys_file.exists():
            try:
                with open(self.keys_file, 'r') as f:
                    keys_data = json.load(f)
                    for key_name, key_data in keys_data.items():
                        self.captured_keys[key_name] = APIKey(**key_data)
            except Exception as e:
                print(f"Error loading keys: {e}")

    def _save_keys(self) -> None:
        """Save keys to storage."""
        try:
            keys_data = {
                key_name: asdict(key) 
                for key_name, key in self.captured_keys.items()
            }
            with open(self.keys_file, 'w') as f:
                json.dump(keys_data, f, indent=2)
        except Exception as e:
            print(f"Error saving keys: {e}")

    def _update_env_file(self) -> None:
        """Update .env file with current keys."""
        try:
            env_lines = []
            for key_name, key in self.captured_keys.items():
                env_lines.append(f"{key_name}={key.key_value}")
            
            with open(self.env_file, 'w') as f:
                f.write('\n'.join(env_lines))
        except Exception as e:
            print(f"Error updating env file: {e}")

    def _save_session(self) -> None:
        """Save current session state."""
        try:
            session_data = {
                "session_id": self.session_id,
                "started_at": datetime.utcnow().isoformat(),
                "captured_keys": list(self.captured_keys.keys()),
                "storage_dir": str(self.storage_dir)
            }
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
        except Exception as e:
            print(f"Error saving session: {e}")

    def check_sudo_access(self) -> bool:
        """Check if sudo access is available."""
        try:
            result = subprocess.run(
                ["sudo", "-n", "true"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def capture_from_system_config(self, key_name: str, config_path: str) -> Optional[APIKey]:
        """
        Capture API key from system configuration file using sudo.
        
        Args:
            key_name: Name for the API key
            config_path: Path to configuration file
            
        Returns:
            APIKey if captured successfully
        """
        if not self.check_sudo_access():
            print("Sudo access required for system config capture")
            return None
        
        try:
            # Read config file with sudo
            result = subprocess.run(
                ["sudo", "cat", config_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                config_content = result.stdout
                
                # Try to extract API key (common patterns)
                key_value = self._extract_key_from_config(config_content, key_name)
                
                if key_value:
                    return self._store_key(key_name, key_value, f"system_config:{config_path}")
            
        except Exception as e:
            print(f"Error capturing from system config: {e}")
        
        return None

    def _extract_key_from_config(self, config_content: str, key_name: str) -> Optional[str]:
        """Extract API key from configuration content."""
        # Common patterns for API keys in config files
        patterns = [
            f"{key_name}=(\\S+)",
            f"{key_name}: (\\S+)",
            f"{key_name} = (\\S+)",
            f'"{key_name}": "(\\S+)"',
            f"'{key_name}': '(\\S+)'",
        ]
        
        import re
        for pattern in patterns:
            match = re.search(pattern, config_content)
            if match:
                return match.group(1)
        
        return None

    def capture_from_environment(self, key_name: str) -> Optional[APIKey]:
        """
        Capture API key from environment variable.
        
        Args:
            key_name: Name of environment variable
            
        Returns:
            APIKey if found
        """
        key_value = os.getenv(key_name)
        if key_value:
            return self._store_key(key_name, key_value, "environment")
        return None

    def capture_from_process(self, key_name: str, process_name: str) -> Optional[APIKey]:
        """
        Capture API key from running process environment using sudo.
        
        Args:
            key_name: Name of environment variable
            process_name: Name of process to search
            
        Returns:
            APIKey if captured successfully
        """
        if not self.check_sudo_access():
            print("Sudo access required for process capture")
            return None
        
        try:
            # Find process PID
            result = subprocess.run(
                ["pgrep", "-f", process_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                pid = result.stdout.strip().split('\n')[0]
                
                # Read process environment
                env_path = f"/proc/{pid}/environ"
                result = subprocess.run(
                    ["sudo", "cat", env_path],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    env_vars = result.stdout.split('\x00')
                    for var in env_vars:
                        if var.startswith(f"{key_name}="):
                            key_value = var.split('=', 1)[1]
                            return self._store_key(key_name, key_value, f"process:{process_name}")
            
        except Exception as e:
            print(f"Error capturing from process: {e}")
        
        return None

    def _store_key(self, key_name: str, key_value: str, source: str) -> APIKey:
        """Store captured API key."""
        api_key = APIKey(
            key_name=key_name,
            key_value=key_value,
            source=source,
            captured_at=datetime.utcnow().isoformat(),
            metadata={"session_id": self.session_id}
        )
        
        self.captured_keys[key_name] = api_key
        self._save_keys()
        self._update_env_file()
        self._save_session()
        
        return api_key

    def set_key_manually(self, key_name: str, key_value: str) -> APIKey:
        """
        Manually set an API key.
        
        Args:
            key_name: Name for the key
            key_value: Key value
            
        Returns:
            APIKey
        """
        return self._store_key(key_name, key_value, "manual")

    def get_key(self, key_name: str) -> Optional[APIKey]:
        """Get stored API key."""
        return self.captured_keys.get(key_name)

    def export_to_environment(self) -> None:
        """Export all keys to current process environment."""
        for key_name, key in self.captured_keys.items():
            os.environ[key_name] = key.key_value

    def generate_env_script(self, output_path: Optional[str] = None) -> str:
        """
        Generate shell script to set environment variables.
        
        Args:
            output_path: Optional path to save script
            
        Returns:
            Script content
        """
        script_lines = [
            "#!/bin/bash",
            "# Auto-generated API key environment script",
            f"# Session: {self.session_id}",
            f"# Generated: {datetime.utcnow().isoformat()}",
            ""
        ]
        
        for key_name, key in self.captured_keys.items():
            script_lines.append(f"export {key_name}='{key.key_value}'")
        
        script_content = '\n'.join(script_lines)
        
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                f.write(script_content)
            output_file.chmod(0o755)  # Make executable
        
        return script_content

    def auto_capture_instagram_keys(self) -> Dict[str, APIKey]:
        """
        Automatically attempt to capture Instagram API keys from common sources.
        
        Returns:
            Dictionary of captured keys
        """
        captured = {}
        
        # Try environment first
        for key_name in ["INSTAGRAM_API_KEY", "INSTAGRAM_ACCESS_TOKEN", "INSTAGRAM_CLIENT_ID"]:
            key = self.capture_from_environment(key_name)
            if key:
                captured[key_name] = key
        
        # Try common config locations with sudo
        config_locations = [
            "/etc/instagram/config",
            "/usr/local/etc/instagram.conf",
            "~/.instagram/config",
            "~/instagram_credentials.json"
        ]
        
        for config_path in config_locations:
            expanded_path = Path(config_path).expanduser()
            if expanded_path.exists():
                key = self.capture_from_system_config("INSTAGRAM_API_KEY", str(expanded_path))
                if key:
                    captured["INSTAGRAM_API_KEY"] = key
                    break
        
        return captured

    def auto_capture_tiktok_keys(self) -> Dict[str, APIKey]:
        """
        Automatically attempt to capture TikTok API keys from common sources.
        
        Returns:
            Dictionary of captured keys
        """
        captured = {}
        
        # Try environment first
        for key_name in ["TIKTOK_API_KEY", "TIKTOK_ACCESS_TOKEN", "TIKTOK_CLIENT_ID"]:
            key = self.capture_from_environment(key_name)
            if key:
                captured[key_name] = key
        
        # Try common config locations with sudo
        config_locations = [
            "/etc/tiktok/config",
            "/usr/local/etc/tiktok.conf",
            "~/.tiktok/config",
            "~/tiktok_credentials.json"
        ]
        
        for config_path in config_locations:
            expanded_path = Path(config_path).expanduser()
            if expanded_path.exists():
                key = self.capture_from_system_config("TIKTOK_API_KEY", str(expanded_path))
                if key:
                    captured["TIKTOK_API_KEY"] = key
                    break
        
        return captured

    def get_session_info(self) -> Dict:
        """Get current session information."""
        return {
            "session_id": self.session_id,
            "storage_dir": str(self.storage_dir),
            "captured_keys": list(self.captured_keys.keys()),
            "keys_file": str(self.keys_file),
            "env_file": str(self.env_file),
            "session_file": str(self.session_file)
        }

    def clear_session(self) -> None:
        """Clear current session data."""
        self.captured_keys.clear()
        if self.keys_file.exists():
            self.keys_file.unlink()
        if self.env_file.exists():
            self.env_file.unlink()
        if self.session_file.exists():
            self.session_file.unlink()
