import discord
from discord import app_commands
from discord.ext import tasks, commands
import os
from datetime import datetime, timedelta, timezone
import datetime
import asyncio
import aiohttp
import typing
from invitesv2 import Invitesv2

uptime = 0

cog = 'qol'
class TaskBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.none()
        intents.guild_messages= True
        intents.guilds = True
        super().__init__(command_prefix=commands.when_mentioned, help_command=None, intents=intents)
    async def setup_hook(self):
        asyncio.get_event_loop().set_debug(True)
        global uptime
        uptime = discord.utils.utcnow().timestamp()
        await self.load_exention(cog)

    async def fetch_invitev2(self, invite_code: str) -> Invitesv2:
        if invite_code.startswith(f"https://discord.gg"):
            invite_code = invite_code.split("/")[3]
        elif invite_code.startswith(f"https://discord.com/invite"):
            invite_code = invite_code.split("/")[4]
        URL = f"https://discord.com/api/v10/invites/{invite_code}?with_permissions=True&?with_counts=True"
        async with aiohttp.ClientSession() as session:
            async with session.get(URL) as res:
                if res.status == 429:
                    raise discord.RateLimited(res, "WE ARE BEING RATELIMITED")
                elif res.status == 404:
                    raise discord.NotFound(res, f"No such invite '{invite_code}'")
                return Invitesv2(await res.json())

bot = TaskBot()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound): 
        return
    elif isinstance(error, commands.MissingPermissions):
        return
    elif isinstance(error, commands.MemberNotFound):
        return await ctx.send(f"The member is no longer in the server or there is no such member.")
    elif isinstance(error, commands.UserNotFound):
        return await ctx.send(f"The user id is invalid.")
    elif isinstance(error, commands.RoleNotFound):
        return await ctx.send("There is no such role.")
    elif isinstance(error, commands.MissingRequiredArgument):
        return await ctx.send(f"Invalid input.")
    elif isinstance(error, commands.CommandOnCooldown):
        pass
    elif isinstance(error, commands.BotMissingPermissions):
        return await ctx.send("I do not have the permission to use this command.")

    else:
        return await ctx.send(error)

@bot.event
async def on_event_error(error):
    print(error)



@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        return
    elif isinstance(error, app_commands.CommandNotFound):
        return
    elif isinstance(error, commands.MemberNotFound):
        return await interaction.response.send_message(f"The member is no longer in the server or there is no such member.")
    elif isinstance(error, commands.UserNotFound):
        return await interaction.response.send_message(f"The user id in invalid.")
    elif isinstance(error, discord.app_commands.CommandOnCooldown):
        await interaction.response.send_message(error, ephemeral=True)
        pass

    elif isinstance(error, discord.app_commands.errors.TransformerError):
        await interaction.response.send_message(f"The member is no longer in the server.", ephemeral=True)
    elif isinstance(error, discord.app_commands.BotMissingPermissions):
        await interaction.response.send_message(f"I do not have the permission to use this command.", ephemeral=True)
    else:
        print(error)

@bot.command()
async def sync(ctx):
    await bot.tree.sync()

