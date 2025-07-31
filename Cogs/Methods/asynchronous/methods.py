import requests, json
from resources.links import warm
from resources.dictionaries import headers
from datetime import datetime

async def crash(error):
    try:
        data = {
            "embeds": [
                {
                    "title": "BOT ERROR!",
                    "description": str(error)[:1024],
                    "color": 0x9B59B6,
                    "thumbnail": {
                        "url": warm,
                    },
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        res = requests.post(
            "https://discord.com/api/webhooks/1399754937491128420/krs4046qAiczly-uy8XAzJN2o5ADaFnZLjklXig6msVui7_I92sl_fafzelbk2xD9Qkj",
            data=json.dumps(data), headers=headers)
        print(f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [INFO    ] {res.status_code}: Error message sent successfully.")
    except Exception as e:
        raise Exception(f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [ERROR    ] Failed to send error message: {e}")
    raise Exception(f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [ERROR    ] Fatal error occurred: {error}")