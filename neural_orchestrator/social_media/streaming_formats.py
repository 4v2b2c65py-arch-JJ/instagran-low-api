"""
Streaming Format Handler - Streaming Format Support (HLS, DASH)
Handles HLS (.m3u8 playlists + .ts segments) and DASH (.mpd + segments) streaming formats.
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import hashlib


class StreamingProtocol(Enum):
    """Streaming protocols."""
    HLS = "hls"  # HTTP Live Streaming
    DASH = "dash"  # Dynamic Adaptive Streaming over HTTP


class SegmentFormat(Enum):
    """Segment formats."""
    TS = "ts"  # MPEG-TS (HLS)
    MP4 = "mp4"  # MP4 segments (DASH)
    WEBM = "webm"  # WebM segments


@dataclass
class StreamSegment:
    """Represents a stream segment."""
    segment_id: str
    sequence_number: int
    duration: float
    format: SegmentFormat
    url: str
    size_bytes: int
    bandwidth: int
    sha256: str


@dataclass
class StreamPlaylist:
    """Represents a stream playlist."""
    playlist_id: str
    protocol: StreamingProtocol
    url: str
    segments: List[StreamSegment]
    target_duration: float
    total_duration: float
    bandwidth: int
    codecs: List[str]
    resolution: Optional[Tuple[int, int]]
    sha256: str


@dataclass
class StreamSession:
    """Represents an active streaming session."""
    session_id: str
    playlist_id: str
    start_time: float
    current_segment: int
    buffer_segments: List[StreamSegment]
    quality_level: str
    status: str


class StreamingFormatHandler:
    """
    Handles streaming formats (HLS and DASH).
    Manages playlists, segments, and adaptive streaming.
    """
    
    def __init__(self):
        """Initialize the Streaming Format Handler."""
        # Playlist storage
        self.playlists: Dict[str, StreamPlaylist] = {}
        
        # Segment storage
        self.segments: Dict[str, StreamSegment] = {}
        
        # Active sessions
        self.sessions: Dict[str, StreamSession] = {}
        
        # Quality levels
        self.quality_levels = {
            'auto': 0,
            'low': 500000,      # 500 kbps
            'medium': 1000000,  # 1 Mbps
            'high': 2500000,    # 2.5 Mbps
            'ultra': 5000000    # 5 Mbps
        }
    
    def create_hls_playlist(
        self,
        segments: List[Dict],
        target_duration: float = 10.0,
        bandwidth: int = 1000000,
        resolution: Optional[Tuple[int, int]] = None
    ) -> StreamPlaylist:
        """
        Create an HLS playlist (.m3u8).
        
        Args:
            segments: List of segment data
            target_duration: Target segment duration in seconds
            bandwidth: Bandwidth in bits per second
            resolution: Video resolution (width, height)
            
        Returns:
            StreamPlaylist object
        """
        # Create segments
        stream_segments = []
        total_duration = 0.0
        
        for i, segment_data in enumerate(segments):
            segment_id = f"hls_seg_{i}_{datetime.now().timestamp()}"
            
            segment = StreamSegment(
                segment_id=segment_id,
                sequence_number=i,
                duration=segment_data.get('duration', target_duration),
                format=SegmentFormat.TS,
                url=segment_data.get('url', f"segment_{i}.ts"),
                size_bytes=segment_data.get('size', 0),
                bandwidth=bandwidth,
                sha256=self._calculate_sha256(str(segment_data).encode())
            )
            
            stream_segments.append(segment)
            self.segments[segment_id] = segment
            total_duration += segment.duration
        
        # Create playlist
        playlist_id = f"hls_{datetime.now().timestamp()}"
        playlist_url = f"playlist_{playlist_id}.m3u8"
        
        playlist = StreamPlaylist(
            playlist_id=playlist_id,
            protocol=StreamingProtocol.HLS,
            url=playlist_url,
            segments=stream_segments,
            target_duration=target_duration,
            total_duration=total_duration,
            bandwidth=bandwidth,
            codecs=['h264', 'aac'],
            resolution=resolution,
            sha256=self._calculate_sha256(playlist_url.encode())
        )
        
        self.playlists[playlist_id] = playlist
        
        return playlist
    
    def create_dash_playlist(
        self,
        segments: List[Dict],
        mpd_url: str,
        bandwidth: int = 1000000,
        resolution: Optional[Tuple[int, int]] = None
    ) -> StreamPlaylist:
        """
        Create a DASH manifest (.mpd).
        
        Args:
            segments: List of segment data
            mpd_url: URL for the MPD file
            bandwidth: Bandwidth in bits per second
            resolution: Video resolution (width, height)
            
        Returns:
            StreamPlaylist object
        """
        # Create segments
        stream_segments = []
        total_duration = 0.0
        
        for i, segment_data in enumerate(segments):
            segment_id = f"dash_seg_{i}_{datetime.now().timestamp()}"
            
            segment = StreamSegment(
                segment_id=segment_id,
                sequence_number=i,
                duration=segment_data.get('duration', 2.0),
                format=SegmentFormat.MP4,
                url=segment_data.get('url', f"segment_{i}.m4s"),
                size_bytes=segment_data.get('size', 0),
                bandwidth=bandwidth,
                sha256=self._calculate_sha256(str(segment_data).encode())
            )
            
            stream_segments.append(segment)
            self.segments[segment_id] = segment
            total_duration += segment.duration
        
        # Create playlist
        playlist_id = f"dash_{datetime.now().timestamp()}"
        
        playlist = StreamPlaylist(
            playlist_id=playlist_id,
            protocol=StreamingProtocol.DASH,
            url=mpd_url,
            segments=stream_segments,
            target_duration=2.0,
            total_duration=total_duration,
            bandwidth=bandwidth,
            codecs=['h264', 'aac'],
            resolution=resolution,
            sha256=self._calculate_sha256(mpd_url.encode())
        )
        
        self.playlists[playlist_id] = playlist
        
        return playlist
    
    def start_streaming_session(
        self,
        playlist_id: str,
        quality_level: str = 'auto'
    ) -> Optional[StreamSession]:
        """
        Start a streaming session.
        
        Args:
            playlist_id: Playlist ID to stream
            quality_level: Quality level (auto, low, medium, high, ultra)
            
        Returns:
            StreamSession object or None
        """
        if playlist_id not in self.playlists:
            return None
        
        playlist = self.playlists[playlist_id]
        
        # Determine actual bandwidth based on quality level
        if quality_level == 'auto':
            bandwidth = playlist.bandwidth
        else:
            bandwidth = self.quality_levels.get(quality_level, playlist.bandwidth)
        
        # Create session
        session_id = f"session_{datetime.now().timestamp()}"
        
        session = StreamSession(
            session_id=session_id,
            playlist_id=playlist_id,
            start_time=datetime.now().timestamp(),
            current_segment=0,
            buffer_segments=[],
            quality_level=quality_level,
            status="buffering"
        )
        
        self.sessions[session_id] = session
        
        return session
    
    def get_next_segment(self, session_id: str) -> Optional[StreamSegment]:
        """
        Get the next segment for a streaming session.
        
        Args:
            session_id: Session ID
            
        Returns:
            StreamSegment object or None
        """
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        playlist = self.playlists.get(session.playlist_id)
        
        if not playlist or session.current_segment >= len(playlist.segments):
            return None
        
        segment = playlist.segments[session.current_segment]
        session.current_segment += 1
        session.status = "playing"
        
        return segment
    
    def buffer_segments(
        self,
        session_id: str,
        buffer_size: int = 3
    ) -> List[StreamSegment]:
        """
        Buffer segments for a session.
        
        Args:
            session_id: Session ID
            buffer_size: Number of segments to buffer
            
        Returns:
            List of buffered StreamSegment objects
        """
        if session_id not in self.sessions:
            return []
        
        session = self.sessions[session_id]
        playlist = self.playlists.get(session.playlist_id)
        
        if not playlist:
            return []
        
        buffered = []
        
        for _ in range(buffer_size):
            segment = self.get_next_segment(session_id)
            if segment:
                buffered.append(segment)
                session.buffer_segments.append(segment)
            else:
                break
        
        if buffered:
            session.status = "ready"
        
        return buffered
    
    def adapt_quality(
        self,
        session_id: str,
        available_bandwidth: int
    ) -> str:
        """
        Adapt quality based on available bandwidth.
        
        Args:
            session_id: Session ID
            available_bandwidth: Available bandwidth in bps
            
        Returns:
            New quality level
        """
        if session_id not in self.sessions:
            return 'auto'
        
        session = self.sessions[session_id]
        
        # Find appropriate quality level
        new_quality = 'auto'
        
        for quality, bandwidth in sorted(self.quality_levels.items(), key=lambda x: x[1]):
            if available_bandwidth >= bandwidth:
                new_quality = quality
        
        session.quality_level = new_quality
        
        return new_quality
    
    def get_playlist_m3u8(self, playlist_id: str) -> Optional[str]:
        """
        Generate HLS playlist content (.m3u8 format).
        
        Args:
            playlist_id: Playlist ID
            
        Returns:
            M3U8 playlist content or None
        """
        if playlist_id not in self.playlists:
            return None
        
        playlist = self.playlists[playlist_id]
        
        if playlist.protocol != StreamingProtocol.HLS:
            return None
        
        # Generate M3U8 content
        m3u8_content = f"#EXTM3U\n"
        m3u8_content += f"#EXT-X-VERSION:3\n"
        m3u8_content += f"#EXT-X-TARGETDURATION:{int(playlist.target_duration)}\n"
        m3u8_content += f"#EXT-X-MEDIA-SEQUENCE:0\n"
        
        for segment in playlist.segments:
            m3u8_content += f"#EXTINF:{segment.duration:.1f},\n"
            m3u8_content += f"{segment.url}\n"
        
        m3u8_content += "#EXT-X-ENDLIST\n"
        
        return m3u8_content
    
    def get_playlist_mpd(self, playlist_id: str) -> Optional[str]:
        """
        Generate DASH manifest content (.mpd format).
        
        Args:
            playlist_id: Playlist ID
            
        Returns:
            MPD manifest content or None
        """
        if playlist_id not in self.playlists:
            return None
        
        playlist = self.playlists[playlist_id]
        
        if playlist.protocol != StreamingProtocol.DASH:
            return None
        
        # Generate simplified MPD content
        mpd_content = f"""<?xml version="1.0"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011" type="static">
  <Period>
    <AdaptationSet mimeType="video/mp4">
      <Representation bandwidth="{playlist.bandwidth}" width="{playlist.resolution[0] if playlist.resolution else 1920}" height="{playlist.resolution[1] if playlist.resolution else 1080}">
