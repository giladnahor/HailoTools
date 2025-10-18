"""
Hailo Utilities - A collection of utilities for Hailo AI hardware and GStreamer pipelines.

This package provides tools for:
- GStreamer pipeline formatting and management
- RTSP video streaming
- Hailo hardware monitoring
- Git repository utilities
- Package information extraction
- Video processing filters
"""

__version__ = "0.1.0"
__author__ = "Hailo Utils Contributors"
__email__ = "support@hailo.ai"

# Import main modules for convenience
from . import core, pipeline, filters, downloaders

__all__ = ["core", "pipeline", "filters", "downloaders", "__version__"]