class Fetch_Group(app_commands.Group):
    def __init__(self):
        super().__init__(name="fetch", description="Fetch a member or user info")

    @app_commands.command(name="member", description="Fetch a member's information")
    @app_commands.describe(member="The member to fetch")
    async def fetch_member(self, interaction:discord.Interaction, member:discord.Member):
        await interaction.response.defer()
        embed = discord.Embed(title="",
                            description=f"- User: {member.mention}\n- ID: `{member.id}`")
        permissions = member.resolved_permissions
        nickname = member.nick or "No Nickname"
        joined_at = member.joined_at
        if member.guild_avatar:
            guild_avatar = member.guild_avatar.url
        else:
            guild_avatar = member.display_avatar.url
        if member.premium_since:
            premium_since = member.premium_since
        else:
            premium_since = None
        if member.flags.did_rejoin:
            did_rejoin = True
        else:
            did_rejoin = False
        quarantined_username = member.flags.automod_quarantined_username
        quarantined_guild_tag = member.flags.automod_quarantined_guild_tag

        embed.add_field(name="Member Data",
                    value=f">>> - Joined on: <t:{int(joined_at.timestamp())}:f>\
                        \n- Muted: {f'✅ (Expires on <t:{int(member.timed_out_until.timestamp())}:f>)' if member.is_timed_out() else f"❌ {f"(Previously muted until <t:{int(member.timed_out_until.timestamp())}:f>)" if not member.is_timed_out() and member.timed_out_until else ""}"}\
                        \n- Nickname: `{nickname}`\n- Rejoined: {'✅' if did_rejoin else '❌'}\
                        \n- Quarantined: {f'✅ ({f"guild_tag and username" if quarantined_guild_tag and quarantined_username else 'guild_tag' if quarantined_guild_tag else 'username'})' if quarantined_username or quarantined_guild_tag else '❌'}\
                        \n- {f"Booster: ✅ (since <t:{int(premium_since.timestamp())}:f>)" if premium_since else 'Booster: ❌'}")
        embed.set_author(name=f"@{member}", icon_url=guild_avatar)
        embed.set_thumbnail(url=guild_avatar)
        await interaction.followup.send(embed=embed, view=PermissionView(permissions))
        
    @app_commands.command(name="user", description="Fetch a users's information")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.describe(user="The user to fetch")
    async def fetch_user(self, interaction:discord.Interaction, user:discord.User):
        await interaction.response.defer()
        member = await bot.fetch_user(int(user.id))
        badges = []
        if member.public_flags.staff:
            badges.append("Staff")
        if member.public_flags.partner:
            badges.append("Partner")
        if member.public_flags.hypesquad:
            badges.append("Hypesquad Event Member")
        if member.public_flags.bug_hunter:
            badges.append("Bug Hunter Lvl 1")
        if member.public_flags.bug_hunter_level_2:
            badges.append("Bug Hunter Lvl 2")
        if member.public_flags.hypesquad_bravery:
            badges.append("Bravery")
        if member.public_flags.hypesquad_brilliance:
            badges.append("Brilliance")
        if member.public_flags.hypesquad_balance:
            badges.append("Balance")
        if member.public_flags.early_supporter:
            badges.append("Early Supporter")
        if member.public_flags.verified_bot:
            badges.append("Verified Bot")
        if member.public_flags.bot_http_interactions:
            badges.append("HTTP Interactions Bot")
        if member.public_flags.active_developer:
            badges.append("Active Dev")
        if member.public_flags.early_verified_bot_developer:
            badges.append("Early Verified Dev")
        if member.public_flags.discord_certified_moderator:
            badges.append("Mod")
        if member.public_flags.team_user:
            badges.append("Team User")
        if member.public_flags.system:
            badges.append("Discord's Official System")  
        if member.public_flags.spammer:
            spammer = "Marked as Likely Spammer by Discord"
        else:
            spammer = "Good"
        badges_final = "\n- ".join(badges)
        embed= discord.Embed(title=f"{"Bot" if member.bot else "User"} Info", description=f">>> {member.mention} ({member.id})\
                            \n**Joined Discord:** <t:{int(member.created_at.timestamp())}:R> \n**Account Status:** {spammer}\
                            ",
                            color = member.accent_color if member.banner is None else discord.Color.blurple())
        embed.add_field(name="Badges:", value=f">>> - {badges_final}" if badges_final != "" else ">>> None")
        embed.set_image(url=member.banner if member.banner is not None else None)
        embed.set_thumbnail(url=member.avatar_decoration if member.avatar_decoration is not None else member.display_avatar.url)
        embed.set_author(name=f"@{member}", icon_url=member.display_avatar)
        embed.set_footer(text=f"Sent by @{interaction.user}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = datetime.datetime.now()
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="channels", description="Fetch channes in a server")
    async def fetch_channels(self, interaction:discord.Interaction):
        await interaction.response.send_message(view=SelectViews("channel"), ephemeral=True)

    @app_commands.command(name="roles", description="Fetch roles in a server")
    async def fetch_roles(self, interaction:discord.Interaction):
        await interaction.response.send_message(view=SelectViews("role"), ephemeral=True)

