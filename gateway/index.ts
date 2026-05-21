// src/index.ts
import "dotenv/config";
import { Spectrum } from "spectrum-ts";
import { imessage } from "spectrum-ts/providers/imessage";
import { startListener } from "./listener.js";

async function main() {
  const app = await Spectrum({
    projectId: process.env.SPECTRUM_PROJECT_ID as string,
    projectSecret: process.env.SPECTRUM_PROJECT_SECRET as string,
    providers: [imessage.config()],
  });

  // Pass the initialized app into your listener loop
  await startListener(app);
}

main().catch(console.error);