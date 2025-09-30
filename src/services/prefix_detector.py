"""
Smart Prefix Detection Service for Ingress Stats
Enhances existing auto-detection with flexible prefix support
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

class PrefixDetector:
    """Smart prefix detection that learns from user patterns and enhances stats detection"""
    
    def __init__(self, db_manager=None):
        self.db = db_manager
        
        # Predefined common prefixes (case-insensitive)
        self.common_prefixes = {
            # Direct indicators
            'stats:', 'ingress:', 'data:', 'submit:',
            '[stats]', '[ingress]', '[data]', 
            '#stats', '#ingress', '#data',
            '@stats', '@ingress', '@data',
            
            # Natural language prefixes
            'my stats:', 'my ingress stats:', 'here are my stats:',
            'stats update:', 'ingress update:', 'latest stats:',
            'current stats:', 'new stats:', 'updated stats:',
            
            # Copy-paste indicators
            'copied from ingress:', 'from ingress app:', 'ingress statistics:',
            'agent statistics:', 'portal statistics:', 'game stats:',
            
            # Time-based prefixes
            'daily stats:', 'weekly stats:', 'monthly stats:', 'all time stats:',
            'today stats:', 'this week:', 'this month:',
            
            # Action-based prefixes
            'submitting:', 'posting stats:', 'sharing stats:', 'updating:',
            'here:', 'check this:', 'look at this:', 'my progress:',
        }
        
        # Pattern-based prefixes (regex patterns)
        self.prefix_patterns = [
            r'^stats\s*[:\-\|]\s*',  # stats: or stats- or stats|
            r'^\[.*stats.*\]\s*',     # [anything with stats]
            r'^#\w*stats\w*\s*',      # #stats, #mystats, #ingressstats
            r'^@\w*stats\w*\s*',      # @stats, @mystats, @ingressstats
            r'^\w+\s*stats\s*[:\-]\s*',  # "my stats:", "agent stats-"
            r'^(here|check|look)\s+(are|at|is)\s+my\s+',  # "here are my", "check my", "look at my"
            r'^(submitting|posting|sharing|updating)\s*[:\-]?\s*',  # action words
            r'^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+',  # starts with timestamp
        ]
        
        # User pattern learning storage
        self.user_patterns = defaultdict(list)
        self.pattern_confidence = defaultdict(float)
        
    def detect_prefix(self, text: str, user_id: int = None) -> Dict:
        """
        Detect if message has a stats prefix and extract the clean stats data
        
        Returns:
        {
            'has_prefix': bool,
            'prefix_type': str,  # 'common', 'pattern', 'learned', 'none'
            'prefix_text': str,  # the actual prefix found
            'clean_text': str,   # text with prefix removed
            'confidence': float, # 0.0 to 1.0
            'suggestion': str    # suggested prefix for user
        }
        """
        if not text or not text.strip():
            return self._no_prefix_result(text)
        
        original_text = text
        text_lower = text.lower().strip()
        
        # 1. Check for common predefined prefixes
        common_result = self._check_common_prefixes(text, text_lower)
        if common_result['has_prefix']:
            self._learn_user_pattern(user_id, common_result['prefix_text'], 'common')
            return common_result
        
        # 2. Check for pattern-based prefixes
        pattern_result = self._check_pattern_prefixes(text, text_lower)
        if pattern_result['has_prefix']:
            self._learn_user_pattern(user_id, pattern_result['prefix_text'], 'pattern')
            return pattern_result
        
        # 3. Check learned user patterns
        if user_id:
            learned_result = self._check_learned_patterns(text, text_lower, user_id)
            if learned_result['has_prefix']:
                return learned_result
        
        # 4. Smart detection for potential prefixes
        smart_result = self._smart_prefix_detection(text, text_lower)
        if smart_result['has_prefix']:
            return smart_result
        
        # 5. No prefix detected
        return self._no_prefix_result(original_text, self._suggest_prefix(text_lower))
    
    def _check_common_prefixes(self, text: str, text_lower: str) -> Dict:
        """Check for predefined common prefixes"""
        for prefix in self.common_prefixes:
            if text_lower.startswith(prefix.lower()):
                clean_text = text[len(prefix):].strip()
                return {
                    'has_prefix': True,
                    'prefix_type': 'common',
                    'prefix_text': text[:len(prefix)].strip(),
                    'clean_text': clean_text,
                    'confidence': 0.95,
                    'suggestion': ''
                }
        return {'has_prefix': False}
    
    def _check_pattern_prefixes(self, text: str, text_lower: str) -> Dict:
        """Check for regex pattern-based prefixes"""
        for pattern in self.prefix_patterns:
            match = re.match(pattern, text_lower)
            if match:
                prefix_length = match.end()
                prefix_text = text[:prefix_length].strip()
                clean_text = text[prefix_length:].strip()
                return {
                    'has_prefix': True,
                    'prefix_type': 'pattern',
                    'prefix_text': prefix_text,
                    'clean_text': clean_text,
                    'confidence': 0.85,
                    'suggestion': ''
                }
        return {'has_prefix': False}
    
    def _check_learned_patterns(self, text: str, text_lower: str, user_id: int) -> Dict:
        """Check for learned user-specific patterns"""
        if user_id not in self.user_patterns:
            return {'has_prefix': False}
        
        user_prefixes = self.user_patterns[user_id]
        for prefix_data in user_prefixes:
            prefix = prefix_data['prefix'].lower()
            if text_lower.startswith(prefix):
                confidence = self.pattern_confidence.get(f"{user_id}_{prefix}", 0.5)
                clean_text = text[len(prefix):].strip()
                return {
                    'has_prefix': True,
                    'prefix_type': 'learned',
                    'prefix_text': text[:len(prefix)].strip(),
                    'clean_text': clean_text,
                    'confidence': min(confidence, 0.9),
                    'suggestion': ''
                }
        return {'has_prefix': False}
    
    def _smart_prefix_detection(self, text: str, text_lower: str) -> Dict:
        """Smart detection for potential prefixes based on context"""
        lines = text.split('\n')
        first_line = lines[0].strip()
        
        # Check if first line looks like a prefix/header
        if len(lines) > 1:
            # Multi-line message - first line might be a prefix
            first_line_words = first_line.split()
            
            # Short first line with stats-related content
            if (len(first_line_words) <= 5 and 
                any(word in first_line.lower() for word in ['stats', 'ingress', 'data', 'agent', 'update'])):
                
                remaining_text = '\n'.join(lines[1:]).strip()
                return {
                    'has_prefix': True,
                    'prefix_type': 'smart',
                    'prefix_text': first_line,
                    'clean_text': remaining_text,
                    'confidence': 0.7,
                    'suggestion': ''
                }
        
        # Check for natural language prefixes at start
        natural_starters = [
            'here is my', 'here are my', 'this is my', 'these are my',
            'my current', 'my latest', 'my new', 'my updated',
            'check out my', 'look at my', 'see my'
        ]
        
        for starter in natural_starters:
            if text_lower.startswith(starter):
                # Find where the actual data starts (look for numbers or known patterns)
                words = text.split()
                for i, word in enumerate(words):
                    if (word.upper() in ['ALL', 'DAILY', 'WEEKLY', 'MONTHLY'] or
                        word.isdigit() or
                        word.lower() in ['enlightened', 'resistance']):
                        
                        prefix_text = ' '.join(words[:i])
                        clean_text = ' '.join(words[i:])
                        return {
                            'has_prefix': True,
                            'prefix_type': 'smart',
                            'prefix_text': prefix_text,
                            'clean_text': clean_text,
                            'confidence': 0.6,
                            'suggestion': ''
                        }
        
        return {'has_prefix': False}
    
    def _no_prefix_result(self, text: str, suggestion: str = '') -> Dict:
        """Return result for no prefix detected"""
        return {
            'has_prefix': False,
            'prefix_type': 'none',
            'prefix_text': '',
            'clean_text': text,
            'confidence': 0.0,
            'suggestion': suggestion
        }
    
    def _suggest_prefix(self, text_lower: str) -> str:
        """Suggest an appropriate prefix for the user"""
        if any(word in text_lower for word in ['all time', 'daily', 'weekly', 'monthly']):
            return "💡 Try prefixing with 'STATS:' for clearer detection"
        elif any(word in text_lower for word in ['enlightened', 'resistance', 'agent']):
            return "💡 Try prefixing with 'INGRESS:' for better recognition"
        elif any(word in text_lower.split()[:10] for word in ['level', 'ap', 'portals']):
            return "💡 Try prefixing with 'DATA:' to help me recognize this faster"
        else:
            return "💡 Try prefixing with 'STATS:' to help me identify your data"
    
    def _learn_user_pattern(self, user_id: int, prefix: str, prefix_type: str):
        """Learn and store user prefix patterns"""
        if not user_id or not prefix:
            return
        
        # Store the pattern
        pattern_data = {
            'prefix': prefix,
            'type': prefix_type,
            'timestamp': datetime.now(),
            'count': 1
        }
        
        # Check if we already have this pattern
        existing_patterns = self.user_patterns[user_id]
        for i, existing in enumerate(existing_patterns):
            if existing['prefix'].lower() == prefix.lower():
                existing_patterns[i]['count'] += 1
                existing_patterns[i]['timestamp'] = datetime.now()
                # Increase confidence
                confidence_key = f"{user_id}_{prefix.lower()}"
                current_confidence = self.pattern_confidence[confidence_key]
                self.pattern_confidence[confidence_key] = min(current_confidence + 0.1, 0.9)
                return
        
        # Add new pattern
        self.user_patterns[user_id].append(pattern_data)
        confidence_key = f"{user_id}_{prefix.lower()}"
        self.pattern_confidence[confidence_key] = 0.6
        
        # Keep only recent patterns (last 30 days, max 10 patterns per user)
        cutoff_date = datetime.now() - timedelta(days=30)
        self.user_patterns[user_id] = [
            p for p in self.user_patterns[user_id] 
            if p['timestamp'] > cutoff_date
        ][-10:]  # Keep only last 10 patterns
    
    def get_user_patterns(self, user_id: int) -> List[Dict]:
        """Get learned patterns for a specific user"""
        if user_id not in self.user_patterns:
            return []
        
        patterns = self.user_patterns[user_id]
        # Sort by usage count and recency
        return sorted(patterns, key=lambda x: (x['count'], x['timestamp']), reverse=True)
    
    def suggest_prefixes_for_user(self, user_id: int) -> List[str]:
        """Suggest prefixes based on user's history"""
        patterns = self.get_user_patterns(user_id)
        suggestions = []
        
        # Add user's most used patterns
        for pattern in patterns[:3]:  # Top 3 patterns
            suggestions.append(f"'{pattern['prefix']}' (you've used this {pattern['count']} times)")
        
        # Add some common suggestions
        if not suggestions:
            suggestions = [
                "'STATS:' - Simple and clear",
                "'[INGRESS]' - Brackets make it stand out", 
                "'My stats:' - Natural language style"
            ]
        
        return suggestions
    
    def is_stats_message_with_prefix(self, text: str, user_id: int = None) -> Tuple[bool, str]:
        """
        Combined check: does this message have a prefix AND contain stats data?
        
        Returns:
            (has_prefix_and_stats, clean_stats_text)
        """
        prefix_result = self.detect_prefix(text, user_id)
        
        if prefix_result['has_prefix']:
            # Check if the clean text looks like stats data
            clean_text = prefix_result['clean_text']
            if self._looks_like_stats_data(clean_text):
                return True, clean_text
        
        return False, text
    
    def _looks_like_stats_data(self, text: str) -> bool:
        """Quick check if text looks like Ingress stats data"""
        if not text or len(text.strip()) < 20:
            return False
        
        parts = text.split()
        if len(parts) < 10:
            return False
        
        # Check for time periods
        time_periods = ["ALL", "TIME", "DAILY", "WEEKLY", "MONTHLY"]
        has_time_period = any(part.upper() in time_periods for part in parts[:3])
        
        # Check for factions
        factions = ["Enlightened", "Resistance", "enlightened", "resistance"]
        has_faction = any(faction in text for faction in factions)
        
        # Check for numeric data (should have many numbers)
        number_count = sum(1 for part in parts if part.isdigit())
        
        return has_time_period and has_faction and number_count >= 5