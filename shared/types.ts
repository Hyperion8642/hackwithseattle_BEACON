// src/shared/types.ts

export interface IncidentPayload {
  incidentId: string;
  driverId: string;
  rawText: string;
  simulatedLocation: string; 
  mediaUrls: string[];
  timestamp: Date;
}

export interface ActionableResponse {
  summary: string;
  immediateSteps: string[];
  eta?: string;
}