"""
        
        for segment in playlist.segments:
            mpd_content += f'        <Segment media="{segment.url}" duration="{segment.duration}"/>\n'
        
        mpd_content += """      </Representation>
    </AdaptationSet>
  </Period>
</MPD>"""
        
        return mpd_content
    
    def get_segment_by_sha(self, sha256: str) -> Optional[StreamSegment]:
        """
        Get a segment by SHA256 hash.
        
        Args:
            sha256: SHA256 hash
            
        Returns:
            StreamSegment object or None
        """
        for segment in self.segments.values():
            if segment.sha256 == sha256:
                return segment
        return None
    
    def end_session(self, session_id: str) -> bool:
        """
        End a streaming session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if ended successfully
        """
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        session.status = "ended"
        
        del self.sessions[session_id]
        
        return True
    
    def get_streaming_statistics(self) -> Dict[str, any]:
        """
        Get statistics about streaming.
        
        Returns:
            Dictionary containing streaming statistics
        """
        protocol_counts = {}
        for playlist in self.playlists.values():
            protocol = playlist.protocol.value
            protocol_counts[protocol] = protocol_counts.get(protocol, 0) + 1
        
        active_sessions = len([s for s in self.sessions.values() if s.status in ["buffering", "playing", "ready"]])
        
        return {
            'total_playlists': len(self.playlists),
            'total_segments': len(self.segments),
            'active_sessions': active_sessions,
            'protocol_distribution': protocol_counts,
            'quality_levels': list(self.quality_levels.keys())
        }
    
    def _calculate_sha256(self, data: bytes) -> str:
        """
        Calculate SHA256 hash of data.
        
        Args:
            data: Data to hash
            
        Returns:
            SHA256 hash string
        """
        return hashlib.sha256(data).hexdigest()
