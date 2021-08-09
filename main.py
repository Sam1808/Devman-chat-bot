import requests
import telegram
import time
import os
from requests.exceptions import ReadTimeout, ConnectionError
from environs import Env


if __name__ == "__main__":

    env = Env()
    env.read_env()

    DEVMAN_TOKEN = env.str('DEVMAN_TOKEN') or os.environ['DEVMAN_TOKEN']
    TELEGRAM_TOKEN = env.str('TELEGRAM_TOKEN') or os.environ['TELEGRAM_TOKEN']
    TELEGRAM_CHAT_ID = env.int('TELEGRAM_CHAT_ID') or os.environ['TELEGRAM_CHAT_ID']

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
            pass
        except ConnectionError as err:
            print(err)
            print(f'Request after: {deferred_request_in_seconds} sec.')
            time.sleep(deferred_request_in_seconds)
            deferred_request_in_seconds += deferred_request_in_seconds
