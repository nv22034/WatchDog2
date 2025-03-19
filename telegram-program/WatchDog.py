import json
import asyncio
import logging
from telethon.sync import TelegramClient, events, types
import requests
from transformers import pipeline  # Hugging Face's pre-trained model
import torch

# Load settings from config.json
def load_config():
    with open("config.json", "r") as file:
        return json.load(file)

config = load_config()

# Telegram configuration
api_id = config["api_id"]
api_hash = config["api_hash"]
channels = config["channels"]

# Logging configuration
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a Telegram client instance
client = TelegramClient('anon', api_id, api_hash)

# Load the pre-trained model for offensive language detection
model_name = "distilbert-base-uncased"  # A smaller version of BERT
classifier = pipeline("text-classification", model=model_name, tokenizer=model_name)

# Function to send a message to Discord using a webhook
async def send_discord_message(text, webhook_url):
    headers = {'Content-Type': 'application/json'}
    payload = {"content": text}
    try:
        response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        logger.info("Message sent successfully to Discord")
    except requests.RequestException as e:
        logger.error(f"Error sending message to Discord: {e}")

# Function to classify the message using the ML model
def classify_message(message):
    result = classifier(message)
    label = result[0]['label']
    return label

# Main asynchronous function
async def main():
    try:
        await client.start()
        dialogs = await client.get_dialogs()
        channel_entities = [dialog.entity for dialog in dialogs if isinstance(dialog.entity, types.Channel)]
    except Exception as e:
        logger.error(f"Error fetching channel information: {e}")
        return

    @client.on(events.NewMessage(chats=channel_entities))
    async def my_event_handler(event):
        try:
            sender = await event.get_sender()
            channel = await event.get_chat()
            message = event.raw_text.lower()

            alert_text = f"Telegram Alert\nChannel: {channel.title}\nUser: {sender.username}\nMessage: {message}"
            logger.info(f"Message received from {sender.username} in {channel.title}: {message}")

            # Classify the message using the ML model
            label = classify_message(message)
            logger.info(f"Message classification result: {label}")

            # Check for offensive language
            if label == "LABEL_1":  # Assuming "LABEL_1" represents offensive language (depends on the model's output)
                # Send alert
                webhook_url = config["webhooks"].get("red", "")
                if webhook_url:
                    alert_text += f"\nRisk Alert: Offensive Language"
                    await send_discord_message(alert_text, webhook_url)
                    logger.info(f"Offensive language alert sent to Discord")

            # Check for other alerts based on keywords
            for risk_level, keywords in config["filter_keywords"].items():
                if any(keyword.lower() in message for keyword in keywords):
                    webhook_url = config["webhooks"].get(risk_level, "")
                    if webhook_url:
                        alert_text += f"\nRisk Alert: {risk_level}"
                        await send_discord_message(alert_text, webhook_url)
                        logger.info(f"{risk_level.capitalize()} alert message sent to Discord")

        except asyncio.CancelledError:
            logger.warning("Event handler cancelled")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    try:
        await client.run_until_disconnected()
    except Exception as e:
        logger.error(f"Error running Telegram client: {e}")

# Execute the main asynchronous function
asyncio.run(main())