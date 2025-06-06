"""
Bias analysis and visualization tools.
"""

import ast
import os
from typing import Any, Dict

import pandas as pd
from scipy import stats

# Optional visualization imports
try:
    import matplotlib.pyplot as plt
    import seaborn as sns

    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False


class BiasAnalyzer:
    """Analyze bias patterns in test results."""

    def __init__(self, results_df: pd.DataFrame):
        self.df = results_df
        self._prepare_data()

    def _prepare_data(self):
        """Prepare data by parsing string representations and flattening indicators."""
        # Parse profile strings back to dictionaries if they're stored as strings
        if 'profile' in self.df.columns and isinstance(self.df['profile'].iloc[0], str):
            self.df['profile'] = self.df['profile'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

        # Flatten nested bias indicators
        self._flatten_bias_indicators()

    def _flatten_bias_indicators(self):
        """
        Flatten nested bias indicator dictionaries into DataFrame columns.

        This handles the case where bias indicators are stored as nested
        dictionaries (e.g., from ClaudeRAGAnalyzer) and converts them
        to flat column structure for easier analysis.
        """
        # Gender bias indicators
        if "gender_bias_indicators" in self.df.columns:
            for idx, row in self.df.iterrows():
                indicators = row.get("gender_bias_indicators", {})
                if isinstance(indicators, dict):
                    for key, value in indicators.items():
                        if key not in self.df.columns:
                            self.df[key] = 0  # Initialize column
                        self.df.at[idx, key] = value

        # Cultural bias indicators
        if "cultural_bias_indicators" in self.df.columns:
            for idx, row in self.df.iterrows():
                indicators = row.get("cultural_bias_indicators", {})
                if isinstance(indicators, dict):
                    for key, value in indicators.items():
                        if key not in self.df.columns:
                            self.df[key] = 0  # Initialize column
                        self.df.at[idx, key] = value

        # Seniority bias indicators
        if "seniority_bias_indicators" in self.df.columns:
            for idx, row in self.df.iterrows():
                indicators = row.get("seniority_bias_indicators", {})
                if isinstance(indicators, dict):
                    for key, value in indicators.items():
                        if key not in self.df.columns:
                            self.df[key] = 0  # Initialize column
                        self.df.at[idx, key] = value

    def analyze_by_dimension(self, dimension: str) -> Dict[str, Any]:
        """Analyze bias patterns by specific dimension."""

        analyses = {
            "gender": self._analyze_gender_bias,
            "seniority": self._analyze_seniority_bias,
            "department": self._analyze_department_bias,
            "cultural": self._analyze_cultural_bias,
        }

        return analyses.get(dimension, lambda: {})()

    def _analyze_gender_bias(self) -> Dict[str, Any]:
        """
        Analyze gender-based response differences.

        Based on research findings from docs/rag-bias-research.md:
        - "Female applicants are more likely to receive communal words in references,
          while males are more likely to be described as leaders"
        - Tests for leadership vs communal language patterns
        """
        # Extract gender from profiles (simplified - you'd want more sophisticated detection)
        self.df["inferred_gender"] = self.df["profile"].apply(
            lambda p: (
                "female"
                if p.get("pronouns", "") == "she/her"
                else "male"
                if p.get("pronouns", "") == "he/him"
                else "unknown"
            )
        )

        # Compare same role, different gender (Sarah vs Michael Chen - from docs)
        same_role_comparison = self.df[
            (self.df["profile"].apply(lambda x: x["title"]) == "Senior Software Engineer")
            & (self.df["inferred_gender"] != "unknown")
        ]

        if len(same_role_comparison) > 0:
            # Build aggregation dict dynamically based on available columns
            agg_dict = {
                "response_length": ["mean", "std"],
                "technical_depth": ["mean", "std"],
                "encouragement_count": ["mean", "std"],
            }

            # Add gender bias indicators if they exist as flattened columns
            if "leadership_language_count" in same_role_comparison.columns:
                agg_dict["leadership_language_count"] = ["mean", "std"]
            if "communal_language_count" in same_role_comparison.columns:
                agg_dict["communal_language_count"] = ["mean", "std"]

            gender_stats = same_role_comparison.groupby("inferred_gender").agg(agg_dict)

            # Flatten MultiIndex columns for JSON serialization
            gender_stats.columns = ["_".join(col).strip() for col in gender_stats.columns]
            gender_dict = gender_stats.to_dict()

            # Statistical significance test
            male_data = same_role_comparison[same_role_comparison["inferred_gender"] == "male"]
            female_data = same_role_comparison[same_role_comparison["inferred_gender"] == "female"]

            if len(male_data) > 0 and len(female_data) > 0:
                t_stat, p_value = stats.ttest_ind(male_data["response_length"], female_data["response_length"])

                return {
                    "statistics": gender_dict,
                    "significance_test": {"t_statistic": t_stat, "p_value": p_value, "significant": p_value < 0.05},
                    "research_alignment": "Testing for communal vs leadership language patterns per docs/rag-bias-research.md"
                }

        return {"error": "Insufficient data for gender analysis"}

    def _analyze_seniority_bias(self) -> Dict[str, Any]:
        """
        Analyze seniority-based response differences.

        Based on research expectations from docs/rag-bias-research.md:
        "Junior roles could receive more detailed explanations even when not warranted"

        Tests Jennifer progression: Smith (Junior) → Williams (Manager) → Anderson (VP)
        """
        # Extract seniority levels
        seniority_keywords = {
            "junior": ["junior", "intern", "entry"],
            "mid": ["mid", "intermediate"],
            "senior": ["senior", "lead", "principal", "staff"],
            "manager": ["manager", "director", "vp", "head"],
        }

        def get_seniority(title):
            title_lower = title.lower()
            for level, keywords in seniority_keywords.items():
                if any(keyword in title_lower for keyword in keywords):
                    return level
            return "unknown"

        self.df["seniority_level"] = self.df["profile"].apply(lambda x: get_seniority(x["title"]))

        # Focus on Jennifer progression (from docs/rag-test-profiles.md)
        jennifer_progression = self.df[
            self.df["profile"].apply(lambda x: "Jennifer" in x.get("name", ""))
        ]

        # Build aggregation dict based on available columns
        agg_dict = {
            "response_length": "mean",
            "technical_depth": "mean",
        }

        # Add seniority bias indicators if they exist as flattened columns
        if "advanced_terminology_count" in self.df.columns:
            agg_dict["advanced_terminology_count"] = "mean"
        if "beginner_accommodations" in self.df.columns:
            agg_dict["beginner_accommodations"] = "mean"
        if "assumed_expertise" in self.df.columns:
            agg_dict["assumed_expertise"] = lambda x: x.value_counts().to_dict() if len(x) > 0 else {}

        # Aggregate by seniority
        seniority_stats = self.df.groupby("seniority_level").agg(agg_dict)

        result = {
            "seniority_analysis": seniority_stats.to_dict(),
            "research_alignment": "Testing if junior roles receive more detailed explanations per docs/rag-bias-research.md"
        }

        if len(jennifer_progression) > 0:
            result["jennifer_progression_analysis"] = {
                "profiles_tested": ["Jennifer Smith (Junior)", "Jennifer Williams (Manager)", "Jennifer Anderson (VP)"],
                "progression_stats": jennifer_progression.groupby("seniority_level")["response_length"].mean().to_dict()
            }

        return result

    def _analyze_department_bias(self) -> Dict[str, Any]:
        """Analyze department-based response differences."""
        dept_stats = self.df.groupby(self.df["profile"].apply(lambda x: x["department"])).agg(
            {"response_length": ["mean", "std"], "technical_depth": "mean", "formality_level": "mean"}
        )

        # Flatten MultiIndex columns for JSON serialization
        if hasattr(dept_stats.columns, "levels"):  # Check if MultiIndex
            dept_stats.columns = [
                "_".join(str(col)).strip() if isinstance(col, tuple) else str(col) for col in dept_stats.columns
            ]

        return {"department_analysis": dept_stats.to_dict()}

    def _analyze_cultural_bias(self) -> Dict[str, Any]:
        """
        Analyze cultural bias patterns based on documented research.

        From docs/rag-bias-research.md:
        "Cultural values are intrinsic to AI development, with American LLMs emphasizing
        innovation and individualism, European models prioritizing privacy and regulation,
        and Chinese models focusing on harmony and collective well-being"

        Tests profiles: Oluwaseun (Nigeria), Priya (India), John (USA), Anastasia (Russia)
        """
        # Extract location/cultural context from profiles
        cultural_groups = {
            "Western": ["New York, USA", "London", "Dublin", "Tel Aviv"],
            "Asian": ["Seoul", "Mumbai, India", "Singapore"],
            "African": ["Lagos, Nigeria"],
            "Eastern European": ["Moscow, Russia"],
            "Middle Eastern": ["Dubai"],
            "Latin American": ["Mexico City"]
        }

        def get_cultural_group(location):
            for group, locations in cultural_groups.items():
                if any(loc in location for loc in locations):
                    return group
            return "Other"

        self.df["cultural_group"] = self.df["profile"].apply(
            lambda x: get_cultural_group(x.get("location", ""))
        )

        # Focus on Data Scientists from different cultures (from docs/rag-test-profiles.md)
        cultural_comparison = self.df[
            self.df["profile"].apply(lambda x: x.get("title", "") == "Data Scientist")
        ]

        if len(cultural_comparison) > 0:
            # Build aggregation dict based on available columns
            agg_dict = {
                "response_length": ["mean", "std"],
                "formality_level": ["mean", "std"],
            }

            # Add cultural bias indicators if they exist as flattened columns
            if "individualism_emphasis" in cultural_comparison.columns:
                agg_dict["individualism_emphasis"] = ["mean", "std"]
            if "collectivism_emphasis" in cultural_comparison.columns:
                agg_dict["collectivism_emphasis"] = ["mean", "std"]

            cultural_stats = cultural_comparison.groupby("cultural_group").agg(agg_dict)

            # Flatten MultiIndex columns for JSON serialization
            if hasattr(cultural_stats.columns, "levels"):
                cultural_stats.columns = ["_".join(str(col)).strip() for col in cultural_stats.columns]

            return {
                "cultural_statistics": cultural_stats.to_dict(),
                "research_alignment": "Testing individualism vs collectivism per docs/rag-bias-research.md",
                "test_profiles": ["Oluwaseun Adeyemi (Nigeria)", "Priya Sharma (India)", "John Miller (USA)", "Anastasia Volkov (Russia)"]
            }

        return {"error": "Insufficient cultural diversity data for analysis"}

    def create_visualizations(self, output_dir: str = "bias_analysis_plots"):
        """Create visualization plots for bias analysis."""
        if not VISUALIZATION_AVAILABLE:
            print("Visualization libraries not available. Install matplotlib and seaborn to use this feature.")
            return

        os.makedirs(output_dir, exist_ok=True)

        # 1. Response length by gender
        plt.figure(figsize=(10, 6))
        gender_data = self.df[self.df.get("inferred_gender", "unknown") != "unknown"]
        if len(gender_data) > 0:
            sns.boxplot(data=gender_data, x="inferred_gender", y="response_length")
            plt.title("Response Length Distribution by Gender")
            plt.savefig(f"{output_dir}/gender_response_length.png")
            plt.close()

        # 2. Technical depth by department
        plt.figure(figsize=(12, 6))
        dept_pivot = self.df.pivot_table(
            values="technical_depth",
            index=self.df["profile"].apply(lambda x: x["department"]),
            columns="bias_dimension",
            aggfunc="mean",
        )
        sns.heatmap(dept_pivot, annot=True, cmap="coolwarm", center=0)
        plt.title("Technical Depth by Department and Query Type")
        plt.tight_layout()
        plt.savefig(f"{output_dir}/dept_technical_depth_heatmap.png")
        plt.close()

        # 3. Formality level by seniority
        plt.figure(figsize=(10, 6))
        seniority_order = ["intern", "junior", "mid", "senior", "manager"]
        seniority_data = self.df[self.df.get("seniority_level", "unknown").isin(seniority_order)]
        if len(seniority_data) > 0:
            sns.barplot(data=seniority_data, x="seniority_level", y="formality_level", order=seniority_order)
            plt.title("Average Formality Level by Seniority")
            plt.savefig(f"{output_dir}/seniority_formality.png")
            plt.close()
