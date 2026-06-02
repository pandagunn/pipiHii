# Discord Automatic Translation Bot 🌍 (Python)

A powerful Python Discord bot that automatically translates messages to English and censors inappropriate content. Supports Chinese, Brazilian Portuguese, Vietnamese, German, and more languages.

## Features

✨ **Automatic Language Translation**
- Detects and translates from multiple languages to English
- Supports: Chinese, Portuguese (Brazil), Vietnamese, German, and more
- Uses free translation APIs for fast processing
- Real-time translation on message receive

🛡️ **Content Moderation**
- Automatically censors slurs and inappropriate language
- Replaces offensive words with asterisks (****)
- Detects both English and non-English slurs
- Inline censoring

🌐 **Slang Translation**
- Translates colloquial expressions and slang
- Converts informal language to standard English equivalents
- Maintains message meaning and context
- Language-specific slang dictionaries

⚡ **Easy to Use**
- Simple slash commands: `/startT` and `/stopT`
- Start translation with `/startT` in any channel
- Stop translation with `/stopT`
- Per-channel translation control
- Manual translation with `/translate`
- Status monitoring with `/status`

## Prerequisites

- Python 3.9 or higher
- Discord Bot Token
- Discord Server (where you have permissions to add bot)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/pandagunn/pipiHii.git
cd pipiHii
```

### 2. Create Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to "Bot" section and click "Add Bot"
4. Copy the bot token
5. Go to "OAuth2" → "URL Generator"
6. Select scopes: `bot`
7. Select permissions:
   - Send Messages
   - Read Messages/View Channels
   - Read Message History
   - Create Public Threads
   - Send Messages in Threads
8. Copy the generated URL and invite bot to your server

### 5. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your bot token:
```
DISCORD_TOKEN=your_bot_token_here
```

### 6. Run the Bot

```bash
python bot.py
```

You should see:
```
✅ Bot logged in as YourBotName#0000
🤖 Discord Translation Bot Ready!
Use /startT to enable translation
Use /stopT to disable translation
✓ Synced slash commands
```

## Usage

### Commands

#### `/startT` - Enable Translation

Enables automatic translation in the current channel.

```
/startT
```

**Response:**
```
🌍 Automatic Translation Enabled
All messages in this channel will now be automatically translated to English and checked for inappropriate content.

Supported Languages:
🇨🇳 Chinese
🇧🇷 Portuguese (Brazil)
🇻🇳 Vietnamese
🇩🇪 German

Use /stopT to disable translation.
```

**What happens:**
- All non-English messages are automatically translated to English
- Slurs and offensive language are censored
- Slang is converted to formal English
- Bot replies to each message with a translation embed

#### `/stopT` - Disable Translation

Disables automatic translation in the current channel.

```
/stopT
```

**Response:**
```
🛑 Automatic Translation Disabled
Translation has been turned off for this channel.

Use /startT to enable it again.
```

#### `/translate <text>` - Manual Translation

Manually translate any text to English.

```
/translate ¡Hola como estás!
```

**Response:**
```
🔄 Manual Translation
Original: ¡Hola como estás!
Translated: Hello how are you!
```

#### `/status` - Check Bot Status

View bot status and active translation channels.

```
/status
```

**Response shows:**
- Bot name and online status
- Number of active translation channels
- List of channels with translation enabled
- Supported languages
- Total servers bot is in

## How It Works

```
Original Message (Any Language)
    ↓
Language Detection (Regex based)
    ↓
Slang Dictionary Translation
    ↓
Full Text Translation (MyMemory API)
    ↓
Slur & Offensive Content Censoring
    ↓
Reply with Translation Embed
```

### Supported Languages

| Language | Code | Detection Method |
|----------|------|-----------------|
| 🇨🇳 Chinese | `zh` | CJK Characters `[\u4E00-\u9FA5]` |
| 🇧🇷 Portuguese (Brazil) | `pt` | Accented characters `[àáâãäå...]` |
| 🇻🇳 Vietnamese | `vi` | Vietnamese diacritics `[\u0102\u0103...]` |
| 🇩🇪 German | `de` | German characters `[äöüß]` |
| 🇬🇧 English | `en` | Default/No special chars |

## Architecture

```
pipiHii/
├── bot.py              # Main bot application (370+ lines)
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create manually)
├── .env.example       # Configuration template
└── README_PYTHON.md   # This file
```

## File Details

### `bot.py` - Main Bot Application

**Language Detection Module:**
```python
def detect_language(text: str) -> str
    # Detects Chinese, Portuguese, Vietnamese, German
    # Returns language code: 'zh', 'pt', 'vi', 'de', 'en'
```

**Censoring Module:**
```python
def censor_slurs(text: str) -> str
    # Replaces offensive words with '***'
    # Case-insensitive with word boundaries
```

**Slang Translation Module:**
```python
def translate_slang(text: str, language: str) -> str
    # Converts regional slang to formal English
    # Language-specific dictionaries
```

**Main Translation Function:**
```python
async def translate_message(text: str, target_language: str = 'en') -> str
    # Orchestrates all translation steps
    # 1. Detect language
    # 2. Translate slang
    # 3. Translate full text
    # 4. Censor slurs
    # 5. Return cleaned translation
