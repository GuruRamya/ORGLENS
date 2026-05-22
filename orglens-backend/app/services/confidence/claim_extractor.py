"""
Dynamic claim extraction from org context.
Don't hardcode "fast", "merit", "transparent".
Parse org's actual stated values.
"""
from dataclasses import dataclass
from typing import List, Dict, Optional
import re
from enum import Enum

class ClaimCategory(str, Enum):
    SPEED = "speed"                # We make decisions quickly
    MERITOCRACY = "meritocracy"    # Best people get ahead
    TRANSPARENCY = "transparency"  # Communication is open
    AUTONOMY = "autonomy"          # People have ownership
    TRUST = "trust"                # We trust each other
    CULTURE = "culture"            # Strong culture
    COLLABORATION = "collaboration"  # Work together
    INNOVATION = "innovation"      # Encourage new ideas
    DIVERSITY = "diversity"        # Inclusive
    GROWTH = "growth"              # Career growth
    BALANCE = "balance"            # Work-life balance
    CUSTOM = "custom"              # Custom claim

@dataclass
class ExtractedClaim:
    """A claim extracted from org context."""
    claim_text: str                 # Full claim: "We move fast"
    category: ClaimCategory
    source: str                     # "mission statement", "values doc", "CEO message"
    confidence_pct: float           # How confident we are this is a real stated value
    related_keywords: List[str]     # Words that support this claim
    
    def to_dict(self) -> dict:
        return {
            "claim": self.claim_text,
            "category": self.category.value,
            "source": self.source,
            "confidence": int(self.confidence_pct),
            "keywords": self.related_keywords,
        }

