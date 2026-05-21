// src/gateway/listener.ts
import { parseIncidentData } from "./parser.js";
import { ActionableResponse } from "../shared/types.js";
import { RocketRideClient, Question } from "rocketride";

export async function startListener(app: any) {
  console.log("📡 BEACON Gateway listening for emergency payloads...");
  
  // Initialize RocketRide Client
  const client = new RocketRideClient({
    uri: process.env.ROCKETRIDE_URI || 'ws://localhost:20000',
    auth: process.env.ROCKETRIDE_APIKEY
  });

  try {
    await client.connect();
    console.log("✅ Connected to RocketRide Engine.");
  } catch (e) {
    console.error("❌ Failed to connect to RocketRide Engine. Ensure it is running.", e);
  }

  for await (const [space, message] of app.messages) {
    console.log(`\n[ALERT] Incoming report from ${message.sender.id}`);

    const payload = parseIncidentData(message);
    console.log("📦 Parsed Payload ready for RocketRide:", payload);

    await space.responding(async () => {
      console.log("🚀 Dispatching to RocketRide pipeline...");
      
      try {
        const { token } = await client.use({ filepath: 'pipelines/beacon_dispatch.pipe' });
        
        const question = new Question({ expectJson: true });
        question.addQuestion(`DRIVER REPORT: ${payload.driver_text} | LOC: ${payload.gps} | OP: ${payload.operator_id}`);
        
        const rrResponse = await client.chat({ token, question });
        
        let finalPlan;
        if (rrResponse.answers && rrResponse.answers.length > 0) {
            finalPlan = rrResponse.answers[0]; // expectJson=true parses the JSON
        } else {
            throw new Error("No answer received from pipeline");
        }
        
        const replyText = `🚨 PROTOCOL ACTIVE\n\nImmediate Steps:\n- ${(finalPlan.immediateSteps || []).join('\n- ')}\n\nETA: ${finalPlan.eta || 'Unknown'}\n${finalPlan.summary || ''}`;
        await message.reply(replyText);
      } catch (err: any) {
        console.error("Pipeline Execution Error:", err);
        await message.reply(`🚨 SYSTEM ERROR\n\nUnable to reach RocketRide Orchestrator. Initiating fallback protocols.\nError: ${err.message}`);
      }
    });
  }
}