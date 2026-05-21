// src/gateway/parser.ts
import { randomUUID } from "crypto";
import { IncidentPayload } from "../shared/types";

// Using 'any' for the message type here to keep it flexible 
// until you see exactly how Spectrum formats attachments.
export function parseIncidentData(message: any): IncidentPayload {
  const rawText = message.content.text || "";
  
  // Spectrum typically stores images/videos in an attachments array.
  // We safely extract URLs if they exist.
  const mediaUrls: string[] = [];
  if (message.content.attachments && Array.isArray(message.content.attachments)) {
     message.content.attachments.forEach((att: any) => {
         if (att.url) mediaUrls.push(att.url);
     });
  }

  // Simulating GPS extraction based on your BEACON prompt design
  const simulatedLocation = "47.6101° N, 122.3400° W (Simulated - Near 3rd & Pine)";

  return {
    incidentId: randomUUID(),
    driverId: message.sender.id,
    rawText: rawText,
    simulatedLocation: simulatedLocation,
    mediaUrls: mediaUrls,
    timestamp: new Date(),
  };
}