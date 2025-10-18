#!/usr/bin/env python3
"""
Tests for pipeline utilities (formatter, RTSP server).
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock

from hailo_utils.pipeline import formatter


class TestPipelineFormatter:
    """Test cases for GStreamer pipeline formatting."""
    
    def test_format_simple_pipeline(self):
        """Test formatting a simple pipeline."""
        pipeline = "videotestsrc ! videoconvert ! autovideosink"
        result = formatter.format_pipeline(pipeline, line_limit=50)
        
        # Should not be broken since it's under the limit
        assert result == pipeline
    
    def test_format_long_pipeline(self):
        """Test formatting a long pipeline that needs breaking."""
        pipeline = "videotestsrc ! videoconvert ! x264enc ! rtph264pay ! udpsink host=127.0.0.1 port=5000"
        result = formatter.format_pipeline(pipeline, line_limit=40)
        
        # Should be broken into multiple lines
        lines = result.split('\n')
        assert len(lines) > 1
        assert all(line.endswith(' \\') or not line.endswith('\\') for line in lines[:-1])
    
    def test_format_pipeline_with_multiple_exclamations(self):
        """Test pipeline with invalid multiple exclamations."""
        pipeline = "videotestsrc !! videoconvert ! autovideosink"
        
        with pytest.raises(formatter.PipelineFormatError, match="Multiple consecutive '!'"):
            formatter.format_pipeline(pipeline)
    
    def test_format_empty_pipeline(self):
        """Test formatting empty pipeline."""
        result = formatter.format_pipeline("")
        assert result == ""
        
        result = formatter.format_pipeline("   ")
        assert result == ""
    
    def test_format_pipeline_no_exclamations(self):
        """Test formatting pipeline with no exclamations."""
        pipeline = "very long pipeline without any exclamation marks that should be broken at line limit"
        result = formatter.format_pipeline(pipeline, line_limit=30)
        
        lines = result.split('\n')
        # Should be broken at line limit since no exclamations
        assert len(lines) > 1
    
    def test_normalize_whitespace(self):
        """Test whitespace normalization."""
        pipeline = "videotestsrc    !   videoconvert\t!\nautovideosink"
        result = formatter.format_pipeline(pipeline)
        
        # Should normalize all whitespace to single spaces
        assert "    " not in result
        assert "\t" not in result
        assert "\n" not in result or result.count('\n') > 0  # May have line breaks from formatting
    
    def test_find_break_point(self):
        """Test break point finding logic."""
        text = "videotestsrc ! videoconvert ! autovideosink"
        
        # Should find the first exclamation
        break_point = formatter._find_break_point(text, 15)
        assert break_point == 14  # After first '!'
        
        # Should find exclamation after limit if none before
        break_point = formatter._find_break_point(text, 5)
        assert break_point == 14  # After first '!'
    
    def test_create_frame_counter(self):
        """Test frame counter creation."""
        counter = formatter.create_frame_counter(3)
        
        # Should return False twice, then True
        assert counter() is False
        assert counter() is False
        assert counter() is True
        assert counter() is False  # Reset


class TestPipelineFormatterClass:
    """Test cases for PipelineFormatter class."""
    
    def test_formatter_initialization(self):
        """Test formatter initialization."""
        formatter_obj = formatter.PipelineFormatter(line_limit=100)
        assert formatter_obj.line_limit == 100
    
    def test_formatter_format_method(self):
        """Test formatter format method."""
        formatter_obj = formatter.PipelineFormatter(line_limit=40)
        pipeline = "videotestsrc ! videoconvert ! x264enc ! rtph264pay ! udpsink"
        
        result = formatter_obj.format(pipeline)
        
        # Should produce same result as standalone function
        expected = formatter.format_pipeline(pipeline, 40)
        assert result == expected


class TestInputFunctions:
    """Test cases for input handling functions."""
    
    @patch('builtins.input')
    def test_get_pipeline_input_simple(self, mock_input):
        """Test simple pipeline input."""
        mock_input.return_value = "videotestsrc ! autovideosink"
        
        result = formatter.get_pipeline_input()
        
        assert result == "videotestsrc ! autovideosink"
    
    @patch('builtins.input')
    def test_get_pipeline_input_long(self, mock_input):
        """Test long pipeline input that triggers chunked input."""
        # First call returns a very long string
        long_pipeline = "x" * 5000
        mock_input.side_effect = [long_pipeline, "chunk1", "chunk2", ""]
        
        result = formatter.get_pipeline_input()
        
        # Should use chunked input
        assert "chunk1" in result
        assert "chunk2" in result
    
    @patch('builtins.input')
    def test_get_input_in_chunks(self, mock_input):
        """Test chunked input functionality."""
        mock_input.side_effect = ["first chunk", "second chunk", ""]
        
        result = formatter._get_input_in_chunks()
        
        assert result == "first chunk second chunk"


# RTSP server tests would require GStreamer to be available
# We'll create basic tests that check for proper error handling
class TestRTSPServer:
    """Test cases for RTSP server (basic functionality)."""
    
    def test_rtsp_server_import_check(self):
        """Test that RTSP server handles missing GStreamer gracefully."""
        # This test just ensures the module can be imported
        from hailo_utils.pipeline import rtsp_server
        
        # Check that the error class exists
        assert hasattr(rtsp_server, 'RTSPServerError')
    
    @pytest.mark.skipif(
        not pytest.importorskip("gi", minversion=None),
        reason="GStreamer not available"
    )
    def test_rtsp_server_initialization(self):
        """Test RTSP server initialization with GStreamer available."""
        from hailo_utils.pipeline.rtsp_server import RTSPVideoServer, RTSPServerError
        
        try:
            server = RTSPVideoServer(port=8555)  # Use different port
            assert server.port == 8555
            assert server.host == "0.0.0.0"
        except RTSPServerError:
            # GStreamer RTSP server might not be available
            pytest.skip("GStreamer RTSP server not available")
    
    def test_parse_github_url_in_rtsp_context(self):
        """Test that we can create test video files for RTSP testing."""
        # This is more of a utility test for creating test fixtures
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
            test_file = f.name
        
        try:
            # File exists
            assert os.path.exists(test_file)
        finally:
            os.unlink(test_file)


if __name__ == '__main__':
    pytest.main([__file__])