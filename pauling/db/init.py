from tortoise import Tortoise, fields, run_async
from tortoise.exceptions import OperationalError

async def init():
    print('making db pauling.db')
    await Tortoise.init(
        db_url='sqlite://../pauling.db',
        modules={'models': ['pauling.db.models']}
    )
    await Tortoise.generate_schemas()
    print('made db pauling.db')

if __name__ == '__main__':
    run_async(init())