import asyncio
import aiohttp
from starwars_hw.db import write_characters, init_db, engine


sem = asyncio.Semaphore(10)

async def fetch_character(session, i):
    async with sem:
        async with session.get(f"https://www.swapi.tech/api/people/{i}") as response:
            if response.status != 200:
                return None
            print(response.status)
            return await response.json()

async def check_records(session: aiohttp.ClientSession)-> int:
    async with session.get("https://www.swapi.tech/api/people") as response:
        print("status:", response.status)
        data = await response.json()

        total_records = data["total_records"]
        print("total records:", total_records)
        return total_records

async def write_records(session: aiohttp.ClientSession, total_records: int):
    records = await asyncio.gather(
        *(fetch_character(session, i) for i in range(1, total_records + 1))
    )
    await write_characters(records)

async def main():
    await init_db(engine)

    session = aiohttp.ClientSession()
    print('session created')
    total_records = await check_records(session)
    await write_records(session, total_records)
    print("records written")

if __name__ == '__main__':
    asyncio.run(main())
