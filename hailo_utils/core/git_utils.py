#!/usr/bin/env python3
"""
Git utilities for extracting repository information.

This module provides functions to get git repository details including
remote URL, branch information, and repository metadata.
"""

import subprocess
from typing import Optional, Tuple, Dict, Any


def get_git_remote_url() -> Optional[str]:
    """
    Get the remote URL of the current git repository.
    
    Returns:
        str: The remote URL if found, None otherwise.
    """
    try:
        result = subprocess.run(
            ["git", "remote", "-v"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        remote_url = result.stdout.split()[1]  # The first URL in the output
        return remote_url
    except subprocess.CalledProcessError:
        return None


def extract_repo_name(url: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Extract repository name and protocol from a git URL.
    
    Args:
        url: Git repository URL (SSH or HTTPS format).
        
    Returns:
        tuple: (repo_name, protocol, full_url) or (None, None, None) if invalid.
    """
    if not url:
        return None, None, None
        
    if url.startswith("git@"):
        repo_name = url.split(":")[1].split(".git")[0]
        protocol = "SSH"
    elif url.startswith("https://"):
        repo_name = url.split("/")[4].split(".git")[0]
        protocol = "HTTPS"
    else:
        return None, None, None
        
    return repo_name, protocol, url


def get_git_branch() -> Optional[str]:
    """
    Get the current git branch name.
    
    Returns:
        str: Current branch name if found, None otherwise.
    """
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        branch = result.stdout.strip()
        return branch
    except subprocess.CalledProcessError:
        return None


def get_git_info() -> Dict[str, Any]:
    """
    Get comprehensive git repository information.
    
    Returns:
        dict: Dictionary containing repository information with keys:
            - name: Repository name
            - branch: Current branch
            - url: Remote URL
            - protocol: Git protocol (SSH/HTTPS)
    """
    remote_url = get_git_remote_url()
    if not remote_url:
        return {
            "name": None,
            "branch": None,
            "url": None,
            "protocol": None,
            "error": "Not a git repository or no remote configured"
        }
    
    repo_name, protocol, full_url = extract_repo_name(remote_url)
    branch = get_git_branch()
    
    return {
        "name": repo_name,
        "branch": branch,
        "url": full_url,
        "protocol": protocol
    }


def main() -> None:
    """Command line interface for git utilities."""
    info = get_git_info()
    
    if info.get("error"):
        print(f"Error: {info['error']}")
        return
    
    if all(info[key] for key in ["name", "protocol", "url", "branch"]):
        print(f"Repository Name: {info['name']}")
        print(f"Protocol: {info['protocol']}")
        print(f"Full URL: {info['url']}")
        print(f"Current Branch: {info['branch']}")
    else:
        print("Error: Could not extract complete repository information")


if __name__ == "__main__":
    main()
