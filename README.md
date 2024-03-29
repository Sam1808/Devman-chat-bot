## Telegram чат-бот для проверки заданий от [Devman.org](https://dvmn.org/)
Просто запустите этого бота, чтобы вовремя знать о поступающих проверках ваших заданий.  
### Что необходимо: 

- Учетная запись [Devman.org](https://dvmn.org/) и бесплатный доступ к [API](https://dvmn.org/api/docs/)
- Свой [Телеграм бот](https://telegram.me/BotFather) и его ID
- Выполнить задания от [Devman.org](https://dvmn.org/)
- Учетная запись [HEROKU](https://id.heroku.com/login) и выложенный код на [GitHub](https://github.com) для деплоя своего бота.

### Установка и использование.

#### I. Локальный запуск бота:
- Скачайте и распакуйте код
```
git clone https://github.com/Sam1808/Devman-chat-bot.git
```
- Создайте файл `.env`, где необходимо указать *чуствительные* данные, а именно: 
```
DEVMAN_TOKEN=ваш_Devman_токен
TELEGRAM_TOKEN=ваш_Telegram_токен
TELEGRAM_CHAT_ID=номер_(ID)_вашего_Telegram_чата
DEBUG=True
TIMEOUT=таймаут запросов к серверу в секундах
```
**Важно**: если у вас проблема с TELEGRAM_CHAT_ID, то напишите в Telegram специальному боту @userinfobot. Данный параметр может быть только цифровой.
- Установите зависимости (используйте [виртуальное окружение](https://devman.org/encyclopedia/pip/pip_virtualenv/))
```
pip install -r requirements.txt
```
- Запустите код
```
python3 main.py
```

#### II. Разворачиваем бота на HEROKU:
- Опубликуйте код на GitHub.
- Авторизуйтесь на HEROKU и [создайте приложение](https://dashboard.heroku.com/new-app?org=personal-apps).  
- Подключите свой профиль GitHub и укажите репозиторий с кодом бота.
- Нажмите кнопку `Deploy branch` и дождитесь успешного развертывания приложения.
- На вкладке `Resources` включите `bot python3 main.py`.
- На вкладке `Settings` сконфигурируйте `Config Vars` аналогично вашему файлу `.env`.
- Повторное `Deploy branch` ускорит процесс ;).

#### III. Использование  
Использование сводится к получению информации в Telergam чат о проверенном уроке, наличие ошибок и ссылке на само задание.
>Обновлено:  
> Теперь в системе живет не только бот, который сообщает о заданиях, но и отдельный бот,
> который логирует ошибки и присылает их в этот же чат.  
> В чате такие сообщения будут присылаться от имени `LOG-BOT`.  
> Скрипт будет пытаться перезапустить бота в случае любой ошибки, но не факт, что это ему будет удаваться. 
> Поэтому без вашего внимания все-таки никак, логи для того и существуют, что бы на них обращали внимание.
</br></br>
### Ошибки.
Код сообщит в консоли о факте проблем с соединением и запустит следующее соединение после паузы.
> А ещё он пришлет вам текст ошибок в чат.