class ClaimExtractor:
    """
    Extract org's stated values dynamically.
    Don't assume anything. Read what they actually say.
    """
    
    # Keyword maps per category
    CLAIM_KEYWORDS = {
        ClaimCategory.SPEED: [
            "fast", "quick", "velocity", "agile", "rapid", "swift",
            "move quickly", "ship fast", "quick decisions", "speed",
            "move at speed", "rapid iteration"
        ],
        ClaimCategory.MERITOCRACY: [
            "merit", "best person", "performance-based", "meritocratic",
            "talent", "best and brightest", "judged on results",
            "performance matters", "earn your position"
        ],
        ClaimCategory.TRANSPARENCY: [
            "transparent", "open", "honest", "clear communication",
            "say what we mean", "no politics", "direct",
            "visibility", "information sharing", "open door"
        ],
        ClaimCategory.AUTONOMY: [
            "autonomy", "ownership", "empower", "self-directed",
            "decide", "authority", "control", "trust people",
            "freedom", "independence"
        ],
        ClaimCategory.TRUST: [
            "trust", "trustworthy", "reliable", "depend on",
            "confidence", "faith in", "believe in"
        ],
        ClaimCategory.COLLABORATION: [
            "collaborate", "teamwork", "together", "unity",
            "cross-functional", "cooperation", "collective",
            "work as one"
        ],
        ClaimCategory.GROWTH: [
            "growth", "development", "learn", "career",
            "opportunity", "advancement", "potential",
            "develop talent"
        ],
        ClaimCategory.BALANCE: [
            "balance", "work-life", "wellness", "flexible",
            "sustainable", "burnout", "well-being"
        ],
    }
    
    def __init__(self, org_context: Optional[str] = None):
        """
        org_context: mission statement, values doc, handbook excerpt, etc.
        If None, we'll use generic defaults.
        """
        self.org_context = org_context or ""
    
    def extract_claims(self) -> List[ExtractedClaim]:
        """
        Parse org context and extract stated claims.
        Returns list of claims org makes about itself.
        """
        claims = []
        
        if not self.org_context:
            # Default generic claims if no org context provided
            return self._default_claims()
        
        # Search for each claim category in the text
        for category, keywords in self.CLAIM_KEYWORDS.items():
            # Find sentences mentioning these keywords
            sentences = self._find_sentences_with_keywords(self.org_context, keywords)
            
            if sentences:
                for sentence in sentences:
                    # Extract claim from sentence
                    claim_text = self._extract_claim_from_sentence(sentence, category)
                    if claim_text:
                        # Find which keywords matched
                        matched_keywords = [kw for kw in keywords if kw.lower() in sentence.lower()]
                        
                        claims.append(ExtractedClaim(
                            claim_text=claim_text,
                            category=category,
                            source=self._infer_source(self.org_context, sentence),
                            confidence_pct=self._calculate_claim_confidence(sentence, matched_keywords),
                            related_keywords=matched_keywords[:5],  # Top 5
                        ))
        
        # Remove duplicates
        seen = set()
        unique_claims = []
        for claim in claims:
            key = (claim.claim_text.lower(), claim.category)
            if key not in seen:
                seen.add(key)
                unique_claims.append(claim)
        
        return unique_claims if unique_claims else self._default_claims()
    
    def _find_sentences_with_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Find sentences containing any of the keywords."""
        sentences = re.split(r'[.!?]', text)
        matching = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(kw.lower() in sentence_lower for kw in keywords):
                matching.append(sentence.strip())
        
        return matching[:10]  # Return top 10 matching sentences
    
    def _extract_claim_from_sentence(self, sentence: str, category: ClaimCategory) -> Optional[str]:
        """Extract a clean claim statement from a sentence."""
        # Remove extra whitespace
        sentence = ' '.join(sentence.split())
        
        # Try to find subject + predicate pattern
        # E.g., "We are transparent" -> "We are transparent"
        
        if len(sentence) > 200:
            # Too long, summarize
            return self._summarize_claim(sentence, category)
        
        return sentence if len(sentence) > 10 else None
    
    def _summarize_claim(self, text: str, category: ClaimCategory) -> str:
        """Summarize long text to a short claim."""
        # Take first 150 chars
        if len(text) > 150:
            return text[:147] + "..."
        return text
    
    def _infer_source(self, full_text: str, sentence: str) -> str:
        """Guess where this claim came from in the text."""
        lower_text = full_text.lower()
        lower_sent = sentence.lower()
        
        # Look for context clues
        if "mission" in lower_text[:lower_text.find(lower_sent)] if lower_sent in lower_text else False:
            return "mission statement"
        elif "value" in lower_text[:lower_text.find(lower_sent)] if lower_sent in lower_text else False:
            return "values statement"
        elif "handbook" in lower_text:
            return "employee handbook"
        elif "ceo" in lower_text:
            return "CEO message"
        else:
            return "org context"
    
    def _calculate_claim_confidence(self, sentence: str, matched_keywords: List[str]) -> float:
        """
        Calculate confidence that this is a real stated claim.
        More matches = higher confidence.
        """
        base_confidence = 60.0  # 60% baseline
        
        # Each keyword match adds 5%
        keyword_boost = min(len(matched_keywords) * 5, 25)
        
        # Sentence length: claims in longer paragraphs are more deliberate
        length_boost = min(len(sentence) / 20, 10)
        
        # Check for emphatic language
        emphatic = ["absolutely", "always", "never", "core", "fundamental", "key"]
        if any(e in sentence.lower() for e in emphatic):
            length_boost += 5
        
        confidence = base_confidence + keyword_boost + length_boost
        return min(confidence, 95)  # Cap at 95%
    
    def _default_claims(self) -> List[ExtractedClaim]:
        """
        Default generic claims if no org context.
        These are TEMPLATES — actual org will override.
        """
        return [
            ExtractedClaim(
                claim_text="We move fast and make decisions quickly",
                category=ClaimCategory.SPEED,
                source="generic",
                confidence_pct=0,  # 0% because not explicitly stated
                related_keywords=["speed", "agility"],
            ),
            ExtractedClaim(
                claim_text="Best people get ahead based on merit",
                category=ClaimCategory.MERITOCRACY,
                source="generic",
                confidence_pct=0,
                related_keywords=["merit", "performance"],
            ),
            ExtractedClaim(
                claim_text="Communication is transparent and honest",
                category=ClaimCategory.TRANSPARENCY,
                source="generic",
                confidence_pct=0,
                related_keywords=["transparent", "honest"],
            ),
        ]
    
    @staticmethod
    def from_file(file_path: str) -> "ClaimExtractor":
        """Load claims from a file (mission statement, handbook, etc.)."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return ClaimExtractor(org_context=content)
        except Exception as e:
            print(f"Error loading org context: {e}")
            return ClaimExtractor()