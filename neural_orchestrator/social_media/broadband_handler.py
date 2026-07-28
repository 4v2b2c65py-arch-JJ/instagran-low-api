"""
Broadband Handler - Broadband Support Handling
Manages broadband connectivity and data transfer for social media features.
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ConnectionQuality(Enum):
    """Quality of broadband connection."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    OFFLINE = "offline"


class DataType(Enum):
    """Types of data for broadband handling."""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    STREAM = "stream"
    FILE = "file"


@dataclass
class BandwidthMeasurement:
    """Represents a bandwidth measurement."""
    timestamp: float
    download_speed_mbps: float
    upload_speed_mbps: float
    latency_ms: float
    packet_loss_percent: float
    connection_quality: ConnectionQuality


@dataclass
class DataTransfer:
    """Represents a data transfer operation."""
    transfer_id: str
    data_type: DataType
    size_bytes: int
    transferred_bytes: int
    start_time: float
    end_time: Optional[float]
    speed_mbps: float
    status: str
    error: Optional[str]


class BroadbandHandler:
    """
    Handles broadband connectivity and data transfer.
    Manages bandwidth, connection quality, and data transfer optimization.
    """
    
    def __init__(self):
        """Initialize the Broadband Handler."""
        # Connection tracking
        self.current_quality = ConnectionQuality.OFFLINE
        self.bandwidth_history: List[BandwidthMeasurement] = []
        
        # Data transfer tracking
        self.active_transfers: Dict[str, DataTransfer] = {}
        self.transfer_history: List[DataTransfer] = []
        
        # Bandwidth thresholds (Mbps)
        self.thresholds = {
            ConnectionQuality.EXCELLENT: 100.0,
            ConnectionQuality.GOOD: 50.0,
            ConnectionQuality.FAIR: 10.0,
            ConnectionQuality.POOR: 1.0,
            ConnectionQuality.OFFLINE: 0.0
        }
        
        # Data size limits for different qualities
        self.size_limits = {
            ConnectionQuality.EXCELLENT: 100 * 1024 * 1024,  # 100MB
            ConnectionQuality.GOOD: 50 * 1024 * 1024,  # 50MB
            ConnectionQuality.FAIR: 10 * 1024 * 1024,  # 10MB
            ConnectionQuality.POOR: 1 * 1024 * 1024,  # 1MB
            ConnectionQuality.OFFLINE: 0
        }
    
    def measure_bandwidth(self) -> BandwidthMeasurement:
        """
        Measure current bandwidth and connection quality.
        
        Returns:
            BandwidthMeasurement object
        """
        # Simulate bandwidth measurement
        # In real implementation, use actual network measurement tools
        import random
        
        download_speed = random.uniform(10, 200)  # Mbps
        upload_speed = download_speed * 0.4  # Typically 40% of download
        latency = random.uniform(5, 100)  # ms
        packet_loss = random.uniform(0, 5)  # percent
        
        # Determine connection quality
        quality = self._determine_quality(download_speed, latency, packet_loss)
        
        measurement = BandwidthMeasurement(
            timestamp=datetime.now().timestamp(),
            download_speed_mbps=download_speed,
            upload_speed_mbps=upload_speed,
            latency_ms=latency,
            packet_loss_percent=packet_loss,
            connection_quality=quality
        )
        
        self.bandwidth_history.append(measurement)
        self.current_quality = quality
        
        # Keep history manageable
        if len(self.bandwidth_history) > 100:
            self.bandwidth_history.pop(0)
        
        return measurement
    
    def _determine_quality(
        self,
        download_speed: float,
        latency: float,
        packet_loss: float
    ) -> ConnectionQuality:
        """
        Determine connection quality from measurements.
        
        Args:
            download_speed: Download speed in Mbps
            latency: Latency in ms
            packet_loss: Packet loss percentage
            
        Returns:
            ConnectionQuality enum
        """
        if download_speed >= self.thresholds[ConnectionQuality.EXCELLENT] and latency < 20 and packet_loss < 1:
            return ConnectionQuality.EXCELLENT
        elif download_speed >= self.thresholds[ConnectionQuality.GOOD] and latency < 50 and packet_loss < 2:
            return ConnectionQuality.GOOD
        elif download_speed >= self.thresholds[ConnectionQuality.FAIR] and latency < 100 and packet_loss < 5:
            return ConnectionQuality.FAIR
        elif download_speed >= self.thresholds[ConnectionQuality.POOR]:
            return ConnectionQuality.POOR
        else:
            return ConnectionQuality.OFFLINE
    
    def can_transfer(self, data_type: DataType, size_bytes: int) -> Tuple[bool, str]:
        """
        Check if data can be transferred given current connection.
        
        Args:
            data_type: Type of data
            size_bytes: Size in bytes
            
        Returns:
            Tuple of (can_transfer, reason)
        """
        if self.current_quality == ConnectionQuality.OFFLINE:
            return False, "No internet connection"
        
        max_size = self.size_limits[self.current_quality]
        
        if size_bytes > max_size:
            return False, f"File too large for current connection (max: {max_size / 1024 / 1024:.1f}MB)"
        
        # Adjust for data type
        if data_type == DataType.VIDEO and self.current_quality in [ConnectionQuality.POOR, ConnectionQuality.FAIR]:
            return False, "Video streaming requires better connection"
        
        return True, "Transfer allowed"
    
    async def transfer_data(
        self,
        data: bytes,
        data_type: DataType,
        metadata: Optional[Dict] = None
    ) -> DataTransfer:
        """
        Transfer data over broadband.
        
        Args:
            data: Data to transfer
            data_type: Type of data
            metadata: Additional metadata
            
        Returns:
            DataTransfer object
        """
        # Check if transfer is possible
        can_transfer, reason = self.can_transfer(data_type, len(data))
        if not can_transfer:
            transfer = DataTransfer(
                transfer_id=f"transfer_failed_{datetime.now().timestamp()}",
                data_type=data_type,
                size_bytes=len(data),
                transferred_bytes=0,
                start_time=datetime.now().timestamp(),
                end_time=datetime.now().timestamp(),
                speed_mbps=0.0,
                status="failed",
                error=reason
            )
            self.transfer_history.append(transfer)
            return transfer
        
        # Generate transfer ID
        transfer_id = f"transfer_{datetime.now().timestamp()}"
        
        # Create transfer object
        transfer = DataTransfer(
            transfer_id=transfer_id,
            data_type=data_type,
            size_bytes=len(data),
            transferred_bytes=0,
            start_time=datetime.now().timestamp(),
            end_time=None,
            speed_mbps=0.0,
            status="in_progress",
            error=None
        )
        
        self.active_transfers[transfer_id] = transfer
        
        # Simulate transfer
        try:
            # Calculate transfer speed based on connection quality
            base_speed = self._get_transfer_speed(data_type)
            
            # Simulate transfer time
            transfer_time = len(data) / (base_speed * 1024 * 1024 / 8)  # seconds
            
            # Simulate progress
            chunk_size = len(data) // 10
            for i in range(10):
                await asyncio.sleep(transfer_time / 10)
                transfer.transferred_bytes += chunk_size
                transfer.speed_mbps = base_speed
            
            # Complete transfer
            transfer.transferred_bytes = len(data)
            transfer.end_time = datetime.now().timestamp()
            transfer.status = "completed"
            
            # Calculate actual speed
            duration = transfer.end_time - transfer.start_time
            if duration > 0:
                transfer.speed_mbps = (len(data) * 8 / 1024 / 1024) / duration
            
        except Exception as e:
            transfer.end_time = datetime.now().timestamp()
            transfer.status = "failed"
            transfer.error = str(e)
        
        # Move to history
        del self.active_transfers[transfer_id]
        self.transfer_history.append(transfer)
        
        if len(self.transfer_history) > 1000:
            self.transfer_history.pop(0)
        
        return transfer
    
    def _get_transfer_speed(self, data_type: DataType) -> float:
        """
        Get transfer speed based on data type and connection quality.
        
        Args:
            data_type: Type of data
            
        Returns:
            Speed in Mbps
        """
        base_speeds = {
            ConnectionQuality.EXCELLENT: 100.0,
            ConnectionQuality.GOOD: 50.0,
            ConnectionQuality.FAIR: 10.0,
            ConnectionQuality.POOR: 1.0
        }
        
        base_speed = base_speeds.get(self.current_quality, 1.0)
        
        # Adjust for data type
        type_multipliers = {
            DataType.IMAGE: 1.0,
            DataType.VIDEO: 0.8,
            DataType.AUDIO: 0.9,
            DataType.TEXT: 1.2,
            DataType.STREAM: 0.5,
            DataType.FILE: 0.7
        }
        
        multiplier = type_multipliers.get(data_type, 1.0)
        
        return base_speed * multiplier
    
    def optimize_for_connection(self, data_type: DataType, original_size: int) -> Dict[str, any]:
        """
        Get optimization recommendations for current connection.
        
        Args:
            data_type: Type of data
            original_size: Original size in bytes
            
        Returns:
            Dictionary with optimization recommendations
        """
        recommendations = {
            'can_transfer': True,
            'recommended_quality': 'high',
            'max_size': self.size_limits[self.current_quality],
            'compression': False,
            'chunking': False
        }
        
        can_transfer, reason = self.can_transfer(data_type, original_size)
        recommendations['can_transfer'] = can_transfer
        recommendations['reason'] = reason if not can_transfer else None
        
        if not can_transfer:
            return recommendations
        
        # Quality recommendations based on connection
        if self.current_quality == ConnectionQuality.EXCELLENT:
            recommendations['recommended_quality'] = 'high'
        elif self.current_quality == ConnectionQuality.GOOD:
            recommendations['recommended_quality'] = 'medium'
        elif self.current_quality == ConnectionQuality.FAIR:
            recommendations['recommended_quality'] = 'low'
            recommendations['compression'] = True
        else:
            recommendations['recommended_quality'] = 'very_low'
            recommendations['compression'] = True
            recommendations['chunking'] = True
        
        return recommendations
    
    def get_connection_status(self) -> Dict[str, any]:
        """
        Get current connection status.
        
        Returns:
            Dictionary containing connection status
        """
        if not self.bandwidth_history:
            return {
                'quality': ConnectionQuality.OFFLINE.value,
                'connected': False
            }
        
        latest = self.bandwidth_history[-1]
        
        return {
            'quality': latest.connection_quality.value,
            'download_speed_mbps': latest.download_speed_mbps,
            'upload_speed_mbps': latest.upload_speed_mbps,
            'latency_ms': latest.latency_ms,
            'packet_loss_percent': latest.packet_loss_percent,
            'connected': latest.connection_quality != ConnectionQuality.OFFLINE,
            'max_transfer_size': self.size_limits[latest.connection_quality]
        }
    
    def get_transfer_statistics(self) -> Dict[str, any]:
        """
        Get statistics about data transfers.
        
        Returns:
            Dictionary containing transfer statistics
        """
        if not self.transfer_history:
            return {
                'total_transfers': 0,
                'successful_transfers': 0,
                'failed_transfers': 0
            }
        
        successful = sum(1 for t in self.transfer_history if t.status == "completed")
        failed = sum(1 for t in self.transfer_history if t.status == "failed")
        
        total_bytes = sum(t.size_bytes for t in self.transfer_history)
        avg_speed = sum(t.speed_mbps for t in self.transfer_history if t.speed_mbps > 0) / len(self.transfer_history)
        
        type_counts = {}
        for transfer in self.transfer_history:
            dtype = transfer.data_type.value
            type_counts[dtype] = type_counts.get(dtype, 0) + 1
        
        return {
            'total_transfers': len(self.transfer_history),
            'successful_transfers': successful,
            'failed_transfers': failed,
            'success_rate': successful / len(self.transfer_history),
            'total_bytes_transferred': total_bytes,
            'average_speed_mbps': avg_speed,
            'active_transfers': len(self.active_transfers),
            'data_type_distribution': type_counts
        }
    
    def cancel_transfer(self, transfer_id: str) -> bool:
        """
        Cancel an active transfer.
        
        Args:
            transfer_id: Transfer ID to cancel
            
        Returns:
            True if cancelled successfully
        """
        if transfer_id not in self.active_transfers:
            return False
        
        transfer = self.active_transfers[transfer_id]
        transfer.end_time = datetime.now().timestamp()
        transfer.status = "cancelled"
        
        # Move to history
        del self.active_transfers[transfer_id]
        self.transfer_history.append(transfer)
        
        return True