class SelectViews(discord.ui.View):
    def __init__(self, select_type: typing.Literal["channel", "role"]):
        super().__init__(timeout=None)
        if select_type == "channel":
            self.add_item(ChannelSelect())
        else:
            self.add_item(RoleSelect())


class RoleSelect(discord.ui.RoleSelect):
    def __init__(self):
        super().__init__(custom_id="RoleSelect")
    async def callback(self, interaction:discord.Interaction):
        role = self.values[0]
        embed = discord.Embed(title="Role Information",
                              description=f"- Name: {role}\n- ID: `{role.id}`",
                              color=role.color)
        embed.add_field(name="Role Data",
                        value=f">>> - Created on: <t:{int(role.created_at.timestamp())}:f>\n- Hoisted: {'✅' if role.hoist else '❌'}\
                            \n- Managed: {f"✅ {'(Bot Managed)' if role.is_bot_managed() else ''}" if role.managed else '❌'}\
                            \n- Mentionable: {'✅' if role.mentionable else '❌'}\n- Position: `{role.position}`")
        if role.display_icon:
            embed.set_thumbnail(url=role.display_icon.url)
            embed.set_author(name=f"@{role.name}", icon_url=role.display_icon.url)
        await interaction.response.send_message(embed=embed, view=PermissionView(role.permissions))

