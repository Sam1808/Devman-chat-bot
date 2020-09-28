
import requests
import telegram
from requests.exceptions import ReadTimeout, ConnectionError
from environs import Env


if __name__ == "__main__":
    
    env = Env()
    env.read_env()  # read .env file

    DEVMAN_TOKEN = env.str('DEVMAN_TOKEN')
    TELEGRAM_TOKEN = env.str('TELEGRAM_TOKEN')
    TG_CHAT_ID = env.int('TG_CHAT_ID')

    bot = telegram.Bot(token=TELEGRAM_TOKEN)

    headers = {'Authorization': f'Token {DEVMAN_TOKEN}'}

    polling_url = 'https://dvmn.org/api/long_polling/'
    payload = {}

    while True:
        try:
                        
            response = requests.get(polling_url,headers = headers, params=payload) 
            response.raise_for_status()
            result = response.json()
            
            if 'timestamp_to_request' in result:
                payload= {
                    'timestamp': str(result['timestamp_to_request'])
                }
            
            if not 'status' in result:
                continue
            
            errors = result['new_attempts'][0]['is_negative']
                
            message = f'''
            The task has been verified:
            Title: {result['new_attempts'][0]['lesson_title']}
            Errors: {errors}
            URL: https://dvmn.org/{result['new_attempts'][0]['lesson_url']}
            '''
                
            bot.send_message(chat_id=TG_CHAT_ID, text=message)
                            
            if errors:
                message = 'You have to work harder!!!'
                bot.send_message(chat_id=TG_CHAT_ID, text=message)
                continue
                
            message = 'Congratulations! It is time to take on a new task'
            bot.send_message(chat_id=TG_CHAT_ID, text=message)

        except ReadTimeout as err:
            print(err)
        except ConnectionError as err:
            print(err)
