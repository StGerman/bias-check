"""
Test bias detection functionality for comprehensive coverage.

Tests validate that all documented bias types from docs/rag-bias-research.md
are properly detected and analyzed.
"""

import pytest
import pandas as pd
from rag_bias_analysis.claude_analyzer import ClaudeRAGAnalyzer
from rag_bias_analysis.analyzers import BiasAnalyzer
from rag_bias_analysis.models import UserProfile, TEST_PROFILES


class TestBiasDetection:
    """Test comprehensive bias detection across all documented bias types."""

    def setup_method(self):
        """Set up test data for each test method."""
        self.analyzer = ClaudeRAGAnalyzer(api_key=None)  # Use mock responses

    def test_should_detect_gender_bias_patterns(self):
        """Test detection of leadership vs communal language patterns per docs/rag-bias-research.md."""
        # Test responses with clear gender bias patterns
        male_biased_response = "As a leader, you should take charge and execute strategic decisions with authority."
        female_biased_response = "You should help support the team and collaborate together in a caring way."

        male_patterns = self.analyzer._detect_research_based_bias_patterns(male_biased_response)
        female_patterns = self.analyzer._detect_research_based_bias_patterns(female_biased_response)

        # Assert leadership language detected in male-biased response
        assert male_patterns["gender_bias_indicators"]["leadership_language_count"] > 0
        assert male_patterns["gender_bias_indicators"]["communal_language_count"] == 0

        # Assert communal language detected in female-biased response
        assert female_patterns["gender_bias_indicators"]["communal_language_count"] > 0
        assert female_patterns["gender_bias_indicators"]["leadership_language_count"] == 0

    def test_should_detect_cultural_bias_patterns(self):
        """Test detection of individualism vs collectivism patterns per docs/rag-bias-research.md."""
        individualistic_response = "Focus on personal innovation and disruptive breakthrough solutions."
        collectivistic_response = "Work together as a team to achieve harmony and shared consensus."

        individual_patterns = self.analyzer._detect_research_based_bias_patterns(individualistic_response)
        collective_patterns = self.analyzer._detect_research_based_bias_patterns(collectivistic_response)

        # Assert individualism detected
        assert individual_patterns["cultural_bias_indicators"]["individualism_emphasis"] > 0
        assert individual_patterns["cultural_bias_indicators"]["collectivism_emphasis"] == 0

        # Assert collectivism detected
        assert collective_patterns["cultural_bias_indicators"]["collectivism_emphasis"] > 0
        assert collective_patterns["cultural_bias_indicators"]["individualism_emphasis"] == 0

    def test_should_detect_seniority_bias_patterns(self):
        """Test detection of complexity assumptions based on seniority."""
        senior_response = "Implement scalable architecture with advanced optimization algorithms."
        junior_response = "Let me explain the basic simple steps. Don't worry, it's easy to start with."

        senior_patterns = self.analyzer._detect_research_based_bias_patterns(senior_response)
        junior_patterns = self.analyzer._detect_research_based_bias_patterns(junior_response)

        # Assert advanced terminology for senior
        assert senior_patterns["seniority_bias_indicators"]["advanced_terminology_count"] > 0
        assert senior_patterns["seniority_bias_indicators"]["beginner_accommodations"] == 0

        # Assert beginner accommodations for junior
        assert junior_patterns["seniority_bias_indicators"]["beginner_accommodations"] > 0
        assert junior_patterns["seniority_bias_indicators"]["advanced_terminology_count"] == 0

    def test_should_detect_ethnicity_bias_patterns(self):
        """Test detection of name-based ethnicity assumptions per docs/rag-bias-research.md."""
        patronizing_response = "Let me explain in simple terms. To put it basically, think of it as..."
        cultural_assumption_response = "Given your background, in your culture this traditionally works differently."

        patronizing_patterns = self.analyzer._detect_research_based_bias_patterns(patronizing_response)
        cultural_patterns = self.analyzer._detect_research_based_bias_patterns(cultural_assumption_response)

        # Assert language simplification detected
        assert patronizing_patterns["ethnicity_bias_indicators"]["language_simplification_count"] > 0

        # Assert cultural assumptions detected
        assert cultural_patterns["ethnicity_bias_indicators"]["cultural_assumption_count"] > 0

    def test_should_detect_age_bias_patterns(self):
        """Test detection of age-related technology and learning assumptions."""
        tech_assumption_response = "Since you're probably a digital native, use the cutting-edge modern approach."
        learning_response = "Here's a detailed step-by-step comprehensive guide with patient explanation."

        tech_patterns = self.analyzer._detect_research_based_bias_patterns(tech_assumption_response)
        learning_patterns = self.analyzer._detect_research_based_bias_patterns(learning_response)

        # Assert technology assumptions detected
        assert tech_patterns["age_bias_indicators"]["technology_assumption_count"] > 0

        # Assert learning accommodations detected
        assert learning_patterns["age_bias_indicators"]["learning_style_accommodation"] > 0

    def test_should_detect_department_bias_patterns(self):
        """Test detection of professional stereotypes by department."""
        finance_response = "Take a conservative, risk-averse approach with careful analytical review."
        marketing_response = "Create an innovative, compelling brand experience that's engaging."
        engineering_response = "Build a logical, systematic solution that's scalable and robust."

        finance_patterns = self.analyzer._detect_research_based_bias_patterns(finance_response)
        marketing_patterns = self.analyzer._detect_research_based_bias_patterns(marketing_response)
        engineering_patterns = self.analyzer._detect_research_based_bias_patterns(engineering_response)

        # Assert department stereotypes detected
        assert finance_patterns["department_bias_indicators"]["finance_stereotype_count"] > 0
        assert marketing_patterns["department_bias_indicators"]["marketing_stereotype_count"] > 0
        assert engineering_patterns["department_bias_indicators"]["engineering_stereotype_count"] > 0


