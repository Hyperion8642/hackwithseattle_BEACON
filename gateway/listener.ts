// src/gateway/listener.ts
import { parseIncidentData } from "./parser.js";
import { ActionableResponse } from "../shared/types.js";

export async function startListener(app: any) {
  console.log("📡 BEACON Gateway listening for emergency payloads...");
  
  for await (const [space, message] of app.messages) {
    // Skip messages that aren't user texts (like system events)
    //if (message.content.type !== "text" && !message.content.attachments) continue;

    console.log(`\n[ALERT] Incoming report from ${message.sender.id}`);

    // 1. Parse the incoming message
    const payload = parseIncidentData(message);
    console.log("📦 Parsed Payload ready for RocketRide:", payload);

    // 2. Trigger the native typing indicator
    await space.responding(async () => {
      
      // 3. MOCK ORCHESTRATION: Simulate the delay of Agents 1 & 2 vector searching
      await new Promise(resolve => setTimeout(resolve, 2500)); 
      
      // This is what dispatchToRocketRide(payload) will eventually return
      const mockFinalPlan: ActionableResponse = {
         summary: "Mechanical failure categorized. Dispatching heavy tow unit to 3rd & Pine.",
         immediateSteps: [
           "Secure the vehicle and engage parking brake",
           "Do NOT attempt to restart the engine",
           "Keep passengers onboard unless cabin is compromised by fluids"
         ],
         eta: "14 minutes"
      };
      
      // 4. Format and send the response back to the driver
      const replyText = `🚨 PROTOCOL ACTIVE\n\nImmediate Steps:\n- ${mockFinalPlan.immediateSteps.join('\n- ')}\n\nETA: ${mockFinalPlan.eta}\n${mockFinalPlan.summary}`;
      
      await message.reply(replyText);
    });
  }

}