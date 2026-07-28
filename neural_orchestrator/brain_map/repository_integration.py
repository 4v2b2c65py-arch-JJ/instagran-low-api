"""
Repository Integration - External Data Source Integration
Integrates external repository data (e.g., probele-sequence) into brain map layer.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class RepositoryData:
    """Represents data from an external repository."""
    repo_name: str
    data_type: str
    content: Dict[str, any]
    timestamp: float
    processed: bool = False


class RepositoryIntegration:
    """
    Integrates external repository data into the brain map layer.
    Currently supports integration with probele-sequence repository.
    """
    
    def __init__(self, repo_url: str = "https://github.com/JlovesYouGit/probele-sequence"):
        """
        Initialize the Repository Integration.
        
        Args:
            repo_url: URL of the repository to integrate
        """
        self.repo_url = repo_url
        self.repo_name = self._extract_repo_name(repo_url)
        
        # Repository data storage
        self.repository_data: List[RepositoryData] = []
        
        # Integration state
        self.is_connected = False
        self.last_sync_timestamp = 0.0
        
        # Data mappings for NETesSpectrumBench
        self.data_mappings: Dict[str, str] = {
            'spectrum': 'spectrum_analysis',
            'network': 'network_testing',
            'tower': 'cellular_tower'
        }
    
    def _extract_repo_name(self, repo_url: str) -> str:
        """
        Extract repository name from URL.
        
        Args:
            repo_url: Repository URL
            
        Returns:
            Repository name
        """
        parts = repo_url.split('/')
        return parts[-1] if parts else "unknown"
    
    def connect(self) -> bool:
        """
        Attempt to connect to the repository.
        
        Returns:
            True if connection successful, False otherwise
        """
        # In a real implementation, this would attempt to connect to the repository
        # For now, we'll simulate connection
        self.is_connected = True
        self.last_sync_timestamp = datetime.now().timestamp()
        return True
    
    def disconnect(self):
        """Disconnect from the repository."""
        self.is_connected = False
    
    def fetch_data(self, data_type: str = "all") -> List[RepositoryData]:
        """
        Fetch data from the repository.
        
        Args:
            data_type: Type of data to fetch ('all' for all types)
            
        Returns:
            List of RepositoryData objects
        """
        if not self.is_connected:
            return []
        
        # In a real implementation, this would fetch actual data from the repository
        # For now, we'll generate sample data based on the probele-sequence concept
        
        sample_data = self._generate_sample_data(data_type)
        
        for data in sample_data:
            self.repository_data.append(data)
        
        self.last_sync_timestamp = datetime.now().timestamp()
        
        return sample_data
    
    def _generate_sample_data(self, data_type: str) -> List[RepositoryData]:
        """
        Generate sample data for integration from NETesSpectrumBench.
        
        Args:
            data_type: Type of data to generate
            
        Returns:
            List of RepositoryData objects
        """
        sample_data = []
        
        if data_type == "all" or data_type == "spectrum":
            # Generate spectrum analysis data
            spectrum_data = RepositoryData(
                repo_name=self.repo_name,
                data_type="spectrum",
                content={
                    'spectrum_id': f"spec_{datetime.now().timestamp()}",
                    'frequency_range': (2.4e9, 5.0e9),  # WiFi frequency range
                    'signal_strength': np.random.uniform(-100, -30),  # dBm
                    'channel': np.random.randint(1, 14),
                    'noise_floor': np.random.uniform(-95, -85),
                    'bandwidth': np.random.choice([20, 40, 80, 160])  # MHz
                },
                timestamp=datetime.now().timestamp()
            )
            sample_data.append(spectrum_data)
        
        if data_type == "all" or data_type == "network":
            # Generate network testing data
            network_data = RepositoryData(
                repo_name=self.repo_name,
                data_type="network",
                content={
                    'network_id': f"net_{datetime.now().timestamp()}",
                    'latency_ms': np.random.uniform(1, 100),
                    'packet_loss': np.random.uniform(0, 5),
                    'throughput_mbps': np.random.uniform(10, 1000),
                    'jitter_ms': np.random.uniform(0, 50),
                    'connection_type': np.random.choice(['wifi', 'cellular', 'ethernet'])
                },
                timestamp=datetime.now().timestamp()
            )
            sample_data.append(network_data)
        
        if data_type == "all" or data_type == "tower":
            # Generate cellular tower mapping data
            tower_data = RepositoryData(
                repo_name=self.repo_name,
                data_type="tower",
                content={
                    'tower_id': f"tower_{datetime.now().timestamp()}",
                    'latitude': np.random.uniform(-90, 90),
                    'longitude': np.random.uniform(-180, 180),
                    'signal_type': np.random.choice(['4G', '5G', 'LTE']),
                    'signal_strength': np.random.uniform(-110, -50),
                    'distance_km': np.random.uniform(0.1, 10)
                },
                timestamp=datetime.now().timestamp()
            )
            sample_data.append(tower_data)
        
        return sample_data
    
    def process_for_brain_map(self, data: RepositoryData) -> Dict[str, any]:
        """
        Process repository data for brain map integration.
        
        Args:
            data: RepositoryData to process
            
        Returns:
            Dictionary containing processed data for brain map
        """
        # Map data type to brain map node type
        brain_map_type = self.data_mappings.get(data.data_type, data.data_type)
        
        # Create brain map feed data
        processed_data = {
            'source': 'repository',
            'repo_name': self.repo_name,
            'data_type': brain_map_type,
            'content': data.content,
            'timestamp': data.timestamp,
            'metadata': {
                'original_type': data.data_type,
                'processed': True
            }
        }
        
        # Mark as processed
        data.processed = True
        
        return processed_data
    
    def get_processed_feeds(self) -> List[Dict[str, any]]:
        """
        Get all processed data feeds for brain map.
        
        Returns:
            List of processed feed dictionaries
        """
        processed_feeds = []
        
        for data in self.repository_data:
            if not data.processed:
                feed = self.process_for_brain_map(data)
                processed_feeds.append(feed)
        
        return processed_feeds
    
    def get_repository_statistics(self) -> Dict[str, any]:
        """
        Get statistics about repository integration.
        
        Returns:
            Dictionary containing repository statistics
        """
        data_types = {}
        for data in self.repository_data:
            data_types[data.data_type] = data_types.get(data.data_type, 0) + 1
        
        return {
            'repo_url': self.repo_url,
            'repo_name': self.repo_name,
            'is_connected': self.is_connected,
            'total_data_items': len(self.repository_data),
            'processed_count': sum(1 for d in self.repository_data if d.processed),
            'unprocessed_count': sum(1 for d in self.repository_data if not d.processed),
            'data_types': data_types,
            'last_sync_timestamp': self.last_sync_timestamp
        }
    
    def clear_old_data(self, max_age_seconds: float = 86400):
        """
        Clear old repository data.
        
        Args:
            max_age_seconds: Maximum age in seconds (default 24 hours)
        """
        current_time = datetime.now().timestamp()
        
        self.repository_data = [
            data for data in self.repository_data
            if current_time - data.timestamp < max_age_seconds
        ]
    
    def sync_with_brain_map(self, brain_map_layer) -> int:
        """
        Sync repository data with brain map layer.
        
        Args:
            brain_map_layer: BrainMapLayer instance to sync with
            
        Returns:
            Number of items synced
        """
        if not self.is_connected:
            return 0
        
        # Get processed feeds
        feeds = self.get_processed_feeds()
        
        # Group by data type
        feeds_by_type = {}
        for feed in feeds:
            data_type = feed['data_type']
            if data_type not in feeds_by_type:
                feeds_by_type[data_type] = []
            feeds_by_type[data_type].append(feed)
        
        # Add to brain map
        for data_type, type_feeds in feeds_by_type.items():
            brain_map_layer.add_input_feed(data_type, type_feeds)
        
        return len(feeds)
