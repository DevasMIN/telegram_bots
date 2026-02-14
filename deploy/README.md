# Деплой на сервер

## 1. Подготовка сервера

```bash
# Клонировать репозиторий
sudo mkdir -p /var/www/telegram_bots
sudo chown $USER:$USER /var/www/telegram_bots
cd /var/www/telegram_bots
git clone https://github.com/DevasMIN/telegram_bots.git .

# KKInstagram бот
cd kkinstagram
cp .env.example .env
nano .env  # добавить KKINSTAGRAM_BOT_TOKEN=...
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## 2. Systemd

```bash
sudo cp deploy/telegram-bot-kkinstagram.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot-kkinstagram
sudo systemctl start telegram-bot-kkinstagram
```

## 3. GitHub Secrets

В настройках репозитория → Secrets and variables → Actions добавить:
- `HOST` — IP или домен сервера
- `SSH_KEY` — приватный SSH-ключ
- `SSH_USERNAME` (опционально) — пользователь, по умолчанию root
- `SSH_PORT` (опционально) — порт SSH, по умолчанию 22

## 4. Настройка SSH на сервере

На сервере в `~/.ssh/authorized_keys` должен быть публичный ключ, соответствующий `SSH_KEY`.
