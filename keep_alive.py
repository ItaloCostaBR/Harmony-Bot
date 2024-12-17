import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("URL")

def keep_alive():
    while True:
        try:
            response = requests.get(URL)
            print(f"Ping enviado! Status: {response.status_code}")
        except Exception as e:
            print(f"Erro ao enviar ping: {e}")
        time.sleep(45)

if __name__ == "__main__":
    print("Starting Keep Alive...")
    keep_alive()
