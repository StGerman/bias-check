#!/usr/bin/env python3
"""
RAG Bias Analysis Runner

This script demonstrates how to use the RAG bias analysis framework
to analyze potential bias in AI-powered information retrieval systems.
"""

import json
import os
from typing import Dict, List

from rag_bias_analysis import (
    SYSTEM_PROMPT,
    TEST_PROFILES,
    TEST_QUERIES,
    BiasAnalyzer,
    ClaudeRAGAnalyzer,
    RAGBiasAnalyzer,
)


def run_demo_analysis(api_key: str = None, num_samples: int = 20):
    """
    Run a demo analysis with mock data or Claude API.

    Args:
        api_key: Claude API key (optional - will use mock data if not provided)
        num_samples: Number of test cases to run (default: 20)
    """
    print("🚀 Starting RAG Bias Analysis Demo")
    print("=" * 50)

    # Initialize the core analyzer
    analyzer = RAGBiasAnalyzer(SYSTEM_PROMPT)

    # Generate test cases
    all_test_cases = analyzer.run_full_analysis()
    test_cases = all_test_cases[:num_samples]  # Limit for demo

    print(f"📊 Generated {len(test_cases)} test cases")
    print(f"👥 Testing {len(TEST_PROFILES)} user profiles")
    print(f"❓ Using {len(TEST_QUERIES)} query types")
    print()

    if api_key and ClaudeRAGAnalyzer:
        # Real analysis with Claude API
        print("🔍 Running analysis with Claude API...")
        claude_analyzer = ClaudeRAGAnalyzer(api_key)
        results_df = claude_analyzer.run_bias_analysis(test_cases, "demo_results.csv")

        # Analyze results for bias patterns
        bias_analyzer = BiasAnalyzer(results_df)

        print("\n📈 Analysis Results:")
        print("-" * 30)

        # Gender bias analysis
        gender_analysis = bias_analyzer.analyze_by_dimension("gender")
        print("👤 Gender Bias Analysis:")
        print(json.dumps(gender_analysis, indent=2, default=str))

        # Seniority bias analysis
        seniority_analysis = bias_analyzer.analyze_by_dimension("seniority")
        print("\n📊 Seniority Bias Analysis:")
        print(json.dumps(seniority_analysis, indent=2, default=str))

        # Create visualizations if possible
        try:
            bias_analyzer.create_visualizations("demo_plots")
            print("\n📊 Visualizations saved to demo_plots/ directory")
        except Exception as e:
            print(f"\n⚠️ Could not create visualizations: {e}")

        print(f"\n💾 Full results saved to demo_results.csv")

    else:
        # Mock analysis without API
        print("🎭 Running mock analysis (no API key provided)")
        print("This demonstrates the framework structure without making API calls")

        # Show sample test case structure
        sample_case = test_cases[0]
        print("\n📝 Sample Test Case Structure:")
        print(json.dumps(sample_case, indent=2, default=str))

        # Generate comparison groups
        comparisons = analyzer.generate_comparison_pairs()
        print(f"\n🔍 Generated {len(comparisons)} comparison groups:")
        for comp in comparisons:
            print(f"  - {comp['dimension']}: {len(comp['profiles'])} profiles")

    print("\n✅ Demo completed!")


def create_sample_config():
    """Create a sample configuration file for custom analysis."""
    config = {
        "analysis_settings": {
            "model": "claude-sonnet-4-20250514",
            "temperature": 0.1,
            "max_tokens": 1000,
        },
        "bias_dimensions": ["technical_depth", "career_advice", "formality_level", "encouragement_level"],
        "profile_comparisons": [
            {
                "name": "gender_same_role",
                "description": "Compare responses for same role, different genders",
                "profile_filters": {"title": "Senior Software Engineer"},
            },
            {
                "name": "seniority_progression",
                "description": "Compare responses across seniority levels",
                "profile_filters": {"department": "Engineering"},
            },
        ],
    }

    with open("analysis_config.json", "w") as f:
        json.dump(config, f, indent=2)

    print("📝 Sample configuration saved to analysis_config.json")


if __name__ == "__main__":
    import argparse
    import sys

    try:
        parser = argparse.ArgumentParser(description="Run RAG bias analysis")
        parser.add_argument("--api-key", help="Claude API key for real analysis")
        parser.add_argument("--samples", type=int, default=20, help="Number of test cases to run")
        parser.add_argument("--create-config", action="store_true", help="Create sample configuration file")

        args = parser.parse_args()

        if args.create_config:
            create_sample_config()
        else:
            # Check for API key in environment if not provided
            api_key = args.api_key or os.getenv("CLAUDE_API_KEY")
            if not api_key:
                print("💡 No API key provided. Running in demo mode with mock data.")
                print("   To run with real Claude API, set CLAUDE_API_KEY environment variable")
                print("   or use --api-key argument")

            run_demo_analysis(api_key, args.samples)

    except KeyboardInterrupt:
        print("\n❌ Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
