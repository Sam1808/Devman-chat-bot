
import requests
from environs import Env





if __name__ == "__main__":
    
    env = Env()
    env.read_env()  # read .env file

    TOKEN = env.str("TOKEN")

    headers = {
        'Authorization': f'Token {TOKEN}'
    }

    tasks_url = 'https://dvmn.org/api/user_reviews/'
    polling_url = 'https://dvmn.org/api/long_polling/'
    
    respond = requests.get(polling_url,headers = headers) 

    print(respond.json())