class ChannelSelect(discord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(custom_id="ChannelSelect")
    async def callback(self, interaction:discord.Interaction):
        channel = self.values[0]
        if isinstance(channel, app_commands.AppCommandChannel):
            embed = discord.Embed(title="Channel Information",
                                  description=f"- Channel: {channel.mention}\n- ID: `{channel.id}`\n> Topic: {channel.topic}"
                                  )
            embed.add_field(name="Channel Data",
                            value=f">>> - Guild ID: `{channel.guild_id}`\n- Created on: <t:{int(channel.created_at.timestamp())}:f>\
                                \n- Type: `{channel.type}`\n- Category ID: `{channel.category_id}`\
                                 \n- Last Message ID: [`{channel.last_message_id}`]({bot.get_partial_messageable(channel.id).get_partial_message(channel.last_message_id).jump_url})\
                                 \n- Slowmode: `{channel.slowmode_delay}s`\
                                 \n- Require tag: {'✅' if channel.flags.require_tag else '❌'}\
                                 \n- Nsfw: {'✅' if channel.is_nsfw() else '❌'}\
                                 \n- Position: `{channel.position}`")
        else:
            thread= channel
            embed = discord.Embed(title="Thread Information",
                                  description=f"- Thread: {thread.mention}\n- ID: `{thread.id}`")
            embed.add_field(name="Thread Data",
                            value=f">>> - Channel: <#{thread.parent_id}>\n - Created on: <t:{int(thread.created_at.timestamp())}:f>\
                                \n- Type: `{thread.type}`\n- Guild ID: `{thread.guild_id}`\n- Invitable: {'✅' if thread.invitable else '❌'}\
                                \n- [`{thread.last_message_id}`]({bot.get_partial_messageable(thread.id).get_partial_message(thread.last_message_id).jump_url})\
                                \n- Slowmode: `{thread.slowmode_delay}s`\\n- Message count: `{thread.message_count}`\
                                \n- Total Message Sent: `{thread.total_message_sent}`\n- Member count: `{thread.member_count}`\
                                \n- Pinned: {'✅' if thread.flags.pinned else '❌'}\n- Owner: <@{thread.owner_id}> ({thread.owner_id})\
                                \n")
            
        await interaction.response.send_message(embed=embed)


bot.tree.add_command(Fetch_Group())

def format_permissions(permission_list) -> list[str]:
    value_dict = {
        False : "❌",
        True : "✅"
    }
    if permission_list is None:
        return None
    return [f"- {perm}: {value_dict.get(value)}" for perm, value in permission_list]

class PermissionView(discord.ui.View):
    def __init__(self, perms):
        super().__init__(timeout=None)
        self.perms = perms
    @discord.ui.button(label="Permissions")
    async def callback(self, interaction:discord.Interaction, button:discord.ui.Button):
        permissions = format_permissions(self.perms)
        await interaction.response.send_message(f"```{"\n".join(perm for perm in permissions)}```", ephemeral=True)



@bot.tree.context_menu(name="Fetch User")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.allowed_installs(guilds=True, users=True)
async def fetch_user_context_menu(interaction:discord.Interaction, user:discord.User):
    await interaction.response.defer()
    member = await bot.fetch_user(int(user.id))
    badges = []
    if member.public_flags.staff:
        badges.append("Staff")
    if member.public_flags.partner:
        badges.append("Partner")
    if member.public_flags.hypesquad:
        badges.append("Hypesquad Event Member")
    if member.public_flags.bug_hunter:
        badges.append("Bug Hunter Lvl 1")
    if member.public_flags.bug_hunter_level_2:
        badges.append("Bug Hunter Lvl 2")
    if member.public_flags.hypesquad_bravery:
        badges.append("Bravery")
    if member.public_flags.hypesquad_brilliance:
        badges.append("Brilliance")
    if member.public_flags.hypesquad_balance:
        badges.append("Balance")
    if member.public_flags.early_supporter:
        badges.append("Early Supporter")
    if member.public_flags.verified_bot:
        badges.append("Verified Bot")
    if member.public_flags.bot_http_interactions:
        badges.append("HTTP Interactions Bot")
    if member.public_flags.active_developer:
        badges.append("Active Dev")
    if member.public_flags.early_verified_bot_developer:
        badges.append("Early Verified Dev")
    if member.public_flags.discord_certified_moderator:
        badges.append("Mod")
    if member.public_flags.team_user:
        badges.append("Team User")
    if member.public_flags.system:
        badges.append("Discord's Official System")  
    if member.public_flags.spammer:
        spammer = "Marked as Likely Spammer by Discord"
    else:
        spammer = "Good"
    badges_final = "\n- ".join(badges)
    embed= discord.Embed(title=f"{"Bot" if member.bot else "User"} Info", description=f">>> {member.mention} ({member.id})\
                         \n**Joined Discord:** <t:{int(member.created_at.timestamp())}:R> \n**Account Status:** {spammer}\
                        ",
                        color = member.accent_color if member.banner is None else discord.Color.blurple())
    embed.add_field(name="Badges:", value=f">>> - {badges_final}" if badges_final != "" else ">>> None")
    embed.set_image(url=member.banner if member.banner is not None else None)
    embed.set_thumbnail(url=member.avatar_decoration if member.avatar_decoration is not None else member.display_avatar.url)
    embed.set_author(name=f"@{member}", icon_url=member.display_avatar)
    embed.set_footer(text=f"Sent by @{interaction.user}", icon_url=interaction.user.display_avatar.url)
    embed.timestamp = datetime.datetime.now()
    await interaction.followup.send(embed=embed)


@bot.tree.context_menu(name="Fetch Member")
async def fetch_member_context_menu(interaction:discord.Interaction, member:discord.Member):
    await interaction.response.defer()
    embed = discord.Embed(title="",
                        description=f"- User: {member.mention}\n- ID: `{member.id}`")
    permissions = member.resolved_permissions
    nickname = member.nick or "No Nickname"
    joined_at = member.joined_at
    if member.guild_avatar:
        guild_avatar = member.guild_avatar.url
    else:
        guild_avatar = member.display_avatar.url
    if member.premium_since:
        premium_since = member.premium_since
    else:
        premium_since = None
    if member.flags.did_rejoin:
        did_rejoin = True
    else:
        did_rejoin = False
    quarantined_username = member.flags.automod_quarantined_username
    quarantined_guild_tag = member.flags.automod_quarantined_guild_tag
    embed.add_field(name="Member Data",
                value=f">>> - Joined on: <t:{int(joined_at.timestamp())}:f>\
                    \n- Muted: {f'✅ (Expires on <t:{int(member.timed_out_until.timestamp())}:f>)' if member.is_timed_out() else f"❌ {f"(Previously muted until <t:{int(member.timed_out_until.timestamp())}:f>)" if not member.is_timed_out() and member.timed_out_until else ""}"}\
                    \n- Nickname: `{nickname}`\n- Rejoined: {'✅' if did_rejoin else '❌'}\
                    \n- Quarantined: {f'✅ ({f"guild_tag and username" if quarantined_guild_tag and quarantined_username else 'guild_tag' if quarantined_guild_tag else 'username'})' if quarantined_username or quarantined_guild_tag else '❌'}\
                    \n- {f"Booster: ✅ (since <t:{int(premium_since.timestamp())}:f>)" if premium_since else 'Booster: ❌'}")
    embed.set_author(name=f"@{member}", icon_url=guild_avatar)
    embed.set_thumbnail(url=guild_avatar)

    await interaction.followup.send(embed=embed, view=PermissionView(permissions))

class GuildFeatureButton(discord.ui.Button):
    def __init__(self, guild_features):
        super().__init__(style=discord.ButtonStyle.secondary, label="View")
        self.guild_features = "\n- ".join(guild_features)
    async def callback(self, interaction:discord.Interaction):
        await interaction.response.send_message(f"- {self.guild_features}", ephemeral=True)

class WithInviteContainer(discord.ui.Container):
    def __init__(self, channel_id: int, channel_type: discord.ChannelType, channel_name: str, member_count: int, online_count: int, tag: str, badge_icon: str, primary_colour: str, 
                 secondary_colour: str, guild_id: int, guild_name: str, description: str, verify_level: int, url_code: str, nsfw_level: int, nsfw: bool, boosts: int, tier: int, features: list[str], icon: str, banner: str):
        super().__init__()
        
        thumbnail_text = (f"Name: {guild_name}\nID: `{guild_id}`\nMembers: {member_count} | {online_count} online\
                          \nChannel: [`#{channel_name}`]({bot.get_partial_messageable(channel_id, guild_id=guild_id).jump_url}) ({channel_id})")
        tag_text = (f"Tag: `{tag}`\nPrimary colour: {primary_colour}\nSeconadary colour: {secondary_colour}")
        second_text = (f"NSFW: {nsfw} | Level {nsfw_level}\nVerification Level: {verify_level}\nBoosts: `{boosts}` | Tier {tier}\nInvite Code: `{url_code}`")
        self.add_item(discord.ui.Section(accessory=discord.ui.Thumbnail(media=icon)).add_item(thumbnail_text))
        self.add_item(discord.ui.Separator())
        if tag:
            self.add_item(discord.ui.Section(tag_text, accessory=discord.ui.Thumbnail(badge_icon)))
            self.add_item(discord.ui.Separator())
        self.add_item(discord.ui.TextDisplay(second_text))
        self.add_item(discord.ui.TextDisplay(f">>> {description}"))
        self.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.small))
        self.add_item(discord.ui.Section(accessory=GuildFeatureButton(features)).add_item(f"**Guild Features [{len(features)}]**"))
        self.add_item(discord.ui.MediaGallery(*[discord.MediaGalleryItem(media=banner)]))

