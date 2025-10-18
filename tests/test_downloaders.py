#!/usr/bin/env python3
"""
Tests for download utilities (GitHub downloader).
"""

import pytest
import tempfile
import os
import shutil
from unittest.mock import patch, MagicMock

from hailo_utils.downloaders import github


class TestGitHubDownloader:
    """Test cases for GitHub directory downloader."""
    
    def test_parse_github_url_valid(self):
        """Test parsing valid GitHub URLs."""
        downloader = github.GitHubDownloader()
        
        url = "https://github.com/user/repo/tree/main/path/to/dir"
        owner, repo, branch, directory = downloader.parse_github_url(url)
        
        assert owner == "user"
        assert repo == "repo"
        assert branch == "main"
        assert directory == "path/to/dir"
    
    def test_parse_github_url_root_directory(self):
        """Test parsing GitHub URL pointing to root."""
        downloader = github.GitHubDownloader()
        
        url = "https://github.com/user/repo/tree/main"
        owner, repo, branch, directory = downloader.parse_github_url(url)
        
        assert owner == "user"
        assert repo == "repo"
        assert branch == "main"
        assert directory == ""
    
    def test_parse_github_url_invalid_format(self):
        """Test parsing invalid GitHub URLs."""
        downloader = github.GitHubDownloader()
        
        with pytest.raises(github.GitHubDownloadError, match="Invalid GitHub URL format"):
            downloader.parse_github_url("https://github.com/user/repo")
        
        with pytest.raises(github.GitHubDownloadError, match="Invalid GitHub URL format"):
            downloader.parse_github_url("https://gitlab.com/user/repo/tree/main/dir")
    
    def test_parse_github_url_malformed(self):
        """Test parsing malformed URLs."""
        downloader = github.GitHubDownloader()
        
        with pytest.raises(github.GitHubDownloadError):
            downloader.parse_github_url("not-a-url")
    
    @patch('shutil.which')
    def test_check_dependencies_wget_missing(self, mock_which):
        """Test dependency check when wget is missing."""
        mock_which.side_effect = lambda cmd: None if cmd == 'wget' else '/usr/bin/' + cmd
        
        with pytest.raises(github.GitHubDownloadError, match="wget not found"):
            github.GitHubDownloader(use_curl=False)
    
    @patch('shutil.which')
    def test_check_dependencies_curl_missing(self, mock_which):
        """Test dependency check when curl is missing."""
        mock_which.side_effect = lambda cmd: None if cmd == 'curl' else '/usr/bin/' + cmd
        
        with pytest.raises(github.GitHubDownloadError, match="curl not found"):
            github.GitHubDownloader(use_curl=True)
    
    @patch('shutil.which')
    def test_check_dependencies_unzip_missing(self, mock_which):
        """Test dependency check when unzip is missing."""
        mock_which.side_effect = lambda cmd: None if cmd == 'unzip' else '/usr/bin/' + cmd
        
        with pytest.raises(github.GitHubDownloadError, match="unzip not found"):
            github.GitHubDownloader()
    
    @patch('shutil.which')
    @patch('subprocess.run')
    def test_download_file_wget(self, mock_run, mock_which):
        """Test file download using wget."""
        mock_which.return_value = '/usr/bin/wget'
        mock_run.return_value = MagicMock(returncode=0)
        
        downloader = github.GitHubDownloader(use_curl=False)
        
        with tempfile.NamedTemporaryFile() as temp_file:
            downloader._download_file("https://example.com/file.zip", temp_file.name)
            
            mock_run.assert_called_once_with(
                ['wget', '-O', temp_file.name, 'https://example.com/file.zip'],
                capture_output=True,
                text=True,
                check=True
            )
    
    @patch('shutil.which')
    @patch('subprocess.run')
    def test_download_file_curl(self, mock_run, mock_which):
        """Test file download using curl."""
        mock_which.return_value = '/usr/bin/curl'
        mock_run.return_value = MagicMock(returncode=0)
        
        downloader = github.GitHubDownloader(use_curl=True)
        
        with tempfile.NamedTemporaryFile() as temp_file:
            downloader._download_file("https://example.com/file.zip", temp_file.name)
            
            mock_run.assert_called_once_with(
                ['curl', '-L', '-o', temp_file.name, 'https://example.com/file.zip'],
                capture_output=True,
                text=True,
                check=True
            )
    
    @patch('shutil.which')
    @patch('subprocess.run')
    def test_download_file_failure(self, mock_run, mock_which):
        """Test file download failure."""
        mock_which.return_value = '/usr/bin/wget'
        mock_run.side_effect = subprocess.CalledProcessError(1, 'wget', stderr='Connection failed')
        
        downloader = github.GitHubDownloader()
        
        with tempfile.NamedTemporaryFile() as temp_file:
            with pytest.raises(github.GitHubDownloadError, match="Failed to download"):
                downloader._download_file("https://example.com/file.zip", temp_file.name)
    
    def test_download_directory_no_path(self):
        """Test download with URL pointing to repository root."""
        downloader = github.GitHubDownloader()
        
        url = "https://github.com/user/repo/tree/main"
        
        with pytest.raises(github.GitHubDownloadError, match="must point to a specific directory"):
            downloader.download_directory(url)


class TestConvenienceFunctions:
    """Test cases for convenience functions."""
    
    @patch('hailo_utils.downloaders.github.GitHubDownloader')
    def test_download_github_directory_function(self, mock_downloader_class):
        """Test the convenience download function."""
        mock_downloader = MagicMock()
        mock_downloader.download_directory.return_value = "/path/to/downloaded"
        mock_downloader_class.return_value = mock_downloader
        
        result = github.download_github_directory(
            "https://github.com/user/repo/tree/main/dir",
            output_dir="/custom/output"
        )
        
        assert result == "/path/to/downloaded"
        mock_downloader_class.assert_called_once_with(use_curl=False)
        mock_downloader.download_directory.assert_called_once_with(
            "https://github.com/user/repo/tree/main/dir",
            "/custom/output"
        )
    
    @patch('hailo_utils.downloaders.github.GitHubDownloader')
    def test_download_github_directory_with_curl(self, mock_downloader_class):
        """Test the convenience download function with curl."""
        mock_downloader = MagicMock()
        mock_downloader_class.return_value = mock_downloader
        
        github.download_github_directory(
            "https://github.com/user/repo/tree/main/dir",
            use_curl=True
        )
        
        mock_downloader_class.assert_called_once_with(use_curl=True)


class TestMainFunction:
    """Test cases for command-line interface."""
    
    @patch('builtins.input')
    @patch('hailo_utils.downloaders.github.download_github_directory')
    def test_main_success(self, mock_download, mock_input):
        """Test successful main function execution."""
        mock_input.return_value = "https://github.com/user/repo/tree/main/dir"
        mock_download.return_value = "/downloaded/path"
        
        # Should not raise any exceptions
        github.main()
        
        mock_download.assert_called_once_with("https://github.com/user/repo/tree/main/dir")
    
    @patch('builtins.input')
    def test_main_empty_input(self, mock_input):
        """Test main function with empty input."""
        mock_input.return_value = ""
        
        # Should not raise any exceptions
        github.main()
    
    @patch('builtins.input')
    @patch('hailo_utils.downloaders.github.download_github_directory')
    def test_main_download_error(self, mock_download, mock_input):
        """Test main function with download error."""
        mock_input.return_value = "https://github.com/user/repo/tree/main/dir"
        mock_download.side_effect = github.GitHubDownloadError("Download failed")
        
        # Should not raise any exceptions (errors are caught and printed)
        github.main()


if __name__ == '__main__':
    pytest.main([__file__])