// src/gateway/parser.ts
import { randomUUID } from "crypto";
import { IncidentPayload } from "../shared/types";

// Using 'any' for the message type here to keep it flexible 
// until you see exactly how Spectrum formats attachments.
export function parseIncidentData(message: any, finalLocationString: string): IncidentPayload {
  const rawText = message.content.text || "";
  
  // Spectrum typically stores images/videos in an attachments array.
  // We safely extract URLs if they exist.
  const mediaUrls: string[] = [];
  if (message.content.attachments && Array.isArray(message.content.attachments)) {
     message.content.attachments.forEach((att: any) => {
         if (att.url) mediaUrls.push(att.url);
     });
  }

  return {
    incidentId: randomUUID(),
    driverId: message.sender.id,
    rawText: rawText,
    simulatedLocation: finalLocationString,
    mediaUrls: mediaUrls,
    timestamp: new Date(),
  };
}

export function extractStreetLocation(text: string): string {
  // Normalize spacing a bit for cleaner regex matching
  const normalized = text.replace(/\s+/g, " ").trim();

  // Pattern 1: Intersections
  const intersectionRegex =
    /(?:on|at|near|corner of)\s+([a-zA-Z0-9\s]+)\s+(?:and|&)\s+([a-zA-Z0-9\s]+)/i;

  // Pattern 2: Block numbers
  const blockRegex =
    /(\d+)\s+block\s+(?:of\s+)?([a-zA-Z0-9\s]+)/i;

  // Pattern 3: Highways
  const highwayRegex =
    /(I-?\d+|SR-?\d+|Hwy\s*\d+).*?(?:mile|mm|marker)\s*(\d+)/i;

  // ✅ NEW Pattern 4: Full street address (basic US format)
  const addressRegex =
    /\b(\d{1,6})\s+([a-zA-Z0-9\s.'-]+?)\s+(street|st|road|rd|avenue|ave|drive|dr|boulevard|blvd|lane|ln|court|ct|highway|hwy|way|pike)\b(?:\s*,?\s*([a-zA-Z\s]+)\s*,?\s*([A-Z]{2})\s*(\d{5})?)?/i;

  // 1. Intersections
  const intersectionMatch = normalized.match(intersectionRegex);
  if (intersectionMatch) {
    const street1 = intersectionMatch[1].trim();
    const street2 = intersectionMatch[2].trim();
    return `${street1} & ${street2}`.replace(/\b\w/g, c => c.toUpperCase());
  }

  // 2. Block numbers
  const blockMatch = normalized.match(blockRegex);
  if (blockMatch) {
    const blockNum = blockMatch[1];
    const street = blockMatch[2].trim();
    return `${blockNum} Block of ${street}`.replace(/\b\w/g, c => c.toUpperCase());
  }

  // 3. Highways
  const highwayMatch = normalized.match(highwayRegex);
  if (highwayMatch) {
    const highway = highwayMatch[1].toUpperCase().replace("I", "I-");
    const mileMarker = highwayMatch[2];
    return `${highway} at Mile Marker ${mileMarker}`;
  }

  // 4. Full address (NEW)
  const addressMatch = normalized.match(addressRegex);
  if (addressMatch) {
    const number = addressMatch[1];
    const street = addressMatch[2];
    const type = addressMatch[3];

    // Optional city/state/zip (if present)
    const city = addressMatch[4]?.trim();
    const state = addressMatch[5];

    let result = `${number} ${street} ${type}`;

    if (city) result += `, ${city}`;
    if (state) result += `, ${state}`;

    return result.replace(/\b\w/g, c => c.toUpperCase());
  }

  return "unknown";
}
