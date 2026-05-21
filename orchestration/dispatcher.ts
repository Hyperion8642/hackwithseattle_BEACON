// src/orchestration/dispatcher.ts
import { IncidentPayload, ActionableResponse } from "../shared/types.js";

export async function dispatchToRocketRide(payload: IncidentPayload): Promise<ActionableResponse> {
  console.log(`[ROCKETRIDE] Routing incident ${payload.incidentId} to Python orchestration layer...`);
  
  try {
    // Send the payload to the Python FastAPI server
    const response = await fetch("http://localhost:8000/api/dispatch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`Python server responded with status: ${response.status}`);
    }

    // Extract the final ActionableResponse sent back by Python
    const actionPlan: ActionableResponse = await response.json();
    return actionPlan;

  } catch (error) {
    console.error("[ROCKETRIDE] Failed to reach Python orchestration layer:", error);
    throw error;
  }
}

// export async function dispatchToRocketRide(payload: IncidentPayload): Promise<ActionableResponse> {
//   console.log(`[ROCKETRIDE] Received incident ${payload.incidentId} from driver ${payload.driverId}`);
  
//   // =====================================================================
//   // TO DO: 
//   // 1. Initialize RocketRide client here
//   // 2. Pass 'payload' to Agent 1 (Protocol) and Agent 2 (Logistics) in parallel
//   // 3. Pass their outputs to Agent 3 (Synthesizer)
//   // 4. Return the final ActionableResponse object
//   // =====================================================================

//   // Temporary placeholder until they drop their code in:
//   return {
//     summary: "System check: RocketRide dispatcher is wired up correctly.",
//     immediateSteps: [
//       "Stand by for Agent 1 protocol extraction",
//       "Stand by for Agent 2 logistics routing"
//     ],
//     eta: "TBD"
//   };
// }