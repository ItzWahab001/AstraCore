from __future__ import annotations
import json, re
from pathlib import Path
from config import settings

SQLITE_SCHEMA='''
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS guild_settings(guild_id INTEGER PRIMARY KEY, data TEXT NOT NULL DEFAULT '{}', updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS users(guild_id INTEGER NOT NULL,user_id INTEGER NOT NULL,data TEXT NOT NULL DEFAULT '{}',PRIMARY KEY(guild_id,user_id));
CREATE TABLE IF NOT EXISTS cases(id INTEGER PRIMARY KEY AUTOINCREMENT,guild_id INTEGER NOT NULL,user_id INTEGER NOT NULL,moderator_id INTEGER NOT NULL,type TEXT NOT NULL,reason TEXT,expires_at TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX IF NOT EXISTS idx_cases_guild_user ON cases(guild_id,user_id);
CREATE INDEX IF NOT EXISTS idx_cases_guild_type ON cases(guild_id,type);
CREATE TABLE IF NOT EXISTS tickets(id INTEGER PRIMARY KEY AUTOINCREMENT,guild_id INTEGER NOT NULL,channel_id INTEGER UNIQUE NOT NULL,opener_id INTEGER NOT NULL,claimed_by INTEGER DEFAULT 0,status TEXT DEFAULT 'open',created_at TEXT DEFAULT CURRENT_TIMESTAMP,closed_at TEXT);
CREATE TABLE IF NOT EXISTS xp(guild_id INTEGER NOT NULL,user_id INTEGER NOT NULL,xp INTEGER DEFAULT 0,level INTEGER DEFAULT 0,PRIMARY KEY(guild_id,user_id));
CREATE INDEX IF NOT EXISTS idx_xp_guild ON xp(guild_id,xp DESC);
CREATE TABLE IF NOT EXISTS economy(guild_id INTEGER NOT NULL,user_id INTEGER NOT NULL,balance INTEGER DEFAULT 0,PRIMARY KEY(guild_id,user_id));
CREATE TABLE IF NOT EXISTS inventory(guild_id INTEGER NOT NULL,user_id INTEGER NOT NULL,item TEXT NOT NULL,qty INTEGER DEFAULT 0,PRIMARY KEY(guild_id,user_id,item));
CREATE TABLE IF NOT EXISTS transactions(id INTEGER PRIMARY KEY AUTOINCREMENT,guild_id INTEGER NOT NULL,user_id INTEGER NOT NULL,kind TEXT NOT NULL,amount INTEGER NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX IF NOT EXISTS idx_transactions_user_time ON transactions(guild_id,user_id,created_at);
CREATE TABLE IF NOT EXISTS giveaways(id INTEGER PRIMARY KEY AUTOINCREMENT,guild_id INTEGER NOT NULL,channel_id INTEGER NOT NULL,message_id INTEGER UNIQUE NOT NULL,ends_at TEXT NOT NULL,prize TEXT NOT NULL,winners INTEGER NOT NULL,status TEXT DEFAULT 'running',requirements TEXT DEFAULT '{}');
CREATE TABLE IF NOT EXISTS giveaway_entries(giveaway_id INTEGER NOT NULL,user_id INTEGER NOT NULL,PRIMARY KEY(giveaway_id,user_id));
CREATE TABLE IF NOT EXISTS reminders(id INTEGER PRIMARY KEY AUTOINCREMENT,guild_id INTEGER,user_id INTEGER NOT NULL,channel_id INTEGER,content TEXT NOT NULL,due_at TEXT NOT NULL,recurring_seconds INTEGER DEFAULT 0,status TEXT DEFAULT 'pending');
CREATE INDEX IF NOT EXISTS idx_reminders_due ON reminders(status,due_at);
CREATE TABLE IF NOT EXISTS suggestions(id INTEGER PRIMARY KEY AUTOINCREMENT,guild_id INTEGER NOT NULL,channel_id INTEGER NOT NULL,message_id INTEGER UNIQUE NOT NULL,author_id INTEGER NOT NULL,text TEXT NOT NULL,status TEXT DEFAULT 'pending');
CREATE TABLE IF NOT EXISTS starboard(message_id INTEGER PRIMARY KEY,guild_id INTEGER NOT NULL,stars INTEGER NOT NULL,starboard_message_id INTEGER);
CREATE TABLE IF NOT EXISTS custom_commands(guild_id INTEGER NOT NULL,name TEXT NOT NULL,response TEXT NOT NULL,enabled INTEGER DEFAULT 1,cooldown INTEGER DEFAULT 0,uses INTEGER DEFAULT 0,PRIMARY KEY(guild_id,name));
CREATE TABLE IF NOT EXISTS role_menus(id INTEGER PRIMARY KEY AUTOINCREMENT,guild_id INTEGER NOT NULL,message_id INTEGER UNIQUE NOT NULL,roles TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS music_state(guild_id INTEGER PRIMARY KEY,channel_id INTEGER,voice_channel_id INTEGER,current_url TEXT,current_title TEXT,position_seconds INTEGER DEFAULT 0,volume REAL DEFAULT 0.5,loop_mode TEXT DEFAULT 'off',updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS security_events(id INTEGER PRIMARY KEY AUTOINCREMENT,guild_id INTEGER NOT NULL,actor_id INTEGER NOT NULL,action TEXT NOT NULL,target_id INTEGER,risk INTEGER NOT NULL,decision TEXT NOT NULL,reason TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX IF NOT EXISTS idx_security_events_guild_time ON security_events(guild_id,created_at);
CREATE TABLE IF NOT EXISTS migrations(version INTEGER PRIMARY KEY, applied_at TEXT DEFAULT CURRENT_TIMESTAMP);
'''
POSTGRES_SCHEMA=SQLITE_SCHEMA.replace('PRAGMA foreign_keys=ON;','').replace('INTEGER PRIMARY KEY AUTOINCREMENT','BIGSERIAL PRIMARY KEY').replace('INTEGER PRIMARY KEY','BIGINT PRIMARY KEY').replace('INTEGER NOT NULL','BIGINT NOT NULL').replace('INTEGER DEFAULT','BIGINT DEFAULT').replace('INTEGER UNIQUE','BIGINT UNIQUE').replace('INTEGER,','BIGINT,').replace('INTEGER)','BIGINT)').replace('REAL DEFAULT','DOUBLE PRECISION DEFAULT')

