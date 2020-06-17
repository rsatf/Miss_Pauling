import aiosqlite

async with aiosqlite.connect(./bot.sqlite3) as db:
    await db.execute("INSERT INTO some_table ...")
        await db.commit()

        async with db.execute("SELECT * FROM some_table") as cursor:
            async for row in cursor: