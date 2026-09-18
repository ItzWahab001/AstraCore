import discord
from discord import app_commands
from discord.ext import commands
from services.player import manager
from services.rate_limit import limiter, RateLimitExceeded
from database.db import db

class Music(commands.Cog):
    def __init__(self,bot):self.bot=bot
    async def ensure_vc(self,i):
        if not i.guild or not i.user.voice or not i.user.voice.channel:raise RuntimeError('Join a voice channel first.')
        ok,retry=await limiter.check(f'music:{i.guild.id}:{i.user.id}',8,10)
        if not ok:raise RateLimitExceeded(retry)
        return await manager.connect(i.guild.id,i.user.voice.channel)
    async def save_state(self,gid):
        p=manager.get(gid);c=p.current
        await db.execute('INSERT INTO music_state(guild_id,channel_id,voice_channel_id,current_url,current_title,position_seconds,volume,loop_mode) VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(guild_id) DO UPDATE SET channel_id=excluded.channel_id,voice_channel_id=excluded.voice_channel_id,current_url=excluded.current_url,current_title=excluded.current_title,position_seconds=excluded.position_seconds,volume=excluded.volume,loop_mode=excluded.loop_mode,updated_at=CURRENT_TIMESTAMP',(gid,p.channel_id,getattr(p.voice.channel,'id',None) if p.voice else None,c.webpage if c else None,c.title if c else None,manager.position(gid),p.volume,p.loop))
    @app_commands.command(name='play',description='Queue a URL or searchable query.')
    async def play(self,i,query:str):
        await i.response.defer()
        try:
            p=await self.ensure_vc(i);t=await manager.resolve(query,i.user.id);await manager.enqueue(i.guild.id,t);await self.save_state(i.guild.id)
            await i.followup.send(f'🎵 Queued **{t.title}**')
        except RateLimitExceeded as e:await i.followup.send(f'⏳ Slow down. Retry in {e.retry_after:.1f}s.')
        except Exception as e:await i.followup.send(f'❌ Music error: {str(e)[:500]}')
    @app_commands.command(name='pause',description='Pause playback.')
    async def pause(self,i):await i.response.send_message('⏸️ Paused.' if await manager.pause(i.guild.id) else 'Nothing is playing.',ephemeral=True)
    @app_commands.command(name='resume',description='Resume playback.')
    async def resume(self,i):await i.response.send_message('▶️ Resumed.' if await manager.resume(i.guild.id) else 'Nothing is paused.',ephemeral=True)
    @app_commands.command(name='skip',description='Skip the current track.')
    async def skip(self,i):await i.response.send_message('⏭️ Skipped.' if await manager.skip(i.guild.id) else 'Nothing is playing.',ephemeral=True)
    @app_commands.command(name='previous',description='Replay the previous track.')
    async def previous(self,i):await i.response.send_message('⏮️ Previous track queued.' if await manager.previous(i.guild.id) else 'No previous track.',ephemeral=True)
    @app_commands.command(name='replay',description='Restart the current track.')
    async def replay(self,i):await i.response.send_message('🔄 Replaying.' if await manager.replay(i.guild.id) else 'Nothing is playing.',ephemeral=True)
    @app_commands.command(name='seek',description='Seek to a position in seconds.')
    async def seek(self,i,seconds:app_commands.Range[int,0,86400]):await i.response.send_message('⏩ Seeked.' if await manager.seek(i.guild.id,seconds) else 'Nothing is playing.',ephemeral=True)
    @app_commands.command(name='stop',description='Stop playback and clear the queue.')
    async def stop(self,i):await manager.disconnect(i.guild.id);await i.response.send_message('⏹️ Stopped.',ephemeral=True)
    @app_commands.command(name='queue',description='Show the current queue.')
    async def queue(self,i):
        p=manager.get(i.guild.id);d='\n'.join(f'{n}. {t.title}' for n,t in enumerate(p.queue,1)) or 'Queue is empty.';await i.response.send_message(embed=discord.Embed(title='🎵 Queue',description=d[:4000]))
    @app_commands.command(name='remove',description='Remove a queue item.')
    async def remove(self,i,position:app_commands.Range[int,1,100]):
        p=manager.get(i.guild.id)
        if position>len(p.queue):return await i.response.send_message('That queue position does not exist.',ephemeral=True)
        q=list(p.queue);removed=q.pop(position-1);p.queue.clear();p.queue.extend(q);await i.response.send_message(f'🗑️ Removed **{removed.title}**.',ephemeral=True)
    @app_commands.command(name='shuffle',description='Shuffle the queue.')
    async def shuffle(self,i):
        import random
        p=manager.get(i.guild.id);q=list(p.queue);random.shuffle(q);p.queue.clear();p.queue.extend(q);await i.response.send_message('🔀 Queue shuffled.',ephemeral=True)
    @app_commands.command(name='loop',description='Set loop mode: off, track, or queue.')
    async def loop(self,i,mode:str):
        if mode not in {'off','track','queue'}:return await i.response.send_message('Mode must be off, track, or queue.',ephemeral=True)
        manager.get(i.guild.id).loop=mode;await self.save_state(i.guild.id);await i.response.send_message(f'🔁 Loop: **{mode}**',ephemeral=True)
    @app_commands.command(name='autoplay',description='Toggle autoplay mode.')
    async def autoplay(self,i,enabled:bool):
        p=manager.get(i.guild.id);setattr(p,'autoplay',enabled);await i.response.send_message(f'🤖 Autoplay: **{"ON" if enabled else "OFF"}**',ephemeral=True)
    @app_commands.command(name='volume',description='Set volume from 0 to 100.')
    async def volume(self,i,level:app_commands.Range[int,0,100]):
        p=manager.get(i.guild.id);p.volume=level/100
        if p.voice and getattr(p.voice,'source',None) and hasattr(p.voice.source,'volume'):p.voice.source.volume=p.volume
        await self.save_state(i.guild.id);await i.response.send_message(f'🔊 Volume: **{level}%**',ephemeral=True)
    @app_commands.command(name='nowplaying',description='Show the current track and position.')
    async def nowplaying(self,i):
        p=manager.get(i.guild.id)
        if not p.current:return await i.response.send_message('Nothing is playing.',ephemeral=True)
        await i.response.send_message(f'🎶 **{p.current.title}**\nProgress: `{manager.position(i.guild.id)}s / {p.current.duration or "?"}s`',ephemeral=True)
    @app_commands.command(name='music-dashboard',description='Open the interactive music player.')
    async def music_dashboard(self,i):
        from views.music_panel import MusicPanel
        await i.response.send_message(embed=MusicPanel.embed(i.guild.id),view=MusicPanel(self.bot,i.guild.id),ephemeral=True)

async def setup(bot):await bot.add_cog(Music(bot))
