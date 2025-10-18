#!/usr/bin/env python3
"""
GStreamer pipeline formatting utilities.

This module provides functions to format long GStreamer pipelines for better
readability by breaking them into multiple lines at appropriate breakpoints.
"""

import re
from typing import List


class PipelineFormatError(Exception):
    """Exception raised when pipeline formatting fails."""
    pass


class PipelineFormatter:
    """
    A class for formatting GStreamer pipelines.
    
    This formatter breaks long pipelines into multiple lines at element
    boundaries (marked by '!') to improve readability.
    """
    
    def __init__(self, line_limit: int = 80):
        """
        Initialize the formatter.
        
        Args:
            line_limit: Maximum line length before breaking (default: 80).
        """
        self.line_limit = line_limit
    
    def format(self, pipeline: str) -> str:
        """
        Format a GStreamer pipeline string.
        
        Args:
            pipeline: The GStreamer pipeline string to format.
            
        Returns:
            str: The formatted pipeline string with line breaks.
            
        Raises:
            PipelineFormatError: If the pipeline contains formatting errors.
        """
        return format_pipeline(pipeline, self.line_limit)


def format_pipeline(pipeline: str, line_limit: int = 80) -> str:
    """
    Format a GStreamer pipeline for better readability.
    
    This function:
    1. Normalizes whitespace in the pipeline
    2. Validates the pipeline structure
    3. Breaks long lines at element boundaries ('!' characters)
    4. Adds line continuation characters ('\')
    
    Args:
        pipeline: The GStreamer pipeline string to format.
        line_limit: Maximum line length before breaking (default: 80).
        
    Returns:
        str: The formatted pipeline string with appropriate line breaks.
        
    Raises:
        PipelineFormatError: If the pipeline contains multiple consecutive '!' 
            characters or other formatting issues.
        
    Example:
        >>> pipeline = "videotestsrc ! videoconvert ! x264enc ! rtph264pay ! udpsink"
        >>> formatted = format_pipeline(pipeline, 40)
        >>> print(formatted)
        videotestsrc ! videoconvert ! x264enc ! \\
        rtph264pay ! udpsink
    """
    if not pipeline or not pipeline.strip():
        return ""
    
    # Remove multiple spaces and tabs, normalize whitespace
    formatted_pipeline = re.sub(r'\s+', ' ', pipeline.strip())

    # Check for multiple consecutive exclamation marks (invalid GStreamer syntax)
    if re.search(r'!\s*!', formatted_pipeline):
        raise PipelineFormatError(
            "Invalid pipeline: Multiple consecutive '!' found. "
            "Each '!' should separate exactly two elements."
        )

    # Break into multiple lines if too long
    broken_lines = []
    remaining = formatted_pipeline
    
    while remaining:
        if len(remaining) <= line_limit:
            broken_lines.append(remaining)
            break

        # Find the best break point (last '!' before line_limit or first after)
        break_index = _find_break_point(remaining, line_limit)
        
        if break_index == -1:
            # No '!' found, break at line_limit or take the rest
            if len(remaining) > line_limit:
                break_index = line_limit
            else:
                break_index = len(remaining)
        
        # Split the line at the break_index and add a backslash
        line = remaining[:break_index].rstrip()
        if break_index < len(remaining):
            line += " \\"
        broken_lines.append(line)
        
        # Move to the next part
        remaining = remaining[break_index:].lstrip()
        if remaining.startswith('!'):
            remaining = remaining[1:].lstrip()
    
    return '\n'.join(broken_lines)


def _find_break_point(text: str, line_limit: int) -> int:
    """
    Find the best break point in a pipeline string.
    
    Args:
        text: The text to find a break point in.
        line_limit: The preferred line length limit.
        
    Returns:
        int: Index of the break point, or -1 if no good break point found.
    """
    # Look for the last '!' before line_limit
    last_exclamation_before = -1
    for i in range(min(line_limit, len(text))):
        if text[i] == '!':
            last_exclamation_before = i + 1
    
    if last_exclamation_before != -1:
        return last_exclamation_before
    
    # If no '!' before line_limit, look for the first one after
    for i in range(line_limit, len(text)):
        if text[i] == '!':
            return i + 1
    
    # No '!' found at all
    return -1


def get_pipeline_input() -> str:
    """
    Get pipeline input from user via command line interface.
    
    Handles both single-line and multi-line input for very long pipelines.
    
    Returns:
        str: The complete pipeline string entered by the user.
    """
    print("Enter your GStreamer pipeline (press Enter to finish):")
    input_data = input().strip()
    
    # Check if the input is likely truncated (very long single line)
    if len(input_data) >= 4095:
        print("Input is too long. Please enter the input in chunks.")
        print("Press Enter on an empty line to finish.")
        input_data = _get_input_in_chunks()
    
    return input_data


def _get_input_in_chunks() -> str:
    """
    Get multi-line input from user, terminated by empty line.
    
    Returns:
        str: The concatenated input from all chunks.
    """
    chunks = []
    while True:
        chunk = input()
        if chunk == "":
            break
        chunks.append(chunk)
    return ' '.join(chunks)


def main() -> None:
    """Command line interface for pipeline formatting."""
    try:
        # Get the pipeline input
        input_pipeline = get_pipeline_input()
        
        if not input_pipeline:
            print("No pipeline provided.")
            return
        
        # Format the pipeline
        formatted_pipeline = format_pipeline(input_pipeline)
        print("\nFormatted Pipeline:")
        print(formatted_pipeline)
        
    except PipelineFormatError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
