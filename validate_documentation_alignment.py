#!/usr/bin/env python3
"""
Documentation Alignment Validation Script

This script validates that the codebase aligns with the documentation
in docs/rag-bias-research.md and docs/rag-test-profiles.md as required
by the GitHub Copilot instructions.
"""

import re
from pathlib import Path
from typing import Dict, List

from rag_bias_analysis.models import TEST_PROFILES, TEST_QUERIES


class DocumentationValidator:
    """Validates alignment between code and documentation."""

    def __init__(self):
        self.docs_dir = Path("docs")
        self.profiles_file = self.docs_dir / "rag-test-profiles.md"
        self.research_file = self.docs_dir / "rag-bias-research.md"

    def validate_profile_alignment(self) -> Dict[str, any]:
        """
        Validate that TEST_PROFILES align with docs/rag-test-profiles.md.

        Returns validation results with any misalignments found.
        """
        results = {
            "status": "PASS",
            "issues": [],
            "validated_profiles": [],
            "missing_profiles": [],
            "extra_profiles": []
        }

        if not self.profiles_file.exists():
            results["status"] = "FAIL"
            results["issues"].append("docs/rag-test-profiles.md not found")
            return results

        # Read documented profiles
        content = self.profiles_file.read_text()
        documented_profiles = self._extract_documented_profiles(content)

        # Compare with code profiles
        code_profile_names = {p.name for p in TEST_PROFILES}
        documented_names = {p["name"] for p in documented_profiles}

        # Check for missing profiles (in docs but not in code)
        missing = documented_names - code_profile_names
        if missing:
            results["status"] = "FAIL"
            results["missing_profiles"] = list(missing)
            results["issues"].append(f"Missing profiles in code: {missing}")

        # Check for extra profiles (in code but not in docs)
        extra = code_profile_names - documented_names
        if extra:
            results["status"] = "FAIL"
            results["extra_profiles"] = list(extra)
            results["issues"].append(f"Extra profiles in code: {extra}")

        # Validate profile details for matching names
        for code_profile in TEST_PROFILES:
            matching_doc = next(
                (p for p in documented_profiles if p["name"] == code_profile.name),
                None
            )
            if matching_doc:
                profile_issues = self._validate_profile_details(code_profile, matching_doc)
                if profile_issues:
                    results["status"] = "FAIL"
                    results["issues"].extend(profile_issues)
                else:
                    results["validated_profiles"].append(code_profile.name)

        return results

    def validate_research_alignment(self) -> Dict[str, any]:
        """
        Validate that bias detection methods align with docs/rag-bias-research.md.

        Checks for implementation of documented research findings.
        """
        results = {
            "status": "PASS",
            "issues": [],
            "implemented_findings": [],
            "missing_implementations": []
        }

        if not self.research_file.exists():
            results["status"] = "FAIL"
            results["issues"].append("docs/rag-bias-research.md not found")
            return results

        # Check for key research findings implementation
        research_patterns = {
            "gender_bias": {
                "finding": "Female applicants are more likely to receive communal words in references, while males are more likely to be described as leaders",
                "implementation_indicators": ["leadership_words", "communal_words", "gender_bias_indicators"]
            },
            "cultural_bias": {
                "finding": "American LLMs emphasizing innovation and individualism, European models prioritizing privacy and regulation",
                "implementation_indicators": ["individualism_words", "collectivism_words", "cultural_bias_indicators"]
            },
            "seniority_bias": {
                "finding": "Junior roles could receive more detailed explanations even when not warranted",
                "implementation_indicators": ["beginner_indicators", "complexity_score", "seniority_bias_indicators"]
            }
        }

        # Check implementations in code files
        code_files = [
            "rag_bias_analysis/claude_analyzer.py",
            "rag_bias_analysis/core.py",
            "rag_bias_analysis/analyzers.py"
        ]

        for pattern_name, pattern_info in research_patterns.items():
            implemented = self._check_research_implementation(code_files, pattern_info["implementation_indicators"])
            if implemented:
                results["implemented_findings"].append(pattern_name)
            else:
                results["status"] = "FAIL"
                results["missing_implementations"].append(pattern_name)
                results["issues"].append(f"Missing implementation for {pattern_name}: {pattern_info['finding']}")

        return results

    def validate_query_alignment(self) -> Dict[str, any]:
        """
        Validate that TEST_QUERIES align with documented test queries.
        """
        results = {
            "status": "PASS",
            "issues": [],
            "validated_queries": [],
            "missing_queries": []
        }

        if not self.profiles_file.exists():
            results["status"] = "FAIL"
            results["issues"].append("docs/rag-test-profiles.md not found")
            return results

        content = self.profiles_file.read_text()
        documented_queries = self._extract_documented_queries(content)

        # Check if documented queries are implemented
        code_query_texts = {q["query"] for q in TEST_QUERIES}
        documented_texts = {q["query"] for q in documented_queries}

        missing = documented_texts - code_query_texts
        if missing:
            results["status"] = "FAIL"
            results["missing_queries"] = list(missing)
            results["issues"].append(f"Missing queries in code: {missing}")
        else:
            results["validated_queries"] = list(documented_texts & code_query_texts)

        return results

    def _extract_documented_profiles(self, content: str) -> List[Dict[str, str]]:
        """Extract profile information from documentation."""
        profiles = []

        # Split into lines and process each line that looks like a profile
        lines = content.split('\n')
        for line in lines:
            # Match profile lines like: "1. **Sarah Chen** - Senior Software Engineer, Engineering, Tel Aviv, 4 years, she/her"
            # Handle cases with and without pronouns, and complex locations
            match = re.match(r'^(\d+)\.\s+\*\*([^*]+)\*\*\s+-\s+(.+)', line.strip())
            if match:
                _, name, rest = match.groups()

                # Split the rest by commas and process based on expected structure
                parts = [part.strip() for part in rest.split(',')]

                if len(parts) >= 4:  # At minimum: title, department, location, years
                    title = parts[0]
                    department = parts[1]

                    # Find the years part - it contains a number followed by "year" or "years"
                    years_part = None
                    years_idx = None
                    for i, part in enumerate(parts):
                        if re.search(r'\d+\s+years?', part):
                            years_part = part
                            years_idx = i
                            break

                    if years_part and years_idx is not None and years_idx >= 2:
                        # Location is everything between department (index 1) and years (years_idx)
                        if years_idx == 2:
                            # Simple location like "Tel Aviv"
                            location = parts[2] if years_idx == 2 else ""
                        else:
                            # Complex location like "Lagos, Nigeria" or "New York, USA"
                            location_parts = parts[2:years_idx]
                            location = ', '.join(location_parts)

                        # Extract years number
                        years_match = re.search(r'(\d+)\s+years?', years_part)
                        years = int(years_match.group(1)) if years_match else 0

                        # Pronouns (if any) come after years part
                        pronouns = ""
                        if years_idx + 1 < len(parts):
                            potential_pronouns = parts[years_idx + 1].strip()
                            # Check if it looks like pronouns (contains / and common pronouns)
                            if '/' in potential_pronouns and any(p in potential_pronouns.lower() for p in ['he', 'she', 'they']):
                                pronouns = potential_pronouns

                        profiles.append({
                            "name": name.strip(),
                            "title": title.strip(),
                            "department": department.strip(),
                            "location": location.strip(),
                            "years": years,
                            "pronouns": pronouns
                        })

        return profiles

    def _extract_documented_queries(self, content: str) -> List[Dict[str, str]]:
        """Extract query information from documentation."""
        queries = []

        # Pattern to match query sections
        query_pattern = r'\*\*Query\*\*:\s+"([^"]+)"\s+- \*\*Bias Dimension\*\*:\s+([^\n]+)'

        matches = re.findall(query_pattern, content)
        for query_text, bias_dimension in matches:
            queries.append({
                "query": query_text.strip(),
                "bias_dimension": bias_dimension.strip()
            })

        return queries

    def _validate_profile_details(self, code_profile, doc_profile) -> List[str]:
        """Validate that profile details match between code and documentation."""
        issues = []

        if code_profile.title != doc_profile["title"]:
            issues.append(f"{code_profile.name}: Title mismatch - Code: '{code_profile.title}', Docs: '{doc_profile['title']}'")

        if code_profile.department != doc_profile["department"]:
            issues.append(f"{code_profile.name}: Department mismatch - Code: '{code_profile.department}', Docs: '{doc_profile['department']}'")

        if code_profile.location != doc_profile["location"]:
            issues.append(f"{code_profile.name}: Location mismatch - Code: '{code_profile.location}', Docs: '{doc_profile['location']}'")

        if code_profile.years_at_company != doc_profile["years"]:
            issues.append(f"{code_profile.name}: Years mismatch - Code: {code_profile.years_at_company}, Docs: {doc_profile['years']}")

        return issues

    def _check_research_implementation(self, code_files: List[str], indicators: List[str]) -> bool:
        """Check if research findings are implemented in code."""
        for file_path in code_files:
            if Path(file_path).exists():
                content = Path(file_path).read_text(encoding='utf-8')
                if any(indicator in content for indicator in indicators):
                    return True
        return False

    def run_full_validation(self) -> Dict[str, any]:
        """Run all validation checks."""
        print("🔍 Validating documentation alignment...")

        profile_results = self.validate_profile_alignment()
        research_results = self.validate_research_alignment()
        query_results = self.validate_query_alignment()

        overall_status = "PASS"
        if any(r["status"] == "FAIL" for r in [profile_results, research_results, query_results]):
            overall_status = "FAIL"

        results = {
            "overall_status": overall_status,
            "profile_validation": profile_results,
            "research_validation": research_results,
            "query_validation": query_results,
            "summary": {
                "total_profiles_validated": len(profile_results.get("validated_profiles", [])),
                "total_research_findings_implemented": len(research_results.get("implemented_findings", [])),
                "total_queries_validated": len(query_results.get("validated_queries", []))
            }
        }

        return results


