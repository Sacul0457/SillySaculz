import discord
from discord import app_commands
import asyncio
import aiohttp
from discord.ext import commands
from typing import Literal
from discordapidocs import DiscordAPiDocs

LANGUAGES = {
    'af': 'Afrikaans',
    'sq': 'Albanian',
    'am': 'Amharic',
    'ar': 'Arabic',
    'hy': 'Armenian',
    'az': 'Azerbaijani',
    'eu': 'Basque',
    'be': 'Belarusian',
    'bn': 'Bengali',
    'bs': 'Bosnian',
    'bg': 'Bulgarian',
    'ca': 'Catalan',
    'ceb': 'Cebuano',
    'ny': 'Chichewa',
    'zh-cn': 'Chinese (Simplified)',
    'zh-tw': 'Chinese (Traditional)',
    'co': 'Corsican',
    'hr': 'Croatian',
    'cs': 'Czech',
    'da': 'Danish',
    'nl': 'Dutch',
    'en': 'English',
    'eo': 'Esperanto',
    'et': 'Estonian',
    'tl': 'Filipino',
    'fi': 'Finnish',
    'fr': 'French',
    'fy': 'Frisian',
    'gl': 'Galician',
    'ka': 'Georgian',
    'de': 'German',
    'el': 'Greek',
    'gu': 'Gujarati',
    'ht': 'Haitian Creole',
    'ha': 'Hausa',
    'haw': 'Hawaiian',
    'iw': 'Hebrew',
    'he': 'Hebrew',
    'hi': 'Hindi',
    'hmn': 'Hmong',
    'hu': 'Hungarian',
    'is': 'Icelandic',
    'ig': 'Igbo',
    'id': 'Indonesian',
    'ga': 'Irish',
    'it': 'Italian',
    'ja': 'Japanese',
    'jw': 'Javanese',
    'kn': 'Kannada',
    'kk': 'Kazakh',
    'km': 'Khmer',
    'ko': 'Korean',
    'ku': 'Kurdish (Kurmanji)',
    'ky': 'Kyrgyz',
    'lo': 'Lao',
    'la': 'Latin',
    'lv': 'Latvian',
    'lt': 'Lithuanian',
    'lb': 'Luxembourgish',
    'mk': 'Macedonian',
    'mg': 'Malagasy',
    'ms': 'Malay',
    'ml': 'Malayalam',
    'mt': 'Maltese',
    'mi': 'Maori',
    'mr': 'Marathi',
    'mn': 'Mongolian',
    'my': 'Myanmar (Burmese)',
    'ne': 'Nepali',
    'no': 'Norwegian',
    'or': 'Odia',
    'ps': 'Pashto',
    'fa': 'Persian',
    'pl': 'Polish',
    'pt': 'Portuguese',
    'pa': 'Punjabi',
    'ro': 'Romanian',
    'ru': 'Russian',
    'sm': 'Samoan',
    'gd': 'Scots Gaelic',
    'sr': 'Serbian',
    'st': 'Sesotho',
    'sn': 'Shona',
    'sd': 'Sindhi',
    'si': 'Sinhala',
    'sk': 'Slovak',
    'sl': 'Slovenian',
    'so': 'Somali',
    'es': 'Spanish',
    'su': 'Sundanese',
    'sw': 'Swahili',
    'sv': 'Swedish',
    'tg': 'Tajik',
    'ta': 'Tamil',
    'te': 'Telugu',
    'th': 'Thai',
    'tr': 'Turkish',
    'uk': 'Ukrainian',
    'ur': 'Urdu',
    'ug': 'Uyghur',
    'uz': 'Uzbek',
    'vi': 'Vietnamese',
    'cy': 'Welsh',
    'xh': 'Xhosa',
    'yi': 'Yiddish',
    'yo': 'Yoruba',
    'zu': 'Zulu',
}


