from __future__ import annotations
import asyncio, shutil, time
from dataclasses import dataclass, field
from collections import deque
import discord, yt_dlp
from config import settings

@dataclass
class Track:
    title:str; webpage:str; stream_url:str|None=None; duration:int=0; requester_id:int=0; position:int=0

@dataclass
class Player:
    guild_id:int; queue:deque=field(default_factory=deque); current:Track|None=None
    voice:discord.VoiceClient|None=None; volume:float=0.5; loop:str='off'
    history:deque=field(default_factory=lambda:deque(maxlen=25)); started_at:float=0.0
    task:asyncio.Task|None=None; generation:int=0; channel_id:int|None=None; restart_current:bool=False; autoplay:bool=False
    lock:asyncio.Lock=field(default_factory=asyncio.Lock,repr=False)

class MusicManager:
    def __init__(self):self.players:dict[int,Player]={}
    def get(self,gid:int)->Player:return self.players.setdefault(gid,Player(gid))
    def drop(self,gid:int):self.players.pop(gid,None)
    async def resolve(self,query,requester_id=0):
        opts={'format':'bestaudio/best','noplaylist':True,'quiet':True,'no_warnings':True,'default_search':'ytsearch'}
        loop=asyncio.get_running_loop()
        def extract():
            with yt_dlp.YoutubeDL(opts) as y:return y.extract_info(query,download=False)
        data=await loop.run_in_executor(None,extract)
        if 'entries' in data:data=next((x for x in data['entries'] if x),None)
        if not data:raise RuntimeError('No playable result was found.')
        return Track(data.get('title','Unknown'),data.get('webpage_url',query),data.get('url'),int(data.get('duration') or 0),requester_id)
    async def connect(self,gid,channel):
        p=self.get(gid);p.channel_id=getattr(channel,'id',None)
        if not p.voice or not p.voice.is_connected():p.voice=await channel.connect()
        elif p.voice.channel!=channel:await p.voice.move_to(channel)
        return p
    async def enqueue(self,gid,track):
        p=self.get(gid);p.queue.append(track)
        if not p.task or p.task.done():p.task=asyncio.create_task(self._run(gid),name=f'astracore-music-{gid}')
    async def _run(self,gid):
        p=self.get(gid)
        while p.voice and p.voice.is_connected() and (p.queue or p.current):
            if p.current is None:
                p.current=p.queue.popleft() if p.queue else None
            if p.current is None:break
            try:await self._play_track(p,p.current)
            except asyncio.CancelledError:raise
            except Exception:
                # A failed stream should not permanently kill the guild player.
                p.history.append(p.current);p.current=None
                if not p.queue:break
            else:
                finished=p.current
                if finished:p.history.append(finished)
                if p.loop=='queue' and finished:p.queue.append(finished)
                if p.restart_current:
                    p.restart_current=False
                elif p.loop!='track':p.current=None
                else:p.current=finished
                if p.autoplay and p.current is None and not p.queue and finished:
                    try:p.queue.append(await self.resolve(f'ytsearch1:{finished.title} mix',finished.requester_id))
                    except Exception:pass
        p.started_at=0
    async def _play_track(self,p,track):
        if not p.voice or not p.voice.is_connected():return
        if not track.stream_url:
            fresh=await self.resolve(track.webpage,track.requester_id);track.stream_url=fresh.stream_url;track.title=fresh.title;track.duration=fresh.duration
        if not shutil.which(settings.ffmpeg_path) and settings.ffmpeg_path=='ffmpeg':raise RuntimeError('FFmpeg executable was not found.')
        before='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
        if track.position>0:before=f'-ss {track.position} '+before
        source=discord.FFmpegPCMAudio(track.stream_url,executable=settings.ffmpeg_path,before_options=before,options='-vn')
        source=discord.PCMVolumeTransformer(source,volume=p.volume)
        loop=asyncio.get_running_loop();done=loop.create_future();p.started_at=time.monotonic()-track.position
        def after(error):
            loop.call_soon_threadsafe(lambda: done.set_exception(error) if error and not done.done() else (done.set_result(None) if not done.done() else None))
        p.voice.play(source,after=after)
        await done
        track.position=0
    async def pause(self,gid):
        p=self.get(gid)
        if p.voice and p.voice.is_playing():p.voice.pause();return True
        return False
    async def resume(self,gid):
        p=self.get(gid)
        if p.voice and p.voice.is_paused():p.voice.resume();return True
        return False
    async def skip(self,gid):
        p=self.get(gid)
        if p.voice and (p.voice.is_playing() or p.voice.is_paused()):p.voice.stop();return True
        return False
    async def seek(self,gid,seconds:int):
        p=self.get(gid)
        if not p.current or not p.voice: return False
        p.current.position=max(0,min(seconds,p.current.duration or seconds));p.restart_current=True;p.generation+=1;p.voice.stop();return True
    async def previous(self,gid):
        p=self.get(gid)
        if not p.history:return False
        if p.current:p.queue.appendleft(p.current)
        p.current=p.history.pop();p.current.position=0
        if p.voice and (p.voice.is_playing() or p.voice.is_paused()):p.voice.stop()
        elif p.voice and p.voice.is_connected() and (not p.task or p.task.done()):p.task=asyncio.create_task(self._run(gid))
        return True
    async def replay(self,gid):
        p=self.get(gid)
        if not p.current:return False
        p.current.position=0;p.restart_current=True
        if p.voice and (p.voice.is_playing() or p.voice.is_paused()):p.voice.stop()
        return True
    def position(self,gid):
        p=self.get(gid)
        if not p.current or not p.started_at:return 0
        return max(0,int(time.monotonic()-p.started_at))
    async def recover_voice(self,gid,channel):
        p=self.get(gid);was=p.current
        if p.voice and p.voice.is_connected():return True
        p.voice=None
        if channel is None:return False
        await self.connect(gid,channel)
        if was and (not p.task or p.task.done()):
            p.current = was
            p.task = asyncio.create_task(self._run(gid), name=f'astracore-music-{gid}')
        return True
    async def disconnect(self,gid,clear=True):
        p=self.get(gid)
        if p.task and not p.task.done():p.task.cancel()
        if p.voice and p.voice.is_connected():await p.voice.disconnect(force=True)
        p.voice=None;p.current=None;p.started_at=0
        if clear:p.queue.clear();p.history.clear()

manager=MusicManager()
