from telethon import TelegramClient
from telethon.events import NewMessage
# from telethon.errors import Error
from telethon.tl.functions.account import UpdateProfileRequest

from aiohttp import ClientSession
from configparser import ConfigParser
from datetime import datetime
from pytz import timezone
import asyncio

# parse config
config = ConfigParser()
config.read('config.ini')

# parse data from config
SESSION_NAME = config.get('telegram_client', 'session_name')
API_ID = config.getint('telegram_client', 'api_id')
API_HASH = config.get('telegram_client', 'api_hash')

WEATHER_API_KEY = config.get('openweathermap', 'api_key')

NAME = config.get('user', 'name')
CITY = config.get('user', 'city')
ABOUT = config.get('user', 'about')

# create client
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
client.connect()


# get current weather
async def get_current_weather():
    url = f'https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric'

    async with ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return data['main']['temp']


# get progress of the day
async def get_progress_of_the_day():
    now = datetime.now(timezone('Europe/Moscow'))
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    seconds = (now - midnight).seconds
    return round(seconds / 86400 * 100, 1)


# update weather in name and progress bar in about
async def update_user_profile():
    while True:
        current_weather = await get_current_weather()
        text_name = f'{NAME} | {current_weather} °C'

        progress_of_the_day = await get_progress_of_the_day()
        about_text = f"{ABOUT} // Day's progress: {progress_of_the_day}%"

        await client(UpdateProfileRequest(
            first_name=text_name,
            about=about_text
        ))

        await asyncio.sleep(5)


# hedgehog and apples
@client.on(NewMessage(pattern='🦔', outgoing=True))
async def hedgehog_handler(event: NewMessage.Event):
    for step in range(20, -1, -1):
        await client.edit_message(event.chat_id, event.message.id, '🍎' * step + '🦔')
        await asyncio.sleep(0.3)


# monkey
@client.on(NewMessage(pattern='🐵', outgoing=True))
async def monkey_handler(event: NewMessage.Event):
    for emoji in ('🙊', '🙈'):
        await client.edit_message(event.chat_id, event.message.id, emoji)
        await asyncio.sleep(3)


# entry point
if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(update_user_profile())
        client.run_until_disconnected()
