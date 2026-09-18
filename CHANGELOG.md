# AstraCore Upgrade

## 2026-09-18
- Reworked the project into a modular package under `astracore/`.
- Added async SQLite database schema, indexes, transactions and persistent records.
- Added centralized command error handling.
- Added moderation case framework and hierarchy checks.
- Added configurable AutoMod and anti-raid foundations.
- Added persistent verification/ticket components.
- Added per-guild music manager with yt-dlp/FFmpeg playback architecture.
- Added AI provider abstraction with retry/timeout handling.
- Added leveling, economy, giveaways, suggestions, starboard, reminders, temporary voice, roles and custom commands.
- Added tests, Docker deployment and Railway configuration.
- Performed Python bytecode compilation across project and tests before packaging.
