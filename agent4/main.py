# main.py
from fastapi import FastAPI
import requests
import uvicorn

app = FastAPI()

def categorize_incident(driver_text: str) -> str:
    print(f"🚀 [AGENT 4] Sending data to RocketRide pipeline...")

    rocketride_webhook_url = "http://localhost:60219/webhook"

    try:
        headers = {
            "Authorization": "Bearer 66f9e63ce5d0eef21d1ef54296073483f8139eeb49780417f9883754be47de5d", 
            "Content-Type": "application/json"
        }

        response = requests.post(
            rocketride_webhook_url,
            # Matched "text" to the {{text}} variable in your Prompt node
            json={"text": driver_text}, 
            headers=headers,
            timeout=15
        )
        response.raise_for_status()
        
        data = response.json()
        category = data.get("category", "OTHER") 
        print(f"✅ [ROCKETRIDE] Returned category: {category}")
        return category
        
    except requests.exceptions.HTTPError as e:
        print(f"⚠️ [AGENT 4] RocketRide HTTP Error: {e}")
        # This will print the EXACT reason RocketRide rejected the payload
        if e.response is not None:
            print(f"🚨 422 DETAILS: {e.response.text}") 
        return "OTHER"
    except Exception as e:
        print(f"⚠️ [AGENT 4] General Error: {e}")
        return "OTHER"

@app.post("/api/dispatch")
def dispatch_incident(payload: dict):
    print(f"📥 [PYTHON] Received payload for driver: {payload.get('driverId')}")
    
    # 1. Extract the text and categorize via RocketRide Webhook
    driver_text = payload.get("rawText", "")
    category = categorize_incident(driver_text)

    # =====================================================================
    # TO DO: Baky and Minh will drop their RAG pipeline logic here.
    # They can use the 'category' to determine which vector database to search.
    # =====================================================================

    # 2. Return the ActionableResponse formatted dictionary back to TypeScript
    return {
        "summary": f"Incident categorized as {category}. Dispatching support unit to {payload.get('simulatedLocation')}.",
        "immediateSteps": [
            "Secure the vehicle and engage parking brake",
            "Do NOT attempt to restart the engine",
            f"Stand by for specific {category} protocol extraction"
        ],
        "eta": "10 minutes"
    }

if __name__ == "__main__":
    # Runs the server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)