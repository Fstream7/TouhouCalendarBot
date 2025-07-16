from touhou_calendar import days_for, format_twitter, format_discord_embed, format_upcoming_twitter, format_upcoming_discord_embed, format_telegram_message, format_upcoming_telegram_message
import json
import os
import sys
import logging
import datetime
import argparse

from urllib.parse import urlparse

logging.basicConfig()

parser = argparse.ArgumentParser()
parser.add_argument("--discord", action="store_true", help="Post on Discord")
parser.add_argument("--twitter", action="store_true", help="Post on Twitter")
parser.add_argument("--telegram", action="store_true", help="Post on Telegram")
parser.add_argument("--today-only", action="store_true", help="Not show upcoming days")
parser.add_argument("--dry", action="store_true", help="Dry run")
parser.add_argument("--force", action="store_true", help="Post on dry mode")
parser.add_argument("--date", help="Run with custom date YYYY-MM-DDD")

args = parser.parse_args()

if not args.telegram and not args.twitter and not args.discord:
    parser.print_help()

if args.date:
    if (not args.force) and (not args.dry):
        print("Date specified for non-dry run!")
        sys.exit(1)

    today_jst = datetime.date(*map(int, args.date.split("-")))
    date_utc = today_jst
else:
    JST = datetime.timezone(datetime.timedelta(hours=9), name="JST")
    today_jst = datetime.datetime.now(JST).date()

    date_utc = datetime.datetime.utcnow().date()

touhoudays = days_for(today_jst)


twitter_preview = None
embeds = []
telegram_messages = []

if date_utc.weekday() == 6 and not args.today_only:
    # It's Sunday, my dudes. Post a preview
    preview_start = today_jst + datetime.timedelta(days=1)
    preview_end   = preview_start + datetime.timedelta(days=14)
    twitter_preview = format_upcoming_twitter(preview_start, preview_end)
    embeds.append(format_upcoming_discord_embed(preview_start, preview_end))
    telegram_messages.append(format_upcoming_telegram_message(preview_start, preview_end))

if touhoudays is not None:
    embeds.append(format_discord_embed(touhoudays))
    telegram_messages.extend(format_telegram_message(touhoudays))


if args.twitter:
    if twitter_preview:
        print(twitter_preview)
    print(today_jst, touhoudays)

if args.discord and len(embeds) > 0:
    if args.dry:
        #Todo: Better dry run
        print(json.dumps(embeds))
    else:
        WEBHOOK_URL = os.environ['WEBHOOK_URL']
        import requests
        import time

        MAX_WEBHOOK_POST_RETRIES = 5

        for webhook_url in WEBHOOK_URL.split(" "):
            for attempt in range(MAX_WEBHOOK_POST_RETRIES):
                try:
                    resp = requests.post(webhook_url+"?wait=true", json={'embeds': embeds})
                    if resp.ok:
                        print(webhook_url+"/messages/"+resp.json()["id"])

                    try:
                        rl_remaining = int(resp.headers["X-RateLimit-Remaining"])
                        if rl_remaining == 0:
                            rl_after = float(resp.headers["X-RateLimit-Reset-After"])
                            time.sleep(rl_after)
                    except:
                        logging.exception('Error handling ratelimiting from {}'.format(webhook_url))

                    if resp.ok:
                        break
                except:
                    logging.exception('Failed to send Discord message {}'.format(webhook_url))
            else:
                logging.error('Failed to send Discord message {}'.format(webhook_url))

if args.telegram and len(telegram_messages) > 0:
    for message in telegram_messages:
        if args.dry:
            print(message)
        else:
            import requests
            TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
            TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }
            try:
                response = requests.post(url, data=payload)
                response.raise_for_status()
            except requests.exceptions.HTTPError:
                print(f"Failed to send Telegram message: {response.text}")
            print(response.json())
