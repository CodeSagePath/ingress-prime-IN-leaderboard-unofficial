"""
Ingress Prefix Detection Service
Handles detection of "Time Span Agent Name" prefix pattern for Ingress stats data
"""

import logging
import re
from typing import Dict, Optional, Tuple
from config.settings import PREFIX_SETTINGS

logger = logging.getLogger(__name__)

class IngressPrefixDetector:
    """
    Detects the specific "Time Span Agent Name" prefix pattern in messages
    Supports both strict and flexible modes
    """
    
    def __init__(self):
        # Reload settings to get current environment variables
        from config.settings import PREFIX_SETTINGS
        self.settings = PREFIX_SETTINGS
        self.required_pattern = self.settings["required_pattern"]
        self.strict_mode = self.settings["strict_mode"]
        self.case_sensitive = self.settings["case_sensitive"]
        self.pattern_anywhere = self.settings["pattern_anywhere"]
        self.ignore_without_prefix = self.settings["ignore_without_prefix"]
        
        logger.info(f"IngressPrefixDetector initialized - Mode: {'strict' if self.strict_mode else 'flexible'}")
    
    def has_required_prefix(self, text: str) -> Tuple[bool, Dict]:
        """
        Check if the message contains the required "Time Span Agent Name" prefix
        
        Returns:
            (has_prefix, info_dict)
            
        info_dict contains:
            - pattern_found: bool
            - pattern_location: str ("start", "middle", "end")
            - clean_text: str (text with pattern removed if found)
            - original_text: str
            - match_details: dict
        """
        if not text or not text.strip():
            return False, self._create_info_dict(text, False)
        
        original_text = text
        search_text = text if self.case_sensitive else text.lower()
        pattern = self.required_pattern if self.case_sensitive else self.required_pattern.lower()
        
        # Find the pattern in the text
        pattern_index = search_text.find(pattern)
        
        if pattern_index == -1:
            # Pattern not found
            return False, self._create_info_dict(original_text, False)
        
        # Pattern found - determine location
        pattern_location = self._determine_pattern_location(pattern_index, len(search_text), len(pattern))
        
        # Extract clean text (remove the pattern)
        clean_text = self._extract_clean_text(original_text, pattern_index, len(pattern))
        
        # Create match details
        match_details = {
            "pattern": self.required_pattern,
            "found_at_index": pattern_index,
            "pattern_length": len(pattern),
            "location": pattern_location,
            "case_sensitive_match": self.case_sensitive
        }
        
        info_dict = self._create_info_dict(
            original_text, 
            True, 
            pattern_location, 
            clean_text, 
            match_details
        )
        
        return True, info_dict
    
    def should_process_message(self, text: str) -> Tuple[bool, str, Dict]:
        """
        Determine if a message should be processed based on prefix detection settings
        
        Returns:
            (should_process, reason, info_dict)
        """
        has_prefix, info = self.has_required_prefix(text)
        
        if self.strict_mode:
            if has_prefix:
                return True, "strict_mode_prefix_found", info
            else:
                return False, "strict_mode_no_prefix", info
        else:
            # Flexible mode - always process, but note if prefix was found
            if has_prefix:
                return True, "flexible_mode_with_prefix", info
            else:
                return True, "flexible_mode_without_prefix", info
    
    def get_processing_text(self, text: str) -> str:
        """
        Get the text that should be used for processing (with prefix removed if found)
        """
        has_prefix, info = self.has_required_prefix(text)
        
        if has_prefix and info.get("clean_text"):
            return info["clean_text"].strip()
        else:
            return text.strip()
    
    def _determine_pattern_location(self, pattern_index: int, text_length: int, pattern_length: int) -> str:
        """Determine where in the text the pattern was found"""
        if pattern_index == 0:
            return "start"
        elif pattern_index + pattern_length >= text_length - 10:  # Within 10 chars of end
            return "end"
        else:
            return "middle"
    
    def _extract_clean_text(self, original_text: str, pattern_index: int, pattern_length: int) -> str:
        """Extract text with the pattern removed"""
        before_pattern = original_text[:pattern_index]
        after_pattern = original_text[pattern_index + pattern_length:]
        
        # Combine and clean up
        clean_text = (before_pattern + " " + after_pattern).strip()
        
        # Remove extra whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text)
        
        return clean_text
    
    def _create_info_dict(self, original_text: str, pattern_found: bool, 
                         pattern_location: str = None, clean_text: str = None, 
                         match_details: Dict = None) -> Dict:
        """Create information dictionary about the prefix detection"""
        return {
            "pattern_found": pattern_found,
            "pattern_location": pattern_location,
            "clean_text": clean_text or original_text,
            "original_text": original_text,
            "match_details": match_details or {},
            "required_pattern": self.required_pattern,
            "detection_mode": "strict" if self.strict_mode else "flexible"
        }
    
    def get_mode_info(self) -> Dict:
        """Get information about current detection mode and settings"""
        return {
            "mode": "strict" if self.strict_mode else "flexible",
            "required_pattern": self.required_pattern,
            "case_sensitive": self.case_sensitive,
            "pattern_anywhere": self.pattern_anywhere,
            "ignore_without_prefix": self.ignore_without_prefix,
            "description": self._get_mode_description()
        }
    
    def _get_mode_description(self) -> str:
        """Get human-readable description of current mode"""
        if self.strict_mode:
            return f"Strict mode: Only processes messages containing '{self.required_pattern}'"
        else:
            return f"Flexible mode: Processes all messages, gives priority to those with '{self.required_pattern}'"
    
    def create_user_guidance_message(self, has_prefix: bool, info: Dict = None) -> str:
        """
        Create user guidance message based on prefix detection results
        """
        if self.strict_mode:
            if has_prefix:
                return (
                    f"✅ **Perfect!** I found the required prefix: `{self.required_pattern}`\n\n"
                    f"🎯 **Processing your Ingress statistics...**"
                )
            else:
                return (
                    f"🚫 **Prefix Required**\n\n"
                    f"To submit Ingress statistics, your message must contain:\n"
                    f"`{self.required_pattern}`\n\n"
                    f"💡 **How to fix:**\n"
                    f"1. Copy your complete Ingress statistics\n"
                    f"2. Make sure it includes the header with `{self.required_pattern}`\n"
                    f"3. Paste the complete data including the header\n\n"
                    f"**Example format:**\n"
                    f"`{self.required_pattern} Agent Faction Date (yyyy-mm-dd) Time (hh:mm:ss) Level...`"
                )
        else:
            if has_prefix:
                return (
                    f"✨ **Great!** I found the Ingress header: `{self.required_pattern}`\n\n"
                    f"🚀 **Enhanced processing** - this helps me identify your data faster!\n\n"
                    f"🎯 **Processing your statistics...**"
                )
            else:
                return (
                    f"📊 **Processing your data...**\n\n"
                    f"💡 **Pro tip:** Including the header `{self.required_pattern}` helps me identify Ingress data faster!"
                )