from __future__ import annotations

from typing import TYPE_CHECKING, Self
from discord import Color
if TYPE_CHECKING:
    from discord.invite import InvitePayload, InviteType, InviteGuildPayload
    from discord.types.guild import GuildFeature, VerificationLevel, NSFWLevel
    from discord.abc import Snowflake
    from discord.types.channel import ChannelType

class Invitesv2():
    def __init__(self, data: InvitePayload):
        self.type : InviteType = data['type']
        self.invite_code :str = data['code']
        self._flags : int = data.get('flags')
        self.guild_id : Snowflake = data['guild_id']
        self._is_nickname_changeable : bool = data['is_nickname_changeable']
        self.guild : PartialInviteGuildv2 = PartialInviteGuildv2(data['guild'], self._is_nickname_changeable)
        self.channel : PartialInviteChannelv2 = PartialInviteChannelv2(data['channel'])
        self.profile : InviteProfileV2 = InviteProfileV2(data['profile'])
class PartialInviteGuildv2():
    def __init__(self, data: InviteGuildPayload, _is_nickname_changeable:bool):
        self._is_nickname_changeable : bool = _is_nickname_changeable
        self.id : int = data['id']
        self.name : str = data['name']
        self._splash : str = data['splash']
        self._banner : str = data['banner']
        self.description : str | None = data.get('description')
        self._icon : str = data['icon']
        self.features : list[GuildFeature] = data['features']
        self.verification_level : VerificationLevel = data['verification_level']
        self.vanity_url_code : str = data['vanity_url_code']
        self.nsfw : bool = data['nsfw']  
        self.nsfw_level : NSFWLevel = data['nsfw_level']
        self.premium_subscription_count : int = data['premium_subscription_count']
        self.premium_tier : int = data['premium_tier']

    @property
    def splash(self) -> CustomAsset | None:
        if self._splash is None:
            return None
        return CustomAsset._from_guild_spash(self.id, self._splash)
    
    @property
    def icon(self) -> CustomAsset | None:
        if self._icon is None:
            return None
        return CustomAsset._from_guild_icon(self.id, self._icon)
    
    @property
    def banner(self) -> CustomAsset | None:
        if self._banner is None:
             return None
        return CustomAsset._from_guild_banner(self.id, self._banner)
    
    def is_nickname_changeable(self) -> bool:
        return self._is_nickname_changeable
    
    def is_nsfw(self) -> bool:
        return self.nsfw
    
 
    
class PartialInviteChannelv2():
    def __init__(self, data: InvitePayload):
        self.id : Snowflake = data['id']
        self.type : ChannelType = data['type']
        self.name : str = data['name']

class InviteProfileV2():
    def __init__(self, data: PartialInviteGuildv2):
        self.id : Snowflake = data['id']
        self.name : str = data['name']
        self._icon_hash : str = data['icon_hash']
        self.member_count : int = data['member_count']
        self.online_count : int = data['online_count']
        self.description : str | None = data['description']
        self.tag : str | None = data['tag']
        self.badge : int | None = data['badge']
        self._badge_hash : str | None = data['badge_hash']
        self._badge_color_primary : str | None = data['badge_color_primary']
        self._badge_color_secondary : str | None = data['badge_color_secondary']
        self.visibility : int = data['visibility']
        self._custom_banner_hash : str | None = data.get('custom_banner_hash')
        self.premium_subscription_count : int = data.get('premium_subscription_count')
        self.premium_tier : int = data.get('premium_tier')

    @property
    def icon(self) -> CustomAsset | None:
        if self._icon_hash is None:
            return None
        return CustomAsset._from_guild_icon(self.id, self._icon_hash)
    
    @property
    def badge_icon(self) -> CustomAsset:
        if self._badge_hash is None:
            return None
        return CustomAsset._from_primary_guild(self.id, self._badge_hash)
    
    @property
    def badge_colour_primary(self) -> Color:
        if self._badge_color_primary is None:
            return Color.default()
        return Color.from_str(self._badge_color_primary)

    @property
    def badge_color_secondary(self) -> Color:
        if self._badge_color_secondary is None:
            return Color.default()
        return Color.from_str(self._badge_color_secondary)
    
    @property
    def banner(self) -> CustomAsset:
        if self._custom_banner_hash is None:
            return None
        return CustomAsset._from_guild_banner(self.id, self._custom_banner_hash)
        

class CustomAsset():
    BASE = "https://cdn.discordapp.com"
    def __init__(self,*, url:str):
        self._url : str = url

    @classmethod
    def _from_splash(cls, guild_id : int, hash: str) -> Self:
        return cls(
            url=f"{cls.BASE}/splashes/{guild_id}/{hash}.png"
        )
    
    @classmethod
    def _from_guild_spash(cls, guild_id: int, splash: str) -> Self:
        return cls(
            url=f'{cls.BASE}/splashes/{guild_id}/{splash}.png?size=1024'
        )

    @classmethod
    def _from_guild_icon(cls, guild_id: int, icon_hash: str) -> Self:
        animated = icon_hash.startswith('a_')
        format = 'gif' if animated else 'png'
        return cls(
            url=f'{cls.BASE}/icons/{guild_id}/{icon_hash}.{format}?size=1024'
        )
    
    @classmethod
    def _from_guild_banner(cls, guild_id: int, icon_hash: str) -> Self:
        animated = icon_hash.startswith('a_')
        format = 'gif' if animated else 'png'
        return cls(
            url=f'{cls.BASE}/banners/{guild_id}/{icon_hash}.{format}?size=1024'
        )

    @classmethod
    def _from_primary_guild(cls, guild_id: int, icon_hash: str) -> Self:
        return cls(
            url=f'{cls.BASE}/guild-tag-badges/{guild_id}/{icon_hash}.png?size=64',
        )


    @property
    def url(self) -> str:
        return self._url
