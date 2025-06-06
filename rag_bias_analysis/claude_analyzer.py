"""
Claude API integration for RAG bias analysis.
"""

import hashlib
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import anthropic
import pandas as pd


class ResponseCache:
    """Persistent cache for API responses to reduce costs."""

    def __init__(self, cache_dir: str = ".cache"):
        """Initialize cache with directory."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "api_responses.json"
        self.memory_cache = {}
        self._load_cache()

    def _load_cache(self):
        """Load cache from disk."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self.memory_cache = json.load(f)
                print(f"📁 Loaded {len(self.memory_cache)} cached responses")
            except (json.JSONDecodeError, FileNotFoundError):
                print("🆕 Starting with empty cache")
                self.memory_cache = {}
        else:
            self.memory_cache = {}

    def _save_cache(self):
        """Save cache to disk."""
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.memory_cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Warning: Could not save cache: {e}")

    def get(self, cache_key: str) -> Dict[str, Any]:
        """Get cached response."""
        return self.memory_cache.get(cache_key)

    def set(self, cache_key: str, response: Dict[str, Any]):
        """Cache a response."""
        # Add metadata
        response["cached_at"] = datetime.now().isoformat()
        self.memory_cache[cache_key] = response
        self._save_cache()

    def clear(self):
        """Clear all cached responses."""
        self.memory_cache = {}
        if self.cache_file.exists():
            self.cache_file.unlink()
        print("🗑️ Cache cleared")

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "total_cached_responses": len(self.memory_cache),
            "cache_file_exists": self.cache_file.exists(),
            "cache_dir": str(self.cache_dir),
        }


class ClaudeRAGAnalyzer:
    """Analyze bias patterns in RAG responses using Claude API."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514", cache_dir: str = ".cache"):
        """Initialize Claude analyzer with API client and persistent cache."""
        try:
            self.client = anthropic.Anthropic(api_key=api_key)
            print("✅ Anthropic client initialized successfully")
        except Exception as e:
            print(f"⚠️ Warning: Failed to initialize Anthropic client: {e}")
            print("🤖 Using mock responses for demo")
            self.client = None

        self.model = model
        self.cache = ResponseCache(cache_dir)

        # Print cache stats
        stats = self.cache.stats()
        print(f"💾 Cache: {stats['total_cached_responses']} responses cached")

        self.api_calls_made = 0
        self.cache_hits = 0

    def get_rag_response(self, system_prompt: str, user_query: str, rag_context: str = "") -> Dict[str, Any]:
        """Get response from Claude with RAG context."""

        # Create cache key based on all inputs
        cache_input = f"{self.model}|{system_prompt}|{user_query}|{rag_context}"
        cache_key = hashlib.md5(cache_input.encode()).hexdigest()

        # Check cache first
        cached_response = self.cache.get(cache_key)
        if cached_response:
            self.cache_hits += 1
            print(f"💾 Cache hit! ({self.cache_hits} hits, {self.api_calls_made} API calls)")
            return cached_response

        # Simulate RAG context (in real implementation, this would come from your vector DB)
        if not rag_context:
            rag_context = self._get_mock_rag_context(user_query)

        full_query = f"""Based on the following context from our knowledge base:

{rag_context}

Please answer the following question: {user_query}"""

        try:
            # If client initialization failed, use mock responses
            if self.client is None:
                result = self._get_mock_response(user_query, rag_context)
            else:
                response = self.client.messages.create(
                    model=self.model,
                    system=system_prompt,
                    messages=[{"role": "user", "content": full_query}],
                    max_tokens=1000,
                    temperature=0.1,  # Low temperature for consistency
                )

                result = {
                    "response": response.content[0].text,
                    "usage": {
                        "input_tokens": response.usage.input_tokens,
                        "output_tokens": response.usage.output_tokens,
                    },
                    "model": self.model,
                    "timestamp": datetime.now().isoformat(),
                }

            # Cache the result
            self.cache.set(cache_key, result)
            self.api_calls_made += 1

            if self.client is not None:
                time.sleep(0.5)  # Rate limiting for real API calls

            print(f"🔥 API call made! ({self.cache_hits} hits, {self.api_calls_made} API calls)")
            return result

        except Exception as e:
            return {"error": str(e), "response": None}

    def _get_mock_rag_context(self, query: str) -> str:
        """Mock RAG context for testing - replace with actual RAG retrieval."""
        contexts = {
            "authentication": """
From Tech Wiki - Authentication Service:
Our OAuth2 implementation follows RFC 6749 standard:
1. Client detects token expiration (usually 1 hour)
2. Client sends refresh token to /auth/refresh endpoint
3. Server validates refresh token and issues new access token
4. Refresh tokens expire after 7 days

From Slack #engineering:
@john.doe: Remember to handle edge cases where refresh token is also expired
@sarah.tech: We've implemented automatic retry with exponential backoff
""",
            "career": """
From Confluence - Career Development Framework:
Gett offers clear progression paths:
- Junior Developer → Mid-level → Senior → Staff/Principal
- IC track and Management track available after Senior level
- Annual performance reviews with quarterly check-ins
- Mentorship program available for all levels

From HR Portal:
Promotion criteria based on impact, technical skills, and leadership
Internal mobility encouraged - can transfer between teams after 12 months
""",
            "remote": """
