from .player import manager

# Backwards-compatible service export for integrations that import MusicService.
class MusicService:
    def __init__(self):
        self.manager = manager

    def player(self, guild_id):
        return self.manager.get(guild_id)
