const account_sid = process.env.TWILIO_ACCOUNT_SID;
const auth_token = process.env.TWILIO_AUTH_TOKEN;

import {
  invertedPhoneNumbers,
  twilioMasterPhoneNumber,
} from "../lib/repoConfig.js";
import twilio from "twilio";

const INITIAL_PAUSE_SECONDS = 10;
const BETWEEN_DIGIT_PLAYS_PAUSE_SECONDS = 10;
const DIGIT_PLAY_COUNT = 6;
const OUTBOUND_CALL_TIME_LIMIT_SECONDS = 70;

export default async (req, res) => {
  res.statusCode = 200;
  res.setHeader("Content-Type", "application/json");

  const client = twilio(account_sid, auth_token);

  const VoiceResponse = twilio.twiml.VoiceResponse;

  const response = new VoiceResponse();
  const is_inverted = invertedPhoneNumbers.has(req.body.to);
  const want_enable = Boolean(req.body.enable);
  const digits =
    (want_enable && !is_inverted) || (!want_enable && is_inverted) ? "w5" : "w1";

  response.pause({ length: INITIAL_PAUSE_SECONDS });
  for (let i = 0; i < DIGIT_PLAY_COUNT; i++) {
    response.play({ digits });
    response.pause({ length: BETWEEN_DIGIT_PLAYS_PAUSE_SECONDS });
  }

  client.calls
    .create({
      from: twilioMasterPhoneNumber,
      to: req.body.to,
      twiml: response,
      timeLimit: OUTBOUND_CALL_TIME_LIMIT_SECONDS,
    })
    .then(() => {
      res.send(JSON.stringify({ success: true }));
    })
    .catch((err) => {
      console.log(err);
      res.send(JSON.stringify({ success: false }));
    });
};
