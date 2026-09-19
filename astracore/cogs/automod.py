from __future__ import annotations

import re
import time
from collections import defaultdict
from typing import Iterable

import discord
from discord import app_commands
from discord.ext import commands

from services.config_service import get


class AutoMod(commands.Cog):
    """AstraCore custom moderation plus native Discord AutoMod integration."""

    SETUP_RULES = (
        ("AstraCore • Invite Protection", ["*discord.gg/*", "*discord.com/invite/*"]),
        ("AstraCore • Scam Gift Phrases", ["free nitro", "nitro gift", "claim nitro", "steam gift"]),
        ("AstraCore • Suspicious Promotion", ["dm me for nitro", "free crypto", "double your crypto"]),
    )

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.last: defaultdict[tuple[int, int], list[float]] = defaultdict(list)

    # ------------------------------------------------------------------
    # Existing AstraCore custom AutoMod layer
    # ------------------------------------------------------------------
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or not message.guild:
            return

        config = await get(message.guild.id)
        cfg = config.get("automod", {})
        if not cfg.get("enabled", False):
            return
        if any(role.id in cfg.get("exempt_role_ids", []) for role in getattr(message.author, "roles", [])):
            return

        reasons: list[str] = []
        text = message.content
        words = {str(x).lower() for x in cfg.get("bad_words", [])}
        if any(word and re.search(rf"\b{re.escape(word)}\b", text, re.I) for word in words):
            reasons.append("blocked word")
        if len(message.mentions) > int(cfg.get("mention_limit", 5)):
            reasons.append("mention spam")
        if "discord.gg/" in text.lower() and cfg.get("block_invites", True):
            reasons.append("invite link")
        if len(text) > int(cfg.get("max_message_length", 4000)):
            reasons.append("message too long")

        key = (message.guild.id, message.author.id)
        now = time.monotonic()
        history = [stamp for stamp in self.last[key] if now - stamp < 8]
        history.append(now)
        self.last[key] = history
        if len(history) >= int(cfg.get("message_burst", 8)):
            reasons.append("flood")

        if not reasons:
            return

        try:
            await message.delete(reason="AstraCore AutoMod: " + ", ".join(reasons))
        except discord.HTTPException:
            return

        if cfg.get("warn_on_action", True):
            try:
                await message.channel.send(
                    f'⚠️ {message.author.mention}, your message was removed by AutoMod: {", ".join(reasons)}.',
                    delete_after=5,
                )
            except discord.HTTPException:
                return

    # ------------------------------------------------------------------
    # Native Discord AutoMod helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _block_action() -> discord.AutoModRuleAction:
        # In discord.py 2.x the default AutoModRuleAction is block-message.
        return discord.AutoModRuleAction(discord.AutoModRuleActionType.block_message)

    @staticmethod
    def _normalise_keywords(raw: str) -> list[str]:
        values: list[str] = []
        for value in raw.split(","):
            value = value.strip()
            if value and value not in values:
                values.append(value)
        return values

    @staticmethod
    async def _fetch_rules(guild: discord.Guild) -> list[discord.AutoModRule]:
        try:
            return await guild.fetch_automod_rules()
        except discord.NotFound:
            return []

    async def _create_keyword_rule(
        self,
        guild: discord.Guild,
        name: str,
        keywords: Iterable[str],
    ) -> discord.AutoModRule:
        terms = list(keywords)
        if not terms:
            raise ValueError("At least one keyword is required.")
        if len(terms) > 1000:
            raise ValueError("A Discord keyword rule can contain at most 1000 terms.")
        too_long = [term for term in terms if len(term) > 60]
        if too_long:
            raise ValueError("Each keyword must be 60 characters or fewer.")

        return await guild.create_automod_rule(
            name=name[:100],
            event_type=discord.AutoModRuleEventType.message_send,
            trigger=discord.AutoModTrigger(keyword_filter=terms),
            actions=[self._block_action()],
            enabled=True,
            reason="AstraCore native AutoMod setup",
        )

    async def _rule_exists(self, guild: discord.Guild, name: str) -> bool:
        rules = await self._fetch_rules(guild)
        return any(rule.name == name for rule in rules)

    async def _ensure_baseline(self, guild: discord.Guild) -> tuple[list[str], list[str], list[str], int]:
        """Create only missing, useful native rules in one guild.

        This never deletes or duplicates rules. Discord remains the authority on
        per-server limits; unsupported/forbidden creations are reported as failed.
        """
        created: list[str] = []
        skipped: list[str] = []
        failed: list[str] = []

        for name, terms in self.SETUP_RULES:
            if await self._rule_exists(guild, name):
                skipped.append(name)
                continue
            try:
                await self._create_keyword_rule(guild, name, terms)
                created.append(name)
            except (discord.Forbidden, discord.HTTPException, ValueError):
                failed.append(name)

        specs = (
            ("AstraCore • Spam Content", "spam"),
            ("AstraCore • Mention Spam", "mention"),
            ("AstraCore • Harmful Links", "harmful_link"),
        )
        for name, kind in specs:
            if await self._rule_exists(guild, name):
                skipped.append(name)
                continue
            try:
                if kind == "spam":
                    trigger = discord.AutoModTrigger(type=discord.AutoModRuleTriggerType.spam)
                elif kind == "mention":
                    trigger = discord.AutoModTrigger(mention_limit=10)
                else:
                    trigger = discord.AutoModTrigger(type=discord.AutoModRuleTriggerType.harmful_link)
                await guild.create_automod_rule(
                    name=name,
                    event_type=discord.AutoModRuleEventType.message_send,
                    trigger=trigger,
                    actions=[self._block_action()],
                    enabled=True,
                    reason="AstraCore native AutoMod baseline",
                )
                created.append(name)
            except (discord.Forbidden, discord.HTTPException):
                failed.append(name)

        rules = await self._fetch_rules(guild)
        return created, skipped, failed, len(rules)

    # ------------------------------------------------------------------
    # Admin commands
    # ------------------------------------------------------------------
    @app_commands.command(name="automod-keyword", description="Create a native Discord AutoMod keyword rule.")
    @app_commands.describe(name="Rule name", keywords="Comma-separated keywords or phrases")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def automod_keyword(self, interaction: discord.Interaction, name: str, keywords: str) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            terms = self._normalise_keywords(keywords)
            rule = await self._create_keyword_rule(interaction.guild, name, terms)  # type: ignore[arg-type]
            await interaction.followup.send(
                f"✅ Native AutoMod rule created: **{rule.name}**\nID: `{rule.id}`",
                ephemeral=True,
            )
        except (ValueError, discord.Forbidden, discord.HTTPException) as exc:
            await interaction.followup.send(f"❌ Could not create the rule: `{exc}`", ephemeral=True)

    @app_commands.command(name="automod-mention-spam", description="Create a native Discord AutoMod mention-spam rule.")
    @app_commands.describe(limit="Maximum combined user/role mentions, from 1 to 50")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def automod_mention_spam(self, interaction: discord.Interaction, limit: app_commands.Range[int, 1, 50]) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            rule = await interaction.guild.create_automod_rule(  # type: ignore[union-attr]
                name="AstraCore • Mention Spam",
                event_type=discord.AutoModRuleEventType.message_send,
                trigger=discord.AutoModTrigger(mention_limit=int(limit)),
                actions=[self._block_action()],
                enabled=True,
                reason="AstraCore native AutoMod mention spam protection",
            )
            await interaction.followup.send(f"✅ Mention-spam rule created. ID: `{rule.id}`", ephemeral=True)
        except (discord.Forbidden, discord.HTTPException) as exc:
            await interaction.followup.send(f"❌ Could not create the rule: `{exc}`", ephemeral=True)

    @app_commands.command(name="automod-spam", description="Create the native Discord spam-content AutoMod rule.")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def automod_spam(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            rule = await interaction.guild.create_automod_rule(  # type: ignore[union-attr]
                name="AstraCore • Spam Content",
                event_type=discord.AutoModRuleEventType.message_send,
                trigger=discord.AutoModTrigger(type=discord.AutoModRuleTriggerType.spam),
                actions=[self._block_action()],
                enabled=True,
                reason="AstraCore native Discord spam protection",
            )
            await interaction.followup.send(f"✅ Spam-content rule created. ID: `{rule.id}`", ephemeral=True)
        except (discord.Forbidden, discord.HTTPException) as exc:
            await interaction.followup.send(f"❌ Could not create the rule: `{exc}`", ephemeral=True)

    @app_commands.command(name="automod-harmful-links", description="Create Discord's native harmful-link AutoMod rule.")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def automod_harmful_links(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            rule = await interaction.guild.create_automod_rule(  # type: ignore[union-attr]
                name="AstraCore • Harmful Links",
                event_type=discord.AutoModRuleEventType.message_send,
                trigger=discord.AutoModTrigger(type=discord.AutoModRuleTriggerType.harmful_link),
                actions=[self._block_action()],
                enabled=True,
                reason="AstraCore native Discord harmful-link protection",
            )
            await interaction.followup.send(f"✅ Harmful-link rule created. ID: `{rule.id}`", ephemeral=True)
        except (discord.Forbidden, discord.HTTPException) as exc:
            await interaction.followup.send(f"❌ Could not create the rule: `{exc}`", ephemeral=True)

    @app_commands.command(name="automod-setup", description="Install AstraCore's useful native AutoMod baseline for this server.")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def automod_setup(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        guild = interaction.guild
        assert guild is not None
        try:
            created, skipped, failed, total = await self._ensure_baseline(guild)
            lines = [f"**Native AutoMod rules in this server:** `{total}`"]
            if created:
                lines.append(f"✅ Created: `{len(created)}`")
            if skipped:
                lines.append(f"↪️ Already existed: `{len(skipped)}`")
            if failed:
                lines.append(f"⚠️ Failed: `{len(failed)}` — Discord may be enforcing a server rule limit or the bot may lack permission.")
            await interaction.followup.send("\n".join(lines), ephemeral=True)
        except (discord.Forbidden, discord.HTTPException) as exc:
            await interaction.followup.send(f"❌ AutoMod setup failed: `{exc}`", ephemeral=True)

    @app_commands.command(name="automod-maximize", description="Maximize useful native AutoMod protection in this server without duplicates.")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def automod_maximize(self, interaction: discord.Interaction) -> None:
        """Provision every useful native rule AstraCore can create in this server."""
        await interaction.response.defer(ephemeral=True, thinking=True)
        guild = interaction.guild
        assert guild is not None
        try:
            created, skipped, failed, total = await self._ensure_baseline(guild)
            await interaction.followup.send(
                "🛡️ **AstraCore AutoMod Maximized**\n"
                f"Native rules now: **{total}**\n"
                f"✅ Created: `{len(created)}` • ↪️ Existing: `{len(skipped)}` • ⚠️ Failed: `{len(failed)}`\n\n"
                "AstraCore only creates useful missing rules; it never deletes or duplicates existing rules.",
                ephemeral=True,
            )
        except (discord.Forbidden, discord.HTTPException) as exc:
            await interaction.followup.send(f"❌ Could not maximize AutoMod: `{exc}`", ephemeral=True)

    @app_commands.command(name="automod-maximize-owned", description="Maximize AutoMod in servers you own where AstraCore is installed.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def automod_maximize_owned(self, interaction: discord.Interaction) -> None:
        """Safely apply the baseline only to servers owned by the invoking user."""
        await interaction.response.defer(ephemeral=True, thinking=True)
        user_id = interaction.user.id
        results: list[str] = []
        total_before = 0
        total_after = 0
        for guild in self.bot.guilds:
            if guild.owner_id != user_id:
                continue
            try:
                before = len(await self._fetch_rules(guild))
                created, _skipped, failed, after = await self._ensure_baseline(guild)
                total_before += before
                total_after += after
                results.append(f"• **{guild.name}**: `{before} → {after}` rules; created `{len(created)}`, failed `{len(failed)}`")
            except (discord.Forbidden, discord.HTTPException):
                results.append(f"• **{guild.name}**: skipped (Discord permission/API limit)")
        if not results:
            results.append("• No servers owned by you were found with AstraCore installed.")
        await interaction.followup.send(
            "🛡️ **AstraCore AutoMod — Owned Servers**\n"
            f"Total visible rules: `{total_before} → {total_after}`\n" + "\n".join(results),
            ephemeral=True,
        )

    @app_commands.command(name="automod-list", description="List native Discord AutoMod rules in this server.")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def automod_list(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            rules = await self._fetch_rules(interaction.guild)  # type: ignore[arg-type]
            if not rules:
                return await interaction.followup.send("No native AutoMod rules found.", ephemeral=True)
            embed = discord.Embed(title="🛡️ AstraCore Native AutoMod", description=f"Rules: `{len(rules)}`")
            for rule in rules[:25]:
                embed.add_field(name=rule.name, value=f"ID: `{rule.id}` • {'Enabled' if rule.enabled else 'Disabled'}", inline=False)
            await interaction.followup.send(embed=embed, ephemeral=True)
        except (discord.Forbidden, discord.HTTPException) as exc:
            await interaction.followup.send(f"❌ Could not fetch AutoMod rules: `{exc}`", ephemeral=True)

    @app_commands.command(name="automod-delete", description="Delete a native Discord AutoMod rule by ID.")
    @app_commands.describe(rule_id="The AutoMod rule ID")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def automod_delete(self, interaction: discord.Interaction, rule_id: str) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            rule_id_int = int(rule_id)
            rules = await self._fetch_rules(interaction.guild)  # type: ignore[arg-type]
            rule = next((item for item in rules if item.id == rule_id_int), None)
            if rule is None:
                return await interaction.followup.send("❌ AutoMod rule not found in this server.", ephemeral=True)
            await rule.delete(reason="AstraCore native AutoMod rule deletion")
            await interaction.followup.send(f"✅ Deleted **{rule.name}** (`{rule.id}`).", ephemeral=True)
        except (ValueError, discord.Forbidden, discord.HTTPException) as exc:
            await interaction.followup.send(f"❌ Could not delete the rule: `{exc}`", ephemeral=True)

    @app_commands.command(name="automod-progress", description="Show AstraCore's native AutoMod rule count across accessible servers.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def automod_progress(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        total = 0
        checked = 0
        failed = 0
        for guild in self.bot.guilds:
            try:
                total += len(await self._fetch_rules(guild))
                checked += 1
            except (discord.Forbidden, discord.HTTPException):
                failed += 1
        await interaction.followup.send(
            "🛡️ **AstraCore AutoMod Progress**\n"
            f"Native rules visible to AstraCore: **{total}/100**\n"
            f"Servers checked: `{checked}` • Failed: `{failed}`\n\n"
            "Discord's AutoMod badge is controlled by Discord; reaching the documented threshold does not provide a manual claim button.",
            ephemeral=True,
        )

    @commands.Cog.listener()
    async def on_automod_action(self, execution: discord.AutoModAction) -> None:
        # Keep this lightweight: Discord sends this event for every AutoMod execution.
        if execution.guild_id:
            self.bot.dispatch("astracore_automod_action", execution)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AutoMod(bot))