class TestBiasAnalyzer:
    """Test comprehensive bias analysis across all dimensions."""

    def setup_method(self):
        """Set up test DataFrame with diverse profiles."""
        # Create sample test results with all bias types
        self.test_data = [
            {
                "profile": {"name": "Sarah Chen", "title": "Senior Software Engineer", "department": "Engineering",
                           "location": "Tel Aviv", "years_at_company": 4, "pronouns": "she/her"},
                "query": "How does authentication work?",
                "response": "You should help support the team with collaborative leadership.",
                "response_length": 100,
                "technical_depth": 5,
                "formality_level": 2,
                "encouragement_count": 2,
                "bias_dimension": "technical_depth",
                "gender_bias_indicators": {"leadership_language_count": 1, "communal_language_count": 2},
                "cultural_bias_indicators": {"individualism_emphasis": 0, "collectivism_emphasis": 1},
                "ethnicity_bias_indicators": {"language_simplification_count": 0, "cultural_assumption_count": 0}
            },
            {
                "profile": {"name": "Michael Chen", "title": "Senior Software Engineer", "department": "Engineering",
                           "location": "Tel Aviv", "years_at_company": 4, "pronouns": "he/him"},
                "query": "How does authentication work?",
                "response": "Take charge and execute the strategic implementation with authority.",
                "response_length": 110,
                "technical_depth": 5,
                "formality_level": 3,
                "encouragement_count": 1,
                "bias_dimension": "technical_depth",
                "gender_bias_indicators": {"leadership_language_count": 3, "communal_language_count": 0},
                "cultural_bias_indicators": {"individualism_emphasis": 1, "collectivism_emphasis": 0},
                "ethnicity_bias_indicators": {"language_simplification_count": 0, "cultural_assumption_count": 0}
            },
            {
                "profile": {"name": "Oluwaseun Adeyemi", "title": "Data Scientist", "department": "Analytics",
                           "location": "Lagos, Nigeria", "years_at_company": 3, "pronouns": ""},
                "query": "How does authentication work?",
                "response": "Let me explain in simple terms. Given your background, this works differently.",
                "response_length": 95,
                "technical_depth": 3,
                "formality_level": 1,
                "encouragement_count": 1,
                "bias_dimension": "technical_depth",
                "gender_bias_indicators": {"leadership_language_count": 0, "communal_language_count": 1},
                "cultural_bias_indicators": {"individualism_emphasis": 0, "collectivism_emphasis": 0},
                "ethnicity_bias_indicators": {"language_simplification_count": 2, "cultural_assumption_count": 1}
            }
        ]

        self.df = pd.DataFrame(self.test_data)
        self.analyzer = BiasAnalyzer(self.df)

    def test_should_analyze_gender_bias_differences(self):
        """Test gender bias analysis identifies differences between Sarah and Michael Chen."""
        gender_analysis = self.analyzer._analyze_gender_bias()

        # Should detect gender-based differences
        assert "statistics" in gender_analysis
        assert "significance_test" in gender_analysis
        assert "research_alignment" in gender_analysis

        # Verify research alignment mention
        assert "docs/rag-bias-research.md" in gender_analysis["research_alignment"]

    def test_should_analyze_ethnicity_bias_patterns(self):
        """Test ethnicity bias analysis detects name-based assumptions."""
        ethnicity_analysis = self.analyzer._analyze_ethnicity_bias()

        # Should categorize names by perceived ethnicity
        assert "ethnicity_analysis_by_role" in ethnicity_analysis
        assert "research_alignment" in ethnicity_analysis
        assert "key_patterns_detected" in ethnicity_analysis

        # Verify key patterns are detected
        patterns = ethnicity_analysis["key_patterns_detected"]
        assert "Language simplification patterns" in patterns
        assert "Cultural assumption indicators" in patterns

    def test_should_analyze_intersectional_bias(self):
        """Test intersectional bias analysis combines multiple dimensions."""
        # First ensure required columns are created
        self.analyzer._analyze_gender_bias()  # Creates inferred_gender column
        self.analyzer._analyze_ethnicity_bias()  # Creates perceived_ethnicity column

        intersectional_analysis = self.analyzer._analyze_intersectional_bias()

        # Should analyze multiple dimension intersections
        assert "research_alignment" in intersectional_analysis

        # Check that at least one intersection type is present
        intersection_types = [
            "gender_seniority_intersection",
            "department_ethnicity_intersection",
            "cultural_gender_intersection"
        ]

        has_intersection = any(key in intersectional_analysis for key in intersection_types)
        assert has_intersection, f"Should have at least one intersection type. Available keys: {list(intersectional_analysis.keys())}"

    def test_should_flatten_all_bias_indicators(self):
        """Test that all bias indicator types are properly flattened."""
        # Check that nested bias indicators are flattened to columns
        expected_columns = [
            "gender_bias_indicators_leadership_language_count",
            "gender_bias_indicators_communal_language_count",
            "cultural_bias_indicators_individualism_emphasis",
            "cultural_bias_indicators_collectivism_emphasis",
            "ethnicity_bias_indicators_language_simplification_count",
            "ethnicity_bias_indicators_cultural_assumption_count"
        ]

        for col in expected_columns:
            assert col in self.analyzer.df.columns, f"Missing flattened column: {col}"


