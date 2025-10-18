#!/usr/bin/env python3
"""
Aspect ratio correction filter for Hailo video processing.

This module provides filters to correct bounding box coordinates when the
inference image has a different aspect ratio than the original video.
"""

from typing import Optional

try:
    import hailo
    # Importing VideoFrame before importing GST is required
    from gsthailo import VideoFrame
    from gi.repository import Gst
    HAILO_AVAILABLE = True
except ImportError:
    HAILO_AVAILABLE = False
    hailo = VideoFrame = Gst = None


class AspectRatioFilter:
    """
    Filter for correcting aspect ratio of detection bounding boxes.
    
    This filter corrects bounding box coordinates when the inference is performed
    on a square (1:1) image that was created by letterboxing a 16:9 video.
    """
    
    def __init__(self, original_aspect_ratio: float = 16/9):
        """
        Initialize the aspect ratio filter.
        
        Args:
            original_aspect_ratio: The original video aspect ratio (default: 16/9).
        """
        if not HAILO_AVAILABLE:
            raise ImportError(
                "Hailo platform not available. Please ensure hailo and gsthailo "
                "packages are installed."
            )
        
        self.original_aspect_ratio = original_aspect_ratio
        # Calculate borders for letterboxing from 16:9 to 1:1
        self.bottom_border = (1 - (1 / original_aspect_ratio)) / 2
        self.top_border = 1 - self.bottom_border
    
    def process_frame(self, video_frame: "VideoFrame") -> "Gst.FlowReturn":
        """
        Process a video frame to correct aspect ratio of detections.
        
        Args:
            video_frame: The video frame containing detections to correct.
            
        Returns:
            Gst.FlowReturn: GStreamer flow return status.
        """
        return fix_aspect_ratio(
            video_frame, 
            self.bottom_border, 
            self.top_border
        )


def linear_map(x: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
    """
    Map a value from one range to another linearly.
    
    Args:
        x: Input value to map.
        in_min: Minimum of input range.
        in_max: Maximum of input range.
        out_min: Minimum of output range.
        out_max: Maximum of output range.
        
    Returns:
        float: Mapped value in the output range.
    """
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def fix_aspect_ratio(
    video_frame: "VideoFrame", 
    bottom_border: Optional[float] = None,
    top_border: Optional[float] = None
) -> "Gst.FlowReturn":
    """
    Correct aspect ratio of detection bounding boxes in a video frame.
    
    This function scales bounding boxes to fit the original aspect ratio when
    inference was performed on a letterboxed square image.
    
    The transformation assumes:
    - Original aspect ratio: 16:9
    - Inference image aspect ratio: 1:1 with letterbox borders
    
    Letterbox layout:
    |----------------------|
    |    (black border)    |  <- top border
    |                      |
    |------top_border------|
    |                      |
    |     scaled image     |  <- actual content
    |                      |
    |----bottom_border-----|
    |                      |
    |    (black border)    |  <- bottom border
    |----------------------|
    
    Args:
        video_frame: The video frame containing detections to correct.
        bottom_border: Bottom border ratio (default: calculated for 16:9 to 1:1).
        top_border: Top border ratio (default: calculated for 16:9 to 1:1).
        
    Returns:
        Gst.FlowReturn: GStreamer flow return status (OK on success).
    """
    if not HAILO_AVAILABLE:
        raise ImportError("Hailo platform not available")
    
    # Calculate default borders for 16:9 to 1:1 letterboxing
    if bottom_border is None:
        bottom_border = (1 - 9/16) / 2
    if top_border is None:
        top_border = 1 - bottom_border
    
    # Get all detections from the frame
    detections = video_frame.roi.get_objects_typed(hailo.HAILO_DETECTION)
    
    for detection in detections:
        bbox = detection.get_bbox()
        
        # Map Y coordinates from letterboxed space to original space
        ymin = linear_map(bbox.ymin(), bottom_border, top_border, 0, 1)
        ymax = linear_map(bbox.ymax(), bottom_border, top_border, 0, 1)
        height = ymax - ymin
        
        # Create corrected bounding box (X coordinates unchanged)
        new_bbox = hailo.HailoBBox(bbox.xmin(), ymin, bbox.width(), height)
        detection.set_bbox(new_bbox)
    
    return Gst.FlowReturn.OK


def run(video_frame: "VideoFrame") -> "Gst.FlowReturn":
    """
    GStreamer plugin entry point for aspect ratio correction.
    
    This is the main entry point called by GStreamer when using this
    filter in a pipeline.
    
    Args:
        video_frame: The video frame to process.
        
    Returns:
        Gst.FlowReturn: GStreamer flow return status.
    """
    return fix_aspect_ratio(video_frame)
