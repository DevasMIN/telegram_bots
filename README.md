# telegram_bots

Коллекция Telegram-ботов.

## Боты

### KKInstagram (`kkinstagram/`)

Подменяет ссылки Instagram на kkinstagram.com.

- Отправь ссылку `https://www.instagram.com/reel/...` → получишь `https://kkinstagram.com/reel/...`
- В группах с правами админа — заменяет сообщения; без прав — отвечает
- Команды: `/help`, `/start`

**Запуск:**
```bash
cd kkinstagram
cp .env.example .env  # добавить KKINSTAGRAM_BOT_TOKEN
pip install -r requirements.txt
python bot.py
```

## Деплой

См. [deploy/README.md](deploy/README.md)
