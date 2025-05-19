<a href="./README.ru.md">
   <img align="right" alt="README на русском" src="./.github/readme-assets/readme-in-russian.svg" height="36" /></a>

# LOLS kicker Telegram bot

This bot kicks users (but only once) that are recognized as spammers by [the LOLS database](https://lols.bot/).

Features:

- Built to be self-hosted
- Minimalistic so that it's easy to understand the source code
- Only works in chats that it recognizes (configurable)
- Humane, anticipates that some users might be wrongly accused, so lets them rejoin

## How to self-host for free

You will need [uv](https://github.com/astral-sh/uv) installed.

1. Clone this project
2. Run `uv sync` to install dependencies
3. Rename the `.env.sample` file to `.env`
4. Create an account on [modal.com](https://modal.com); that's where the bot will be hosted
   1. Run `uv run modal setup` to log in from the terminal
6. Create a Telegram bot using [@BotFather](https://t.me/BotFather)
   1. Copy the bot token into `TELEGRAM_BOT_TOKEN` in the `.env` file, removing the sample value
7. [Create a long password](https://bitwarden.com/password-generator/#password-generator) (50 characters) and copy it into `EXTRA_SECURITY_TOKEN` in the `.env` file, removing the sample value
8. Create a secret on Modal with these commands:
   1. `source .env` to load the environment variables into your shell
   2. `uv run modal secret create lols-kicker-telegram-bot-token EXTRA_SECURITY_TOKEN=$EXTRA_SECURITY_TOKEN TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN`
10. Go to `main.py` and find `allowed_chats`. Replace the sample chat with your own.
11. Run `uv run modal deploy -m main` to deploy the bot to Modal
    1. It will print the web endpoint:
       ```
       └── 🔨 Created web endpoint for LolsKicker.process_update => 
           https://something-something.modal.run
       ```
       Copy `https://something-something.modal.run` into `WEBHOOK_URL` in the `.env` file, removing the sample value
12. Run `uv run setup_bot.py` to connect the bot to your Modal app and set the extra security token
13. Invite the bot to your chat. Done!

## Navigate the source code

The code of the bot is almost entirely contained in [`main.py`](./main.py). The logic of what the bot does is inside the `setup_bot` method in the `Model` class.

The `setup_bot.py` is a script that is used to connect the bot to the Modal app and set the extra security token.

## License

The source code of the bot is licensed under GNU AGPL-3.0. Explained: https://choosealicense.com/licenses/agpl-3.0
