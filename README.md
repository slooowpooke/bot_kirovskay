
# Telegram Bot (Render, 3 шага)

Этапы бота:
1. Приветствие + согласие с политикой
2. Ожидание видео от клиента
3. Отправка видео менеджеру + благодарность

## Локальный запуск (опционально)
1. Установите Python 3.10+ и зависимости:
   ```bash
   pip install -r requirements.txt
   ```
2. Задайте переменные окружения (Windows PowerShell пример):
   ```powershell
   setx TELEGRAM_TOKEN "ВАШ_ТОКЕН_ОТ_BOTFATHER"
   setx MANAGER_CHAT_ID "ВАШ_TG_ID_ЧИСЛОМ"
   ```
   или в текущей сессии bash:
   ```bash
   export TELEGRAM_TOKEN="ВАШ_ТОКЕН_ОТ_BOTFATHER"
   export MANAGER_CHAT_ID="ВАШ_TG_ID_ЧИСЛОМ"
   ```
3. Запуск:
   ```bash
   python bot.py
   ```

## Деплой на Render
1. Загрузите этот проект в репозиторий GitHub.
2. Войдите на https://render.com → **New** → **Web Service** → выберите ваш репозиторий.
3. Настройки сервиса:
   - Environment: **Python 3**
   - Build Command:
     ```
     pip install -r requirements.txt
     ```
   - Start Command:
     ```
     python bot.py
     ```
4. Переменные окружения (**Environment**):
   - `TELEGRAM_TOKEN` — токен бота из @BotFather
   - `MANAGER_CHAT_ID` — ваш Telegram ID (узнать можно через @userinfobot)
5. Сохраните и дождитесь деплоя. Бот будет работать 24/7.

### Подсказки
- Если Render перезапустился, бот запустится автоматически.
- Если видео очень большое и не отправляется как `video`, бот попробует переслать как `document`.
- Логи смотрите во вкладке **Logs** в Render.

Удачи! 🚀
