import requests
from dotenv import load_dotenv
import os
load_dotenv()

def send_message(number:str, message:str):
    """Enviar menssagem no whatsapp
    Args:
        number: numero de telefone 
        message: menssagem para enviar
    
    """
    url = "http://127.0.0.1:8080/message/sendText/Madu"

    payload = {
        "number": number,
        "textMessage": { "text": message },

    }
    headers = {
        "apikey": os.getenv("AUTHENTICATION_API_KEY"),
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)

