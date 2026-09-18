import re
import time
from collections import defaultdict

import discord
from discord import app_commands
from discord.ext import commands

from services.config_service import get


class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last = defaultdict(list)

    # -------------------------
    # Existing custom AutoMod
    # -------------------------
    @commands.Cog.listener()
    async def on_message(self, m):
        if m.author.bot or not m.guild:
            return

        c = await get(m.guild.id)
        cfg = c.get("automod", {})

        if not cfg.get("enabled", False):
            return

        if any(
            r.id in cfg.get("exempt_role_ids", [])
            for r in getattr(m.author, "roles", [])
        ):
            return

        reasons = []
        txt = m.content

        words = {x.lower() for x in cfg.get("bad_words", [])}

        if any(
            w and re.search(rf"\b{re.escape(w)}\b", txt, re.I)
            for w in words
        ):
            reasons.append("blocked word")

        if len(m.mentions) > int(cfg.get("mention_limit", 5)):
            reasons.append("mention spam")

        if "discord.gg/" in txt.lower() and cfg.get("block_invites", True):
            reasons.append("invite link")

        if len(txt) > int(cfg.get("max_message_length", 4000)):
            reasons.append("message too long")

        key = (m.guild.id, m.author.id)
        now = time.monotonic()
        hist = [t for t in self.last[key] if now - t < 8]
        hist.append(now)
        self.last[key] = hist

        if len(hist) >= int(cfg.get("message_burst", 8)):
            reasons.append("flood")

        if reasons:
            try:
                await m.delete(
                    reason="AstraCore AutoMod: " + ", ".join(reasons)
                )
            except discord.HTTPException:
                return

            if cfg.get("warn_on_action", True):
                try:
                    await m.channel.send(
                        f'⚠️ {m.author.mention}, your message was removed by '
                        f'AutoMod: {", ".join(reasons)}.',
                        delete_after=5,
                    )
                except discord.HTTPException:
                    return

    # -------------------------
    # Discord Native AutoMod
    # -------------------------
    @app_commands.command(
        name="automod-keyword",
        description="Create a native Discord AutoMod keyword rule."
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def automod_keyword(self, interaction: discord.Interaction, keyword: str):
        if not interaction.guild:
            return await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True,
            )

        keyword = keyword.strip()

        if not keyword or len(keyword) > 60:
            return await interaction.response.send_message(
                "❌ Keyword must contain 1-60 characters.",
                ephemeral=True,
            )

        await interaction.response.defer(ephemeral=True)

        try:
            rule = await interaction.guild.create_automod_rule(
                name=f"AstraCore • {keyword[:45]}",
                event_type=discord.AutoModRuleEventType.message_send,
                trigger=discord.AutoModTrigger(
                    keyword_filter=[keyword]
                ),
                actions=[
                    discord.AutoModRuleAction(discord.AutoModRuleActionType.block_message)
                ],
                enabled=True,
                reason=f"AstraCore native AutoMod by {interaction.user}",
            )

            await interaction.followup.send(
                f"✅ Native AutoMod keyword rule created.\n"
                f"**Rule:** `{rule.name}`\n"
                f"**ID:** `{rule.id}`",
                ephemeral=True,
            )

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ Discord denied this action. AstraCore needs **Manage Server**.",
                ephemeral=True,
            )
        except discord.HTTPException as e:
            await interaction.followup.send(
                f"❌ Discord API error: `{e}`",
                ephemeral=True,
            )

    @app_commands.command(
        name="automod-mention-spam",
        description="Create a native Discord AutoMod mention-spam rule."
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def automod_mention_spam(
        self,
        interaction: discord.Interaction,
        limit: app_commands.Range[int, 2, 50] = 5,
    ):
        if not interaction.guild:
            return await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True,
            )

        await interaction.response.defer(ephemeral=True)

        try:
            rule = await interaction.guild.create_automod_rule(
                name="AstraCore • Mention Spam",
                event_type=discord.AutoModRuleEventType.message_send,
                trigger=discord.AutoModTrigger(
                    mention_spam_limit=int(limit)
                ),
                actions=[
                    discord.AutoModRuleAction(discord.AutoModRuleActionType.block_message)
                ],
                enabled=True,
                reason=f"AstraCore native AutoMod by {interaction.user}",
            )

            await interaction.followup.send(
                f"✅ Native mention-spam rule created.\n"
                f"**Limit:** `{limit}` mentions\n"
                f"**Rule ID:** `{rule.id}`",
                ephemeral=True,
            )

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ Discord denied this action. AstraCore needs **Manage Server**.",
                ephemeral=True,
            )
        except discord.HTTPException as e:
            await interaction.followup.send(
                f"❌ Discord API error: `{e}`",
                ephemeral=True,
            )

    @app_commands.command(
        name="automod-list",
        description="List native Discord AutoMod rules."
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def automod_list(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True,
            )

        try:
            rules = await interaction.guild.fetch_automod_rules()

            if not rules:
                return await interaction.response.send_message(
                    "🛡️ No native Discord AutoMod rules found.",
                    ephemeral=True,
                )

            lines = []

            for rule in rules[:20]:
                status = "🟢 Enabled" if rule.enabled else "🔴 Disabled"
                lines.append(
                    f"**{rule.name}**\n"
                    f"`{rule.id}` • {status}"
                )

            embed = discord.Embed(
                title="🛡️ AstraCore Native AutoMod",
                description="\n\n".join(lines),
                color=discord.Color.red(),
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True,
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Discord denied access to AutoMod rules.",
                ephemeral=True,
            )
        except discord.HTTPException as e:
            await interaction.response.send_message(
                f"❌ Discord API error: `{e}`",
                ephemeral=True,
            )

    @app_commands.command(
        name="automod-delete",
        description="Delete a native Discord AutoMod rule."
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def automod_delete(
        self,
        interaction: discord.Interaction,
        rule_id: str,
    ):
        if not interaction.guild:
            return await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True,
            )

        try:
            rule_id_int = int(rule_id)
        except ValueError:
            return await interaction.response.send_message(
                "❌ Invalid AutoMod rule ID.",
                ephemeral=True,
            )

        try:
            rule = await interaction.guild.fetch_automod_rule(rule_id_int)

            await interaction.guild.delete_automod_rule(
                rule.id,
                reason=f"AstraCore native AutoMod deletion by {interaction.user}",
            )

            await interaction.response.send_message(
                f"✅ Deleted native AutoMod rule `{rule.name}`.",
                ephemeral=True,
            )

        except discord.NotFound:
            await interaction.response.send_message(
                "❌ AutoMod rule not found.",
                ephemeral=True,
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Discord denied this action. AstraCore needs **Manage Server**.",
                ephemeral=True,
            )
        except discord.HTTPException as e:
            await interaction.response.send_message(
                f"❌ Discord API error: `{e}`",
                ephemeral=True,
            )

    # -------------------------
    # Native AutoMod execution
    # -------------------------
    @commands.Cog.listener()
    async def on_automod_action(self, execution: discord.AutoModAction):
        guild = self.bot.get_guild(execution.guild_id)

        if guild is None:
            return

        channel = None

        if execution.channel_id:
            channel = guild.get_channel(execution.channel_id)

        if channel is None:
            return

        try:
            embed = discord.Embed(
                title="🛡️ Native AutoMod Action",
                description=(
                    "Discord AutoMod blocked an automated moderation event."
                ),
                color=discord.Color.red(),
            )
            embed.add_field(
                name="Rule ID",
                value=f"`{execution.rule_id}`",
                inline=True,
            )
            embed.add_field(
                name="Action",
                value=f"`{execution.action.type.name}`",
                inline=True,
            )

            await channel.send(embed=embed, delete_after=10)

        except discord.HTTPException:
            return


async def setup(bot):
    await bot.add_cog(AutoMod(bot))
