# Contributing to Hailo Utilities

Thank you for your interest in contributing to Hailo Utilities! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/hailo-utils.git
   cd hailo-utils
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -e ".[dev]"
   pre-commit install
   ```

4. **Verify Setup**
   ```bash
   make check-system
   pytest tests/ -v
   ```

## 📋 Development Guidelines

### Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking
- **pytest** for testing

Run all checks:
```bash
make check
```

Format code:
```bash
make format
```

### Code Structure

- **Modules**: Organize code into logical modules under `hailo_utils/`
- **Type Hints**: Use type hints for all function parameters and return values
- **Docstrings**: Use Google-style docstrings for all public functions and classes
- **Error Handling**: Provide clear error messages and proper exception handling

### Example Function

```python
def process_video_frame(
    frame: VideoFrame, 
    threshold: float = 0.5
) -> List[Detection]:
    """
    Process a video frame to extract detections.
    
    Args:
        frame: The video frame to process.
        threshold: Confidence threshold for detections (default: 0.5).
        
    Returns:
        List of detected objects with confidence above threshold.
        
    Raises:
        ProcessingError: If frame processing fails.
    """
    # Implementation here
    pass
```

## 🧪 Testing

### Writing Tests

- Write tests for all new functionality
- Include unit tests, integration tests, and edge cases
- Use pytest fixtures for common test setup
- Mock external dependencies (hardware, network)

### Test Categories

Use pytest markers to categorize tests:

```python
@pytest.mark.slow
def test_long_running_operation():
    """Test that takes significant time."""
    pass

@pytest.mark.hardware
def test_hailo_device_interaction():
    """Test requiring Hailo hardware."""
    pass

@pytest.mark.integration
def test_full_pipeline():
    """Integration test with multiple components."""
    pass
```

### Running Tests

```bash
# All tests
pytest

# Fast tests only
pytest -m "not slow"

# Specific test file
pytest tests/test_pipeline.py

# With coverage
pytest --cov=hailo_utils --cov-report=html
```

## 📝 Documentation

### Docstring Style

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int = 10) -> bool:
    """
    Brief description of the function.
    
    Longer description if needed, explaining the purpose,
    algorithm, or important details.
    
    Args:
        param1: Description of first parameter.
        param2: Description of second parameter (default: 10).
        
    Returns:
        Description of return value.
        
    Raises:
        ValueError: When param1 is empty.
        ProcessingError: When processing fails.
        
    Example:
        >>> result = example_function("hello", 5)
        >>> print(result)
        True
    """
```

### README Updates

When adding new features:
1. Update the main README.md
2. Add usage examples
3. Update installation instructions if needed
4. Document any new dependencies

## 🔄 Pull Request Process

### Before Submitting

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow coding guidelines
   - Add tests for new functionality
   - Update documentation

3. **Run Checks**
   ```bash
   make check
   pytest
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new video processing filter"
   ```

### Commit Message Format

Use conventional commit format:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```
feat: add aspect ratio correction filter
fix: handle missing GStreamer dependencies gracefully
docs: update installation instructions for Ubuntu 22.04
test: add unit tests for pipeline formatter
```

### Pull Request Checklist

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if applicable)
- [ ] No breaking changes (or clearly documented)
- [ ] PR description explains the changes

### PR Description Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added and passing
```

## 🐛 Bug Reports

### Before Reporting

1. Check existing issues
2. Try with the latest version
3. Provide minimal reproduction case

### Bug Report Template

```markdown
**Describe the Bug**
Clear description of the bug.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
What you expected to happen.

**Environment**
- OS: [e.g. Ubuntu 20.04]
- Python Version: [e.g. 3.9.5]
- Hailo Utils Version: [e.g. 0.1.0]
- GStreamer Version: [e.g. 1.18.4]
- TAPPAS Version: [e.g. 3.27.0]

**Additional Context**
Any other context about the problem.
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
Clear description of the problem.

**Describe the solution you'd like**
Clear description of what you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features considered.

**Additional context**
Any other context or screenshots.
```

## 🏗️ Architecture Decisions

### Adding New Modules

1. Follow the existing package structure
2. Add appropriate `__init__.py` files
3. Update main package imports
4. Add tests in corresponding test directory
5. Update documentation

### Dependencies

- **Core**: Minimize dependencies for core functionality
- **Optional**: Use optional dependencies for specialized features
- **System**: Document system dependencies clearly
- **Versions**: Pin major versions, allow minor updates

## 🤝 Community

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the project's code of conduct

### Getting Help

- Check documentation first
- Search existing issues
- Ask questions in discussions
- Join community channels (if available)

## 📜 License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

---

Thank you for contributing to Hailo Utilities! 🎉