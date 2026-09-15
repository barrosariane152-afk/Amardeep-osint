import requests
import json
import time


# ==============================
# Configuration
# ==============================

BOT_TOKEN = "8970185697:AAEBT6ymuLMJb7vxL37mYbCy097DcV13qhg"
EXTERNAL_API_URL = "https://dark-info.site/test/api.php?key=JSON-0018&num=918448379473"

# Dummy HTTPS server URL for testing.
# Replace with your authorized API endpoint when needed.
DUMMY_HTTPS_SERVER = "https://example.com/api"


TELEGRAM_API = "https://api.telegram.org/bot" + BOT_TOKEN


# ==============================
# Telegram API functions
# ==============================

def get_updates(offset=None):
    url = TELEGRAM_API + "/getUpdates"

    params = {
        "timeout": 30
    }

    if offset is not None:
        params["offset"] = offset

    try:
        response = requests.get(
            url,
            params=params,
            timeout=35
        )

        response.raise_for_status()
        return response.json()

    except requests.RequestException as error:
        print("Telegram connection error:", error)
        return None

    except json.JSONDecodeError:
        print("Invalid JSON received from Telegram.")
        return None


def send_message(chat_id, text, reply_markup=None):
    url = TELEGRAM_API + "/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup is not None:
        data["reply_markup"] = json.dumps(reply_markup)

    try:
        response = requests.post(
            url,
            data=data,
            timeout=15
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:
        print("Message sending error:", error)
        return None

    except json.JSONDecodeError:
        print("Invalid JSON received while sending message.")
        return None


# ==============================
# Reply keyboard
# ==============================

def phone_keyboard():
    return {
        "keyboard": [
            [
                {
                    "text": "📱 Phone Lookup"
                }
            ]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }


# ==============================
# External API
# ==============================

def phone_lookup(phone_number):
    if not EXTERNAL_API_URL:
        return {
            "error": "External API URL is not configured.",
            "phone": phone_number
        }

    try:
        response = requests.get(
            EXTERNAL_API_URL,
            params={
                "phone": phone_number
            },
            timeout=15
        )

        response.raise_for_status()

        # Convert API response into JSON
        return response.json()

    except requests.RequestException as error:
        return {
            "error": "External API request failed.",
            "details": str(error)
        }

    except json.JSONDecodeError:
        return {
            "error": "External API did not return valid JSON."
        }


# ==============================
# Main bot
# ==============================

def main():
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN is empty.")
        print("Add your Telegram bot token to BOT_TOKEN.")
        return

    print("Bot started.")
    print("Waiting for messages...")

    offset = None

    while True:
        updates = get_updates(offset)

        if updates is None:
            time.sleep(3)
            continue

        if not updates.get("ok"):
            print("Telegram API returned an error:")
            print(updates)
            time.sleep(3)
            continue

        for update in updates.get("result", []):

            # Move offset forward so the same update is not processed again
            offset = update["update_id"] + 1

            message = update.get("message")

            if not message:
                continue

            chat = message.get("chat")

            if not chat:
                continue

            chat_id = chat.get("id")
            text = message.get("text", "").strip()
