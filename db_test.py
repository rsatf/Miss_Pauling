from tortoise import Tortoise, run_async
import models

async def create_players():
    await Tortoise.init(
        db_url='sqlite://pauling.db',
        modules={'models': ['models']}
    )
    await models.PlayersModel.create(steam_id="123abc", nick='Russ')

async def list_players():
    await Tortoise.init(
        db_url='sqlite://pauling.db',
        modules={'models': ['models']}
    )
    player = await models.PlayersModel.filter(nick__contains='us').first()
    print(player.steam_id)

if __name__ == '__main__':
    run_async(list_players())