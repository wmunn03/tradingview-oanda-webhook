from fastapi import FastAPI, Request
from pydantic import BaseModel
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

OANDA_API_KEY = os.getenv("OANDA_API_KEY")
OANDA_ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")
OANDA_URL = os.getenv("OANDA_URL")

HEADERS = {
    "Authorization": f"Bearer {OANDA_API_KEY}",
    "Content-Type": "application/json"
}

class AlertData(BaseModel):
    action: str
    ticker: str
    price: float
    sl: float
    tp: float

@app.post("/webhook")
async def webhook(alert: AlertData):
    print(f"🔔 Webhook received: {alert.dict()}")

    instrument = alert.ticker.replace("/", "_")
    units = "100" if alert.action == "buy" else "-100"

    tp_distance = round(abs(alert.tp - alert.price), 5)
    sl_distance = round(abs(alert.price - alert.sl), 5)

    order_data = {
        "order": {
            "instrument": instrument,
            "units": units,
            "type": "MARKET",
            "positionFill": "DEFAULT",
            "timeInForce": "FOK",
            "takeProfitOnFill": {
                "distance": str(tp_distance)
            },
            "stopLossOnFill": {
                "distance": str(sl_distance)
            }
        }
    }

    print(f"📦 Sending order to OANDA:\n{order_data}")

    response = requests.post(
        f"{OANDA_URL}/accounts/{OANDA_ACCOUNT_ID}/orders",
        headers=HEADERS,
        json=order_data
    )

    print(f"📤 OANDA response: {response.status_code} {response.text}")
    return {"status": "success", "oanda_response": response.json()}

