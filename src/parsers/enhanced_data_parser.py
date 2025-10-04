"""
Enhanced Data Parser for Ingress statistics with improved field detection and validation
Addresses data mismatch issues and provides automatic field correction suggestions
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from config.settings import DATA_FIELDS

@dataclass
class FieldValidationResult:
    """Result of field validation with suggestions for corrections"""
    is_valid: bool
    field_name: str
    expected_type: type
    actual_value: Any
    suggested_value: Any = None
    confidence: float = 0.0
    error_message: str = ""

@dataclass
class ParseResult:
    """Enhanced parse result with validation details"""
    success: bool
    data: Optional[Dict] = None
    errors: List[str] = None
    warnings: List[str] = None
    field_validations: List[FieldValidationResult] = None
    confidence_score: float = 0.0

class EnhancedDataParser:
    """Enhanced parser with intelligent field detection and validation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Define expected data types and validation rules for each field
        self.field_definitions = {
            'time_span': {'type': str, 'pattern': r'^(ALL TIME|DAILY|WEEKLY|MONTHLY|YEARLY)$', 'required': True},
            'agent_name': {'type': str, 'min_length': 1, 'max_length': 50, 'required': True},
            'faction': {'type': str, 'pattern': r'^(Enlightened|Resistance)$', 'required': True},
            'data_date': {'type': 'date', 'format': '%Y-%m-%d', 'required': True},
            'data_time': {'type': 'time', 'format': '%H:%M:%S', 'required': True},
            'level': {'type': int, 'min': 1, 'max': 16, 'required': True},
            'lifetime_ap': {'type': int, 'min': 0, 'max': 999999999999, 'required': True},
            'current_ap': {'type': int, 'min': 0, 'max': 999999999999, 'required': True},
            'unique_portals_visited': {'type': int, 'min': 0, 'required': True},
            'unique_portals_drone_visited': {'type': int, 'min': 0, 'required': False},
            'furthest_drone_distance': {'type': int, 'min': 0, 'required': False},
            'portals_discovered': {'type': int, 'min': 0, 'required': True},
            'xm_collected': {'type': int, 'min': 0, 'required': True},
            'opr_agreements': {'type': int, 'min': 0, 'required': False},
            'portal_scans_uploaded': {'type': int, 'min': 0, 'required': False},
            'uniques_scout_controlled': {'type': int, 'min': 0, 'required': False},
            'resonators_deployed': {'type': int, 'min': 0, 'required': True},
            'links_created': {'type': int, 'min': 0, 'required': True},
            'control_fields_created': {'type': int, 'min': 0, 'required': True},
            'mind_units_captured': {'type': int, 'min': 0, 'required': True},
            'longest_link_ever_created': {'type': int, 'min': 0, 'required': False},
            'largest_control_field': {'type': int, 'min': 0, 'required': False},
            'xm_recharged': {'type': int, 'min': 0, 'required': True},
            'portals_captured': {'type': int, 'min': 0, 'required': True},
            'unique_portals_captured': {'type': int, 'min': 0, 'required': True},
            'mods_deployed': {'type': int, 'min': 0, 'required': True},
            'hacks': {'type': int, 'min': 0, 'required': True},
            'drone_hacks': {'type': int, 'min': 0, 'required': False},
            'glyph_hack_points': {'type': int, 'min': 0, 'required': True},
            'completed_hackstreaks': {'type': int, 'min': 0, 'required': False},
            'longest_sojourner_streak': {'type': int, 'min': 0, 'required': False},
            'resonators_destroyed': {'type': int, 'min': 0, 'required': True},
            'portals_neutralized': {'type': int, 'min': 0, 'required': True},
            'enemy_links_destroyed': {'type': int, 'min': 0, 'required': True},
            'enemy_fields_destroyed': {'type': int, 'min': 0, 'required': True},
            'battle_beacon_combatant': {'type': int, 'min': 0, 'required': False},
            'drones_returned': {'type': int, 'min': 0, 'required': False},
            'machina_links_destroyed': {'type': int, 'min': 0, 'required': False},
            'machina_resonators_destroyed': {'type': int, 'min': 0, 'required': False},
            'machina_portals_neutralized': {'type': int, 'min': 0, 'required': False},
            'machina_portals_reclaimed': {'type': int, 'min': 0, 'required': False},
            'max_time_portal_held': {'type': int, 'min': 0, 'required': False},
            'max_time_link_maintained': {'type': int, 'min': 0, 'required': False},
            'max_link_length_x_days': {'type': int, 'min': 0, 'required': False},
            'max_time_field_held': {'type': int, 'min': 0, 'required': False},
            'largest_field_mus_x_days': {'type': int, 'min': 0, 'required': False},
            'forced_drone_recalls': {'type': int, 'min': 0, 'required': False},
            'distance_walked': {'type': int, 'min': 0, 'required': True},
            'kinetic_capsules_completed': {'type': int, 'min': 0, 'required': False},
            'unique_missions_completed': {'type': int, 'min': 0, 'required': False},
            'research_bounties_completed': {'type': int, 'min': 0, 'required': False},
            'research_days_completed': {'type': int, 'min': 0, 'required': False},
            'mission_days_attended': {'type': int, 'min': 0, 'required': False},
            'nl1331_meetups_attended': {'type': int, 'min': 0, 'required': False},
            'first_saturday_events': {'type': int, 'min': 0, 'required': False},
            'second_sunday_events': {'type': int, 'min': 0, 'required': False},
            'delta_tokens': {'type': int, 'min': 0, 'required': False},
            'delta_reso_points': {'type': int, 'min': 0, 'required': False},
            'delta_field_points': {'type': int, 'min': 0, 'required': False},
            'agents_recruited': {'type': int, 'min': 0, 'required': False},
            'recursions': {'type': int, 'min': 0, 'required': False},
            'months_subscribed': {'type': int, 'min': 0, 'required': False}
        }
        
        # Common patterns for intelligent field detection
        self.detection_patterns = {
            'agent_name': r'^[a-zA-Z0-9_.-]+$',
            'faction': r'^(Enlightened|Resistance)$',
            'date': r'^\d{4}-\d{2}-\d{2}$',
            'time': r'^\d{2}:\d{2}:\d{2}$',
            'level': r'^(1[0-6]|[1-9])$',  # Level 1-16
            'large_number': r'^\d{6,}$',    # Large numbers (AP, XM, etc.)
            'small_number': r'^\d{1,5}$',   # Smaller numbers
        }
    
    def parse_data_line(self, data_line: str) -> ParseResult:
        """Parse a single line with enhanced validation and field detection"""
        try:
            # Clean and prepare the data
            cleaned_line = self._clean_data_line(data_line.strip())
            if not cleaned_line:
                return ParseResult(success=False, errors=["Empty or invalid data line"])
            
            # Split the data
            parts = cleaned_line.split()
            
            # Skip header lines, but check if there's data mixed in
            if self._is_header_line(parts):
                # Try to extract data from mixed header/data line
                extracted_data = self._extract_data_from_mixed_line(parts)
                if extracted_data:
                    # Use the extracted data instead
                    parts = extracted_data
                else:
                    return ParseResult(success=False, errors=["Header line detected, not data"])
            
            # Intelligent field detection and parsing
            parse_result = self._intelligent_parse(parts)
            
            return parse_result
            
        except Exception as e:
            self.logger.error(f"Error parsing data line: {e}")
            return ParseResult(
                success=False, 
                errors=[f"Unexpected parsing error: {str(e)}"]
            )
    
    def _intelligent_parse(self, parts: List[str]) -> ParseResult:
        """Intelligently parse data with field detection and validation"""
        data = {}
        errors = []
        warnings = []
        field_validations = []
        
        # Step 1: Detect the basic structure
        structure_result = self._detect_structure(parts)
        if not structure_result['valid']:
            return ParseResult(
                success=False, 
                errors=structure_result['errors']
            )
        
        # Step 2: Parse basic fields (time_span, agent_name, faction, date, time)
        basic_fields_result = self._parse_basic_fields(parts, structure_result)
        data.update(basic_fields_result['data'])
        errors.extend(basic_fields_result['errors'])
        warnings.extend(basic_fields_result['warnings'])
        field_validations.extend(basic_fields_result['validations'])
        
        # Step 3: Parse numeric fields with intelligent detection
        numeric_offset = basic_fields_result['numeric_offset']
        numeric_result = self._parse_numeric_fields(parts[numeric_offset:])
        data.update(numeric_result['data'])
        errors.extend(numeric_result['errors'])
        warnings.extend(numeric_result['warnings'])
        field_validations.extend(numeric_result['validations'])
        
        # Step 4: Calculate confidence score
        confidence_score = self._calculate_confidence_score(field_validations)
        
        # Step 5: Generate suggestions for low-confidence fields
        if confidence_score < 0.8:
            suggestions = self._generate_suggestions(field_validations, parts)
            warnings.extend(suggestions)
        
        success = len(errors) == 0 and confidence_score > 0.5
        
        return ParseResult(
            success=success,
            data=data if success else None,
            errors=errors,
            warnings=warnings,
            field_validations=field_validations,
            confidence_score=confidence_score
        )
    
    def _detect_structure(self, parts: List[str]) -> Dict:
        """Detect the basic structure of the data line"""
        if len(parts) < 10:
            return {
                'valid': False,
                'errors': [f"Insufficient data fields. Found {len(parts)}, need at least 10."]
            }
        
        # Look for "ALL TIME" pattern
        has_all_time = len(parts) > 1 and parts[0] == "ALL" and parts[1] == "TIME"
        
        # Validate basic structure
        expected_positions = {
            'time_span_end': 2 if has_all_time else 1,
            'agent_name': 2 if has_all_time else 1,
            'faction': 3 if has_all_time else 2,
            'date': 4 if has_all_time else 3,
            'time': 5 if has_all_time else 4,
            'level': 6 if has_all_time else 5
        }
        
        errors = []
        
        # Check if we have enough parts for basic structure
        min_required = max(expected_positions.values()) + 1
        if len(parts) < min_required:
            errors.append(f"Not enough fields for basic structure. Need at least {min_required}, got {len(parts)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'has_all_time': has_all_time,
            'positions': expected_positions
        }
    
    def _parse_basic_fields(self, parts: List[str], structure: Dict) -> Dict:
        """Parse basic non-numeric fields with validation"""
        data = {}
        errors = []
        warnings = []
        validations = []
        
        has_all_time = structure['has_all_time']
        positions = structure['positions']
        
        try:
            # Time span
            if has_all_time:
                data['time_span'] = "ALL TIME"
                validations.append(FieldValidationResult(
                    is_valid=True, field_name='time_span', expected_type=str,
                    actual_value="ALL TIME", confidence=1.0
                ))
            else:
                time_span = parts[0]
                validation = self._validate_field('time_span', time_span)
                data['time_span'] = time_span
                validations.append(validation)
                if not validation.is_valid:
                    warnings.append(f"Unusual time span: {time_span}")
            
            # Agent name
            agent_name = parts[positions['agent_name']]
            validation = self._validate_field('agent_name', agent_name)
            data['agent_name'] = agent_name
            validations.append(validation)
            
            # Faction
            faction = parts[positions['faction']]
            validation = self._validate_field('faction', faction)
            data['faction'] = faction
            validations.append(validation)
            if not validation.is_valid:
                errors.append(f"Invalid faction: {faction}. Must be 'Enlightened' or 'Resistance'")
            
            # Date
            date_str = parts[positions['date']]
            try:
                data['data_date'] = datetime.strptime(date_str, '%Y-%m-%d').date()
                validations.append(FieldValidationResult(
                    is_valid=True, field_name='data_date', expected_type='date',
                    actual_value=date_str, confidence=1.0
                ))
            except ValueError:
                errors.append(f"Invalid date format: {date_str}. Expected YYYY-MM-DD")
                validations.append(FieldValidationResult(
                    is_valid=False, field_name='data_date', expected_type='date',
                    actual_value=date_str, error_message="Invalid date format"
                ))
            
            # Time
            time_str = parts[positions['time']]
            try:
                data['data_time'] = datetime.strptime(time_str, '%H:%M:%S').time()
                validations.append(FieldValidationResult(
                    is_valid=True, field_name='data_time', expected_type='time',
                    actual_value=time_str, confidence=1.0
                ))
            except ValueError:
                errors.append(f"Invalid time format: {time_str}. Expected HH:MM:SS")
                validations.append(FieldValidationResult(
                    is_valid=False, field_name='data_time', expected_type='time',
                    actual_value=time_str, error_message="Invalid time format"
                ))
            
            numeric_offset = positions['level']
            
        except IndexError as e:
            errors.append(f"Missing required basic fields: {str(e)}")
            numeric_offset = len(parts)  # Fallback
        
        return {
            'data': data,
            'errors': errors,
            'warnings': warnings,
            'validations': validations,
            'numeric_offset': numeric_offset
        }
    
    def _parse_numeric_fields(self, numeric_parts: List[str]) -> Dict:
        """Parse numeric fields with intelligent detection and validation"""
        data = {}
        errors = []
        warnings = []
        validations = []
        
        # Define the expected order of numeric fields
        numeric_fields = [
            'level', 'lifetime_ap', 'current_ap', 'unique_portals_visited',
            'unique_portals_drone_visited', 'furthest_drone_distance',
            'portals_discovered', 'xm_collected', 'opr_agreements',
            'portal_scans_uploaded', 'uniques_scout_controlled',
            'resonators_deployed', 'links_created', 'control_fields_created',
            'mind_units_captured', 'longest_link_ever_created',
            'largest_control_field', 'xm_recharged', 'portals_captured',
            'unique_portals_captured', 'mods_deployed', 'hacks',
            'drone_hacks', 'glyph_hack_points', 'completed_hackstreaks',
            'longest_sojourner_streak', 'resonators_destroyed',
            'portals_neutralized', 'enemy_links_destroyed',
            'enemy_fields_destroyed', 'battle_beacon_combatant',
            'drones_returned', 'machina_links_destroyed',
            'machina_resonators_destroyed', 'machina_portals_neutralized',
            'machina_portals_reclaimed', 'max_time_portal_held',
            'max_time_link_maintained', 'max_link_length_x_days',
            'max_time_field_held', 'largest_field_mus_x_days',
            'forced_drone_recalls', 'distance_walked',
            'kinetic_capsules_completed', 'unique_missions_completed',
            'research_bounties_completed', 'research_days_completed',
            'mission_days_attended', 'nl1331_meetups_attended',
            'first_saturday_events', 'second_sunday_events',
            'delta_tokens', 'delta_reso_points', 'delta_field_points',
            'agents_recruited', 'recursions', 'months_subscribed'
        ]
        
        # Parse each field with validation
        for i, field_name in enumerate(numeric_fields):
            if i < len(numeric_parts):
                value_str = numeric_parts[i]
                try:
                    value = int(value_str) if value_str.isdigit() or (value_str.startswith('-') and value_str[1:].isdigit()) else 0
                    validation = self._validate_field(field_name, value)
                    data[field_name] = validation.suggested_value if validation.suggested_value is not None else value
                    validations.append(validation)
                    
                    if not validation.is_valid:
                        warnings.append(f"Field {field_name}: {validation.error_message}")
                        
                except (ValueError, TypeError):
                    data[field_name] = 0
                    validations.append(FieldValidationResult(
                        is_valid=False, field_name=field_name, expected_type=int,
                        actual_value=value_str, suggested_value=0,
                        error_message=f"Invalid numeric value: {value_str}"
                    ))
                    warnings.append(f"Invalid numeric value for {field_name}: {value_str}, using 0")
            else:
                # Missing field, use default
                data[field_name] = 0
                validations.append(FieldValidationResult(
                    is_valid=False, field_name=field_name, expected_type=int,
                    actual_value=None, suggested_value=0,
                    error_message="Missing field, using default value 0"
                ))
        
        return {
            'data': data,
            'errors': errors,
            'warnings': warnings,
            'validations': validations
        }
    
    def _validate_field(self, field_name: str, value: Any) -> FieldValidationResult:
        """Validate a single field with suggestions"""
        if field_name not in self.field_definitions:
            return FieldValidationResult(
                is_valid=True, field_name=field_name, expected_type=type(value),
                actual_value=value, confidence=0.5
            )
        
        definition = self.field_definitions[field_name]
        expected_type = definition['type']
        
        # Type validation
        if expected_type == int:
            try:
                int_value = int(value) if not isinstance(value, int) else value
                
                # Range validation
                if 'min' in definition and int_value < definition['min']:
                    return FieldValidationResult(
                        is_valid=False, field_name=field_name, expected_type=int,
                        actual_value=value, suggested_value=definition['min'],
                        error_message=f"Value {int_value} below minimum {definition['min']}"
                    )
                
                if 'max' in definition and int_value > definition['max']:
                    return FieldValidationResult(
                        is_valid=False, field_name=field_name, expected_type=int,
                        actual_value=value, suggested_value=definition['max'],
                        error_message=f"Value {int_value} above maximum {definition['max']}"
                    )
                
                return FieldValidationResult(
                    is_valid=True, field_name=field_name, expected_type=int,
                    actual_value=int_value, confidence=1.0
                )
                
            except (ValueError, TypeError):
                return FieldValidationResult(
                    is_valid=False, field_name=field_name, expected_type=int,
                    actual_value=value, suggested_value=0,
                    error_message=f"Cannot convert {value} to integer"
                )
        
        elif expected_type == str:
            str_value = str(value)
            
            # Pattern validation
            if 'pattern' in definition:
                if not re.match(definition['pattern'], str_value):
                    return FieldValidationResult(
                        is_valid=False, field_name=field_name, expected_type=str,
                        actual_value=value, error_message=f"Value doesn't match expected pattern"
                    )
            
            # Length validation
            if 'min_length' in definition and len(str_value) < definition['min_length']:
                return FieldValidationResult(
                    is_valid=False, field_name=field_name, expected_type=str,
                    actual_value=value, error_message=f"Value too short (min: {definition['min_length']})"
                )
            
            if 'max_length' in definition and len(str_value) > definition['max_length']:
                return FieldValidationResult(
                    is_valid=False, field_name=field_name, expected_type=str,
                    actual_value=value, error_message=f"Value too long (max: {definition['max_length']})"
                )
            
            return FieldValidationResult(
                is_valid=True, field_name=field_name, expected_type=str,
                actual_value=str_value, confidence=1.0
            )
        
        # Default case
        return FieldValidationResult(
            is_valid=True, field_name=field_name, expected_type=expected_type,
            actual_value=value, confidence=0.8
        )
    
    def _calculate_confidence_score(self, validations: List[FieldValidationResult]) -> float:
        """Calculate overall confidence score for the parse result"""
        if not validations:
            return 0.0
        
        total_confidence = sum(v.confidence for v in validations)
        return total_confidence / len(validations)
    
    def _generate_suggestions(self, validations: List[FieldValidationResult], parts: List[str]) -> List[str]:
        """Generate suggestions for improving data quality"""
        suggestions = []
        
        invalid_fields = [v for v in validations if not v.is_valid]
        if invalid_fields:
            suggestions.append(f"Found {len(invalid_fields)} fields with potential issues:")
            for field in invalid_fields[:5]:  # Show first 5 issues
                if field.suggested_value is not None:
                    suggestions.append(f"  • {field.field_name}: {field.error_message} (suggested: {field.suggested_value})")
                else:
                    suggestions.append(f"  • {field.field_name}: {field.error_message}")
        
        return suggestions
    
    def _clean_data_line(self, line: str) -> str:
        """Clean data line by removing bot commands and unnecessary text"""
        # Remove common bot command patterns
        if line.startswith('/submit'):
            line = line[7:].strip()
        
        return line.strip()
    
    def _is_header_line(self, parts: List[str]) -> bool:
        """Check if this is a header line that should be skipped"""
        if not parts:
            return True
        
        # Check for obvious header indicators
        header_keywords = [
            "Time", "Span", "Agent", "Name", "Faction", "Date", "Level",
            "Lifetime", "Current", "Unique", "Portals", "Visited"
        ]
        
        # Check if line contains "ALL TIME" pattern - indicates mixed header/data
        for i in range(len(parts) - 1):
            if parts[i] == "ALL" and parts[i + 1] == "TIME":
                return True  # Mixed line that needs data extraction
        
        # Check if first 20 parts contain many header keywords (for mixed lines)
        first_parts = parts[:20]  # Only check first 20 parts
        keyword_count = sum(1 for part in first_parts if part in header_keywords)
        if keyword_count >= 8:  # If 8+ header keywords in first 20 parts
            return True
        
        # Check if overall line has high concentration of header keywords
        keyword_count_total = sum(1 for part in parts if part in header_keywords)
        return keyword_count_total > len(parts) * 0.3  # More than 30% are header keywords

    def _extract_data_from_mixed_line(self, parts: List[str]) -> Optional[List[str]]:
        """Extract data from a line that contains both header and data"""
        # Look for "ALL TIME" pattern which indicates start of data
        for i in range(len(parts) - 1):
            if parts[i] == "ALL" and parts[i + 1] == "TIME":
                # Check if this looks like the start of actual data
                # We need at least agent_name, faction, date, time after "ALL TIME"
                if i + 6 < len(parts):
                    try:
                        # Try to parse date and time at expected positions
                        datetime.strptime(parts[i + 4], '%Y-%m-%d')
                        datetime.strptime(parts[i + 5], '%H:%M:%S')
                        # Extract from "ALL TIME" onwards
                        return parts[i:]
                    except (ValueError, IndexError):
                        continue
        
        # Look for other time span patterns (single word followed by agent name, faction, date, time)
        for i in range(len(parts) - 5):
            # Check if this position could be start of data
            if i + 4 < len(parts):
                try:
                    # Check if positions i+2, i+3 could be date and time
                    datetime.strptime(parts[i + 2], '%Y-%m-%d')
                    datetime.strptime(parts[i + 3], '%H:%M:%S')
                    # Check if position i+1 looks like a faction
                    if parts[i + 1].lower() in ['enlightened', 'resistance']:
                        return parts[i:]
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def format_number(self, number: int) -> str:
        """Format large numbers with appropriate suffixes"""
        if number >= 1_000_000_000:
            return f"{number / 1_000_000_000:.1f}B"
        elif number >= 1_000_000:
            return f"{number / 1_000_000:.1f}M"
        elif number >= 1_000:
            return f"{number / 1_000:.1f}K"
        else:
            return str(number)