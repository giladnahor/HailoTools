#!/usr/bin/env python3
"""
GitHub directory downloader utility.

This module provides functionality to download specific directories from
GitHub repositories without cloning the entire repository.
"""

import os
import subprocess
import urllib.parse
import tempfile
import shutil
from typing import Optional, Tuple
from pathlib import Path


class GitHubDownloadError(Exception):
    """Exception raised when GitHub download operations fail."""
    pass


class GitHubDownloader:
    """
    A class for downloading directories from GitHub repositories.
    
    This downloader can extract specific directories from GitHub repositories
    by downloading the repository archive and extracting only the needed parts.
    """
    
    def __init__(self, use_curl: bool = False):
        """
        Initialize the GitHub downloader.
        
        Args:
            use_curl: Whether to use curl instead of wget for downloads.
        """
        self.use_curl = use_curl
        self._check_dependencies()
    
    def _check_dependencies(self) -> None:
        """Check if required system dependencies are available."""
        # Check for download tool
        download_tool = 'curl' if self.use_curl else 'wget'
        if shutil.which(download_tool) is None:
            raise GitHubDownloadError(f"{download_tool} not found. Please install {download_tool}.")
        
        # Check for unzip
        if shutil.which('unzip') is None:
            raise GitHubDownloadError("unzip not found. Please install unzip.")
    
    def parse_github_url(self, github_url: str) -> Tuple[str, str, str, str]:
        """
        Parse a GitHub URL to extract repository and directory information.
        
        Args:
            github_url: GitHub URL in the format:
                https://github.com/owner/repo/tree/branch/path/to/directory
                
        Returns:
            tuple: (owner, repo, branch, directory_path)
            
        Raises:
            GitHubDownloadError: If the URL format is invalid.
        """
        try:
            parsed_url = urllib.parse.urlparse(github_url)
            path_parts = parsed_url.path.strip('/').split('/')
            
            # Validate URL structure
            if (len(path_parts) < 5 or 
                parsed_url.netloc != 'github.com' or 
                path_parts[2] != 'tree'):
                raise GitHubDownloadError(
                    "Invalid GitHub URL format. Expected: "
                    "https://github.com/owner/repo/tree/branch/path/to/directory"
                )
            
            owner = path_parts[0]
            repo = path_parts[1]
            branch = path_parts[3]
            directory_path = '/'.join(path_parts[4:]) if len(path_parts) > 4 else ''
            
            return owner, repo, branch, directory_path
            
        except Exception as e:
            raise GitHubDownloadError(f"Failed to parse GitHub URL: {e}") from e
    
    def download_directory(
        self, 
        github_url: str, 
        output_dir: Optional[str] = None,
        preserve_structure: bool = False
    ) -> str:
        """
        Download a specific directory from a GitHub repository.
        
        Args:
            github_url: GitHub URL pointing to the directory to download.
            output_dir: Output directory path. If None, uses the directory name.
            preserve_structure: Whether to preserve the full directory structure.
            
        Returns:
            str: Path to the downloaded directory.
            
        Raises:
            GitHubDownloadError: If download or extraction fails.
        """
        owner, repo, branch, directory_path = self.parse_github_url(github_url)
        
        if not directory_path:
            raise GitHubDownloadError("URL must point to a specific directory, not the repository root")
        
        # Create ZIP download URL
        zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, f"{branch}.zip")
            
            # Download the ZIP file
            self._download_file(zip_url, zip_path)
            
            # Extract the specific directory
            extracted_path = self._extract_directory(
                zip_path, repo, branch, directory_path, temp_dir
            )
            
            # Determine output location
            if output_dir is None:
                output_dir = os.path.basename(directory_path) or f"{repo}-{directory_path.replace('/', '-')}"
            
            # Move to final location
            final_path = os.path.abspath(output_dir)
            if os.path.exists(final_path):
                shutil.rmtree(final_path)
            
            shutil.move(extracted_path, final_path)
            
            return final_path
    
    def _download_file(self, url: str, output_path: str) -> None:
        """Download a file using wget or curl."""
        try:
            if self.use_curl:
                cmd = ['curl', '-L', '-o', output_path, url]
            else:
                cmd = ['wget', '-O', output_path, url]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
        except subprocess.CalledProcessError as e:
            raise GitHubDownloadError(
                f"Failed to download {url}: {e.stderr or e.stdout}"
            ) from e
    
    def _extract_directory(
        self, 
        zip_path: str, 
        repo: str, 
        branch: str, 
        directory_path: str, 
        temp_dir: str
    ) -> str:
        """Extract a specific directory from the downloaded ZIP file."""
        try:
            # Create extraction target
            extract_target = os.path.join(temp_dir, 'extracted')
            os.makedirs(extract_target, exist_ok=True)
            
            # Build the path pattern for unzip
            archive_dir_path = f"{repo}-{branch}/{directory_path}"
            
            # Extract the specific directory
            cmd = ['unzip', '-q', zip_path, f"{archive_dir_path}/*", '-d', extract_target]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                # Try without the /* suffix in case it's a single file
                cmd = ['unzip', '-q', zip_path, archive_dir_path, '-d', extract_target]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Find the extracted directory
            extracted_base = os.path.join(extract_target, f"{repo}-{branch}")
            extracted_dir = os.path.join(extracted_base, directory_path)
            
            if not os.path.exists(extracted_dir):
                raise GitHubDownloadError(f"Directory not found in archive: {directory_path}")
            
            return extracted_dir
            
        except subprocess.CalledProcessError as e:
            raise GitHubDownloadError(
                f"Failed to extract directory {directory_path}: {e.stderr or e.stdout}"
            ) from e


def download_github_directory(
    github_url: str, 
    output_dir: Optional[str] = None,
    use_curl: bool = False
) -> str:
    """
    Download a specific directory from a GitHub repository.
    
    This is a convenience function that creates a GitHubDownloader instance
    and downloads the specified directory.
    
    Args:
        github_url: GitHub URL pointing to the directory to download.
            Format: https://github.com/owner/repo/tree/branch/path/to/directory
        output_dir: Output directory path. If None, uses the directory name.
        use_curl: Whether to use curl instead of wget for downloads.
        
    Returns:
        str: Path to the downloaded directory.
        
    Raises:
        GitHubDownloadError: If download fails.
        
    Example:
        >>> path = download_github_directory(
        ...     "https://github.com/user/repo/tree/main/examples/demo"
        ... )
        >>> print(f"Downloaded to: {path}")
    """
    downloader = GitHubDownloader(use_curl=use_curl)
    return downloader.download_directory(github_url, output_dir)


def main() -> None:
    """Command line interface for GitHub directory downloader."""
    try:
        github_url = input("Enter the GitHub URL of the directory you want to download: ").strip()
        
        if not github_url:
            print("No URL provided.")
            return
        
        print(f"Downloading from: {github_url}")
        output_path = download_github_directory(github_url)
        print(f"Successfully downloaded to: {output_path}")
        
    except GitHubDownloadError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == '__main__':
    main()
