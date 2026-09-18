# AstraCore — Production-Oriented Upgrade

AstraCore is a modular `discord.py 2.x` Discord bot foundation designed for large servers. This upgrade preserves the existing project direction while separating commands, services, persistent data, UI, and configuration.

## What is implemented

### Core
- Slash commands and interactive help
- Centralized application-command error handling
- DND presence reapplied on every ready/reconnect event
- Async SQLite repository/database layer with indexes and transactions
- Environment-only secrets
- Per-guild configuration storage
- Health, server and user utilities

### Moderation
- warn, kick, ban, unban, timeout, untimeout
- moderation case IDs and history
- clear messages
- slowmode
- lock/unlock
- role hierarchy checks

### Security / AutoMod
- configurable flood detection
- mention-limit enforcement
- invite blocking
- blocked words
- message length limits
- role exemptions
- join-rate anti-raid monitoring
- configurable emergency lockdown/unlockdown

### Verification / onboarding
- persistent verification button
- verified/unverified role transitions
- automatic onboarding role assignment
- configurable channel/role IDs

### Tickets
- persistent category select menu
- private channels
- staff access
- claim
- close
- persistent ticket records

### Music
- per-guild player state
- YouTube/search resolution through `yt-dlp`
- queue, pause, resume, skip, stop, remove, shuffle, loop, volume and now-playing controls
- FFmpeg validation
- voice reconnect/move handling
- isolated service architecture

**Source compatibility changes over time.** The project does not claim Spotify direct audio playback. Spotify credentials are intentionally optional and can be used by a future metadata resolver; Spotify is not treated as an audio-stream endpoint.

### AI
- OpenAI-compatible Chat Completions service
- configurable endpoint/model
- environment-only API key
- timeout and retry handling
- per-user/guild rate limiting
- `/ai` and `/teacher`

### Community
- XP/levels/rank/leaderboard
- economy balance/daily/work/pay/leaderboard
- persistent giveaways with saved entries/end/reroll
- suggestions and status tracking
- starboard threshold tracking
- persistent reminders with restart recovery
- temporary voice channels
- self-role configuration
- custom server commands with variables/cooldowns/usage tracking

## Important Discord configuration

Enable only the privileged intents the bot needs in the Developer Portal. This build uses Members and Message Content, plus voice/reaction/message events.

Recommended permissions depend on enabled modules. Moderation, role, channel, voice, and message-management features require their corresponding Discord permissions. Discord role hierarchy still applies: AstraCore cannot manage members or roles above its highest role.

## Install locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python astracore/main.py
```

Windows activation:
```powershell
.venv\Scripts\activate
```

## Railway

Set the environment variables from `.env.example` in Railway. The included Dockerfile installs FFmpeg. For persistent SQLite data, attach persistent storage or use PostgreSQL for a multi-instance/sharded deployment.

## Docker

```bash
docker build -t astracore .
docker run --env-file .env astracore
```

## Verification security

The bot assigns/removes roles, but Discord permission overwrites enforce visibility. Configure the unverified role so it can only see the onboarding/verification channels; grant the verified role access to normal server areas. Do not rely on the bot alone to hide private channels.

## Scaling guidance

SQLite is appropriate for a single-process/small deployment and development. For high-concurrency multi-instance production, migrate repositories to PostgreSQL, use a shared rate-limit/cache layer, shard Discord sessions, and centralize logs/metrics.

## Testing

Run:
```bash
pytest -q
```

The test suite is intentionally honest about external dependencies. Live Discord gateway, voice playback, third-party API credentials, and provider behavior require a real deployment and are not represented as locally mocked production tests.

## 500+ roadmap policy

AstraCore's long-term target is 500+ real capabilities across modules and subcommands. This repository intentionally does **not** inflate the count with duplicate or dummy commands. New capabilities should be added only when their persistence, permissions, error handling, UI and tests are implemented.

## Security

Never commit `.env`, bot tokens, API keys, or database files. Rotate credentials immediately if exposed. Use least-privilege Discord permissions and keep the bot's highest role below roles it must not manage.

## 10/10 production upgrade layers
- **Music 3.0:** isolated per-guild players, non-blocking playback tasks, queue lifecycle, previous/replay/seek, autoplay, loop modes, voice recovery, stream recovery, player dashboard, and persistent state records.
- **Premium control center:** `/dashboard` provides live, interactive controls for Moderation, AutoMod, Security, Music, Tickets, Verification, Welcome, Leveling, Economy, Giveaways, Roles, Temp Voice, Suggestions, Starboard, AI and Server Settings.
- **Security 2.0:** correlated action tracking, thresholds, exemptions, risk decisions, database event history, optional automatic protective lockdown, and recovery.
- **Database 2.0:** SQLite development mode plus PostgreSQL/asyncpg production mode, pooled PostgreSQL connections, transactions, indexes, idempotent schema and migration records.
- **Scalability:** TTL caching, shared sliding-window rate limiting, background task supervision primitives, shard-aware runtime information and per-guild isolation.
- **Observability:** JSON structured logs, health status, database/media checks, runtime metrics and command-error counters.
- **Capability toolkit:** 520 distinct deterministic production utility operations are registered across 20 major system domains; these are callable implementation helpers rather than inflated slash-command names.

## Verification
Run the dependency-free verifier before deployment:
```bash
python scripts_verify.py
```
Then run the full suite in an environment with dependencies installed:
```bash
pytest -q
```
The bundled environment used for packaging may not have network access to install Discord/DB dependencies, so live Discord gateway, PostgreSQL, voice/FFmpeg and external AI-provider integration still require the deployment environment's credentials and services.
