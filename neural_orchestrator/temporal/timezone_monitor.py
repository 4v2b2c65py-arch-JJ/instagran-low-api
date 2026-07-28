"""
Timezone Monitor - Global Temporal Tracking System
Monitors current date/time across all global timezones using standard formats.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import pytz
from zoneinfo import ZoneInfo


class TimezoneMonitor:
    """
    Monitors and tracks time across global timezones with constant update intervals.
    Uses standard time format of global scale respective to each continent zone.
    """
    
    # Continent-based timezone groupings
    CONTINENT_TIMEZONES = {
        'Africa': [
            'Africa/Cairo', 'Africa/Johannesburg', 'Africa/Lagos', 
            'Africa/Nairobi', 'Africa/Casablanca'
        ],
        'America': [
            'America/New_York', 'America/Los_Angeles', 'America/Chicago',
            'America/Denver', 'America/Mexico_City', 'America/Sao_Paulo',
            'America/Argentina/Buenos_Aires', 'America/Toronto'
        ],
        'Asia': [
            'Asia/Tokyo', 'Asia/Shanghai', 'Asia/Hong_Kong', 'Asia/Singapore',
            'Asia/Seoul', 'Asia/Dubai', 'Asia/Mumbai', 'Asia/Bangkok',
            'Asia/Jakarta', 'Asia/Kolkata'
        ],
        'Europe': [
            'Europe/London', 'Europe/Paris', 'Europe/Berlin', 'Europe/Moscow',
            'Europe/Rome', 'Europe/Madrid', 'Europe/Amsterdam', 'Europe/Zurich'
        ],
        'Oceania': [
            'Pacific/Auckland', 'Pacific/Sydney', 'Pacific/Melbourne',
            'Australia/Brisbane', 'Pacific/Fiji'
        ],
        'Antarctica': [
            'Antarctica/McMurdo', 'Antarctica/Palmer'
        ]
    }
    
    def __init__(self, update_interval_seconds: float = 1.0):
        """
        Initialize the Timezone Monitor.
        
        Args:
            update_interval_seconds: Constant update interval for time monitoring
        """
        self.update_interval = update_interval_seconds
        self.current_time_utc = datetime.now(timezone.utc)
        self.timezone_snapshots: Dict[str, datetime] = {}
        self.continent_snapshots: Dict[str, Dict[str, datetime]] = {}
        self.time_lag_tracking: Dict[str, timedelta] = {}
        
        # Initialize all timezone snapshots
        self._initialize_timezone_snapshots()
    
    def _initialize_timezone_snapshots(self):
        """Initialize timezone snapshots for all configured timezones."""
        for continent, zones in self.CONTINENT_TIMEZONES.items():
            self.continent_snapshots[continent] = {}
            for zone in zones:
                try:
                    tz = ZoneInfo(zone)
                    local_time = self.current_time_utc.astimezone(tz)
                    self.timezone_snapshots[zone] = local_time
                    self.continent_snapshots[continent][zone] = local_time
                    
                    # Calculate time lag from UTC
                    time_lag = local_time.utcoffset()
                    self.time_lag_tracking[zone] = time_lag
                except Exception as e:
                    print(f"Warning: Could not initialize timezone {zone}: {e}")
    
    def update_time(self):
        """Update current time and refresh all timezone snapshots."""
        self.current_time_utc = datetime.now(timezone.utc)
        
        for zone in self.timezone_snapshots:
            try:
                tz = ZoneInfo(zone)
                local_time = self.current_time_utc.astimezone(tz)
                self.timezone_snapshots[zone] = local_time
                
                # Update continent snapshot
                for continent, zones in self.CONTINENT_TIMEZONES.items():
                    if zone in zones:
                        self.continent_snapshots[continent][zone] = local_time
                        break
            except Exception as e:
                print(f"Warning: Could not update timezone {zone}: {e}")
    
    def get_global_time_snapshot(self) -> Dict[str, Dict[str, str]]:
        """
        Get current time snapshot across all global timezones.
        
        Returns:
            Dictionary containing time snapshots by continent and timezone
        """
        self.update_time()
        
        snapshot = {
            'utc': self.current_time_utc.isoformat(),
            'timestamp': self.current_time_utc.timestamp(),
            'continents': {}
        }
        
        for continent, zones in self.continent_snapshots.items():
            snapshot['continents'][continent] = {}
            for zone, time_obj in zones.items():
                snapshot['continents'][continent][zone] = {
                    'time': time_obj.isoformat(),
                    'offset_hours': time_obj.utcoffset().total_seconds() / 3600,
                    'standard_format': time_obj.strftime('%Y-%m-%d %H:%M:%S %Z')
                }
        
        return snapshot
    
    def get_timezone_time(self, timezone_str: str) -> Optional[datetime]:
        """
        Get current time for a specific timezone.
        
        Args:
            timezone_str: IANA timezone string (e.g., 'America/New_York')
            
        Returns:
            Current datetime in the specified timezone, or None if invalid
        """
        try:
            tz = ZoneInfo(timezone_str)
            return self.current_time_utc.astimezone(tz)
        except Exception:
            return None
    
    def get_continent_times(self, continent: str) -> Optional[Dict[str, datetime]]:
        """
        Get current times for all timezones in a continent.
        
        Args:
            continent: Continent name (e.g., 'Europe', 'Asia')
            
        Returns:
            Dictionary of timezone to datetime mappings, or None if invalid
        """
        return self.continent_snapshots.get(continent)
    
    def calculate_time_lag(self, timezone1: str, timezone2: str) -> Optional[timedelta]:
        """
        Calculate time lag between two timezones.
        
        Args:
            timezone1: First timezone string
            timezone2: Second timezone string
            
        Returns:
            Time difference as timedelta, or None if invalid
        """
        time1 = self.get_timezone_time(timezone1)
        time2 = self.get_timezone_time(timezone2)
        
        if time1 and time2:
            return time2 - time1
        return None
    
    def get_spatial_temporal_mapping(self) -> Dict[str, Dict]:
        """
        Get spatial-temporal mapping for cognitive dimension tracking.
        
        Returns:
            Dictionary mapping timezones to spatial coordinates and temporal data
        """
        mapping = {}
        
        for zone, time_obj in self.timezone_snapshots.items():
            # Extract continent and city from timezone string
            parts = zone.split('/')
            continent = parts[0] if len(parts) > 0 else 'Unknown'
            city = parts[-1] if len(parts) > 1 else 'Unknown'
            
            mapping[zone] = {
                'continent': continent,
                'city': city,
                'utc_offset': time_obj.utcoffset().total_seconds(),
                'timestamp': time_obj.timestamp(),
                'hour': time_obj.hour,
                'is_daylight': 6 <= time_obj.hour < 18,
                'temporal_density': time_obj.hour / 24.0
            }
        
        return mapping
    
    def get_biologic_neural_time_iteration(self) -> Dict[str, float]:
        """
        Calculate biologic neural time iteration for cognitive processing.
        Based on 24-hour biological cycle.
        
        Returns:
            Dictionary containing biologic time metrics
        """
        utc_hour = self.current_time_utc.hour
        utc_minute = self.current_time_utc.minute
        utc_second = self.current_time_utc.second
        
        # Calculate iteration based on 24-hour cycle
        total_seconds = utc_hour * 3600 + utc_minute * 60 + utc_second
        iteration = total_seconds / 86400.0  # Fraction of day
        
        return {
            'iteration_n': iteration,
            'hour': utc_hour,
            'minute': utc_minute,
            'second': utc_second,
            'cycle_position': iteration * 2 * 3.14159  # Convert to radians
        }
