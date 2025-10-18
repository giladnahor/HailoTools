#!/usr/bin/env python3
"""
Debug utilities for Hailo video processing pipelines.

This module provides debugging filters and utilities for inspecting
video frames, detections, and pipeline behavior during development.
"""

import time
from typing import Optional, List, Dict, Any

try:
    import hailo
    import numpy as np
    # Importing VideoFrame before importing GST is required
    from gsthailo import VideoFrame
    from gi.repository import Gst
    HAILO_AVAILABLE = True
except ImportError:
    HAILO_AVAILABLE = False
    hailo = VideoFrame = Gst = np = None


class DebugFilter:
    """
    Debug filter for inspecting Hailo video processing pipelines.
    
    This filter provides various debugging capabilities including:
    - Detection inspection and logging
    - Frame delay for manual inspection
    - Mask addition for testing
    """
    
    def __init__(self, enable_breakpoint: bool = False, log_detections: bool = True):
        """
        Initialize the debug filter.
        
        Args:
            enable_breakpoint: Whether to enable interactive debugging breakpoints.
            log_detections: Whether to log detection information to console.
        """
        if not HAILO_AVAILABLE:
            raise ImportError(
                "Hailo platform not available. Please ensure hailo and gsthailo "
                "packages are installed."
            )
        
        self.enable_breakpoint = enable_breakpoint
        self.log_detections = log_detections
        self.frame_count = 0
    
    def process_frame(self, video_frame: "VideoFrame") -> "Gst.FlowReturn":
        """
        Process a video frame for debugging.
        
        Args:
            video_frame: The video frame to debug.
            
        Returns:
            Gst.FlowReturn: GStreamer flow return status.
        """
        self.frame_count += 1
        
        if self.enable_breakpoint:
            return debug_with_breakpoint(video_frame)
        elif self.log_detections:
            return debug_detections(video_frame)
        else:
            return Gst.FlowReturn.OK


def debug_detections(video_frame: "VideoFrame") -> "Gst.FlowReturn":
    """
    Debug detections in a video frame by logging their information.
    
    Args:
        video_frame: The video frame containing detections to debug.
        
    Returns:
        Gst.FlowReturn: GStreamer flow return status.
    """
    if not HAILO_AVAILABLE:
        raise ImportError("Hailo platform not available")
    
    detections = hailo.get_hailo_detections(video_frame.roi)
    
    if detections:
        print(f"Frame contains {len(detections)} detection(s):")
        for i, detection in enumerate(detections):
            label = detection.get_label()
            bbox = detection.get_bbox()
            confidence = detection.get_confidence()
            
            print(f"  Detection {i+1}:")
            print(f"    Label: {label}")
            print(f"    Confidence: {confidence:.3f}")
            print(f"    BBox: x={bbox.xmin():.3f}, y={bbox.ymin():.3f}, "
                  f"w={bbox.width():.3f}, h={bbox.height():.3f}")
    else:
        print("Frame contains no detections")
    
    return Gst.FlowReturn.OK


def debug_with_breakpoint(video_frame: "VideoFrame") -> "Gst.FlowReturn":
    """
    Debug a video frame with an interactive breakpoint.
    
    This function drops into an interactive debugger (ipdb) to allow
    manual inspection of the video frame and its contents.
    
    Args:
        video_frame: The video frame to debug.
        
    Returns:
        Gst.FlowReturn: GStreamer flow return status.
    """
    if not HAILO_AVAILABLE:
        raise ImportError("Hailo platform not available")
    
    try:
        import ipdb
        ipdb.set_trace()
    except ImportError:
        print("ipdb not available, falling back to regular debug")
        return debug_detections(video_frame)
    
    return Gst.FlowReturn.OK


def add_debug_mask(
    video_frame: "VideoFrame",
    xmin: float = 0.05,
    ymin: float = 0.45, 
    width: float = 0.9,
    height: float = 0.52
) -> "Gst.FlowReturn":
    """
    Add a debug mask/tile to a video frame for testing purposes.
    
    Args:
        video_frame: The video frame to add the mask to.
        xmin: Left edge of the mask (normalized 0-1).
        ymin: Top edge of the mask (normalized 0-1).
        width: Width of the mask (normalized 0-1).
        height: Height of the mask (normalized 0-1).
        
    Returns:
        Gst.FlowReturn: GStreamer flow return status.
    """
    if not HAILO_AVAILABLE:
        raise ImportError("Hailo platform not available")
    
    mask_bbox = hailo.HailoBBox(xmin=xmin, ymin=ymin, width=width, height=height)
    mask_tile = hailo.HailoTileROI(mask_bbox, 1, 0.0, 0.0, 0, hailo.SINGLE_SCALE)
    video_frame.roi.add_object(mask_tile)
    
    return Gst.FlowReturn.OK


def add_frame_delay(video_frame: "VideoFrame", delay_seconds: float = 0.2) -> "Gst.FlowReturn":
    """
    Add a delay to frame processing for debugging purposes.
    
    This can be useful for slowing down processing to manually observe
    pipeline behavior or for testing timing-sensitive code.
    
    Args:
        video_frame: The video frame being processed.
        delay_seconds: Delay time in seconds (default: 0.2).
        
    Returns:
        Gst.FlowReturn: GStreamer flow return status.
    """
    time.sleep(delay_seconds)
    return Gst.FlowReturn.OK


def get_frame_info(video_frame: "VideoFrame") -> Dict[str, Any]:
    """
    Extract comprehensive information from a video frame.
    
    Args:
        video_frame: The video frame to analyze.
        
    Returns:
        dict: Dictionary containing frame information including:
            - detection_count: Number of detections
            - detections: List of detection details
            - roi_info: ROI information
    """
    if not HAILO_AVAILABLE:
        raise ImportError("Hailo platform not available")
    
    detections = hailo.get_hailo_detections(video_frame.roi)
    
    detection_details = []
    for detection in detections:
        bbox = detection.get_bbox()
        detection_details.append({
            'label': detection.get_label(),
            'confidence': detection.get_confidence(),
            'bbox': {
                'xmin': bbox.xmin(),
                'ymin': bbox.ymin(),
                'width': bbox.width(),
                'height': bbox.height()
            }
        })
    
    return {
        'detection_count': len(detections),
        'detections': detection_details,
        'roi_info': str(video_frame.roi)
    }


# GStreamer plugin entry points
def run(video_frame: "VideoFrame") -> "Gst.FlowReturn":
    """
    GStreamer plugin entry point for debug processing.
    
    This is the main entry point called by GStreamer when using this
    filter in a pipeline. It enables interactive debugging.
    
    Args:
        video_frame: The video frame to process.
        
    Returns:
        Gst.FlowReturn: GStreamer flow return status.
    """
    return debug_with_breakpoint(video_frame)


def add_mask(video_frame: "VideoFrame") -> "Gst.FlowReturn":
    """
    GStreamer plugin entry point for adding debug masks.
    
    Args:
        video_frame: The video frame to add mask to.
        
    Returns:
        Gst.FlowReturn: GStreamer flow return status.
    """
    return add_debug_mask(video_frame)


def delay(video_frame: "VideoFrame") -> "Gst.FlowReturn":
    """
    GStreamer plugin entry point for adding frame delays.
    
    Args:
        video_frame: The video frame being processed.
        
    Returns:
        Gst.FlowReturn: GStreamer flow return status.
    """
    return add_frame_delay(video_frame)
