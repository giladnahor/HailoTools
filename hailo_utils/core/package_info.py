#!/usr/bin/env python3
"""
Package information utilities for TAPPAS and Hailo packages.

This module provides functions to get TAPPAS workspace configuration,
version information, and library paths from both environment variables
and pkg-config.
"""

import subprocess
import os
from typing import Dict, Optional


class TappasConfigError(Exception):
    """Exception raised when TAPPAS configuration cannot be determined."""
    pass


def get_tappas_info(package_name: str = "hailo_tappas") -> Dict[str, str]:
    """
    Get TAPPAS workspace and version information.
    
    This function first checks environment variables (TAPPAS_WORKSPACE, 
    TAPPAS_LIBDIR, TAPPAS_VERSION). If they are not set, it uses pkg-config 
    to get the data from the pkg-config file.
    
    Args:
        package_name: Name of the package to query (default: "hailo_tappas").
        
    Returns:
        dict: Dictionary containing TAPPAS configuration with keys:
            - tappas_workspace: Workspace directory path
            - version: TAPPAS version
            - libdir: Library directory path
            
    Raises:
        TappasConfigError: If configuration cannot be determined from either
            environment variables or pkg-config.
    """
    info = {}
    
    try:
        # Get the tappas_workspace environment variable
        tappas_workspace = os.environ.get("TAPPAS_WORKSPACE", "")
        if not tappas_workspace:
            # Get the tappas_workspace variable from pkg-config
            tappas_workspace = subprocess.check_output(
                ['pkg-config', '--variable=tappas_workspace', package_name], 
                text=True
            ).strip()
        info['tappas_workspace'] = tappas_workspace
        
        # Get the version
        tappas_version = os.environ.get("TAPPAS_VERSION", "")
        if not tappas_version:
            tappas_version = subprocess.check_output(
                ['pkg-config', '--modversion', package_name], 
                text=True
            ).strip()
        info['version'] = tappas_version
        
        # Get the libdir
        tappas_libdir = os.environ.get("TAPPAS_LIBDIR", "")
        if not tappas_libdir:
            tappas_libdir = subprocess.check_output(
                ['pkg-config', '--variable=tappas_libdir', package_name], 
                text=True
            ).strip()
        info['libdir'] = tappas_libdir

    except subprocess.CalledProcessError as e:
        raise TappasConfigError(
            "TAPPAS configuration not found. Please ensure that:\n"
            "1. TAPPAS environment variables are set (TAPPAS_WORKSPACE, TAPPAS_VERSION, TAPPAS_LIBDIR), OR\n"
            "2. pkg-config can find hailo_tappas.pc file\n"
            "3. PKG_CONFIG_PATH includes /opt/hailo/tappas/pkgconfig\n"
            f"Original error: {e}"
        ) from e
    
    return info


def check_tappas_environment() -> bool:
    """
    Check if TAPPAS environment is properly configured.
    
    Returns:
        bool: True if TAPPAS is configured, False otherwise.
    """
    try:
        get_tappas_info()
        return True
    except TappasConfigError:
        return False


def print_tappas_info(package_name: str = "hailo_tappas") -> None:
    """
    Print TAPPAS configuration information to stdout.
    
    Args:
        package_name: Name of the package to query.
    """
    try:
        info = get_tappas_info(package_name)
        print(f"Using TAPPAS_WORKSPACE: {info['tappas_workspace']}")
        print(f"TAPPAS_LIBDIR: {info['libdir']}")
        print(f"TAPPAS_VERSION: {info['version']}")
    except TappasConfigError as e:
        print(f"Error: {e}")


def main() -> None:
    """Command line interface for package information utilities."""
    package_name = "hailo_tappas"
    print_tappas_info(package_name)


if __name__ == "__main__":
    main()