class SendView(discord.ui.View):
    def __init__(self, embed : discord.Embed, message  : discord.Message = None):
        super().__init__(timeout=None)
        self.embed = embed
        self.message = message 
    @discord.ui.button(label="Send", style=discord.ButtonStyle.green, custom_id="send_not_ephemeral")
    async def sendcallback(self, interaction:discord.Interaction, button:discord.ui.Button) -> None:
        await interaction.response.send_message(embed=self.embed)

class TranslateCog(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot =bot
        self.ctx_menu = app_commands.ContextMenu(
            name="Translate",
            callback=self.translate
        )
        self.bot.tree.add_command(self.ctx_menu)

    @app_commands.command(name="define", description="Get the meaning of a word")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.describe(word="The word to get the definition of")
    async def define(self, interaction: discord.Interaction, word: str) -> None:
        await interaction.response.defer(ephemeral=True)
        async with aiohttp.ClientSession() as session:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            async with session.get(url) as response:
                data = await response.json()
        adj_definition = None
        noun_example = None
        adj_example = None
        adj_definition = None
        verb_example = None
        verb_definition = None
        noun_definition = None
        pronounce = "Unknown"
        try:
            first_dict : dict[list, dict] = data[0]
            phonetics = first_dict.get("phonetics", [])
            text_dict = phonetics[0]
            pronounce = text_dict.get("text", "Unknown")
            meanings_list : list = first_dict.get("meanings", [])
            noun_definition = meanings_list[0].get("definitions", [])[0].get("definition", "Unknown")
            noun_example = meanings_list[0].get("definitions", [])[0].get("example", "Unknown")
            verb_definition = meanings_list[1].get("definitions", [])[0].get("definition", "Unknown")
            verb_example = meanings_list[1].get("definitions", [])[0].get("example", "Unknown")
            adj_definition = meanings_list[2].get("definitions", [])[0].get("definition", "Unknown")
            adj_example = meanings_list[2].get("definitions", [])[0].get("example", "Unknown")
        except IndexError:
            pass
        except KeyError as e:
            await interaction.followup.send(e, ephemeral=True)
            return
        except Exception as e:
            await interaction.followup.send(e, ephemeral=True)
            return
        embed = discord.Embed(title=f"Meaning of `{word}` ({pronounce})")
        if noun_definition:
            embed.add_field(name="Noun",
                            value=f"- {noun_definition}\n- E.g: {noun_example}")
        if verb_definition:
            embed.add_field(name="Verb",
                            value=f"- {verb_definition}\n- E.g: {verb_example}",
                            inline=False)
        if adj_definition:
            embed.add_field(name="Adjective",
                            value=f"- {adj_definition}\n- E.g: {adj_example}",
                            inline=False)   
        embed.set_footer(text=f"Requested by @{interaction.user}",
                        icon_url=interaction.user.display_avatar.url)
        view= SendView(embed)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def translate(self, interaction:discord.Interaction, message:discord.Message) -> str:
        # This was discovered by the people here:
        # https://github.com/ssut/py-googletrans/issues/268
        await interaction.response.defer(ephemeral=True)
        query = {
            'dj': '1',
            'dt': ['sp', 't', 'ld', 'bd'],
            'client': 'dict-chrome-ex',
            # Source Language
            'sl': 'auto',
            # Target Language
            'tl': "en",
            # Query
            'q': message.content,
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get('https://clients5.google.com/translate_a/single', params=query, headers=headers) as resp:
                if resp.status != 200:
                    html = await resp.text()
                    await interaction.followup.send(f"An error occurred!", ephemeral=True)
                    print(html)
                    return

                data = await resp.json()
        src = data.get('src', 'Unknown')
        sentences = data.get('sentences', [])
        if len(sentences) == 0:
            await interaction.followup.send(f"No translation found!", ephemeral=True)
            return

        #original = ''.join(sentence.get('orig', '') for sentence in sentences)
        translated = ''.join(sentence.get('trans', '') for sentence in sentences)
        embed = discord.Embed(title=f"Translated from `{src}` to English:",
                            description=f">>> {translated}",
                            color=discord.Color.blurple(),
                            timestamp=discord.utils.utcnow())
        embed.set_author(name=f"Message by @{message.author}", icon_url=message.author.display_avatar.url)
        embed.set_footer(text=f"Used by @{interaction.user}", icon_url=interaction.user.display_avatar.url)
        view = SendView(embed, message)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="docs", description="Search up discord docs")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.describe(field="Events, Resource or Components")
    async def docs(self, interaction:discord.Interaction, field:Literal["Events", "Resources", "Components"]) -> None :
        await interaction.response.send_message(view=DocsView(field), ephemeral=True)


async def setup(bot:commands.Bot):
    await bot.add_cog(TranslateCog(bot))

class SelectDocs(discord.ui.Select):
    def __init__(self, field: Literal["Events", "Resources", "Components"]):
        if field == "Events":
            options = [discord.SelectOption(label="overview"),
                    discord.SelectOption(label="gateway"),
                    discord.SelectOption(label="gateway-events"),
                    discord.SelectOption(label="webhook-events"),
                    ]
        elif field == "Resources":
        
            options = [discord.SelectOption(label="application-role-connection-metadata"),
                    discord.SelectOption(label="application"),
                    discord.SelectOption(label="audit-log"),
                    discord.SelectOption(label="auto-moderation"),
                    discord.SelectOption(label="channel"),
                    discord.SelectOption(label="emoji"),
                    discord.SelectOption(label="guild-scheduled-event"),
                    discord.SelectOption(label="guild-template"),
                    discord.SelectOption(label="guild"),
                    discord.SelectOption(label="invite"),
                    discord.SelectOption(label="lobby"),
                    discord.SelectOption(label="message"),
                    discord.SelectOption(label="poll"),
                    discord.SelectOption(label="sku"),
                    discord.SelectOption(label="stage-instance"),
                    discord.SelectOption(label="sticker"),
                    discord.SelectOption(label="user"),
                    discord.SelectOption(label="voice"),
                    discord.SelectOption(label="webhook"),
                    ]
        else:
            options = [discord.SelectOption(label="using-message-components"),
                    discord.SelectOption(label="using-modal-components"),
                    discord.SelectOption(label="reference"),
        ]

        super().__init__(custom_id="SelectEvents", min_values=1, max_values=1, options=options, placeholder=f"Choose options for {field}...")
        self.field = field
    async def callback(self, interaction:discord.Interaction):
        module = self.values[0]
        url = DiscordAPiDocs._construct_url(self.field.lower(), module).url
        embed = discord.Embed(title=f"",
                              description=f"- Showing results for [`{self.field}/{module}`]({url})")
        embed.set_author(name=f"Requested by @{interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, view=ManualSearchView(self.field, module))


class DocsView(discord.ui.View):
    def __init__(self, field: Literal["Events", "Resources", "Components"]):
        super().__init__(timeout=None)
        self.add_item(SelectDocs(field))

class ManualSearchView(discord.ui.View):
    def __init__(self, field: Literal["Events", "Resources", "Components"], module:str):
        super().__init__(timeout=None)
        self.field = field
        self.module = module

    @discord.ui.button(label="Manual Search", custom_id="manual search")
    async def callback(self, interaction:discord.Interaction, button:discord.ui.Button):
        await interaction.response.send_modal(ManualSearchModal(self.field, self.module))

    async def interaction_check(self, interaction:discord.Interaction) -> bool:
        return interaction.user.id == 802167689011134474

class ManualSearchModal(discord.ui.Modal):
    def __init__(self, field: Literal["Events", "Resources", "Components"], module:str):
        super().__init__(title="Manual Search", timeout=None, custom_id="manual_search_modal")
        self.input = discord.ui.TextInput(label="Query", required=True, style=discord.TextStyle.short)
        self.add_item(self.input)
        self.field = field
        self.module = module
    async def on_submit(self, interaction:discord.Interaction):
        query = self.input.value
        url = DiscordAPiDocs._construct_url_with_query(self.field.lower(), self.module, query).url
        embed = discord.Embed(title=f"",
                              description=f"- Showing results for [`{self.field}/{self.module}#{query}`]({url})")
        embed.set_author(name=f"Requested by @{interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)
