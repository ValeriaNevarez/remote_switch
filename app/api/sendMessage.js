const account_sid = process.env.TWILIO_ACCOUNT_SID;
const auth_token = process.env.TWILIO_AUTH_TOKEN;


import twilio from "twilio";

export default async (req, res) => {
  res.statusCode = 200;
  res.setHeader("Content-Type", "application/json");

  const client = twilio(account_sid, auth_token);

  client.messages.create({
    from: '+18667487103',
    to: req.body.to,
    body: req.body.body,
  })
  .then(() => {
    res.send(JSON.stringify({ success: true }));
  })
  .catch((err) => {
    console.log(err);
    res.send(JSON.stringify({ success: false }));
  });
};
