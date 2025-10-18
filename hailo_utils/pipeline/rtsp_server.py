#!/usr/bin/env python3
"""
RTSP video file server using GStreamer.

This module provides an RTSP server that can stream video files over the network.
It supports multiple video files streamed simultaneously on different endpoints.

Requirements:
    - GStreamer 1.0 with RTSP server support
    - PyGObject for Python GStreamer bindings
    
System packages (Ubuntu/Debian):
    sudo apt-get install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev
    sudo apt-get install gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly gstreamer1.0-plugins-bad
    sudo apt-get install libgstrtspserver-1.0-dev

Usage:
    python3 rtsp_server.py <video-file-path> [<video-file-path> ...]
    
    The video files will be streamed at:
    - rtsp://127.0.0.1:8554/stream1
    - rtsp://127.0.0.1:8554/stream2
    - etc.
    
    View with any RTSP client (VLC, GStreamer, etc.):
    gst-launch-1.0 -v rtspsrc location=rtsp://127.0.0.1:8554/stream1 latency=0 ! \\
        rtph264depay ! avdec_h264 ! videoconvert ! autovideosink
"""

import sys
import os
from typing import List, Optional

try:
    import gi
    gi.require_version('Gst', '1.0')
    gi.require_version('GstRtspServer', '1.0')
    from gi.repository import Gst, GstRtspServer, GObject
    GSTREAMER_AVAILABLE = True
except (ImportError, ValueError) as e:
    GSTREAMER_AVAILABLE = False
    Gst = GstRtspServer = GObject = None


class RTSPServerError(Exception):
    """Exception raised when RTSP server operations fail."""
    pass


if GSTREAMER_AVAILABLE:
    class VideoFileRtspMediaFactory(GstRtspServer.RTSPMediaFactory):
        """
        RTSP Media Factory for streaming video files.
        
        This factory creates GStreamer pipelines that read video files and
        encode them for RTSP streaming using H.264.
        """
        
        def __init__(self, video_path: str):
            """
            Initialize the media factory.
            
            Args:
                video_path: Path to the video file to stream.
                
            Raises:
                RTSPServerError: If the video file doesn't exist.
            """
            if not GSTREAMER_AVAILABLE:
                raise RTSPServerError(
                    "GStreamer not available. Please install PyGObject and GStreamer RTSP server."
                )
            
            if not os.path.exists(video_path):
                raise RTSPServerError(f"Video file not found: {video_path}")
            
            GstRtspServer.RTSPMediaFactory.__init__(self)
            self.video_path = os.path.abspath(video_path)

        def do_create_element(self, url):
            """
            Create the GStreamer pipeline element for this media.
            
            Args:
                url: The RTSP URL being requested.
                
            Returns:
                Gst.Element: The pipeline element for streaming.
            """
            # Create pipeline: file -> decode -> convert -> scale -> encode -> RTP payload
            src_pipeline = (
                f"filesrc location={self.video_path} ! "
                "decodebin ! videoconvert ! videoscale ! "
                "x264enc tune=zerolatency bitrate=2000 ! "
                "rtph264pay name=pay0 pt=96"
            )
            return Gst.parse_launch(src_pipeline)
else:
    # Placeholder class when GStreamer is not available
    class VideoFileRtspMediaFactory:
        def __init__(self, *args, **kwargs):
            raise RTSPServerError(
                "GStreamer not available. Please install PyGObject and GStreamer RTSP server."
            )


