// src/gateway/listener.ts
import { parseIncidentData, extractStreetLocation } from "./parser.js";
import { ActionableResponse } from "../shared/types.js";
import { imessage } from "spectrum-ts/providers/imessage";
import { dispatchToRocketRide } from "../orchestration/dispatcher.js";

export async function startListener(app: any) {
  console.log("📡 BEACON Gateway listening for emergency payloads...");

  for await (const [space, message] of app.messages) {
    console.log(`\n[ALERT] Incoming report from ${message.sender.id}`);

    const rawText = message.content.text || "";
    let isLocationResolved = false;
    let finalLocationString = "";

    // LOCATION EXTRACTION LOGIC
    // Try parse text
    if (!isLocationResolved) {
      const extractedStreets = extractStreetLocation(rawText);
      if (extractedStreets !== "unknown") {
        finalLocationString = `Text Location: ${extractedStreets}`;
        isLocationResolved = true;
        console.log("📍 Location found via Regex Parser");
      }
    }
    // 3. If neither worked, request location
    if (!isLocationResolved) {
      console.log(`[SYS] Location missing. Asking ${message.sender.id} to share their location...`);
      
      await message.reply(
          "📍 Please reply with your address or nearby cross streets."
      );

      continue;
    }

    // DISPATCH MESSAGE
    const payload = parseIncidentData(message, finalLocationString);
    console.log("📦 Parsed Payload ready for RocketRide:", payload);
    // react to the users message while we process the payload and wait for RocketRide's response
    await message.reply("Accident details received. Running emergency protocol...");

    await space.responding(async () => {
      
      try {
        // Handoff to RocketRide
        const finalPlan = await dispatchToRocketRide(payload);

        const replyText = `🚨 PROTOCOL ACTIVE\n\nImmediate Steps:\n- ${finalPlan.immediateSteps.join('\n- ')}\n\nETA: ${finalPlan.eta || 'Unknown'}\n${finalPlan.summary}`;
        
        // // 3. MOCK ORCHESTRATION: Simulate the delay of Agents 1 & 2 vector searching
        // await new Promise(resolve => setTimeout(resolve, 2500)); 
        
        // // This is what dispatchToRocketRide(payload) will eventually return
        // const mockFinalPlan: ActionableResponse = {
        //    summary: "Mechanical failure categorized. Dispatching heavy tow unit to 3rd & Pine.",
        //    immediateSteps: [
        //      "Secure the vehicle and engage parking brake",
        //      "Do NOT attempt to restart the engine",
        //      "Keep passengers onboard unless cabin is compromised by fluids"
        //    ],
        //    eta: "14 minutes"
        // };
        
        // // Format and send the response back to the driver
        // const replyText = `🚨 PROTOCOL ACTIVE\n\nImmediate Steps:\n- ${mockFinalPlan.immediateSteps.join('\n- ')}\n\nETA: ${mockFinalPlan.eta}\n${mockFinalPlan.summary}`;
        
        await message.reply(replyText);
      } catch (error) {
        console.error("[ERROR] RocketRide dispatch failed:", error);
        await message.reply("⚠️ System error: Unable to reach dispatch agents. Please fall back to voice radio immediately.");
      }
    });
  }
}