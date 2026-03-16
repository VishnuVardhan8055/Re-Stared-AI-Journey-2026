"""
AI Content Analysis using Claude API
Analyzes articles for sensationalism, bias, and credibility
"""

import logging
from typing import Dict, Any, Optional
import json

from anthropic import Anthropic

from app.config import settings

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """AI-based content analysis using Claude"""

    def __init__(self):
        """Initialize AI analyzer"""
        self.client = None
        self._initialize()

    def _initialize(self):
        """Initialize Claude client"""
        if not settings.anthropic_api_key:
            logger.warning("Anthropic API key not configured")
            return

        try:
            self.client = Anthropic(api_key=settings.anthropic_api_key)
            logger.info("Claude client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Claude client: {e}")

    async def analyze_article(
        self,
        title: str,
        content: str,
        summary: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze article content using AI

        Args:
            title: Article title
            content: Article content
            summary: Optional summary

        Returns:
            Dictionary with analysis results
        """
        if not self.client:
            logger.warning("Claude client not initialized")
            return self._default_analysis()

        try:
            # Prepare the content to analyze
            text_to_analyze = self._prepare_text(title, content, summary)

            # Create the analysis prompt
            prompt = self._create_analysis_prompt(text_to_analyze)

            # Call Claude API
            message = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1024,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Parse the response
            response_text = message.content[0].text
            analysis = self._parse_analysis_response(response_text)

            logger.info(f"AI analysis completed for article: {title[:50]}...")
            return analysis

        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            return self._default_analysis()

    def _prepare_text(
        self,
        title: str,
        content: str,
        summary: Optional[str]
    ) -> str:
        """Prepare text for analysis"""
        # Use summary if available, otherwise truncate content
        text_content = summary if summary else content

        # Limit content length
        max_length = 2000
        if len(text_content) > max_length:
            text_content = text_content[:max_length] + "..."

        return f"Title: {title}\n\nContent: {text_content}"

    def _create_analysis_prompt(self, text: str) -> str:
        """Create the analysis prompt for Claude"""
        return f"""Please analyze the following news article and provide a detailed assessment in JSON format.

Article to analyze:
{text}

Please analyze and return a JSON object with the following structure:
{{
    "sensationalism_score": <number 0-100>,
    "sentiment": <"positive", "negative", "neutral", or "mixed">,
    "bias_detection": {{
        "has_bias": <boolean>,
        "bias_type": <"political", "commercial", "confirmation", "none" or null>,
        "bias_strength": <number 0-100>
    }},
    "credibility_indicators": {{
        "has_factual_claims": <boolean>,
        "has_sources_cited": <boolean>,
        "uses_clickbait": <boolean>,
        "uses_exaggerated_language": <boolean>,
        "has_logical_consistency": <boolean>
    }},
    "key_claims": [<array of main claims extracted>],
    "risk_assessment": <"low", "medium", or "high">,
    "recommendation": <"verified", "needs_review", or "unverified">,
    "explanation": <brief explanation of the analysis>
}}

Analysis criteria:
- Sensationalism: Higher score for more emotional/exaggerated language
- Bias: Detect any political, commercial, or confirmation bias
- Credibility: Check for factual claims, sources, and consistency
- Risk: Based on overall credibility and potential for misinformation

Return ONLY the JSON object, no other text."""

    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse Claude's response into structured data"""
        try:
            # Extract JSON from response
            # Look for JSON object in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1

            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)

            # If no JSON found, return default
            logger.warning("No JSON found in Claude response")
            return self._default_analysis()

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {e}")
            return self._default_analysis()

    def _default_analysis(self) -> Dict[str, Any]:
        """Return default analysis when AI is unavailable"""
        return {
            "sensationalism_score": 50.0,
            "sentiment": "neutral",
            "bias_detection": {
                "has_bias": False,
                "bias_type": None,
                "bias_strength": 0.0
            },
            "credibility_indicators": {
                "has_factual_claims": True,
                "has_sources_cited": False,
                "uses_clickbait": False,
                "uses_exaggerated_language": False,
                "has_logical_consistency": True
            },
            "key_claims": [],
            "risk_assessment": "medium",
            "recommendation": "needs_review",
            "explanation": "AI analysis not available"
        }

    def calculate_ai_score(self, analysis: Dict[str, Any]) -> float:
        """
        Calculate overall AI credibility score from analysis

        Args:
            analysis: Analysis results from AI

        Returns:
            Score from 0-100
        """
        try:
            score = 50.0  # Base score

            # Lower sensationalism = higher score
            sensationalism = analysis.get("sensationalism_score", 50)
            score += (100 - sensationalism) * 0.2

            # Check credibility indicators
            indicators = analysis.get("credibility_indicators", {})

            if indicators.get("has_factual_claims"):
                score += 10
            if indicators.get("has_sources_cited"):
                score += 10
            if indicators.get("has_logical_consistency"):
                score += 10

            # Penalize for negative indicators
            if indicators.get("uses_clickbait"):
                score -= 20
            if indicators.get("uses_exaggerated_language"):
                score -= 15

            # Check bias
            bias = analysis.get("bias_detection", {})
            if bias.get("has_bias"):
                score -= bias.get("bias_strength", 0) * 0.2

            # Normalize to 0-100
            return max(0, min(100, score))

        except Exception as e:
            logger.error(f"Error calculating AI score: {e}")
            return 50.0

    def get_sentiment(self, analysis: Dict[str, Any]) -> str:
        """Get sentiment from analysis"""
        return analysis.get("sentiment", "neutral")

    async def batch_analyze(
        self,
        articles: list[Dict[str, Any]]
    ) -> list[Dict[str, Any]]:
        """
        Analyze multiple articles in batch

        Args:
            articles: List of article dictionaries with title, content, summary

        Returns:
            List of analysis results
        """
        results = []

        for article in articles:
            analysis = await self.analyze_article(
                title=article.get("title", ""),
                content=article.get("content", ""),
                summary=article.get("summary")
            )
            results.append(analysis)

        return results


# Singleton instance
ai_analyzer = AIAnalyzer()