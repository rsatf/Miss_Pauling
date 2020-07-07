import asyncio
import aiohttp
import json
from tortoise import Tortoise, run_async
from tortoise.exceptions import IntegrityError
import models
import datetime

async def get_uploads(uploader_id: int):
    async with aiohttp.ClientSession() as session:
        async with session.get('http://logs.tf/api/v1/log?uploader=' + str(uploader_id)) as resp:
            d = json.loads(await resp.text())
            for log in d['logs']:
                await store_game(log['id'])

async def get_game(game_id: int):
    async with aiohttp.ClientSession() as session:
        async with session.get('http://logs.tf/json/' + str(game_id)) as resp:
            d = json.loads(await resp.text())
            return d

async def store_game(game_id: int):
    await Tortoise.init(
        db_url='sqlite://pauling.db',
        modules={'models': ['models']}
    )
    data = await get_game(game_id)
    print(f'ID: {game_id}')
    game_map = data['info']['map']
    print(f'Map: {game_map}')
    game_date = data['info']['date']
    game_date = datetime.datetime.fromtimestamp(game_date, tz=None).isoformat()
    print(f'Date: {game_date}')
    game_title = data['info']['title']
    print(f'Title: {game_title}')
    game_data = data
    try:
        await models.GameModel.create(game_id=game_id, game_map=game_map, game_date=game_date, game_title=game_title, game_data=game_data)
    except IntegrityError:
        print("Game already added to DB")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    run_async(get_uploads(76561198003234706))