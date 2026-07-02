const account_sid = process.env.TWILIO_ACCOUNT_SID;
const auth_token = process.env.TWILIO_AUTH_TOKEN;

import { twilioMasterPhoneNumber } from "../lib/repoConfig.js";
import { dtmfSignalForEnable } from "../lib/callDigit.js";
import { buildStatusCallbackUrl } from "../lib/statusCallbackUrl.js";
import twilio from "twilio";

const INITIAL_PAUSE_SECONDS = 10;
const BETWEEN_DIGIT_PLAYS_PAUSE_SECONDS = 10;
const DIGIT_PLAY_COUNT = 5;
const OUTBOUND_CALL_TIME_LIMIT_SECONDS = 70;

export default async (req, res) => {
  res.statusCode = 200;
  res.setHeader("Content-Type", "application/json");

  const client = twilio(account_sid, auth_token);
  const VoiceResponse = twilio.twiml.VoiceResponse;

  const to = req.body.to;
  const want_enable = Boolean(req.body.enable);
  const digits = dtmfSignalForEnable(to, want_enable);

  const response = new VoiceResponse();
  response.pause({ length: INITIAL_PAUSE_SECONDS });
  for (let i = 0; i < DIGIT_PLAY_COUNT; i++) {
    response.play({ digits });
    response.pause({ length: BETWEEN_DIGIT_PLAYS_PAUSE_SECONDS });
  }

  const callParams = {
    from: twilioMasterPhoneNumber,
    to,
    twiml: response,
    timeLimit: OUTBOUND_CALL_TIME_LIMIT_SECONDS,
  };

  const statusCallback = buildStatusCallbackUrl(want_enable);
  if (statusCallback) {
    callParams.statusCallback = statusCallback;
    callParams.statusCallbackMethod = "POST";
    callParams.statusCallbackEvent = [
      "completed",
      "busy",
      "failed",
      "no-answer",
      "canceled",
    ];
  }

  client.calls
    .create(callParams)
    .then(() => {
      res.send(JSON.stringify({ success: true }));
    })
    .catch((err) => {
      console.log(err);
      res.send(JSON.stringify({ success: false }));
    });
};
