import requests
import time
import json
import os

# --- CONFIGURATION ---
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"
SYMBOL = "TCS.NS"  # Yahoo Finance symbol for TCS
TARGET_PRICE = 4000.0
BUFFER_PRICE = 3980.0  # Reset alert only when price drops below this
CHECK_INTERVAL = 300   # Check every 5 minutes (300 seconds)

def get_price(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        data = response.json()
        return data['chart']['result'][0]['meta']['regularMarketPrice']
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

def load_state():
    if os.path.exists("state.json"):
        with open("state.json", "r") as f:
            return json.load(f)
    return {"alert_sent": False}

def save_state(state):
    with open("state.json", "w") as f:
        json.dump(state, f)

def main():
    print(f"Starting monitor for {SYMBOL}...")
    state = load_state()

    while True:
        current_price = get_price(SYMBOL)
        
        if current_price:
            print(f"Current Price: {current_price}")

            # TRIGGER: Price goes above 4000
            if current_price >= TARGET_PRICE and not state["alert_sent"]:
                msg = f"🚀 ALERT: {SYMBOL} is at ₹{current_price}! (Above target ₹{TARGET_PRICE})"
                send_telegram(msg)
                state["alert_sent"] = True
                save_state(state)
                print("Alert sent and locked.")

            # RESET (Re-arm): Price drops below 3980
            elif current_price < BUFFER_PRICE and state["alert_sent"]:
                print("Price dropped below buffer. Re-arming alert...")
                state["alert_sent"] = False
                save_state(state)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
