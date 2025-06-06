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
    model_name: str = "claude-sonnet-4-20250514"
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

## Documentation Alignment
All code, examples, and implementations MUST align with the documentation in the `docs/` directory:

### Required Consistency
- **User Profiles**: Use only profiles defined in `docs/rag-test-profiles.md`
- **Research Context**: Implement bias detection methods based on findings in `docs/rag-bias-research.md`
- **Test Cases**: Design test scenarios that reflect documented research patterns
- **Metrics**: Measure bias indicators mentioned in research documentation

### Validation Steps
1. **Before implementing features**: Review relevant documentation sections
2. **During development**: Ensure code examples match documented profiles and scenarios
3. **In tests**: Use documented test profiles and expected bias patterns
4. **Comments**: Reference specific research findings when implementing detection logic

### Example Alignment
```python
# Implementation should match profiles in docs/rag-test-profiles.md
SENIOR_ENGINEER_PROFILES = [
    UserProfile(name="Sarah Chen", title="Senior Software Engineer", ...),  # From docs
    UserProfile(name="Michael Chen", title="Senior Software Engineer", ...)  # From docs
]

# Detection logic should align with docs/rag-bias-research.md findings
def detect_gender_bias(response: str) -> Dict[str, float]:
    """
    Detect gender bias based on research showing males described as leaders,
    females with communal words (docs/rag-bias-research.md).
    """
```

## Key Principles
- **Simplicity First**: Avoid over-engineering - this is educational code
- **Readability**: Prefer explicit code over clever code
- **Educational Value**: Include comments explaining WHY decisions were made
- **API Integration**: Always include rate limiting for Claude API calls
- **Data Analysis**: Use pandas for structured data manipulation
- **Bias Detection**: Focus on measurable metrics (response length, technical depth, formality)
- **Documentation Consistency**: All implementations must reflect documented research and profiles

## Avoid These Patterns
- Complex inheritance hierarchies
- Overly abstract base classes
- Premature optimization
- Unclear abbreviations
- Silent failures
- Monolithic functions
