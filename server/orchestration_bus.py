import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from rag_agent import ask_rag

app = FastAPI(title="RocketRide Orchestration Bus")


class IncidentPayload(BaseModel):
    incidentId: str
    driverId: str
    rawText: str
    simulatedLocation: str
    mediaUrls: Optional[List[str]] = []
    timestamp: str


@app.post("/dispatch")
async def dispatch_incident(payload: IncidentPayload):
    print(f"🚀 Orchestration bus received: {payload.incidentId} from {payload.driverId}")

    try:
        full_response = await ask_rag(payload.rawText)
    except Exception as e:
        print(f"❌ RAG pipeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    print(f"✅ RAG answer ready for {payload.incidentId}")
    return {
        "summary": full_response,
        "immediateSteps": [],
        "eta": None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5565)
