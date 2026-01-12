# Contributing to MasterChief Platform

Thank you for your interest in contributing to the MasterChief Platform! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported
2. Use the bug report template
3. Include:
   - OS and version
   - Platform version
   - Steps to reproduce
   - Expected vs actual behavior
   - Relevant logs

### Suggesting Features

1. Check existing feature requests
2. Describe the use case
3. Explain the expected behavior
4. Consider implementation details

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write or update tests
5. Update documentation
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Development Setup

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Git

### Local Development

```bash
# Clone repository
git clone https://github.com/jbalestrine/masterchief.git
cd masterchief

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest

# Run platform
python3 platform/main.py
```

### Docker Development

```bash
# Build and run
docker-compose up --build

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Code Style

### Python

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use meaningful variable names
- Add docstrings to all functions/classes

```python
def process_data(input_data: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Process input data and return statistics.
    
    Args:
        input_data: List of data dictionaries
        
    Returns:
        Dictionary with processing statistics
    """
    pass
```

### Formatting

Use `black` for formatting:

```bash
black platform/ addons/
```

Use `flake8` for linting:

```bash
flake8 platform/ addons/
```

## Testing

### Unit Tests

- Write tests for all new features
- Test edge cases and error conditions
- Aim for >80% code coverage

```python
def test_service_manager_start():
    manager = ServiceManager()
    result = manager.start('test-service')
    assert result is True
```

### Integration Tests

- Test interactions between modules
- Use mocks for external dependencies
- Test API endpoints

### Running Tests

```bash
# All tests
pytest

# Specific module
pytest platform/services/

# With coverage
pytest --cov=platform --cov-report=html

# Verbose output
pytest -v
```

## Documentation

### Code Documentation

- Add docstrings to all public functions/classes
- Use clear, concise language
- Include examples where helpful

### User Documentation

- Update relevant documentation in `docs/`
- Include examples and use cases
- Keep documentation up-to-date with code changes

### API Documentation

- Document all API endpoints
- Include request/response examples
- Document error codes

## Commit Messages

Use conventional commit format:

```
type(scope): subject

body

footer
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

Example:
```
feat(services): add service dependency management

Add ability to define and manage service dependencies.
Services will start in correct order based on dependencies.

Closes #123
```

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Ensure tests pass** locally
4. **Update CHANGELOG.md** with changes
5. **Request review** from maintainers
6. **Address feedback** promptly
7. **Squash commits** if requested

## Release Process

(For maintainers)

1. Update version in `platform/config.py`
2. Update `CHANGELOG.md`
3. Create release branch
4. Tag release (`git tag -a v1.0.0 -m "Release v1.0.0"`)
5. Push tags (`git push --tags`)
6. Create GitHub release
7. Build and publish Docker images
8. Update documentation

## Questions?

- Open a GitHub Discussion
- Join our IRC channel
- Email the maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
