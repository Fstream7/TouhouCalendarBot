# Touhou Calendar Bot

A simple bot that posts about Touhou Character days to Twitter, Discord and Telegram. 
Primarily a list of such days with English explanations at the moment.

## environment variables

#### Discord
- `WEBHOOK_URL=` Discord webhook integration. 

#### Telegram
- `TELEGRAM_BOT_TOKEN=` Telegram bot token.
- `TELEGRAM_CHAT_ID=` Telegram chat id where message will be posted.

### Usage:
```bash
python3 post_calendar.py
```
This will show help with all availiable commands

#### Dry run with custom date for telegram:
```bash
python3 post_calendar.py --dry --telegram --date 2025-06-18 
```
