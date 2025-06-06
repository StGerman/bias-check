# GitHub Copilot Instructions - RAG Bias Analysis Framework

Remember: Create code that effectively demonstrates bias differences in RAG systems, making it easy for readers to understand and replicate the analysis in their own projects.

## Project Overview
This is a **demo project** for an article about analyzing bias in RAG systems. Code should be:
- **Simple and readable** - prioritize clarity over complexity
- **Well documented** - comprehensive docstrings and comments
- **Educational** - demonstrate concepts clearly for readers

## Technology Stack
- **Python 3.9+** with Poetry for dependency management
- **pytest** for testing, **Anthropic Claude API** for LLM interactions
- **pandas/numpy** for data analysis, **matplotlib** for visualizations

## Code Style Guidelines

### General Principles
- Write code that tells a story - this is for an article
- Use descriptive variable names and type hints for all public methods
- Add docstrings to all classes and public methods
- Keep functions small and focused (max 20-30 lines)
- Use dataclasses for structured data

### Documentation Standards
```python
def example_function(param: str, optional_param: int = 10) -> Dict[str, Any]:
    """
    Brief description of what the function does.

    Args:
        param: Description of the parameter
        optional_param: Description with default value

    Returns:
        Dictionary containing the result data
    """
```

### Error Handling
- Use specific exception types with helpful error messages
- Log errors appropriately for demo purposes
- Don't fail silently - make issues visible

## Testing Guidelines
- One test file per module: `test_<module_name>.py`
- Use descriptive test names: `test_should_detect_gender_bias_in_responses`
- Use pytest fixtures for setup/teardown
- Include unit tests, integration tests, and mock tests to avoid API costs

### Example Test Pattern
```python
def test_should_analyze_response_characteristics():
    """Test that response analysis extracts expected metrics."""
    # Arrange
    sample_response = "This is a technical response with API endpoints."
    analyzer = ResponseAnalyzer()

    # Act
    result = analyzer.analyze_response(sample_response)

    # Assert
    assert "technical_depth" in result
    assert result["technical_depth"] > 0
```

## Project Structure
```
rag_bias_analysis/         # Main package
├── core/                  # Core functionality
├── analyzers/             # Bias analysis modules
├── models/                # Data models
tests/                     # Test files
docs/                      # Documentation files
examples/                  # Usage examples
```

## Import Organization
```python
# Standard library
import json
from datetime import datetime
from typing import Dict, List, Any

# Third-party packages
import pandas as pd
from anthropic import Anthropic

# Local imports
from rag_bias_analysis.core import BiasAnalyzer
from rag_bias_analysis.models import UserProfile
```

## Implementation Patterns

### Configuration Management
```python
@dataclass
class AnalysisConfig:
    """Configuration for bias analysis."""
    api_key: str
    model_name: str = "claude-3-sonnet-20240229"
    max_tokens: int = 1000
    temperature: float = 0.1
```

### Error Handling
```python
try:
    response = api_client.get_response(prompt)
except Exception as e:
    logger.error(f"API call failed: {e}")
    return {"error": str(e), "response": None}
```

## Development Workflow
Use the provided Makefile commands for consistent development workflow:

### Essential Commands
- `make install` - Install dependencies with Poetry
- `make test` - Run all tests with coverage
- `make format` - Format code with black and isort
- `make lint` - Check code style and types
- `make check` - Run format, lint, and test together

### Quick Commands
- `make test-fast` - Run tests excluding slow integration tests
- `make run-demo` - Execute the demo script with mock data
- `make clean` - Remove temporary files and caches
- `make setup-dev` - Complete development environment setup

Always run `make check` before committing changes to ensure code quality.

## Key Principles
- **Simplicity First**: Avoid over-engineering - this is educational code
- **Readability**: Prefer explicit code over clever code
- **Educational Value**: Include comments explaining WHY decisions were made
- **API Integration**: Always include rate limiting for Claude API calls
- **Data Analysis**: Use pandas for structured data manipulation
- **Bias Detection**: Focus on measurable metrics (response length, technical depth, formality)

## Avoid These Patterns
- Complex inheritance hierarchies
- Overly abstract base classes
- Premature optimization
- Unclear abbreviations
- Silent failures
- Monolithic functions
