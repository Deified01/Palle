from flask import Flask
import base64
import os
import re
import time
from telethon import TelegramClient, events, types
from telethon.sessions import StringSession
from pymongo import MongoClient
import nest_asyncio
import logging
import uvloop

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Telegram API credentials
api_id = 8447214
api_hash = '9ec5782ddd935f7e2763e5e49a590c0d'
string_session = "1BVtsOIQBu4fptwJ-g1-1cdl38_94JtPiDQ8SplOGHFt5mIY5T-yzJZUOoc1odu6k2XPaXe4_B0pmWPIrxAEpkWtGsusQeTyUzckSPa9m-_Z7ApAm5jK0Ee_-dNoeaSjfrRuLVDvlHCmQl8-Rdi_CeFb4DbL4bkPQhX6GNplBi7XA8cGSKPN9bmITsowryES9NqGk2YiljO_4xD3xkvIMVDE-s4DZ8ZC-dVpEifNkB9zepg_bDapu-10nmNrQ7IFLR9PGoh8YAWsJTZYgSe4P4JjDAxWHO1aurCCwfjDYqKnTcTl6442or7PsHX6eZxiqlOFBN3nSzoH7GhC0dDitECs5wUwjFQU="

# MongoDB credentials
mongo_uri = "mongodb+srv://xmon77:fF5ew07G0pll9YI3@cluster0.1travym.mongodb.net/?retryWrites=true&w=majority"

# Initialize Telegram client
client = TelegramClient(StringSession(string_session), api_id, api_hash)

# Initialize MongoDB client and create index on base64_media field
mongo_client = MongoClient(mongo_uri)
db = mongo_client.telegram_data
collection = db.media_data
collection.create_index("base64_media")

def alphanumeric(text):
    return re.sub(r'[^a-zA-Z0-9]', '', text)

def encode_to_base64(file_path):
    with open(file_path, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode('utf-8')
    return encoded_string

def find_matching_document(encoded_media):
    start_time = time.time()
    document = collection.find_one({"base64_media": encoded_media})
    end_time = time.time()
    time_taken = end_time - start_time
    if document:
        return document.get('character_name'), time_taken
    return None, None

async def main():
    await client.start()
    print("Client is running...")

    @client.on(events.NewMessage(chats='lustsupport'))
    async def handler(event):
        try:
            message_text = alphanumeric(event.message.message)
            print(message_text)
            if message_text == "Whoisthisslave":
                media_path = await event.message.download_media()
                encoded_media = encode_to_base64(media_path)
                character_name, time_taken = find_matching_document(encoded_media)
                os.remove(media_path)  # Clean up the downloaded file
                if character_name:
                    parts = character_name.split()
                    shortest_part = min(parts, key=len)
                    logging.info(f"Character found: {shortest_part}")
                    await event.client.send_message(event.chat_id, shortest_part)
        except Exception as e:
            logging.error(f"Error processing message: {e}")
            await event.client.send_message(event.chat_id, "Sorry, an error occurred while processing your request.")

    await client.run_until_disconnected()

import asyncio


app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return 'Hello, World'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(main())
