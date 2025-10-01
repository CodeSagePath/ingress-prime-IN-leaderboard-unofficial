"""
Database management for the Ingress Leaderboard Bot
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from config import DATABASE_PATH, DATA_FIELDS

class DatabaseManager:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create agents table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS agents (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        agent_name TEXT NOT NULL,
                        faction TEXT NOT NULL,
                        telegram_user_id INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(agent_name, telegram_user_id)
                    )
                ''')
                
                # Create submissions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS submissions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        agent_id INTEGER,
                        submission_date DATE NOT NULL,
                        submission_time TIME NOT NULL,
                        data_date DATE NOT NULL,
                        data_time TIME NOT NULL,
                        level INTEGER,
                        lifetime_ap BIGINT,
                        current_ap BIGINT,
                        unique_portals_visited INTEGER,
                        unique_portals_drone_visited INTEGER,
                        furthest_drone_distance INTEGER,
                        portals_discovered INTEGER,
                        xm_collected BIGINT,
                        opr_agreements INTEGER,
                        portal_scans_uploaded INTEGER,
                        uniques_scout_controlled INTEGER,
                        resonators_deployed INTEGER,
                        links_created INTEGER,
                        control_fields_created INTEGER,
                        mind_units_captured BIGINT,
                        longest_link_ever_created INTEGER,
                        largest_control_field BIGINT,
                        xm_recharged BIGINT,
                        portals_captured INTEGER,
                        unique_portals_captured INTEGER,
                        mods_deployed INTEGER,
                        hacks INTEGER,
                        drone_hacks INTEGER,
                        glyph_hack_points INTEGER,
                        completed_hackstreaks INTEGER,
                        longest_sojourner_streak INTEGER,
                        resonators_destroyed INTEGER,
                        portals_neutralized INTEGER,
                        enemy_links_destroyed INTEGER,
                        enemy_fields_destroyed INTEGER,
                        battle_beacon_combatant INTEGER,
                        drones_returned INTEGER,
                        machina_links_destroyed INTEGER,
                        machina_resonators_destroyed INTEGER,
                        machina_portals_neutralized INTEGER,
                        machina_portals_reclaimed INTEGER,
                        max_time_portal_held INTEGER,
                        max_time_link_maintained INTEGER,
                        max_link_length_x_days INTEGER,
                        max_time_field_held INTEGER,
                        largest_field_mus_x_days BIGINT,
                        forced_drone_recalls INTEGER,
                        distance_walked INTEGER,
                        kinetic_capsules_completed INTEGER,
                        unique_missions_completed INTEGER,
                        research_bounties_completed INTEGER,
                        research_days_completed INTEGER,
                        mission_days_attended INTEGER,
                        nl1331_meetups_attended INTEGER,
                        first_saturday_events INTEGER,
                        second_sunday_events INTEGER,
                        delta_tokens INTEGER,
                        delta_reso_points INTEGER,
                        delta_field_points INTEGER,
                        agents_recruited INTEGER,
                        recursions INTEGER,
                        months_subscribed INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (agent_id) REFERENCES agents (id)
                    )
                ''')
                
                conn.commit()
                logging.info("Database initialized successfully")
                
        except sqlite3.Error as e:
            logging.error(f"Database initialization error: {e}")
            raise
    
    def add_agent(self, agent_name: str, faction: str, telegram_user_id: int) -> int:
        """Add a new agent or get existing agent ID - concurrent safe"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                # Enable WAL mode for better concurrency
                conn.execute("PRAGMA journal_mode = WAL")
                cursor = conn.cursor()
                
                # Try to get existing agent first
                cursor.execute('''
                    SELECT id FROM agents 
                    WHERE agent_name = ? AND telegram_user_id = ?
                ''', (agent_name, telegram_user_id))
                
                result = cursor.fetchone()
                if result:
                    return result[0]
                
                # Use INSERT OR IGNORE to handle concurrent inserts
                cursor.execute('''
                    INSERT OR IGNORE INTO agents (agent_name, faction, telegram_user_id)
                    VALUES (?, ?, ?)
                ''', (agent_name, faction, telegram_user_id))
                
                # If we inserted a new row, return its ID
                if cursor.lastrowid:
                    return cursor.lastrowid
                
                # If INSERT OR IGNORE didn't insert (concurrent insert happened), 
                # try to get the existing ID again
                cursor.execute('''
                    SELECT id FROM agents 
                    WHERE agent_name = ? AND telegram_user_id = ?
                ''', (agent_name, telegram_user_id))
                
                result = cursor.fetchone()
                return result[0] if result else None
                
        except sqlite3.Error as e:
            logging.error(f"Error adding agent {agent_name} for user {telegram_user_id}: {e}")
            raise
    
    def add_submission(self, agent_id: int, data: Dict) -> bool:
        """Add a new data submission - concurrent safe"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                # Enable WAL mode for better concurrency
                conn.execute("PRAGMA journal_mode = WAL")
                cursor = conn.cursor()
                
                # Parse the data according to the format
                submission_date = datetime.now().date()
                submission_time = datetime.now().time()
                
                # Insert submission
                cursor.execute('''
                    INSERT INTO submissions (
                        agent_id, submission_date, submission_time, data_date, data_time,
                        level, lifetime_ap, current_ap, unique_portals_visited,
                        unique_portals_drone_visited, furthest_drone_distance,
                        portals_discovered, xm_collected, opr_agreements,
                        portal_scans_uploaded, uniques_scout_controlled,
                        resonators_deployed, links_created, control_fields_created,
                        mind_units_captured, longest_link_ever_created,
                        largest_control_field, xm_recharged, portals_captured,
                        unique_portals_captured, mods_deployed, hacks, drone_hacks,
                        glyph_hack_points, completed_hackstreaks, longest_sojourner_streak,
                        resonators_destroyed, portals_neutralized, enemy_links_destroyed,
                        enemy_fields_destroyed, battle_beacon_combatant, drones_returned,
                        machina_links_destroyed, machina_resonators_destroyed,
                        machina_portals_neutralized, machina_portals_reclaimed,
                        max_time_portal_held, max_time_link_maintained,
                        max_link_length_x_days, max_time_field_held,
                        largest_field_mus_x_days, forced_drone_recalls,
                        distance_walked, kinetic_capsules_completed,
                        unique_missions_completed, research_bounties_completed,
                        research_days_completed, mission_days_attended,
                        nl1331_meetups_attended, first_saturday_events,
                        second_sunday_events, delta_tokens, delta_reso_points,
                        delta_field_points, agents_recruited, recursions,
                        months_subscribed
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    agent_id, submission_date, submission_time.strftime('%H:%M:%S'),
                    data['data_date'], data['data_time'].strftime('%H:%M:%S'),
                    data['level'], data['lifetime_ap'], data['current_ap'],
                    data['unique_portals_visited'], data['unique_portals_drone_visited'],
                    data['furthest_drone_distance'], data['portals_discovered'],
                    data['xm_collected'], data['opr_agreements'], data['portal_scans_uploaded'],
                    data['uniques_scout_controlled'], data['resonators_deployed'],
                    data['links_created'], data['control_fields_created'],
                    data['mind_units_captured'], data['longest_link_ever_created'],
                    data['largest_control_field'], data['xm_recharged'],
                    data['portals_captured'], data['unique_portals_captured'],
                    data['mods_deployed'], data['hacks'], data['drone_hacks'],
                    data['glyph_hack_points'], data['completed_hackstreaks'],
                    data['longest_sojourner_streak'], data['resonators_destroyed'],
                    data['portals_neutralized'], data['enemy_links_destroyed'],
                    data['enemy_fields_destroyed'], data['battle_beacon_combatant'],
                    data['drones_returned'], data['machina_links_destroyed'],
                    data['machina_resonators_destroyed'], data['machina_portals_neutralized'],
                    data['machina_portals_reclaimed'], data['max_time_portal_held'],
                    data['max_time_link_maintained'], data['max_link_length_x_days'],
                    data['max_time_field_held'], data['largest_field_mus_x_days'],
                    data['forced_drone_recalls'], data['distance_walked'],
                    data['kinetic_capsules_completed'], data['unique_missions_completed'],
                    data['research_bounties_completed'], data['research_days_completed'],
                    data['mission_days_attended'], data['nl1331_meetups_attended'],
                    data['first_saturday_events'], data['second_sunday_events'],
                    data['delta_tokens'], data['delta_reso_points'],
                    data['delta_field_points'], data['agents_recruited'],
                    data['recursions'], data['months_subscribed']
                ))
                
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            logging.error(f"Error adding submission: {e}")
            return False
    
    def get_leaderboard(self, stat: str, faction: Optional[str] = None, 
                       days: Optional[int] = None, limit: int = 10) -> List[Tuple]:
        """Get leaderboard for a specific statistic - concurrent safe"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                # Enable WAL mode for better concurrency
                conn.execute("PRAGMA journal_mode = WAL")
                cursor = conn.cursor()
                
                # Build the query
                query = '''
                    SELECT a.agent_name, a.faction, s.{stat}, s.submission_date
                    FROM submissions s
                    JOIN agents a ON s.agent_id = a.id
                    WHERE 1=1
                '''.format(stat=stat.lower().replace(' ', '_'))
                
                params = []
                
                if faction:
                    query += ' AND a.faction = ?'
                    params.append(faction)
                
                if days:
                    cutoff_date = datetime.now().date() - timedelta(days=days)
                    query += ' AND s.submission_date >= ?'
                    params.append(cutoff_date)
                
                # Get latest submission for each agent
                query += '''
                    AND s.id IN (
                        SELECT MAX(s2.id)
                        FROM submissions s2
                        JOIN agents a2 ON s2.agent_id = a2.id
                        WHERE a2.agent_name = a.agent_name
                '''
                
                if days:
                    query += ' AND s2.submission_date >= ?'
                    params.append(cutoff_date)
                
                query += ')'
                
                query += f' ORDER BY s.{stat.lower().replace(" ", "_")} DESC LIMIT ?'
                params.append(limit)
                
                cursor.execute(query, params)
                return cursor.fetchall()
                
        except sqlite3.Error as e:
            logging.error(f"Error getting leaderboard: {e}")
            return []
    
    def get_agent_progress(self, agent_name: str, telegram_user_id: int, 
                          stat: str, days: int = 30) -> List[Tuple]:
        """Get agent's progress over time for a specific stat"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cutoff_date = datetime.now().date() - timedelta(days=days)
                
                cursor.execute(f'''
                    SELECT s.submission_date, s.{stat.lower().replace(' ', '_')}
                    FROM submissions s
                    JOIN agents a ON s.agent_id = a.id
                    WHERE a.agent_name = ? AND a.telegram_user_id = ?
                    AND s.submission_date >= ?
                    ORDER BY s.submission_date ASC
                ''', (agent_name, telegram_user_id, cutoff_date))
                
                return cursor.fetchall()
                
        except sqlite3.Error as e:
            logging.error(f"Error getting agent progress: {e}")
            return []
    
    def get_faction_stats(self, days: Optional[int] = None) -> Dict:
        """Get faction comparison statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT a.faction, 
                           COUNT(DISTINCT a.agent_name) as agent_count,
                           AVG(s.level) as avg_level,
                           SUM(s.current_ap) as total_ap,
                           SUM(s.portals_captured) as total_portals_captured
                    FROM submissions s
                    JOIN agents a ON s.agent_id = a.id
                    WHERE s.id IN (
                        SELECT MAX(s2.id)
                        FROM submissions s2
                        JOIN agents a2 ON s2.agent_id = a2.id
                        WHERE a2.agent_name = a.agent_name
                '''
                
                params = []
                if days:
                    cutoff_date = datetime.now().date() - timedelta(days=days)
                    query += ' AND s2.submission_date >= ?'
                    params.append(cutoff_date)
                
                query += ') GROUP BY a.faction'
                
                cursor.execute(query, params)
                results = cursor.fetchall()
                
                faction_stats = {}
                for row in results:
                    faction_stats[row[0]] = {
                        'agent_count': row[1],
                        'avg_level': round(row[2], 1) if row[2] else 0,
                        'total_ap': row[3] or 0,
                        'total_portals_captured': row[4] or 0
                    }
                
                return faction_stats
                
        except sqlite3.Error as e:
            logging.error(f"Error getting faction stats: {e}")
            return {}