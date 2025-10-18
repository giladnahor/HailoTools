#!/usr/bin/env python3
"""
Breakpoint debugging utilities for video processing pipelines.

This module provides utilities to set conditional breakpoints in video
processing pipelines, allowing developers to debug specific frames
or frame intervals.
"""

from typing import Callable, Optional

try:
    import ipdb
    IPDB_AVAILABLE = True
except ImportError:
    IPDB_AVAILABLE = False

try:
    # Importing VideoFrame before importing GST is required
    from gsthailo import VideoFrame
    from gi.repository import Gst
    HAILO_AVAILABLE = True
except ImportError:
    HAILO_AVAILABLE = False
    VideoFrame = Gst = None


class BreakpointFilter:
    """
    A filter that provides conditional breakpoints for video frame debugging.
    
    This filter allows setting breakpoints every N frames, which is useful
    for debugging video processing pipelines without stopping on every frame.
    """
    
    def __init__(self, n_frames: int = 1, enable_ipdb: bool = True):
        """
        Initialize the breakpoint filter.
        
        Args:
            n_frames: Break every N frames (1 = every frame, 0 = disabled).
            enable_ipdb: Whether to use ipdb for interactive debugging.
        """
        self.n_frames = n_frames
        self.enable_ipdb = enable_ipdb and IPDB_AVAILABLE
        self.counter = 0
        
        if enable_ipdb and not IPDB_AVAILABLE:
            print("Warning: ipdb not available, breakpoints will only print messages")
    
    def should_break(self) -> bool:
        """
        Check if a breakpoint should be triggered on this frame.
        
        Returns:
            bool: True if breakpoint should be triggered, False otherwise.
        """
        if self.n_frames <= 0:
            return False
        
        self.counter += 1
        if self.counter >= self.n_frames:
            self.counter = 0
            return True
        return False
    
    def process_frame(self, video_frame: Optional["VideoFrame"] = None) -> "Gst.FlowReturn":
        """
        Process a frame and potentially trigger a breakpoint.
        
        Args:
            video_frame: The video frame being processed (optional).
            
        Returns:
            Gst.FlowReturn: GStreamer flow return status.
        """
        if self.should_break():
            if self.enable_ipdb:
                print(f"Breakpoint triggered at frame {self.get_total_frames()}")
                ipdb.set_trace()
            else:
                print(f"Debug point reached at frame {self.get_total_frames()}")
        
        if HAILO_AVAILABLE:
            return Gst.FlowReturn.OK
        else:
            return None
    
    def update_interval(self, new_n_frames: int) -> None:
        """
        Update the breakpoint interval.
        
        Args:
            new_n_frames: New interval for breakpoints (0 to disable).
        """
        self.n_frames = new_n_frames
        self.counter = 0  # Reset counter
    
    def get_total_frames(self) -> int:
        """
        Get the total number of frames processed.
        
        Returns:
            int: Total frame count across all breakpoint intervals.
        """
        # This is an approximation based on breakpoint intervals
        return (self.counter + 
                (self.n_frames if self.n_frames > 0 else 1) * 
                getattr(self, '_breakpoint_count', 0))


# Global instance for backward compatibility
_global_filter = BreakpointFilter()


def create_frame_counter(n_frames: int = 1) -> Callable[[], bool]:
    """
    Create a frame counter function that returns True every N frames.
    
    Args:
        n_frames: Number of frames between True returns.
        
    Returns:
        function: A function that returns True every N frames.
    """
    counter = 0
    
    def helper() -> bool:
        nonlocal counter
        if n_frames <= 0:
            return False
        
        counter += 1
        if counter >= n_frames:
            counter = 0
            return True
        return False
    
    return helper


def breakpoint_every_n_frames(n_frames: int = 1) -> None:
    """
    Set a breakpoint every N frames using the global filter.
    
    This function maintains a global frame counter and triggers breakpoints
    at the specified interval.
    
    Args:
        n_frames: Break every N frames (1 = every frame, 0 = disabled).
        
    Note:
        You can call update_n_frames(new_value) from the ipdb prompt to
        change the interval during debugging.
    """
    global _global_filter
    
    if _global_filter.n_frames != n_frames:
        _global_filter.update_interval(n_frames)
    
    _global_filter.process_frame()


def update_n_frames(new_value: int) -> None:
    """
    Update the global breakpoint interval.
    
    This function can be called from the ipdb prompt to change the
    breakpoint frequency during debugging.
    
    Args:
        new_value: New interval for breakpoints (0 to disable).
    """
    global _global_filter
    _global_filter.update_interval(new_value)
    print(f"Updated breakpoint interval to {new_value} frames")


def set_breakpoint_every_n_frames() -> None:
    """
    Trigger a conditional breakpoint using the global filter.
    
    This is the main function to call in your code for debugging.
    The breakpoint will only trigger based on the current interval setting.
    """
    global _global_filter
    _global_filter.process_frame()


def run(video_frame: "VideoFrame") -> "Gst.FlowReturn":
    """
    GStreamer plugin entry point for breakpoint debugging.
    
    This is the main entry point called by GStreamer when using this
    filter in a pipeline.
    
    Args:
        video_frame: The video frame to process.
        
    Returns:
        Gst.FlowReturn: GStreamer flow return status.
    """
    if not HAILO_AVAILABLE:
        raise ImportError("Hailo platform not available")
    
    set_breakpoint_every_n_frames()
    return Gst.FlowReturn.OK


# Backward compatibility
every_n_frames = create_frame_counter
debug_launch = create_frame_counter(1)
