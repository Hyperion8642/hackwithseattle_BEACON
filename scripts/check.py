import asyncio
import os
import re
import subprocess
from pathlib import Path

from rocketride import RocketRideClient


def detect_rocketride_port() -> int | None:
    """Find the IPv4 port the RocketRide engine is currently listening on."""
    try:
        out = subprocess.check_output(["lsof", "-i", "-P", "-n"], text=True)
    except Exception:
        return None
    for line in out.splitlines():
        if "engine" in line and "LISTEN" in line and "127.0.0.1" in line:
            m = re.search(r"127\.0\.0\.1:(\d+)", line)
            if m:
                return int(m.group(1))
    return None


def sync_env_port(port: int) -> None:
    """Rewrite ROCKETRIDE_URI in .env to match the running engine port."""
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        return
    text = env_path.read_text()
    updated = re.sub(
        r"^(ROCKETRIDE_URI=http://localhost:)\d+",
        rf"\g<1>{port}",
        text,
        flags=re.MULTILINE,
    )
    if updated != text:
        env_path.write_text(updated)
        print(f"  .env updated → ROCKETRIDE_URI=http://localhost:{port}")
    os.environ["ROCKETRIDE_URI"] = f"http://localhost:{port}"


async def check() -> None:
    print("Checking BEACON system connectivity...\n")

    port = detect_rocketride_port()
    if port:
        print(f"  Detected RocketRide engine on port {port}")
        sync_env_port(port)
    else:
        print("  WARNING: Could not detect running engine — using URI from .env")

    async with RocketRideClient() as client:
        await client.ping()
        print("✓  RocketRide server reachable")

        result = await client.use(filepath="pipelines/ingestion.pipe", use_existing=True)
        print(f"✓  ingestion.pipe started  token={result['token']}")

        result = await client.use(filepath="pipelines/rag_search.pipe", use_existing=True)
        print(f"✓  rag_search.pipe started token={result['token']}")

    print("\nAll checks passed. BEACON is ready.")


if __name__ == "__main__":
    asyncio.run(check())
