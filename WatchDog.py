import json
import asyncio
import logging
from telethon.sync import TelegramClient, events, types
import requests

from email.message import EmailMessage
import smtplib

# Configuration Section
filter_keywords_map = {
    ('NVTC', 'edu.bh', 'Bahrain', ' bh ','BH','BH','bh','bd','bahrain','BAPCO','Batelco','BATELCO','BSTRLC0','batelc0','Bahrain', 'ka47eogPqmU=',' 1goc9aTK3mQ=',' xTfAzIbl5XM=',' +PQYN2vZr3o=',' tlcWXvAcQtY=',' tlcWXvAcQtY=',' +dPmKkM1eOUpJQhFzY6bRQ==',' KXxxSRtgpNFs7tRmkl1gtQ==',' whtIiQRxhkQ=',' xTQn0PsxfxI=','R4pBYxkDUjg=', '30zfrexaTeE=',' VdKMX8vwSDI=', 'fBt6hty1wy4=',' 2uHHGFGbmW4=', 'bSG7m6KLSdA=', 'kS9qneHEx2w=', 'Trij31BBWt0=', 'mtPJOQKqbcQ=',' MVXnwc1fL1Y=',' hjFY21yfGlKILnrFKiPOqQ==', '0oiGIE7e8jvYtDIN5vV6+g==', 'Ss0g6ik95+xSsUV/iBJpUQ==', 'CLjVFSG5Ru0=', 'pCUcfDy6z+U=', 'VZYT+CD1dPM=', 'Wewcq24N+4Q=', 'S+3+nqSURbQ=', '3J077JNbAHk=', '54MK/yWe+Oo=','NVTC','N V T C','nvtc','n v t c ','nasser school','NASSER SCHOOL','Nasser School','nasser vocational training center','NasserVocationlTrainingCenter','nasservocationaltrainingcenter','nasser_vocational_training_center','nasser-vocational-training-center','nasser0vocational0training0center', '/Zima0M3XXY=','uVWGdqvkV2I=','kuw7yWA6l+w=','UqDyrK8qPIo=','uZKtbRRegIjPOhM/q+vt9A==','2iXn27dlH6zmiidY9cTIEA==','C4IFsayv0QbPOhM/q+vt9A==','xf/0j5+LCpagrS03dP2uf/DNxhTUv3v+lrOatino80A=','lOSVS/2JynXYJb2wDla5MegrK4o4sVHVFKgIapupTBU=','p5EJvZpj83O4ZFrI8b14ubACOURyjVgQBIzwLaoPBEE=','EGy/qQE18vKgrS03dP2ufwKQwekObS5aj2fJyGUJG4hgPeGHOEucCQ==','q0kJMgQk/iKgrS03dP2uf6Z+7xoYZ6upqR9BoN2JJCNgPeGHOEucCQ==','+t5GYn6P0LCgrS03dP2ufxBuNCNP00KpRA2IFyuPlVRgPeGHOEucCQ==', 'ZP4bKgKLC6g=', 'GPpEaLlj00I=', 'wzoyQlUmPv4=', 'yDjNCn1KO1A=', '0KUVWA+ZDM3D8E1GiPMHGA==', 'MUczDlqgaunNDW92xPadeQ==', 'NrOdTDLFKkfD8E1GiPMHGA==l', 'r1SFuM7o5zDjRnw7aazvEGCEOPxRFuj79iq6r8M8I40=','fXWx+Ua+17jkElu6VffTJ1iBphSf6W+xdJJbTqRvuNw=', 'ZmtAxmQcxgHkElu6VffTJ3N8PHY2r185Qle8uC7SEwoNms1YSPk+kg=='): "https://discord.com/api/webhooks/1219916425892855860/lIZRIkXjWo9zsqqQzZhWrZg96qCuJx0CQU4kHpQe_iewf0q6b7TJsIgLufI-l0jT3z6V",
    ('security', 'hack', 'DDoS'): "https://discord.com/api/webhooks/1221755359346294884/winmiZlXwXiWj-3GjWFMROCb-R4sESFfwn31ueCKbOKZXXu9W0Br0c94JOMNRVQIVYxB"
}

# Telegram configuration
api_id = ''
api_hash = ''
channels = ['sysadm_in_channel','thehackernews','mb_cyber','mrkhalidtest']

# Logging configuration
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a Telegram client instance
client = TelegramClient('anon', api_id, api_hash)

# Asynchronous function to send a message to Discord using a webhook
async def send_discord_message(text, webhook_url):
    headers = {'Content-Type': 'application/json'}
    payload = {"content": text}
    try:
        response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        logger.info(f"Message sent successfully to Discord")
    except requests.RequestException as e:
        logger.error(f"Error sending message to Discord: {e}")

# Main asynchronous function
async def main():
    try:
        await client.start()

        #######################
        # Fetch all channels the user is subscribed to
        dialogs = await client.get_dialogs()
        #Filter channels
        channel_entities = [dialog.entity for dialog in dialogs if isinstance(dialog.entity, types.Channel)]
        #######################

        #######################
        #the below was used for manual channel list
        #channel_entities = await asyncio.gather(*(client.get_entity(c) for c in channels))
        #######################

    except Exception as e:
        logger.error(f"Error fetching channel information: {e}")
        return

    @client.on(events.NewMessage(chats=channel_entities))
    async def my_event_handler(event):
        try:
            sender = await event.get_sender()
            channel = await event.get_chat()
            message = event.raw_text

            alert_text = f"Telegram Alert\nChannel: {channel.title}\nUser: {sender.username}\nMessage: {message}"
            logger.info(f"Message received from {sender.username} in {channel.title}: {message}")

            for keywords, webhook_url in filter_keywords_map.items():
                if any(keyword.lower() in message.lower() for keyword in keywords):
                    await send_discord_message(alert_text, webhook_url)
                    logger.info("Message sent to Discord")
                    break # Stop checking other keyword lists once a match is found

        except asyncio.CancelledError:
            logger.warning("Event handler cancelled")
        except ValueError as ve:
            logger.error(f"ValueError: {ve}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    try:
        await client.run_until_disconnected()
    except Exception as e:
        logger.error(f"Error running Telegram client: {e}")

# Execute the main asynchronous function
asyncio.run(main())