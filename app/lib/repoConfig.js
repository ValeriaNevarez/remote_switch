import { readFileSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const repoRoot = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const config = JSON.parse(
  readFileSync(join(repoRoot, "config.json"), "utf-8"),
);

export const twilioMasterPhoneNumber = config.twilio_master_phone_number;
