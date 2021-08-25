import logging
import requests
import telegram
import time
from requests.exceptions import ReadTimeout, ConnectionError
from environs import Env

logger = logging.getLogger('Logger')


class TelegramLogsHandler(logging.Handler):

    def __init__(self, log_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = log_bot
        self.tg_bot.send_message(chat_id=self.chat_id, text='LOG-BOT: started')

    def emit(self, record):
        log_entry = f"LOG-BOT: {self.format(record)}"
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


if __name__ == "__main__":
    env = Env()
    env.read_env()

    DEVMAN_TOKEN = env.str('DEVMAN_TOKEN')
    TELEGRAM_TOKEN = env.str('TELEGRAM_TOKEN')
    TELEGRAM_CHAT_ID = env.int('TELEGRAM_CHAT_ID')
    debug = env.bool('DEBUG')

    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level)

    logger.setLevel(logging.INFO)

    headers = {'Authorization': f'Token {DEVMAN_TOKEN}'}

    polling_url = 'https://dvmn.org/api/long_polling/'
    payload = {}
    deferred_request_in_seconds = 2  # If a ConnectionError is received at the first start

    while True:  # Restart bot for any Exception
        try:
            bot = telegram.Bot(token=TELEGRAM_TOKEN)
            logger.addHandler(TelegramLogsHandler(bot, TELEGRAM_CHAT_ID))
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text='Devman bot started')

            while True:  # Re-request if ReadTimeout or ConnectionError
                logging.debug('Run DEVMAN bot')
                try:
                    response = requests.get(
                        polling_url,
                        headers=headers,
                        params=payload,
                        timeout=3,
                    )
                    response.raise_for_status()
                    result = response.json()
                    deferred_request_in_seconds = 2  # If a second ConnectionError is received after bot recovery

                    if 'timeout' in result['status']:
                        payload['timestamp'] = result['timestamp_to_request']
                        continue

                    payload['timestamp'] = result['last_attempt_timestamp']

                    for attempt in result['new_attempts']:

                        errors = attempt['is_negative']
                        message = f'''
                        The task has been verified:
                        Title: {attempt['lesson_title']}
                        Errors: {errors}
                        URL: https://dvmn.org{attempt['lesson_url']}
                        '''

                        if errors:
                            bot.send_message(
                                chat_id=TELEGRAM_CHAT_ID,
                                text=f'You have to work harder! {message}'
                                )
                            continue

                        bot.send_message(
                            chat_id=TELEGRAM_CHAT_ID,
                            text=f'Congratulations! {message}'
                            )
                except ReadTimeout:
                    logging.debug('Error ReadTimeout')
                    pass
                except ConnectionError as err:
                    logger.info('Bot catch ConnectionError exception. Need your attention.')
                    logging.debug(
                        f'''Error ConnectionError. Details:
                        {err}
                        Re-request after: {deferred_request_in_seconds} sec.'''
                    )
                    time.sleep(deferred_request_in_seconds)
                    deferred_request_in_seconds += deferred_request_in_seconds
        except Exception as err:
            logging.exception(err)
