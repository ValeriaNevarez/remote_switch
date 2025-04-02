const account_sid = process.env.TWILIO_ACCOUNT_SID;
const auth_token = process.env.TWILIO_AUTH_TOKEN;

import twilio from "twilio";

export default async (req, res) => {
  res.statusCode = 200;
  res.setHeader("Content-Type", "application/json");

  const client = twilio(account_sid, auth_token);

  const VoiceResponse = twilio.twiml.VoiceResponse;

  const response = new VoiceResponse();
  response.pause({
    length: 10,
  });
  // Prototype phone numbers that have inverted logic (wired backwards),
  // digit 5 turns them off, digit 1 turns them on.
  const is_inverted =
    req.body.to == "+528713293364" ||
    req.body.to == "+528713971819" ||
    req.body.to == "+528713971823" ||
    req.body.to == "+528713865040" ||
    req.body.to == "+528713971807" ||
    req.body.to == "+528713460690";

  const digits = is_inverted == true ? "w1" : "w5";

  response.play({
    digits: digits,
  });

  response.pause({
    length: 60,
  });

  client.calls
    .create({
      from: "+18667487103",
      to: req.body.to,
      twiml: response,
      timeLimit: 70,
    })
    .then((CallInstance) => {
      res.send(JSON.stringify({ success: true }));
    })
    .catch((err) => {
      console.log(err);
      res.send(JSON.stringify({ success: false }));
    });
};
