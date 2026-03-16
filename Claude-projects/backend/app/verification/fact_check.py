"""
Fact-Check API Integration
Integrates with Google Fact Check Tools API and other fact-checking services
"""

import httpx
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)


class FactCheckAPI:
    """Google Fact Check Tools API client"""

    def __init__(self):
        """Initialize Fact Check API client"""
        self.api_key = settings.google_fact_check_api_key
        self.base_url = "https://factchecktools.googleapis.com/v1alpha1"
        self.timeout = 30

    async def check_claim(
        self,
        query: str,
        language_code: str = "en-US"
    ) -> Dict[str, Any]:
        """
        Check a claim using Google Fact Check Tools API

        Args:
            query: The claim to check
            language_code: Language code (e.g., en-US)

        Returns:
            Dictionary with fact-check results
        """
        if not self.api_key:
            logger.warning("Google Fact Check API key not configured")
            return self._default_result()

        try:
            url = f"{self.base_url}/claims:search"

            params = {
                "key": self.api_key,
                "query": query,
                "languageCode": language_code,
                "pageSize": 10
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)

                if response.status_code != 200:
                    logger.warning(f"Fact Check API error: {response.status_code}")
                    return self._default_result()

                data = response.json()

                if not data.get("claims"):
                    logger.info(f"No fact-check results found for: {query}")
                    return self._default_result()

                # Parse results
                return self._parse_fact_check_results(data)

        except Exception as e:
            logger.error(f"Error checking claim: {e}")
            return self._default_result()

    def _parse_fact_check_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse fact check results from API response"""
        claims = data.get("claims", [])

        if not claims:
            return self._default_result()

        # Analyze first claim (most relevant)
        claim = claims[0]
        claim_text = claim.get("text", "")
        claim_date = claim.get("claimDate")

        # Get claim reviews
        claim_reviews = claim.get("claimReview", [])

        if not claim_reviews:
            return {
                "has_results": True,
                "claim_found": True,
                "claim_text": claim_text,
                "claim_date": claim_date,
                "reviews": [],
                "overall_rating": None,
                "explanation": "Claim found but no fact-check reviews available"
            }

        # Analyze reviews
        reviews = []
        rating_counts = {}

        for review in claim_reviews:
            publisher = review.get("publisher", {})
            reviewer = publisher.get("name", "Unknown")

            textual_rating = review.get("textualRating", "")
            rating = review.get("rating", {})
            rating_value = rating.get("numericValue")
            rating_best = rating.get("bestValue")

            # Normalize rating if possible
            normalized_rating = None
            if rating_value is not None and rating_best is not None:
                normalized_rating = (rating_value / rating_best) * 100

            # Count ratings
            if textual_rating:
                rating_counts[textual_rating] = rating_counts.get(textual_rating, 0) + 1

            reviews.append({
                "reviewer": reviewer,
                "url": review.get("url"),
                "textual_rating": textual_rating,
                "normalized_rating": normalized_rating,
                "published_date": review.get("publishedDate")
            })

        # Calculate overall rating
        overall_rating = self._calculate_overall_rating(reviews)

        return {
            "has_results": True,
            "claim_found": True,
            "claim_text": claim_text,
            "claim_date": claim_date,
            "reviews": reviews,
            "overall_rating": overall_rating,
            "rating_distribution": rating_counts,
            "explanation": f"Found {len(reviews)} fact-check reviews"
        }

    def _calculate_overall_rating(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall rating from multiple reviews"""
        if not reviews:
            return {
                "rating": None,
                "confidence": 0.0
            }

        # Use numeric ratings if available
        numeric_ratings = [
            r["normalized_rating"]
            for r in reviews
            if r["normalized_rating"] is not None
        ]

        if numeric_ratings:
            avg_rating = sum(numeric_ratings) / len(numeric_ratings)
            confidence = min(len(numeric_ratings) * 10, 100)

            # Determine textual rating
            if avg_rating >= 70:
                textual = "True / Accurate"
            elif avg_rating >= 50:
                textual = "Mixed / Partially True"
            elif avg_rating >= 30:
                textual = "Mostly False"
            else:
                textual = "False / Misleading"

            return {
                "rating": textual,
                "numeric_score": avg_rating,
                "confidence": confidence
            }

        # Fall back to textual ratings
        textual_ratings = [r["textual_rating"] for r in reviews if r["textual_rating"]]
        if textual_ratings:
            # Count occurrences
            from collections import Counter
            counts = Counter(textual_ratings)
            most_common = counts.most_common(1)[0][0]

            confidence = min(len(textual_ratings) * 10, 100)

            return {
                "rating": most_common,
                "numeric_score": None,
                "confidence": confidence
            }

        return {
            "rating": None,
            "confidence": 0.0
        }

    def _default_result(self) -> Dict[str, Any]:
        """Return default result when API is unavailable"""
        return {
            "has_results": False,
            "claim_found": False,
            "claim_text": None,
            "claim_date": None,
            "reviews": [],
            "overall_rating": {
                "rating": None,
                "numeric_score": None,
                "confidence": 0.0
            },
            "explanation": "No fact-check results available"
        }

    async def check_article(
        self,
        title: str,
        content: str
    ) -> Dict[str, Any]:
        """
        Check an article for fact-checking

        Args:
            title: Article title
            content: Article content

        Returns:
            Dictionary with fact-check results
        """
        # Extract key claims from title and first paragraph
        claims = self._extract_claims(title, content)

        results = []

        for claim in claims[:3]:  # Check top 3 claims
            result = await self.check_claim(claim)
            results.append({
                "claim": claim,
                "result": result
            })

        return {
            "claims_checked": len(claims),
            "results": results,
            "has_any_results": any(r["result"]["has_results"] for r in results)
        }

    def _extract_claims(self, title: str, content: str) -> List[str]:
        """Extract potential claims from article"""
        claims = []

        # Add title as a claim
        if title:
            claims.append(title)

        # Get first paragraph
        paragraphs = content.split('\n')
        first_para = None
        for para in paragraphs:
            if para.strip():
                first_para = para.strip()
                break

        if first_para:
            # If first paragraph is a reasonable length, add it
            if len(first_para) <= 300:
                claims.append(first_para)

        # Look for sentences with claim indicators
        claim_indicators = [
            "reports that",
            "claims that",
            "says that",
            "according to",
            "reveals that",
            "shows that",
            "finds that",
            "confirms that"
        ]

        for indicator in claim_indicators:
            if indicator in content.lower():
                # Find sentence with indicator
                sentences = content.split('.')
                for sentence in sentences:
                    if indicator in sentence.lower() and len(sentence.strip()) <= 200:
                        claims.append(sentence.strip())
                        break

        # Remove duplicates
        claims = list(dict.fromkeys(claims))

        return claims

    def calculate_fact_check_score(self, result: Dict[str, Any]) -> float:
        """
        Calculate fact-check score from result

        Args:
            result: Fact-check result

        Returns:
            Score from 0-100
        """
        try:
            if not result.get("has_results"):
                return 50.0

            overall_rating = result.get("overall_rating", {})

            if not overall_rating.get("rating"):
                return 50.0

            rating = overall_rating["rating"].lower()
            confidence = overall_rating.get("confidence", 0) / 100

            # Base score from rating
            if "true" in rating or "accurate" in rating:
                base_score = 85.0
            elif "mixed" in rating or "partial" in rating:
                base_score = 60.0
            elif "mostly false" in rating:
                base_score = 30.0
            elif "false" in rating or "misleading" in rating:
                base_score = 10.0
            else:
                base_score = 50.0

            # Adjust by confidence
            final_score = base_score * confidence + 50 * (1 - confidence)

            return max(0, min(100, final_score))

        except Exception as e:
            logger.error(f"Error calculating fact-check score: {e}")
            return 50.0


# Alternative fact-check sources
class SnopesChecker:
    """Checker for Snopes (would need web scraping implementation)"""

    async def check_claim(self, claim: str) -> Dict[str, Any]:
        """Check claim against Snopes"""
        # Placeholder - would implement web scraping
        logger.info(f"Snopes check for: {claim}")
        return {"has_results": False}


class PolitiFactChecker:
    """Checker for PolitiFact (would need web scraping implementation)"""

    async def check_claim(self, claim: str) -> Dict[str, Any]:
        """Check claim against PolitiFact"""
        # Placeholder - would implement web scraping
        logger.info(f"PolitiFact check for: {claim}")
        return {"has_results": False}


# Singleton instances
fact_check_api = FactCheckAPI()
snopes_checker = SnopesChecker()
politi_fact_checker = PolitiFactChecker()