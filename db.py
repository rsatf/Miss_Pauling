import asyncio
import json
from tortoise import Tortoise, run_async
from tortoise.exceptions import IntegrityError
import models
import datetime
from logstf import Match, Uploads

class DataHandler():

    def __init__(self):
        pass

    async def db_store_match(self, game_data: dict):
        pass

    async def db_store_player_stats(self, player_data: dict):
        pass

    async def db_get_match(self, game_id: int) -> list:
        await Tortoise.init(
            db_url='sqlite://pauling.db',
            modules={'models': ['models']}
        )
        try:
            data = await models.LogstfData.filter(game_id=game_id)
        finally:
            await Tortoise.close_connections()
        return data

    async def logstf_get_match(self, game_id: int):
        game_data = await Match(game_id).db_get_match()
        uploader_id = game_data['info']['uploader']['id']
        game_map = game_data['info']['map']
        game_date = datetime.datetime.fromtimestamp(game_data['info']['date'], tz=None).isoformat()
        game_title = game_data['info']['title']
        await Tortoise.init(
            db_url='sqlite://pauling.db',
            modules={'models': ['models']}
        )
        try:
            await models.LogstfData.create(
                game_id=game_id,
                uploader_id=uploader_id,
                game_map=game_map,
                game_date=game_date,
                game_title=game_title,
                game_data=game_data)
            print(f'Added game {game_id}')
        except IntegrityError:
            print('Match already added to DB')
        finally:
            await Tortoise.close_connections()

if __name__ == '__main__':
    # all_uploads = asyncio.run(Uploads(76561198003234706).get_uploads())
    # for upload in all_uploads:
    #     game_data = asyncio.run(Match(upload).get_match())
    #     handler = DataHandler()
    #     asyncio.run(handler.logstf_get_match(upload))
    handler = DataHandler()
    asyncio.run(handler.db_get_match(2614815))