
import requests
import telegram
import time
from requests.exceptions import ReadTimeout, ConnectionError
from environs import Env


if __name__ == "__main__":

    env = Env()
    env.read_env()

    DEVMAN_TOKEN = env.str('DEVMAN_TOKEN')
    TELEGRAM_TOKEN = env.str('TELEGRAM_TOKEN')
    TG_CHAT_ID = env.int('TG_CHAT_ID')

    bot = telegram.Bot(token=TELEGRAM_TOKEN)

    headers = {'Authorization': f'Token {DEVMAN_TOKEN}'}

    polling_url = 'https://dvmn.org/api/long_polling/'
    payload = {}
    deferred_request_in_seconds = 2

    while True:
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

            if 'timestamp_to_request' in result:
                payload = {
                    'timestamp': str(result['timestamp_to_request'])
                }
            elif 'last_attempt_timestamp' in result:
                payload = {
                    'timestamp': str(result['last_attempt_timestamp'])
                }

            if 'new_attempts' not in result:
                continue

            # we have a chance for a few checks
            for attempt in result['new_attempts']:

                errors = attempt['is_negative']

                message = f'''
                The task has been verified:
                Title: {attempt['lesson_title']}
                Errors: {errors}
                URL: https://dvmn.org/{attempt['lesson_url']}
                '''

                bot.send_message(chat_id=TG_CHAT_ID, text=message)

                if errors:
                    message = 'You have to work harder!!!'
                    bot.send_message(chat_id=TG_CHAT_ID, text=message)
                    continue

                message = 'Congratulations! It is time to take on a new task!'
                bot.send_message(chat_id=TG_CHAT_ID, text=message)

        except ReadTimeout:
            pass
        except ConnectionError as err:
            print(err)
            print(
                f'Request after: {deferred_request_in_seconds} sec.'
                )
            time.sleep(deferred_request_in_seconds)
            deferred_request_in_seconds += deferred_request_in_seconds
