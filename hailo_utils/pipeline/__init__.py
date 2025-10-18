"""
Pipeline utilities for GStreamer pipeline management and RTSP streaming.
"""

from .formatter import format_pipeline, PipelineFormatter

# Import RTSP components conditionally
try:
    from .rtsp_server import RTSPVideoServer, VideoFileRtspMediaFactory
except ImportError:
    # GStreamer not available, provide placeholder
    class RTSPVideoServer:
        def __init__(self, *args, **kwargs):
            raise ImportError("GStreamer not available for RTSP server functionality")
    
    class VideoFileRtspMediaFactory:
        def __init__(self, *args, **kwargs):
            raise ImportError("GStreamer not available for RTSP server functionality")

__all__ = [
    "format_pipeline",
    "PipelineFormatter", 
    "RTSPVideoServer",
    "VideoFileRtspMediaFactory",
]