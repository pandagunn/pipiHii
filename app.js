import 'dotenv/config';
import express from 'express';
import {
  InteractionResponseFlags,
  InteractionResponseType,
  InteractionType,
  verifyKeyMiddleware,
} from 'discord-interactions';
import { DiscordRequest } from './utils.js';
import { processMessage } from './translator.js';

// Create an express app
const app = express();
// Get port, or default to 3000
const PORT = process.env.PORT || 3000;

// Store active translation channels and users
const activeTranslations = new Map(); // channelId -> { enabled: boolean, userId: string }

/**
 * Interactions endpoint URL where Discord will send HTTP requests
 * Parse request body and verifies incoming requests using discord-interactions package
 */
app.post('/interactions', verifyKeyMiddleware(process.env.PUBLIC_KEY), async function (req, res) {
  const { type, data, channel_id, member, user } = req.body;

  /**
   * Handle verification requests
   */
  if (type === InteractionType.PING) {
    return res.send({ type: InteractionResponseType.PONG });
  }

  /**
   * Handle slash command requests
   */
  if (type === InteractionType.APPLICATION_COMMAND) {
    const { name } = data;
    const userId = member?.user?.id || user?.id;
    const channelId = channel_id;

    // /startT command
    if (name === 'startT') {
      try {
        // Mark this channel as having active translation
        activeTranslations.set(channelId, {
          enabled: true,
          userId: userId,
          startedAt: new Date().toISOString()
        });

        return res.send({
          type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
          data: {
            content: '🌍 **Automatic Translation Enabled**\n' +
                     'All messages in this channel will now be automatically translated to English and checked for inappropriate content.\n' +
                     'Supported languages: Chinese, Portuguese (Brazil), Vietnamese, German, and more.\n' +
                     'Use `/stopT` to disable translation.',
            flags: InteractionResponseFlags.IS_COMPONENTS_V2
          },
        });
      } catch (error) {
        console.error('Error in startT command:', error);
        return res.send({
          type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
          data: {
            content: '❌ Error enabling translation. Please try again.',
          },
        });
      }
    }

    // /stopT command
    if (name === 'stopT') {
      try {
        // Disable translation for this channel
        activeTranslations.delete(channelId);

        return res.send({
          type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
          data: {
            content: '🛑 **Automatic Translation Disabled**\n' +
                     'Translation has been turned off for this channel.\n' +
                     'Use `/startT` to enable it again.',
            flags: InteractionResponseFlags.IS_COMPONENTS_V2
          },
        });
      } catch (error) {
        console.error('Error in stopT command:', error);
        return res.send({
          type: InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
          data: {
            content: '❌ Error disabling translation. Please try again.',
          },
        });
      }
    }

    console.error(`unknown command: ${name}`);
    return res.status(400).json({ error: 'unknown command' });
  }

  console.error('unknown interaction type', type);
  return res.status(400).json({ error: 'unknown interaction type' });
});

// Handle MESSAGE_CREATE events via gateway (requires bot to be setup with intents)
// This is a fallback - you'll need to setup the Discord bot gateway for real message interception
app.post('/gateway-events', async (req, res) => {
  try {
    const { type, data } = req.body;

    if (type === 'MESSAGE_CREATE') {
      const message = data;
      const channelId = message.channel_id;

      // Check if translation is enabled for this channel
      if (activeTranslations.has(channelId)) {
        const translationConfig = activeTranslations.get(channelId);
        
        if (translationConfig.enabled) {
          try {
            // Process the message
            const translatedText = await processMessage(message);
            
            // Send translated message back to channel
            const endpoint = `channels/${channelId}/messages`;
            await DiscordRequest(endpoint, {
              method: 'POST',
              body: {
                content: `🔄 **Translation** (from ${message.author.username}):\n${translatedText}`,
                message_reference: {
                  message_id: message.id,
                  channel_id: channelId,
                  guild_id: message.guild_id
                }
              }
            });
          } catch (error) {
            console.error('Error translating message:', error);
          }
        }
      }
    }

    res.send({ success: true });
  } catch (error) {
    console.error('Gateway event error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', activeTranslations: activeTranslations.size });
});

app.listen(PORT, () => {
  console.log('🤖 Discord Translation Bot listening on port', PORT);
  console.log('Available commands: /startT, /stopT');
});
