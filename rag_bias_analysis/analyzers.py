"""
Bias analysis and visualization tools.
"""

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
        """Analyze gender-based response differences."""
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

        # Compare same role, different gender
        same_role_comparison = self.df[
            (self.df["profile"].apply(lambda x: x["title"]) == "Senior Software Engineer")
            & (self.df["inferred_gender"] != "unknown")
        ]

        if len(same_role_comparison) > 0:
            gender_stats = same_role_comparison.groupby("inferred_gender").agg(
                {
                    "response_length": ["mean", "std"],
                    "technical_depth": ["mean", "std"],
                    "encouragement_count": ["mean", "std"],
                }
            )

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
                }

        return {"error": "Insufficient data for gender analysis"}

    def _analyze_seniority_bias(self) -> Dict[str, Any]:
        """Analyze seniority-based response differences."""
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

        # Aggregate by seniority
        seniority_stats = self.df.groupby("seniority_level").agg(
            {
                "response_length": "mean",
                "technical_depth": "mean",
                "assumed_expertise": lambda x: x.value_counts().to_dict() if len(x) > 0 else {},
            }
        )

        return {"seniority_analysis": seniority_stats.to_dict()}

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
        """Analyze cultural/geographic response differences."""
        # Group by location
        location_stats = self.df.groupby(
            self.df["profile"].apply(lambda x: x["location"].split(",")[0])  # City only
        ).agg({"response_length": "mean", "formality_level": "mean", "encouragement_count": "mean"})

        return {"location_analysis": location_stats.to_dict()}

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
