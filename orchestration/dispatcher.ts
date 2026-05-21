// src/orchestration/dispatcher.ts
import { IncidentPayload, ActionableResponse } from "../shared/types.js";

const ORCHESTRATION_BUS_URL = process.env.ORCHESTRATION_BUS_URL || "http://localhost:5565/dispatch";

export async function dispatchToRocketRide(payload: IncidentPayload): Promise<ActionableResponse> {
  console.log(`[DISPATCHER] Incident ${payload.incidentId} from driver ${payload.driverId}`);

  const res = await fetch(ORCHESTRATION_BUS_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      incidentId: payload.incidentId,
      driverId: payload.driverId,
      rawText: payload.rawText,
      simulatedLocation: payload.simulatedLocation,
      mediaUrls: payload.mediaUrls,
      timestamp: payload.timestamp.toISOString(),
    }),
  });

  if (!res.ok) {
    throw new Error(`Orchestration bus returned ${res.status}: ${await res.text()}`);
  }

  const data = await res.json() as { summary: string; immediateSteps: string[]; eta?: string };
  console.log(`[DISPATCHER] Response received for ${payload.incidentId}`);

  return {
    summary: data.summary,
    immediateSteps: data.immediateSteps ?? [],
    eta: data.eta,
  };
}
