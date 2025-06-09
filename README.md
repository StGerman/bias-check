# RAG Bias Analysis Framework

A **demo framework** for analyzing bias patterns in Retrieval-Augmented Generation (RAG) systems. This educational tool demonstrates how user profile characteristics can influence AI responses in enterprise knowledge retrieval systems.

> 🎯 **Purpose**: Companion code for research article on RAG bias detection and mitigation strategies.

## Quick Start

```bash
# Setup environment
make setup-dev

# Run demo analysis (uses mock data without API key)
make run-demo

# Validate documentation alignment
python validate_documentation_alignment.py
```

## Research Overview

This framework implements bias detection methods based on documented research findings:

### Key Bias Dimensions Analyzed

1. **Gender Bias**: Detects leadership vs. communal language patterns
2. **Cultural Bias**: Identifies individualism vs. collectivism assumptions
3. **Seniority Bias**: Measures complexity and accommodation variations

### Research-Based Test Profiles

**19 test profiles** covering bias dimensions:
- Gender diversity (same roles)
- Seniority progression (junior → senior → manager)
- Cultural/geographic diversity (4 continents)
- Department diversity (technical vs. non-technical)

See [`docs/rag-test-profiles.md`](docs/rag-test-profiles.md) for complete profile specifications.

### Test Query Categories

**10 specialized queries** designed to reveal bias:
- Technical complexity questions
- Career development inquiries
- Policy interpretation requests
- Troubleshooting scenarios
- Performance metrics

## Framework Architecture

```
rag_bias_analysis/
├── core.py              # RAGBiasAnalyzer (main framework)
├── claude_analyzer.py   # Claude API integration + caching
├── analyzers.py         # Statistical bias analysis
├── models.py           # Test profiles and queries
```

### Core Components

- **`RAGBiasAnalyzer`**: Framework for detecting bias patterns
- **`ClaudeRAGAnalyzer`**: Claude API integration with response caching
- **`BiasAnalyzer`**: Statistical analysis and visualization tools
- **`DocumentationValidator`**: Automated alignment verification

## Usage Examples

### Basic Analysis

```python
from rag_bias_analysis import RAGBiasAnalyzer, SYSTEM_PROMPT

# Initialize framework
analyzer = RAGBiasAnalyzer(SYSTEM_PROMPT)

# Generate comparison pairs for bias analysis
comparisons = analyzer.generate_comparison_pairs()
# Returns 3 comparison groups: gender, seniority, cultural
```

### API Integration

```python
from rag_bias_analysis import ClaudeRAGAnalyzer

# Run with Claude API (requires ANTHROPIC_API_KEY)
claude_analyzer = ClaudeRAGAnalyzer(api_key="your-key")
results_df = claude_analyzer.run_bias_analysis(test_cases)
```

### Statistical Analysis

```python
from rag_bias_analysis import BiasAnalyzer

# Analyze results for bias patterns
bias_analyzer = BiasAnalyzer(results_df)
gender_analysis = bias_analyzer.analyze_by_dimension("gender")
seniority_analysis = bias_analyzer.analyze_by_dimension("seniority")
```

## Research Validation

The framework includes automated validation to ensure code aligns with research documentation:

```bash
python validate_documentation_alignment.py
```

**Validation checks**:
- ✅ All 19 test profiles match documentation
- ✅ Research-based bias detection methods implemented
- ✅ Test queries align with documented scenarios

## Key Features

### 🔬 **Research-Based Detection**
Implements bias indicators from academic research:
- Leadership vs. communal language patterns
- Cultural assumption detection (individualism/collectivism)
- Seniority-based complexity variations

### 💾 **Response Caching**
Persistent cache system reduces API costs:
- JSON-based local storage
- Request deduplication
- Cache statistics and management

### 📊 **Comprehensive Analysis**
Multiple analysis dimensions:
- Response length and technical depth
- Formality and encouragement levels
- Bias-specific pattern detection

### 🎨 **Visualization Support**
Automated chart generation:
- Gender bias heatmaps
- Seniority progression analysis
- Department comparison plots

## Development Workflow

### Essential Commands

```bash
make install     # Install dependencies with Poetry
make test        # Run tests with coverage
make format      # Format code (black + isort)
make lint        # Type checking and style validation
make check       # Run format + lint + test together
```

### Quick Commands

```bash
make test-fast   # Skip slow integration tests
make run-demo    # Execute demo with mock data
make clean       # Remove caches and temp files
```

## Configuration

### Environment Variables

```bash
# For real API calls (optional - framework works with mocks)
export ANTHROPIC_API_KEY="your-api-key"

# Claude model selection (optional)
export CLAUDE_MODEL="claude-sonnet-4-20250514"
```

### Mock vs. Real API

- **Without API key**: Uses intelligent mock responses for demo
- **With API key**: Makes real Claude API calls with caching

## Research Applications

### Bias Detection Use Cases

1. **Enterprise RAG Auditing**: Assess bias in internal knowledge systems
2. **AI Fairness Research**: Quantify response variations across demographics
3. **Model Comparison**: Compare bias patterns across different LLMs
4. **Mitigation Testing**: Evaluate bias reduction interventions

### Measurable Bias Indicators

- **Response Length**: Average words per response by profile
- **Technical Depth**: Technical terminology density
- **Formality Level**: Formal vs. informal language patterns
- **Encouragement**: Supportive language frequency
- **Cultural Assumptions**: Individualism vs. collectivism emphasis

## Educational Value

This framework serves as a **practical demonstration** of:

- Systematic bias detection methodology
- Quantitative bias measurement approaches
- Research-driven test case design
- Statistical analysis of AI system fairness
- Documentation-driven development practices

## Research Documentation

- [`docs/rag-bias-research.md`](docs/rag-bias-research.md) - Research findings and bias patterns
- [`docs/rag-test-profiles.md`](docs/rag-test-profiles.md) - Complete test profile specifications

## Technical Requirements

- **Python 3.9+** with Poetry dependency management
- **Optional**: Anthropic API key for real Claude integration
- **Dependencies**: pandas, anthropic, matplotlib (auto-installed)

## License & Attribution

Educational demonstration framework for RAG bias research. See source code for implementation details and research methodology.

---

**Note**: This framework is designed for educational and research purposes. Always validate findings with domain experts and consider ethical implications when analyzing bias in AI systems.
