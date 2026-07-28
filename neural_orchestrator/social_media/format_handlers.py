"""
Social Media Format Handlers - Social Media File Format Support
Handles JPEG, PNG, WebP, MP4, MP3, AAC, WAV, and other social media formats.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import hashlib


class ImageFormat(Enum):
    """Image formats used by social media."""
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    GIF = "gif"


class VideoFormat(Enum):
    """Video formats used by social media."""
    MP4_H264 = "mp4_h264"  # H.264/AVC
    MP4_H265 = "mp4_h265"  # H.265/HEVC
    WEBM = "webm"


class AudioFormat(Enum):
    """Audio formats used by social media."""
    MP3 = "mp3"
    AAC = "aac"
    WAV = "wav"
    AAC_IN_MP4 = "aac_in_mp4"


class StreamingFormat(Enum):
    """Streaming formats used by social media."""
    HLS = "hls"  # .m3u8 playlists + .ts segments
    DASH = "dash"  # .mpd + segments


@dataclass
class MediaMetadata:
    """Metadata for media files."""
    format: str
    width: Optional[int]
    height: Optional[int]
    duration: Optional[float]
    bitrate: Optional[int]
    codec: Optional[str]
    size_bytes: int
    sha256: str
    timestamp: float


class SocialMediaFormatHandlers:
    """
    Handles social media file formats.
    Supports JPEG, PNG, WebP, MP4, MP3, AAC, WAV, HLS, DASH.
    """
    
    def __init__(self):
        """Initialize the Social Media Format Handlers."""
        self.processed_files: Dict[str, MediaMetadata] = {}
        self.format_statistics: Dict[str, int] = {}
        
        # Supported formats
        self.image_formats = [fmt.value for fmt in ImageFormat]
        self.video_formats = [fmt.value for fmt in VideoFormat]
        self.audio_formats = [fmt.value for fmt in AudioFormat]
        self.streaming_formats = [fmt.value for fmt in StreamingFormat]
    
    def process_image(
        self,
        image_data: Union[bytes, np.ndarray],
        format: str = "jpeg",
        metadata: Optional[Dict] = None
    ) -> Tuple[MediaMetadata, np.ndarray]:
        """
        Process image data for social media.
        
        Args:
            image_data: Image data (bytes or numpy array)
            format: Image format (jpeg, png, webp, gif)
            metadata: Additional metadata
            
        Returns:
            Tuple of (MediaMetadata, processed_image)
        """
        # Convert to numpy array if bytes
        if isinstance(image_data, bytes):
            processed_image = self._decode_image_bytes(image_data, format)
        else:
            processed_image = image_data
        
        # Calculate SHA256
        sha256 = self._calculate_sha256(image_data)
        
        # Create metadata
        media_metadata = MediaMetadata(
            format=format,
            width=processed_image.shape[1] if len(processed_image.shape) > 1 else None,
            height=processed_image.shape[0] if len(processed_image.shape) > 1 else None,
            duration=None,
            bitrate=None,
            codec=format.upper(),
            size_bytes=len(image_data) if isinstance(image_data, bytes) else processed_image.nbytes,
            sha256=sha256,
            timestamp=datetime.now().timestamp()
        )
        
        # Store metadata
        self.processed_files[sha256] = media_metadata
        self.format_statistics[format] = self.format_statistics.get(format, 0) + 1
        
        return media_metadata, processed_image
    
    def process_video(
        self,
        video_data: Union[bytes, Dict],
        format: str = "mp4_h264",
        metadata: Optional[Dict] = None
    ) -> Tuple[MediaMetadata, Dict]:
        """
        Process video data for social media.
        
        Args:
            video_data: Video data (bytes or dict with frames)
            format: Video format (mp4_h264, mp4_h265, webm)
            metadata: Additional metadata
            
        Returns:
            Tuple of (MediaMetadata, processed_video)
        """
        # Calculate SHA256
        sha256 = self._calculate_sha256(str(video_data).encode())
        
        # Process video
        if isinstance(video_data, bytes):
            processed_video = {'raw_data': video_data, 'format': format}
        else:
            processed_video = video_data
        
        # Extract video properties
        width = metadata.get('width') if metadata else None
        height = metadata.get('height') if metadata else None
        duration = metadata.get('duration') if metadata else None
        bitrate = metadata.get('bitrate') if metadata else None
        
        # Determine codec
        codec = "H.264/AVC" if format == "mp4_h264" else "H.265/HEVC" if format == "mp4_h265" else format.upper()
        
        media_metadata = MediaMetadata(
            format=format,
            width=width,
            height=height,
            duration=duration,
            bitrate=bitrate,
            codec=codec,
            size_bytes=len(video_data) if isinstance(video_data, bytes) else len(str(video_data).encode()),
            sha256=sha256,
            timestamp=datetime.now().timestamp()
        )
        
        self.processed_files[sha256] = media_metadata
        self.format_statistics[format] = self.format_statistics.get(format, 0) + 1
        
        return media_metadata, processed_video
    
    def process_audio(
        self,
        audio_data: Union[bytes, np.ndarray],
        format: str = "aac",
        metadata: Optional[Dict] = None
    ) -> Tuple[MediaMetadata, Union[bytes, np.ndarray]]:
        """
        Process audio data for social media.
        
        Args:
            audio_data: Audio data (bytes or numpy array)
            format: Audio format (mp3, aac, wav, aac_in_mp4)
            metadata: Additional metadata
            
        Returns:
            Tuple of (MediaMetadata, processed_audio)
        """
        # Calculate SHA256
        sha256 = self._calculate_sha256(audio_data if isinstance(audio_data, bytes) else audio_data.tobytes())
        
        # Process audio
        if isinstance(audio_data, bytes):
            processed_audio = audio_data
        else:
            processed_audio = audio_data
        
        # Extract audio properties
        duration = metadata.get('duration') if metadata else None
        bitrate = metadata.get('bitrate') if metadata else None
        sample_rate = metadata.get('sample_rate') if metadata else None
        
        media_metadata = MediaMetadata(
            format=format,
            width=None,
            height=None,
            duration=duration,
            bitrate=bitrate,
            codec=format.upper(),
            size_bytes=len(audio_data) if isinstance(audio_data, bytes) else audio_data.nbytes,
            sha256=sha256,
            timestamp=datetime.now().timestamp()
        )
        
        self.processed_files[sha256] = media_metadata
        self.format_statistics[format] = self.format_statistics.get(format, 0) + 1
        
        return media_metadata, processed_audio
    
    def process_text(
        self,
        text_data: str,
        metadata: Optional[Dict] = None
    ) -> Tuple[MediaMetadata, str]:
        """
        Process text data for social media (plain text + emojis).
        
        Args:
            text_data: Text data
            metadata: Additional metadata
            
        Returns:
            Tuple of (MediaMetadata, processed_text)
        """
        # Calculate SHA256
        sha256 = self._calculate_sha256(text_data.encode())
        
        # Process text (handle emojis, rich text)
        processed_text = self._process_text_content(text_data)
        
        media_metadata = MediaMetadata(
            format="text",
            width=None,
            height=None,
            duration=None,
            bitrate=None,
            codec="UTF-8",
            size_bytes=len(text_data.encode()),
            sha256=sha256,
            timestamp=datetime.now().timestamp()
        )
        
        self.processed_files[sha256] = media_metadata
        self.format_statistics["text"] = self.format_statistics.get("text", 0) + 1
        
        return media_metadata, processed_text
    
    def process_sticker(
        self,
        sticker_data: Union[bytes, np.ndarray],
        format: str = "webp",
        animated: bool = False,
        metadata: Optional[Dict] = None
    ) -> Tuple[MediaMetadata, Union[bytes, np.ndarray]]:
        """
        Process sticker/overlay data for social media.
        
        Args:
            sticker_data: Sticker data
            format: Format (webp, png, gif)
            animated: Whether sticker is animated
            metadata: Additional metadata
            
        Returns:
            Tuple of (MediaMetadata, processed_sticker)
        """
        # Calculate SHA256
        sha256 = self._calculate_sha256(sticker_data if isinstance(sticker_data, bytes) else sticker_data.tobytes())
        
        # Process sticker
        if isinstance(sticker_data, bytes):
            processed_sticker = sticker_data
        else:
            processed_sticker = sticker_data
        
        media_metadata = MediaMetadata(
            format=f"{format}_animated" if animated else format,
            width=metadata.get('width') if metadata else None,
            height=metadata.get('height') if metadata else None,
            duration=None,
            bitrate=None,
            codec=format.upper(),
            size_bytes=len(sticker_data) if isinstance(sticker_data, bytes) else sticker_data.nbytes,
            sha256=sha256,
            timestamp=datetime.now().timestamp()
        )
        
        self.processed_files[sha256] = media_metadata
        format_key = f"{format}_animated" if animated else format
        self.format_statistics[format_key] = self.format_statistics.get(format_key, 0) + 1
        
        return media_metadata, processed_sticker
    
    def _decode_image_bytes(self, image_bytes: bytes, format: str) -> np.ndarray:
        """Decode image bytes to numpy array (simplified)."""
        # In real implementation, use PIL or cv2
        return np.frombuffer(image_bytes, dtype=np.uint8)
    
    def _process_text_content(self, text: str) -> str:
        """Process text content (handle emojis, rich text)."""
        # In real implementation, handle emoji normalization, HTML parsing
        return text
    
    def _calculate_sha256(self, data: bytes) -> str:
        """
        Calculate SHA256 hash of data.
        
        Args:
            data: Data to hash
            
        Returns:
            SHA256 hash string
        """
        return hashlib.sha256(data).hexdigest()
    
    def get_media_by_sha(self, sha256: str) -> Optional[MediaMetadata]:
        """
        Get media metadata by SHA256 hash.
        
        Args:
            sha256: SHA256 hash
            
        Returns:
            MediaMetadata or None
        """
        return self.processed_files.get(sha256)
    
    def get_format_statistics(self) -> Dict[str, int]:
        """
        Get statistics about processed formats.
        
        Returns:
            Dictionary with format counts
        """
        return self.format_statistics.copy()
    
    def convert_format(
        self,
        media_data: Union[bytes, np.ndarray],
        from_format: str,
        to_format: str
    ) -> Tuple[MediaMetadata, Union[bytes, np.ndarray]]:
        """
        Convert media from one format to another.
        
        Args:
            media_data: Media data to convert
            from_format: Source format
            to_format: Target format
            
        Returns:
            Tuple of (MediaMetadata, converted_data)
        """
        # In real implementation, use format conversion libraries
        # For now, return as-is with updated metadata
        sha256 = self._calculate_sha256(media_data if isinstance(media_data, bytes) else media_data.tobytes())
        
        media_metadata = MediaMetadata(
            format=to_format,
            width=None,
            height=None,
            duration=None,
            bitrate=None,
            codec=to_format.upper(),
            size_bytes=len(media_data) if isinstance(media_data, bytes) else media_data.nbytes,
            sha256=sha256,
            timestamp=datetime.now().timestamp()
        )
        
        return media_metadata, media_data
