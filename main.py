 
from fastapi import FastAPI, Request
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up app
app = FastAPI()

# Load credentials from environment
OANDA_API_KEY = os.getenv("OANDA_API_KEY")
OANDA_ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")
OANDA_URL = os.getenv("OANDA_URL", "https://api-fxpractice.oanda.com/v3")

HEADERS = {
    "Authorization": f"Bearer {OANDA_API_KEY}",
    "Content-Type": "application/json"
}

@app.post("/webhook")
async def webhook(request: Request):
    try:
        # Parse TradingView webhook JSON
        data = await request.json()
        print("🔔 Webhook received:", data)

        action = data.get("action")
        ticker = data.get("ticker", "")
        instrument = ticker.replace("/", "_").upper()  # Convert to OANDA format
        price = float(data.get("price"))
        sl = float(data.get("sl"))
        tp = float(data.get("tp"))

        # Validate action
        if action not in ["buy", "sell"]:
            return {"status": "error", "message": "Invalid action"}

        # Choose units (hardcoded 100 for now)
        units = "100" if action == "buy" else "-100"

        # Build the order payload
        order_payload = {
            "order": {
                "units": units,
                "instrument": instrument,
                "type": "MARKET",
                "positionFill": "DEFAULT",
                "takeProfitOnFill": {"price": f"{tp:.5f}"},
                "stopLossOnFill": {"price": f"{sl:.5f}"}
            }
        }

        # Send the order to OANDA
        response = requests.post(
            f"{OANDA_URL}/accounts/{OANDA_ACCOUNT_ID}/orders",
            headers=HEADERS,
            json=order_payload
        )

        print("📤 OANDA response:", response.status_code, response.text)
        return {
            "status": "success",
            "request": data,
            "oanda_response": response.json()
        }

    except Exception as e:
        print("❌ Error:", str(e))
        return {"status": "error", "message": str(e)}
