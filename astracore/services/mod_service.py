import discord
from database.db import db
async def case(guild_id,user_id,moderator_id,kind,reason='',expires_at=None):
    return await db.execute('INSERT INTO cases(guild_id,user_id,moderator_id,type,reason,expires_at) VALUES(?,?,?,?,?,?)',(guild_id,user_id,moderator_id,kind,reason,expires_at))
async def history(guild_id,user_id=None,limit=20):
    if user_id:return await db.fetchall('SELECT * FROM cases WHERE guild_id=? AND user_id=? ORDER BY id DESC LIMIT ?',(guild_id,user_id,limit))
    return await db.fetchall('SELECT * FROM cases WHERE guild_id=? ORDER BY id DESC LIMIT ?',(guild_id,limit))
async def timeout(member:discord.Member,seconds:int,reason:str):
    until=discord.utils.utcnow()+discord.timedelta(seconds=seconds) if hasattr(discord,'timedelta') else None
    # discord.py uses datetime.timedelta; caller supplies validated duration.
    import datetime
    await member.timeout(datetime.timedelta(seconds=seconds),reason=reason)