def main():
    """Run documentation validation and report results."""
    validator = DocumentationValidator()
    results = validator.run_full_validation()

    print("\n" + "="*60)
    print("📋 DOCUMENTATION ALIGNMENT VALIDATION REPORT")
    print("="*60)

    print(f"\n🎯 Overall Status: {results['overall_status']}")

    # Profile validation results
    profile_results = results["profile_validation"]
    print(f"\n👥 Profile Validation: {profile_results['status']}")
    print(f"   ✅ Validated Profiles: {len(profile_results.get('validated_profiles', []))}")
    if profile_results.get("missing_profiles"):
        print(f"   ❌ Missing Profiles: {profile_results['missing_profiles']}")
    if profile_results.get("extra_profiles"):
        print(f"   ⚠️  Extra Profiles: {profile_results['extra_profiles']}")

    # Research validation results
    research_results = results["research_validation"]
    print(f"\n🔬 Research Implementation: {research_results['status']}")
    print("   ✅ Implemented Findings:", research_results.get('implemented_findings', []))
    if research_results.get("missing_implementations"):
        print("   ❌ Missing Implementations:", research_results['missing_implementations'])

    # Query validation results
    query_results = results["query_validation"]
    print(f"\n❓ Query Validation: {query_results['status']}")
    print(f"   ✅ Validated Queries: {len(query_results.get('validated_queries', []))}")
    if query_results.get("missing_queries"):
        print(f"   ❌ Missing Queries: {len(query_results['missing_queries'])}")

    # Issues summary
    all_issues = []
    all_issues.extend(profile_results.get("issues", []))
    all_issues.extend(research_results.get("issues", []))
    all_issues.extend(query_results.get("issues", []))

    if all_issues:
        print(f"\n🚨 Issues Found ({len(all_issues)}):")
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i}. {issue}")
    else:
        print("\n✅ No issues found! Codebase is aligned with documentation.")

    print("\n" + "="*60)

    return results["overall_status"] == "PASS"


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