class RTSPVideoServer:
    """
    RTSP video streaming server.
    
    This server can stream multiple video files simultaneously over RTSP.
    Each video file is available at a different endpoint.
    """
    
    def __init__(self, port: int = 8554, host: str = "0.0.0.0"):
        """
        Initialize the RTSP server.
        
        Args:
            port: Port number for the RTSP server (default: 8554).
            host: Host address to bind to (default: "0.0.0.0").
        """
        if not GSTREAMER_AVAILABLE:
            raise RTSPServerError(
                "GStreamer not available. Please install PyGObject and GStreamer RTSP server."
            )
        
        self.port = port
        self.host = host
        self.server = None
        self.mount_points = None
        self.streams = {}
        self._initialized = False
    
    def _initialize(self) -> None:
        """Initialize GStreamer and create the server."""
        if self._initialized:
            return
        
        GObject.threads_init()
        Gst.init(None)

        self.server = GstRtspServer.RTSPServer()
        self.server.set_service(str(self.port))
        self.server.set_address(self.host)
        self.mount_points = self.server.get_mount_points()
        self._initialized = True
    
    def add_stream(self, endpoint: str, video_path: str, shared: bool = True) -> None:
        """
        Add a video stream to the server.
        
        Args:
            endpoint: RTSP endpoint path (e.g., "/stream1").
            video_path: Path to the video file to stream.
            shared: Whether the stream can be shared among multiple clients.
            
        Raises:
            RTSPServerError: If the video file doesn't exist or stream setup fails.
        """
        self._initialize()
        
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
        
        try:
            factory = VideoFileRtspMediaFactory(video_path)
            factory.set_shared(shared)
            self.mount_points.add_factory(endpoint, factory)
            self.streams[endpoint] = video_path
            
        except Exception as e:
            raise RTSPServerError(f"Failed to add stream {endpoint}: {e}") from e
    
    def remove_stream(self, endpoint: str) -> None:
        """
        Remove a stream from the server.
        
        Args:
            endpoint: RTSP endpoint path to remove.
        """
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
        
        if self.mount_points and endpoint in self.streams:
            self.mount_points.remove_factory(endpoint)
            del self.streams[endpoint]
    
    def start(self) -> None:
        """
        Start the RTSP server.
        
        This method blocks until the server is stopped (e.g., by Ctrl+C).
        
        Raises:
            RTSPServerError: If the server fails to start.
        """
        self._initialize()
        
        if not self.streams:
            raise RTSPServerError("No streams configured. Add streams before starting the server.")
        
        try:
            # Attach the server to the default main context
            self.server.attach(None)
            
            # Print stream information
            print(f"RTSP server started on {self.host}:{self.port}")
            for endpoint, video_path in self.streams.items():
                url = f"rtsp://{self.host if self.host != '0.0.0.0' else '127.0.0.1'}:{self.port}{endpoint}"
                print(f"Streaming {video_path} at {url}")
            
            print("Press Ctrl+C to stop the server")
            
            # Start the main loop
            loop = GObject.MainLoop()
            loop.run()
            
        except KeyboardInterrupt:
            print("\nStopping RTSP server...")
        except Exception as e:
            raise RTSPServerError(f"Server error: {e}") from e
    
    def get_stream_urls(self) -> List[str]:
        """
        Get list of all stream URLs.
        
        Returns:
            list: List of RTSP URLs for all configured streams.
        """
        host = self.host if self.host != "0.0.0.0" else "127.0.0.1"
        return [
            f"rtsp://{host}:{self.port}{endpoint}"
            for endpoint in self.streams.keys()
        ]


def create_server_from_files(video_paths: List[str], port: int = 8554) -> RTSPVideoServer:
    """
    Create an RTSP server with video files.
    
    Args:
        video_paths: List of video file paths to stream.
        port: Port number for the RTSP server.
        
    Returns:
        RTSPVideoServer: Configured server ready to start.
    """
    server = RTSPVideoServer(port=port)
    
    for index, video_path in enumerate(video_paths, start=1):
        endpoint = f"/stream{index}"
        server.add_stream(endpoint, video_path)
    
    return server


def main(args: Optional[List[str]] = None) -> int:
    """
    Command line interface for RTSP video server.
    
    Args:
        args: Command line arguments. If None, uses sys.argv.
        
    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    if args is None:
        args = sys.argv
    
    if len(args) < 2:
        print(f"Usage: {args[0]} <video-file-path> [<video-file-path> ...]")
        print("\nExample:")
        print(f"  {args[0]} video1.mp4 video2.mp4")
        print("\nStreams will be available at:")
        print("  rtsp://127.0.0.1:8554/stream1")
        print("  rtsp://127.0.0.1:8554/stream2")
        return 1

    video_paths = args[1:]
    
    # Validate video files
    for video_path in video_paths:
        if not os.path.exists(video_path):
            print(f"Error: Video file not found: {video_path}")
            return 1
    
    try:
        server = create_server_from_files(video_paths)
        server.start()
        return 0
        
    except RTSPServerError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
