import json
import asyncio
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from telethon.sync import TelegramClient, events, types
import requests

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

# Function to send email alert
def send_email(subject, body, recipient_email):
    sender_email = "your_email@gmail.com"  # Your Gmail address
    sender_password = "your_password"  # Your Gmail app password or password (if you have 2FA enabled, use an app password)

    # Set up the email server
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)

        # Prepare the email content
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()

        logger.info("Email sent successfully!")
    except Exception as e:
        logger.error(f"Error sending email: {e}")

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

            # Check for alerts
            for risk_level, keywords in config["filter_keywords"].items():
                if any(keyword.lower() in message for keyword in keywords):
                    webhook_url = config["webhooks"].get(risk_level, "")
                    if webhook_url:
                        alert_text += f"\nRisk Alert: {risk_level}"
                        await send_discord_message(alert_text, webhook_url)
                        logger.info(f"{risk_level.capitalize()} alert message sent to Discord")

                        # Send an email alert
                        subject = f"Suspicious Message Detected: {risk_level.capitalize()}"
                        body = f"Message from {sender.username} in {channel.title}:\n{message}\n\n{alert_text}"
                        # Get email recipient from config.json
                        recipient_email = config["email_recipient"]

                        send_email(subject, body, recipient_email)
                    break  # Stop checking after a match is found

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