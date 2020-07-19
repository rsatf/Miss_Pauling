import asyncio
import aiohttp
import json

class Match():

    def __init__(self, log_id: int) -> None:
        self.log_id = log_id

    async def get_match(self) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://logs.tf/json/' + str(self.log_id)) as resp:
                return json.loads(await resp.text())

class Uploads():

    def __init__(self, uploader_id: int) -> None:
        self.uploader_id = uploader_id

    async def get_uploads(self, limit: int=1000) -> list:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://logs.tf/api/v1/log?limit=' + str(limit) + '&uploader=' + str(self.uploader_id)) as resp:
                d = json.loads(await resp.text())
                logs = []
                for log in d['logs']:
                    logs.append(log['id'])
                # reverse the order so the oldest game is first in the list
                return list(reversed(logs))

if __name__ == '__main__':
    data = asyncio.run(Uploads(76561198003234706).get_uploads())
    print(data)
    data = asyncio.run(Match(2614815).get_match())
    print(data)