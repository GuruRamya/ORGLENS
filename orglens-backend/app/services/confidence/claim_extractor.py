from dataclasses import dataclass
from typing import List, Dict, Optional
import re
from enum import Enum

class ClaimCategory(str, Enum):
    SPEED = "speed"               
    MERITOCRACY = "meritocracy"    
    TRANSPARENCY = "transparency"  
    AUTONOMY = "autonomy"          
    TRUST = "trust"                
    CULTURE = "culture"            
    COLLABORATION = "collaboration"  
    INNOVATION = "innovation"     
    DIVERSITY = "diversity"        
    GROWTH = "growth"             
    BALANCE = "balance"            
    CUSTOM = "custom"              

@dataclass
class ExtractedClaim:
    """A claim extracted from org context."""
    claim_text: str                 
    category: ClaimCategory
    source: str                     
    confidence_pct: float           
    related_keywords: List[str]    
    
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
            return self._default_claims()
        
        for category, keywords in self.CLAIM_KEYWORDS.items():
            sentences = self._find_sentences_with_keywords(self.org_context, keywords)
            
            if sentences:
                for sentence in sentences:
                    claim_text = self._extract_claim_from_sentence(sentence, category)
                    if claim_text:
                        matched_keywords = [kw for kw in keywords if kw.lower() in sentence.lower()]
                        
                        claims.append(ExtractedClaim(
                            claim_text=claim_text,
                            category=category,
                            source=self._infer_source(self.org_context, sentence),
                            confidence_pct=self._calculate_claim_confidence(sentence, matched_keywords),
                            related_keywords=matched_keywords[:5],  
                        ))
        
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
        
        return matching[:10]  
    
    def _extract_claim_from_sentence(self, sentence: str, category: ClaimCategory) -> Optional[str]:
        """Extract a clean claim statement from a sentence."""
        sentence = ' '.join(sentence.split())
        if len(sentence) > 200:
            return self._summarize_claim(sentence, category)
        
        return sentence if len(sentence) > 10 else None
    
    def _summarize_claim(self, text: str, category: ClaimCategory) -> str:
        """Summarize long text to a short claim."""
        if len(text) > 150:
            return text[:147] + "..."
        return text
    
    def _infer_source(self, full_text: str, sentence: str) -> str:
        """Guess where this claim came from in the text."""
        lower_text = full_text.lower()
        lower_sent = sentence.lower()
        
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
        base_confidence = 60.0  
        
        keyword_boost = min(len(matched_keywords) * 5, 25)
        length_boost = min(len(sentence) / 20, 10)
        emphatic = ["absolutely", "always", "never", "core", "fundamental", "key"]
        if any(e in sentence.lower() for e in emphatic):
            length_boost += 5
        
        confidence = base_confidence + keyword_boost + length_boost
        return min(confidence, 95)  
    
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
                confidence_pct=0, 
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
