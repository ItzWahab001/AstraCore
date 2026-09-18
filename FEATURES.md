# Implemented Capability Manifest

This file is intentionally descriptive rather than inflating a numeric command count.

## Core
- Interactive category help
- Ping/latency
- Health/uptime
- Shard info
- Server information
- User information
- Avatar display
- Role information
- Channel information
- Snowflake timestamp inspection
- Safe arithmetic calculator
- Discord timestamp formatting
- Permission inspection
- Centralized application-command error responses
- DND presence on ready/reconnect

## Moderation
- Warning case creation
- Kick case creation
- Ban case creation
- Unban case creation
- Timeout case creation
- Timeout removal
- Case history per user
- Recent guild case history
- Message purge
- Slowmode
- Channel lock
- Channel unlock
- Hierarchy protection

## AutoMod/Security
- Blocked words
- Mention limits
- Invite blocking
- Maximum message length
- Burst/flood detection
- Role exemptions
- Join-rate monitoring
- Configurable anti-raid threshold
- Automatic lockdown trigger
- Manual emergency lockdown
- Manual lockdown recovery
- Security status display

## Verification
- Persistent verification component
- Verified role assignment
- Unverified role removal
- Join-time unverified role
- Join-time default role
- Verification configuration IDs

## Tickets
- Category selection
- Private ticket creation
- Staff access
- Claim
- Close
- Persistent ticket record
- Ticket status update

## Music
- Query/URL resolution with yt-dlp
- Per-guild player isolation
- Voice-channel join
- Voice-channel move
- Play
- Queue
- Pause
- Resume
- Skip
- Stop
- Queue item removal
- Shuffle
- Loop off/track/queue
- Volume
- Now playing
- FFmpeg validation
- Stream reconnect flags
- Player cleanup

## AI
- Configurable OpenAI-compatible endpoint
- Configurable model
- Environment-only API key
- Timeout
- Retry for transient provider failures
- Provider error handling
- Per-user/guild rate limiting
- AI assistant command
- Teacher command

## Leveling
- Message XP
- XP cooldown
- Level calculation
- Level-up notification
- Rank lookup
- XP leaderboard
- Admin XP set
- Admin XP add

## Economy
- Balance
- Daily reward
- Work reward
- Transfer
- Transaction records
- Economy leaderboard
- Cooldowns

## Giveaways
- Timed giveaway creation
- Persistent giveaway records
- Persistent entry records
- Entry toggle
- Automatic ending task
- Manual ending
- Winner selection
- Reroll

## Community
- Suggestion submission
- Suggestion voting reactions
- Suggestion status
- Starboard threshold configuration
- Starboard creation/update
- Persistent reminders
- Reminder listing
- Reminder deletion
- Restart recovery for pending reminders

## Temporary voice
- Trigger configuration
- Temporary room creation
- Ownership tracking
- Automatic empty-room deletion
- Owner rename
- Owner user-limit control

## Roles
- Self-role validation
- Self-role add/remove
- Configurable self-role allowlist

## Custom commands
- Create
- Edit via upsert
- Delete
- List
- Variables
- Cooldowns
- Usage counters
- Enable state

## Administration
- Per-guild JSON configuration
- Supported-key validation
- Interactive configuration display
- Administrator permission checks

## Testing / delivery
- Syntax compilation verification performed during packaging
- Database initialization test
- Environment file test
- Dockerfile
- Railway configuration
- README
- .gitignore

The long-term 500+ target remains a roadmap metric. This package does not misrepresent the above capabilities as 500 separate production-tested commands.
