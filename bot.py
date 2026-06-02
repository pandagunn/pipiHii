import os
import discord
from discord.ext import commands
import requests
from typing import Dict, Optional
import re

# Intents
intents = discord.Intents.default()
intents.message_content = True

# Bot setup
bot = commands.Bot(command_prefix="!", intents=intents)

# Store active translation channels
active_translations: Dict[int, Dict] = {}

# ==================== TRANSLATOR MODULE ====================

# Slur censoring list
SLURS = [
    'fuck', 'fucking', 'fucked', 'fucks', 'f***',
    'shit', 'shitty', 'damn', 'dammit',
    'asshole', 'bastard', 'bitch', 'bitches',
    'crap', 'pissed', 'piss', 'ass', 'arse'
]

# Slang dictionary for different languages
SLANG_DICTIONARY = {
    # Chinese slang
    'zh': {
        '哈': 'haha',
        '呃': 'uh',
        '嗯': 'um',
        '滚': 'get lost',
        '牛逼': 'awesome',
        '傻逼': 'idiot',
        '给力': 'awesome',
        '很HIGH': 'excited',
        '不爽': 'upset'
    },
    # Brazilian Portuguese slang
    'pt': {
        'mano': 'man',
        'cara': 'dude',
        'véio': 'old man',
        'véia': 'old woman',
        'beleza': 'ok',
        'blz': 'ok',
        'tmj': 'together',
        'bolado': 'angry',
        'maconha': 'marijuana',
        'virado': 'turned on',
        'zoado': 'messed up'
    },
    # Vietnamese slang
    'vi': {
        'dạo này': 'lately',
        'tình hình': 'situation',
        'bọn': 'group/gang',
        'gái gú': 'pretty girl',
        'bạn bè': 'friends',
        'ngang ngược': 'stubborn',
        'vô duyên': 'tactless',
        'khó tính': 'picky'
    },
    # German slang
    'de': {
        'Kerl': 'guy',
        'Mädel': 'girl',
        'Alter': 'dude',
        'dufte': 'cool',
        'blöd': 'stupid',
        'nervig': 'annoying',
        'kacke': 'crap',
        'verdammt': 'damn',
        'super': 'great'
    }
}

def detect_language(text: str) -> str:
    """Detect language from text based on character patterns"""
    # Chinese detection
    if re.search(r'[\u4E00-\u9FA5]', text):
        return 'zh'
    
    # Vietnamese detection
    if re.search(r'[\u0102\u0103\u0110\u0111\u0128\u0129\u0168\u0169\u01A0\u01A1]', text):
        return 'vi'
    
    # Portuguese detection
    if re.search(r'[àáâãäåèéêëìíîïòóôõöùúûü]', text):
        return 'pt'
    
    # German detection
    if re.search(r'[äöüß]', text):
        return 'de'
    
    return 'en'

def censor_slurs(text: str) -> str:
    """Replace slurs with asterisks"""
    censored = text
    for slur in SLURS:
        pattern = r'\b' + re.escape(slur) + r'\b'
        censored = re.sub(pattern, '***', censored, flags=re.IGNORECASE)
    return censored

def translate_slang(text: str, language: str) -> str:
    """Replace slang with formal versions"""
    translated = text
    slang_map = SLANG_DICTIONARY.get(language, {})
    
    for slang, formal in slang_map.items():
        pattern = r'\b' + re.escape(slang) + r'\b'
        translated = re.sub(pattern, formal, translated, flags=re.IGNORECASE)
    
    return translated

def simple_translate(text: str, source_lang: str, target_lang: str = 'en') -> str:
    """Translate using free MyMemory API"""
    try:
        url = f'https://api.mymemory.translated.net/get'
        params = {
            'q': text,
            'langpair': f'{source_lang}|{target_lang}'
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('responseStatus') == 200:
                return data.get('responseData', {}).get('translatedText', text)
    except Exception as e:
        print(f'Translation error: {e}')
    
    return text

async def translate_message(text: str, target_language: str = 'en') -> str:
    """Main translation function"""
    try:
        # Detect source language
        source_language = detect_language(text)
        
        # If already English, just censor slurs
        if source_language == 'en':
            return censor_slurs(text)
        
        # Translate to target language
        translated_text = simple_translate(text, source_language, target_language)
        
        # Apply slang translation
        translated_text = translate_slang(translated_text, source_language)
        
        # Censor slurs
        translated_text = censor_slurs(translated_text)
        
        return translated_text
    except Exception as e:
        print(f'Translation process error: {e}')
        return text

# ==================== BOT EVENTS ====================

@bot.event
async def on_ready():
    """Called when bot is ready"""
    print(f'✅ Bot logged in as {bot.user}')
    print(f'🤖 Discord Translation Bot Ready!')
    print(f'Use /startT to enable translation')
    print(f'Use /stopT to disable translation')
    await bot.tree.sync()
    print(f'✓ Synced slash commands')

@bot.event
async def on_message(message):
    """Handle incoming messages"""
    # Ignore bot's own messages
    if message.author == bot.user:
        return
    
    # Check if translation is enabled for this channel
    channel_id = message.channel.id
    
    if channel_id in active_translations:
        translation_config = active_translations[channel_id]
        
        if translation_config.get('enabled'):
            try:
                # Translate the message
                translated_text = await translate_message(message.content)
                
                # Only send if translation is different
                if translated_text != message.content:
                    embed = discord.Embed(
                        title="🔄 Translation",
                        description=translated_text,
                        color=discord.Color.blue()
                    )
                    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar)
                    embed.set_footer(text="Automatic Translation | Use /stopT to disable")
                    
                    # Send as reply
                    await message.reply(embed=embed, mention_author=False)
            except Exception as e:
                print(f'Error translating message: {e}')
    
    # Process commands
    await bot.process_commands(message)

