import hmac
import logging
import os
from datetime import datetime, timedelta
from typing import Annotated

import modal
from fastapi import Header
from aiogram import types

remote_project_path = "/app"
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("fastapi==0.115.12")
    .pip_install("pydantic==2.11.4")
    .pip_install("aiogram==3.20.0.post0")
    .pip_install("requests==2.32.3")
)

with image.imports():
    import requests
    from aiogram import Bot, Dispatcher, types
    from aiogram.enums import ParseMode
    from aiogram.client.default import DefaultBotProperties
    from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER, ChatMemberUpdatedFilter


app = modal.App(name="lols-kicker", image=image)
kicked_users = modal.Dict.from_name("kicked_users", create_if_missing=True)

# Add your chat here to allow the bot to work there.
allowed_chats = [
    "feature_sliced"
    # "your_chat_link_without_@",
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.cls(
    image=image,
    secrets=[modal.Secret.from_name("lols-kicker-telegram-bot-token")],
    scaledown_window=2,
)
class LolsKicker:
    @modal.enter()
    def setup_bot(self):
        """Register event handlers for the bot."""
        self.dp = Dispatcher()

        @self.dp.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
        async def on_new_user(event: types.chat_member_updated.ChatMemberUpdated):
            """
            When a new user joins, check them in the LOLS database and kick them if LOLS says they are a spammer.

            To allow wrongly accused users to join, we only kick them the first time, and let them through the second time.
            """
            if event.new_chat_member.user.id in kicked_users:
                logger.info(
                    f"User {event.new_chat_member.user.id} has been kicked before and joined again, letting them through"
                )
                self.forget_users_kicked_weeks_ago()
                return

            response = requests.get(
                "https://api.lols.bot/account",
                params={"id": event.new_chat_member.user.id, "quick": True},
            )

            if not response.ok:
                logger.error(
                    f"Request to LOLS API failed with status code {response.status_code}, {response.text}"
                )
            elif response.json().get("banned"):
                logger.info(
                    f"User {event.new_chat_member.user.id} is recognized as spammer by LOLS, kicking"
                )
                await self.bot.ban_chat_member(
                    chat_id=event.chat.id,
                    user_id=event.new_chat_member.user.id,
                    until_date=timedelta(seconds=30),
                )
                kicked_users[event.new_chat_member.user.id] = datetime.now()

            self.forget_users_kicked_weeks_ago()

        @self.dp.my_chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
        async def on_me_added_to_chat(
            event: types.chat_member_updated.ChatMemberUpdated,
        ):
            """Leave chats where the bot is not expected to run."""
            if (
                event.chat.id not in allowed_chats
                and event.chat.username not in allowed_chats
            ):
                logger.info(f"Added to unknown chat {event.chat.id}, leaving")
                await self.bot.leave_chat(event.chat.id)

        if "TELEGRAM_BOT_TOKEN" in os.environ:
            self.bot = Bot(
                token=os.environ["TELEGRAM_BOT_TOKEN"],
                default=DefaultBotProperties(parse_mode=ParseMode.HTML),
            )

    @modal.fastapi_endpoint(method="POST")
    async def process_update(
        self,
        update: dict,
        x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None,
    ) -> None | dict:
        """Accept an update from Telegram's API and verify that it's legit."""

        if not hmac.compare_digest(
            x_telegram_bot_api_secret_token, os.environ["EXTRA_SECURITY_TOKEN"]
        ):
            logger.error("Wrong secret token!")
            return {"status": "error", "message": "Wrong secret token!"}

        logger.info(f"Received update: {update}")
        telegram_update = types.Update(**update)
        try:
            await self.dp.feed_webhook_update(bot=self.bot, update=telegram_update)
        except Exception as e:
            logger.error(e, exc_info=True)

    def forget_users_kicked_weeks_ago(self):
        """Forget users who were kicked more than a week ago."""
        now = datetime.now()

        users_to_forget = []
        for user_id, timestamp in kicked_users.items():
            if now - timestamp > timedelta(days=7):
                logger.info(f"Forgetting kicked user {user_id}, kicked on {timestamp}")
                users_to_forget.append(user_id)

        for user_id in users_to_forget:
            kicked_users.pop(user_id)
