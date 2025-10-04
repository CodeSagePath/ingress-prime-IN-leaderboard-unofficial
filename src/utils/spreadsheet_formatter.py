"""
Spreadsheet-like formatter for Ingress statistics data
Provides visual grid layout with clear column headers and borders
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass

@dataclass
class TableColumn:
    """Definition of a table column"""
    key: str
    header: str
    width: int
    align: str = 'left'  # 'left', 'right', 'center'
    format_func: Optional[callable] = None

class SpreadsheetFormatter:
    """Creates spreadsheet-like visual layouts for Telegram"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Define column configurations for different views
        self.column_configs = {
            'summary': [
                TableColumn('agent_name', 'Agent', 12, 'left'),
                TableColumn('faction', 'Faction', 10, 'center'),
                TableColumn('level', 'Lvl', 4, 'center'),
                TableColumn('current_ap', 'Current AP', 12, 'right', self._format_large_number),
                TableColumn('portals_captured', 'Portals', 8, 'right', self._format_number),
                TableColumn('links_created', 'Links', 8, 'right', self._format_number),
                TableColumn('data_date', 'Date', 10, 'center', self._format_date),
            ],
            'detailed': [
                TableColumn('field_name', 'Statistic', 25, 'left'),
                TableColumn('value', 'Value', 15, 'right', self._format_large_number),
                TableColumn('rank', 'Rank', 6, 'center'),
                TableColumn('percentile', 'Top %', 8, 'center', self._format_percentage),
            ],
            'comparison': [
                TableColumn('agent_name', 'Agent', 15, 'left'),
                TableColumn('faction', 'Team', 8, 'center'),
                TableColumn('current_value', 'Current', 12, 'right', self._format_large_number),
                TableColumn('previous_value', 'Previous', 12, 'right', self._format_large_number),
                TableColumn('delta', 'Change', 10, 'right', self._format_delta),
                TableColumn('trend', 'Trend', 6, 'center'),
            ],
            'validation': [
                TableColumn('field_name', 'Field', 20, 'left'),
                TableColumn('status', 'Status', 8, 'center'),
                TableColumn('actual_value', 'Actual', 12, 'right'),
                TableColumn('expected', 'Expected', 12, 'right'),
                TableColumn('confidence', 'Conf%', 6, 'center', self._format_percentage),
            ]
        }
    
    def format_agent_summary(self, data: Dict, validation_results: Optional[List] = None) -> str:
        """Format agent data as a summary table"""
        try:
            # Create the summary data
            summary_data = [{
                'agent_name': data.get('agent_name', 'Unknown'),
                'faction': self._get_faction_emoji(data.get('faction', 'Unknown')),
                'level': data.get('level', 0),
                'current_ap': data.get('current_ap', 0),
                'portals_captured': data.get('portals_captured', 0),
                'links_created': data.get('links_created', 0),
                'data_date': data.get('data_date', datetime.now().date()),
            }]
            
            # Create the table
            table = self._create_table(summary_data, 'summary')
            
            # Add validation summary if provided
            validation_summary = ""
            if validation_results:
                validation_summary = self._create_validation_summary(validation_results)
            
            # Combine everything
            result = f"📊 **Agent Statistics Summary**\n\n"
            result += f"```\n{table}\n```"
            
            if validation_summary:
                result += f"\n{validation_summary}"
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error formatting agent summary: {e}")
            return "❌ Error formatting data summary"
    
    def format_detailed_stats(self, data: Dict, selected_stats: Optional[List[str]] = None) -> str:
        """Format detailed statistics in a grid layout"""
        try:
            # Define key statistics to show
            key_stats = selected_stats or [
                'level', 'current_ap', 'lifetime_ap', 'unique_portals_visited',
                'portals_discovered', 'portals_captured', 'resonators_deployed',
                'links_created', 'control_fields_created', 'mind_units_captured',
                'xm_collected', 'xm_recharged', 'distance_walked', 'hacks'
            ]
            
            # Create detailed data
            detailed_data = []
            for stat in key_stats:
                if stat in data:
                    detailed_data.append({
                        'field_name': self._get_display_name(stat),
                        'value': data[stat],
                        'rank': '—',  # Would need leaderboard data
                        'percentile': '—'  # Would need leaderboard data
                    })
            
            # Create the table
            table = self._create_table(detailed_data, 'detailed')
            
            result = f"📈 **Detailed Statistics**\n\n"
            result += f"```\n{table}\n```"
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error formatting detailed stats: {e}")
            return "❌ Error formatting detailed statistics"
    
    def format_validation_report(self, validation_results: List) -> str:
        """Format validation results in a table"""
        try:
            if not validation_results:
                return "✅ **All fields validated successfully!**"
            
            # Filter to show only problematic fields
            problematic_fields = [v for v in validation_results if not v.is_valid or v.confidence < 0.9]
            
            if not problematic_fields:
                return "✅ **All fields validated successfully!**"
            
            # Create validation data
            validation_data = []
            for validation in problematic_fields[:10]:  # Show top 10 issues
                validation_data.append({
                    'field_name': validation.field_name.replace('_', ' ').title(),
                    'status': '❌' if not validation.is_valid else '⚠️',
                    'actual_value': str(validation.actual_value)[:10] if validation.actual_value is not None else 'None',
                    'expected': validation.suggested_value if validation.suggested_value is not None else '—',
                    'confidence': validation.confidence
                })
            
            # Create the table
            table = self._create_table(validation_data, 'validation')
            
            result = f"🔍 **Data Validation Report**\n\n"
            result += f"```\n{table}\n```"
            
            # Add summary
            total_issues = len(problematic_fields)
            critical_issues = len([v for v in problematic_fields if not v.is_valid])
            warnings = total_issues - critical_issues
            
            result += f"\n📋 **Summary:** {critical_issues} errors, {warnings} warnings"
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error formatting validation report: {e}")
            return "❌ Error formatting validation report"
    
    def format_comparison_table(self, agents_data: List[Dict], stat_name: str) -> str:
        """Format multiple agents comparison in a table"""
        try:
            if not agents_data:
                return "No data available for comparison"
            
            # Create comparison data
            comparison_data = []
            for i, agent in enumerate(agents_data):
                comparison_data.append({
                    'agent_name': agent.get('agent_name', 'Unknown'),
                    'faction': self._get_faction_emoji(agent.get('faction', 'Unknown')),
                    'current_value': agent.get(stat_name, 0),
                    'previous_value': agent.get(f'prev_{stat_name}', 0),
                    'delta': agent.get(stat_name, 0) - agent.get(f'prev_{stat_name}', 0),
                    'trend': self._get_trend_arrow(agent.get(stat_name, 0) - agent.get(f'prev_{stat_name}', 0))
                })
            
            # Sort by current value
            comparison_data.sort(key=lambda x: x['current_value'], reverse=True)
            
            # Add rank numbers
            for i, row in enumerate(comparison_data, 1):
                row['rank'] = f"#{i}"
            
            # Create the table
            table = self._create_table(comparison_data, 'comparison')
            
            result = f"🏆 **{self._get_display_name(stat_name)} Leaderboard**\n\n"
            result += f"```\n{table}\n```"
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error formatting comparison table: {e}")
            return "❌ Error formatting comparison table"
    
    def _create_table(self, data: List[Dict], config_name: str) -> str:
        """Create a formatted table with borders and alignment"""
        if not data or config_name not in self.column_configs:
            return "No data to display"
        
        columns = self.column_configs[config_name]
        
        # Calculate actual column widths based on content
        for col in columns:
            max_width = len(col.header)
            for row in data:
                value = row.get(col.key, '')
                if col.format_func:
                    value = col.format_func(value)
                max_width = max(max_width, len(str(value)))
            col.width = min(max_width + 2, col.width + 5)  # Add padding, but respect max width
        
        # Create header
        header_parts = []
        separator_parts = []
        
        for col in columns:
            header_text = col.header.center(col.width) if col.align == 'center' else col.header.ljust(col.width)
            header_parts.append(header_text[:col.width])
            separator_parts.append('─' * col.width)
        
        header = '│' + '│'.join(header_parts) + '│'
        separator = '├' + '┼'.join(separator_parts) + '┤'
        top_border = '┌' + '┬'.join(separator_parts) + '┐'
        bottom_border = '└' + '┴'.join(separator_parts) + '┘'
        
        # Create data rows
        rows = []
        for row_data in data:
            row_parts = []
            for col in columns:
                value = row_data.get(col.key, '')
                if col.format_func:
                    value = col.format_func(value)
                
                value_str = str(value)[:col.width]  # Truncate if too long
                
                if col.align == 'right':
                    formatted_value = value_str.rjust(col.width)
                elif col.align == 'center':
                    formatted_value = value_str.center(col.width)
                else:
                    formatted_value = value_str.ljust(col.width)
                
                row_parts.append(formatted_value)
            
            rows.append('│' + '│'.join(row_parts) + '│')
        
        # Combine all parts
        table_parts = [top_border, header]
        if len(data) > 1:
            table_parts.append(separator)
        table_parts.extend(rows)
        table_parts.append(bottom_border)
        
        return '\n'.join(table_parts)
    
    def _create_validation_summary(self, validation_results: List) -> str:
        """Create a brief validation summary"""
        if not validation_results:
            return ""
        
        total_fields = len(validation_results)
        valid_fields = len([v for v in validation_results if v.is_valid])
        avg_confidence = sum(v.confidence for v in validation_results) / total_fields
        
        status_emoji = "✅" if valid_fields == total_fields else "⚠️" if valid_fields > total_fields * 0.8 else "❌"
        
        summary = f"\n{status_emoji} **Validation Summary**\n"
        summary += f"• Valid fields: {valid_fields}/{total_fields}\n"
        summary += f"• Average confidence: {avg_confidence:.1%}\n"
        
        if valid_fields < total_fields:
            issues = total_fields - valid_fields
            summary += f"• Issues found: {issues} (see validation report for details)"
        
        return summary
    
    def _format_large_number(self, number: Any) -> str:
        """Format large numbers with suffixes"""
        try:
            num = int(number) if number is not None else 0
            if num >= 1_000_000_000:
                return f"{num / 1_000_000_000:.1f}B"
            elif num >= 1_000_000:
                return f"{num / 1_000_000:.1f}M"
            elif num >= 1_000:
                return f"{num / 1_000:.1f}K"
            else:
                return str(num)
        except (ValueError, TypeError):
            return str(number)
    
    def _format_number(self, number: Any) -> str:
        """Format regular numbers with commas"""
        try:
            num = int(number) if number is not None else 0
            return f"{num:,}"
        except (ValueError, TypeError):
            return str(number)
    
    def _format_percentage(self, value: Any) -> str:
        """Format percentage values"""
        try:
            if isinstance(value, (int, float)):
                return f"{value:.1%}" if value <= 1 else f"{value:.1f}%"
            return str(value)
        except (ValueError, TypeError):
            return str(value)
    
    def _format_date(self, date_value: Any) -> str:
        """Format date values"""
        try:
            if hasattr(date_value, 'strftime'):
                return date_value.strftime('%Y-%m-%d')
            return str(date_value)
        except:
            return str(date_value)
    
    def _format_delta(self, delta: Any) -> str:
        """Format delta/change values"""
        try:
            num = int(delta) if delta is not None else 0
            if num > 0:
                return f"+{self._format_large_number(num)}"
            elif num < 0:
                return f"{self._format_large_number(num)}"
            else:
                return "0"
        except (ValueError, TypeError):
            return str(delta)
    
    def _get_faction_emoji(self, faction: str) -> str:
        """Get faction emoji"""
        faction_lower = faction.lower() if faction else ''
        if 'enlightened' in faction_lower:
            return '💚 ENL'
        elif 'resistance' in faction_lower:
            return '💙 RES'
        else:
            return f'❓ {faction}'
    
    def _get_trend_arrow(self, delta: Any) -> str:
        """Get trend arrow based on delta"""
        try:
            num = int(delta) if delta is not None else 0
            if num > 0:
                return '📈'
            elif num < 0:
                return '📉'
            else:
                return '➡️'
        except (ValueError, TypeError):
            return '❓'
    
    def _get_display_name(self, field_name: str) -> str:
        """Get human-readable display name for a field"""
        display_names = {
            'level': 'Level',
            'lifetime_ap': 'Lifetime AP',
            'current_ap': 'Current AP',
            'unique_portals_visited': 'Unique Portals Visited',
            'portals_discovered': 'Portals Discovered',
            'xm_collected': 'XM Collected',
            'resonators_deployed': 'Resonators Deployed',
            'links_created': 'Links Created',
            'control_fields_created': 'Control Fields Created',
            'mind_units_captured': 'Mind Units Captured',
            'portals_captured': 'Portals Captured',
            'distance_walked': 'Distance Walked',
            'resonators_destroyed': 'Resonators Destroyed',
            'portals_neutralized': 'Portals Neutralized',
            'enemy_links_destroyed': 'Enemy Links Destroyed',
            'enemy_fields_destroyed': 'Enemy Fields Destroyed',
            'mods_deployed': 'Mods Deployed',
            'hacks': 'Hacks',
            'kinetic_capsules_completed': 'Kinetic Capsules Completed',
            'drone_hacks': 'Drone Hacks',
            'glyph_hack_points': 'Glyph Hack Points',
            'xm_recharged': 'XM Recharged',
            'machina_portals_reclaimed': 'Machina Portals Reclaimed',
            'opr_agreements': 'OPR Agreements',
            'recursions': 'Recursions',
            'portal_scans_uploaded': 'Portal Scans Uploaded',
            'uniques_scout_controlled': 'Uniques Scout Controlled',
            'unique_missions_completed': 'Unique Missions Completed'
        }
        return display_names.get(field_name, field_name.replace('_', ' ').title())
    
    def create_interactive_menu(self, data: Dict, validation_results: Optional[List] = None) -> Tuple[str, List[List]]:
        """Create an interactive menu with buttons for different views"""
        # Create the main summary
        summary = self.format_agent_summary(data, validation_results)
        
        # Create inline keyboard buttons
        keyboard = [
            [
                {'text': '📊 Summary', 'callback_data': 'view_summary'},
                {'text': '📈 Detailed', 'callback_data': 'view_detailed'}
            ],
            [
                {'text': '🔍 Validation', 'callback_data': 'view_validation'},
                {'text': '🏆 Compare', 'callback_data': 'view_compare'}
            ],
            [
                {'text': '💾 Save Data', 'callback_data': 'save_data'},
                {'text': '❌ Cancel', 'callback_data': 'cancel'}
            ]
        ]
        
        return summary, keyboard