#!/usr/bin/env python3
"""
Tests for core utilities (git, package info, temperature monitoring).
"""

import pytest
import subprocess
from unittest.mock import patch, MagicMock

from hailo_utils.core import git_utils, package_info


class TestGitUtils:
    """Test cases for git utilities."""
    
    def test_extract_repo_name_ssh(self):
        """Test SSH URL parsing."""
        url = "git@github.com:user/repo.git"
        name, protocol, full_url = git_utils.extract_repo_name(url)
        
        assert name == "user/repo"
        assert protocol == "SSH"
        assert full_url == url
    
    def test_extract_repo_name_https(self):
        """Test HTTPS URL parsing."""
        url = "https://github.com/user/repo.git"
        name, protocol, full_url = git_utils.extract_repo_name(url)
        
        assert name == "repo"
        assert protocol == "HTTPS"
        assert full_url == url
    
    def test_extract_repo_name_invalid(self):
        """Test invalid URL handling."""
        name, protocol, full_url = git_utils.extract_repo_name("invalid-url")
        
        assert name is None
        assert protocol is None
        assert full_url is None
    
    def test_extract_repo_name_empty(self):
        """Test empty URL handling."""
        name, protocol, full_url = git_utils.extract_repo_name("")
        
        assert name is None
        assert protocol is None
        assert full_url is None
    
    @patch('subprocess.run')
    def test_get_git_remote_url_success(self, mock_run):
        """Test successful git remote URL retrieval."""
        mock_run.return_value.stdout = "origin\tgit@github.com:user/repo.git (fetch)\n"
        
        result = git_utils.get_git_remote_url()
        
        assert result == "git@github.com:user/repo.git"
        mock_run.assert_called_once_with(
            ["git", "remote", "-v"],
            capture_output=True,
            text=True,
            check=True
        )
    
    @patch('subprocess.run')
    def test_get_git_remote_url_failure(self, mock_run):
        """Test git remote URL retrieval failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'git')
        
        result = git_utils.get_git_remote_url()
        
        assert result is None
    
    @patch('subprocess.run')
    def test_get_git_branch_success(self, mock_run):
        """Test successful git branch retrieval."""
        mock_run.return_value.stdout = "main\n"
        
        result = git_utils.get_git_branch()
        
        assert result == "main"
    
    @patch('subprocess.run')
    def test_get_git_branch_failure(self, mock_run):
        """Test git branch retrieval failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'git')
        
        result = git_utils.get_git_branch()
        
        assert result is None
    
    @patch('hailo_utils.core.git_utils.get_git_remote_url')
    @patch('hailo_utils.core.git_utils.get_git_branch')
    def test_get_git_info_success(self, mock_branch, mock_url):
        """Test successful git info retrieval."""
        mock_url.return_value = "https://github.com/user/repo.git"
        mock_branch.return_value = "main"
        
        result = git_utils.get_git_info()
        
        assert result['name'] == "repo"
        assert result['branch'] == "main"
        assert result['url'] == "https://github.com/user/repo.git"
        assert result['protocol'] == "HTTPS"
        assert 'error' not in result
    
    @patch('hailo_utils.core.git_utils.get_git_remote_url')
    def test_get_git_info_no_remote(self, mock_url):
        """Test git info retrieval with no remote."""
        mock_url.return_value = None
        
        result = git_utils.get_git_info()
        
        assert result['name'] is None
        assert result['branch'] is None
        assert result['url'] is None
        assert result['protocol'] is None
        assert 'error' in result


class TestPackageInfo:
    """Test cases for package information utilities."""
    
    @patch.dict('os.environ', {
        'TAPPAS_WORKSPACE': '/opt/hailo/tappas',
        'TAPPAS_VERSION': '3.27.0',
        'TAPPAS_LIBDIR': '/opt/hailo/tappas/lib'
    })
    def test_get_tappas_info_from_env(self):
        """Test TAPPAS info retrieval from environment variables."""
        result = package_info.get_tappas_info()
        
        assert result['tappas_workspace'] == '/opt/hailo/tappas'
        assert result['version'] == '3.27.0'
        assert result['libdir'] == '/opt/hailo/tappas/lib'
    
    @patch.dict('os.environ', {}, clear=True)
    @patch('subprocess.check_output')
    def test_get_tappas_info_from_pkgconfig(self, mock_subprocess):
        """Test TAPPAS info retrieval from pkg-config."""
        mock_subprocess.side_effect = [
            '/opt/hailo/tappas\n',
            '3.27.0\n', 
            '/opt/hailo/tappas/lib\n'
        ]
        
        result = package_info.get_tappas_info()
        
        assert result['tappas_workspace'] == '/opt/hailo/tappas'
        assert result['version'] == '3.27.0'
        assert result['libdir'] == '/opt/hailo/tappas/lib'
    
    @patch.dict('os.environ', {}, clear=True)
    @patch('subprocess.check_output')
    def test_get_tappas_info_failure(self, mock_subprocess):
        """Test TAPPAS info retrieval failure."""
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, 'pkg-config')
        
        with pytest.raises(package_info.TappasConfigError):
            package_info.get_tappas_info()
    
    def test_check_tappas_environment_success(self):
        """Test TAPPAS environment check success."""
        with patch('hailo_utils.core.package_info.get_tappas_info') as mock_get:
            mock_get.return_value = {'tappas_workspace': '/opt/hailo/tappas'}
            
            result = package_info.check_tappas_environment()
            
            assert result is True
    
    def test_check_tappas_environment_failure(self):
        """Test TAPPAS environment check failure."""
        with patch('hailo_utils.core.package_info.get_tappas_info') as mock_get:
            mock_get.side_effect = package_info.TappasConfigError("Not found")
            
            result = package_info.check_tappas_environment()
            
            assert result is False


# Temperature monitoring tests would require mocking the hailo_platform module
# which is optional, so we'll skip those for now unless hailo is available
class TestTemperature:
    """Test cases for temperature monitoring (requires hailo_platform)."""
    
    def test_check_hailo_availability(self):
        """Test hailo availability check."""
        from hailo_utils.core import temperature
        
        # This will return True or False depending on whether hailo_platform is installed
        result = temperature.check_hailo_availability()
        assert isinstance(result, bool)
    
    @pytest.mark.skipif(
        not pytest.importorskip("hailo_platform", minversion=None),
        reason="hailo_platform not available"
    )
    def test_get_device_temperature_no_devices(self):
        """Test temperature retrieval with no devices."""
        from hailo_utils.core import temperature
        
        with patch('hailo_platform.Device.scan') as mock_scan:
            mock_scan.return_value = []
            
            with pytest.raises(temperature.HailoDeviceError, match="No Hailo devices found"):
                temperature.get_device_temperature()


if __name__ == '__main__':
    pytest.main([__file__])