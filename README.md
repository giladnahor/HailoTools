# Hailo Utilities

A comprehensive collection of utilities and filters for working with Hailo AI hardware acceleration and GStreamer pipelines. This toolkit provides essential tools for video processing, RTSP streaming, pipeline management, and system monitoring.

## 🚀 Features

- **GStreamer Pipeline Formatter** - Format long GStreamer pipelines for better readability
- **RTSP Video Server** - Stream video files over RTSP protocol
- **Hardware Monitoring** - Monitor temperature and power consumption of Hailo devices
- **Git Utilities** - Extract repository information and branch details
- **Package Management** - Detect and configure TAPPAS environment
- **GitHub Downloader** - Download specific directories from GitHub repositories
- **Video Filters** - Aspect ratio correction and debugging tools for video processing
- **Development Tools** - Various utilities for development and debugging

## 📋 Requirements

### System Requirements
- **Operating System**: Linux (Ubuntu 18.04+ recommended)
- **Python**: 3.8 or higher
- **GStreamer**: 1.0 or higher
- **pkg-config**: For package detection

### Optional Dependencies
- **Hailo TAPPAS**: For AI processing capabilities
- **Hailo Hardware**: For hardware monitoring features

## 🔧 Installation

### Quick Install (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd hailo-utils

# Install the package
pip install -e .

# Or install system dependencies first
make install-deps
make install
```

### Manual Installation

1. **Install System Dependencies**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install python3 python3-pip pkg-config
   sudo apt-get install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev
   sudo apt-get install gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly gstreamer1.0-plugins-bad
   sudo apt-get install libgstrtspserver-1.0-dev
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Hailo TAPPAS** (Optional):
   ```bash
   # Follow Hailo's official installation guide
   # Set environment variables:
   export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/opt/hailo/tappas/pkgconfig
   ```

### Docker Installation

```bash
# Build the Docker image
docker build -t hailo-utils .

# Run with hardware access
docker run --privileged -v /dev:/dev hailo-utils
```

## 📖 Usage

### GStreamer Pipeline Formatter

Format long GStreamer pipelines for better readability:

```python
from hailo_utils.pipeline import format_pipeline

# Format a long pipeline
pipeline = "videotestsrc ! videoconvert ! x264enc ! rtph264pay ! udpsink host=127.0.0.1 port=5000"
formatted = format_pipeline(pipeline, line_limit=80)
print(formatted)
```

Or use the command line:
```bash
python -m hailo_utils.pipeline.formatter
# Enter your pipeline when prompted
```

### RTSP Video Server

Stream video files over RTSP:

```python
from hailo_utils.pipeline import RTSPVideoServer

# Start RTSP server
server = RTSPVideoServer()
server.add_stream("/stream1", "/path/to/video.mp4")
server.start(port=8554)
```

Command line usage:
```bash
python -m hailo_utils.pipeline.rtsp_server video1.mp4 video2.mp4
# Streams available at rtsp://127.0.0.1:8554/stream1, rtsp://127.0.0.1:8554/stream2
```

### Hardware Monitoring

Monitor Hailo device temperature and power:

```python
from hailo_utils.core import get_device_temperature

# Get temperature readings
temp_data = get_device_temperature()
for device, temp in temp_data.items():
    print(f"Device {device}: {temp}°C")
```

Command line usage:
```bash
python -m hailo_utils.core.temperature
# Displays real-time temperature and power data
```

### Git Utilities

Extract git repository information:

```python
from hailo_utils.core import get_git_info

# Get repository details
info = get_git_info()
print(f"Repository: {info['name']}")
print(f"Branch: {info['branch']}")
print(f"URL: {info['url']}")
```

### Package Information

Get TAPPAS environment information:

```python
from hailo_utils.core import get_tappas_info

# Get TAPPAS configuration
tappas_info = get_tappas_info()
print(f"Workspace: {tappas_info['workspace']}")
print(f"Version: {tappas_info['version']}")
```

### GitHub Directory Downloader

Download specific directories from GitHub:

```python
from hailo_utils.downloaders import download_github_directory

# Download a specific directory
download_github_directory("https://github.com/user/repo/tree/main/subdir")
```

Command line usage:
```bash
python -m hailo_utils.downloaders.github
# Enter GitHub URL when prompted
```

### Video Filters

Apply aspect ratio corrections and debugging:

```python
from hailo_utils.filters.python import AspectRatioFilter

# Use in GStreamer pipeline
filter = AspectRatioFilter()
# Filter will be applied automatically in GStreamer context
```

## 🛠️ Development

### Setting up Development Environment

```bash
# Clone and setup
git clone <repository-url>
cd hailo-utils

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=hailo_utils --cov-report=html

# Run specific test file
pytest tests/test_pipeline.py
```

### Code Formatting

```bash
# Format code
black hailo_utils/ tests/

# Check formatting
black --check hailo_utils/ tests/

# Sort imports
isort hailo_utils/ tests/
```

## 📁 Project Structure

```
hailo-utils/
├── hailo_utils/              # Main package
│   ├── __init__.py
│   ├── core/                 # Core utilities
│   │   ├── git_utils.py
│   │   ├── package_info.py
│   │   └── temperature.py
│   ├── pipeline/             # Pipeline tools
│   │   ├── formatter.py
│   │   └── rtsp_server.py
│   ├── filters/              # Video filters
│   │   ├── python/
│   │   └── cpp/
│   └── downloaders/          # Download utilities
│       └── github.py
├── tests/                    # Test suite
├── docs/                     # Documentation
├── scripts/                  # Utility scripts
├── requirements.txt          # Python dependencies
├── setup.py                  # Package setup
├── pyproject.toml           # Modern packaging config
├── Makefile                 # Build automation
└── README.md                # This file
```

## 🔍 Troubleshooting

### Common Issues

1. **ImportError: hailo_platform not found**
   ```bash
   # Activate TAPPAS virtual environment
   source /opt/hailo/tappas/bin/activate
   # Or install pyhailort
   pip install pyhailort
   ```

2. **GStreamer plugins not found**
   ```bash
   # Install GStreamer plugins
   sudo apt-get install gstreamer1.0-plugins-*
   ```

3. **pkg-config errors**
   ```bash
   # Set PKG_CONFIG_PATH
   export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/opt/hailo/tappas/pkgconfig
   ```

4. **Permission denied for hardware access**
   ```bash
   # Add user to video group
   sudo usermod -a -G video $USER
   # Logout and login again
   ```

### Getting Help

- Check the [documentation](docs/)
- Review [examples](examples/)
- Open an [issue](issues/) for bugs
- Join our [discussions](discussions/) for questions

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Hailo Technologies for the AI hardware platform
- GStreamer community for the multimedia framework
- Contributors and maintainers of this project

## 📊 Status

![Build Status](https://github.com/user/hailo-utils/workflows/CI/badge.svg)
![Coverage](https://codecov.io/gh/user/hailo-utils/branch/main/graph/badge.svg)
![PyPI Version](https://badge.fury.io/py/hailo-utils.svg)
![Python Versions](https://img.shields.io/pypi/pyversions/hailo-utils.svg)

---

For more detailed documentation, visit our [documentation site](https://hailo-utils.readthedocs.io/).