class WithInviteView(discord.ui.LayoutView):
    def __init__(self, channel_id: int, channel_type, channel_name, member_count, online_count, tag, badge_icon, primary_colour, secondary_colour, guild_id, guild_name, description, verify_level, url_code, nsfw_level, nsfw, boosts, tier, features, icon, banner):
        super().__init__(timeout=None)
        self.add_item(WithInviteContainer(channel_id, channel_type, channel_name, member_count, online_count, tag, badge_icon, primary_colour, secondary_colour, guild_id, guild_name, description, verify_level, url_code, nsfw_level, nsfw, boosts, tier, features, icon, banner))


class NoInviteContainer(discord.ui.Container):
    def __init__(self, guild_id: int, guild_features: list[str], locale: str, nsfw_level: int):
        super().__init__()
        text = (f"Guild ID: `{guild_id}`\nCreated_at: {discord.utils.format_dt(discord.utils.snowflake_time(guild_id), 't')}\
                \nLocale: {locale}\nNSFW level: `{nsfw_level}`")
        self.add_item(discord.ui.TextDisplay(text))
        self.add_item(discord.ui.Section(f"Guild Features [{len(guild_features)}]", accessory=GuildFeatureButton(guild_features)) )

class NoInviteView(discord.ui.LayoutView):
    def __init__(self, guild_id: int, guild_features: list[str], locale: str, nsfw_level: int):
        super().__init__(timeout=None)
        self.add_item(NoInviteContainer(guild_id, guild_features, locale, nsfw_level))
                 