```

**Discord Events:**
- `on_ready()` - Bot startup initialization
- `on_message()` - Processes incoming messages

**Slash Commands:**
- `startT` - Enable channel translation
- `stopT` - Disable channel translation
- `translate` - Manual text translation
- `status` - View bot status

## Customization

### Add Custom Slang

Edit the `SLANG_DICTIONARY` in `bot.py`:

```python
SLANG_DICTIONARY = {
    'pt': {
        'seu_slang': 'formal translation',
        'outro_slang': 'another translation',
        # Add more entries
    },
    'your_language_code': {
        'slang1': 'formal1',
        'slang2': 'formal2',
    }
}
```

### Add Slur Words

Modify the `SLURS` list in `bot.py`:

```python
SLURS = [
    'offensive_word1',
    'offensive_word2',
    'offensive_word3',
    # Add more slurs to censor
]
```

### Add New Language

1. Add language code to `SLANG_DICTIONARY`:
```python
'es': {  # Spanish
    'hola': 'hello',
    'adiós': 'goodbye',
}
```

2. Update `detect_language()` function:
```python
def detect_language(text: str) -> str:
    # Spanish detection
    if re.search(r'[¿¡]', text):
        return 'es'
    # ... rest of function
```

3. Test with `/translate ¡Hola!`

## API Integration

### MyMemory Translated API (Current)

**Free, no authentication required:**
```
https://api.mymemory.translated.net/get?q=text&langpair=source|target
```

**Features:**
- 100+ languages supported
- ~200 requests/day per IP
- Response time: ~500ms
- No API key needed
- Open source

**Usage:**
```python
params = {
    'q': 'Hello world',
    'langpair': 'en|es'  # English to Spanish
}
response = requests.get('https://api.mymemory.translated.net/get', params=params)
```

### Alternative APIs

**Google Translate:**
```bash
pip install google-trans-new
```

**DeepL API (Premium):**
```bash
pip install deepl
```

**LibreTranslate:**
```bash
pip install libretranslatepy
```

## Troubleshooting

### Bot doesn't respond to commands

```
❌ Problem: Commands not appearing
✅ Solution:
   1. Ensure bot has "Use Slash Commands" permission
   2. Restart bot: python bot.py
   3. Restart Discord client
   4. Wait up to 1 hour for command sync
   5. Check DISCORD_TOKEN in .env is correct
```

### Translation not working

```
❌ Problem: Messages not translating
✅ Solution:
   1. Check internet connection
   2. Use /status to verify bot is online
   3. Try /translate command manually
   4. Check MyMemory API: curl "https://api.mymemory.translated.net/get?q=hello&langpair=en|es"
   5. Check message isn't too long (>500 chars)
```

### "DISCORD_TOKEN not found" error

```
❌ Problem: Bot won't start
✅ Solution:
   1. Create .env file: cp .env.example .env
   2. Add your bot token: DISCORD_TOKEN=your_token_here
   3. Save the file
   4. Restart bot: python bot.py
```

### Rate limiting (API errors)

```
❌ Problem: Too many requests to translation API
✅ Solution:
   1. Space out translation requests
   2. Use paid API (DeepL, Google Translate)
   3. Implement message caching
   4. Add request queue/delay system
```

### Bot offline/disconnected

```
❌ Problem: Bot keeps disconnecting
✅ Solution:
   1. Check internet connection
   2. Verify Discord isn't having issues (status.discordapp.com)
   3. Check token hasn't been invalidated
   4. Try reconnecting: restart bot
   5. Check firewall/network settings
```

## Performance Tips

🚀 **Optimization:**
- Messages are processed asynchronously
- Translation only active in enabled channels
- Consider caching frequent phrases
- Monitor MyMemory API usage

💾 **Caching Example:**
```python
translation_cache = {}

async def get_translation(text: str) -> str:
    if text in translation_cache:
        return translation_cache[text]
    
    translated = await translate_message(text)
    translation_cache[text] = translated
    return translated
```

## Error Handling

✅ **Built-in Safety:**
- Returns original message if translation fails
- Logs errors to console for debugging
- Bot continues if one message fails
- Graceful fallback mechanism
- Exception handling in all async functions

## Advanced Setup

### Run with PM2 (Production)

```bash
# Install PM2
npm install -g pm2

# Start bot
pm2 start bot.py --name "discord-translator" --interpreter python

# View logs
pm2 logs discord-translator

# Auto-restart on reboot
pm2 startup
pm2 save
```

### Run in Docker

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py .
COPY .env .

CMD ["python", "bot.py"]
```

**Build and run:**
```bash
docker build -t discord-translator .
docker run -d discord-translator
```

### Environment Variables

```bash
DISCORD_TOKEN=your_token_here
# Optional additions:
LOG_LEVEL=INFO
MAX_MESSAGE_LENGTH=2000
TRANSLATION_TIMEOUT=5
```

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Bot offline | Bad token | Regenerate token in Developer Portal |
| Slow translations | Free API | Use paid API or accept delay |
| Commands not appearing | Sync failed | Restart bot, wait 1 hour |
| Language not detected | Missing regex | Add detection to `detect_language()` |
| Slurs not censored | Not in list | Add to `SLURS` list |
| Rate limited | Too many requests | Implement request queue |

## Contributing

Feel free to fork and submit pull requests for improvements!

## License

MIT License - see LICENSE file for details

## Support

For issues or questions:
- Check [Discord.py Documentation](https://discordpy.readthedocs.io/)
- Visit [Discord Developer Docs](https://discord.com/developers/docs)
- Open an issue on GitHub
- Check troubleshooting section above

---

## Quick Reference

```bash
# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your token

# Run
python bot.py

# Commands in Discord
/startT      # Enable translation
/stopT       # Disable translation
/translate   # Manual translation
/status      # Check bot status
```

---

**Made with ❤️ for Discord communities**

### Version Info

- **Python Version:** 3.9+
- **Discord.py Version:** 2.3.2
- **Status:** ✅ Production Ready
- **Last Updated:** 2026-06-02
