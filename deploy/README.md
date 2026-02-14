# Деплой на сервер (Docker)

## 1. Подготовка сервера

```bash
# Установить Docker и Docker Compose (если нет)
# Ubuntu: apt install docker.io docker-compose-plugin

# Клонировать репозиторий
sudo mkdir -p /var/www/telegram_bots
sudo chown $USER:$USER /var/www/telegram_bots
cd /var/www/telegram_bots
git clone https://github.com/DevasMIN/telegram_bots.git .
```

При push в main GitHub Actions выполнит `docker compose up -d --build` — боты пересоберутся и перезапустятся.

## 2. Ручной запуск (если нужно)

```bash
cd /var/www/telegram_bots
echo "KKINSTAGRAM_BOT_TOKEN=твой_токен" > .env
docker compose up -d --build
```

## 3. GitHub Secrets

В настройках репозитория → Secrets and variables → Actions добавить:
- `HOST` — IP или домен сервера
- `SSH_KEY` — приватный SSH-ключ (см. ниже)
- `KKINSTAGRAM_BOT_TOKEN` — токен бота от @BotFather
- `SSH_USERNAME` (опционально) — пользователь на сервере, по умолчанию root
- `SSH_PORT` (опционально) — порт SSH, по умолчанию 22

## 4. Как получить SSH-ключ

```bash
# Ed25519 (рекомендуется)
ssh-keygen -t ed25519 -C "github-deploy" -f ~/.ssh/github_deploy -N ""

# Или RSA
ssh-keygen -t rsa -b 4096 -C "github-deploy" -f ~/.ssh/github_deploy -N ""
```

- **Приватный ключ** (`~/.ssh/github_deploy`) → в GitHub Secrets как `SSH_KEY`
- **Публичный ключ** (`~/.ssh/github_deploy.pub`) → на сервер в `~/.ssh/authorized_keys`

## 5. Зачем SSH_USERNAME

SSH подключается как `пользователь@хост`. Ключ лежит в `authorized_keys` этого пользователя. `SSH_USERNAME` — под каким юзером заходить (root, ubuntu и т.д.). По умолчанию — root.
