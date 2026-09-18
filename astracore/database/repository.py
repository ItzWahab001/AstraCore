from __future__ import annotations
import json
from .db import db

class GuildRepository:
    async def get_settings(self,guild_id:int)->dict:
        row=await db.fetchone('SELECT data FROM guild_settings WHERE guild_id=?',(guild_id,)); return json.loads(row['data']) if row else {}
    async def update_settings(self,guild_id:int,updates:dict)->dict:
        data=await self.get_settings(guild_id); data.update(updates)
        await db.execute('INSERT INTO guild_settings(guild_id,data) VALUES(?,?) ON CONFLICT(guild_id) DO UPDATE SET data=excluded.data,updated_at=CURRENT_TIMESTAMP',(guild_id,json.dumps(data,separators=(',',':')))); return data
    async def delete_setting(self,guild_id:int,key:str)->dict:
        data=await self.get_settings(guild_id);data.pop(key,None);return await self.update_settings(guild_id,data)
    async def has_setting(self,guild_id:int,key:str)->bool:return key in await self.get_settings(guild_id)
    async def get_setting(self,guild_id:int,key:str,default=None):return (await self.get_settings(guild_id)).get(key,default)
    async def set_setting(self,guild_id:int,key:str,value):return await self.update_settings(guild_id,{key:value})

guild_repo=GuildRepository()