# ==================== SLASH COMMANDS ====================

@bot.tree.command(name="startT", description="Start automatic translation of messages to English")
async def start_translation(interaction: discord.Interaction):
    """Enable translation for the channel"""
    channel_id = interaction.channel_id
    user_id = interaction.user.id
    
    # Enable translation for this channel
    active_translations[channel_id] = {
        'enabled': True,
        'user_id': user_id,
        'started_at': discord.utils.utcnow()
    }
    
    embed = discord.Embed(
        title="🌍 Automatic Translation Enabled",
        description=(
            "All messages in this channel will now be automatically translated to English and checked for inappropriate content.\n\n"
            "**Supported Languages:**\n"
            "🇨🇳 Chinese\n"
            "🇧🇷 Portuguese (Brazil)\n"
            "🇻🇳 Vietnamese\n"
            "🇩🇪 German\n\n"
            "Use `/stopT` to disable translation."
        ),
        color=discord.Color.green()
    )
    embed.set_footer(text="Translation started")
    
    await interaction.response.send_message(embed=embed)
    print(f'✅ Translation enabled in channel {channel_id}')

@bot.tree.command(name="stopT", description="Stop automatic translation of messages")
async def stop_translation(interaction: discord.Interaction):
    """Disable translation for the channel"""
    channel_id = interaction.channel_id
    
    # Disable translation for this channel
    if channel_id in active_translations:
        del active_translations[channel_id]
    
    embed = discord.Embed(
        title="🛑 Automatic Translation Disabled",
        description=(
            "Translation has been turned off for this channel.\n\n"
            "Use `/startT` to enable it again."
        ),
        color=discord.Color.red()
    )
    embed.set_footer(text="Translation stopped")
    
    await interaction.response.send_message(embed=embed)
    print(f'❌ Translation disabled in channel {channel_id}')

@bot.tree.command(name="translate", description="Manually translate text to English")
@discord.app_commands.describe(text="Text to translate")
async def manual_translate(interaction: discord.Interaction, text: str):
    """Manually translate a message"""
    await interaction.response.defer()
    
    try:
        translated = await translate_message(text)
        
        embed = discord.Embed(
            title="🔄 Manual Translation",
            color=discord.Color.blue()
        )
        embed.add_field(name="Original", value=text[:1024], inline=False)
        embed.add_field(name="Translated", value=translated[:1024], inline=False)
        embed.set_footer(text="Translation by Discord Bot")
        
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"❌ Translation error: {str(e)}")

@bot.tree.command(name="status", description="Check bot status and active translations")
async def status(interaction: discord.Interaction):
    """Check bot status"""
    active_count = len(active_translations)
    
    embed = discord.Embed(
        title="🤖 Bot Status",
        color=discord.Color.blurple()
    )
    embed.add_field(name="Bot Name", value=bot.user.name, inline=True)
    embed.add_field(name="Status", value="🟢 Online", inline=True)
    embed.add_field(name="Active Translation Channels", value=str(active_count), inline=False)
    
    if active_count > 0:
        channel_list = ", ".join([f"<#{cid}>" for cid in active_translations.keys()])
        embed.add_field(name="Channels", value=channel_list, inline=False)
    
    embed.add_field(name="Supported Languages", value="🇨🇳 Chinese\n🇧🇷 Portuguese\n🇻🇳 Vietnamese\n🇩🇪 German", inline=False)
    embed.set_footer(text=f"Total guilds: {len(bot.guilds)}")
    
    await interaction.response.send_message(embed=embed)

# ==================== MAIN ====================

def main():
    """Start the bot"""
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        print("❌ Error: DISCORD_TOKEN not found in .env file")
        print("Please create a .env file with your bot token:")
        print("DISCORD_TOKEN=your_token_here")
        return
    
    bot.run(token)

if __name__ == "__main__":
    main()
