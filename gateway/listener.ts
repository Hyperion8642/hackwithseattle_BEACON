// src/gateway/listener.ts
import { parseIncidentData, extractStreetLocation } from "./parser.js";
import { dispatchToRocketRide } from "../orchestration/dispatcher.js";

const BOLD_MAP: Record<string, string> = {
  a:"𝗮",b:"𝗯",c:"𝗰",d:"𝗱",e:"𝗲",f:"𝗳",g:"𝗴",h:"𝗵",i:"𝗶",j:"𝗷",k:"𝗸",l:"𝗹",m:"𝗺",
  n:"𝗻",o:"𝗼",p:"𝗽",q:"𝗾",r:"𝗿",s:"𝘀",t:"𝘁",u:"𝘂",v:"𝘃",w:"𝘄",x:"𝘅",y:"𝘆",z:"𝘇",
  A:"𝗔",B:"𝗕",C:"𝗖",D:"𝗗",E:"𝗘",F:"𝗙",G:"𝗚",H:"𝗛",I:"𝗜",J:"𝗝",K:"𝗞",L:"𝗟",M:"𝗠",
  N:"𝗡",O:"𝗢",P:"𝗣",Q:"𝗤",R:"𝗥",S:"𝗦",T:"𝗧",U:"𝗨",V:"𝗩",W:"𝗪",X:"𝗫",Y:"𝗬",Z:"𝗭",
  "0":"𝟬","1":"𝟭","2":"𝟮","3":"𝟯","4":"𝟰","5":"𝟱","6":"𝟲","7":"𝟳","8":"𝟴","9":"𝟵",
};

function toUnicodeBold(text: string): string {
  return text.split("").map(c => BOLD_MAP[c] ?? c).join("");
}

function renderMarkdown(text: string): string {
  return text.replace(/\*\*(.+?)\*\*/g, (_, inner) => toUnicodeBold(inner));
}

export async function startListener(app: any) {
  console.log("📡 BEACON Gateway listening for emergency payloads...");

  for await (const [space, message] of app.messages) {
    console.log(`\n[ALERT] Incoming report from ${message.sender.id}`);

    const rawText: string = message.content?.text || "";
    const location = extractStreetLocation(rawText);
    const payload = parseIncidentData(message, location);

    console.log("📦 Parsed payload:", { driverId: payload.driverId, location, rawText });

    await space.responding(async () => {
      console.log("🚀 Dispatching to RocketRide orchestration bus...");

      try {
        const response = await dispatchToRocketRide(payload);

        const replyText = renderMarkdown([
          `Hello, Driver`,
          "",
          response.summary,
          response.immediateSteps.length > 0
            ? `\nImmediate Steps:\n- ${response.immediateSteps.join("\n- ")}`
            : "",
          "\n— BEACON Transit Assistant",
        ]
          .filter(Boolean)
          .join("\n"));

        await message.reply(replyText);
      } catch (err: any) {
        console.error("Dispatch error:", err);
        await message.reply(
          `🚨 SYSTEM ERROR\n\nUnable to process your report.\nError: ${err.message}`
        );
      }
    });
  }
}
