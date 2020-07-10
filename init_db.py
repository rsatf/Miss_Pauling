from tortoise import Tortoise, fields, run_async
from tortoise.exceptions import OperationalError
from tortoise.models import Model
import models



async def init():
    await Tortoise.init(
        db_url='sqlite://pauling.db',
        modules={'models': ['models']}
    )
    await Tortoise.generate_schemas()

if __name__ == '__main__':
    run_async(init())