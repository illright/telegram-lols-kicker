<a href="./README.md">
   <img align="right" alt="README in English" src="./.github/readme-assets/readme-in-english.svg" height="36" /></a>

# LOLS кикер-бот для Telegram

Этот бот кикает пользователей (но только один раз), которые были помечены как спамеры в [базе данных LOLS](https://lols.bot/).

## Возможности:

- Разработан для самостоятельного хостинга
- Минималистичный, чтобы было легко понять исходный код
- Работает только в чатах, которые он распознает (настраиваемо)
- Человечный, учитывает, что некоторые пользователи могут быть ошибочно обвинены, поэтому позволяет им повторно присоединиться

## Как бесплатно самостоятельно захостить

Вам понадобится установленный [uv](https://github.com/astral-sh/uv).

1. Склонируйте этот проект
2. Запустите `uv sync` для установки зависимостей
3. Переименуйте файл `.env.sample` в `.env`
4. Создайте аккаунт на [modal.com](https://modal.com); там будет хоститься бот
   1. Запустите в терминале `uv run modal setup` для входа в Modal
6. Создайте Telegram-бота с помощью [@BotFather](https://t.me/BotFather)
   1. Скопируйте токен бота в `TELEGRAM_BOT_TOKEN` в файле `.env`, удалив оттуда токен-пример
7. [Создайте длинный пароль](https://bitwarden.com/password-generator/#password-generator) (50 символов) и скопируйте его в `EXTRA_SECURITY_TOKEN` в файле `.env`, удалив оттуда значение-пример.
8. Создайте секрет на Modal с помощью этих команд:
   1. `source .env` для загрузки переменных окружения в ваш шелл
   2. `uv run modal secret create lols-kicker-telegram-bot-token EXTRA_SECURITY_TOKEN=$EXTRA_SECURITY_TOKEN TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN`
10. Перейдите в `main.py` и найдите `allowed_chats`. Замените пример чата на свой.
11. Запустите `uv run modal deploy -m main` для развертывания бота на Modal
    1. Он выведет веб-эндпоинт:
       ```
       └── 🔨 Created web endpoint for LolsKicker.process_update => 
           https://something-something.modal.run
       ```
       Скопируйте `https://something-something.modal.run` в `WEBHOOK_URL` в файле `.env`, удалив пример значения
12. Запустите `uv run setup_bot.py` для подключения бота к вашему приложению Modal и установки дополнительного токена безопасности
13. Пригласите бота в ваш чат. Готово!

## Навигация по исходному коду

Код бота почти полностью содержится в файле [`main.py`](./main.py). Логика работы бота находится в методе `setup_bot` класса `Model`.

`setup_bot.py` — это скрипт, который используется для подключения бота к приложению Modal и установки дополнительного токена безопасности.

## Лицензия

Исходный код бота лицензирован под GNU AGPL-3.0. Объяснение: https://choosealicense.com/licenses/agpl-3.0
