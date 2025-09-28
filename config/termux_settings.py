"""
Termux-specific settings for the Ingress Leaderboard Bot
This file contains Android/Termux optimized configurations
"""

import os
import sys
from pathlib import Path

# Detect if we're running in Termux
IS_TERMUX = os.environ.get('PREFIX', '').endswith('com.termux')

# Base paths
if IS_TERMUX:
    # Termux-specific paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / 'data'
    LOGS_DIR = BASE_DIR / 'logs'
    
    # Termux storage paths (if storage permission granted)
    TERMUX_STORAGE = Path.home() / 'storage'
    SHARED_STORAGE = TERMUX_STORAGE / 'shared' if TERMUX_STORAGE.exists() else None
    
    # Database path (prefer internal storage for security)
    DATABASE_PATH = DATA_DIR / 'ingress_leaderboard.db'
    
    # Log file path
    LOG_FILE = LOGS_DIR / 'bot.log'
    
    # Backup directory (can use shared storage if available)
    BACKUP_DIR = SHARED_STORAGE / 'IngressBot' if SHARED_STORAGE else DATA_DIR / 'backups'
    
else:
    # Standard paths for other systems
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / 'data'
    LOGS_DIR = BASE_DIR / 'logs'
    DATABASE_PATH = DATA_DIR / 'ingress_leaderboard.db'
    LOG_FILE = LOGS_DIR / 'bot.log'
    BACKUP_DIR = DATA_DIR / 'backups'

# Create directories if they don't exist
for directory in [DATA_DIR, LOGS_DIR, BACKUP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Termux-specific optimizations
TERMUX_CONFIG = {
    'use_wake_lock': IS_TERMUX,
    'enable_notifications': IS_TERMUX,
    'low_memory_mode': IS_TERMUX,
    'reduced_logging': IS_TERMUX,
    'auto_cleanup': IS_TERMUX,
    'max_log_size_mb': 10 if IS_TERMUX else 50,
    'max_backup_files': 3 if IS_TERMUX else 10,
}

# Logging configuration for Termux
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'termux': {
            'format': '%(asctime)s [%(levelname)s]: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'termux' if IS_TERMUX else 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'level': 'DEBUG' if not IS_TERMUX else 'INFO',
            'formatter': 'termux' if IS_TERMUX else 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_FILE),
            'maxBytes': TERMUX_CONFIG['max_log_size_mb'] * 1024 * 1024,
            'backupCount': TERMUX_CONFIG['max_backup_files'],
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['default', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

# Performance settings for Termux
PERFORMANCE_CONFIG = {
    'max_concurrent_requests': 5 if IS_TERMUX else 10,
    'request_timeout': 30 if IS_TERMUX else 60,
    'database_timeout': 10 if IS_TERMUX else 30,
    'cache_size': 100 if IS_TERMUX else 500,
    'cleanup_interval_hours': 6 if IS_TERMUX else 24,
}

# Bot-specific settings
BOT_CONFIG = {
    'read_timeout': 20 if IS_TERMUX else 30,
    'write_timeout': 20 if IS_TERMUX else 30,
    'connect_timeout': 10 if IS_TERMUX else 20,
    'pool_timeout': 5 if IS_TERMUX else 10,
}

def get_termux_info():
    """Get information about the Termux environment"""
    if not IS_TERMUX:
        return None
    
    info = {
        'is_termux': True,
        'prefix': os.environ.get('PREFIX', ''),
        'home': str(Path.home()),
        'storage_available': SHARED_STORAGE is not None,
        'python_version': sys.version,
        'platform': sys.platform,
    }
    
    # Check for Termux API
    try:
        import subprocess
        result = subprocess.run(['which', 'termux-notification'], 
                              capture_output=True, text=True)
        info['termux_api_available'] = result.returncode == 0
    except:
        info['termux_api_available'] = False
    
    return info

def send_termux_notification(title, content):
    """Send a notification using Termux API if available"""
    if not IS_TERMUX:
        return False
    
    try:
        import subprocess
        subprocess.run([
            'termux-notification',
            '--title', title,
            '--content', content,
            '--id', 'ingress_bot'
        ], check=True)
        return True
    except:
        return False

def acquire_wake_lock():
    """Acquire wake lock to prevent Android from killing the process"""
    if not IS_TERMUX:
        return False
    
    try:
        import subprocess
        subprocess.run(['termux-wake-lock'], check=True)
        return True
    except:
        return False

def release_wake_lock():
    """Release wake lock"""
    if not IS_TERMUX:
        return False
    
    try:
        import subprocess
        subprocess.run(['termux-wake-unlock'], check=True)
        return True
    except:
        return False

# Export commonly used paths and configs
__all__ = [
    'IS_TERMUX',
    'BASE_DIR',
    'DATA_DIR',
    'LOGS_DIR',
    'DATABASE_PATH',
    'LOG_FILE',
    'BACKUP_DIR',
    'TERMUX_CONFIG',
    'LOGGING_CONFIG',
    'PERFORMANCE_CONFIG',
    'BOT_CONFIG',
    'get_termux_info',
    'send_termux_notification',
    'acquire_wake_lock',
    'release_wake_lock',
]