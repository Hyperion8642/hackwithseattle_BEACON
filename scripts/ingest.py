import asyncio
import sys

from rocketride import RocketRideClient


async def ingest(files: list[str]) -> None:
    async with RocketRideClient() as client:
        result = await client.use(filepath="pipelines/ingestion.pipe", use_existing=True)
        token = result["token"]
        print(f"PDF pipeline ready — token: {token}")

        file_list = [(p, {"source": "transit_manual"}) for p in files]
        results = await client.send_files(file_list, token)

        for r in results:
            if r["action"] == "complete":
                print(f"✓  {r['filepath']}  ({r['upload_time']:.2f}s)")
            else:
                print(f"✗  {r['filepath']}  — {r.get('error', 'unknown error')}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/ingest.py data/the_book.pdf")
        sys.exit(1)
    asyncio.run(ingest(sys.argv[1:]))
