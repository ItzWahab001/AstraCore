from __future__ import annotations
import shutil, time
from dataclasses import dataclass

@dataclass(frozen=True)
class HealthReport:
    status:str; uptime:float; ffmpeg:bool; database:str

def build_health(started:float, database_status:str='unknown', ffmpeg_path:str='ffmpeg')->HealthReport:
    ffmpeg=bool(shutil.which(ffmpeg_path) if ffmpeg_path=='ffmpeg' else shutil.which(ffmpeg_path) or __import__('os').path.exists(ffmpeg_path))
    ok=database_status in {'ok','sqlite','postgres'} and ffmpeg
    return HealthReport('healthy' if ok else 'degraded',time.time()-started,ffmpeg,database_status)