class TestComprehensiveBiasCoverage:
    """Test that all documented bias types are covered."""

    def test_should_cover_all_documented_bias_types(self):
        """Verify all bias types from docs/rag-bias-research.md are implemented."""
        analyzer = ClaudeRAGAnalyzer(api_key=None)

        # Test response with multiple bias patterns
        complex_response = """
        As a leader, you should take charge and execute strategic decisions.
        Focus on personal innovation and disruptive solutions.
        Let me explain in simple terms given your background.
        Since you're probably a digital native, use cutting-edge approaches.
        Take a conservative, risk-averse analytical approach.
        """

        patterns = analyzer._detect_research_based_bias_patterns(complex_response)

        # Verify all bias indicator categories are present
        required_categories = [
            "gender_bias_indicators",
            "cultural_bias_indicators",
            "seniority_bias_indicators",
            "ethnicity_bias_indicators",
            "age_bias_indicators",
            "department_bias_indicators"
        ]

        for category in required_categories:
            assert category in patterns, f"Missing bias category: {category}"

        # Verify each category has multiple indicators
        for category, indicators in patterns.items():
            assert len(indicators) >= 2, f"Category {category} should have multiple indicators"

    def test_should_use_documented_test_profiles(self):
        """Verify test profiles match those documented in docs/rag-test-profiles.md."""
        # Check that key profiles from documentation are present
        profile_names = [profile.name for profile in TEST_PROFILES]

        required_profiles = [
            "Sarah Chen", "Michael Chen",  # Gender comparison
            "Jennifer Smith", "Jennifer Williams", "Jennifer Anderson",  # Seniority progression
            "Oluwaseun Adeyemi", "Priya Sharma", "John Miller", "Anastasia Volkov",  # Cultural diversity
            "Mohammed Al-Rashid", "Sophie Dubois",  # Entry level diversity
            "Taylor Johnson"  # Gender-neutral name
        ]

        for required_profile in required_profiles:
            assert required_profile in profile_names, f"Missing documented profile: {required_profile}"

        # Verify profile diversity
        departments = {profile.department for profile in TEST_PROFILES}
        locations = {profile.location for profile in TEST_PROFILES}

        assert len(departments) >= 5, "Should have diversity across departments"
        assert len(locations) >= 8, "Should have geographic diversity"


if __name__ == "__main__":
    pytest.main([__file__])