@bot.tree.command(name="sinfo", description=f"Get information about a server!")
@app_commands.describe(invite_code = "The invite code of the server")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.allowed_installs(guilds=True, users=True)
async def sinfo(interaction:discord.Interaction, invite_code: str | None = None) -> str:
    await interaction.response.defer()
    if invite_code is None:
        guild_id = interaction.guild_id
        locale = interaction.guild.preferred_locale
        guild_features = interaction.guild.features
        nsfw_level = interaction.guild.nsfw_level.name
        await interaction.followup.send(view=NoInviteView(guild_id, guild_features, locale, nsfw_level))
    else:
        try:
            invite = await bot.fetch_invitev2(invite_code)                                                                   
        except discord.NotFound as e:
            return await interaction.followup.send("Invalid invite!", ephemeral=True)
        channel_id = invite.channel.id
        channel_type = invite.channel.type
        channel_name = invite.channel.name
        member_count = invite.profile.member_count
        online_count = invite.profile.online_count
        tag = invite.profile.tag
        badge_icon = invite.profile.badge_icon.url if invite.profile.badge_icon else ""
        primary_colour = invite.profile.badge_colour_primary
        secondary_colour = invite.profile.badge_color_secondary
        id = invite.guild.id
        guild_name = invite.guild.name
        description = invite.guild.description
        verify_level = invite.guild.verification_level
        vanity_url_code = invite.guild.vanity_url_code
        nsfw_level = invite.guild.nsfw_level
        nsfw = invite.guild.is_nsfw()
        boosts = invite.guild.premium_subscription_count
        tier = invite.guild.premium_tier
        list_features = [f"{feature} **__(Exclusive)__**" if "_TEST" in feature  else feature for feature in invite.guild.features]
        icon = invite.guild.icon.url
        banner = invite.guild.banner.url if invite.guild.banner else ""
        await interaction.followup.send(view=WithInviteView(channel_id, channel_type, channel_name, member_count, online_count, tag, badge_icon, primary_colour, secondary_colour, 
                                                            id, guild_name, description, verify_level, vanity_url_code, nsfw_level, nsfw, boosts, tier, list_features, icon, banner))



@bot.tree.command(description="Get the server created_at using server id")
@app_commands.describe(guild_id="The server ID")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.allowed_installs(guilds=True, users=True)
async def id(interaction:discord.Interaction, guild_id : str):
    if guild_id is None:
        guild_id = interaction.guild.id
    discord_epoch = 1420070400000
    timestamp = (int(guild_id) >> 22) + discord_epoch
    embed = discord.Embed(title="Guild Timestamp", description=f">>> **ID:** {guild_id}\n**Created at:** <t:{int(timestamp / 1000)}:f> | `{int(timestamp / 1000)}`",
                          color=discord.Color.blurple())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ping", description="Get the bot's ping and stats")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.allowed_installs(guilds=True, users=True)
async def ping(interaction:discord.Interaction) -> None:
    global uptime
    embed = discord.Embed(title="",
                          description=f">>> - **Ping:** `{bot.latency * 1000:.2f}ms`\
                            \n- **Online since:** <t:{int(uptime)}:R>")
    embed.set_author(name=f"@{bot.user.name}'s Bot Stats", icon_url=bot.user.display_avatar.url)
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

bot.run('YOUR_TOKEN')