def _is_postgres(url:str)->bool:return url.startswith(('postgres://','postgresql://','postgresql+asyncpg://'))
def _sqlite_path(url:str)->str:
    if url.startswith('sqlite'): return url.split('///',1)[-1]
    return 'data/astracore.db'

def _pg_sql(q:str):
    # Existing cogs use DB-agnostic ? placeholders. Convert to asyncpg $n.
    return re.sub(r'\?', lambda m: f'${_pg_sql.counter.__next__()}', q)
_pg_sql.counter=lambda:None

def _convert_pg(q:str)->str:
    n=0
    def repl(_):
        nonlocal n;n+=1;return f'${n}'
    return re.sub(r'\?',repl,q)

class Database:
    def __init__(self):
        self.url=settings.database_url
        self.postgres=_is_postgres(self.url)
        self.path=_sqlite_path(self.url)
        self._pool=None
    async def init(self):
        if self.postgres:
            try:
                import asyncpg
            except ImportError as e: raise RuntimeError('PostgreSQL configured but asyncpg is not installed.') from e
            self._pool=await asyncpg.create_pool(self.url,min_size=1,max_size=10,command_timeout=30)
            async with self._pool.acquire() as conn: await conn.execute(POSTGRES_SCHEMA)
        else:
            import aiosqlite
            Path(self.path).parent.mkdir(parents=True,exist_ok=True)
            async with aiosqlite.connect(self.path) as conn:
                await conn.execute('PRAGMA foreign_keys=ON'); await conn.executescript(SQLITE_SCHEMA); await conn.commit()
    async def close(self):
        if self._pool: await self._pool.close(); self._pool=None
    async def fetchone(self,q,p=()):
        if self.postgres:
            async with self._pool.acquire() as c:
                return await c.fetchrow(_convert_pg(q),*p)
        import aiosqlite
        async with aiosqlite.connect(self.path) as c:
            c.row_factory=aiosqlite.Row; cur=await c.execute(q,p); return await cur.fetchone()
    async def fetchall(self,q,p=()):
        if self.postgres:
            async with self._pool.acquire() as c:return await c.fetch(_convert_pg(q),*p)
        import aiosqlite
        async with aiosqlite.connect(self.path) as c:
            c.row_factory=aiosqlite.Row; cur=await c.execute(q,p); return await cur.fetchall()
    async def execute(self,q,p=()):
        if self.postgres:
            async with self._pool.acquire() as c:
                # Return inserted primary key when available, preserving the existing API.
                if re.match(r'\s*INSERT\s+INTO',q,re.I) and 'RETURNING' not in q.upper():
                    m=re.search(r'INSERT\s+INTO\s+([\w]+)',q,re.I); table=m.group(1) if m else ''
                    q=q.rstrip(';')+' RETURNING id' if table in {'cases','tickets','transactions','giveaways','reminders','suggestions','role_menus','security_events'} else q
                result=await c.fetchval(_convert_pg(q),*p) if 'RETURNING id' in q else await c.execute(_convert_pg(q),*p)
                return result if isinstance(result,int) else None
        import aiosqlite
        async with aiosqlite.connect(self.path) as c:
            cur=await c.execute(q,p); await c.commit(); return cur.lastrowid
    async def transaction(self,statements):
        if self.postgres:
            async with self._pool.acquire() as c:
                async with c.transaction():
                    for q,p in statements:await c.execute(_convert_pg(q),*p)
            return
        import aiosqlite
        async with aiosqlite.connect(self.path) as c:
            try:
                await c.execute('BEGIN')
                for q,p in statements:await c.execute(q,p)
                await c.commit()
            except Exception: await c.rollback();raise
    async def health(self)->str:
        try:
            row=await self.fetchone('SELECT 1 AS ok')
            return 'postgres' if self.postgres and row else ('sqlite' if row else 'degraded')
        except Exception:return 'degraded'

db=Database()
