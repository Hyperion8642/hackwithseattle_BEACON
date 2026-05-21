import asyncio
from rocketride import RocketRideClient
from rocketride.schema import Question
import os
from dotenv import load_dotenv

load_dotenv("../.env")

async def test():
    async with RocketRideClient() as client:
        await client.connect()
        res = await client.use(filepath='pipelines/beacon_dispatch.pipe')
        tok = res['token']
        q = Question(expectJson=True)
        q.addQuestion(f"DRIVER REPORT: hey a passenger fainted")
        rr_response = await client.chat(token=tok, question=q)
        print(rr_response)

asyncio.run(test())
