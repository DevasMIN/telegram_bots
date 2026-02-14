# Telegram Bot — замена ссылок Instagram

Бот отслеживает сообщения в чатах и автоматически подменяет ссылки Instagram на kkinstagram.com.

**Пример:**
- Входящее: `https://www.instagram.com/reel/DUGxOCBCJQG/?igsh=b2FlNDJjeTNmbGFw`
- Ответ бота: `https://kkinstagram.com/reel/DUGxOCBCJQG/?igsh=b2FlNDJjeTNmbGFw`

## Установка

```bash
pip install -r requirements.txt
```

## Настройка

1. Создайте бота через [@BotFather](https://t.me/BotFather) в Telegram
2. Скопируйте `.env.example` в `.env`
3. Укажите токен в `.env`:
   ```
   TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather
   ```

## Запуск

```bash
python bot.py
```

## Добавление в группу

1. **Отключи режим приватности** в @BotFather: `/setprivacy` → выбери бота → **Disable**. Иначе бот не будет получать сообщения в группах.
2. Добавь бота в группу. С правами админа бот будет заменять сообщения; без прав — просто отвечать подменённой ссылкой.

## Деплой

См. [deploy/README.md](deploy/README.md) — настройка сервера, systemd и GitHub Actions.
