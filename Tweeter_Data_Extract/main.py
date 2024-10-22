from twikit import Client, TooManyRequests
import time
from datetime import datetime
import csv
from configparser import ConfigParser
import asyncio  # Importer asyncio pour gérer les coroutines
from random import randint


# Configuration des tweets minimum et de la requête
MINIMUM_TWEETS = 10
# Requête pour les mots-clés
#QUERY = '"UVBF" OR "UV-BF" OR "Université Virtuelle du Burkina Faso"'  # Recherche les tweets contenant l'un des trois termes
QUERY = '(Université UVBF OR UVBF OR #UVBF OR "Université Virtuelle du Burkina Faso" OR "UV-BF" OR "UV BF" OR "UV_BF") lang:fr'

tweet_count = 0
tweets = None

def get_tweets():
    global tweets  # Déclarer tweets comme global pour le modifier
    if tweets is None: 
        print(f'{datetime.now()} - Getting tweets ...')
        tweets =  client.search_tweet(QUERY, product='Latest')
    else: 
        wait_time = randint(5,10)
        print(f"{datetime.now()} - Getting next tweets after {wait_time} seconds ...")
        tweets =  tweets.next()
        time.sleep(wait_time)

    return tweets

# * Informations d'identification
config = ConfigParser()
config.read('config.ini')
username = config['X']['username']
email = config['X']['email']
password = config['X']['password']

# Créer un fichier CSV
with open('tweets.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Tweet_count', 'Username', 'Text', 'Create_At', 'Retweets', 'Likes'])

# * Authentification sur X.com 
client = Client(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36", language='en-US')

# Fonction asynchrone pour gérer l'authentification
async def authenticate():
    global tweet_count  # Déclarer tweet_count comme global pour le modifier
    global tweets  # Déclarer tweets comme global pour le modifier
    await client.login(auth_info_1=email, auth_info_2=username, password=password)  # Attendre la connexion
    client.save_cookies('cookies.json')  # Enregistrer les cookies après la connexion
    
    #! get tweets
    try:
        while tweet_count < MINIMUM_TWEETS:

            try:
                tweets = await get_tweets()
            except TooManyRequests as e:
                rate_limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
                print(f"{datetime.now()} - Rate limit Reached . Waiting until {rate_limit_reset}")
                wait_time = rate_limit_reset - datetime.now()
                time.sleep(wait_time.total_seconds())
                continue

            
            if not tweets:
                print(f'{datetime.now()} - No more tweets getting')
                break

            for tweet in tweets:
                tweet_count += 1
                tweet_data = [tweet_count, tweet.user.name, tweet.text, tweet.created_at, tweet.retweet_count, tweet.favorite_count]
                with open('tweets.csv', 'a', newline='') as file:
                    writer = csv.writer(file) 
                    writer.writerow(tweet_data)   

            print(f'{datetime.now()} - Got {tweet_count} tweets')      
        print(f'{datetime.now()} - Done ! Got {tweet_count} tweets found')
    except asyncio.TimeoutError:
        print("La connexion a dépassé le délai d'attente.")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")

# Exécuter la fonction d'authentification
asyncio.run(authenticate())  # Utiliser asyncio.run pour exécuter la coroutine
