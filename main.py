import logging
import requests
import telegram
import time
import os
from requests.exceptions import ReadTimeout, ConnectionError
from environs import Env


class TelegramLogsHandler(logging.Handler):

    def __init__(self, log_bot, chat_id):
        super().__init__()
        # self.chat_id = TELEGRAM_CHAT_ID
        # self.tg_bot = telegram.Bot(token=TELEGRAM_TOKEN)
        self.chat_id = chat_id
        self.tg_bot = log_bot
        self.tg_bot.send_message(chat_id=self.chat_id, text='LOG-BOT: started')

    def emit(self, record):
        log_entry = f"LOG-BOT: {self.format(record)}"
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


if __name__ == "__main__":
    env = Env()
    env.read_env()

    DEVMAN_TOKEN = env.str('DEVMAN_TOKEN') or os.environ['DEVMAN_TOKEN']
    TELEGRAM_TOKEN = env.str('TELEGRAM_TOKEN') or os.environ['TELEGRAM_TOKEN']
    TELEGRAM_CHAT_ID = env.int('TELEGRAM_CHAT_ID') or os.environ['TELEGRAM_CHAT_ID']

    debug = env.bool('DEBUG') or os.environ['DEBUG']
    logging.basicConfig(level=logging.INFO)
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    bot = telegram.Bot(token=TELEGRAM_TOKEN)

    logger = logging.getLogger('Logger')
    logger.setLevel(logging.INFO)  # TODO: Turn log level in .env
    logger.addHandler(TelegramLogsHandler(bot, TELEGRAM_CHAT_ID))

    headers = {'Authorization': f'Token {DEVMAN_TOKEN}'}

    polling_url = 'https://dvmn.org/api/long_polling/'
    payload = {}
    deferred_request_in_seconds = 2

    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text='Devman bot started')
        while True:
            logging.debug('Run DEVMAN bot')
            try:
                response = requests.get(
                    polling_url,
                    headers=headers,
                    params=payload,
                    timeout=100,
                )
                response.raise_for_status()
                result = response.json()
                deferred_request_in_seconds = 2

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
                logging.debug('Error ConnectionError. Details:')
                print(err)
                print(f'Request after: {deferred_request_in_seconds} sec.')
                time.sleep(deferred_request_in_seconds)
                deferred_request_in_seconds += deferred_request_in_seconds
    except Exception as err:
        logger.info('Error')
        logger.exception(err)
