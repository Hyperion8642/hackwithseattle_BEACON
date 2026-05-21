from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

# Ensure we can import agent1
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from agent1.agent1 import process_query, QueryRequest

app = FastAPI(title="RocketRide Orchestration Bus")

# Incoming payload from TS gateway
class IncidentPayload(BaseModel):
    incidentId: str
    driverId: str
    rawText: str
    simulatedLocation: str
    mediaUrls: Optional[List[str]] = []
    timestamp: str

@app.post("/dispatch")
async def dispatch_incident(payload: IncidentPayload):
    print(f"🚀 RocketRide received incident: {payload.incidentId} from {payload.driverId}")
    
    # 1. Orchestrate Agent 1 (Protocol Specialist)
    agent1_req = QueryRequest(
        driver_text=payload.rawText,
        gps=payload.simulatedLocation,
        operator_id=payload.driverId,
        coach_id="UNKNOWN" # Could be extracted later
    )
    
    try:
        agent1_resp = process_query(agent1_req)
    except Exception as e:
        print(f"Error in Agent 1: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
    # In the future, Agent 2 (Logistics Allocator) and Agent 3 (Copywriter) would be orchestrated here
    
    # Construct final ActionableResponse for the Gateway
    immediate_steps = agent1_resp.legal_reminders
    if not immediate_steps:
        immediate_steps = ["Follow standard safety protocols.", "Await further instructions."]
        
    action_taken = agent1_resp.tool_executed.get("action_taken", "Incident logged.")
        
    final_plan = {
        "summary": f"Categorized as: {agent1_resp.incident_category.replace('_', ' ').upper()}.\nAction: {action_taken}",
        "immediateSteps": immediate_steps,
        "eta": "10-15 minutes (Agent 2 Stub)",
        "protocolContext": agent1_resp.protocol_context
    }
    
    print(f"✅ RocketRide finalized plan for {payload.incidentId}")
    return final_plan

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5565)
