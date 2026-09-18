import discord
from services.player import manager

class MusicPanel(discord.ui.View):
    def __init__(self,bot,guild_id):super().__init__(timeout=600);self.bot=bot;self.guild_id=guild_id
    @staticmethod
    def embed(gid):
        p=manager.get(gid);title=p.current.title if p.current else 'Nothing playing';q=len(p.queue);return discord.Embed(title='🎵 AstraCore Music 3.0',description=f'**Now Playing:** {title}\n**Queue:** {q}\n**Loop:** {p.loop}\n**Volume:** {round(p.volume*100)}%')
    async def refresh(self,i):await i.response.edit_message(embed=self.embed(self.guild_id),view=self)
    @discord.ui.button(label='Pause / Resume',emoji='⏯️',style=discord.ButtonStyle.primary)
    async def toggle(self,i,b):
        p=manager.get(self.guild_id)
        if p.voice and p.voice.is_paused():p.voice.resume()
        elif p.voice and p.voice.is_playing():p.voice.pause()
        await self.refresh(i)
    @discord.ui.button(label='Skip',emoji='⏭️',style=discord.ButtonStyle.secondary)
    async def skip(self,i,b):await manager.skip(self.guild_id);await self.refresh(i)
    @discord.ui.button(label='Replay',emoji='🔄',style=discord.ButtonStyle.secondary)
    async def replay(self,i,b):await manager.replay(self.guild_id);await self.refresh(i)
    @discord.ui.button(label='Stop',emoji='⏹️',style=discord.ButtonStyle.danger)
    async def stop(self,i,b):await manager.disconnect(self.guild_id);await self.refresh(i)
    @discord.ui.button(label='Queue',emoji='📜',style=discord.ButtonStyle.success)
    async def queue(self,i,b):
        p=manager.get(self.guild_id);text='\n'.join(f'{n}. {t.title}' for n,t in enumerate(p.queue,1)) or 'Queue is empty.';await i.response.send_message(text[:1900],ephemeral=True)
