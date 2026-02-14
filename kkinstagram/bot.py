import re
import os
import logging
from telegram import Update, MessageEntity
from telegram.ext import Application, MessageHandler, CommandHandler, TypeHandler, filters, ContextTypes
from telegram.error import Conflict
from dotenv import load_dotenv

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Не логировать HTTP-запросы — в них попадает токен
logging.getLogger('telegram').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)


async def _log_all_updates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Логирует ВСЕ апдейты — для отладки."""
    if update.message:
        logger.info('UPDATE: message chat_id=%s', update.message.chat_id)
    elif update.edited_message:
        logger.info('UPDATE: edited_message chat_id=%s', update.edited_message.chat_id)
    else:
        logger.info('UPDATE: type=%s', type(update).__name__)

load_dotenv()

# Паттерн для ссылок Instagram (reel, p/, post и т.д.)
INSTAGRAM_PATTERN = re.compile(
    r'https?://(?:www\.)?instagram\.com/([^\s]+)',
    re.IGNORECASE
)


def _get_sender_name(user) -> str:
    if not user:
        return 'Неизвестный'
    name = user.first_name or ''
    if user.last_name:
        name = f'{name} {user.last_name}'.strip()
    return name or (f'@{user.username}' if user.username else 'Неизвестный')


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
    """Собирает все URL из сообщения: text, caption + скрытые URL из text_link."""
    if not message:
        return ''
    parts = []
    # Берём text/caption — в них уже содержатся обычные URL
    if message.text:
        parts.append(message.text)
    if message.caption:
        parts.append(message.caption)
    # Дополнительно: TEXT_LINK — ссылка скрыта за текстом, её нет в text/caption
    for entity in (message.entities or []):
        if entity.type == MessageEntity.TEXT_LINK and entity.url:
            parts.append(entity.url)
    for entity in (message.caption_entities or []):
        if entity.type == MessageEntity.TEXT_LINK and entity.url:
            parts.append(entity.url)
    return ' '.join(parts)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает входящие сообщения и подменяет ссылки Instagram."""
    if not update.message:
        return

    msg = update.message

    text = extract_urls_from_message(msg)
    if msg.reply_to_message:
        text = text + ' ' + extract_urls_from_message(msg.reply_to_message)

    text = text.strip()
    replaced = replace_instagram_links(text)
    if not replaced:
        return

    is_private = msg.chat and msg.chat.type == 'private'

    if is_private:
        # В личке: просто отвечаем заменённой ссылкой
        await msg.reply_text(replaced)
    else:
        # В группе: пытаемся удалить и отправить от имени бота
        target = msg.reply_to_message if (msg.reply_to_message and replace_instagram_links(extract_urls_from_message(msg.reply_to_message))) else msg
        text_with_header = f'От {_get_sender_name(target.from_user)}:\n{replaced}'
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

В личке: сначала нажми Start (или /start), затем отправь ссылку.

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

    async def log_updates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.message:
            t = (update.message.text or update.message.caption or '(пусто)')[:80]
            logger.info('>>> %s | %r', update.message.chat.type, t)

    app.add_handler(TypeHandler(Update, _log_all_updates), group=-2)
    app.add_handler(MessageHandler(filters.ALL, log_updates), group=-1)
    app.add_handler(CommandHandler('help', help_handler))
    app.add_handler(CommandHandler('start', help_handler))
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    app.add_error_handler(error_handler)

    logger.info('Бот запущен, polling... (если UPDATE не появляются — проверь: 1) нет ли другого экземпляра 2) доступ к api.telegram.org)')
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
