from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()

def i(name: str, default=0):
    try: return int(os.getenv(name, str(default)) or default)
    except ValueError: return default

def b(name: str, default=False): return os.getenv(name, str(default)).lower() in {'1','true','yes','on'}

@dataclass(frozen=True)
class Settings:
    token: str = os.getenv('DISCORD_TOKEN', os.getenv('BOT_TOKEN',''))
    database_url: str = os.getenv('DATABASE_URL','sqlite+aiosqlite:///data/astracore.db')
    ai_api_key: str = os.getenv('AI_API_KEY','')
    ai_base_url: str = os.getenv('AI_BASE_URL','')
    ai_model: str = os.getenv('AI_MODEL','')
    spotify_client_id: str = os.getenv('SPOTIFY_CLIENT_ID','')
    spotify_client_secret: str = os.getenv('SPOTIFY_CLIENT_SECRET','')
    ffmpeg_path: str = os.getenv('FFMPEG_PATH','ffmpeg')
    status_text: str = os.getenv('STATUS_TEXT','AstraCore')
    log_level: str = os.getenv('LOG_LEVEL','INFO')
    sync_commands: bool = b('SYNC_COMMANDS', True)
    default_role_id: int = i('DEFAULT_ROLE_ID')
    verified_role_id: int = i('VERIFIED_ROLE_ID', i('VERIFICATION_ROLE_ID'))
    unverified_role_id: int = i('UNVERIFIED_ROLE_ID')
    verification_channel_id: int = i('VERIFICATION_CHANNEL_ID')
    log_channel_id: int = i('LOG_CHANNEL_ID')
    ticket_category_id: int = i('TICKET_CATEGORY_ID')
    staff_role_id: int = i('STAFF_ROLE_ID')
settings = Settings()
