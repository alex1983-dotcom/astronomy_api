import asyncio
import asyncpg

async def test():
    conn = await asyncpg.connect(
        user='omega',
        password='tango52echo23',
        database='astronomy_db',
        host='localhost'
    )
    print("✅ Подключение успешно!")
    await conn.close()

asyncio.run(test())