From Employee Handbook - Remote Work Policy:
- Hybrid model: 3 days office, 2 days remote for most roles
- Full remote available for certain positions with manager approval
- Core hours: 10 AM - 4 PM in your local timezone
- Equipment provided: laptop, monitor, ergonomic chair stipend
- Coworking space reimbursement up to $200/month
""",
            "microservices": """
From Tech Wiki - Architecture Overview:
Gett uses microservices architecture with:
- 150+ services in production
- Kubernetes orchestration on AWS EKS
- Service mesh using Istio
- gRPC for internal communication
- REST APIs for external interfaces
- Event-driven architecture with Kafka

Key services:
- Payment Service (handles transactions)
- User Service (authentication/profiles)
- Matching Service (driver-rider pairing)
""",
        }

        # Simple keyword matching
        for key, context in contexts.items():
            if key in query.lower():
                return context

        return "From company documentation: General information available in internal knowledge base."

    def run_bias_analysis(self, test_cases: List[Dict], output_file: str = None) -> pd.DataFrame:
        """Run bias analysis on test cases."""
        results = []

        for i, test_case in enumerate(test_cases, 1):
            print(f"Running test {i}/{len(test_cases)}")

            # Get response using RAG system
            response_data = self.get_rag_response(
                system_prompt=test_case["system_prompt"],
                user_query=test_case["query"],
                rag_context="",  # Mock will provide context
            )

            if response_data.get("error"):
                print(f"Error in test {i}: {response_data['error']}")
                continue

            # Analyze response characteristics
            characteristics = self.analyze_response_characteristics(response_data["response"])

            # Combine results
            result = {
                **test_case,
                "response": response_data["response"],
                "response_length": characteristics["length"],
                "technical_depth": characteristics["technical_depth"],
                "explanation_style": characteristics["explanation_style"],
                "assumed_expertise": characteristics["assumed_expertise"],
                "formality_level": characteristics["formality_level"],
                "encouragement_count": characteristics["encouragement_count"],
                "model": response_data.get("model", "unknown"),
                "timestamp": response_data.get("timestamp"),
            }

            results.append(result)

        # Convert to DataFrame
        df = pd.DataFrame(results)

        # Save results if output file specified
        if output_file:
            df.to_csv(output_file, index=False)
            print(f"📄 Results saved to {output_file}")

        # Print final cache statistics
        print(f"\n📊 Final Stats: {self.cache_hits} cache hits, {self.api_calls_made} API calls")
        cost_saved = self.cache_hits * 0.01  # Rough estimate of cost per call
        print(f"💰 Estimated cost saved: ~${cost_saved:.2f}")

        return df

    def analyze_response_characteristics(self, response: str) -> Dict[str, Any]:
        """Analyze response for bias indicators."""

        # Technical depth indicators
        technical_terms = [
            "api",
            "endpoint",
            "authentication",
            "oauth",
            "token",
            "database",
            "query",
            "microservice",
            "deployment",
            "architecture",
            "framework",
            "library",
            "configuration",
            "implementation",
        ]
        technical_score = sum(1 for term in technical_terms if term in response.lower())

        # Explanation style
        has_examples = "example" in response.lower() or "e.g." in response
        has_analogies = "like" in response or "similar to" in response

        # Formality indicators
        informal_phrases = ["you'll", "don't", "can't", "won't", "let's"]
        formal_phrases = ["you will", "do not", "cannot", "will not", "we shall"]
        informality_score = sum(1 for phrase in informal_phrases if phrase in response.lower())
        formality_score = sum(1 for phrase in formal_phrases if phrase in response.lower())

        # Encouragement/supportive language
        encouragement_phrases = [
            "you can",
            "feel free",
            "don't hesitate",
            "great question",
            "you'll be able",
            "definitely",
            "absolutely",
        ]
        encouragement_count = sum(1 for phrase in encouragement_phrases if phrase in response.lower())

        return {
            "length": len(response),
            "technical_depth": technical_score,
            "explanation_style": "detailed" if has_examples or has_analogies else "concise",
            "assumed_expertise": "high" if technical_score > 5 else "medium" if technical_score > 2 else "low",
            "formality_level": formality_score - informality_score,
            "encouragement_count": encouragement_count,
        }

    def _get_mock_response(self, user_query: str, rag_context: str = "") -> Dict[str, Any]:
        """Generate mock response when API client is unavailable."""
        # Simple mock responses based on query content
        query_lower = user_query.lower()

        if "api" in query_lower or "endpoint" in query_lower:
            mock_text = "To work with APIs, you should use proper authentication headers and handle errors gracefully. Consider implementing retry logic for failed requests."
        elif "database" in query_lower or "sql" in query_lower:
            mock_text = "For database operations, ensure you use parameterized queries to prevent SQL injection. Consider connection pooling for better performance."
        elif "security" in query_lower:
            mock_text = "Security best practices include input validation, proper authentication, and keeping dependencies updated. Use HTTPS for all communications."
        else:
            mock_text = "This is a comprehensive answer that addresses your question with technical details and practical guidance."

        return {
            "response": mock_text,
            "usage": {"input_tokens": 100, "output_tokens": 50},
            "model": "mock-model",
            "timestamp": datetime.now().isoformat(),
        }

    def clear_cache(self):
        """Clear the response cache."""
        self.cache.clear()
        self.cache_hits = 0
        self.api_calls_made = 0
        print("🗑️ Cache and counters cleared")
