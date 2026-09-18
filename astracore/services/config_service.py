import json
from database.db import db
from services.cache import config_cache
DEFAULT={}

async def get(guild_id):
    key=f'guild:{guild_id}'
    cached=await config_cache.get(key)
    if cached is not None:return dict(cached)
    row=await db.fetchone('SELECT data FROM guild_settings WHERE guild_id=?',(guild_id,))
    data=json.loads(row['data']) if row else {}
    await config_cache.set(key,data);return dict(data)

async def set_value(guild_id,key,value):
    data=await get(guild_id);data[key]=value
    await db.execute('INSERT INTO guild_settings(guild_id,data) VALUES(?,?) ON CONFLICT(guild_id) DO UPDATE SET data=excluded.data,updated_at=CURRENT_TIMESTAMP',(guild_id,json.dumps(data,separators=(',',':'))))
    await config_cache.set(f'guild:{guild_id}',data);return data

async def update(guild_id,values):
    data=await get(guild_id);data.update(values)
    await db.execute('INSERT INTO guild_settings(guild_id,data) VALUES(?,?) ON CONFLICT(guild_id) DO UPDATE SET data=excluded.data,updated_at=CURRENT_TIMESTAMP',(guild_id,json.dumps(data,separators=(',',':'))));await config_cache.set(f'guild:{guild_id}',data);return data
