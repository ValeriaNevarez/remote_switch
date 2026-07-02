const account_sid = process.env.TWILIO_ACCOUNT_SID;
const auth_token = process.env.TWILIO_AUTH_TOKEN;

import twilio from "twilio";
import {
  findDeviceKeyByPhone,
  updateDeviceLastCall,
} from "../lib/firebaseAdmin.js";

const TERMINAL_STATUSES = new Set([
  "completed",
  "busy",
  "failed",
  "no-answer",
  "canceled",
]);
const COMPLETED_CALL_MIN_DURATION_SECONDS = 60;

const normalizeStatus = (status, durationSeconds) => {
  if (
    status === "completed" &&
    durationSeconds != null &&
    durationSeconds < COMPLETED_CALL_MIN_DURATION_SECONDS
  ) {
    return "incompleted";
  }
  return status;
};

const parseCompletedState = (value) => {
  if (value === "on") {
    return true;
  }
  if (value === "off") {
    return false;
  }
  return null;
};

const requestUrl = (req) => {
  const protocol = req.headers["x-forwarded-proto"] || "https";
  const host = req.headers["x-forwarded-host"] || req.headers.host;
  const path = req.url?.split("?")[0] || "/api/twilioCallStatus";
  const query = req.url?.includes("?") ? `?${req.url.split("?")[1]}` : "";
  return `${protocol}://${host}${path}${query}`;
};

export default async (req, res) => {
  if (req.method !== "POST") {
    res.statusCode = 405;
    res.end();
    return;
  }

  const signature = req.headers["x-twilio-signature"];
  const url = requestUrl(req);
  const params = req.body ?? {};

  if (
    auth_token &&
    signature &&
    !twilio.validateRequest(auth_token, signature, url, params)
  ) {
    res.statusCode = 403;
    res.end();
    return;
  }

  const callStatus = String(params.CallStatus || "");
  if (!TERMINAL_STATUSES.has(callStatus)) {
    res.statusCode = 200;
    res.setHeader("Content-Type", "text/plain");
    res.end();
    return;
  }

  const phoneNumber = String(params.To || "");
  const completedState = parseCompletedState(
    String(req.query?.completed_state || ""),
  );
  if (!phoneNumber || completedState == null) {
    res.statusCode = 200;
    res.setHeader("Content-Type", "text/plain");
    res.end();
    return;
  }

  const durationSeconds = Number.parseInt(String(params.CallDuration || ""), 10);
  const normalizedStatus = normalizeStatus(
    callStatus,
    Number.isNaN(durationSeconds) ? null : durationSeconds,
  );

  try {
    const deviceKey = await findDeviceKeyByPhone(phoneNumber);
    if (deviceKey != null) {
      const fields = {
        last_call_sid: String(params.CallSid || ""),
        last_call_status: normalizedStatus,
        last_call_at: new Date().toISOString(),
      };
      if (normalizedStatus === "completed") {
        fields.last_completed_state = completedState;
        fields.last_completed_call_at = fields.last_call_at;
      }
      await updateDeviceLastCall(deviceKey, fields);
    }
  } catch (error) {
    console.log("twilioCallStatus failed to update Firebase", error);
  }

  res.statusCode = 200;
  res.setHeader("Content-Type", "text/plain");
  res.end();
};
