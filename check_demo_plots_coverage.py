#!/usr/bin/env python3
"""
Demo Plot Coverage Checker

This script analyzes the completeness of your demo_plots directory by:
1. Checking which plots are currently generated
2. Identifying bias dimensions that need visualization
3. Suggesting additional plots based on research documentation
4. Providing recommendations for comprehensive coverage
"""

import os
from pathlib import Path
from typing import Dict, List, Set, Tuple
import json

# Import our analysis modules to understand what data is available
try:
    from rag_bias_analysis.models import TEST_PROFILES, TEST_QUERIES
    from rag_bias_analysis.analyzers import BiasAnalyzer
    import pandas as pd
except ImportError as e:
    print(f"Warning: Could not import analysis modules: {e}")
    TEST_PROFILES = []
    TEST_QUERIES = []

class DemoPlotChecker:
    """Check the completeness of demo plots for bias analysis."""

    def __init__(self, demo_plots_dir: str = "demo_plots"):
        self.demo_plots_dir = Path(demo_plots_dir)
        self.current_plots = self._get_current_plots()
        self.bias_dimensions = self._get_bias_dimensions()
        self.profile_characteristics = self._analyze_test_profiles()

    def _get_current_plots(self) -> List[str]:
        """Get list of currently generated plot files."""
        if not self.demo_plots_dir.exists():
            return []

        plot_files = []
        for file_path in self.demo_plots_dir.glob("*.png"):
            plot_files.append(file_path.name)

        return sorted(plot_files)

    def _get_bias_dimensions(self) -> Dict[str, List[str]]:
        """Define bias dimensions based on research documentation."""
        return {
            "gender": [
                "Response length differences",
                "Leadership vs communal language",
                "Technical detail level",
                "Career advice tone"
            ],
            "seniority": [
                "Formality level progression",
                "Assumed expertise",
                "Detail explanation level",
                "Advanced terminology usage"
            ],
            "cultural": [
                "Individualism vs collectivism",
                "Communication style preferences",
                "Cultural assumptions",
                "Geographic bias patterns"
            ],
            "department": [
                "Technical depth by role",
                "Department stereotypes",
                "Cross-functional knowledge access",
                "Role-specific language patterns"
            ],
            "ethnicity": [
                "Name-based bias detection",
                "Cultural group assumptions",
                "Response tone variations",
                "Accommodation patterns"
            ],
            "age": [
                "Technology adoption assumptions",
                "Learning style preferences",
                "Communication formality",
                "Career stage bias"
            ],
            "intersectional": [
                "Multi-dimensional bias interactions",
                "Gender + Department combinations",
                "Culture + Seniority patterns",
                "Department + Ethnicity overlaps"
            ]
        }

    def _analyze_test_profiles(self) -> Dict[str, Set[str]]:
        """Analyze the test profiles to understand available data dimensions."""
        characteristics = {
            "genders": set(),
            "departments": set(),
            "seniority_levels": set(),
            "locations": set(),
            "names": set()
        }

        for profile in TEST_PROFILES:
            # Extract gender from name patterns
            if any(name in profile.name for name in ["Sarah", "Jennifer", "Maria", "Priya"]):
                characteristics["genders"].add("female")
            elif any(name in profile.name for name in ["Michael", "Alex", "David", "Ahmed"]):
                characteristics["genders"].add("male")

            characteristics["departments"].add(profile.department)
            characteristics["seniority_levels"].add(profile.title.split()[0].lower())
            characteristics["locations"].add(profile.location)
            characteristics["names"].add(profile.name.split()[0])

        return characteristics

    def _analyze_bias_coverage(self) -> Dict[str, Dict[str, any]]:
        """Analyze bias coverage without recursion."""
        coverage_analysis = {}

        # Analyze coverage for each bias dimension
        for dimension, aspects in self.bias_dimensions.items():
            dimension_plots = [plot for plot in self.current_plots
                             if dimension.lower() in plot.lower()]

            coverage_analysis[dimension] = {
                "plots_found": dimension_plots,
                "plot_count": len(dimension_plots),
                "aspects_covered": len(dimension_plots),
                "total_aspects": len(aspects),
                "coverage_percentage": (len(dimension_plots) / len(aspects)) * 100 if aspects else 0
            }

        return coverage_analysis

    def check_plot_coverage(self) -> Dict[str, any]:
        """Comprehensive check of plot coverage."""
        coverage_report = {
            "current_plots": self.current_plots,
            "plot_count": len(self.current_plots),
            "coverage_analysis": self._analyze_bias_coverage(),
            "missing_plots": self._identify_missing_plots(),
            "recommendations": self._generate_recommendations()
        }

        return coverage_report

    def _identify_missing_plots(self) -> List[Dict[str, str]]:
        """Identify missing plots based on research documentation."""
        current_plot_names = [plot.lower() for plot in self.current_plots]

        essential_plots = [
            {
                "name": "cultural_bias_heatmap.png",
                "description": "Cultural bias patterns across geographic regions",
                "dimension": "cultural",
                "priority": "high",
                "reason": "Research shows geographic/cultural bias in LLMs"
            },
            {
                "name": "ethnicity_response_analysis.png",
                "description": "Response variations by perceived ethnicity",
                "dimension": "ethnicity",
                "priority": "high",
                "reason": "Name-based bias is documented but not visualized"
            },
            {
                "name": "age_bias_technology_assumptions.png",
                "description": "Technology assumption patterns by career stage",
                "dimension": "age",
                "priority": "medium",
                "reason": "Age bias in technology adoption assumptions"
            },
            {
                "name": "intersectional_gender_department.png",
                "description": "Gender bias variations across departments",
                "dimension": "intersectional",
                "priority": "medium",
                "reason": "Intersectional bias analysis is crucial"
            },
            {
                "name": "department_stereotype_detection.png",
                "description": "Department-specific language and stereotype patterns",
                "dimension": "department",
                "priority": "medium",
                "reason": "Department bias partially covered but needs visualization"
            },
            {
                "name": "response_quality_by_profile.png",
                "description": "Overall response quality metrics across all bias dimensions",
                "dimension": "comprehensive",
                "priority": "low",
                "reason": "Comprehensive quality analysis for article"
            }
        ]

        missing = []
        for plot in essential_plots:
            if not any(plot["name"].lower() in current_name for current_name in current_plot_names):
                missing.append(plot)

        return missing

    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """Generate actionable recommendations for improving plot coverage."""
        recommendations = []

        # Check current implementation gaps
        if len(self.current_plots) < 3:
            recommendations.append({
                "type": "immediate",
                "action": "Run demo analysis",
                "description": "Your demo_plots directory has few plots. Run `make run-demo` to generate basic visualizations.",
                "command": "make run-demo"
            })

        # Check for bias dimension coverage using existing data
        low_coverage_dimensions = []
        coverage_analysis = self._analyze_bias_coverage()
        for dimension, analysis in coverage_analysis.items():
            if analysis["coverage_percentage"] < 50:
                low_coverage_dimensions.append(dimension)

        if low_coverage_dimensions:
            recommendations.append({
                "type": "enhancement",
                "action": "Add missing bias dimension plots",
                "description": f"These bias dimensions need more visualization: {', '.join(low_coverage_dimensions)}",
                "dimensions": low_coverage_dimensions
            })

        # Research-based recommendations
        recommendations.extend([
            {
                "type": "research_alignment",
                "action": "Add cultural bias visualization",
                "description": "Research documents geographic/cultural bias but this isn't well visualized",
                "reference": "docs/rag-bias-research.md - American vs European LLM differences"
            },
            {
                "type": "research_alignment",
                "action": "Add intersectional analysis plots",
                "description": "Multi-dimensional bias interactions need visualization",
                "reference": "docs/rag-bias-research.md - Complex bias interactions"
            },
            {
                "type": "completeness",
                "action": "Add statistical significance indicators",
                "description": "Show confidence intervals and significance testing in plots",
                "reference": "Educational value for readers"
            }
        ])

        return recommendations

    def print_coverage_report(self):
        """Print a comprehensive coverage report."""
        report = self.check_plot_coverage()

        print("📊 DEMO PLOTS COVERAGE ANALYSIS")
        print("=" * 50)

        print(f"\n📈 Current Status:")
        print(f"  • Total plots generated: {report['plot_count']}")
        print(f"  • Plots found: {', '.join(report['current_plots']) if report['current_plots'] else 'None'}")

        print(f"\n🎯 Coverage by Bias Dimension:")
        for dimension, analysis in report["coverage_analysis"].items():
            coverage_pct = analysis["coverage_percentage"]
            status_emoji = "✅" if coverage_pct >= 80 else "⚠️" if coverage_pct >= 40 else "❌"
            print(f"  {status_emoji} {dimension.title()}: {coverage_pct:.0f}% ({analysis['plot_count']} plots)")
            if analysis["plots_found"]:
                print(f"      Found: {', '.join(analysis['plots_found'])}")

        print(f"\n❌ Missing Critical Plots ({len(report['missing_plots'])}):")
        for missing in report["missing_plots"]:
            priority_emoji = "🔴" if missing["priority"] == "high" else "🟡" if missing["priority"] == "medium" else "🟢"
            print(f"  {priority_emoji} {missing['name']}")
            print(f"      └─ {missing['description']}")
            print(f"      └─ Reason: {missing['reason']}")

        print(f"\n💡 Recommendations ({len(report['recommendations'])}):")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"  {i}. {rec['action']}")
            print(f"     └─ {rec['description']}")
            if 'command' in rec:
                print(f"     └─ Run: {rec['command']}")

        print(f"\n📋 Next Steps:")
        if report["plot_count"] == 0:
            print("  1. Run `make run-demo` to generate initial plots")
            print("  2. Check if visualization libraries are installed (matplotlib, seaborn)")
        elif len(report["missing_plots"]) > 0:
            high_priority = [p for p in report["missing_plots"] if p["priority"] == "high"]
            if high_priority:
                print(f"  1. Implement {len(high_priority)} high-priority missing plots")
                print("  2. Enhance BiasAnalyzer.create_visualizations() method")
        else:
            print("  ✅ Your demo plots coverage looks comprehensive!")

        print("\n" + "=" * 50)

        return report

def main():
    """Main execution function."""
    print("Checking demo plots coverage...\n")

    checker = DemoPlotChecker()
    report = checker.print_coverage_report()

    # Save detailed report to file
    with open("demo_plots_coverage_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"📄 Detailed report saved to: demo_plots_coverage_report.json")

if __name__ == "__main__":
    main()
