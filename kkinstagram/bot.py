import re
import os
import logging
from telegram import Update, MessageEntity
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from telegram.error import Conflict
from dotenv import load_dotenv

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Не логировать HTTP-запросы — в них попадает токен
logging.getLogger('telegram').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)

load_dotenv()

# Паттерн для ссылок Instagram (reel, p/, post и т.д.)
INSTAGRAM_PATTERN = re.compile(
    r'https?://(?:www\.)?instagram\.com/([^\s]+)',
    re.IGNORECASE
)


def replace_instagram_links(text: str) -> str | None:
    """Заменяет instagram.com на kkinstagram.com в тексте."""
    if not text:
        return None
    match = INSTAGRAM_PATTERN.search(text)
    if not match:
        return None

    replaced = INSTAGRAM_PATTERN.sub(
        r'https://kkinstagram.com/\1',
        text
    )
    return replaced if replaced != text else None


def extract_urls_from_message(message) -> str:
    """Собирает все URL из сообщения: text, caption, entities (url, text_link)."""
    if not message:
        return ''
    parts = []
    if message.text:
        parts.append(message.text)
    if message.caption:
        parts.append(message.caption)
    for entity in (message.entities or []):
        if entity.type == MessageEntity.TEXT_LINK and entity.url:
            parts.append(entity.url)
        elif entity.type == MessageEntity.URL:
            try:
                parts.append(message.parse_entity(entity))
            except (IndexError, TypeError, ValueError):
                pass
    for entity in (message.caption_entities or []):
        if entity.type == MessageEntity.TEXT_LINK and entity.url:
            parts.append(entity.url)
        elif entity.type == MessageEntity.URL:
            try:
                parts.append(message.parse_caption_entity(entity))
            except (IndexError, TypeError, ValueError):
                pass
    return ' '.join(parts)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает входящие сообщения и подменяет ссылки Instagram."""
    if not update.message:
        return

    msg = update.message

    # Собираем текст из сообщения, caption, entities и ответа
    text = extract_urls_from_message(msg)
    if msg.reply_to_message:
        text = text + ' ' + extract_urls_from_message(msg.reply_to_message)

    text = text.strip()
    replaced = replace_instagram_links(text)
    if replaced:
        target = msg.reply_to_message if (msg.reply_to_message and replace_instagram_links(extract_urls_from_message(msg.reply_to_message))) else msg
        sender = target.from_user
        sender_name = sender.first_name or ''
        if sender.last_name:
            sender_name = f'{sender_name} {sender.last_name}'.strip()
        if not sender_name and sender.username:
            sender_name = f'@{sender.username}'
        if not sender_name:
            sender_name = 'Неизвестный'
        text_with_header = f'От {sender_name}:\n{replaced}'
        try:
            await target.delete()
            await context.bot.send_message(chat_id=msg.chat_id, text=text_with_header)
        except Exception:
            await msg.reply_text(text_with_header)


HELP_TEXT = '''Я подменяю ссылки Instagram на kkinstagram.com.

Отправь ссылку вида:
https://www.instagram.com/reel/...

Я отвечу заменой:
https://kkinstagram.com/reel/...

В группах: добавь меня как админа с правом удаления — тогда я буду заменять сообщения. Без прав — просто отвечу.'''


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    if isinstance(context.error, Conflict):
        logger.error('Запущен другой экземпляр бота! Остановите все процессы bot.py и запустите заново.')
        raise SystemExit(1)
    logger.exception('Ошибка при обработке обновления')


def main() -> None:
    token = os.getenv('KKINSTAGRAM_BOT_TOKEN')
    if not token:
        raise ValueError('Установите KKINSTAGRAM_BOT_TOKEN в .env файле')

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler('help', help_handler))
    app.add_handler(CommandHandler('start', help_handler))
    # Обрабатываем все сообщения (в т.ч. личку, где ссылка может быть в entity)
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    app.add_error_handler(error_handler)

    logger.info('Бот запущен')
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
