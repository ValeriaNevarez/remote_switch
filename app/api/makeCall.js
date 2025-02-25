const account_sid = process.env.TWILIO_ACCOUNT_SID;
const auth_token = process.env.TWILIO_AUTH_TOKEN;


import twilio from "twilio";

export default async (req, res) => {
  res.statusCode = 200;
  res.setHeader("Content-Type", "application/json");

  const client = twilio(account_sid, auth_token);

  client.calls
    .create({
      from: "+18667487103",
      to: req.body.to,
      url: "http://twimlets.com/holdmusic?Bucket=com.twilio.music.ambient",
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
