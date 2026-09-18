import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'astracore'))
from astracore.main import bot, settings
if __name__=='__main__':
    if not settings.token: raise SystemExit('DISCORD_TOKEN/BOT_TOKEN is missing. Configure .env.')
    bot.run(settings.token,log_handler=None)
