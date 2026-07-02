const account_sid = process.env.TWILIO_ACCOUNT_SID;
const auth_token = process.env.TWILIO_AUTH_TOKEN;

import twilio from "twilio";

const ExtractTwimlFromEvents = (events) => {
  for (const event of events) {
    const parameters = event?.request?.parameters;
    if (!parameters) {
      continue;
    }
    for (const [key, value] of Object.entries(parameters)) {
      if (key.toLowerCase() === "twiml" && value) {
        return String(value);
      }
    }
  }
  return null;
};

const ExtractPressedDigit = (twiml) => {
  if (!twiml) {
    return null;
  }

  const matches = twiml.matchAll(/<Play\b[^>]*\bdigits=["']([^"']+)["']/gi);
  for (const match of matches) {
    const digits = match[1];
    if (digits.endsWith("5")) {
      return "5";
    }
    if (digits.endsWith("1")) {
      return "1";
    }
  }
  return null;
};

const GetPressedDigitForCall = async (client, callSid) => {
  try {
    const events = await client.calls(callSid).events.list({ limit: 20 });
    const twiml = ExtractTwimlFromEvents(events);
    return ExtractPressedDigit(twiml);
  } catch (error) {
    console.log(`Could not fetch Twilio call events for ${callSid}`, error);
    return null;
  }
};

const GetCallList = async (client) => {
  const startTimeAfter = new Date();
  // Restrict call list to 120 days since we consider numbers
  // to be dead after 120 days without any call.
  startTimeAfter.setDate(startTimeAfter.getDate() - 120);
  return await client.calls.list({
    pageSize: 1000,
    startTimeAfter: startTimeAfter,
  });
};

export default async (req, res) => {
  res.statusCode = 200;
  res.setHeader("Content-Type", "application/json");

  const client = twilio(account_sid, auth_token);
  const phone_numbers = req.body.phone_numbers;
  let dictionary = {};
  for (const phone_number of phone_numbers) {
    dictionary[phone_number] = {
      date: null,
      status: null,
      status_date: null,
      last_completed_call_sid: null,
      last_completed_pressed_digit: null,
    };
  }

  const call_list = await GetCallList(client);
  for (const element of call_list) {
    const date_created = element["dateCreated"];
    const phone_to = element["to"];
    const call_sid = element["sid"];
    let status = element["status"];
    const duration = element["duration"];

    if (!(phone_to in dictionary)) {
      continue;
    }

    if (status == "completed" && Number(duration) < 60) {
      status = "incompleted";
    }
    // Con esto llenamos la última llamada completada
    if (dictionary[phone_to]["date"] == null && status == "completed") {
      dictionary[phone_to]["date"] = date_created;
      dictionary[phone_to]["last_completed_call_sid"] = call_sid;
    }
    if (dictionary[phone_to]["status"] == null) {
      dictionary[phone_to]["status"] = status;
      dictionary[phone_to]["status_date"] = date_created;
    }
  }

  await Promise.all(
    Object.entries(dictionary).map(async ([phone_number, value]) => {
      const callSid = value["last_completed_call_sid"];
      if (!callSid) {
        return;
      }
      value["last_completed_pressed_digit"] = await GetPressedDigitForCall(
        client,
        callSid
      );
      dictionary[phone_number] = value;
    })
  );

  res.send(JSON.stringify({ dictionary: dictionary }));
};
