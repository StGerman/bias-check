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

        # Add derived columns for visualization
        self._add_derived_columns()

    def _add_derived_columns(self):
        """Add derived columns needed for visualization."""
        # Infer gender from pronouns
        def infer_gender(profile):
            if isinstance(profile, dict):
                pronouns = profile.get('pronouns', '').lower()
                if 'she/her' in pronouns:
                    return 'female'
                elif 'he/him' in pronouns:
                    return 'male'
                elif 'they/them' in pronouns:
                    return 'non-binary'
            return 'unknown'

        self.df['inferred_gender'] = self.df['profile'].apply(infer_gender)

        # Infer seniority level from title
        def infer_seniority(profile):
            if isinstance(profile, dict):
                title = profile.get('title', '').lower()
                if 'intern' in title:
                    return 'intern'
                elif 'junior' in title:
                    return 'junior'
                elif 'senior' in title or 'manager' in title:
                    return 'senior'
                elif 'vp' in title or 'director' in title:
                    return 'manager'
                else:
                    return 'mid'
            return 'unknown'

        self.df['seniority_level'] = self.df['profile'].apply(infer_seniority)

    def _flatten_bias_indicators(self):
        """
        Flatten nested bias indicator dictionaries into DataFrame columns.

        This handles the case where bias indicators are stored as nested
        dictionaries (e.g., from ClaudeRAGAnalyzer) and converts them
        to flat column structure for easier analysis.
        """
        # List of all bias indicator types to process
        bias_types = [
            "gender_bias_indicators",
            "cultural_bias_indicators",
            "seniority_bias_indicators",
            "ethnicity_bias_indicators",
            "age_bias_indicators",
            "department_bias_indicators"
        ]

        for bias_type in bias_types:
            if bias_type in self.df.columns:
                for idx, row in self.df.iterrows():
                    indicators = row.get(bias_type, {})
                    if isinstance(indicators, dict):
                        for key, value in indicators.items():
                            column_name = f"{bias_type}_{key}"
                            if column_name not in self.df.columns:
                                self.df[column_name] = 0  # Initialize column
                            self.df.at[idx, column_name] = value

    def analyze_by_dimension(self, dimension: str) -> Dict[str, Any]:
        """Analyze bias patterns by specific dimension."""

        analyses = {
            "gender": self._analyze_gender_bias,
            "seniority": self._analyze_seniority_bias,
            "department": self._analyze_department_bias,
            "cultural": self._analyze_cultural_bias,
            "ethnicity": self._analyze_ethnicity_bias,
            "age": self._analyze_age_bias,
            "intersectional": self._analyze_intersectional_bias,
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

    def _analyze_ethnicity_bias(self) -> Dict[str, Any]:
        """
        Analyze ethnicity-based bias patterns from names.

        Based on research from docs/rag-bias-research.md:
        "LLMs implicitly personalize their responses by inferring user background from names,
        with certain cultures leading to high cultural presumption in responses"

        Tests name-based assumptions: Mohammed (Arabic), Oluwaseun (Nigerian),
        Priya (Indian), John (Anglo), Anastasia (Russian)
        """
        # Categorize names by perceived ethnicity
        ethnicity_patterns = {
            "Arabic/Middle Eastern": ["Mohammed"],
            "Nigerian/African": ["Oluwaseun"],
            "Indian/South Asian": ["Priya"],
            "Anglo/Western": ["John", "Michael", "Sarah", "Jennifer", "David", "Rachel", "Emma", "Alex"],
            "Russian/Eastern European": ["Anastasia"],
            "East Asian": ["Alex Kim"],  # Kim is Korean
            "Latino": ["Carlos"]
        }

        def get_perceived_ethnicity(name):
            for ethnicity, names in ethnicity_patterns.items():
                if any(pattern in name for pattern in names):
                    return ethnicity
            return "Other"

        self.df["perceived_ethnicity"] = self.df["profile"].apply(
            lambda x: get_perceived_ethnicity(x.get("name", ""))
        )

        # Focus on same roles with different ethnic names
        same_role_comparisons = {}
        for role in ["Data Scientist", "Senior Manager", "Intern"]:
            role_data = self.df[
                self.df["profile"].apply(lambda x: x.get("title", "") == role)
            ]
            if len(role_data) > 1:
                same_role_comparisons[role] = role_data

        results = {"ethnicity_analysis_by_role": {}}

        for role, data in same_role_comparisons.items():
            if len(data) > 0:
                # Build aggregation dict based on available columns
                agg_dict = {
                    "response_length": ["mean", "std"],
                    "formality_level": ["mean", "std"],
                }

                # Add ethnicity bias indicators if they exist as flattened columns
                ethnicity_columns = [col for col in data.columns if "ethnicity_bias_indicators" in col]
                for col in ethnicity_columns:
                    agg_dict[col] = ["mean", "std"]

                if len(agg_dict) > 2:  # More than just response_length and formality
                    ethnicity_stats = data.groupby("perceived_ethnicity").agg(agg_dict)

                    # Flatten MultiIndex columns for JSON serialization
                    ethnicity_stats.columns = ["_".join(col).strip() for col in ethnicity_stats.columns]

                    results["ethnicity_analysis_by_role"][role] = {
                        "statistics": ethnicity_stats.to_dict(),
                        "sample_size": len(data),
                        "ethnicities_tested": data["perceived_ethnicity"].unique().tolist()
                    }

        results["research_alignment"] = "Testing name-based cultural assumptions per docs/rag-bias-research.md"
        results["key_patterns_detected"] = [
            "Language simplification patterns",
            "Cultural assumption indicators",
            "Patronizing language ratios"
        ]

        return results

    def _analyze_age_bias(self) -> Dict[str, Any]:
        """
        Analyze age-related bias patterns.

        Based on research from docs/rag-bias-research.md:
        "disparities across demographic groups, showing biases related to age"

        Uses years_at_company and seniority as age proxies.
        """
        # Create age groups based on years at company (proxy for age)
        def get_age_group(years):
            if years <= 1:
                return "Early Career"
            elif years <= 4:
                return "Mid Career"
            elif years <= 7:
                return "Senior Career"
            else:
                return "Veteran"

        self.df["career_stage"] = self.df["profile"].apply(
            lambda x: get_age_group(x.get("years_at_company", 0))
        )

        # Build aggregation dict based on available columns
        agg_dict = {
            "response_length": ["mean", "std"],
            "technical_depth": ["mean", "std"],
        }

        # Add age bias indicators if they exist as flattened columns
        age_columns = [col for col in self.df.columns if "age_bias_indicators" in col]
        for col in age_columns:
            agg_dict[col] = ["mean", "std"]

        age_stats = self.df.groupby("career_stage").agg(agg_dict)

        # Flatten MultiIndex columns for JSON serialization
        age_stats.columns = ["_".join(col).strip() for col in age_stats.columns]

        return {
            "age_statistics": age_stats.to_dict(),
            "research_alignment": "Testing age-related assumptions per docs/rag-bias-research.md",
            "career_stages_tested": self.df["career_stage"].unique().tolist(),
            "age_bias_patterns": [
                "Technology adoption assumptions",
                "Learning style preferences",
                "Communication formality expectations"
            ]
        }

    def _analyze_intersectional_bias(self) -> Dict[str, Any]:
        """
        Analyze bias patterns across multiple dimensions simultaneously.

        Examples:
        - Gender + Seniority: How does advice differ for junior women vs junior men?
        - Ethnicity + Department: Technical responses to engineers with different names
        - Culture + Gender: Leadership advice across cultural and gender lines
        """
        results = {}

        # Gender + Seniority intersection
        if "inferred_gender" in self.df.columns and "seniority_level" in self.df.columns:
            gender_seniority = self.df.groupby(["inferred_gender", "seniority_level"]).agg({
                "response_length": "mean",
                "technical_depth": "mean",
                "formality_level": "mean"
            })

            results["gender_seniority_intersection"] = gender_seniority.to_dict()

        # Ethnicity + Department intersection
        if "perceived_ethnicity" in self.df.columns:
            dept_ethnicity = self.df.groupby([
                self.df["profile"].apply(lambda x: x.get("department", "")),
                "perceived_ethnicity"
            ]).agg({
                "response_length": "mean",
                "technical_depth": "mean"
            })

            results["department_ethnicity_intersection"] = dept_ethnicity.to_dict()

        # Cultural + Gender intersection
        if "cultural_group" in self.df.columns and "inferred_gender" in self.df.columns:
            cultural_gender = self.df.groupby(["cultural_group", "inferred_gender"]).agg({
                "response_length": "mean",
                "formality_level": "mean"
            })

            results["cultural_gender_intersection"] = cultural_gender.to_dict()

        results["research_alignment"] = "Analyzing multi-dimensional bias interactions"

        return results

    def create_visualizations(self, output_dir: str = "bias_analysis_plots"):
        """Create visualization plots for bias analysis."""
        if not VISUALIZATION_AVAILABLE:
            print("Visualization libraries not available. Install matplotlib and seaborn to use this feature.")
            return

        os.makedirs(output_dir, exist_ok=True)

        # Override output_dir to use demo_plots for demo purposes
        if output_dir == "bias_analysis_plots":
            output_dir = "demo_plots"
            os.makedirs(output_dir, exist_ok=True)

        # 1. Response length by gender (existing)
        plt.figure(figsize=(10, 6))
        try:
            gender_mask = self.df["inferred_gender"].fillna("unknown") != "unknown"
            gender_data = self.df[gender_mask]
            if len(gender_data) > 0:
                sns.boxplot(data=gender_data, x="inferred_gender", y="response_length")
                plt.title("Response Length Distribution by Gender")
                plt.ylabel("Response Length (characters)")
                plt.savefig(f"{output_dir}/gender_response_length.png", dpi=300, bbox_inches='tight')
            plt.close()
        except Exception as e:
            print(f"Warning: Could not create gender response length plot: {e}")
            plt.close()

        # 2. Technical depth by department (existing)
        plt.figure(figsize=(12, 6))
        dept_pivot = self.df.pivot_table(
            values="technical_depth",
            index=self.df["profile"].apply(lambda x: x["department"]),
            columns="bias_dimension",
            aggfunc="mean",
        )
        sns.heatmap(dept_pivot, annot=True, cmap="coolwarm", center=0, fmt='.2f')
        plt.title("Technical Depth by Department and Query Type")
        plt.tight_layout()
        plt.savefig(f"{output_dir}/dept_technical_depth_heatmap.png", dpi=300, bbox_inches='tight')
        plt.close()

        # 3. Formality level by seniority (existing)
        plt.figure(figsize=(10, 6))
        try:
            seniority_order = ["intern", "junior", "mid", "senior", "manager"]
            seniority_mask = self.df["seniority_level"].fillna("unknown").isin(seniority_order)
            seniority_data = self.df[seniority_mask]
            if len(seniority_data) > 0:
                sns.barplot(data=seniority_data, x="seniority_level", y="formality_level", order=seniority_order)
                plt.title("Average Formality Level by Seniority")
                plt.ylabel("Formality Score")
                plt.savefig(f"{output_dir}/seniority_formality.png", dpi=300, bbox_inches='tight')
            plt.close()
        except Exception as e:
            print(f"Warning: Could not create seniority formality plot: {e}")
            plt.close()

        # 4. NEW: Cultural bias heatmap (HIGH PRIORITY)
        try:
            self._create_cultural_bias_heatmap(output_dir)
        except Exception as e:
            print(f"Warning: Could not create cultural bias heatmap: {e}")

        # 5. NEW: Ethnicity response analysis (HIGH PRIORITY)
        try:
            self._create_ethnicity_response_analysis(output_dir)
        except Exception as e:
            print(f"Warning: Could not create ethnicity response analysis: {e}")

        # 6. NEW: Age bias technology assumptions (MEDIUM PRIORITY)
        try:
            self._create_age_bias_analysis(output_dir)
        except Exception as e:
            print(f"Warning: Could not create age bias analysis: {e}")

        # 7. NEW: Intersectional gender-department analysis (MEDIUM PRIORITY)
        try:
            self._create_intersectional_gender_department(output_dir)
        except Exception as e:
            print(f"Warning: Could not create intersectional analysis: {e}")

        # 8. NEW: Department stereotype detection (MEDIUM PRIORITY)
        try:
            self._create_department_stereotype_analysis(output_dir)
        except Exception as e:
            print(f"Warning: Could not create department stereotype analysis: {e}")

        # 9. NEW: Response quality by profile overview (LOW PRIORITY)
        try:
            self._create_response_quality_overview(output_dir)
        except Exception as e:
            print(f"Warning: Could not create response quality overview: {e}")

        print(f"📊 Generated comprehensive bias analysis plots in {output_dir}/")

    def _create_cultural_bias_heatmap(self, output_dir: str):
        """Create cultural bias visualization based on geographic regions."""
        plt.figure(figsize=(14, 8))

        # Extract location regions from profiles
        def get_region(location):
            """Map locations to broader regions."""
            region_mapping = {
                'Tel Aviv': 'Middle East', 'Dubai': 'Middle East',
                'London': 'Europe', 'Paris': 'Europe', 'Dublin': 'Europe', 'Barcelona': 'Europe', 'Moscow': 'Europe',
                'New York': 'North America', 'Mexico City': 'North America',
                'Singapore': 'Asia', 'Seoul': 'Asia', 'Mumbai': 'Asia',
                'Lagos': 'Africa',
                'Remote': 'Remote'
            }
            return region_mapping.get(location, 'Other')

        # Add region column
        self.df['region'] = self.df['profile'].apply(lambda x: get_region(x.get('location', 'Unknown')))

        # Create pivot table for cultural bias analysis
        cultural_pivot = self.df.pivot_table(
            values=['response_length', 'technical_depth', 'formality_level'],
            index='region',
            columns='bias_dimension',
            aggfunc='mean'
        )

        # Create subplots for different metrics
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))

        # Response length by region
        if 'response_length' in cultural_pivot.columns.levels[0]:
            sns.heatmap(cultural_pivot['response_length'], annot=True, cmap="viridis", ax=axes[0], fmt='.0f')
            axes[0].set_title("Response Length by Region")
            axes[0].set_ylabel("Geographic Region")

        # Technical depth by region
        if 'technical_depth' in cultural_pivot.columns.levels[0]:
            sns.heatmap(cultural_pivot['technical_depth'], annot=True, cmap="plasma", ax=axes[1], fmt='.2f')
            axes[1].set_title("Technical Depth by Region")
            axes[1].set_ylabel("")

        # Formality by region
        if 'formality_level' in cultural_pivot.columns.levels[0]:
            sns.heatmap(cultural_pivot['formality_level'], annot=True, cmap="coolwarm", ax=axes[2], fmt='.2f')
            axes[2].set_title("Formality Level by Region")
            axes[2].set_ylabel("")

        plt.tight_layout()
        plt.savefig(f"{output_dir}/cultural_bias_heatmap.png", dpi=300, bbox_inches='tight')
        plt.close()

    def _create_ethnicity_response_analysis(self, output_dir: str):
        """Create ethnicity-based response analysis using name patterns."""
        plt.figure(figsize=(12, 8))

        def infer_ethnicity_from_name(name):
            """Infer ethnicity from name patterns (simplified for demo)."""
            name_lower = name.lower()
            if any(pattern in name_lower for pattern in ['chen', 'zhang', 'wei']):
                return 'East Asian'
            elif any(pattern in name_lower for pattern in ['mohammed', 'fatima', 'al-', 'adeyemi']):
                return 'Middle Eastern/African'
            elif any(pattern in name_lower for pattern in ['priya', 'sharma']):
                return 'South Asian'
            elif any(pattern in name_lower for pattern in ['rodriguez', 'gonzalez', 'maria']):
                return 'Hispanic/Latino'
            elif any(pattern in name_lower for pattern in ['volkov', 'anastasia']):
                return 'Eastern European'
            else:
                return 'Western/Anglo'

        # Add ethnicity inference
        self.df['inferred_ethnicity'] = self.df['profile'].apply(lambda x: infer_ethnicity_from_name(x.get('name', '')))

        # Create subplot analysis
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        # Response length by ethnicity
        sns.boxplot(data=self.df, x='inferred_ethnicity', y='response_length', ax=axes[0,0])
        axes[0,0].set_title("Response Length by Inferred Ethnicity")
        axes[0,0].tick_params(axis='x', rotation=45)

        # Technical depth by ethnicity
        sns.violinplot(data=self.df, x='inferred_ethnicity', y='technical_depth', ax=axes[0,1])
        axes[0,1].set_title("Technical Depth by Inferred Ethnicity")
        axes[0,1].tick_params(axis='x', rotation=45)

        # Formality by ethnicity
        sns.barplot(data=self.df, x='inferred_ethnicity', y='formality_level', ax=axes[1,0])
        axes[1,0].set_title("Formality Level by Inferred Ethnicity")
        axes[1,0].tick_params(axis='x', rotation=45)

        # Count of responses by ethnicity
        ethnicity_counts = self.df['inferred_ethnicity'].value_counts()
        axes[1,1].pie(ethnicity_counts.values, labels=ethnicity_counts.index, autopct='%1.1f%%')
        axes[1,1].set_title("Distribution of Test Profiles by Ethnicity")

        plt.tight_layout()
        plt.savefig(f"{output_dir}/ethnicity_response_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()

    def _create_age_bias_analysis(self, output_dir: str):
        """Create age bias analysis using years at company as proxy."""
        plt.figure(figsize=(14, 6))

        def categorize_career_stage(years):
            """Categorize career stage based on years at company."""
            if years == 0:
                return "Entry Level"
            elif years <= 2:
                return "Early Career"
            elif years <= 5:
                return "Mid Career"
            elif years <= 10:
                return "Senior"
            else:
                return "Veteran"

        # Add career stage
        self.df['career_stage'] = self.df['profile'].apply(lambda x: categorize_career_stage(x.get('years_at_company', 0)))

        # Create analysis plots
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))

        # Technology assumption patterns by career stage
        stage_order = ["Entry Level", "Early Career", "Mid Career", "Senior", "Veteran"]

        # Technical depth assumptions
        stage_data = self.df[self.df['career_stage'].isin(stage_order)]
        if len(stage_data) > 0:
            sns.boxplot(data=stage_data, x='career_stage', y='technical_depth', order=stage_order, ax=axes[0])
            axes[0].set_title("Technical Depth Assumptions by Career Stage")
            axes[0].set_xlabel("Career Stage")
            axes[0].set_ylabel("Technical Depth Score")
            axes[0].tick_params(axis='x', rotation=45)

        # Response formality by career stage
        if len(stage_data) > 0:
            sns.violinplot(data=stage_data, x='career_stage', y='formality_level', order=stage_order, ax=axes[1])
            axes[1].set_title("Response Formality by Career Stage")
            axes[1].set_xlabel("Career Stage")
            axes[1].set_ylabel("Formality Level")
            axes[1].tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.savefig(f"{output_dir}/age_bias_technology_assumptions.png", dpi=300, bbox_inches='tight')
        plt.close()

    def _create_intersectional_gender_department(self, output_dir: str):
        """Create intersectional analysis of gender bias across departments."""
        plt.figure(figsize=(14, 8))

        # Filter for profiles with gender information
        gender_mask = (self.df["inferred_gender"] != "unknown") & (self.df["inferred_gender"].notna())
        gendered_data = self.df[gender_mask]

        if len(gendered_data) > 0:
            # Ensure department column exists
            if 'department' not in gendered_data.columns:
                gendered_data = gendered_data.copy()
                gendered_data['department'] = gendered_data['profile'].apply(lambda x: x.get('department', 'Unknown') if isinstance(x, dict) else 'Unknown')

            # Create pivot table for intersectional analysis
            intersectional_pivot = gendered_data.pivot_table(
                values=['response_length', 'technical_depth', 'formality_level'],
                index='department',
                columns='inferred_gender',
                aggfunc='mean'
            )

            # Create subplots
            fig, axes = plt.subplots(1, 3, figsize=(18, 6))

            # Response length gender gap by department
            if 'response_length' in intersectional_pivot.columns.levels[0]:
                sns.heatmap(intersectional_pivot['response_length'], annot=True, cmap="RdBu_r",
                           center=intersectional_pivot['response_length'].mean().mean(), ax=axes[0], fmt='.0f')
                axes[0].set_title("Response Length: Gender by Department")
                axes[0].set_ylabel("Department")

            # Technical depth gender gap by department
            if 'technical_depth' in intersectional_pivot.columns.levels[0]:
                sns.heatmap(intersectional_pivot['technical_depth'], annot=True, cmap="RdBu_r",
                           center=intersectional_pivot['technical_depth'].mean().mean(), ax=axes[1], fmt='.2f')
                axes[1].set_title("Technical Depth: Gender by Department")
                axes[1].set_ylabel("")

            # Formality gender gap by department
            if 'formality_level' in intersectional_pivot.columns.levels[0]:
                sns.heatmap(intersectional_pivot['formality_level'], annot=True, cmap="RdBu_r",
                           center=intersectional_pivot['formality_level'].mean().mean(), ax=axes[2], fmt='.2f')
                axes[2].set_title("Formality Level: Gender by Department")
                axes[2].set_ylabel("")

            plt.tight_layout()
            plt.savefig(f"{output_dir}/intersectional_gender_department.png", dpi=300, bbox_inches='tight')
            plt.close()

    def _create_department_stereotype_analysis(self, output_dir: str):
        """Create department-specific stereotype detection visualization."""
        plt.figure(figsize=(14, 10))

        # Create comprehensive department analysis
        # Add department column for easier grouping
        self.df['department'] = self.df['profile'].apply(lambda x: x.get('department', 'Unknown') if isinstance(x, dict) else 'Unknown')

        dept_data = self.df.groupby('department').agg({
            'response_length': ['mean', 'std'],
            'technical_depth': ['mean', 'std'],
            'formality_level': ['mean', 'std']
        }).round(2)

        # Flatten column names
        dept_data.columns = ['_'.join(col).strip() for col in dept_data.columns.values]

        # Create subplots for stereotype patterns
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # Mean response characteristics by department
        mean_cols = [col for col in dept_data.columns if 'mean' in col]
        if mean_cols:
            dept_data[mean_cols].plot(kind='bar', ax=axes[0,0])
            axes[0,0].set_title("Average Response Characteristics by Department")
            axes[0,0].set_ylabel("Score")
            axes[0,0].tick_params(axis='x', rotation=45)
            axes[0,0].legend(['Response Length', 'Technical Depth', 'Formality Level'])

        # Variation (std) by department - higher variation might indicate bias
        std_cols = [col for col in dept_data.columns if 'std' in col]
        if std_cols:
            dept_data[std_cols].plot(kind='bar', ax=axes[0,1], color=['orange', 'red', 'purple'])
            axes[0,1].set_title("Response Variation by Department")
            axes[0,1].set_ylabel("Standard Deviation")
            axes[0,1].tick_params(axis='x', rotation=45)
            axes[0,1].legend(['Response Length Std', 'Technical Depth Std', 'Formality Level Std'])

        # Department vs query type heatmap
        if 'bias_dimension' in self.df.columns:
            dept_query_pivot = self.df.pivot_table(
                values='technical_depth',
                index='department',
                columns='bias_dimension',
                aggfunc='mean'
            )
            sns.heatmap(dept_query_pivot, annot=True, cmap="viridis", ax=axes[1,0], fmt='.2f')
            axes[1,0].set_title("Technical Depth by Department & Query Type")
            axes[1,0].set_ylabel("Department")

        # Department response length distribution
        self.df.boxplot(column='response_length',
                       by='department',
                       ax=axes[1,1])
        axes[1,1].set_title("Response Length Distribution by Department")
        axes[1,1].set_xlabel("Department")
        axes[1,1].set_ylabel("Response Length")

        plt.tight_layout()
        plt.savefig(f"{output_dir}/department_stereotype_detection.png", dpi=300, bbox_inches='tight')
        plt.close()

    def _create_response_quality_overview(self, output_dir: str):
        """Create comprehensive response quality overview across all bias dimensions."""
        plt.figure(figsize=(16, 12))

        # Create comprehensive quality metrics
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))

        # 1. Overall quality distribution
        quality_metrics = ['response_length', 'technical_depth', 'formality_level']
        self.df[quality_metrics].hist(bins=15, ax=axes[0,0], alpha=0.7)
        axes[0,0].set_title("Overall Response Quality Distribution")
        axes[0,0].legend(quality_metrics)

        # 2. Quality correlation matrix
        if len(quality_metrics) >= 2:
            corr_matrix = self.df[quality_metrics].corr()
            sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", center=0, ax=axes[0,1])
            axes[0,1].set_title("Quality Metrics Correlation")

        # 3. Quality by profile characteristics
        if 'inferred_gender' in self.df.columns:
            quality_by_gender = self.df.groupby('inferred_gender')[quality_metrics].mean()
            quality_by_gender.plot(kind='bar', ax=axes[0,2])
            axes[0,2].set_title("Average Quality by Gender")
            axes[0,2].tick_params(axis='x', rotation=45)

        # 4. Response length vs technical depth scatter
        if 'inferred_gender' in self.df.columns:
            for gender in self.df['inferred_gender'].unique():
                if gender != 'unknown':
                    gender_data = self.df[self.df['inferred_gender'] == gender]
                    axes[1,0].scatter(gender_data['response_length'], gender_data['technical_depth'],
                                    label=gender, alpha=0.7)
            axes[1,0].set_xlabel("Response Length")
            axes[1,0].set_ylabel("Technical Depth")
            axes[1,0].set_title("Response Length vs Technical Depth")
            axes[1,0].legend()

        # 5. Query type performance
        if 'bias_dimension' in self.df.columns:
            query_performance = self.df.groupby('bias_dimension')[quality_metrics].mean()
            query_performance.plot(kind='bar', ax=axes[1,1])
            axes[1,1].set_title("Quality Metrics by Query Type")
            axes[1,1].tick_params(axis='x', rotation=45)

        # 6. Statistical significance indicators (placeholder for future enhancement)
        axes[1,2].text(0.5, 0.5, "Statistical Significance\nTesting Placeholder\n\n" +
                      "Future Enhancement:\n• T-tests for group differences\n• ANOVA for multiple groups\n" +
                      "• Effect size calculations\n• Confidence intervals",
                      ha='center', va='center', transform=axes[1,2].transAxes,
                      bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
        axes[1,2].set_title("Statistical Testing Framework")
        axes[1,2].set_xticks([])
        axes[1,2].set_yticks([])

        plt.tight_layout()
        plt.savefig(f"{output_dir}/response_quality_by_profile.png", dpi=300, bbox_inches='tight')
        plt.close()
