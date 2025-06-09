"""
RAG Bias Analysis Framework

A demo framework for analyzing bias in RAG systems based on user profiles.
This package provides tools for educational demonstrations of bias detection
in AI-powered information retrieval systems.
"""

from .core import SYSTEM_PROMPT, RAGBiasAnalyzer

# Core imports that should always work
from .models import TEST_PROFILES, TEST_QUERIES, UserProfile

# Optional imports that depend on external libraries
try:
    from .claude_analyzer import ClaudeRAGAnalyzer
except ImportError:
    ClaudeRAGAnalyzer = None

try:
    from .analyzers import BiasAnalyzer
except ImportError:
    BiasAnalyzer = None

__version__ = "0.1.0"
__all__ = [
    "RAGBiasAnalyzer",
    "ClaudeRAGAnalyzer",
    "BiasAnalyzer",
    "UserProfile",
    "TEST_PROFILES",
    "TEST_QUERIES",
    "SYSTEM_PROMPT",
]
